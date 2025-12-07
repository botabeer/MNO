from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from datetime import datetime
from typing import Dict, Any, Optional

from constants import COLORS
from games.game_helpers import (
    normalize_text,
    create_game_header,
    create_progress_box,
    create_separator,
    create_action_buttons,
    create_winner_card
)


class FastTypingGame:
    """Game: Fast Typing — players must type a given phrase as fast as possible."""

    DEFAULT_WORDS = [
        "سبحان الله", "الحمد لله", "لا اله الا الله", "الله اكبر", "استغفر الله",
        "لا حول ولا قوه الا بالله", "حسبنا الله ونعم الوكيل", "توكلت على الله",
        "الله يرحمه", "العلم نور", "بارك الله فيك", "جزاك الله خيرا",
        "الله يحفظك", "ما شاء الله", "اللهم صل على محمد", "رب اغفر لي",
        "اللهم ارحمنا", "اللهم اجرني", "اللهم اهدني", "اللهم ارزقني",
        "اللهم عافني", "اللهم اصلح حالي"
    ]

    TOTAL_QUESTIONS = 5
    TIME_LIMIT = 30  # seconds

    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api

        # Game state
        self.words: list[str] = []
        self.questions: list[str] = []
        self.current_question: int = 0
        self.player_scores: Dict[str, Dict[str, Any]] = {}
        self.answered_users: set[str] = set()

        # Time tracking
        self.start_time: Optional[datetime] = None

    # ---------------------------------------------------------
    # Game start
    # ---------------------------------------------------------
    def start_game(self) -> FlexMessage:
        """Initialize game state and show the first question."""
        self.words = self.DEFAULT_WORDS.copy()
        self.questions = random.sample(self.words, min(self.TOTAL_QUESTIONS, len(self.words)))

        self.current_question = 0
        self.player_scores.clear()
        self.answered_users.clear()
        self.start_time = datetime.now()

        return self._show_question()

    # ---------------------------------------------------------
    # UI — generate the question Flex bubble
    # ---------------------------------------------------------
    def _show_question(self) -> FlexMessage:
        """Create and return a message containing the current question UI."""
        word = self.questions[self.current_question]
        self.start_time = datetime.now()  # reset timer for this question

        contents = [
            create_game_header("الكتابة السريعة"),
            create_progress_box(self.current_question + 1, self.TOTAL_QUESTIONS),
            create_separator(),
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": word,
                        "size": "lg",
                        "color": COLORS["primary"],
                        "weight": "bold",
                        "align": "center",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": "اكتب النص بأسرع وقت",
                        "size": "sm",
                        "color": COLORS["text_dark"],
                        "margin": "md",
                        "align": "center",
                    },
                    {
                        "type": "text",
                        "text": f"لديك {self.TIME_LIMIT} ثانية",
                        "size": "xs",
                        "color": COLORS["text_light"],
                        "margin": "xs",
                        "align": "center",
                    },
                ],
                "margin": "lg",
            },
            create_separator(),
            *create_action_buttons()
        ]

        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": contents,
                "backgroundColor": COLORS["card_bg"],
                "paddingAll": "20px",
            },
        }

        return FlexMessage(
            alt_text="الكتابة السريعة",
            contents=FlexContainer.from_dict(bubble)
        )

    # ---------------------------------------------------------
    # Next question
    # ---------------------------------------------------------
    def next_question(self) -> Optional[FlexMessage]:
        """Move to the next question if available."""
        self.current_question += 1

        if self.current_question < self.TOTAL_QUESTIONS:
            self.answered_users.clear()
            return self._show_question()

        return None  # signal that game should end

    # ---------------------------------------------------------
    # Answer check
    # ---------------------------------------------------------
    def check_answer(self, text: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        """Check player's message and determine outcome."""

        # Already answered this round
        if user_id in self.answered_users:
            return None

        # -----------------------------
        # Hint request
        # -----------------------------
        if text.lower() in ["لمح", "تلميح"]:
            word = self.questions[self.current_question]
            return {
                "response": TextMessage(
                    text=f"يبدأ بحرف: {word[0]}\nعدد الحروف: {len(word)}"
                ),
                "points": 0,
                "correct": False,
            }

        # -----------------------------
        # Request to reveal answer
        # -----------------------------
        if text.lower() in ["جاوب", "الجواب"]:
            self.answered_users.add(user_id)
            word = self.questions[self.current_question]

            # Another question coming?
            if self.current_question + 1 < self.TOTAL_QUESTIONS:
                return {
                    "response": TextMessage(text=f"الإجابة: {word}"),
                    "points": 0,
                    "correct": False,
                    "next_question": True
                }

            return self._end_game()

        # -----------------------------
        # Time exceeded?
        # -----------------------------
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).seconds
            if elapsed > self.TIME_LIMIT:
                if self.current_question + 1 < self.TOTAL_QUESTIONS:
                    return {
                        "response": TextMessage(text="انتهى الوقت"),
                        "points": 0,
                        "correct": False,
                        "next_question": True
                    }
                return self._end_game()

        # -----------------------------
        # Normalize and check answer
        # -----------------------------
        text_norm = normalize_text(text)
        correct_norm = normalize_text(self.questions[self.current_question])

        if text_norm == correct_norm:
            return self._handle_correct_answer(user_id, display_name)

        return None

    # ---------------------------------------------------------
    # Correct answer handler
    # ---------------------------------------------------------
    def _handle_correct_answer(self, user_id: str, display_name: str) -> Dict[str, Any]:
        """Update score + calculate time + return response dict."""
        elapsed_time = (datetime.now() - self.start_time).total_seconds()

        self.player_scores.setdefault(user_id, {
            "name": display_name,
            "score": 0,
            "time": 0.0
        })

        self.player_scores[user_id]["score"] += 1
        self.player_scores[user_id]["time"] += elapsed_time
        self.answered_users.add(user_id)

        # More questions left?
        if self.current_question + 1 < self.TOTAL_QUESTIONS:
            return {
                "response": TextMessage(
                    text=(
                        f"إجابة صحيحة {display_name} 🎉\n"
                        f"الوقت: {elapsed_time:.1f} ثانية\n"
                        f"+1 نقطة"
                    )
                ),
                "points": 1,
                "correct": True,
                "won": True,
                "next_question": True
            }

        # End game
        return self._end_game()

    # ---------------------------------------------------------
    # Game end
    # ---------------------------------------------------------
    def _end_game(self) -> Dict[str, Any]:
        """Show winner card and end the game."""
        if not self.player_scores:
            return {
                "response": TextMessage(text="انتهت اللعبة"),
                "points": 0,
                "correct": False,
                "won": False,
                "game_over": True
            }

        # Sort by: highest score → lowest total time
        sorted_players = sorted(
            self.player_scores.items(),
            key=lambda x: (x[1]["score"], -x[1]["time"]),
            reverse=True
        )

        winner = sorted_players[0][1]
        winner_card = create_winner_card(winner, sorted_players, "أسرع")

        return {
            "response": FlexMessage(
                alt_text="نتائج اللعبة",
                contents=FlexContainer.from_dict(winner_card)
            ),
            "points": winner["score"],
            "correct": True,
            "won": True,
            "game_over": True
        }
