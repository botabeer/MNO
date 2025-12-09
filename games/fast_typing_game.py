# games/fast_typing_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random, time
from constants import THEMES
from games.game_helpers import normalize_text, create_game_header, create_progress_box, create_separator, create_winner_card
from database import Database

class FastTypingGame:
    PHRASES = [
        "اكتب هذه العبارة بسرعة",
        "السماء زرقاء والشمس ساطعة",
        "التحدي يبدأ الان",
        "الوقت كالسيف ان لم تقطعه قطعك",
        "الصديق وقت الضيق",
        "الحياة قصيرة فلا تضيعها",
        "العلم نور والجهل ظلام",
        "اطلب العلم من المهد الى اللحد",
        "درهم وقاية خير من قنطار علاج",
        "من جد وجد ومن سار على الدرب وصل"
    ]

    def __init__(self, line_bot_api, total_questions=5):
        self.line_bot_api = line_bot_api
        self.total_questions = total_questions
        self.questions = []
        self.current_question = 0
        self.player_scores = {}
        self.question_start_time = None
        self.question_answered = False
        self.registered = set()

    def register_player(self, uid, name):
        self.registered.add(uid)
        return True

    def start_game(self):
        self.questions = random.sample(self.PHRASES, self.total_questions)
        self.current_question = 0
        self.player_scores = {}
        return self._show_question()

    def _show_question(self, theme="light"):
        colors = THEMES.get(theme, THEMES["light"])
        phrase = self.questions[self.current_question]
        self.question_start_time = time.time()
        self.question_answered = False

        contents = [
            create_game_header("التايب السريع", "اكتب الجملة فورا", theme=theme),
            create_progress_box(self.current_question+1, self.total_questions, theme=theme),
            create_separator(theme=theme),
            {
                "type": "text",
                "text": phrase,
                "size": "lg",
                "weight": "bold",
                "color": colors['primary'],
                "align": "center",
                "wrap": True,
                "margin": "lg"
            },
            {
                "type": "text",
                "text": "المؤقت يعمل الان",
                "size": "sm",
                "color": colors['text_light'],
                "align": "center",
                "margin": "md"
            }
        ]

        return FlexMessage(
            alt_text="التايب السريع",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": contents,
                    "backgroundColor": colors['card_bg'],
                    "paddingAll": "18px"
                }
            })
        )

    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            return self._show_question()
        return None

    def check_answer(self, answer, uid, name):
        if uid not in self.registered:
            return None
        if self.question_answered:
            return None

        phrase = self.questions[self.current_question]
        theme = Database.get_user_theme(uid)

        if normalize_text(answer) == normalize_text(phrase):
            time_taken = time.time() - self.question_start_time
            self.question_answered = True
            self.player_scores.setdefault(uid, {"name": name, "score": 0, "time": 0})
            self.player_scores[uid]["score"] += 1
            self.player_scores[uid]["time"] += time_taken

            msg = f"اسرع اجابة\n{name}\nالوقت: {time_taken:.1f} ثانية"

            if self.current_question + 1 < self.total_questions:
                return {"response": TextMessage(text=msg), "points": 1, "correct": True, "next_question": True}
            return self._end_game(uid, msg)
        return None

    def _end_game(self, uid, final_msg=""):
        theme = Database.get_user_theme(uid)
        if not self.player_scores:
            return {"response": TextMessage(text="انتهت اللعبة بدون فائز"), "game_over": True}

        sorted_players = sorted(self.player_scores.items(), key=lambda x: (-x[1]["score"], x[1]["time"]))
        winner = sorted_players[0][1]
        avg = winner["time"] / winner["score"]
        winner_info = winner.copy()
        winner_info["name"] = f"{winner['name']} - متوسط: {avg:.1f}ث"

        return {
            "response": FlexMessage(
                alt_text="نتائج اللعبة",
                contents=FlexContainer.from_dict(create_winner_card(winner_info, sorted_players, "التايب السريع", theme=theme))
            ),
            "game_over": True,
            "won": True
        }
