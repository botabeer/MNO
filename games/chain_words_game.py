# games/chain_words.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import COLORS
from games.game_helpers import normalize_text, create_game_header, create_progress_box, create_separator, create_action_buttons, create_winner_card
from storage import Storage

START_WORDS = [
    "قلم", "كتاب", "مدرسة", "باب", "نافذة", "طاولة", "كرسي", "حديقة", "شجرة", "زهرة",
    "سماء", "بحر", "جبل", "نهر", "وادي", "صحراء", "غابة", "حقل", "مزرعة", "قرية"
]

class ChainWordsGame:
    TAG = "سلسله"
    def __init__(self, line_bot_api, storage: Storage):
        self.line_bot_api = line_bot_api
        self.storage = storage
        self.max_rounds = 5
        self.reset_game()

    def reset_game(self):
        self.current_word = None
        self.used_words = set()
        self.round_count = 0
        self.player_scores = {}
        self.answered_users = set()

    def start_game(self):
        self.current_word = random.choice(START_WORDS)
        self.used_words = {normalize_text(self.current_word)}
        self.round_count = 0
        self.player_scores = {}
        self.answered_users = set()
        return self._show_question()

    def _show_question(self):
        last_letter = self.current_word[-1]
        contents = [
            create_game_header("سلسلة الكلمات"),
            create_progress_box(self.round_count + 1, self.max_rounds),
            create_separator(),
            {"type":"box","layout":"vertical","contents":[
                {"type":"text","text":f"الكلمة: {self.current_word}","size":"xxl","color":COLORS['primary'],"weight":"bold","align":"center"},
                {"type":"text","text":f"اكتب كلمة تبدأ بحرف: {last_letter}","size":"md","color":COLORS['text_dark'],"wrap":True,"margin":"md","align":"center"}
            ], "margin":"lg"},
            create_separator(),
            *create_action_buttons()
        ]
        bubble = {"type":"bubble","body":{"type":"box","layout":"vertical","spacing":"md","contents":contents,"backgroundColor":COLORS['card_bg'],"paddingAll":"20px"}}
        return FlexMessage(alt_text="سلسلة الكلمات", contents=FlexContainer.from_dict(bubble))

    def next_question(self):
        if self.round_count < self.max_rounds:
            self.answered_users = set()
            return self._show_question()
        return None

    def check_answer(self, answer, user_id, display_name):
        if not answer:
            return None
        user = self.storage.get_user(user_id)
        if not user or self.TAG not in user.get("registered_games", []):
            return {'response': TextMessage(text="غير مسجل في اللعبة — استخدم أمر الانضمام أولاً."), 'points': 0, 'correct': False}
        self.storage.touch_user(user_id)

        if user_id in self.answered_users:
            return None

        answer = answer.strip()
        if answer.lower() in ['لمح', 'تلميح']:
            last_letter = self.current_word[-1]
            return {'response': TextMessage(text=f"يبدأ بحرف: {last_letter}\nمثال: كلمة تبدأ بهذا الحرف"), 'points': 0, 'correct': False}

        if answer.lower() in ['جاوب', 'الجواب']:
            self.answered_users.add(user_id)
            if self.round_count + 1 < self.max_rounds:
                last_letter = self.current_word[-1]
                return {'response': TextMessage(text=f"يمكنك كتابة أي كلمة تبدأ بحرف: {last_letter}"), 'points': 0, 'correct': False, 'next_question': True}
            return self._end_game()

        normalized_last = 'ه' if self.current_word[-1] in ['ة','ه'] else self.current_word[-1]
        normalized_answer = normalize_text(answer)
        if normalized_answer in self.used_words:
            return {'response': TextMessage(text="هذه الكلمة استخدمت من قبل"), 'points': 0, 'correct': False}
        first_letter = answer[0]
        first_letter = 'ه' if first_letter in ['ه','ة'] else first_letter

        if first_letter == normalized_last or (normalized_last == 'ه' and first_letter in ['ه','ة']):
            self.used_words.add(normalized_answer)
            self.current_word = answer
            self.round_count += 1
            points = 1
            self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})
            self.player_scores[user_id]['score'] += points
            self.answered_users.add(user_id)
            if self.round_count < self.max_rounds:
                return {'response': TextMessage(text=f"اجابة صحيحة {display_name}\n+{points} نقطة"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
            return self._end_game()

        return {'response': TextMessage(text=f"يجب أن تبدأ الكلمة بحرف: {self.current_word[-1]}"), 'points': 0, 'correct': False}

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبة"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        winner_card_dict = create_winner_card(winner, sorted_players, self.TAG)
        return {'response': FlexMessage(alt_text="نتائج اللعبة", contents=FlexContainer.from_dict(winner_card_dict)), 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
