from linebot.models import TextSendMessage, FlexSendMessage
import random
from constants import COLORS

class HumanAnimalPlantGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.letters = [
            'أ', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 
            'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي'
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.answered_users = {}

    def start_game(self):
        self.questions = random.sample(self.letters, min(self.total_questions, len(self.letters)))
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = {}
        return self._show_question()

    def _show_question(self):
        letter = self.questions[self.current_question]
        progress = f"{self.current_question + 1}/{self.total_questions}"
        
        return FlexSendMessage(
            alt_text="إنسان حيوان نبات بلاد",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "إنسان حيوان نبات بلاد", "weight": "bold", "size": "lg", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                        {"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": "السؤال", "size": "xs", "color": COLORS['text_light'], "flex": 0}, {"type": "text", "text": progress, "size": "xs", "color": COLORS['primary'], "weight": "bold", "align": "end"}], "margin": "lg"},
                        {"type": "separator", "margin": "md", "color": COLORS['border']},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": letter, "size": "5xl", "color": COLORS['primary'], "weight": "bold", "align": "center"}, {"type": "text", "text": "اكتب 4 كلمات تبدأ بهذا الحرف", "size": "sm", "color": COLORS['text_dark'], "margin": "md", "wrap": True, "align": "center"}, {"type": "text", "text": "كل كلمة في سطر منفصل", "size": "xs", "color": COLORS['text_light'], "margin": "xs", "align": "center"}], "margin": "lg"},
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
            self.answered_users = {}
            return self._show_question()
        return None

    def check_answer(self, text, user_id, display_name):
        if user_id in self.answered_users:
            return None
        
        text = text.strip()
        letter = self.questions[self.current_question]

        if text.lower() in ['لمح', 'تلميح']:
            return {'response': TextSendMessage(text=f"يبدأ بحرف: {letter}\nمثال: إنسان، حيوان، نبات، بلاد"), 'points': 0, 'correct': False}

        if text.lower() in ['جاوب', 'الجواب']:
            self.answered_users[user_id] = True
            if self.current_question + 1 < self.total_questions:
                return {'response': TextSendMessage(text=f"اكتب 4 كلمات تبدأ بحرف: {letter}"), 'points': 0, 'correct': False, 'next_question': True}
            return self._end_game()

        lines = text.split('\n')
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
                        {"type": "button", "action": {"type": "message", "label": "إعادة اللعب", "text": "لعبه"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "lg"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )
        return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
