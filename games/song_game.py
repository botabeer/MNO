from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import COLORS
from games.game_helpers import normalize_text, create_hint_text, create_game_header, create_progress_box, create_separator, create_action_buttons, create_winner_card

# قائمة الأغاني (يمكن توسيعها بسهولة)
SONGS = [
    {'lyrics':'رجعت لي أيام الماضي معاك','singer':'أم كلثوم'},
    {'lyrics':'جلست والخوف بعينيها تتأمل فنجاني','singer':'عبد الحليم حافظ'},
    {'lyrics':'تملي معاك ولو حتى بعيد عني','singer':'عمرو دياب'},
    {'lyrics':'يا بنات يا بنات','singer':'نانسي عجرم'},
    {'lyrics':'قولي أحبك كي تزيد وسامتي','singer':'كاظم الساهر'},
    {'lyrics':'أنا لحبيبي وحبيبي إلي','singer':'فيروز'},
    {'lyrics':'حبيبي يا كل الحياة اوعدني تبقى معايا','singer':'تامر حسني'},
    {'lyrics':'قلبي بيسألني عنك دخلك طمني وينك','singer':'وائل كفوري'},
    {'lyrics':'كيف أبيّن لك شعوري دون ما أحكي','singer':'عايض'},
    {'lyrics':'اسخر لك غلا وتشوفني مقصر','singer':'عايض'},
    {'lyrics':'رحت عني ما قويت جيت لك لاتردني','singer':'عبدالمجيد عبدالله'},
    {'lyrics':'خذني من ليلي لليلك','singer':'عبادي الجوهر'},
    {'lyrics':'تدري كثر ماني من البعد مخنوق','singer':'راشد الماجد'},
    {'lyrics':'انسى هالعالم ولو هم يزعلون','singer':'عباس ابراهيم'},
    {'lyrics':'أنا عندي قلب واحد','singer':'حسين الجسمي'},
    {'lyrics':'منوتي ليتك معي','singer':'محمد عبده'},
    {'lyrics':'خلنا مني طمني عليك','singer':'نوال الكويتية'},
    {'lyrics':'أحبك ليه أنا مدري','singer':'عبدالمجيد عبدالله'},
    {'lyrics':'أمر الله أقوى أحبك والعقل واعي','singer':'ماجد المهندس'},
    {'lyrics':'الحب يتعب من يدله والله في حبه بلاني','singer':'راشد الماجد'},
    # ... يمكنك إضافة المزيد بسهولة
]

