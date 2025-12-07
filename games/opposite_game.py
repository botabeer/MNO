# games/opposite_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import COLORS
from games.game_helpers import normalize_text, create_game_header, create_progress_box, create_separator, create_action_buttons, create_winner_card
from storage import Storage

ALL_WORDS = [
    {"word":"كبير","opposite":"صغير"}, {"word":"طويل","opposite":"قصير"},
    {"word":"سريع","opposite":"بطيء"}, {"word":"ساخن","opposite":"بارد"},
    {"word":"نظيف","opposite":"وسخ"}, {"word":"قوي","opposite":"ضعيف"},
    {"word":"سهل","opposite":"صعب"}, {"word":"جميل","opposite":"قبيح"},
    {"word":"غني","opposite":"فقير"}, {"word":"فوق","opposite":"تحت"},
    {"word":"يمين","opposite":"يسار"}, {"word":"أمام","opposite":"خلف"},
    {"word":"داخل","opposite":"خارج"}, {"word":"قريب","opposite":"بعيد"},
    {"word":"جديد","opposite":"قديم"}, {"word":"ثقيل","opposite":"خفيف"},
    {"word":"مظلم","opposite":"مضيء"}, {"word":"صادق","opposite":"كاذب"},
    {"word":"شجاع","opposite":"جبان"}, {"word":"نشيط","opposite":"كسول"}
]

class OppositeGame:
    TAG = "ضد"
    def __init__(self, line_bot_api, storage: Storage):
        self.line_bot_api = line_bot_api
        self.storage = storage
        self.total_questions = 5
        self.reset_game()

    def reset_game(self):
        self.questions = []
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        self.hints_used = {}

    def start_game(self):
        self.questions = random.sample(ALL_WORDS, self.total_questions)
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        self.hints_used = {}
        return self._show_question()

    def _show_question(self):
        word = self.questions[self.current_question]
        contents = [
            create_game_header("لعبة الأضداد"),
            create_progress_box(self.current_question + 1, self.total_questions),
            create_separator(),
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":f"ما هو عكس: {word['word']}", "size":"lg","color":COLORS['text_dark'],"wrap":True,"weight":"bold","align":"center"}],"margin":"lg"},
            create_separator(),
            *create_action_buttons()
        ]
        bubble = {"type":"bubble","body":{"type":"box","layout":"vertical","spacing":"md","contents":contents,"backgroundColor":COLORS['card_bg'],"paddingAll":"20px"}}
        return FlexMessage(alt_text="لعبة الأضداد", contents=FlexContainer.from_dict(bubble))

    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.answered_users = set()
            self.hints_used = {}
            return self._show_question()
        return None

    def check_answer(self, answer, user_id, display_name):
        if not answer:
            return None
        user = self.storage.get_user(user_id)
        if not user or self.TAG not in user.get("registered_games", []):
            return {'response': TextMessage(text="غير مسجل في اللعبة — استخدم أمر الانضمام أولاً."), 'points':0,'correct':False}
        self.storage.touch_user(user_id)
        if user_id in self.answered_users:
            return None

        word = self.questions[self.current_question]
        a = answer.strip()
        if a.lower() in ['لمح','تلميح']:
            if user_id not in self.hints_used:
                self.hints_used[user_id] = True
                return {'response': TextMessage(text=f"يبدأ بحرف: {word['opposite'][0]}\nعدد الحروف: {len(word['opposite'])}"), 'points':0,'correct':False}
            return {'response': TextMessage(text="استخدمت التلميح"), 'points':0,'correct':False}
        if a.lower() in ['جاوب','الجواب']:
            self.answered_users.add(user_id)
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"الاجابة: {word['opposite']}"), 'points':0,'correct':False,'next_question':True}
            return self._end_game()

        if normalize_text(a) == normalize_text(word['opposite']):
            points = 1
            self.player_scores.setdefault(user_id, {'name': display_name, 'score':0})
            self.player_scores[user_id]['score'] += points
            self.answered_users.add(user_id)
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"اجابة صحيحة {display_name}\n+{points} نقطة"), 'points':points,'correct':True,'won':True,'next_question':True}
            return self._end_game()
        return None

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبة"), 'points':0,'correct':False,'won':False,'game_over':True}
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        winner_card_dict = create_winner_card(winner, sorted_players, self.TAG)
        return {'response': FlexMessage(alt_text="نتائج اللعبة", contents=FlexContainer.from_dict(winner_card_dict)), 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
