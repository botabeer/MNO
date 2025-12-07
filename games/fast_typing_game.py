# fast_typing_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random, time
from constants import COLORS
from games.game_helpers import normalize_text, create_game_header, create_progress_box, create_separator, create_action_buttons, create_winner_card

class FastTypingGame:
    def __init__(self, line_bot_api, total_questions=5):
        self.line_bot_api = line_bot_api
        self.phrases = ["اكتب هذه العبارة بسرعة", "السماء زرقاء والشمس ساطعة", "التحدي يبدأ الآن", "سجل اسمك لتشارك"]
        self.questions = []
        self.current_question = 0
        self.total_questions = total_questions
        self.player_scores = {}
        self.first_answer_time = None
        self.question_answered = False
        self.registered = set()

    def register_player(self, uid, name):
        self.registered.add(uid)

    def start_game(self):
        self.questions = random.sample(self.phrases, min(self.total_questions,len(self.phrases)))
        self.current_question = 0
        self.player_scores = {}
        self.question_answered = False
        return self._show_question()

    def _show_question(self):
        phrase = self.questions[self.current_question]
        self.question_answered = False
        self.first_answer_time = time.time()
        contents = [
            create_game_header("التايب السريع"),
            create_progress_box(self.current_question+1,self.total_questions),
            create_separator(),
            {"type":"text","text":phrase,"size":"lg","weight":"bold","color":COLORS['text_dark'],"align":"center","margin":"lg"},
            create_separator(),
            *create_action_buttons()
        ]
        return FlexMessage(alt_text="التايب السريع", contents=FlexContainer.from_dict({"type":"bubble","body":{"type":"box","layout":"vertical","spacing":"md","contents":contents,"backgroundColor":COLORS['card_bg'],"paddingAll":"18px"}}))

    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.question_answered = False
            return self._show_question()
        return None

    def check_answer(self, text, user_id, display_name):
        if user_id not in self.registered:
            return None
        phrase = self.questions[self.current_question]
        if text.strip().lower() in ['لمح','تلميح']:
            return {'response': TextMessage(text=f"اكتب العبارة التالية بسرعة:\n{phrase}"), 'points':0, 'correct':False}
        if text.strip().lower() in ['جاوب','الجواب','الحل']:
            return {'response': TextMessage(text=f"الإجابة: {phrase}"), 'points':0, 'correct':False, 'next_question':True}
        if self.question_answered:
            return None
        if normalize_text(text) == normalize_text(phrase):
            self.player_scores.setdefault(user_id, {'name':display_name,'score':0})
            self.player_scores[user_id]['score'] += 1
            self.question_answered = True
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"اجابة صحيحة {display_name}\n+1 نقطة"), 'points':1, 'correct':True, 'next_question':True}
            return self._end_game()
        return None

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبة بدون فائز"), 'points':0, 'game_over':True}
        sorted_players = sorted(self.player_scores.items(), key=lambda x:x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        return {'response': FlexMessage(alt_text="نتائج اللعبة", contents=FlexContainer.from_dict(create_winner_card(winner, sorted_players, "تايب"))), 'points': winner['score'], 'game_over':True}
