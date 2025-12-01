from linebot.models import TextSendMessage, FlexSendMessage
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
        return FlexSendMessage(
            alt_text="سلسلة الكلمات",
            contents={"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": [{"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "سلسلة الكلمات", "weight": "bold", "size": "xl", "color": COLORS['white']}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "10px"}, {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": f"جولة {self.round_count + 1} من {self.max_rounds}", "size": "sm", "color": COLORS['text_light']}, {"type": "text", "text": f"الكلمة: {self.current_word}", "size": "xxl", "color": COLORS['primary'], "weight": "bold", "margin": "md"}, {"type": "text", "text": f"اكتب كلمة تبدأ بحرف: {last_letter}", "size": "md", "color": COLORS['text_dark'], "wrap": True, "margin": "md"}], "margin": "lg", "spacing": "sm"}], "backgroundColor": COLORS['card_bg'], "paddingAll": "20px"}}
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
        normalized_last = 'ه' if last_letter in ['ة', 'ه'] else last_letter
        normalized_answer = normalize_text(answer)

        if normalized_answer in self.used_words:
            return {'response': TextSendMessage(text="هذه الكلمة استخدمت من قبل"), 'points': 0, 'correct': False}

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
                return {'response': TextSendMessage(text=f"اجابة صحيحة {display_name}\n+{points} نقطة"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
            return self._end_game()
        return {'response': TextSendMessage(text=f"يجب أن تبدأ الكلمة بحرف: {last_letter}"), 'points': 0, 'correct': False}

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextSendMessage(text="انتهت اللعبة"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        players_text = "\n".join([f"{i+1}. {p[1]['name']}: {p[1]['score']} نقطة" for i, p in enumerate(sorted_players[:5])])
        winner_card = FlexSendMessage(
            alt_text="نتائج اللعبة",
            contents={"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": [{"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "انتهت اللعبة", "weight": "bold", "size": "xl", "color": COLORS['white']}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "10px"}, {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "الفائز", "size": "sm", "color": COLORS['text_light']}, {"type": "text", "text": winner['name'], "size": "xxl", "color": COLORS['primary'], "weight": "bold", "margin": "xs"}, {"type": "text", "text": f"{winner['score']} نقطة", "size": "lg", "color": COLORS['text_dark'], "margin": "xs"}], "margin": "lg", "spacing": "xs"}, {"type": "separator", "margin": "lg", "color": COLORS['border']}, {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "النتائج", "size": "sm", "color": COLORS['text_light']}, {"type": "text", "text": players_text, "size": "sm", "color": COLORS['text_dark'], "wrap": True, "margin": "md"}], "margin": "lg"}, {"type": "separator", "margin": "lg", "color": COLORS['border']}, {"type": "button", "action": {"type": "message", "label": "إعادة", "text": "سلسلة"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "lg"}], "backgroundColor": COLORS['card_bg'], "paddingAll": "20px"}}
        )
        return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
