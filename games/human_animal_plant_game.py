"""
لعبة إنسان حيوان نبات بلاد - Human Animal Plant Game
اكتب 4 كلمات تبدأ بنفس الحرف
"""

from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
import logging
from constants import COLORS

logger = logging.getLogger(__name__)


class HumanAnimalPlantGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.letters = [
            'أ', 'ب', 'ت', 'ج', 'ح', 'خ', 'د', 'ر', 'ز', 'س',
            'ش', 'ص', 'ع', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي'
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.answered_users = {}
    
    def start_game(self):
        try:
            self.questions = random.sample(self.letters, min(self.total_questions, len(self.letters)))
            self.current_question = 0
            self.player_scores = {}
            self.answered_users = {}
            logger.info(f"بدء لعبة إنسان حيوان نبات بلاد - عدد الأسئلة: {self.total_questions}")
            return self._show_question()
        except Exception as e:
            logger.error(f"خطأ في بدء لعبة إنسان حيوان نبات بلاد: {e}")
            return TextMessage(text="حدث خطأ في بدء اللعبة")
    
    def _show_question(self):
        try:
            letter = self.questions[self.current_question]
            progress = f"{self.current_question + 1}/{self.total_questions}"
            
            return FlexMessage(
                alt_text="إنسان حيوان نبات بلاد",
                contents=FlexContainer.from_dict({
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "contents": [
                            {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "إنسان حيوان نبات بلاد", "weight": "bold", "size": "lg", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                            {"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": "السؤال", "size": "xs", "color": COLORS['text_light'], "flex": 0}, {"type": "text", "text": progress, "size": "xs", "color": COLORS['primary'], "weight": "bold", "align": "end"}], "margin": "lg"},
                            {"type": "separator", "margin": "md"},
                            {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": letter, "size": "5xl", "color": COLORS['primary'], "weight": "bold", "align": "center"}, {"type": "text", "text": "اكتب 4 كلمات تبدأ بهذا الحرف", "size": "sm", "margin": "md", "wrap": True, "align": "center"}, {"type": "text", "text": "كل كلمة في سطر منفصل", "size": "xs", "color": COLORS['text_light'], "margin": "xs", "align": "center"}], "margin": "lg"},
                            {"type": "separator", "margin": "lg"},
                            {"type": "box", "layout": "horizontal", "contents": [{"type": "button", "action": {"type": "message", "label": "لمح", "text": "لمح"}, "style": "secondary", "height": "sm"}, {"type": "button", "action": {"type": "message", "label": "جاوب", "text": "جاوب"}, "style": "secondary", "height": "sm"}], "spacing": "sm", "margin": "lg"}
                        ],
                        "paddingAll": "20px"
                    }
                })
            )
        except Exception as e:
            logger.error(f"خطأ في عرض السؤال: {e}")
            return TextMessage(text="حدث خطأ في عرض السؤال")
    
    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.answered_users = {}
            return self._show_question()
        return None
    
    def check_answer(self, text, user_id, display_name):
        try:
            if user_id in self.answered_users:
                return None
            
            text = text.strip()
            letter = self.questions[self.current_question]
            
            if text.lower() in ['لمح', 'تلميح']:
                hint_text = f"يبدأ بحرف: {letter}\nمثال: إنسان حيوان نبات بلاد"
                return {'response': TextMessage(text=hint_text), 'points': 0, 'correct': False}
            
            if text.lower() in ['جاوب', 'الجواب', 'الحل']:
                self.answered_users[user_id] = True
                if self.current_question + 1 < self.total_questions:
                    return {'response': TextMessage(text=f"اكتب 4 كلمات تبدأ بحرف: {letter}"), 'points': 0, 'correct': False, 'next_question': True}
                else:
                    result = self._end_game()
                    result['response'] = [TextMessage(text=f"اكتب 4 كلمات تبدأ بحرف: {letter}"), result['response']]
                    return result
            
            lines = text.split('\n')
            if len(lines) >= 4:
                words = [line.strip() for line in lines if line.strip()]
                if len(words) >= 4:
                    valid_count = sum(1 for word in words[:4] if word and word[0] == letter)
                    
                    if valid_count >= 1:
                        points = valid_count * 3
                        if user_id not in self.player_scores:
                            self.player_scores[user_id] = {'name': display_name, 'score': 0}
                        self.player_scores[user_id]['score'] += points
                        self.answered_users[user_id] = True
                        
                        if self.current_question + 1 < self.total_questions:
                            return {'response': TextMessage(text=f"صحيح {display_name}\nالكلمات الصحيحة: {valid_count}/4\n+{points} نقطة"), 'points': points, 'correct': True, 'won': valid_count == 4, 'next_question': True}
                        else:
                            return self._end_game()
            
            return None
        except Exception as e:
            logger.error(f"خطأ في التحقق من الإجابة: {e}")
            return None
    
    def _end_game(self):
        try:
            if not self.player_scores:
                return {'response': TextMessage(text="انتهت اللعبة"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
            
            sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
            winner = sorted_players[0][1]
            
            players_contents = []
            for i, (uid, player) in enumerate(sorted_players[:5]):
                players_contents.append({"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": f"{i+1}.", "size": "sm", "flex": 0}, {"type": "text", "text": player['name'], "size": "sm", "flex": 3, "margin": "sm"}, {"type": "text", "text": f"{player['score']}", "size": "sm", "color": COLORS['primary'], "weight": "bold", "align": "end"}], "margin": "md" if i > 0 else "sm"})
            
            winner_card = FlexMessage(
                alt_text="نتائج اللعبة",
                contents=FlexContainer.from_dict({
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
                            {"type": "button", "action": {"type": "message", "label": "اعادة اللعب", "text": "لعبه"}, "style": "primary", "margin": "lg"}
                        ],
                        "paddingAll": "20px"
                    }
                })
            )
            
            return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
        except Exception as e:
            logger.error(f"خطأ في إنهاء اللعبة: {e}")
            return {'response': TextMessage(text="حدث خطأ في إنهاء اللعبة"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
