from linebot.models import TextSendMessage, FlexSendMessage
import random
import re
from datetime import datetime

COLORS = {
    'primary': '#00D4FF',
    'dark': '#1A1A2E',
    'card_bg': '#1E2A38',
    'text_light': '#8FA3B8',
    'text_dark': '#E8EEF3',
    'border': '#2D3E50'
}

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

class FastTypingGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.words = [
            "سرعة", "كتابة", "برمجة", "حاسوب", "إنترنت", "تطبيق", "موقع", "شبكة",
            "تقنية", "ذكاء", "استغفر الله", "تطوير", "مبرمج", "لغة", "كود", "برنامج",
            "نظام", "بيانات", "معلومات", "أمان"
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.start_time = None
        self.time_limit = 30
        self.answered_users = set()
    
    def start_game(self):
        self.questions = random.sample(self.words, self.total_questions)
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        self.start_time = datetime.now()
        return self._show_question()
    
    def _show_question(self):
        word = self.questions[self.current_question]
        self.start_time = datetime.now()
        
        return FlexSendMessage(
            alt_text="الكتابة السريعة",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "الكتابة السريعة",
                                    "weight": "bold",
                                    "size": "xl",
                                    "color": "#FFFFFF"
                                }
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "10px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"جولة {self.current_question + 1} من {self.total_questions}",
                                    "size": "sm",
                                    "color": COLORS['text_light']
                                },
                                {
                                    "type": "text",
                                    "text": word,
                                    "size": "xxl",
                                    "color": COLORS['primary'],
                                    "weight": "bold",
                                    "margin": "md",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": "اكتب الكلمة بأسرع وقت",
                                    "size": "sm",
                                    "color": COLORS['text_dark'],
                                    "margin": "md",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": f"لديك {self.time_limit} ثانية",
                                    "size": "xs",
                                    "color": COLORS['text_light'],
                                    "margin": "xs",
                                    "align": "center"
                                }
                            ],
                            "margin": "lg",
                            "spacing": "sm"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )
    
    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.answered_users = set()
            return self._show_question()
        return None
    
    def check_answer(self, text, user_id, display_name):
        if user_id in self.answered_users:
            return None
        
        if self.start_time and (datetime.now() - self.start_time).seconds > self.time_limit:
            if self.current_question + 1 < self.total_questions:
                return {
                    'response': TextSendMessage(text="انتهى الوقت"),
                    'points': 0,
                    'correct': False,
                    'next_question': True
                }
            else:
                return self._end_game()
        
        text_normalized = normalize_text(text)
        word_normalized = normalize_text(self.questions[self.current_question])
        
        if text_normalized == word_normalized:
            elapsed_time = (datetime.now() - self.start_time).total_seconds()
            points = max(5, int(20 - elapsed_time))
            
            if user_id not in self.player_scores:
                self.player_scores[user_id] = {'name': display_name, 'score': 0}
            self.player_scores[user_id]['score'] += points
            
            self.answered_users.add(user_id)
            
            if self.current_question + 1 < self.total_questions:
                return {
                    'response': TextSendMessage(text=f"اجابة صحيحة {display_name}\nالوقت: {elapsed_time:.2f}ث\n+{points} نقطة"),
                    'points': points,
                    'correct': True,
                    'won': True,
                    'next_question': True
                }
            else:
                return self._end_game()
        
        return None
    
    def _end_game(self):
        if not self.player_scores:
            return {
                'response': TextSendMessage(text="انتهت اللعبة"),
                'points': 0,
                'correct': False,
                'won': False,
                'game_over': True
            }
        
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        
        players_text = "\n".join([f"{i+1}. {p[1]['name']}: {p[1]['score']} نقطة" 
                                  for i, p in enumerate(sorted_players[:5])])
        
        winner_card = FlexSendMessage(
            alt_text="نتائج اللعبة",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "انتهت اللعبة",
                                    "weight": "bold",
                                    "size": "xl",
                                    "color": "#FFFFFF"
                                }
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "10px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "الفائز",
                                    "size": "sm",
                                    "color": COLORS['text_light']
                                },
                                {
                                    "type": "text",
                                    "text": winner['name'],
                                    "size": "xxl",
                                    "color": COLORS['primary'],
                                    "weight": "bold",
                                    "margin": "xs"
                                },
                                {
                                    "type": "text",
                                    "text": f"{winner['score']} نقطة",
                                    "size": "lg",
                                    "color": COLORS['text_dark'],
                                    "margin": "xs"
                                }
                            ],
                            "margin": "lg",
                            "spacing": "xs"
                        },
                        {
                            "type": "separator",
                            "margin": "lg",
                            "color": COLORS['border']
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "النتائج",
                                    "size": "sm",
                                    "color": COLORS['text_light']
                                },
                                {
                                    "type": "text",
                                    "text": players_text,
                                    "size": "sm",
                                    "color": COLORS['text_dark'],
                                    "wrap": True,
                                    "margin": "md"
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
                            "type": "button",
                            "action": {"type": "message", "label": "إعادة", "text": "أسرع"},
                            "style": "primary",
                            "color": COLORS['primary'],
                            "height": "sm",
                            "margin": "lg"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )
        
        return {
            'response': winner_card,
            'points': winner['score'],
            'correct': True,
            'won': True,
            'game_over': True
        }
