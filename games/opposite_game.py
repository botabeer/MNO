# opposite_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import COLORS
from games.game_helpers import normalize_text, create_game_header, create_progress_box, create_separator, create_action_buttons, create_winner_card

class OppositeGame:
    def __init__(self, line_bot_api, total_questions=5):
        self.line_bot_api = line_bot_api
        self.all_words = [
            {"word":"كبير","opposite":"صغير"},{"word":"طويل","opposite":"قصير"},
            {"word":"سريع","opposite":"بطيء"},{"word":"ساخن","opposite":"بارد"}
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = total_questions
        self.player_scores = {}
        self.answered_users = set()
        self.hints_used = {}
        self.registered = set()

    def register_player(self, uid, name):
        self.registered.add(uid)

    def start_game(self):
        self.questions = random.sample(self.all_words, min(self.total_questions,len(self.all_words)))
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        self.hints_used = {}
        return self._show_question()

    def _show_question(self):
        word = self.questions[self.current_question]
        contents = [
            create_game_header("لعبة الأضداد"),
            create_progress_box(self.current_question+1,self.total_questions),
            create_separator(),
            {"type":"text","text":f"ما هو عكس: {word['word']}","size":"lg","color":COLORS['text_dark'],"align":"center","weight":"bold","margin":"lg"},
            create_separator(),
            *create_action_buttons()
        ]
        return FlexMessage(alt_text="لعبة الأضداد", contents=FlexContainer.from_dict({"type":"bubble","body":{"type":"box","layout":"vertical","spacing":"md","contents":contents,"backgroundColor":COLORS['card_bg'],"paddingAll":"18px"}}))

    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.answered_users = set()
            self.hints_used = {}
            return self._show_question()
        return None

    def check_answer(self, answer, user_id, display_name):
        if user_id not in self.registered:
            return None
        if user_id in self.answered_users:
            return None
        word = self.questions[self.current_question]
        txt = answer.strip().lower()
        if txt in ['لمح','تلميح']:
            if user_id not in self.hints_used:
                self.hints_used[user_id] = True
                return {'response': TextMessage(text=f"يبدأ بحرف: {word['opposite'][0]}\nعدد الحروف: {len(word['opposite'])}"), 'points':0, 'correct':False}
            return {'response': TextMessage(text="استخدمت التلميح"), 'points':0, 'correct':False}
        if txt in ['جاوب','الجواب','الحل']:
            self.answered_users.add(user_id)
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"الاجابة: {word['opposite']}"), 'points':0, 'correct':False, 'next_question':True}
            return self._end_game()
        if normalize_text(answer) == normalize_text(word['opposite']):
            self.player_scores.setdefault(user_id, {'name':display_name,'score':0})
            self.player_scores[user_id]['score'] += 1
            self.answered_users.add(user_id)
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"اجابة صحيحة {display_name}\n+1 نقطة"), 'points':1, 'correct':True, 'next_question':True}
            return self._end_game()
        return None

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبة"), 'points':0, 'game_over':True}
        sorted_players = sorted(self.player_scores.items(), key=lambda x:x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        return {'response': FlexMessage(alt_text="نتائج اللعبة", contents=FlexContainer.from_dict(create_winner_card(winner, sorted_players, "ضد"))), 'points': winner['score'], 'game_over':True}
