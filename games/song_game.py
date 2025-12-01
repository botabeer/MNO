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

class SongGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.songs = [
            {"lyrics": "أنا بلياك إذا أرمش إلك تنزل ألف دمعة", "singer": "ماجد المهندس"},
            {"lyrics": "يا بعدهم كلهم .. يا سراجي بينهم", "singer": "عبدالمجيد عبدالله"},
            {"lyrics": "أنا لحبيبي وحبيبي إلي", "singer": "فيروز"},
            {"lyrics": "قولي أحبك كي تزيد وسامتي", "singer": "كاظم الساهر"},
            {"lyrics": "كيف أبيّن لك شعوري دون ما أحكي", "singer": "عايض"},
            {"lyrics": "أريد الله يسامحني لان أذيت نفسي", "singer": "رحمة رياض"},
            {"lyrics": "جنّنت قلبي بحبٍ يلوي ذراعي", "singer": "ماجد المهندس"},
            {"lyrics": "واسِع خيالك إكتبه آنا بكذبك مُعجبه", "singer": "شمة حمدان"},
            {"lyrics": "خذني من ليلي لليلك", "singer": "عبادي الجوهر"},
            {"lyrics": "أنا عندي قلب واحد", "singer": "حسين الجسمي"},
            {"lyrics": "احس اني لقيتك بس عشان تضيع مني", "singer": "عبدالمجيد عبدالله"},
            {"lyrics": "قال الوداع و مقصده يجرح القلب", "singer": "راشد الماجد"},
            {"lyrics": "يا بنات يا بنات", "singer": "نانسي عجرم"},
            {"lyrics": "احبك موت كلمة مالها تفسير", "singer": "ماجد المهندس"},
            {"lyrics": "خلني مني طمني عليك", "singer": "نوال الكويتية"},
            {"lyrics": "رحت عني ما قويت جيت لك لاتردني", "singer": "عبدالمجيد عبدالله"},
            {"lyrics": "انسى هالعالم ولو هم يزعلون", "singer": "عباس ابراهيم"},
            {"lyrics": "مشاعر تشاور تودع تسافر", "singer": "شيرين"},
            {"lyrics": "جلست والخوف بعينيها تتأمل فنجاني", "singer": "عبد الحليم حافظ"},
            {"lyrics": "اسخر لك غلا وتشوفني مقصر", "singer": "عايض"}
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.answered_users = set()
        self.previous_answer = None
        self.hints_used = {}
        
    def start_game(self):
        self.questions = random.sample(self.songs, self.total_questions)
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        self.previous_answer = None
        self.hints_used = {}
        return self._show_question()
    
    def _show_question(self):
        song = self.questions[self.current_question]
        prev_text = f"\n\nالاجابة السابقة: {self.previous_answer}" if self.previous_answer else ""
        
        return FlexSendMessage(
            alt_text="لعبة الأغنية",
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
                                    "text": "لعبة الأغنية",
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
                                    "text": song['lyrics'] + prev_text,
                                    "size": "md",
                                    "color": COLORS['text_dark'],
                                    "wrap": True,
                                    "margin": "md"
                                },
                                {
                                    "type": "text",
                                    "text": "من المغني؟",
                                    "size": "sm",
                                    "color": COLORS['primary'],
                                    "margin": "md"
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
        song = self.questions[self.current_question]
        
        if answer_lower in ['لمح', 'تلميح']:
            if user_id not in self.hints_used:
                self.hints_used[user_id] = True
                first_letter = song['singer'][0]
                word_length = len(song['singer'])
                return {
                    'response': TextSendMessage(text=f"يبدأ بحرف: {first_letter}\nعدد الحروف: {word_length}"),
                    'points': 0,
                    'correct': False
                }
            return {'response': TextSendMessage(text="استخدمت التلميح"), 'points': 0, 'correct': False}
        
        if answer_lower in ['جاوب', 'الجواب']:
            self.previous_answer = song['singer']
            self.answered_users.add(user_id)
            if self.current_question + 1 < self.total_questions:
                return {
                    'response': TextSendMessage(text=f"الاجابة: {song['singer']}"),
                    'points': 0,
                    'correct': False,
                    'next_question': True
                }
            else:
                return self._end_game()
        
        if normalize_text(answer) == normalize_text(song['singer']):
            points = 10 if user_id not in self.hints_used else 7
            
            if user_id not in self.player_scores:
                self.player_scores[user_id] = {'name': display_name, 'score': 0}
            self.player_scores[user_id]['score'] += points
            
            self.answered_users.add(user_id)
            self.previous_answer = song['singer']
            
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
                            "action": {"type": "message", "label": "إعادة", "text": "أغنية"},
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
