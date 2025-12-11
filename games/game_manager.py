"""
مدير الألعاب - يدير جميع الألعاب المتاحة
"""
import random
from pathlib import Path
from linebot.models import TextSendMessage

class GameManager:
    """مدير الألعاب الموحد"""
    
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.active_games = {}
        
        # تحميل محتوى الألعاب البسيطة
        self.questions = self._load_text_file('games/questions.txt')
        self.challenges = self._load_text_file('games/challenges.txt')
        self.confessions = self._load_text_file('games/confessions.txt')
        self.mentions = self._load_text_file('games/mentions.txt')
    
    def _load_text_file(self, filename):
        """تحميل ملف نصي"""
        try:
            file_path = Path(filename)
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return [line.strip() for line in f if line.strip()]
            return []
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return []
    
    def start_game(self, game_type, group_id):
        """بدء لعبة جديدة"""
        from games.song_game import SongGame
        from games.opposite_game import OppositeGame
        from games.compatibility_game import CompatibilityGame
        from games.fast_typing_game import FastTypingGame
        from games.chain_words_game import ChainWordsGame
        from games.human_animal_plant_game import HumanAnimalPlantGame
        from games.letters_words_game import LettersWordsGame
        from games.category_letter_game import CategoryLetterGame
        from games.mafia_game import MafiaGame
        
        # إنشاء اللعبة المناسبة
        game_classes = {
            'song': SongGame,
            'opposite': OppositeGame,
            'compatibility': CompatibilityGame,
            'fast_typing': FastTypingGame,
            'chain': ChainWordsGame,
            'human_animal': HumanAnimalPlantGame,
            'letters': LettersWordsGame,
            'category': CategoryLetterGame,
            'mafia': MafiaGame
        }
        
        game_class = game_classes.get(game_type)
        if not game_class:
            return None
        
        # إنشاء وبدء اللعبة
        game = game_class(self.line_bot_api)
        self.active_games[group_id] = {
            'type': game_type,
            'instance': game
        }
        
        return game.start_game()
    
    def get_game(self, group_id):
        """الحصول على اللعبة النشطة"""
        game_data = self.active_games.get(group_id)
        if game_data:
            return game_data['instance']
        return None
    
    def check_answer(self, group_id, text, user_id, display_name):
        """فحص الإجابة في اللعبة النشطة"""
        game = self.get_game(group_id)
        if not game:
            return None
        
        return game.check_answer(text, user_id, display_name)
    
    def next_question(self, group_id):
        """الانتقال للسؤال التالي"""
        game = self.get_game(group_id)
        if not game:
            return None
        
        return game.next_question()
    
    def stop_game(self, group_id):
        """إيقاف اللعبة"""
        if group_id in self.active_games:
            del self.active_games[group_id]
            return True
        return False
    
    # الألعاب البسيطة بدون تسجيل
    
    def get_random_question(self):
        """الحصول على سؤال عشوائي"""
        if not self.questions:
            return "لا توجد أسئلة متاحة حالياً"
        return random.choice(self.questions)
    
    def get_random_challenge(self):
        """الحصول على تحدي عشوائي"""
        if not self.challenges:
            return "لا توجد تحديات متاحة حالياً"
        return random.choice(self.challenges)
    
    def get_random_confession(self):
        """الحصول على اعتراف عشوائي"""
        if not self.confessions:
            return "لا توجد اعترافات متاحة حالياً"
        return random.choice(self.confessions)
    
    def get_random_mention(self):
        """الحصول على منشن عشوائي"""
        if not self.mentions:
            return "لا توجد منشنات متاحة حالياً"
        return random.choice(self.mentions)