class SongGame:
    """
    لعبة الأغنية — السؤال: بيت من كلمات، المطلوب: تحديد المغني.
    إعدادات حسب اختيارات المستخدم:
      - نظام نقاط: 1 نقطة لكل إجابة صحيحة (A)
      - التلميح: أول حرف فقط (1)
      - نهاية: كرت فائز واحد (I)
      - ثيم: استخدام ألوان الثيم الحالي (A)
    """
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.songs_pool = SONGS.copy()
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}   # user_id -> {'name': display_name, 'score': int}
        self.question_answered = False
        self.hints_used = set()   # users who used hint for current question

    def start_game(self, total_questions: int = 5):
        """ابدأ اللعبة — يمكن تحديد عدد الأسئلة (افتراضي 5)."""
        self.total_questions = min(max(1, int(total_questions)), len(self.songs_pool))
        # اختيار أسئلة عشوائية بدون تكرار
        self.questions = random.sample(self.songs_pool, self.total_questions)
        self.current_question = 0
        self.player_scores = {}
        self.question_answered = False
        self.hints_used = set()
        return self._show_question()

    def _show_question(self):
        """إنشاء FlexMessage لسؤال واحد"""
        song = self.questions[self.current_question]
        progress = f"{self.current_question + 1}/{self.total_questions}"

        contents = [
            create_game_header("لعبة الأغنية"),
            create_progress_box(self.current_question + 1, self.total_questions),
            create_separator(),
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": song['lyrics'], "size": "lg", "color": COLORS['text_dark'], "wrap": True, "weight": "bold", "align": "center"},
                    {"type": "text", "text": "من المغني؟", "size": "md", "color": COLORS['primary'], "margin": "md", "align": "center"}
                ],
                "margin": "lg"
            },
            create_separator(),
            *create_action_buttons()
        ]

        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": contents,
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
        return FlexMessage(alt_text="لعبة الأغنية", contents=FlexContainer.from_dict(bubble))

    def next_question(self):
        """انتقال للسؤال التالي — يعيد FlexMessage أو None إذا انتهت الأسئلة"""
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.question_answered = False
            self.hints_used = set()
            return self._show_question()
        return None

    def check_answer(self, answer: str, user_id: str, display_name: str):
        """
        معالجة إجابة المستخدم.
        يعيد dict متوافق مع بقية الألعاب:
          - 'response': TextMessage أو FlexMessage (أو قائمة)
          - 'points': عدد النقاط المكتسبة
          - 'correct': Bool
          - 'next_question': Bool (اختياري)
          - 'game_over': Bool (اختياري)
        """
        if not answer:
            return None

        answer = answer.strip()
        song = self.questions[self.current_question]

        # تلميح (أول حرف فقط) — كل مستخدم تلميح واحد لكل سؤال
        if answer.lower() in ['لمح', 'تلميح']:
            if user_id in self.hints_used:
                return {'response': TextMessage(text="لقد استخدمت التلميح لهذا السؤال بالفعل"), 'points': 0, 'correct': False}
            self.hints_used.add(user_id)
            # نستخدم create_hint_text لكن نعدل ليُظهر فقط الحرف الأول (حسب اختيارك)
            singer = song['singer']
            hint_text = f"يبدأ بحرف: {singer[0]}\nعدد الحروف: {len(singer)}"
            return {'response': TextMessage(text=hint_text), 'points': 0, 'correct': False}

        # طلب الحل
        if answer.lower() in ['جاوب', 'الجواب', 'الحل']:
            # نكشف الإجابة وننتقل للسؤال التالي (أو نهاية اللعبة)
            reveal = song['singer']
            self.question_answered = True
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"الإجابة: {reveal}"), 'points': 0, 'correct': False, 'next_question': True}
            return self._end_game()

        # إذا السؤال قد أُجيب بالفعل فلا نقبل إجابات أخرى
        if self.question_answered:
            return None

        # تحقق صحة الإجابة (تطبيع الحروف)
        if normalize_text(answer) == normalize_text(song['singer']):
            # صحيح — نقطة واحدة (اختيار A)
            points = 1
            self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})
            self.player_scores[user_id]['score'] += points
            self.question_answered = True

            # إذا لا زال هناك أسئلة أخرى نطلب الانتقال
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"إجابة صحيحة {display_name}\n+{points} نقطة"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
            # آخر سؤال — إنهاء اللعبة
            return self._end_game()

        # إجابة خاطئة — لا تستهلك محاولة المستخدم (يمكن أن يكرر)
        return {'response': TextMessage(text="إجابة خاطئة"), 'points': 0, 'correct': False}

    def _end_game(self):
        """إنهاء اللعبة — عرض كرت فائز واحد (الخيار I)"""
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبة بدون فائز"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}

        # ترتيب اللاعبين بحسب النقاط
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]

        # استخدم create_winner_card لتوحيد شكل الكرت المتبع في الألعاب الأخرى
        winner_card_dict = create_winner_card(winner, sorted_players, "اغنيه")

        flex = FlexMessage(alt_text="نتائج اللعبة", contents=FlexContainer.from_dict(winner_card_dict))
        return {'response': flex, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}

    def reset_game(self):
        """إعادة تهيئة اللعبة بالكامل (يمكن استدعاؤها عند الحاجة)"""
        self.questions = []
        self.current_question = 0
        self.player_scores = {}
        self.question_answered = False
        self.hints_used = set()
