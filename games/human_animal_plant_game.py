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

class HumanAnimalPlantGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.letters = ['أ', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي']
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.answered_users = {}

    def start_game(self):
        self.questions = random.sample(self.letters, self.total_questions)
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = {}
        return self._show_question()

    def _show_question(self):
        letter = self.questions[self.current_question]
        return FlexSendMessage(
            alt_text="إنسان حيوان نبات بلاد",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "إنسان حيوان نبات بلاد", "weight": "bold", "size": "lg", "color": COLORS['white']}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "10px"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": f"جولة {self.current_question + 1} من {self.total_questions}", "size": "sm", "color": COLORS['text_light']}, {"type": "text", "text": letter, "size": "5xl", "color": COLORS['primary'], "weight": "bold", "margin": "md", "align": "center"}, {"type": "text", "text": "اكتب 4 كلمات تبدأ بهذا الحرف", "size": "sm", "color": COLORS['text_dark'], "margin": "md", "wrap": True}, {"type": "text", "text": "كل كلمة في سطر منفصل", "size": "xs", "color": COLORS['text_light'], "margin": "xs"}], "margin": "lg", "spacing": "sm"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.answered_users = {}
            return self._show_question()
        return None

    def check_answer(self, text, user_id, display_name):
        if user_id in self.answered_users:
            return None
        text = text.strip()
        lines = text.split('\n')
        letter = self.questions[self.current_question]

        if len(lines) >= 4:
            words = [line.strip() for line in lines if line.strip()]
            if len(words) >= 4:
                valid_count = sum(1 for word in words[:4] if word and word[0] == letter)
                if valid_count >= 1:
                    points = valid_count * 3
                    self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})
                    self.player_scores[user_id]['score'] += points
                    self.answered_users[user_id] = True

                    if self.current_question + 1 < self.total_questions:
                        return {'response': TextSendMessage(text=f"اجابة صحيحة {display_name}\nالكلمات الصحيحة: {valid_count}/4\n+{points} نقطة"), 'points': points, 'correct': True, 'won': valid_count == 4, 'next_question': True}
                    return self._end_game()
        return None

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextSendMessage(text="انتهت اللعبة"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        players_text = "\n".join([f"{i+1}. {p[1]['name']}: {p[1]['score']} نقطة" for i, p in enumerate(sorted_players[:5])])
        winner_card = FlexSendMessage(
            alt_text="نتائج اللعبة",
            contents={"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": [{"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "انتهت اللعبة", "weight": "bold", "size": "xl", "color": COLORS['white']}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "10px"}, {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "الفائز", "size": "sm", "color": COLORS['text_light']}, {"type": "text", "text": winner['name'], "size": "xxl", "color": COLORS['primary'], "weight": "bold", "margin": "xs"}, {"type": "text", "text": f"{winner['score']} نقطة", "size": "lg", "color": COLORS['text_dark'], "margin": "xs"}], "margin": "lg", "spacing": "xs"}, {"type": "separator", "margin": "lg", "color": COLORS['border']}, {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "النتائج", "size": "sm", "color": COLORS['text_light']}, {"type": "text", "text": players_text, "size": "sm", "color": COLORS['text_dark'], "wrap": True, "margin": "md"}], "margin": "lg"}, {"type": "separator", "margin": "lg", "color": COLORS['border']}, {"type": "button", "action": {"type": "message", "label": "إعادة", "text": "لعبة"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "lg"}], "backgroundColor": COLORS['card_bg'], "paddingAll": "20px"}}
        )
        return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
