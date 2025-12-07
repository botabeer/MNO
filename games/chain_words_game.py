# chain_words_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import COLORS
from games.game_helpers import normalize_text, create_game_header, create_progress_box, create_separator, create_action_buttons, create_winner_card

class ChainWordsGame:
    def __init__(self, line_bot_api, total_rounds=5):
        self.line_bot_api = line_bot_api
        self.start_words = ["قلم","كتاب","مدرسة","باب","نافذة","طاولة","كرسي","حديقة"]
        self.current_word = None
        self.used_words = set()
        self.round_count = 0
        self.max_rounds = total_rounds
        self.player_scores = {}
        self.answered_users = set()
        self.registered = set()

    def register_player(self, user_id, name):
        self.registered.add(user_id)

    def start_game(self):
        self.current_word = random.choice(self.start_words)
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
                {"type":"text","text":f"الكلمة: {self.current_word}","size":"xxl","color":COLORS['primary'],"align":"center","weight":"bold"},
                {"type":"text","text":f"اكتب كلمة تبدأ بحرف: {last_letter}","size":"md","color":COLORS['text_dark'],"wrap":True,"margin":"md","align":"center"}
            ], "margin":"lg"},
            create_separator(),
            *create_action_buttons()
        ]
        return FlexMessage(alt_text="سلسلة الكلمات", contents=FlexContainer.from_dict({"type":"bubble","body":{"type":"box","layout":"vertical","spacing":"md","contents":contents,"backgroundColor":COLORS['card_bg'],"paddingAll":"18px"}}))

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
        if answer.lower() in ['لمح','تلميح']:
            return {'response': TextMessage(text=f"يبدأ بحرف: {last_letter}\nمثال: كلمة تبدأ بهذا الحرف"), 'points':0, 'correct':False}
        if answer.lower() in ['جاوب','الجواب']:
            self.answered_users.add(user_id)
            if self.round_count + 1 < self.max_rounds:
                return {'response': TextMessage(text=f"يمكنك كتابة أي كلمة تبدأ بحرف: {last_letter}"), 'points':0, 'correct':False, 'next_question':True}
            return self._end_game()

        normalized_last = 'ه' if last_letter in ['ة','ه'] else last_letter
        first_letter = answer[0]
        first_letter = 'ه' if first_letter in ['ة','ه'] else first_letter

        normalized_answer = normalize_text(answer)
        if normalized_answer in self.used_words:
            return {'response': TextMessage(text="هذه الكلمة استخدمت من قبل"), 'points':0, 'correct':False}

        if first_letter == normalized_last:
            self.used_words.add(normalized_answer)
            self.current_word = answer
            points = 1
            self.player_scores.setdefault(user_id, {'name':display_name,'score':0})
            self.player_scores[user_id]['score'] += points
            self.answered_users.add(user_id)
            if self.round_count + 1 < self.max_rounds:
                return {'response': TextMessage(text=f"اجابة صحيحة {display_name}\n+{points} نقطة"), 'points':points, 'correct':True, 'next_question':True}
            return self._end_game()
        return {'response': TextMessage(text=f"يجب أن تبدأ الكلمة بحرف: {last_letter}"), 'points':0, 'correct':False}

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبة"), 'points':0, 'correct':False, 'game_over':True}
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        return {'response': FlexMessage(alt_text="نتائج اللعبة", contents=FlexContainer.from_dict(create_winner_card(winner, sorted_players, "سلسلة"))), 'points': winner['score'], 'correct':True, 'game_over':True}
