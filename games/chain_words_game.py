from linebot.v3.messaging import TextMessage, FlexMessage
import random
import re
from constants import COLORS

def normalize_text(text):
    if not text:
        return ""
    text = text.strip().lower()
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '').replace('ة', 'ه').replace('ى', 'ي')
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'\s+', '', text)
    return text

class ChainWordsGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.start_words = ["قلم", "كتاب", "مدرسة", "باب", "نافذة", "طاولة", "كرسي", "حديقة", "شجرة", "زهرة"]
        self.current_word = None
        self.used_words = set()
        self.round_count = 0
        self.max_rounds = 5
        self.player_scores = {}
        self.answered_users = set()

    def start_game(self):
        self.current_word = random.choice(self.start_words)
        self.used_words = {normalize_text(self.current_word)}
        self.round_count = 0
        self.player_scores = {}
        self.answered_users = set()
        return self._show_question()

    def _show_question(self):
        last_letter = self.current_word[-1]
        progress = f"{self.round_count + 1}/{self.max_rounds}"
        
        return FlexMessage(
            alt_text="سلسلة الكلمات",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "سلسلة الكلمات", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                        {"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": "السؤال", "size": "xs", "color": COLORS['text_light'], "flex": 0}, {"type": "text", "text": progress, "size": "xs", "color": COLORS['primary'], "weight": "bold", "align": "end"}], "margin": "lg"},
                        {"type": "separator", "margin": "md"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": f"الكلمة: {self.current_word}", "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center"}, {"type": "text", "text": f"اكتب كلمة تبدأ بحرف: {last_letter}", "size": "md", "wrap": True, "margin": "md", "align": "center"}], "margin": "lg"},
                        {"type": "separator", "margin": "lg"},
                        {"type": "box", "layout": "horizontal", "contents": [{"type": "button", "action": {"type": "message", "label": "لمح", "text": "لمح"}, "style": "secondary", "height": "sm"}, {"type": "button", "action": {"type": "message", "label": "جاوب", "text": "جاوب"}, "style": "secondary", "height": "sm"}], "spacing": "sm", "margin": "lg"}
                    ],
                    "paddingAll": "20px"
                }
            }
        )

    def next_question(self):
        if self.round_count < self.max_rounds:
            self.answered_users = set()
            return self._show_question()
        return None

    def check_answer(self, answer, user_id, display_name):
        if user_id in self.answered_users:
            return None
        
        answer = answer.strip()
        last_letter = self.current_word[-1]
        
        if answer.lower() in ['لمح', 'تلميح']:
            return {'response': TextMessage(text=f"يبدأ بحرف: {last_letter}"), 'points': 0, 'correct': False}

        if answer.lower() in ['جاوب', 'الجواب', 'الحل']:
            self.answered_users.add(user_id)
            if self.round_count + 1 < self.max_rounds:
                return {'response': TextMessage(text=f"اي كلمة تبدأ بحرف: {last_letter}"), 'points': 0, 'correct': False, 'next_question': True}
            return self._end_game()

        normalized_last = 'ه' if last_letter in ['ة', 'ه'] else last_letter
        normalized_answer = normalize_text(answer)

        if normalized_answer in self.used_words:
            return {'response': TextMessage(text="الكلمة مستخدمة"), 'points': 0, 'correct': False}

        first_letter = answer[0].lower()
        first_letter = 'ه' if first_letter in ['ة', 'ه'] else first_letter

        if first_letter == normalized_last or (normalized_last == 'ه' and first_letter in ['ه', 'ة']):
            self.used_words.add(normalized_answer)
            self.current_word = answer
            self.round_count += 1
            points = 1
            self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})
            self.player_scores[user_id]['score'] += points
            self.answered_users.add(user_id)

            if self.round_count < self.max_rounds:
                return {'response': TextMessage(text=f"صحيح {display_name} +{points}"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
            return self._end_game()
        
        return {'response': TextMessage(text=f"يجب ان تبدأ بحرف: {last_letter}"), 'points': 0, 'correct': False}

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبة"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
        
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        
        players_contents = []
        for i, p in enumerate(sorted_players[:5]):
            players_contents.append({"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": f"{i+1}.", "size": "sm", "flex": 0}, {"type": "text", "text": p[1]['name'], "size": "sm", "flex": 3, "margin": "sm"}, {"type": "text", "text": f"{p[1]['score']}", "size": "sm", "color": COLORS['primary'], "weight": "bold", "align": "end"}], "margin": "md" if i > 0 else "sm"})
        
        winner_card = FlexMessage(
            alt_text="نتائج اللعبة",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "انتهت اللعبة", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "الفائز", "size": "sm", "color": COLORS['text_light'], "align": "center"}, {"type": "text", "text": winner['name'], "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center"}, {"type": "text", "text": f"{winner['score']} نقطة", "size": "lg", "color": COLORS['success'], "align": "center"}], "margin": "lg"},
                        {"type": "separator", "margin": "lg"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "النتائج", "size": "md", "weight": "bold"}, *players_contents], "margin": "lg"},
                        {"type": "button", "action": {"type": "message", "label": "اعادة اللعب", "text": "سلسله"}, "style": "primary", "margin": "lg"}
                    ],
                    "paddingAll": "20px"
                }
            }
        )
        return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
