# games/game_manager.py
import os
import random
import threading
import logging
from typing import Optional, Any, Dict

from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer

from ui_builder import UIBuilder
from games.song_game import SongGame
from games.chain_words_game import ChainWordsGame
from games.opposite_game import OppositeGame
from games.fast_typing_game import FastTypingGame
from games.letters_words_game import LettersWordsGame
from games.category_letter_game import CategoryLetterGame
from games.human_animal_plant_game import HumanAnimalPlantGame
from games.compatibility_game import CompatibilityGame
from games.mafia_game import MafiaGame

logger = logging.getLogger(__name__)


class GameManager:
    """
    GameManager — مدير الألعاب المركزي
    واجهة موحدة لبدء الألعاب، استقبال الإجابات، الانتقال للسؤال التالي، وإيقاف اللعبة.
    """

    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        # active_games: group_id -> {'type': str, 'instance': GameInstance, 'lock': threading.Lock()}
        self.active_games: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

        # mapping of public command -> Game class
        self._game_map = {
            "song": SongGame,
            "chain": ChainWordsGame,
            "opposite": OppositeGame,
            "fast_typing": FastTypingGame,
            "letters": LettersWordsGame,
            "category": CategoryLetterGame,
            "human_animal": HumanAnimalPlantGame,
            "compatibility": CompatibilityGame,
            "mafia": MafiaGame,
        }

        # fun content collections (questions, challenges, etc.)
        self.questions = []
        self.challenges = []
        self.confessions = []
        self.mentions = []
        self._load_fun_content()

    # ----------------------
    #  Content Loading
    # ----------------------
    def _load_list_file(self, filename, default):
        path = os.path.join(os.path.dirname(__file__), filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                items = [line.strip() for line in f if line.strip()]
                if items:
                    return items
        except Exception:
            logger.debug("Could not load %s; using default", filename, exc_info=True)
        return default

    def _load_fun_content(self):
        self.questions = self._load_list_file("questions.txt", ["ما أكثر موقف علّمك معنى الصداقة؟"])
        self.challenges = self._load_list_file("challenges.txt", ["تحدٍّ: اكتب اسم آخر شخص تواصلت معه الآن"])
        self.confessions = self._load_list_file("confessions.txt", ["اعترف بشيء صغير فعلته اليوم!"])
        self.mentions = self._load_list_file("mentions.txt", ["منشن أقرب صديق لك الآن"])

    # ----------------------
    #  Fun commands
    # ----------------------
    def get_random_question(self) -> str:
        return random.choice(self.questions) if self.questions else "ما أكثر شيء تحبه؟"

    def get_random_challenge(self) -> str:
        return random.choice(self.challenges) if self.challenges else "اكتب تحدٍ صغير الآن"

    def get_random_confession(self) -> str:
        return random.choice(self.confessions) if self.confessions else "اعترف بشيء صغير"

    def get_random_mention(self) -> str:
        return random.choice(self.mentions) if self.mentions else "منشن شخص الآن"

    # ----------------------
    #  Game lifecycle
    # ----------------------
    def start_game(self, game_type: str, group_id: str):
        """
        يبدأ لعبة بالـ game_type للمجموعة group_id.
        يعيد FlexMessage أو TextMessage حسب نتيجة start_game الخاصة باللعبة.
        """
        if not group_id:
            logger.warning("start_game called without group_id")
            return TextMessage(text="حدث خطأ: لا يوجد معرف للمجموعة")

        game_type = (game_type or "").strip()
        with self._lock:
            # Stop any existing game in group
            if group_id in self.active_games:
                logger.info("Stopping existing game in group %s before starting new one", group_id)
                try:
                    self.stop_game(group_id)
                except Exception:
                    logger.exception("Error stopping existing game for group %s", group_id)

            GameClass = self._game_map.get(game_type)
            if not GameClass:
                logger.warning("Unknown game type requested: %s", game_type)
                return TextMessage(text="لعبة غير معروفة")

            try:
                # Instantiate game; pass manager reference if game needs to call back
                game_instance = GameClass(self.line_bot_api, manager=self) if self._accepts_manager(GameClass) else GameClass(self.line_bot_api)

                # special handling for mafia: set group_id if supported
                try:
                    if hasattr(game_instance, "group_id"):
                        setattr(game_instance, "group_id", group_id)
                except Exception:
                    pass

                # start game (games should return a message-compatible object or dict)
                start_result = game_instance.start_game()
                # register active game with per-game lock
                self.active_games[group_id] = {
                    "type": game_type,
                    "instance": game_instance,
                    "lock": threading.RLock()
                }

                # If game returned a Flex container dict, wrap into FlexMessage
                if isinstance(start_result, dict):
                    try:
                        # ensure it's a FlexContainer-compatible dict
                        flex = FlexContainer.from_dict(start_result)
                        return FlexMessage(alt_text=f"بدء {game_type}", contents=flex)
                    except Exception:
                        # If conversion fails, return as text fallback
                        logger.debug("start_game returned dict but couldn't convert to FlexContainer", exc_info=True)
                        return TextMessage(text=str(start_result))

                # If game returned a FlexMessage or TextMessage already, return it directly
                return start_result if start_result is not None else TextMessage(text="تم بدء اللعبة")
            except Exception as exc:
                logger.exception("Failed to start game %s for group %s: %s", game_type, group_id, exc)
                return TextMessage(text="حدث خطأ في بدء اللعبة")

    def _accepts_manager(self, cls) -> bool:
        """Heuristic: detect if GameClass constructor supports manager kwarg."""
        try:
            import inspect
            sig = inspect.signature(cls)
            return "manager" in sig.parameters
        except Exception:
            return False

    def get_game(self, group_id: str):
        """إرجاع كائن اللعبة النشط للمجموعة أو None"""
        with self._lock:
            entry = self.active_games.get(group_id)
            return entry["instance"] if entry else None

    def stop_game(self, group_id: str) -> bool:
        """
        إيقاف اللعبة النشطة للمجموعة.
        يحاول استدعاء method `stop_game` على الكائن لو وُجد.
        """
        if not group_id:
            return False

        with self._lock:
            entry = self.active_games.get(group_id)
            if not entry:
                return False

            game_inst = entry.get("instance")
            try:
                if hasattr(game_inst, "stop_game"):
                    # allow game to clean up timers / state
                    try:
                        game_inst.stop_game()
                    except Exception:
                        logger.exception("Game-specific stop_game failed for group %s", group_id)
                # finally remove from registry
                del self.active_games[group_id]
                logger.info("Stopped and removed game for group %s", group_id)
                return True
            except Exception:
                logger.exception("Failed to stop game for group %s", group_id)
                # try to remove anyway
                try:
                    del self.active_games[group_id]
                except Exception:
                    pass
                return False

    # ----------------------
    #  Gameplay: answers & next question
    # ----------------------
    def check_answer(self, group_id: str, answer: str, user_id: str, display_name: str):
        """
        تمرير الإجابة إلى كائن اللعبة النشط.
        من المتوقع أن تُعيد اللعبة dict (Flex container) أو FlexMessage/TextMessage أو None.
        """
        entry = self.active_games.get(group_id)
        if not entry:
            logger.debug("check_answer called but no active game for %s", group_id)
            return None

        game_inst = entry["instance"]
        lock = entry.get("lock", threading.RLock())

        with lock:
            try:
                # many game implementations may return:
                # - dict (flex container)
                # - FlexMessage/TextMessage
                # - dict with keys: response, next_question, correct, points, game_over
                result = game_inst.check_answer(answer, user_id=user_id, display_name=display_name)

                # If result is a dict representing a Flex bubble
                if isinstance(result, dict):
                    try:
                        flex = FlexContainer.from_dict(result)
                        return FlexMessage(alt_text="رد اللعبة", contents=flex)
                    except Exception:
                        return TextMessage(text=str(result))

                # If result is already message-like, return directly
                if isinstance(result, (FlexMessage, TextMessage)):
                    return result

                # If result is a structured dict with fields, translate to UI
                if isinstance(result, dict):
                    # preference: if 'response' is present, return it
                    if "response" in result and isinstance(result["response"], dict):
                        try:
                            flex = FlexContainer.from_dict(result["response"])
                            return FlexMessage(alt_text="رد", contents=flex)
                        except Exception:
                            return TextMessage(text=str(result["response"]))

                    if "response" in result and isinstance(result["response"], str):
                        return TextMessage(text=result["response"])

                    # fallback messages for next_question/game_over
                    if result.get("game_over"):
                        # build winner card if provided
                        winner = result.get("winner")
                        all_players = result.get("all_players", [])
                        game_name = result.get("game_name", "")
                        if winner:
                            card = UIBuilder.card([UIBuilder.header("انتهت اللعبة"), UIBuilder.section("الفائز", winner.get("name", ""))])
                            try:
                                flex = FlexContainer.from_dict(card)
                                return FlexMessage(alt_text="انتهت اللعبة", contents=flex)
                            except Exception:
                                return TextMessage(text=f"انتهت اللعبة. الفائز: {winner.get('name', '')}")
                        return TextMessage(text="انتهت اللعبة")

                    if result.get("response_text"):
                        return TextMessage(text=result["response_text"])

                # default fallback: stringify
                if result is None:
                    return None
                return TextMessage(text=str(result))
            except Exception as exc:
                logger.exception("Exception while checking answer for group %s: %s", group_id, exc)
                return TextMessage(text="حدث خطأ أثناء معالجة الإجابة")

    def next_question(self, group_id: str):
        """
        طلب السؤال التالي من اللعبة النشطة.
        تتوقع الألعاب أن تُعيد dict (Flex bubble) أو رسالة نصية أو None.
        """
        entry = self.active_games.get(group_id)
        if not entry:
            logger.debug("next_question called but no active game for %s", group_id)
            return None

        game_inst = entry["instance"]
        lock = entry.get("lock", threading.RLock())

        with lock:
            try:
                nxt = game_inst.next_question()
                if isinstance(nxt, dict):
                    try:
                        flex = FlexContainer.from_dict(nxt)
                        return FlexMessage(alt_text="سؤال جديد", contents=flex)
                    except Exception:
                        return TextMessage(text=str(nxt))
                if isinstance(nxt, (FlexMessage, TextMessage)):
                    return nxt
                if isinstance(nxt, str):
                    return TextMessage(text=nxt)
                return None
            except Exception as exc:
                logger.exception("Failed to get next question for group %s: %s", group_id, exc)
                return TextMessage(text="حدث خطأ أثناء جلب السؤال التالي")

    # ----------------------
    #  Utility: get mapping / available games
    # ----------------------
    def available_games(self):
        """Returns list of available game keys for menus."""
        return list(self._game_map.keys())
