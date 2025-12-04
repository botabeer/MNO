"""
لعبة الأضداد - Opposite Game
لعبة تخمين عكس الكلمة المعطاة
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


class OppositeGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.all_words = [
            {"word": "كبير", "opposite": "صغير"},
            {"word": "طويل", "opposite": "قصير"},
            {"word": "سريع", "opposite": "بطيء"},
            {"word": "ساخن", "opposite": "بارد"},
            {"word": "نظيف", "opposite": "وسخ"},
            {"word": "قوي", "opposite": "ضعيف"},
            {"word": "سهل", "opposite": "صعب"},
            {"word": "جميل", "opposite": "قبيح"},
            {"word": "غني", "opposite": "فقير"},
            {"word": "فوق", "opposite": "تحت"},
            {"word": "يمين", "opposite": "يسار"},
            {"word": "أمام", "opposite": "خلف"},
            {"word": "داخل", "opposite": "خارج"},
            {"word": "قريب", "opposite": "بعيد"},
            {"word": "جديد", "opposite": "قديم"},
            {"word": "ثقيل", "opposite": "خفيف"},
            {"word": "مظلم", "opposite": "مضيء"},
            {"word": "صادق", "opposite": "كاذب"},
            {"word": "شجاع", "opposite": "جبان"},
            {"word": "نشيط", "opposite": "كسول"},
            {"word": "ممتلئ", "opposite": "فارغ"},
            {"word": "واسع", "opposite": "ضيق"},
            {"word": "عالي", "opposite": "منخفض"},
            {"word": "حار", "opposite": "بارد"},
            {"word": "رطب", "opposite": "جاف"},
            {"word": "صحيح", "opposite": "خطأ"},
            {"word": "مفتوح", "opposite": "مغلق"},
            {"word": "نعم", "opposite": "لا"},
            {"word": "أبيض", "opposite": "أسود"},
            {"word": "نهار", "opposite": "ليل"},
            {"word": "شتاء", "opposite": "صيف"},
            {"word": "ذكي", "opposite": "غبي"},
            {"word": "حلو", "opposite": "مر"},
            {"word": "سعيد", "opposite": "حزين"},
            {"word": "حي", "opposite": "ميت"},
            {"word": "نائم", "opposite": "مستيقظ"},
            {"word": "صاعد", "opposite": "نازل"},
            {"word": "محبوب", "opposite": "مكروه"},
            {"word": "شرير", "opposite": "طيب"},
            {"word": "رخيص", "opposite": "غالي"},
            {"word": "جاهل", "opposite": "عالم"},
            {"word": "بخيل", "opposite": "كريم"},
            {"word": "صحي", "opposite": "مريض"},
            {"word": "مريح", "opposite": "متعب"},
            {"word": "حديث", "opposite": "قديم"},
            {"word": "ناجح", "opposite": "فاشل"},
            {"word": "محظوظ", "opposite": "منحوس"},
            {"word": "مبكر", "opposite": "متأخر"},
            {"word": "أول", "opposite": "آخر"},
            {"word": "بداية", "opposite": "نهاية"},
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.answered_users = set()
    
    def start_game(self):
        try:
            self.questions = random.sample(self.all_words, self.total_questions)
            self.current_question = 0
            self.player_scores = {}
            self.answered_users = set()
            logger.info(f"بدء لعبة الأضداد - عدد الأسئلة: {self.total_questions}")
            return self._show_question()
        except Exception as e:
            logger.error(f"خطأ في بدء لعبة الأضداد: {e}")
            return TextMessage(text="حدث خطأ في بدء اللعبة")
    
    def _show_question(self):
        try:
            word = self.questions[self.current_question]
            progress = f"{self.current_question + 1}/{self.total_questions}"
            
            return FlexMessage(
                alt_text="لعبة الأضداد",
                contents=FlexContainer.from_dict({
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
                            {"type": "box", "layout": "horizontal", "contents": [{"type": "button", "action": {"type": "message", "label": "لمح", "text": "لمح"}, "style": "secondary", "height": "sm", "flex": 1}, {"type": "button", "action": {"type": "message", "label": "جاوب", "text": "جاوب"}, "style": "secondary", "height": "sm", "flex": 1}], "spacing": "sm", "margin": "lg"}
                        ],
                        "backgroundColor": COLORS['card_bg'],
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
            self.answered_users = set()
            return self._show_question()
        return None
    
    def check_answer(self, answer, user_id, display_name):
        try:
            if user_id in self.answered_users:
                return None
            
            word = self.questions[self.current_question]
            answer = answer.strip()
            
            if answer.lower() in ['لمح', 'تلميح']:
                hint_text = f"أول حرف: {word['opposite'][0]}\nعدد الحروف: {len(word['opposite'])}"
                return {'response': TextMessage(text=hint_text), 'points': 0, 'correct': False}
            
            if answer.lower() in ['جاوب', 'الجواب', 'الحل']:
                self.answered_users.add(user_id)
                if self.current_question + 1 < self.total_questions:
                    return {'response': TextMessage(text=f"الإجابة: {word['opposite']}"), 'points': 0, 'correct': False, 'next_question': True}
                else:
                    result = self._end_game()
                    result['response'] = [TextMessage(text=f"الإجابة: {word['opposite']}"), result['response']]
                    return result
            
            if normalize_text(answer) == normalize_text(word['opposite']):
                points = 1
                if user_id not in self.player_scores:
                    self.player_scores[user_id] = {'name': display_name, 'score': 0}
                self.player_scores[user_id]['score'] += points
                self.answered_users.add(user_id)
                
                if self.current_question + 1 < self.total_questions:
                    return {'response': TextMessage(text=f"إجابة صحيحة {display_name}\n+{points} نقطة"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
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
                players_contents.append({"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": f"{i+1}.", "size": "sm", "flex": 0}, {"type": "text", "text": player['name'], "size": "sm", "color": COLORS['text_dark'], "flex": 3, "margin": "sm"}, {"type": "text", "text": f"{player['score']} نقطة", "size": "sm", "color": COLORS['primary'], "weight": "bold", "align": "end", "flex": 2}], "margin": "md" if i > 0 else "sm"})
            
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
                            {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "الفائز", "size": "sm", "color": COLORS['text_light'], "align": "center"}, {"type": "text", "text": winner['name'], "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center", "margin": "xs"}, {"type": "text", "text": f"{winner['score']} نقطة", "size": "lg", "color": COLORS['success'], "align": "center", "margin": "xs"}], "margin": "lg"},
                            {"type": "separator", "margin": "lg", "color": COLORS['border']},
                            {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "النتائج", "size": "md", "color": COLORS['text_dark'], "weight": "bold"}, *players_contents], "margin": "lg"},
                            {"type": "separator", "margin": "lg", "color": COLORS['border']},
                            {"type": "button", "action": {"type": "message", "label": "إعادة اللعب", "text": "ضد"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "lg"}
                        ],
                        "backgroundColor": COLORS['card_bg'],
                        "paddingAll": "20px"
                    }
                })
            )
            
            return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
        except Exception as e:
            logger.error(f"خطأ في إنهاء اللعبة: {e}")
            return {'response': TextMessage(text="حدث خطأ في إنهاء اللعبة"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
