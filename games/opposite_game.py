from linebot.models import TextSendMessage, FlexSendMessage
import random
import re
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

class OppositeGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.all_words = [
            {"word": "كبير", "opposite": "صغير"}, {"word": "طويل", "opposite": "قصير"},
            {"word": "سريع", "opposite": "بطيء"}, {"word": "ساخن", "opposite": "بارد"},
            {"word": "نظيف", "opposite": "وسخ"}, {"word": "قوي", "opposite": "ضعيف"},
            {"word": "سهل", "opposite": "صعب"}, {"word": "جميل", "opposite": "قبيح"},
            {"word": "غني", "opposite": "فقير"}, {"word": "فوق", "opposite": "تحت"},
            {"word": "يمين", "opposite": "يسار"}, {"word": "أمام", "opposite": "خلف"},
            {"word": "داخل", "opposite": "خارج"}, {"word": "قريب", "opposite": "بعيد"},
            {"word": "جديد", "opposite": "قديم"}, {"word": "ثقيل", "opposite": "خفيف"},
            {"word": "مظلم", "opposite": "مضيء"}, {"word": "صادق", "opposite": "كاذب"},
            {"word": "شجاع", "opposite": "جبان"}, {"word": "نشيط", "opposite": "كسول"}
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.answered_users = set()
        self.hints_used = {}

    def start_game(self):
        self.questions = random.sample(self.all_words, self.total_questions)
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        self.hints_used = {}
        return self._show_question()

    def _show_question(self):
        word = self.questions[self.current_question]
        progress = f"{self.current_question + 1}/{self.total_questions}"
        
        return FlexSendMessage(
            alt_text="لعبة الأضداد",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "لعبة الأضداد", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                        {"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": "السؤال", "size": "xs", "color": COLORS['text_light'], "flex": 0}, {"type": "text", "text": progress, "size": "xs", "color": COLORS['primary'], "weight": "bold", "align": "end"}], "margin": "lg"},
                        {"type": "separator", "margin": "md", "color": COLORS['border']},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": f"ما هو عكس: {word['word']}", "size": "lg", "color": COLORS['text_dark'], "wrap": True, "weight": "bold", "align": "center"}], "margin": "lg"},
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
            self.hints_used = {}
            return self._show_question()
        return None

    def check_answer(self, answer, user_id, display_name):
        if user_id in self.answered_users:
            return None
        word = self.questions[self.current_question]

        if answer.lower() in ['لمح', 'تلميح']:
            if user_id not in self.hints_used:
                self.hints_used[user_id] = True
                return {'response': TextSendMessage(text=f"يبدأ بحرف: {word['opposite'][0]}\nعدد الحروف: {len(word['opposite'])}"), 'points': 0, 'correct': False}
            return {'response': TextSendMessage(text="استخدمت التلميح"), 'points': 0, 'correct': False}

        if answer.lower() in ['جاوب', 'الجواب']:
            self.answered_users.add(user_id)
            if self.current_question + 1 < self.total_questions:
                return {'response': TextSendMessage(text=f"الاجابة: {word['opposite']}"), 'points': 0, 'correct': False, 'next_question': True}
            return self._end_game()

        if normalize_text(answer) == normalize_text(word['opposite']):
            points = 1
            self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})
            self.player_scores[user_id]['score'] += points
            self.answered_users.add(user_id)

            if self.current_question + 1 < self.total_questions:
                return {'response': TextSendMessage(text=f"اجابة صحيحة {display_name}\n+{points} نقطة"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
            return self._end_game()
        return None

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextSendMessage(text="انتهت اللعبة"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
        
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        
        players_contents = []
        
        for i, p in enumerate(sorted_players[:5]):
            rank = f"{i+1}."
            players_contents.append({"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": rank, "size": "sm", "flex": 0}, {"type": "text", "text": p[1]['name'], "size": "sm", "color": COLORS['text_dark'], "flex": 3, "margin": "sm"}, {"type": "text", "text": f"{p[1]['score']} نقطة", "size": "sm", "color": COLORS['primary'], "weight": "bold", "align": "end", "flex": 2}], "margin": "md" if i > 0 else "sm"})
        
        winner_card = FlexSendMessage(
            alt_text="نتائج اللعبة",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "انتهت اللعبة", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "الفائز", "size": "sm", "color": COLORS['text_light'], "align": "center"}, {"type": "text", "text": winner['name'], "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center", "margin": "xs"}, {"type": "text", "text": f"{winner['score']} نقطة", "size": "lg", "color": COLORS['success'], "align": "center", "margin": "xs"}], "margin": "lg"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "النتائج", "size": "md", "color": COLORS['text_dark'], "weight": "bold"}, *players_contents], "margin": "lg"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "button", "action": {"type": "message", "label": "إعادة اللعب", "text": "ضد"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "lg"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )
        return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
