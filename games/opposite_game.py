from linebot.models import TextSendMessage, FlexSendMessage
import random
import re

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
            {"word": "نشيط", "opposite": "كسول"}
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.answered_users = set()
        self.previous_answer = None
        self.hints_used = {}
        
    def start_game(self):
        self.questions = random.sample(self.all_words, self.total_questions)
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        self.previous_answer = None
        self.hints_used = {}
        return self._show_question()
    
    def _show_question(self):
        word = self.questions[self.current_question]
        prev_text = f"\n\nالاجابة السابقة: {self.previous_answer}" if self.previous_answer else ""
        
        return FlexSendMessage(
            alt_text="لعبة الأضداد",
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
                                    "text": "لعبة الأضداد",
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
                                    "text": f"السؤال {self.current_question + 1} من {self.total_questions}",
                                    "size": "sm",
                                    "color": COLORS['text_light']
                                },
                                {
                                    "type": "text",
                                    "text": f"ما هو عكس: {word['word']}" + prev_text,
                                    "size": "lg",
                                    "color": COLORS['text_dark'],
                                    "wrap": True,
                                    "margin": "md",
                                    "weight": "bold"
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
                                    "action": {"type": "message", "label": "لمح", "text": "لمح"},
                                    "style": "secondary",
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {"type": "message", "label": "جاوب", "text": "جاوب"},
                                    "style": "secondary",
                                    "height": "sm"
                                }
                            ],
                            "spacing": "sm",
                            "margin": "lg"
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
            self.hints_used = {}
            return self._show_question()
        return None
    
    def check_answer(self, answer, user_id, display_name):
        if user_id in self.answered_users:
            return None
            
        answer_lower = answer.strip().lower()
        word = self.questions[self.current_question]
        
        if answer_lower in ['لمح', 'تلميح']:
            if user_id not in self.hints_used:
                self.hints_used[user_id] = True
                first_letter = word['opposite'][0]
                word_length = len(word['opposite'])
                return {
                    'response': TextSendMessage(text=f"يبدأ بحرف: {first_letter}\nعدد الحروف: {word_length}"),
                    'points': 0,
                    'correct': False
                }
            return {'response': TextSendMessage(text="استخدمت التلميح"), 'points': 0, 'correct': False}
        
        if answer_lower in ['جاوب', 'الجواب']:
            self.previous_answer = word['opposite']
            self.answered_users.add(user_id)
            if self.current_question + 1 < self.total_questions:
                return {
                    'response': TextSendMessage(text=f"الاجابة: {word['opposite']}"),
                    'points': 0,
                    'correct': False,
                    'next_question': True
                }
            else:
                return self._end_game()
        
        if normalize_text(answer) == normalize_text(word['opposite']):
            points = 10 if user_id not in self.hints_used else 7
            
            if user_id not in self.player_scores:
                self.player_scores[user_id] = {'name': display_name, 'score': 0}
            self.player_scores[user_id]['score'] += points
            
            self.answered_users.add(user_id)
            self.previous_answer = word['opposite']
            
            if self.current_question + 1 < self.total_questions:
                return {
                    'response': TextSendMessage(text=f"اجابة صحيحة {display_name}\n+{points} نقطة"),
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
                            "action": {"type": "message", "label": "إعادة", "text": "ضد"},
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
