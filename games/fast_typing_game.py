from linebot.models import TextSendMessage, FlexSendMessage
import random
import re
from datetime import datetime
from constants import COLORS

def normalize_text(text):
    if not text:
        return ""
    text = text.strip().lower()
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    text = text.replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '')
    text = text.replace('ة', 'ه').replace('ى', 'ي')
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'\s+', '', text)
    return text

class FastTypingGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.words = [
            "سبحان الله", "الحمد لله", "لا اله الا الله", "الله اكبر", "استغفر الله",
            "لا حول ولا قوه الا بالله", "حسبنا الله ونعم الوكيل", "توكلت على الله",
            "الله يرحمه", "انا لله وانا اليه راجعون", "بارك الله فيك", "جزاك الله خيرا",
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
        progress = f"{self.current_question + 1}/{self.total_questions}"
        self.start_time = datetime.now()
        
        return FlexSendMessage(
            alt_text="الكتابه السريعه",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "الكتابه السريعه", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                        {"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": "السؤال", "size": "xs", "color": COLORS['text_light'], "flex": 0}, {"type": "text", "text": progress, "size": "xs", "color": COLORS['primary'], "weight": "bold", "align": "end"}], "margin": "lg"},
                        {"type": "separator", "margin": "md", "color": COLORS['border']},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": word, "size": "lg", "color": COLORS['primary'], "weight": "bold", "align": "center", "wrap": True}, {"type": "text", "text": "اكتب النص باسرع وقت", "size": "sm", "color": COLORS['text_dark'], "margin": "md", "align": "center"}, {"type": "text", "text": f"لديك {self.time_limit} ثانيه", "size": "xs", "color": COLORS['text_light'], "margin": "xs", "align": "center"}], "margin": "lg"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "box", "layout": "horizontal", "contents": [{"type": "button", "action": {"type": "message", "label": "لمح", "text": "لمح"}, "style": "secondary", "height": "sm", "flex": 1}, {"type": "button", "action": {"type": "message", "label": "جاوب", "text": "جاوب"}, "style": "secondary", "height": "sm", "flex": 1}], "spacing": "sm", "margin": "lg"},
                        {"type": "box", "layout": "horizontal", "contents": [{"type": "button", "action": {"type": "message", "label": "إيقاف", "text": "إيقاف"}, "style": "secondary", "height": "sm", "flex": 1}, {"type": "button", "action": {"type": "message", "label": "تسجيل", "text": "تسجيل"}, "style": "secondary", "height": "sm", "flex": 1}], "spacing": "sm", "margin": "sm"}
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

        if text.lower() in ['لمح', 'تلميح']:
            word = self.questions[self.current_question]
            return {'response': TextSendMessage(text=f"يبدأ بحرف: {word[0]}\nعدد الحروف: {len(word)}"), 'points': 0, 'correct': False}

        if text.lower() in ['جاوب', 'الجواب']:
            self.answered_users.add(user_id)
            word = self.questions[self.current_question]
            if self.current_question + 1 < self.total_questions:
                return {'response': TextSendMessage(text=f"الاجابة: {word}"), 'points': 0, 'correct': False, 'next_question': True}
            return self._end_game()

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
            
            self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0, 'time': 0})
            self.player_scores[user_id]['score'] += points
            self.player_scores[user_id]['time'] += elapsed_time
            self.answered_users.add(user_id)

            if self.current_question + 1 < self.total_questions:
                return {'response': TextSendMessage(text=f"اجابه صحيحه {display_name}\nالوقت {elapsed_time:.1f} ثانيه\n+{points} نقطه"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
            return self._end_game()
        return None

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextSendMessage(text="انتهت اللعبه"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
        
        sorted_players = sorted(self.player_scores.items(), key=lambda x: (x[1]['score'], -x[1]['time']), reverse=True)
        winner = sorted_players[0][1]
        
        players_contents = []
        
        for i, p in enumerate(sorted_players[:5]):
            rank = f"{i+1}."
            players_contents.append({"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": rank, "size": "sm", "flex": 0}, {"type": "text", "text": p[1]['name'], "size": "sm", "color": COLORS['text_dark'], "flex": 3, "margin": "sm"}, {"type": "text", "text": f"{p[1]['score']} نقطه", "size": "sm", "color": COLORS['primary'], "weight": "bold", "align": "end", "flex": 2}], "margin": "md" if i > 0 else "sm"})
        
        winner_card = FlexSendMessage(
            alt_text="نتائج اللعبه",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "انتهت اللعبه", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "الفائز", "size": "sm", "color": COLORS['text_light'], "align": "center"}, {"type": "text", "text": winner['name'], "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center", "margin": "xs"}, {"type": "text", "text": f"{winner['score']} نقطه", "size": "lg", "color": COLORS['success'], "align": "center", "margin": "xs"}], "margin": "lg"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "النتائج", "size": "md", "color": COLORS['text_dark'], "weight": "bold"}, *players_contents], "margin": "lg"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "button", "action": {"type": "message", "label": "إعادة اللعب", "text": "اسرع"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "lg"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )
        return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
