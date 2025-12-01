from linebot.models import TextSendMessage, FlexSendMessage
import random
import re
from constants import COLORS

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
            {"lyrics": "أنا عندي قلب واحد", "singer": "حسين الجسمي"}
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

    def _progress_bar(self):
        percent = int(((self.current_question + 1) / self.total_questions) * 100)
        filled = int(percent / 10)
        return "█" * filled + "░" * (10 - filled)

    def _show_question(self):
        song = self.questions[self.current_question]

        footer_buttons = {
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "action": {"type": "message", "label": "لمح", "text": "لمح"},
                    "style": "secondary"
                },
                {
                    "type": "button",
                    "action": {"type": "message", "label": "جاوب", "text": "جاوب"},
                    "style": "secondary"
                },
                {
                    "type": "button",
                    "action": {"type": "message", "label": "إيقاف", "text": "إيقاف"},
                    "style": "secondary"
                }
            ]
        }

        return FlexSendMessage(
            alt_text="لعبة الأغنية",
            contents={
                "type": "bubble",
                "size": "mega",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": "لعبة الأغنية",
                            "weight": "bold",
                            "size": "xl",
                            "color": COLORS['white']
                        },
                        {
                            "type": "text",
                            "text": f"{self._progress_bar()} {self.current_question + 1}/{self.total_questions}",
                            "size": "sm",
                            "color": COLORS['text_light']
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "backgroundColor": COLORS['card_bg'],
                            "paddingAll": "16px",
                            "cornerRadius": "12px",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": song['lyrics'],
                                    "wrap": True,
                                    "size": "md",
                                    "color": COLORS['white']
                                },
                                {
                                    "type": "text",
                                    "text": "من المغني",
                                    "margin": "md",
                                    "size": "sm",
                                    "weight": "bold",
                                    "color": COLORS['primary']
                                }
                            ]
                        },
                        footer_buttons
                    ],
                    "backgroundColor": COLORS['background'],
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

        song = self.questions[self.current_question]

        if answer in ['لمح', 'تلميح']:
            if user_id not in self.hints_used:
                self.hints_used[user_id] = True
                first_letter = song['singer'][0]
                word_length = len(song['singer'])
                return {
                    'response': TextSendMessage(
                        text=f"يبدأ بحرف: {first_letter}\nعدد الحروف: {word_length}"
                    ),
                    'points': 0,
                    'correct': False
                }
            return {'response': TextSendMessage(text="تم استخدام التلميح مسبقًا"), 'points': 0, 'correct': False}

        if answer in ['جاوب', 'الجواب']:
            self.previous_answer = song['singer']
            self.answered_users.add(user_id)
            if self.current_question + 1 < self.total_questions:
                return {
                    'response': TextSendMessage(text=f"الإجابة: {song['singer']}"),
                    'points': 0,
                    'correct': False,
                    'next_question': True
                }
            return self._end_game()

        if normalize_text(answer) == normalize_text(song['singer']):
            points = 10 if user_id not in self.hints_used else 7

            self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})
            self.player_scores[user_id]['score'] += points
            self.answered_users.add(user_id)
            self.previous_answer = song['singer']

            return {
                'response': TextSendMessage(
                    text=f"إجابة صحيحة {display_name}\nتمت إضافة {points} نقاط"
                ),
                'points': points,
                'correct': True,
                'won': True,
                'next_question': True
            }

        return {
            'response': TextSendMessage(text="إجابة خاطئة"),
            'points': 0,
            'correct': False
        }

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

        players_text = "\n".join([
            f"{p[1]['name']} - {p[1]['score']} نقطة"
            for p in sorted_players[:5]
        ])

        winner_card = FlexSendMessage(
            alt_text="نتائج اللعبة",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": "انتهت اللعبة",
                            "weight": "bold",
                            "size": "xl",
                            "color": COLORS['white']
                        },
                        {
                            "type": "text",
                            "text": f"الفائز: {winner['name']}",
                            "size": "lg",
                            "color": COLORS['primary']
                        },
                        {
                            "type": "text",
                            "text": players_text,
                            "wrap": True,
                            "size": "sm",
                            "color": COLORS['text_light']
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "إعادة اللعب", "text": "أغنية"},
                            "style": "primary"
                        }
                    ],
                    "backgroundColor": COLORS['background'],
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
