# letters_words_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import COLORS
from games.game_helpers import normalize_text, create_game_header, create_progress_box, create_separator, create_action_buttons, create_winner_card

class LettersWordsGame:
    def __init__(self, line_bot_api, total_questions=5, words_needed=3):
        self.line_bot_api = line_bot_api
        self.challenges = [
            {"letters":"ق ل م ع ر ك", "answers":["قلم","علم","عمر","رقم","ملك","كرم"]},
            {"letters":"ك ت ا ب ر ل", "answers":["كتاب","تراب","بكر","كبر","بار","كرت"]},
            # أضف المزيد أو حمّل من الملف
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = total_questions
        self.player_scores = {}
        self.found_words = {}
        self.valid_words = []
        self.words_needed = words_needed
        self.hints_used = {}
        self.registered = set()

    def register_player(self, uid, name):
        self.registered.add(uid)

    def start_game(self):
        self.questions = random.sample(self.challenges, min(self.total_questions, len(self.challenges)))
        self.current_question = 0
        self.player_scores = {}
        self.found_words = {}
        self.hints_used = {}
        return self._show_question()

    def _show_question(self):
        challenge = self.questions[self.current_question]
        letters = challenge['letters']
        self.valid_words = [normalize_text(w) for w in challenge['answers']]
        contents = [
            create_game_header("تكوين الكلمات"),
            create_progress_box(self.current_question+1,self.total_questions),
            create_separator(),
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":letters,"size":"xxl","color":COLORS['primary'],"align":"center","weight":"bold"},{"type":"text","text":f"كون {self.words_needed} كلمات من هذه الحروف","size":"sm","color":COLORS['text_dark'],"wrap":True,"align":"center","margin":"md"}],"margin":"lg"},
            create_separator(),
            *create_action_buttons()
        ]
        return FlexMessage(alt_text="تكوين الكلمات", contents=FlexContainer.from_dict({"type":"bubble","body":{"type":"box","layout":"vertical","spacing":"md","contents":contents,"backgroundColor":COLORS['card_bg'],"paddingAll":"18px"}}))

    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.found_words = {}
            self.hints_used = {}
            return self._show_question()
        return None

    def check_answer(self, text, user_id, display_name):
        if user_id not in self.registered:
            return None
        txt = text.strip()
        if txt.lower() in ['لمح','تلميح']:
            if user_id not in self.hints_used:
                self.hints_used[user_id] = True
                sample_word = self.questions[self.current_question]['answers'][0]
                return {'response': TextMessage(text=f"يبدا بحرف: {sample_word[0]}\nعدد الحروف: {len(sample_word)}"), 'points':0, 'correct':False}
            return {'response': TextMessage(text="استخدمت التلميح بالفعل"), 'points':0, 'correct':False}
        if txt.lower() in ['جاوب','الحل','الجواب']:
            some_words = ' - '.join(self.questions[self.current_question]['answers'][:5])
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"بعض الكلمات الصحيحه:\n{some_words}"), 'points':0, 'correct':False, 'next_question':True}
            return self._end_game()
        normalized = normalize_text(txt)
        if user_id in self.found_words and normalized in self.found_words[user_id]:
            return {'response': TextMessage(text="هذه الكلمة سبق وان ادخلتها"), 'points':0, 'correct':False}
        if normalized not in self.valid_words:
            return {'response': TextMessage(text="هذه الكلمه غير صحيحه"), 'points':0, 'correct':False}
        self.found_words.setdefault(user_id, []).append(normalized)
        self.player_scores.setdefault(user_id, {'name':display_name,'score':0})
        self.player_scores[user_id]['score'] += 1
        words_count = len(self.found_words[user_id])
        if words_count >= self.words_needed:
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"اجابه صحيحه {display_name}\n+1 نقطه"), 'points':1, 'correct':True, 'next_question':True}
            return self._end_game()
        return {'response': TextMessage(text=f"كلمه صحيحه\n+1 نقطه\nالكلمات المتبقيه: {self.words_needed-words_count}"), 'points':1, 'correct':True}

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبه"), 'points':0, 'game_over':True}
        sorted_players = sorted(self.player_scores.items(), key=lambda x:x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        return {'response': FlexMessage(alt_text="نتائج اللعبة", contents=FlexContainer.from_dict(create_winner_card(winner, sorted_players, "تكوين"))), 'points': winner['score'], 'game_over':True}
