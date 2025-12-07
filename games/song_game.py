from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import COLORS
from games.game_helpers import normalize_text, create_hint_text

SONGS = [
    {'lyrics': 'رجعت لي أيام الماضي معاك', 'singer': 'أم كلثوم'},
    {'lyrics': 'جلست والخوف بعينيها تتأمل فنجاني', 'singer': 'عبد الحليم حافظ'},
    {'lyrics': 'تملي معاك ولو حتى بعيد عني', 'singer': 'عمرو دياب'},
    {'lyrics': 'يا بنات يا بنات', 'singer': 'نانسي عجرم'},
    {'lyrics': 'قولي أحبك كي تزيد وسامتي', 'singer': 'كاظم الساهر'},
    {'lyrics': 'أنا لحبيبي وحبيبي إلي', 'singer': 'فيروز'},
    {'lyrics': 'حبيبي يا كل الحياة اوعدني تبقى معايا', 'singer': 'تامر حسني'},
    {'lyrics': 'قلبي بيسألني عنك دخلك طمني وينك', 'singer': 'وائل كفوري'},
    {'lyrics': 'كيف أبيّن لك شعوري دون ما أحكي', 'singer': 'عايض'},
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
    {'lyrics': 'الحب يتعب من يدله والله في حبه بلاني', 'singer': 'راشد الماجد'}
]

class SongGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.songs = SONGS
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.question_answered = False

    def start_game(self):
        self.questions = random.sample(self.songs, min(self.total_questions, len(self.songs)))
        self.current_question = 0
        self.player_scores = {}
        self.question_answered = False
        return self._show_question()

    def _show_question(self):
        song = self.questions[self.current_question]
        progress = f"{self.current_question + 1}/{self.total_questions}"
        
        return FlexMessage(
            alt_text="لعبه الاغنيه",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "لعبة الأغنية", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                        {"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": "السؤال", "size": "xs", "color": COLORS['text_light'], "flex": 0}, {"type": "text", "text": progress, "size": "xs", "color": COLORS['primary'], "weight": "bold", "align": "end"}], "margin": "lg"},
                        {"type": "separator", "margin": "md", "color": COLORS['border']},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": song['lyrics'], "size": "lg", "color": COLORS['text_dark'], "wrap": True, "weight": "bold", "align": "center"}, {"type": "text", "text": "من المغني؟", "size": "md", "color": COLORS['primary'], "margin": "md", "align": "center"}], "margin": "lg", "spacing": "sm"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "box", "layout": "horizontal", "contents": [{"type": "button", "action": {"type": "message", "label": "لمح", "text": "لمح"}, "style": "secondary", "height": "sm", "flex": 1}, {"type": "button", "action": {"type": "message", "label": "جاوب", "text": "جاوب"}, "style": "secondary", "height": "sm", "flex": 1}], "spacing": "sm", "margin": "lg"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            })
        )

    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.question_answered = False
            return self._show_question()
        return None

    def check_answer(self, answer, user_id, display_name):
        song = self.questions[self.current_question]

        if answer.lower() in ['لمح', 'تلميح']:
            hint = create_hint_text(song['singer'])
            return {'response': TextMessage(text=hint), 'points': 0, 'correct': False}

        if answer.lower() in ['جاوب', 'الجواب', 'الحل']:
            self.question_answered = True
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"الإجابة: {song['singer']}"), 'points': 0, 'correct': False, 'next_question': True}
            return self._end_game()

        if self.question_answered:
            return None

        if normalize_text(answer) == normalize_text(song['singer']):
            points = 1
            self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})
            self.player_scores[user_id]['score'] += points
            self.question_answered = True

            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"إجابة صحيحة {display_name}\n+{points} نقطة"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
            return self._end_game()

        return None

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبة بدون فائز"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}

        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        
        players_contents = []
        for i, p in enumerate(sorted_players[:5]):
            players_contents.append({"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": f"{i+1}.", "size": "sm", "flex": 0}, {"type": "text", "text": p[1]['name'], "size": "sm", "color": COLORS['text_dark'], "flex": 3, "margin": "sm"}, {"type": "text", "text": f"{p[1]['score']} نقطة", "size": "sm", "color": COLORS['primary'], "weight": "bold", "align": "end", "flex": 2}], "margin": "md" if i > 0 else "sm"})

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

        return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
