from linebot.models import TextSendMessage, FlexSendMessage
import random
import re
from constants import COLORS
from ui_builder import UIBuilder

SONGS = [
    {'lyrics':'رجعت لي أيام الماضي معاك','singer':'أم كلثوم'},
    {'lyrics':'جلست والخوف بعينيها تتأمل فنجاني','singer':'عبد الحليم حافظ'},
    {'lyrics':'تملي معاك ولو حتى بعيد عني','singer':'عمرو دياب'},
    {'lyrics':'يا بنات يا بنات','singer':'نانسي عجرم'},
    {'lyrics':'قولي أحبك كي تزيد وسامتي','singer':'كاظم الساهر'},
    {'lyrics':'أنا لحبيبي وحبيبي إلي','singer':'فيروز'},
    {'lyrics':'حبيبي يا كل الحياة اوعدني تبقى معايا','singer':'تامر حسني'},
    {'lyrics':'قلبي بيسألني عنك دخلك طمني وينك','singer':'وائل كفوري'},
    {'lyrics':'كيف أبيّن لك شعوري دون ما أحكي','singer':'عايض'},
    {'lyrics':'اسخر لك غلا وتشوفني مقصر','singer':'عايض'},
    {'lyrics':'رحت عني ما قويت جيت لك لاتردني','singer':'عبدالمجيد عبدالله'},
    {'lyrics':'خذني من ليلي لليلك','singer':'عبادي الجوهر'},
    {'lyrics':'تدري كثر ماني من البعد مخنوق','singer':'راشد الماجد'},
    {'lyrics':'انسى هالعالم ولو هم يزعلون','singer':'عباس ابراهيم'},
    {'lyrics':'أنا عندي قلب واحد','singer':'حسين الجسمي'},
    {'lyrics':'منوتي ليتك معي','singer':'محمد عبده'},
    {'lyrics':'خلنا مني طمني عليك','singer':'نوال الكويتية'},
    {'lyrics':'أحبك ليه أنا مدري','singer':'عبدالمجيد عبدالله'},
    {'lyrics':'أمر الله أقوى أحبك والعقل واعي','singer':'ماجد المهندس'},
    {'lyrics':'الحب يتعب من يدله والله في حبه بلاني','singer':'راشد الماجد'}
]

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
        self.songs = SONGS
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.answered_users = set()
        self.hints_used = {}

    def start_game(self):
        self.questions = random.sample(self.songs, self.total_questions)
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        self.hints_used = {}
        return self._show_question()

    def _show_question(self):
        song = self.questions[self.current_question]
        return FlexSendMessage(
            alt_text="لعبه الاغنيه",
            contents=UIBuilder.game_card(
                "لعبة الاغنية",
                f"{song['lyrics']}\n\nمن المغني",
                self.current_question + 1,
                self.total_questions
            )
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
                return {'response': TextSendMessage(text=f"يبدا بحرف {first_letter}\nعدد الحروف {word_length}"), 'points': 0, 'correct': False}
            return {'response': TextSendMessage(text="استخدمت التلميح"), 'points': 0, 'correct': False}

        if answer in ['جاوب', 'الجواب']:
            self.answered_users.add(user_id)
            if self.current_question + 1 < self.total_questions:
                return {'response': TextSendMessage(text=f"الاجابه {song['singer']}"), 'points': 0, 'correct': False, 'next_question': True}
            return self._end_game()

        if normalize_text(answer) == normalize_text(song['singer']):
            points = 1
            self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})
            self.player_scores[user_id]['score'] += points
            self.answered_users.add(user_id)

            if self.current_question + 1 < self.total_questions:
                return {'response': TextSendMessage(text=f"اجابه صحيحه {display_name}\nنقطه {points}"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
            return self._end_game()

        return None

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextSendMessage(text="انتهت اللعبه"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}

        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        players_text = "\n".join([f"{i+1}. {p[1]['name']} {p[1]['score']} نقطه" for i, p in enumerate(sorted_players[:5])])

        winner_card = FlexSendMessage(
            alt_text="نتائج اللعبه",
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
                                {"type": "text", "text": "انتهت اللعبه", "weight": "bold", "size": "xl", "color": COLORS['text'], "align": "center"}
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "15px",
                            "cornerRadius": "8px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "الفائز", "size": "xs", "color": COLORS['text_secondary'], "align": "center"},
                                {"type": "text", "text": winner['name'], "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center", "margin": "xs"},
                                {"type": "text", "text": f"{winner['score']} نقطه", "size": "lg", "color": COLORS['text'], "align": "center", "margin": "xs"}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "النتائج", "size": "sm", "color": COLORS['text_secondary']},
                                {"type": "text", "text": players_text, "size": "sm", "color": COLORS['text'], "wrap": True, "margin": "md"}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "اعاده", "text": "اغنيه"},
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

        return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
