from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import COLORS
from games.game_helpers import (
    normalize_text,
    create_game_header,
    create_progress_box,
    create_separator,
    create_action_buttons,
    create_winner_card
)

class OppositeGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api

        self.all_words = [
            {"word": "كبير", "opposite": "صغير"}, {"word": "طويل", "opposite": "قصير"},
            {"word": "سريع", "opposite": "بطيء"}, {"word": "ساخن", "opposite": "بارد"},
            {"word": "نظيف", "opposite": "وسخ"}, {"word": "قوي", "opposite": "ضعيف"},
            {"word": "سهل", "opposite": "صعب"}, {"word": "جميل", "opposite": "قبيح"},
            {"word": "غني", "opposite": "فقير"}, {"word": "فوق", "opposite": "تحت"},
            {"word": "يمين", "opposite": "يسار"}, {"word": "أمام", "opposite": "خلف"},
            {"word": "داخل", "opposite": "خارج"}, {"word": "قريب", "opposite": "بعيد"},
            {"word": "جديد", "opposite": "قديم"}, {"word": "ثقيل", "opposite": "خفيف"},
            {"word": "مظلم", "opposite": "مضيء"}, {"word": "صادق", "opposite": "كاذب"},
            {"word": "شجاع", "opposite": "جبان"}, {"word": "نشيط", "opposite": "كسول"}
        ]

        self.questions = []
        self.current_question = 0
        self.total_questions = 5

        self.player_scores = {}
        self.answered_users = set()
        self.hints_used = {}

    # ----------------------------------------------------------
    # Start Game
    # ----------------------------------------------------------

    def start_game(self):
        self.questions = random.sample(self.all_words, self.total_questions)
        self.current_question = 0
        self.player_scores.clear()
        self.answered_users.clear()
        self.hints_used.clear()

        return self._show_question()

    # ----------------------------------------------------------
    def _show_question(self):
        word = self.questions[self.current_question]["word"]

        contents = [
            create_game_header("لعبة الأضداد"),
            create_progress_box(self.current_question + 1, self.total_questions),
            create_separator(),
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"ما هو عكس: {word}",
                        "size": "lg",
                        "color": COLORS['text_dark'],
                        "weight": "bold",
                        "wrap": True,
                        "align": "center"
                    }
                ],
                "margin": "lg"
            },
            create_separator(),
            *create_action_buttons()
        ]

        return FlexMessage(
            alt_text="لعبة الأضداد",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": contents,
                    "paddingAll": "20px",
                    "backgroundColor": COLORS["card_bg"]
                }
            })
        )

    # ----------------------------------------------------------

    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.answered_users.clear()
            self.hints_used.clear()
            return self._show_question()
        return None

    # ----------------------------------------------------------
    # Check Answer
    # ----------------------------------------------------------

    def check_answer(self, answer, user_id, display_name):
        if user_id in self.answered_users:
            return None

        answer = answer.strip()
        question = self.questions[self.current_question]
        correct_opposite = question["opposite"]

        # ------------------ تلميح ------------------
        if answer.lower() in ["لمح", "تلميح"]:
            if user_id not in self.hints_used:
                self.hints_used[user_id] = True
                return {
                    "response": TextMessage(
                        text=f"🔍 يبدأ بحرف: {correct_opposite[0]}\n📏 عدد الحروف: {len(correct_opposite)}"
                    ),
                    "points": 0,
                    "correct": False
                }
            return {
                "response": TextMessage(text="❗ لقد استخدمت التلميح مسبقًا"),
                "points": 0,
                "correct": False
            }

        # ------------------ طلب الحل ------------------
        if answer.lower() in ["جاوب", "الجواب", "الحل"]:
            self.answered_users.add(user_id)
            if self.current_question + 1 < self.total_questions:
                return {
                    "response": TextMessage(text=f"✔ الإجابة الصحيحة هي: {correct_opposite}"),
                    "points": 0,
                    "correct": False,
                    "next_question": True
                }
            return self._end_game()

        # ------------------ إجابة اللاعب ------------------
        if normalize_text(answer) == normalize_text(correct_opposite):
            self.answered_users.add(user_id)

            self.player_scores.setdefault(
                user_id, {"name": display_name, "score": 0}
            )
            self.player_scores[user_id]["score"] += 1

            if self.current_question + 1 < self.total_questions:
                return {
                    "response": TextMessage(
                        text=f"✔ إجابة صحيحة يا {display_name}!\n+1 نقطة 🎉"
                    ),
                    "points": 1,
                    "correct": True,
                    "won": True,
                    "next_question": True
                }

            return self._end_game()

        # ------------------ إجابة خاطئة ------------------
        return {
            "response": TextMessage(text="❌ إجابة غير صحيحة، حاول مرة أخرى"),
            "points": 0,
            "correct": False
        }

    # ----------------------------------------------------------
    # End Game
    # ----------------------------------------------------------

    def _end_game(self):
        if not self.player_scores:
            return {
                "response": TextMessage(text="انتهت اللعبة بدون أي نقاط 😅"),
                "points": 0,
                "correct": False,
                "game_over": True
            }

        sorted_players = sorted(
            self.player_scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )

        winner = sorted_players[0][1]

        winner_card = create_winner_card(winner, sorted_players, "الأضداد")

        return {
            "response": FlexMessage(
                alt_text="نتائج لعبة الأضداد",
                contents=FlexContainer.from_dict(winner_card)
            ),
            "correct": True,
            "won": True,
            "points": winner["score"],
            "game_over": True
        }
