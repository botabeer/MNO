# category_letter_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import COLORS
from games.game_helpers import normalize_text, create_game_header, create_progress_box, create_separator, create_action_buttons, create_winner_card

class CategoryLetterGame:
    def __init__(self, line_bot_api, total_questions=5):
        self.line_bot_api = line_bot_api
        self.challenges = [
            {"category": "المطبخ", "letter": "ق", "answers": ["قدر", "قلايه", "قهوه", "قنينه", "قباقيب"]},
            {"category": "حيوان", "letter": "ب", "answers": ["بطه", "بقره", "ببغاء", "بومه", "بعير"]},
            {"category": "فاكهه", "letter": "ت", "answers": ["تفاح", "توت", "تمر", "تين", "ترنج"]}
            # أضف باقي التحديات حسب الملف
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = total_questions
        self.player_scores = {}
        self.answered_users = set()
        self.registered = set()  # اللاعبين المسجلين في هذه اللعبة

    def register_player(self, user_id, display_name):
        self.registered.add(user_id)
        # يمكن تخزين الاسم إن شئت
        return True

    def start_game(self):
        self.questions = random.sample(self.challenges, min(self.total_questions, len(self.challenges)))
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        return self._show_question()

    def _show_question(self):
        challenge = self.questions[self.current_question]
        contents = [
            create_game_header("فئة و حرف"),
            create_progress_box(self.current_question + 1, self.total_questions),
            create_separator(),
            {"type":"box","layout":"vertical","contents":[
                {"type":"text","text":f"الفئة: {challenge['category']}","size":"lg","color":COLORS['text_dark'],"align":"center","weight":"bold"},
                {"type":"text","text":f"الحرف: {challenge['letter']}","size":"xxl","color":COLORS['primary'],"align":"center","weight":"bold","margin":"md"}
            ],"margin":"lg"},
            create_separator(),
            *create_action_buttons()
        ]
        return FlexMessage(alt_text="فئة وحرف", contents=FlexContainer.from_dict({"type":"bubble","body":{"type":"box","layout":"vertical","spacing":"md","contents":contents,"backgroundColor":COLORS['card_bg'],"paddingAll":"18px"}}))

    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.answered_users = set()
            return self._show_question()
        return None

    def check_answer(self, text, user_id, display_name):
        # ignore non-registered
        if user_id not in self.registered:
            return None
        if user_id in self.answered_users:
            return None

        challenge = self.questions[self.current_question]
        txt = text.strip().lower()
        if txt in ['لمح','تلميح']:
            sample = challenge['answers'][0]
            return {'response': TextMessage(text=f"يبدا بحرف: {sample[0]}\nعدد الحروف: {len(sample)}"), 'points':0, 'correct':False}

        if txt in ['جاوب','الجواب','الحل']:
            self.answered_users.add(user_id)
            answers = ' - '.join(challenge['answers'][:3])
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"بعض الاجابات:\n{answers}"), 'points':0, 'correct':False, 'next_question':True}
            return self._end_game()

        normalized = normalize_text(text)
        valid_answers = [normalize_text(a) for a in challenge['answers']]
        if normalized in valid_answers:
            self.player_scores.setdefault(user_id, {'name': display_name, 'score':0})
            self.player_scores[user_id]['score'] += 1
            self.answered_users.add(user_id)
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"اجابة صحيحة {display_name}\n+1 نقطة"), 'points':1, 'correct':True, 'next_question':True}
            return self._end_game()
        return None

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبة بدون فائز"), 'points':0, 'correct':False, 'game_over':True}
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        return {'response': FlexMessage(alt_text="نتائج اللعبة", contents=FlexContainer.from_dict(create_winner_card(winner, sorted_players, "فئة"))), 'points': winner['score'], 'correct':True, 'game_over':True}
