# games/opposite_game.py
import random
from linebot.v3.messaging import FlexMessage, FlexContainer, TextMessage
from constants import COLORS
from games.game_helpers import (
    normalize_text,
    create_game_header,
    create_progress_box,
    create_separator,
    create_action_buttons,
    create_winner_card,
    create_hint_text
)


class OppositeGame:
    def __init__(self, line_bot_api, total_questions=5, **kwargs):
        self.line_bot_api = line_bot_api
        self.total_questions = total_questions

        self.all_words = [
            {"word": "كبير", "opposite": "صغير"},
            {"word": "طويل", "opposite": "قصير"},
            {"word": "سريع", "opposite": "بطيء"},
            {"word": "ساخن", "opposite": "بارد"},
        ]

        self.questions = []
        self.current_question = 0

        self.player_scores = {}
        self.answered_users = set()
        self.hints_used = {}
        self.registered = set()

    # -----------------------------------------
    def register_player(self, uid, name):
        self.registered.add(uid)

    # -----------------------------------------
    def start_game(self):
        self.questions = random.sample(
            self.all_words, min(self.total_questions, len(self.all_words))
        )
        self.current_question = 0
        self.player_scores.clear()
        self.answered_users.clear()
        self.hints_used.clear()

        return self._build_question_flex()

    # -----------------------------------------
    def _build_question_flex(self):
        q = self.questions[self.current_question]

        body = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "backgroundColor": COLORS["card_bg"],
                "paddingAll": "18px",
                "contents": [
                    create_game_header("لعبة الأضداد"),
                    create_progress_box(self.current_question + 1, self.total_questions),
                    create_separator(),
                    {
                        "type": "text",
                        "text": f"ما هو عكس: {q['word']}",
                        "size": "lg",
                        "weight": "bold",
                        "align": "center",
                        "color": COLORS["text_dark"],
                        "margin": "lg",
                        "wrap": True
                    },
                    create_separator(),
                    *create_action_buttons()
                ]
            }
        }

        return FlexMessage(
            alt_text="لعبة الأضداد",
            contents=FlexContainer.from_dict(body)
        )

    # -----------------------------------------
    def next_question(self):
        self.current_question += 1

        if self.current_question < self.total_questions:
            self.answered_users.clear()
            self.hints_used.clear()
            return self._build_question_flex()

        return self._end_game()

    # -----------------------------------------
    def _build_text_flex(self, text, color=None):
        """إنشاء رسالة فليكس نصية بسيطة بشكل موحد."""
        body = {
            "type": "bubble",
            "body": {
                "type": "box",
                "paddingAll": "16px",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": text,
                    "wrap": True,
                    "color": color if color else COLORS["text_dark"]
                }]
            }
        }
        return FlexMessage(alt_text=text, contents=FlexContainer.from_dict(body))

    # -----------------------------------------
    def check_answer(self, answer, user_id, display_name):
        if user_id not in self.registered:
            return None

        # منع تكرار الإجابة
        if user_id in self.answered_users:
            return None

        q = self.questions[self.current_question]
        ans = normalize_text(answer)

        # ------------------ التلميح ------------------
        if ans in ["لمح", "تلميح"]:
            if user_id not in self.hints_used:
                self.hints_used[user_id] = True
                hint = create_hint_text(q["opposite"])
                return {
                    "response": self._build_text_flex(hint, COLORS["primary"]),
                    "correct": False
                }
            return {
                "response": self._build_text_flex("استخدمت التلميح بالفعل", COLORS["warning"]),
                "correct": False
            }

        # ------------------ طلب الجواب ------------------
        if ans in ["جاوب", "الحل", "الجواب"]:
            self.answered_users.add(user_id)

            if self.current_question + 1 < self.total_questions:
                return {
                    "response": self._build_text_flex(f"الإجابة: {q['opposite']}"),
                    "next_question": True
                }

            return self._end_game()

        # ------------------ إجابة صحيحة ------------------
        if ans == normalize_text(q["opposite"]):
            self.answered_users.add(user_id)

            self.player_scores.setdefault(user_id, {"name": display_name, "score": 0})
            self.player_scores[user_id]["score"] += 1

            if self.current_question + 1 < self.total_questions:
                return {
                    "response": self._build_text_flex(
                        f"إجابة صحيحة يا {display_name}!\n+1 نقطة",
                        COLORS["success"]
                    ),
                    "next_question": True
                }

            return self._end_game()

        # ------------------ إجابة خاطئة ------------------
        return None

    # -----------------------------------------
    def _end_game(self):
        if not self.player_scores:
            return {
                "response": self._build_text_flex("انتهت اللعبة"),
                "game_over": True
            }

        sorted_players = sorted(
            self.player_scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        winner = sorted_players[0][1]

        winner_card = create_winner_card(winner, sorted_players, "لعبة الأضداد")

        return {
            "response": FlexMessage(
                alt_text="نتائج اللعبة",
                contents=FlexContainer.from_dict(winner_card)
            ),
            "game_over": True,
            "winner": winner,
            "all_players": sorted_players
        }
