from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from datetime import datetime
from constants import COLORS
from games.game_helpers import normalize_text, create_game_header, create_progress_box, create_separator, create_action_buttons, create_winner_card

class FastTypingGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.words = [
            "سبحان الله", "الحمد لله", "لا اله الا الله", "الله اكبر", "استغفر الله",
            "لا حول ولا قوه الا بالله", "حسبنا الله ونعم الوكيل", "توكلت على الله",
            "الله يرحمه", "العلم نور", "بارك الله فيك", "جزاك الله خيرا",
            "الله يحفظك", "ما شاء الله", "اللهم صل على محمد", "رب اغفر لي", "اللهم ارحمنا",
            "اللهم اجرني", "اللهم اهدني", "اللهم ارزقني", "اللهم عافني", "اللهم اصلح حالي"
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.start_time = None
        self.time_limit = 30
        self.answered_users = set()

    def start_game(self):
        self.questions = random.sample(self.words, min(self.total_questions, len(self.words)))
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        self.start_time = datetime.now()
        return self._show_question()

    def _show_question(self):
        word = self.questions[self.current_question]
        self.start_time = datetime.now()
        
        contents = [
            create_game_header("الكتابه السريعه"),
            create_progress_box(self.current_question + 1, self.total_questions),
            create_separator(),
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": word, "size": "lg", "color": COLORS['primary'], "weight": "bold", "align": "center", "wrap": True},
                    {"type": "text", "text": "اكتب النص باسرع وقت", "size": "sm", "color": COLORS['text_dark'], "margin": "md", "align": "center"},
                    {"type": "text", "text": f"لديك {self.time_limit} ثانيه", "size": "xs", "color": COLORS['text_light'], "margin": "xs", "align": "center"}
                ],
                "margin": "lg"
            },
            create_separator(),
            *create_action_buttons()
        ]
        
        return FlexMessage(
            alt_text="الكتابه السريعه",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": contents,
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            })
        )

    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.answered_users = set()
            return self._show_question()
        return None

    def check_answer(self, text, user_id, display_name):
        if user_id in self.answered_users:
            return None

        if text.lower() in ['لمح', 'تلميح']:
            word = self.questions[self.current_question]
            return {'response': TextMessage(text=f"يبدأ بحرف: {word[0]}\nعدد الحروف: {len(word)}"), 'points': 0, 'correct': False}

        if text.lower() in ['جاوب', 'الجواب']:
            self.answered_users.add(user_id)
            word = self.questions[self.current_question]
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"الاجابة: {word}"), 'points': 0, 'correct': False, 'next_question': True}
            return self._end_game()

        if self.start_time:
            elapsed = (datetime.now() - self.start_time).seconds
            if elapsed > self.time_limit:
                if self.current_question + 1 < self.total_questions:
                    return {'response': TextMessage(text="انتهى الوقت"), 'points': 0, 'correct': False, 'next_question': True}
                return self._end_game()

        text_normalized = normalize_text(text)
        word_normalized = normalize_text(self.questions[self.current_question])

        if text_normalized == word_normalized:
            elapsed_time = (datetime.now() - self.start_time).total_seconds()
            points = 1
            
            self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0, 'time': 0})
            self.player_scores[user_id]['score'] += points
            self.player_scores[user_id]['time'] += elapsed_time
            self.answered_users.add(user_id)

            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"اجابه صحيحه {display_name}\nالوقت {elapsed_time:.1f} ثانيه\n+{points} نقطه"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
            return self._end_game()
        return None

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبه"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
        
        sorted_players = sorted(self.player_scores.items(), key=lambda x: (x[1]['score'], -x[1]['time']), reverse=True)
        winner = sorted_players[0][1]
        
        winner_card_dict = create_winner_card(winner, sorted_players, "اسرع")
        
        return {
            'response': FlexMessage(alt_text="نتائج اللعبه", contents=FlexContainer.from_dict(winner_card_dict)),
            'points': winner['score'],
            'correct': True,
            'won': True,
            'game_over': True
        }
