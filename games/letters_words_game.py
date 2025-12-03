"""
لعبة تكوين الكلمات - Letters Words Game
كوّن كلمات من الحروف المعطاة
"""

from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
import re
import logging
from constants import COLORS

logger = logging.getLogger(__name__)


def normalize_text(text):
    """تطبيع النص العربي للمقارنة"""
    if not text:
        return ""
    
    text = text.strip().lower()
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    text = text.replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '')
    text = text.replace('ة', 'ه').replace('ى', 'ي')
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'\s+', '', text)
    
    return text


class LettersWordsGame:
    """لعبة تكوين الكلمات من الحروف"""
    
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.challenges = [
            {"letters": "ق ل م ع ر ك", "answers": ["قلم", "علم", "عمر", "رقم", "ملك"]},
            {"letters": "ك ت ا ب ر ل", "answers": ["كتاب", "باب", "كتب", "تراب", "بكر"]},
            {"letters": "م د ر س ه ل", "answers": ["مدرسه", "سهل", "درس", "سهم", "مدر"]},
            {"letters": "ش ج ر ف ق ه", "answers": ["شجر", "فجر", "قهر", "شرف", "فرش"]},
            {"letters": "ح د ي ق ه ل", "answers": ["حديقه", "قديح", "حقل", "دقيق", "حيل"]},
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.found_words = {}
        self.valid_words = []
        self.words_needed = 3
        self.hints_used = {}
    
    def start_game(self):
        """بدء اللعبة"""
        try:
            self.questions = random.sample(self.challenges, self.total_questions)
            self.current_question = 0
            self.player_scores = {}
            self.found_words = {}
            self.hints_used = {}
            
            logger.info(f"بدء لعبة تكوين الكلمات - عدد الأسئلة: {self.total_questions}")
            return self._show_question()
        
        except Exception as e:
            logger.error(f"خطأ في بدء لعبة تكوين الكلمات: {e}")
            return TextMessage(text="حدث خطأ في بدء اللعبة")
    
    def _show_question(self):
        """عرض السؤال الحالي"""
        try:
            challenge = self.questions[self.current_question]
            letters = challenge['letters']
            progress = f"{self.current_question + 1}/{self.total_questions}"
            self.valid_words = [normalize_text(word) for word in challenge['answers']]
            
            return FlexMessage(
                alt_text="تكوين الكلمات",
                contents=FlexContainer.from_dict({
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "تكوين الكلمات",
                                        "weight": "bold",
                                        "size": "xl",
                                        "color": COLORS['white'],
                                        "align": "center"
                                    }
                                ],
                                "backgroundColor": COLORS['primary'],
                                "paddingAll": "20px",
                                "cornerRadius": "12px"
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "السؤال",
                                        "size": "xs",
                                        "color": COLORS['text_light'],
                                        "flex": 0
                                    },
                                    {
                                        "type": "text",
                                        "text": progress,
                                        "size": "xs",
                                        "color": COLORS['primary'],
                                        "weight": "bold",
                                        "align": "end"
                                    }
                                ],
                                "margin": "lg"
                            },
                            {
                                "type": "separator",
                                "margin": "md",
                                "color": COLORS['border']
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": letters,
                                        "size": "xxl",
                                        "color": COLORS['primary'],
                                        "weight": "bold",
                                        "align": "center"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"كون {self.words_needed} كلمات من هذه الحروف",
                                        "size": "sm",
                                        "color": COLORS['text_dark'],
                                        "margin": "md",
                                        "wrap": True,
                                        "align": "center"
                                    }
                                ],
                                "margin": "lg"
                            },
                            {
                                "type": "separator",
                                "margin": "lg",
                                "color": COLORS['border']
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "button",
                                        "action": {
                                            "type": "message",
                                            "label": "لمح",
                                            "text": "لمح"
                                        },
                                        "style": "secondary",
                                        "height": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "button",
                                        "action": {
                                            "type": "message",
                                            "label": "جاوب",
                                            "text": "جاوب"
                                        },
                                        "style": "secondary",
                                        "height": "sm",
                                        "flex": 1
                                    }
                                ],
                                "spacing": "sm",
                                "margin": "lg"
                            }
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
        """الانتقال للسؤال التالي"""
        self.current_question += 1
        
        if self.current_question < self.total_questions:
            self.found_words = {}
            self.hints_used = {}
            return self._show_question()
        
        return None
    
    def check_answer(self, text, user_id, display_name):
        """التحقق من إجابة اللاعب"""
        try:
            text = text.strip()
            
            # معالجة طلب التلميح
            if text.lower() in ['لمح', 'تلميح']:
                if user_id not in self.hints_used:
                    self.hints_used[user_id] = True
                    sample_word = self.questions[self.current_question]['answers'][0]
                    hint_text = f"أول حرف: {sample_word[0]}\nعدد الحروف: {len(sample_word)}"
                    logger.info(f"تلميح لـ {display_name}: {hint_text}")
                    
                    return {
                        'response': TextMessage(text=hint_text),
                        'points': 0,
                        'correct': False
                    }
                else:
                    return {
                        'response': TextMessage(text="لقد استخدمت التلميح بالفعل"),
                        'points': 0,
                        'correct': False
                    }
            
            # معالجة طلب الإجابة
            if text.lower() in ['جاوب', 'الحل']:
                some_words = ' - '.join(self.questions[self.current_question]['answers'][:5])
                
                if self.current_question + 1 < self.total_questions:
                    return {
                        'response': TextMessage(
                            text=f"بعض الكلمات الصحيحة:\n{some_words}"
                        ),
                        'points': 0,
                        'correct': False,
                        'next_question': True
                    }
                else:
                    return self._end_game()
            
            word_normalized = normalize_text(text)
            
            # التحقق من عدم التكرار
            if user_id in self.found_words and word_normalized in self.found_words[user_id]:
                return {
                    'response': TextMessage(text="هذه الكلمة أدخلتها من قبل"),
                    'points': 0,
                    'correct': False
                }
            
            # التحقق من صحة الكلمة
            is_valid = word_normalized in self.valid_words
            
            if not is_valid:
                return {
                    'response': TextMessage(text="هذه الكلمة غير صحيحة"),
                    'points': 0,
                    'correct': False
                }
            
            # إضافة الكلمة وتحديث النقاط
            if user_id not in self.found_words:
                self.found_words[user_id] = []
            
            self.found_words[user_id].append(word_normalized)
            
            if user_id not in self.player_scores:
                self.player_scores[user_id] = {
                    'name': display_name,
                    'score': 0
                }
            
            points = 1
            self.player_scores[user_id]['score'] += points
            words_count = len(self.found_words[user_id])
            
            logger.info(f"كلمة صحيحة من {display_name}: {text} ({words_count}/{self.words_needed})")
            
            # التحقق من اكتمال العدد المطلوب
            if words_count >= self.words_needed:
                if self.current_question + 1 < self.total_questions:
                    return {
                        'response': TextMessage(
                            text=f"إجابة صحيحة {display_name}\n+{points} نقطة"
                        ),
                        'points': points,
                        'correct': True,
                        'won': True,
                        'next_question': True
                    }
                else:
                    return self._end_game()
            else:
                return {
                    'response': TextMessage(
                        text=f"كلمة صحيحة\n+{points} نقطة\nالكلمات المتبقية: {self.words_needed - words_count}"
                    ),
                    'points': points,
                    'correct': True
                }
        
        except Exception as e:
            logger.error(f"خطأ في التحقق من الإجابة: {e}")
            return None
    
    def _end_game(self):
        """إنهاء اللعبة وعرض النتائج"""
        try:
            if not self.player_scores:
                return {
                    'response': TextMessage(text="انتهت اللعبة"),
                    'points': 0,
                    'correct': False,
                    'won': False,
                    'game_over': True
                }
            
            sorted_players = sorted(
                self.player_scores.items(),
                key=lambda x: x[1]['score'],
                reverse=True
            )
            
            winner = sorted_players[0][1]
            
            players_contents = []
            for i, (uid, player) in enumerate(sorted_players[:5]):
                players_contents.append({
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                        {"type": "text", "text": f"{i+1}.", "size": "sm", "flex": 0},
                        {"type": "text", "text": player['name'], "size": "sm", "color": COLORS['text_dark'], "flex": 3, "margin": "sm"},
                        {"type": "text", "text": f"{player['score']} نقطة", "size": "sm", "color": COLORS['primary'], "weight": "bold", "align": "end", "flex": 2}
                    ],
                    "margin": "md" if i > 0 else "sm"
                })
            
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
                            {"type": "button", "action": {"type": "message", "label": "إعادة اللعب", "text": "تكوين"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "lg"}
                        ],
                        "backgroundColor": COLORS['card_bg'],
                        "paddingAll": "20px"
                    }
                })
            )
            
            logger.info(f"انتهت اللعبة - الفائز: {winner['name']}")
            
            return {
                'response': winner_card,
                'points': winner['score'],
                'correct': True,
                'won': True,
                'game_over': True
            }
        
        except Exception as e:
            logger.error(f"خطأ في إنهاء اللعبة: {e}")
            return {
                'response': TextMessage(text="حدث خطأ في إنهاء اللعبة"),
                'points': 0,
                'correct': False,
                'won': False,
                'game_over': True
            }
