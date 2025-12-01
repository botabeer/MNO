from linebot.models import TextSendMessage, FlexSendMessage
import random
import re
from datetime import datetime
from constants import COLORS

def normalize_text(text):
    if not text:
        return ""
    text = text.strip().lower()
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '').replace('ة', 'ه').replace('ى', 'ي')
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'\s+', '', text)
    return text

class FastTypingGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.words = [
            "سبحان الله",
            "الحمد لله",
            "لا اله الا الله",
            "الله اكبر",
            "استغفر الله",
            "لا حول ولا قوه الا بالله",
            "حسبنا الله ونعم الوكيل",
            "توكلت على الله",
            "الله يرحمه",
            "انا لله وانا اليه راجعون",
            "بارك الله فيك",
            "جزاك الله خيرا",
            "الله يحفظك",
            "ما شاء الله",
            "اللهم صل على محمد",
            "رب اغفر لي",
            "اللهم ارحمنا",
            "اللهم اجرني",
            "اللهم اهدني",
            "اللهم ارزقني",
            "اللهم عافني",
            "اللهم اصلح حالي",
            "رب يسر ولا تعسر",
            "اللهم امين",
            "تقبل الله",
            "اللهم بارك",
            "اللهم وفقنا",
            "الله المستعان",
            "قدر الله وما شاء فعل",
            "اعوذ بالله من الشيطان",
            "بسم الله الرحمن الرحيم",
            "ولا تيئسوا من روح الله",
            "واصبر فان الله لا يضيع",
            "الصبر مفتاح الفرج",
            "الدنيا دار ممر لا دار مقر",
            "العلم نور والجهل ظلام",
            "ازرع خيرا تحصد خيرا",
            "من طلب العلا سهر الليالي",
            "الصديق وقت الضيق",
            "خير الكلام ما قل ودل",
            "العقل السليم في الجسم السليم",
            "في التاني السلامه",
            "الوقت كالسيف ان لم تقطعه قطعك",
            "الصدق منجاه",
            "الامانه غايه",
            "العلم يرفع بيوتا لا عماد لها",
            "اطلبوا العلم ولو في الصين",
            "الكتاب يقرا من عنوانه",
            "من جد وجد ومن زرع حصد",
            "الصحه تاج على راس الاصحاء"
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.start_time = None
        self.time_limit = 30
        self.answered_users = set()

    def start_game(self):
        self.questions = random.sample(self.words, self.total_questions)
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        self.start_time = datetime.now()
        return self._show_question()

    def _show_question(self):
        word = self.questions[self.current_question]
        self.start_time = datetime.now()
        return FlexSendMessage(
            alt_text="الكتابه السريعه",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "الكتابه السريعه", "weight": "bold", "size": "xl", "color": COLORS['white']}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "10px"},
                        {"type": "box", "layout": "vertical", "contents": [
                            {"type": "text", "text": f"جوله {self.current_question + 1} من {self.total_questions}", "size": "sm", "color": COLORS['text_light']},
                            {"type": "text", "text": word, "size": "lg", "color": COLORS['primary'], "weight": "bold", "margin": "md", "align": "center", "wrap": True},
                            {"type": "text", "text": "اكتب النص باسرع وقت", "size": "sm", "color": COLORS['text_dark'], "margin": "md", "align": "center"},
                            {"type": "text", "text": f"لديك {self.time_limit} ثانيه", "size": "xs", "color": COLORS['text_light'], "margin": "xs", "align": "center"}
                        ], "margin": "lg", "spacing": "sm"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
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

        if self.start_time:
            elapsed = (datetime.now() - self.start_time).seconds
            if elapsed > self.time_limit:
                if self.current_question + 1 < self.total_questions:
                    return {'response': TextSendMessage(text="انتهى الوقت"), 'points': 0, 'correct': False, 'next_question': True}
                return self._end_game()

        text_normalized = normalize_text(text)
        word_normalized = normalize_text(self.questions[self.current_question])

        if text_normalized == word_normalized:
            elapsed_time = (datetime.now() - self.start_time).total_seconds()
            
            points = 1
            if elapsed_time <= 5:
                bonus_msg = "سريع جدا"
            elif elapsed_time <= 10:
                bonus_msg = "سريع"
            elif elapsed_time <= 15:
                bonus_msg = "جيد"
            elif elapsed_time <= 20:
                bonus_msg = "متوسط"
            else:
                bonus_msg = "بطيء"
            
            self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0, 'time': 0})
            self.player_scores[user_id]['score'] += points
            self.player_scores[user_id]['time'] += elapsed_time
            self.answered_users.add(user_id)

            if self.current_question + 1 < self.total_questions:
                return {'response': TextSendMessage(text=f"اجابه صحيحه {display_name}\n{bonus_msg}\nالوقت {elapsed_time:.1f} ثانيه\nنقطه {points}"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
            return self._end_game()
        return None

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextSendMessage(text="انتهت اللعبه"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
        
        sorted_players = sorted(self.player_scores.items(), key=lambda x: (x[1]['score'], -x[1]['time']), reverse=True)
        winner = sorted_players[0][1]
        avg_time = winner['time'] / self.total_questions if winner.get('time', 0) > 0 else 0
        
        players_text = "\n".join([
            f"{i+1}. {p[1]['name']} - {p[1]['score']} نقطه - {p[1].get('time', 0):.1f}ث" 
            for i, p in enumerate(sorted_players[:5])
        ])
        
        winner_card = FlexSendMessage(
            alt_text="نتائج اللعبه",
            contents={"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": [
                {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "انتهت اللعبه", "weight": "bold", "size": "xl", "color": COLORS['white']}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "10px"},
                {"type": "box", "layout": "vertical", "contents": [
                    {"type": "text", "text": "الفائز", "size": "sm", "color": COLORS['text_light']},
                    {"type": "text", "text": winner['name'], "size": "xxl", "color": COLORS['primary'], "weight": "bold", "margin": "xs"},
                    {"type": "text", "text": f"{winner['score']} نقطه", "size": "lg", "color": COLORS['text_dark'], "margin": "xs"},
                    {"type": "text", "text": f"متوسط الوقت {avg_time:.1f} ثانيه", "size": "sm", "color": COLORS['text_light'], "margin": "xs"}
                ], "margin": "lg", "spacing": "xs"},
                {"type": "separator", "margin": "lg", "color": COLORS['border']},
                {"type": "box", "layout": "vertical", "contents": [
                    {"type": "text", "text": "النتائج", "size": "sm", "color": COLORS['text_light']},
                    {"type": "text", "text": players_text, "size": "sm", "color": COLORS['text_dark'], "wrap": True, "margin": "md"}
                ], "margin": "lg"},
                {"type": "separator", "margin": "lg", "color": COLORS['border']},
                {"type": "button", "action": {"type": "message", "label": "اعاده", "text": "اسرع"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "lg"}
            ], "backgroundColor": COLORS['card_bg'], "paddingAll": "20px"}}
        )
        return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
