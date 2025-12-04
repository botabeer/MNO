"""
لعبة الأغنية - Song Game
لعبة تخمين اسم المغني من كلمات الأغنية
"""

from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
import re
import logging
from constants import COLORS

logger = logging.getLogger(__name__)

SONGS = [
    {'lyrics': 'رجعت لي أيام الماضي معاك', 'singer': 'أم كلثوم'},
    {'lyrics': 'جلست والخوف بعينيها تتأمل فنجاني', 'singer': 'عبد الحليم حافظ'},
    {'lyrics': 'تملي معاك ولو حتى بعيد عني', 'singer': 'عمرو دياب'},
    {'lyrics': 'يا بنات يا بنات', 'singer': 'نانسي عجرم'},
    {'lyrics': 'قولي أحبك كي تزيد وسامتي', 'singer': 'كاظم الساهر'},
    {'lyrics': 'أنا لحبيبي وحبيبي إلي', 'singer': 'فيروز'},
    {'lyrics': 'حبيبي يا كل الحياة اوعدني تبقى معايا', 'singer': 'تامر حسني'},
    {'lyrics': 'قلبي بيسألني عنك دخلك طمني وينك', 'singer': 'وائل كفوري'},
    {'lyrics': 'كيف أبين لك شعوري دون ما أحكي', 'singer': 'عايض'},
    {'lyrics': 'اسخر لك غلا وتشوفني مقصر', 'singer': 'عايض'},
    {'lyrics': 'رحت عني ما قويت جيت لك لاتردني', 'singer': 'عبدالمجيد عبدالله'},
    {'lyrics': 'خذني من ليلي لليلك', 'singer': 'عبادي الجوهر'},
    {'lyrics': 'تدري كثر ماني من البعد مخنوق', 'singer': 'راشد الماجد'},
    {'lyrics': 'انسى هالعالم ولو هم يزعلون', 'singer': 'عباس ابراهيم'},
    {'lyrics': 'أنا عندي قلب واحد', 'singer': 'حسين الجسمي'},
    {'lyrics': 'منوتي ليتك معي', 'singer': 'محمد عبده'},
    {'lyrics': 'خلنا مني طمني عليك', 'singer': 'نوال الكويتية'},
    {'lyrics': 'أحبك ليه أنا مدري', 'singer': 'عبدالمجيد عبدالله'},
    {'lyrics': 'أمر الله أقوى أحبك والعقل واعي', 'singer': 'ماجد المهندس'},
    {'lyrics': 'الحب يتعب من يدله والله في حبه بلاني', 'singer': 'راشد الماجد'},
]


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


class SongGame:
    """لعبة تخمين اسم المغني من كلمات الأغنية"""
    
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.songs = SONGS
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.answered_users = set()
        self.hints_used = {}
    
    def start_game(self):
        """بدء اللعبة"""
        try:
            self.questions = random.sample(self.songs, min(self.total_questions, len(self.songs)))
            self.current_question = 0
            self.player_scores = {}
            self.answered_users = set()
            self.hints_used = {}
            
            logger.info(f"بدء لعبة الأغنية - عدد الأسئلة: {self.total_questions}")
            return self._show_question()
        
        except Exception as e:
            logger.error(f"خطأ في بدء لعبة الأغنية: {e}")
            return TextMessage(text="حدث خطأ في بدء اللعبة")
    
    def _show_question(self):
        """عرض السؤال الحالي"""
        try:
            song = self.questions[self.current_question]
            progress = f"{self.current_question + 1}/{self.total_questions}"
            
            return FlexMessage(
                alt_text="لعبة الأغنية",
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
                                        "text": "لعبة الأغنية",
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
                                        "text": song['lyrics'],
                                        "size": "lg",
                                        "color": COLORS['text_dark'],
                                        "wrap": True,
                                        "weight": "bold",
                                        "align": "center"
                                    },
                                    {
                                        "type": "text",
                                        "text": "من المغني؟",
                                        "size": "md",
                                        "color": COLORS['primary'],
                                        "margin": "md",
                                        "align": "center"
                                    }
                                ],
                                "margin": "lg",
                                "spacing": "sm"
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
            self.answered_users = set()
            self.hints_used = {}
            return self._show_question()
        
        return None
    
    def check_answer(self, answer, user_id, display_name):
        """التحقق من إجابة اللاعب"""
        try:
            if user_id in self.answered_users:
                return None
            
            song = self.questions[self.current_question]
            answer = answer.strip()
            
            # معالجة طلب التلميح
            if answer.lower() in ['لمح', 'تلميح']:
                hint_text = f"أول حرف: {song['singer'][0]}\nعدد الحروف: {len(song['singer'])}"
                logger.info(f"تلميح لـ {display_name}: {hint_text}")
                
                return {
                    'response': TextMessage(text=hint_text),
                    'points': 0,
                    'correct': False
                }
            
            # معالجة طلب الإجابة
            if answer.lower() in ['جاوب', 'الجواب', 'الحل']:
                self.answered_users.add(user_id)
                answer_text = f"الإجابة: {song['singer']}"
                
                if self.current_question + 1 < self.total_questions:
                    return {
                        'response': TextMessage(text=answer_text),
                        'points': 0,
                        'correct': False,
                        'next_question': True
                    }
                else:
                    return self._end_game()
            
            # التحقق من الإجابة
            if normalize_text(answer) == normalize_text(song['singer']):
                points = 1
                
                if user_id not in self.player_scores:
                    self.player_scores[user_id] = {
                        'name': display_name,
                        'score': 0
                    }
                
                self.player_scores[user_id]['score'] += points
                self.answered_users.add(user_id)
                
                logger.info(f"إجابة صحيحة من {display_name}: {answer}")
                
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
            
            return None
        
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
                            {"type": "button", "action": {"type": "message", "label": "إعادة اللعب", "text": "اغنيه"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "lg"}
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
