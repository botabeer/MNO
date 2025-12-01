"""
Game Manager - مدير الألعاب
==============================
يدير جميع الألعاب والنصوص العشوائية
"""

from games.song_game import SongGame
from games.opposite_game import OppositeGame
from games.fast_typing_game import FastTypingGame
from games.chain_words_game import ChainWordsGame
from games.human_animal_plant_game import HumanAnimalPlantGame
from games.letters_words_game import LettersWordsGame
from games.compatibility_game import CompatibilityGame
from games.differences_game import DifferencesGame
from games.mafia_game import MafiaGame
import random
import os


class GameManager:
    """مدير الألعاب الرئيسي"""
    
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        
        # الألعاب النشطة حسب المجموعة/المستخدم
        # الشكل: { group_id: {'type': game_type, 'game': game_instance} }
        self.active_games = {}
        
        # تحميل الملفات النصية (نصوص مستقلة وليست Flex)
        self.questions = self._load_file('games/questions.txt')
        self.challenges = self._load_file('games/challenges.txt')
        self.confessions = self._load_file('games/confessions.txt')
        self.mentions = self._load_file('games/mentions.txt')
    
    def _load_file(self, filepath):
        """تحميل ملف نصي — إرجاع قائمة الأسطر (نظيفة)"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f if line.strip()]
                    return lines
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
        return []
    
    # ===== إدارة الألعاب =====
    
    def start_game(self, game_type, group_id):
        """بدء لعبة جديدة - يرجع رسالة/Flex حسب اللعبة"""
        game_classes = {
            'song': SongGame,
            'opposite': OppositeGame,
            'fast_typing': FastTypingGame,
            'chain': ChainWordsGame,
            'human_animal': HumanAnimalPlantGame,
            'letters': LettersWordsGame,
            'compatibility': CompatibilityGame,
            'differences': DifferencesGame,
            'mafia': MafiaGame
        }
        
        if game_type in game_classes:
            # انشئ نسخة جديدة من اللعبة و خزّنها
            game = game_classes[game_type](self.line_bot_api)
            self.active_games[group_id] = {
                'type': game_type,
                'game': game
            }
            # ارجع رسالة البداية التي تصنعها اللعبة نفسها
            return game.start_game()
        
        return None
    
    def get_game(self, group_id):
        """الحصول على اللعبة النشطة"""
        if group_id in self.active_games:
            return self.active_games[group_id]['game']
        return None
    
    def check_answer(self, group_id, answer, user_id, display_name):
        """التحقق من الإجابة — يعيد نفس القيم التي تعيدها اللعبة الفرعية"""
        game = self.get_game(group_id)
        if game:
            return game.check_answer(answer, user_id, display_name)
        return None
    
    def next_question(self, group_id):
        """السؤال التالي"""
        game = self.get_game(group_id)
        if game:
            return game.next_question()
        return None
    
    def stop_game(self, group_id):
        """إيقاف اللعبة وإزالتها من الذاكرة"""
        if group_id in self.active_games:
            del self.active_games[group_id]
            return True
        return False
    
    # ===== النصوص العشوائية (نص فقط بدون إيموجي) =====
    
    def get_random_question(self):
        """سؤال عشوائي — نص خام"""
        if self.questions:
            return random.choice(self.questions)
        return "لا توجد أسئلة متاحة"
    
    def get_random_challenge(self):
        """تحدي عشوائي — نص خام"""
        if self.challenges:
            return random.choice(self.challenges)
        return "لا توجد تحديات متاحة"
    
    def get_random_confession(self):
        """اعتراف عشوائي — نص خام"""
        if self.confessions:
            return random.choice(self.confessions)
        return "لا توجد اعترافات متاحة"
    
    def get_random_mention(self):
        """منشن عشوائي — نص خام"""
        if self.mentions:
            return random.choice(self.mentions)
        return "لا توجد منشنات متاحة"
    
    def get_random_member(self, group_id):
        """اختيار عضو عشوائي (placeholder)"""
        # يمكنك ربط هذا بواجهة LINE لاختيار عضو من المجموعة إن رغبت لاحقاً.
        return "عضو عشوائي"
