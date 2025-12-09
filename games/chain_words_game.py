# games/chain_words_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from games.game_helpers import normalize_text, create_winner_card, create_question_card
from database import Database

class ChainWordsGame:
    START_WORDS = ['قلم', 'كتاب', 'مدرسة', 'باب', 'نافذة', 'طاولة', 'كرسي', 'حديقة', 'شجرة', 'زهرة']

    def __init__(self, line_bot_api, total_rounds=5):
        self.line_bot_api = line_bot_api
        self.max_rounds = total_rounds
        self.current_word = None
        self.used_words = set()
        self.round_count = 0
        self.player_scores = {}
        self.answered_users = set()
        self.registered = set()

    def register_player(self, user_id, display_name):
        self.registered.add(user_id)
        return True

    def start_game(self):
        self.current_word = random.choice(self.START_WORDS)
        self.used_words = {normalize_text(self.current_word)}
        self.round_count = 0
        self.player_scores = {}
        self.answered_users = set()
        return self._show_question()

    def _show_question(self):
        last_letter = self.current_word[-1]
        question_text = f"الكلمة الحالية: {self.current_word}\n\nاكتب كلمة تبدأ بحرف: {last_letter}"
        return create_question_card(question_text, self.round_count + 1, self.max_rounds, "سلسلة الكلمات", theme="light")

    def next_question(self):
        self.round_count += 1
        if self.round_count < self.max_rounds:
            self.answered_users = set()
            return self._show_question()
        return None

    def check_answer(self, answer, user_id, display_name):
        if user_id not in self.registered:
            return None
        if user_id in self.answered_users:
            return None

        answer = answer.strip()
        last_letter = self.current_word[-1]
        answer_lower = answer.lower()
        theme = Database.get_user_theme(user_id)

        if answer_lower in ['لمح', 'تلميح']:
            return {'response': TextMessage(text=f"يبدأ بحرف: {last_letter}\nمثال: اي كلمة تبدأ بهذا الحرف"), 'points': 0, 'correct': False}

        if answer_lower in ['جاوب', 'الجواب', 'الحل']:
            self.answered_users.add(user_id)
            if self.round_count + 1 < self.max_rounds:
                return {'response': TextMessage(text=f"يمكنك كتابة اي كلمة تبدأ بحرف: {last_letter}"), 'points': 0, 'correct': False, 'next_question': True}
            else:
                return self._end_game(user_id)

        normalized_last = 'ه' if last_letter in ['ة', 'ه'] else last_letter
        first_letter = answer[0]
        first_letter = 'ه' if first_letter in ['ة', 'ه'] else first_letter
        normalized_answer = normalize_text(answer)

        if normalized_answer in self.used_words:
            return {'response': TextMessage(text="هذه الكلمة استخدمت من قبل"), 'points': 0, 'correct': False}

        if first_letter == normalized_last:
            self.used_words.add(normalized_answer)
            self.current_word = answer
            points = 1
            self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})
            self.player_scores[user_id]['score'] += points
            self.answered_users.add(user_id)

            if self.round_count + 1 < self.max_rounds:
                return {'response': TextMessage(text=f"اجابة صحيحة {display_name}\n+{points} نقطة"), 'points': points, 'correct': True, 'next_question': True}
            else:
                return self._end_game(user_id)

        return {'response': TextMessage(text=f"يجب ان تبدأ الكلمة بحرف: {last_letter}"), 'points': 0, 'correct': False}

    def _end_game(self, user_id):
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبة بدون فائز"), 'points': 0, 'correct': False, 'game_over': True}

        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        theme = Database.get_user_theme(user_id)

        return {
            'response': FlexMessage(
                alt_text="نتائج اللعبة",
                contents=FlexContainer.from_dict(create_winner_card(winner, sorted_players, "سلسلة الكلمات", theme=theme))
            ),
            'points': winner['score'],
            'correct': True,
            'won': True,
            'game_over': True
        }
