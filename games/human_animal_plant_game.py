# human_animal_plant_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import COLORS
from games.game_helpers import create_game_header, create_progress_box, create_separator, create_action_buttons, create_winner_card, normalize_text

class HumanAnimalPlantGame:
    def __init__(self, line_bot_api, total_questions=5):
        self.line_bot_api = line_bot_api
        self.letters = list("ابتثجحخدذرزسشصضطظعغفقكلمنهوي")
        self.questions = []
        self.current_question = 0
        self.total_questions = total_questions
        self.player_scores = {}
        self.answered_users = {}
        self.registered = set()

    def register_player(self, uid, name):
        self.registered.add(uid)

    def start_game(self):
        self.questions = random.sample(self.letters, min(self.total_questions, len(self.letters)))
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = {}
        return self._show_question()

    def _show_question(self):
        letter = self.questions[self.current_question]
        contents = [
            create_game_header("إنسان - حيوان - نبات - بلاد"),
            create_progress_box(self.current_question + 1, self.total_questions),
            create_separator(),
            {"type":"box","layout":"vertical","contents":[
                {"type":"text","text":letter,"size":"5xl","color":COLORS['primary'],"weight":"bold","align":"center"},
                {"type":"text","text":"اكتب 4 كلمات تبدأ بهذا الحرف، كل كلمة بسطر منفصل","size":"sm","color":COLORS['text_dark'],"margin":"md","wrap":True,"align":"center"}
            ],"margin":"lg"},
            create_separator(),
            *create_action_buttons()
        ]
        return FlexMessage(alt_text="إنسان حيوان نبات بلاد", contents=FlexContainer.from_dict({"type":"bubble","body":{"type":"box","layout":"vertical","spacing":"md","contents":contents,"backgroundColor":COLORS['card_bg'],"paddingAll":"18px"}}))

    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.answered_users = {}
            return self._show_question()
        return None

    def check_answer(self, text, user_id, display_name):
        if user_id not in self.registered:
            return None
        if user_id in self.answered_users:
            return None
        text = text.strip()
        letter = self.questions[self.current_question]
        if text.lower() in ['لمح','تلميح']:
            return {'response': TextMessage(text=f"يبدأ بحرف: {letter}\nمثال: اسم - حيوان - نبات - بلاد"), 'points':0, 'correct':False}
        if text.lower() in ['جاوب','الجواب','الحل']:
            self.answered_users[user_id] = True
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"اكتب 4 كلمات تبدأ بحرف: {letter}"), 'points':0, 'correct':False, 'next_question':True}
            return self._end_game()
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if len(lines) >= 4:
            valid_count = sum(1 for w in lines[:4] if w and normalize_text(w).startswith(normalize_text(letter)))
            if valid_count >= 1:
                points = valid_count * 3  # مكافأة: 3 لكل كلمة صحيحة
                self.player_scores.setdefault(user_id, {'name':display_name,'score':0})
                self.player_scores[user_id]['score'] += points
                self.answered_users[user_id] = True
                if self.current_question + 1 < self.total_questions:
                    return {'response': TextMessage(text=f"اجابة صحيحة {display_name}\nالكلمات الصحيحة: {valid_count}/4\n+{points} نقطة"), 'points':points, 'correct':True, 'next_question':True}
                return self._end_game()
        return None

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبة"), 'points':0, 'game_over':True}
        sorted_players = sorted(self.player_scores.items(), key=lambda x:x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        return {'response': FlexMessage(alt_text="نتائج اللعبة", contents=FlexContainer.from_dict(create_winner_card(winner, sorted_players, "إنسان-حيوان-نبات-بلاد"))), 'points': winner['score'], 'game_over':True}
