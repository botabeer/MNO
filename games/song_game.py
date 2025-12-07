# games/song_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import COLORS
from games.game_helpers import normalize_text, create_hint_text, create_game_header, create_progress_box, create_separator, create_action_buttons, create_winner_card
from storage import Storage

# SONGS: (استخدم القائمة التي أعطيتها أو وسعها حسب الحاجة)
SONGS = [
    {'lyrics':'رجعت لي أيام الماضي معاك','singer':'أم كلثوم'},
    {'lyrics':'جلست والخوف بعينيها تتأمل فنجاني','singer':'عبد الحليم حافظ'},
    {'lyrics':'تملي معاك ولو حتى بعيد عني','singer':'عمرو دياب'},
    {'lyrics':'يا بنات يا بنات','singer':'نانسي عجرم'},
    {'lyrics':'قولي أحبك كي تزيد وسامتي','singer':'كاظم الساهر'},
    {'lyrics':'أنا لحبيبي وحبيبي إلي','singer':'فيروز'},
    # ... أكمل أو استورد من ملف خارجي
]

class SongGame:
    TAG = "اغنيه"
    def __init__(self, line_bot_api, storage: Storage):
        self.line_bot_api = line_bot_api
        self.storage = storage
        self.songs = SONGS.copy()
        self.total_questions = 5
        self.reset_game()

    def reset_game(self):
        self.questions = []
        self.current_question = 0
        self.player_scores = {}
        self.question_answered = False
        self.hints_used = set()

    def start_game(self, total_questions: int = 5):
        self.total_questions = min(total_questions, len(self.songs))
        self.questions = random.sample(self.songs, self.total_questions)
        self.current_question = 0
        self.player_scores = {}
        self.question_answered = False
        self.hints_used = set()
        return self._show_question()

    def _show_question(self):
        song = self.questions[self.current_question]
        contents = [
            create_game_header("لعبة الأغنية"),
            create_progress_box(self.current_question + 1, self.total_questions),
            create_separator(),
            {
                "type":"box","layout":"vertical","contents":[
                    {"type":"text","text":song['lyrics'],"size":"lg","color":COLORS['text_dark'],"wrap":True,"weight":"bold","align":"center"},
                    {"type":"text","text":"من المغني؟","size":"md","color":COLORS['primary'],"margin":"md","align":"center"}
                ], "margin":"lg"
            },
            create_separator(),
            *create_action_buttons()
        ]
        bubble = {"type":"bubble","body":{"type":"box","layout":"vertical","spacing":"md","contents":contents,"backgroundColor":COLORS['card_bg'],"paddingAll":"20px"}}
        return FlexMessage(alt_text="لعبة الأغنية", contents=FlexContainer.from_dict(bubble))

    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.question_answered = False
            self.hints_used = set()
            return self._show_question()
        return None

    def check_answer(self, answer, user_id, display_name):
        if not answer:
            return None
        # فقط المستخدمين المسجلين في اللعبة تُحسب إجاباتهم
        user = self.storage.get_user(user_id)
        if not user or self.TAG not in user.get("registered_games", []):
            return {'response': TextMessage(text="غير مسجل في لعبة الأغنية — استخدم أمر الانضمام أولاً."), 'points': 0, 'correct': False}

        # تسجيل نشاط
        self.storage.touch_user(user_id)

        song = self.questions[self.current_question]
        a = answer.strip()

        if a.lower() in ['لمح', 'تلميح']:
            if user_id in self.hints_used:
                return {'response': TextMessage(text="استخدمت التلميح لهذا السؤال بالفعل"), 'points': 0, 'correct': False}
            self.hints_used.add(user_id)
            hint = create_hint_text(song['singer'])
            return {'response': TextMessage(text=hint), 'points': 0, 'correct': False}

        if a.lower() in ['جاوب', 'الجواب', 'الحل']:
            self.question_answered = True
            reveal = song['singer']
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"الإجابة: {reveal}"), 'points': 0, 'correct': False, 'next_question': True}
            return self._end_game()

        if self.question_answered:
            return None

        if normalize_text(a) == normalize_text(song['singer']):
            points = 1
            self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})
            self.player_scores[user_id]['score'] += points
            self.question_answered = True
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"إجابة صحيحة {display_name}\n+{points} نقطة"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
            return self._end_game()

        return {'response': TextMessage(text="إجابة خاطئة"), 'points': 0, 'correct': False}

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبة بدون فائز"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        winner_card_dict = create_winner_card(winner, sorted_players, self.TAG)
        return {'response': FlexMessage(alt_text="نتائج اللعبة", contents=FlexContainer.from_dict(winner_card_dict)), 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
