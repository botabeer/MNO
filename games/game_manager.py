# games/game_manager.py - Enhanced Game Manager
import random
import os
from linebot.v3.messaging import TextMessage

from games.song_game import SongGame
from games.chain_words_game import ChainWordsGame
from games.opposite_game import OppositeGame
from games.fast_typing_game import FastTypingGame
from games.letters_words_game import LettersWordsGame
from games.category_letter_game import CategoryLetterGame
from games.human_animal_plant_game import HumanAnimalPlantGame
from games.compatibility_game import CompatibilityGame
from games.mafia_game import MafiaGame


class GameManager:
    """
    مدير الألعاب المركزي
    - إدارة جلسات الألعاب
    - التنسيق بين الألعاب المختلفة
    - التعامل مع الأوامر الترفيهية
    """

    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.active_games = {}  # {group_id: {'type': game_type, 'instance': game_obj}}
        
        # Load fun content
        self._load_fun_content()

    def _load_fun_content(self):
        """تحميل المحتوى الترفيهي"""
        try:
            # Questions
            questions_path = os.path.join(os.path.dirname(__file__), 'questions.txt')
            with open(questions_path, 'r', encoding='utf-8') as f:
                self.questions = [line.strip() for line in f if line.strip()]
        except:
            self.questions = ["سؤال ما أكثر موقف حسّسَك بمعنى الصداقة الحقيقي؟"]

        try:
            # Challenges
            challenges_path = os.path.join(os.path.dirname(__file__), 'challenges.txt')
            with open(challenges_path, 'r', encoding='utf-8') as f:
                self.challenges = [line.strip() for line in f if line.strip()]
        except:
            self.challenges = ["تحدي اكتب اسم آخر شخص كلمته الآن"]

        try:
            # Confessions
            confessions_path = os.path.join(os.path.dirname(__file__), 'confessions.txt')
            with open(confessions_path, 'r', encoding='utf-8') as f:
                self.confessions = [line.strip() for line in f if line.strip()]
        except:
            self.confessions = ["اعترف كم مرة أرسلت رسالة بالخطأ وحذفتها بسرعة؟"]

        try:
            # Mentions
            mentions_path = os.path.join(os.path.dirname(__file__), 'mentions.txt')
            with open(mentions_path, 'r', encoding='utf-8') as f:
                self.mentions = [line.strip() for line in f if line.strip()]
        except:
            self.mentions = ["منشن أكثر شخص عصبي؟"]

    # ========== Fun Commands ========== #

    def get_random_question(self):
        """سؤال عشوائي"""
        return random.choice(self.questions) if self.questions else "سؤال ما أكثر شيء تحبه؟"

    def get_random_challenge(self):
        """تحدي عشوائي"""
        return random.choice(self.challenges) if self.challenges else "تحدي اكتب اسم آخر شخص كلمته"

    def get_random_confession(self):
        """اعتراف عشوائي"""
        return random.choice(self.confessions) if self.confessions else "اعترف بشيء صغير"

    def get_random_mention(self):
        """منشن عشوائي"""
        return random.choice(self.mentions) if self.mentions else "منشن أكثر شخص مميز؟"

    # ========== Game Management ========== #

    def start_game(self, game_type: str, group_id: str):
        """بدء لعبة جديدة"""
        # Stop any active game first
        if group_id in self.active_games:
            self.stop_game(group_id)

        try:
            game_instance = None
            
            if game_type == "song":
                game_instance = SongGame(self.line_bot_api)
            elif game_type == "chain":
                game_instance = ChainWordsGame(self.line_bot_api)
            elif game_type == "opposite":
                game_instance = OppositeGame(self.line_bot_api)
            elif game_type == "fast_typing":
                game_instance = FastTypingGame(self.line_bot_api)
            elif game_type == "letters":
                game_instance = LettersWordsGame(self.line_bot_api)
            elif game_type == "category":
                game_instance = CategoryLetterGame(self.line_bot_api)
            elif game_type == "human_animal":
                game_instance = HumanAnimalPlantGame(self.line_bot_api)
            elif game_type == "compatibility":
                game_instance = CompatibilityGame(self.line_bot_api)
            elif game_type == "mafia":
                game_instance = MafiaGame(self.line_bot_api)
                game_instance.group_id = group_id
            else:
                return TextMessage(text="لعبة غير معروفة")

            if game_instance:
                self.active_games[group_id] = {
                    'type': game_type,
                    'instance': game_instance
                }
                return game_instance.start_game()

        except Exception as e:
            print(f"Error starting game {game_type}: {e}")
            return TextMessage(text="حدث خطأ في بدء اللعبة")

    def get_game(self, group_id: str):
        """الحصول على اللعبة النشطة"""
        if group_id in self.active_games:
            return self.active_games[group_id]['instance']
        return None

    def stop_game(self, group_id: str) -> bool:
        """إيقاف اللعبة النشطة"""
        if group_id in self.active_games:
            del self.active_games[group_id]
            return True
        return False

    def check_answer(self, group_id: str, answer: str, user_id: str, display_name: str):
        """فحص الإجابة"""
        game_data = self.active_games.get(group_id)
        if not game_data:
            return None

        game_instance = game_data['instance']
        try:
            return game_instance.check_answer(answer, user_id, display_name)
        except Exception as e:
            print(f"Error checking answer: {e}")
            return None

    def next_question(self, group_id: str):
        """السؤال التالي"""
        game_data = self.active_games.get(group_id)
        if not game_data:
            return None

        game_instance = game_data['instance']
        try:
            return game_instance.next_question()
        except Exception as e:
            print(f"Error getting next question: {e}")
            return None
