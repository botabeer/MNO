# human_animal_plant_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import COLORS
from games.game_helpers import (
    create_game_header, create_progress_box, create_separator,
    create_winner_card, normalize_text
)

class HumanAnimalPlantGame:
    def __init__(self, line_bot_api, total_questions=5):
        self.line_bot_api = line_bot_api
        self.letters = list("ابتثجحخدذرزسشصضطظعغفقكلمنهوي")
        self.questions = []
        self.current_question = 0
        self.total_questions = total_questions
        self.player_scores = {}
        self.answered = False
        self.registered = set()

        # أمثلة جاهزة
        self.examples = {
            "ا": ["احمد", "أرنب", "أقحوان", "أمريكا"],
            "ب": ["بشير", "بقرة", "برتقال", "بريطانيا"],
            "م": ["ماجد", "ماعز", "منجا", "مصر"],
            "س": ["سليم", "سحلية", "سمسم", "سوريا"],
            "ك": ["كريم", "كلب", "كادي", "كندا"],
            "ن": ["نواف", "نمر", "نعناع", "نرويج"],
        }

    # ---------------------------------------
    def register_player(self, uid, name):
        self.registered.add(uid)

    # ---------------------------------------
    def start_game(self):
        self.questions = random.sample(self.letters, min(self.total_questions, len(self.letters)))
        self.current_question = 0
        self.player_scores = {}
        self.answered = False
        return self._show_question()

    # ---------------------------------------
    def _show_question(self):
        self.answered = False
        letter = self.questions[self.current_question]

        contents = [
            create_game_header("إنسان - حيوان - نبات - بلاد (سريع)"),
            create_progress_box(self.current_question + 1, self.total_questions),
            create_separator(),
            {
                "type":"box","layout":"vertical","contents":[
                    {"type":"text","text":letter,"size":"5xl",
                     "color":COLORS['primary'],"weight":"bold","align":"center"},
                    {"type":"text",
                     "text":"اكتب 4 كلمات تبدأ بهذا الحرف (إنسان • حيوان • نبات • بلاد)",
                     "size":"sm","color":COLORS['text_dark'],
                     "margin":"md","wrap":True,"align":"center"}
                ],
                "margin":"lg"
            },
            create_separator(),
            {
                "type": "box",
                "layout": "horizontal",
                "spacing": "md",
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
                        "height": "sm",
                        "color": COLORS['warning']
                    }
                ]
            }
        ]

        return FlexMessage(
            alt_text="إنسان حيوان نبات بلاد",
            contents=FlexContainer.from_dict({
                "type":"bubble",
                "body":{
                    "type":"box","layout":"vertical","spacing":"md",
                    "contents":contents,
                    "backgroundColor":COLORS['card_bg'],
                    "paddingAll":"18px"
                }
            })
        )

    # ---------------------------------------
    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            return self._show_question()
        return self._end_game()

    # ---------------------------------------
    def check_answer(self, text, user_id, display_name):
        if user_id not in self.registered:
            return None

        text = text.strip().lower()
        letter = self.questions[self.current_question]

        # =========================
        # 👈 1) لمّـــح
        # =========================
        if text in ["لمح", "تلميح"]:
            hint = (
                f"🔍 **تلميح:**\n"
                f"• يبدأ بحرف: {letter}\n"
                f"• إنسان: {letter}... (5-3 حروف)\n"
                f"• حيوان: {letter}... (4-3 حروف)\n"
                f"• نبات: {letter}... (5-3 حروف)\n"
                f"• بلاد: {letter}... (6-3 حروف)\n"
            )
            return {
                "response": TextMessage(text=hint),
                "correct": False,
                "points": 0
            }

        # =========================
        # 👈 2) جاوب (يعطي الإجابة الصحيحة)
        # =========================
        if text in ["جاوب", "الجواب", "الحل"]:
            example = self.examples.get(letter, ["اسم", "حيوان", "نبات", "بلاد"])
            msg = (
                f"📌 **الإجابة الصحيحة:**\n"
                f"إنسان: {example[0]}\n"
                f"حيوان: {example[1]}\n"
                f"Nبات: {example[2]}\n"
                f"بلاد: {example[3]}"
            )
            return {
                "response": TextMessage(text=msg),
                "correct": False,
                "points": 0
            }

        # =========================
        # 👈 3) الإجابة السريعة (أول شخص فقط)
        # =========================
        if self.answered:
            return None  # السؤال مقفل بعد أول إجابة صحيحة

        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if len(lines) < 4:
            return None

        valid = sum(
            1 for w in lines[:4]
            if normalize_text(w).startswith(normalize_text(letter))
        )

        if valid >= 1:
            self.answered = True

            points = valid * 3
            self.player_scores.setdefault(user_id, {"name": display_name, "score": 0})
            self.player_scores[user_id]["score"] += points

            msg = (
                f"🎉 أسرع إجابة صحيحة!\n"
                f"{display_name}\n"
                f"الكلمات الصحيحة: {valid}/4\n"
                f"+{points} نقطة"
            )

            return {
                "response": TextMessage(text=msg),
                "correct": True,
                "points": points,
                "next_question": True
            }

        return None

    # ---------------------------------------
    def _end_game(self):
        if not self.player_scores:
            return {"response": TextMessage(text="انتهت اللعبة."), "game_over": True}

        players = sorted(self.player_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        winner = players[0][1]

        return {
            "response": FlexMessage(
                alt_text="نتائج اللعبة",
                contents=FlexContainer.from_dict(
                    create_winner_card(winner, players, "إنسان - حيوان - نبات - بلاد")
                )
            ),
            "game_over": True
        }
