"""
لعبة سلسلة الكلمات - Chain Words Game
كل كلمة تبدأ بآخر حرف من الكلمة السابقة
"""

from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
import re
import logging
from constants import COLORS

logger = logging.getLogger(__name__)


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


class ChainWordsGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.start_words = [
            "قلم", "كتاب", "مدرسة", "باب", "نافذة",
            "طاولة", "كرسي", "حديقة", "شجرة", "زهرة"
        ]
        self.current_word = None
        self.used_words = set()
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.current_round_answered = False
    
    def start_game(self):
        try:
            self.current_word = random.choice(self.start_words)
            self.used_words = {normalize_text(self.current_word)}
            self.current_question = 0
            self.player_scores = {}
            self.current_round_answered = False
            logger.info(f"بدء لعبة سلسلة الكلمات - الكلمة الأولى: {self.current_word}")
            return self._show_question()
        except Exception as e:
            logger.error(f"خطأ في بدء لعبة سلسلة الكلمات: {e}")
            return TextMessage(text="حدث خطأ في بدء اللعبة")
    
    def _show_question(self):
        try:
            last_letter = self.current_word[-1]
            progress = f"{self.current_question + 1}/{self.total_questions}"
            
            return FlexMessage(
                alt_text="سلسلة الكلمات",
                contents=FlexContainer.from_dict({
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "contents": [
                            {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "سلسلة الكلمات", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                            {"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": "السؤال", "size": "xs", "color": COLORS['text_light'], "flex": 0}, {"type": "text", "text": progress, "size": "xs", "color": COLORS['primary'], "weight": "bold", "align": "end"}], "margin": "lg"},
                            {"type": "separator", "margin": "md"},
                            {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": f"الكلمة: {self.current_word}", "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center"}, {"type": "text", "text": f"اكتب كلمة تبدأ بحرف: {last_letter}", "size": "md", "wrap": True, "margin": "md", "align": "center"}], "margin": "lg", "spacing": "sm"},
                            {"type": "separator", "margin": "lg"},
                            {"type": "box", "layout": "horizontal", "contents": [{"type": "button", "action": {"type": "message", "label": "لمح", "text": "لمح"}, "style": "secondary", "height": "sm", "flex": 1}, {"type": "button", "action": {"type": "message", "label": "جاوب", "text": "جاوب"}, "style": "secondary", "height": "sm", "flex": 1}], "spacing": "sm", "margin": "lg"}
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
            self.current_round_answered = False
            return self._show_question()
        return None
    
    def check_answer(self, answer, user_id, display_name):
        try:
            # تجاهل الإجابات بعد أول إجابة صحيحة
            if self.current_round_answered:
                return None
            
            answer = answer.strip()
            last_letter = self.current_word[-1]
            
            # معالجة لمح
            if answer.lower() in ['لمح', 'تلميح']:
                hint_text = f"يبدأ بحرف: {last_letter}"
                return {'response': TextMessage(text=hint_text), 'points': 0, 'correct': False}
            
            # معالجة جاوب
            if answer.lower() in ['جاوب', 'الجواب', 'الحل']:
                self.current_round_answered = True
                
                if self.current_question + 1 < self.total_questions:
                    return {'response': TextMessage(text=f"أي كلمة تبدأ بحرف: {last_letter}"), 'points': 0, 'correct': False, 'next_question': True}
                else:
                    result = self._end_game()
                    result['response'] = [TextMessage(text=f"أي كلمة تبدأ بحرف: {last_letter}"), result['response']]
                    return result
            
            # تطبيع الحروف للمقارنة
            normalized_last = 'ه' if last_letter in ['ة', 'ه'] else last_letter
            normalized_answer = normalize_text(answer)
            
            # التحقق من الكلمات المستخدمة
            if normalized_answer in self.used_words:
                return {'response': TextMessage(text="الكلمة مستخدمة من قبل"), 'points': 0, 'correct': False}
            
            first_letter = answer[0].lower()
            first_letter = 'ه' if first_letter in ['ة', 'ه'] else first_letter
            
            # التحقق من الإجابة
            if first_letter == normalized_last or (normalized_last == 'ه' and first_letter in ['ه', 'ة']):
                self.used_words.add(normalized_answer)
                self.current_word = answer
                points = 1
                
                if user_id not in self.player_scores:
                    self.player_scores[user_id] = {'name': display_name, 'score': 0}
                self.player_scores[user_id]['score'] += points
                self.current_round_answered = True
                
                if self.current_question + 1 < self.total_questions:
                    return {'response': TextMessage(text=f"صحيح {display_name}\n+{points} نقطة"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
                else:
                    return self._end_game()
            else:
                return {'response': TextMessage(text=f"يجب أن تبدأ بحرف: {last_letter}"), 'points': 0, 'correct': False}
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
                            {"type": "button", "action": {"type": "message", "label": "اعادة اللعب", "text": "سلسله"}, "style": "primary", "margin": "lg"}
                        ],
                        "paddingAll": "20px"
                    }
                })
            )
            
            return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
        except Exception as e:
            logger.error(f"خطأ في إنهاء اللعبة: {e}")
            return {'response': TextMessage(text="حدث خطأ في إنهاء اللعبة"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
