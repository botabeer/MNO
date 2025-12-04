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

class GameManager:
    
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.active_games = {}
        self.questions = self._load_file('games/questions.txt')
        self.challenges = self._load_file('games/challenges.txt')
        self.confessions = self._load_file('games/confessions.txt')
        self.mentions = self._load_file('games/mentions.txt')
    
    def _load_file(self, filepath):
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"خطا تحميل {filepath}: {e}")
        return []
    
    def start_game(self, game_type, group_id):
        game_classes = {
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
        
        if game_type in game_classes:
            game = game_classes[game_type](self.line_bot_api)
            self.active_games[group_id] = {'type': game_type, 'game': game}
            return game.start_game()
        return None
    
    def get_game(self, group_id):
        if group_id in self.active_games:
            return self.active_games[group_id]['game']
        return None
    
    def check_answer(self, group_id, answer, user_id, display_name):
        game = self.get_game(group_id)
        if game:
            return game.check_answer(answer, user_id, display_name)
        return None
    
    def next_question(self, group_id):
        game = self.get_game(group_id)
        if game:
            return game.next_question()
        return None
    
    def stop_game(self, group_id):
        if group_id in self.active_games:
            del self.active_games[group_id]
            return True
        return False
    
    def get_random_question(self):
        return random.choice(self.questions) if self.questions else "لا توجد اسئله متاحه"
    
    def get_random_challenge(self):
        return random.choice(self.challenges) if self.challenges else "لا توجد تحديات متاحه"
    
    def get_random_confession(self):
        return random.choice(self.confessions) if self.confessions else "لا توجد اعترافات متاحه"
    
    def get_random_mention(self):
        return random.choice(self.mentions) if self.mentions else "لا توجد منشنات متاحه"
