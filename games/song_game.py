# games/song_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from games.game_helpers import normalize_text, create_hint_text, create_winner_card, create_question_card
from database import Database

class SongGame:
    SONGS=[
{'lyrics':'رجعت لي ايام الماضي معاك','singer':'ام كلثوم'},
{'lyrics':'جلست والخوف بعينيها تتأمل فنجاني','singer':'عبد الحليم حافظ'},
{'lyrics':'تملي معاك ولو حتى بعيد عني','singer':'عمرو دياب'},
{'lyrics':'يا بنات يا بنات','singer':'نانسي عجرم'},
{'lyrics':'قولي احبك كي تزيد وسامتي','singer':'كاظم الساهر'},
{'lyrics':'انا لحبيبي وحبيبي الي','singer':'فيروز'},
{'lyrics':'حبيبي يا كل الحياة اوعدني تبقى معايا','singer':'تامر حسني'},
{'lyrics':'قلبي بيسألني عنك دخلك طمني وينك','singer':'وائل كفوري'},
{'lyrics':'كيف ابين لك شعوري دون ما احكي','singer':'عايض'},
{'lyrics':'اسخر لك غلا وتشوفني مقصر','singer':'عايض'}
    ]

    def __init__(self, line_bot_api, total_questions=5):
        self.line_bot_api = line_bot_api
        self.total_questions = total_questions
        self.questions = []
        self.current_question = 0
        self.player_scores = {}
        self.question_answered = False
        self.registered = set()

    def register_player(self, user_id, display_name):
        self.registered.add(user_id)
        return True

    def start_game(self):
        self.questions = random.sample(self.SONGS, min(self.total_questions, len(self.SONGS)))
        self.current_question = 0
        self.player_scores = {}
        self.question_answered = False
        return self._show_question()

    def _show_question(self):
        song = self.questions[self.current_question]
        lyrics = song['lyrics']
        question_text = f"{lyrics}\n\nمن المغني"
        return create_question_card(question_text, self.current_question + 1, self.total_questions, "الاغنية", theme="light")

    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.question_answered = False
            return self._show_question()
        return None

    def check_answer(self, answer, user_id, display_name):
        if user_id not in self.registered:
            return None
        if self.question_answered:
            return None

        song = self.questions[self.current_question]
        answer_lower = answer.strip().lower()
        theme = Database.get_user_theme(user_id)

        if answer_lower in ['لمح', 'تلميح']:
            hint = create_hint_text(song['singer'], theme=theme)
            return {'response': TextMessage(text=hint), 'points': 0, 'correct': False}

        if answer_lower in ['جاوب', 'الجواب', 'الحل']:
            self.question_answered = True
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"الاجابة: {song['singer']}"), 'points': 0, 'correct': False, 'next_question': True}
            else:
                return self._end_game(user_id)

        if normalize_text(answer) == normalize_text(song['singer']):
            self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})
            self.player_scores[user_id]['score'] += 1
            self.question_answered = True

            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"اجابة صحيحة {display_name}\n+1 نقطة"), 'points': 1, 'correct': True, 'next_question': True}
            else:
                return self._end_game(user_id)
        return None

    def _end_game(self, user_id):
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبة بدون فائز"), 'points': 0, 'correct': False, 'game_over': True}

        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        theme = Database.get_user_theme(user_id)

        return {
            'response': FlexMessage(
                alt_text="نتائج اللعبة",
                contents=FlexContainer.from_dict(create_winner_card(winner, sorted_players, "الاغنية", theme=theme))
            ),
            'points': winner['score'],
            'correct': True,
            'won': True,
            'game_over': True
        }
