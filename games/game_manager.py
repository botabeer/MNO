from games.song_game import SongGame
from games.opposite_game import OppositeGame
from games.fast_typing_game import FastTypingGame
from games.chain_words_game import ChainWordsGame
from games.human_animal_plant_game import HumanAnimalPlantGame
from games.letters_words_game import LettersWordsGame
from games.category_letter_game import CategoryLetterGame
from games.compatibility_game import CompatibilityGame
from games.mafia_game import MafiaGame
import random
import os
import logging

logger = logging.getLogger(__name__)

class GameManager:
    """مدير الألعاب - يدير جميع الألعاب النشطة"""
    
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.active_games = {}
        
        # تحميل الملفات النصية
        self.questions = self._load_file('games/questions.txt')
        self.challenges = self._load_file('games/challenges.txt')
        self.confessions = self._load_file('games/confessions.txt')
        self.mentions = self._load_file('games/mentions.txt')
        
        # قائمة الألعاب المتاحة
        self.game_classes = {
            'song': SongGame,
            'opposite': OppositeGame,
            'fast_typing': FastTypingGame,
            'chain': ChainWordsGame,
            'human_animal': HumanAnimalPlantGame,
            'letters': LettersWordsGame,
            'category': CategoryLetterGame,
            'compatibility': CompatibilityGame,
            'mafia': MafiaGame
        }
        
        logger.info("GameManager initialized")
    
    def _load_file(self, filepath):
        """تحميل ملف نصي"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f if line.strip()]
                    logger.info(f"Loaded {len(lines)} lines from {filepath}")
                    return lines
        except Exception as e:
            logger.error(f"Error loading file {filepath}: {e}")
        
        return []
    
    def start_game(self, game_type, group_id):
        """بدء لعبة جديدة"""
        if game_type not in self.game_classes:
            logger.warning(f"Unknown game type: {game_type}")
            return None
        
        try:
            # إنشاء اللعبة
            game_class = self.game_classes[game_type]
            game = game_class(self.line_bot_api)
            
            # حفظ اللعبة
            self.active_games[group_id] = {
                'type': game_type,
                'game': game
            }
            
            logger.info(f"Started game {game_type} for group {group_id}")
            
            # بدء اللعبة
            return game.start_game()
        
        except Exception as e:
            logger.error(f"Error starting game {game_type}: {e}")
            return None
    
    def get_game(self, group_id):
        """الحصول على اللعبة النشطة"""
        if group_id in self.active_games:
            return self.active_games[group_id]['game']
        return None
    
    def check_answer(self, group_id, answer, user_id, display_name):
        """التحقق من الإجابة"""
        game = self.get_game(group_id)
        if not game:
            return None
        
        try:
            return game.check_answer(answer, user_id, display_name)
        except Exception as e:
            logger.error(f"Error checking answer for group {group_id}: {e}")
            return None
    
    def next_question(self, group_id):
        """الانتقال للسؤال التالي"""
        game = self.get_game(group_id)
        if not game:
            return None
        
        try:
            return game.next_question()
        except Exception as e:
            logger.error(f"Error getting next question for group {group_id}: {e}")
            return None
    
    def stop_game(self, group_id):
        """إيقاف اللعبة"""
        if group_id in self.active_games:
            game_type = self.active_games[group_id]['type']
            del self.active_games[group_id]
            logger.info(f"Stopped game {game_type} for group {group_id}")
            return True
        return False
    
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
    
    def get_active_games_count(self):
        """عدد الألعاب النشطة"""
        return len(self.active_games)
    
    def get_active_games_info(self):
        """معلومات الألعاب النشطة"""
        return {
            group_id: {
                'type': info['type'],
                'current_question': info['game'].current_question if hasattr(info['game'], 'current_question') else None
            }
            for group_id, info in self.active_games.items()
        }
