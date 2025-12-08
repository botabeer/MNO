# games/opposite_game.py
import random
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

    # ---------------------------------------------------
    # تسجيل اللاعبين
    # ---------------------------------------------------
    def register_player(self, uid, name):
        self.registered.add(uid)

    # ---------------------------------------------------
    # بدء اللعبة
    # ---------------------------------------------------
    def start_game(self):
        self.questions = random.sample(
            self.all_words,
            min(self.total_questions, len(self.all_words))
        )
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        self.hints_used = {}

        return self._build_question_card()

    # ---------------------------------------------------
    # إنشاء بطاقة السؤال
    # ---------------------------------------------------
    def _build_question_card(self):
        q = self.questions[self.current_question]

        card = {
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
                        "color": COLORS["text_dark"],
                        "align": "center",
                        "wrap": True,
                        "margin": "lg"
                    },
                    create_separator(),
                    *create_action_buttons()
                ]
            }
        }

        return card

    # ---------------------------------------------------
    # السؤال التالي
    # ---------------------------------------------------
    def next_question(self):
        self.current_question += 1

        if self.current_question < self.total_questions:
            self.answered_users = set()
            self.hints_used = {}
            return self._build_question_card()

        return self._end_game()

    # ---------------------------------------------------
    # فحص الإجابة
    # ---------------------------------------------------
    def check_answer(self, answer, user_id, display_name):
        if user_id not in self.registered:
            # تجاهل المستخدمين غير المسجلين
            return None

        if user_id in self.answered_users:
            return None

        q = self.questions[self.current_question]
        ans = normalize_text(answer)

        # ---------------- تلميح ----------------
        if ans in ["لمح", "تلميح"]:
            if user_id not in self.hints_used:
                self.hints_used[user_id] = True
                hint = create_hint_text(q["opposite"])
                return {
                    "response": {
                        "type": "bubble",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "paddingAll": "16px",
                            "contents": [{
                                "type": "text",
                                "text": hint,
                                "color": COLORS["primary"],
                                "wrap": True
                            }]
                        }
                    },
                    "correct": False
                }
            return {
                "response": {
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "paddingAll": "16px",
                        "contents": [{
                            "type": "text",
                            "text": "استخدمت التلميح بالفعل",
                            "color": COLORS["warning"],
                            "wrap": True
                        }]
                    }
                },
                "correct": False
            }

        # ---------------- طلب الجواب ----------------
        if ans in ["جاوب", "الجواب", "الحل"]:
            self.answered_users.add(user_id)

            if self.current_question + 1 < self.total_questions:
                return {
                    "response": {
                        "type": "bubble",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "paddingAll": "16px",
                            "contents": [{
                                "type": "text",
                                "text": f"الإجابة: {q['opposite']}",
                                "wrap": True
                            }]
                        }
                    },
                    "next_question": True
                }
            return self._end_game()

        # ---------------- إجابة صحيحة ----------------
        if ans == normalize_text(q["opposite"]):
            self.answered_users.add(user_id)

            self.player_scores.setdefault(user_id, {"name": display_name, "score": 0})
            self.player_scores[user_id]["score"] += 1

            if self.current_question + 1 < self.total_questions:
                return {
                    "response": {
                        "type": "bubble",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "paddingAll": "16px",
                            "contents": [{
                                "type": "text",
                                "text": f"إجابة صحيحة يا {display_name}!\n+1 نقطة",
                                "color": COLORS["success"],
                                "wrap": True
                            }]
                        }
                    },
                    "next_question": True
                }

            return self._end_game()

        # ---------------- إجابة خاطئة ----------------
        return None

    # ---------------------------------------------------
    # نهاية اللعبة
    # ---------------------------------------------------
    def _end_game(self):
        if not self.player_scores:
            return {
                "response": {
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "paddingAll": "16px",
                        "contents": [{
                            "type": "text",
                            "text": "انتهت اللعبة",
                            "wrap": True
                        }]
                    }
                },
                "game_over": True
            }

        sorted_players = sorted(
            self.player_scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )

        winner = sorted_players[0][1]

        card = create_winner_card(winner, sorted_players, "لعبة الأضداد")

        return {
            "response": card,
            "game_over": True,
            "winner": winner,
            "all_players": sorted_players,
            "game_name": "لعبة الأضداد"
        }
