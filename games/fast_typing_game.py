"""
لعبة الكتابة السريعة - Fast Typing Game
اكتب النص بأسرع وقت ممكن - بدون لمح أو جاوب
"""

from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
import re
import logging
from datetime import datetime
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
    text = re.sub(r'\s+', ' ', text)
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
            "بسم الله الرحمن الرحيم",
            "اللهم صل على محمد"
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.start_time = None
        self.time_limit = 60
        self.current_round_answered = False
    
    def start_game(self):
        try:
            self.questions = random.sample(self.words, min(self.total_questions, len(self.words)))
            self.current_question = 0
            self.player_scores = {}
            self.current_round_answered = False
            self.start_time = datetime.now()
            logger.info(f"بدء لعبة الكتابة السريعة - عدد الأسئلة: {self.total_questions}")
            return self._show_question()
        except Exception as e:
            logger.error(f"خطأ في بدء لعبة الكتابة السريعة: {e}")
            return TextMessage(text="حدث خطأ في بدء اللعبة")
    
    def _show_question(self):
        try:
            word = self.questions[self.current_question]
            progress = f"{self.current_question + 1}/{self.total_questions}"
            self.start_time = datetime.now()
            
            return FlexMessage(
                alt_text="الكتابة السريعة",
                contents=FlexContainer.from_dict({
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "contents": [
                            {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "الكتابة السريعة", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                            {"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": "السؤال", "size": "xs", "color": COLORS['text_light'], "flex": 0}, {"type": "text", "text": progress, "size": "xs", "color": COLORS['primary'], "weight": "bold", "align": "end"}], "margin": "lg"},
                            {"type": "separator", "margin": "md"},
                            {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": word, "size": "lg", "color": COLORS['primary'], "weight": "bold", "align": "center", "wrap": True}, {"type": "text", "text": "اكتب النص بأسرع وقت", "size": "sm", "margin": "md", "align": "center"}], "margin": "lg"}
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
    
    def check_answer(self, text, user_id, display_name):
        try:
            # تجاهل الإجابات بعد أول إجابة صحيحة
            if self.current_round_answered:
                return None
            
            text = text.strip()
            word = self.questions[self.current_question]
            
            # التحقق من انتهاء الوقت
            if self.start_time:
                elapsed = (datetime.now() - self.start_time).seconds
                if elapsed > self.time_limit:
                    self.current_round_answered = True
                    
                    if self.current_question + 1 < self.total_questions:
                        return {'response': TextMessage(text="انتهى الوقت"), 'points': 0, 'correct': False, 'next_question': True}
                    else:
                        return self._end_game()
            
            text_normalized = normalize_text(text)
            word_normalized = normalize_text(word)
            
            # التحقق من الإجابة
            if text_normalized == word_normalized:
                elapsed_time = (datetime.now() - self.start_time).total_seconds()
                points = max(1, int(10 - elapsed_time / 6))
                
                if user_id not in self.player_scores:
                    self.player_scores[user_id] = {'name': display_name, 'score': 0, 'time': 0}
                self.player_scores[user_id]['score'] += points
                self.player_scores[user_id]['time'] += elapsed_time
                
                self.current_round_answered = True
                
                if self.current_question + 1 < self.total_questions:
                    return {'response': TextMessage(text=f"صحيح {display_name}\nالوقت: {elapsed_time:.1f}ث\n+{points} نقطة"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
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
            
            sorted_players = sorted(self.player_scores.items(), key=lambda x: (x[1]['score'], -x[1]['time']), reverse=True)
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
                            {"type": "button", "action": {"type": "message", "label": "اعادة اللعب", "text": "اسرع"}, "style": "primary", "margin": "lg"}
                        ],
                        "paddingAll": "20px"
                    }
                })
            )
            
            return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
        except Exception as e:
            logger.error(f"خطأ في إنهاء اللعبة: {e}")
            return {'response': TextMessage(text="حدث خطأ في إنهاء اللعبة"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
