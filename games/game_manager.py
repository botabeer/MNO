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

        # الألعاب النشطة
        self.active_games = {}

        # اللاعبين المسجلين بكل مجموعة
        self.joined_players = {}

        # تحميل النصوص
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
            print(f"Error loading {filepath}: {e}")
        return []

    # ========================
    # إدارة التسجيل
    # ========================

    def join_player(self, group_id, user_id):
        if group_id not in self.joined_players:
            self.joined_players[group_id] = set()
        self.joined_players[group_id].add(user_id)

    def is_player_joined(self, group_id, user_id):
        return user_id in self.joined_players.get(group_id, [])

    # ========================
    # إدارة الألعاب
    # ========================

    def start_game(self, game_type, group_id):
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
            game = game_classes[game_type](self.line_bot_api)

            # تحديد عدد الجولات الخاص
            if game_type in ['compatibility', 'differences']:
                game.total_questions = 1
                game.disable_points = True
                game.disable_winner = True
            else:
                game.total_questions = 5

            self.active_games[group_id] = {
                'type': game_type,
                'game': game,
                'answered_users': set()
            }

            return game.start_game()

        return None

    def get_game(self, group_id):
        return self.active_games.get(group_id, {}).get('game')

    def check_answer(self, group_id, answer, user_id, display_name):
        if group_id not in self.active_games:
            return None

        # لا تُحسب الإجابة إلا للمسجلين
        if not self.is_player_joined(group_id, user_id):
            return None

        game_data = self.active_games[group_id]
        game = game_data['game']

        # فقط أول إجابة صحيحة تُحسب
        if user_id in game_data['answered_users']:
            return None

        result = game.check_answer(answer, user_id, display_name)

        if result and result.get('correct'):
            game_data['answered_users'].add(user_id)

        return result

    def next_question(self, group_id):
        if group_id in self.active_games:
            self.active_games[group_id]['answered_users'] = set()
            return self.active_games[group_id]['game'].next_question()
        return None

    def stop_game(self, group_id):
        if group_id in self.active_games:
            del self.active_games[group_id]
            if group_id in self.joined_players:
                del self.joined_players[group_id]
            return True
        return False

    # ========================
    # النصوص فقط (خارج الألعاب)
    # ========================

    def get_random_question(self):
        if self.questions:
            return random.choice(self.questions)
        return "لا توجد أسئلة متاحة"

    def get_random_challenge(self):
        if self.challenges:
            return random.choice(self.challenges)
        return "لا توجد تحديات متاحة"

    def get_random_confession(self):
        if self.confessions:
            return random.choice(self.confessions)
        return "لا توجد اعترافات متاحة"

    def get_random_mention(self):
        if self.mentions:
            return random.choice(self.mentions)
        return "لا توجد منشنات متاحة"

    def get_random_member(self, group_id):
        members = list(self.joined_players.get(group_id, []))
        if members:
            return random.choice(members)
        return "لا يوجد أعضاء"
