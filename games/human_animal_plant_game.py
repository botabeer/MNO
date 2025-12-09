# games/human_animal_plant_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import THEMES
from games.game_helpers import create_game_header, create_progress_box, create_separator, create_winner_card, normalize_text
from database import Database

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
        self.examples = {
            "ا": ["احمد", "ارنب", "اقحوان", "امريكا"],
            "ب": ["بشير", "بقرة", "برتقال", "بريطانيا"],
            "م": ["ماجد", "ماعز", "منجا", "مصر"],
            "س": ["سليم", "سحلية", "سمسم", "سوريا"],
            "ك": ["كريم", "كلب", "كادي", "كندا"],
            "ن": ["نواف", "نمر", "نعناع", "نرويج"]
        }

    def register_player(self, uid, name):
        self.registered.add(uid)

    def start_game(self):
        self.questions = random.sample(self.letters, min(self.total_questions, len(self.letters)))
        self.current_question = 0
        self.player_scores = {}
        self.answered = False
        return self._show_question()

    def _show_question(self, theme="light"):
        colors = THEMES.get(theme, THEMES["light"])
        self.answered = False
        letter = self.questions[self.current_question]

        contents = [
            create_game_header("انسان - حيوان - نبات - بلاد سريع", theme=theme),
            create_progress_box(self.current_question + 1, self.total_questions, theme=theme),
            create_separator(theme=theme),
            {
                "type":"box","layout":"vertical","contents":[
                    {"type":"text","text":letter,"size":"5xl","color":colors['primary'],"weight":"bold","align":"center"},
                    {"type":"text","text":"اكتب 4 كلمات تبدأ بهذا الحرف انسان حيوان نبات بلاد","size":"sm","color":colors['text_dark'],"margin":"md","wrap":True,"align":"center"}
                ],
                "margin":"lg"
            },
            create_separator(theme=theme),
            {
                "type": "box",
                "layout": "horizontal",
                "spacing": "md",
                "contents": [
                    {"type": "button","action": {"type": "message", "label": "لمح", "text": "لمح"},"style": "secondary","height": "sm"},
                    {"type": "button","action": {"type": "message", "label": "جاوب", "text": "جاوب"},"style": "secondary","height": "sm","color": colors['warning']}
                ]
            }
        ]

        return FlexMessage(
            alt_text="انسان حيوان نبات بلاد",
            contents=FlexContainer.from_dict({
                "type":"bubble",
                "body":{
                    "type":"box","layout":"vertical","spacing":"md",
                    "contents":contents,
                    "backgroundColor":colors['card_bg'],
                    "paddingAll":"18px"
                }
            })
        )

    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            return self._show_question()
        return None

    def check_answer(self, text, user_id, display_name):
        if user_id not in self.registered:
            return None

        text = text.strip().lower()
        letter = self.questions[self.current_question]
        theme = Database.get_user_theme(user_id)

        if text in ["لمح", "تلميح"]:
            hint = f"تلميح:\nيبدأ بحرف: {letter}\nانسان: {letter}... 5-3 حروف\nحيوان: {letter}... 4-3 حروف\nنبات: {letter}... 5-3 حروف\nبلاد: {letter}... 6-3 حروف"
            return {"response": TextMessage(text=hint), "correct": False, "points": 0}

        if text in ["جاوب", "الجواب", "الحل"]:
            example = self.examples.get(letter, ["اسم", "حيوان", "نبات", "بلاد"])
            msg = f"الاجابة الصحيحة:\nانسان: {example[0]}\nحيوان: {example[1]}\nنبات: {example[2]}\nبلاد: {example[3]}"
            return {"response": TextMessage(text=msg), "correct": False, "points": 0}

        if self.answered:
            return None

        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if len(lines) < 4:
            return None

        valid = sum(1 for w in lines[:4] if normalize_text(w).startswith(normalize_text(letter)))

        if valid >= 1:
            self.answered = True
            points = valid * 3
            self.player_scores.setdefault(user_id, {"name": display_name, "score": 0})
            self.player_scores[user_id]["score"] += points

            msg = f"اسرع اجابة صحيحة\n{display_name}\nالكلمات الصحيحة: {valid}/4\n+{points} نقطة"

            if self.current_question + 1 < self.total_questions:
                return {"response": TextMessage(text=msg), "correct": True, "points": points, "next_question": True}
            return self._end_game(user_id)

        return None

    def _end_game(self, user_id):
        theme = Database.get_user_theme(user_id)
        if not self.player_scores:
            return {"response": TextMessage(text="انتهت اللعبة"), "game_over": True}

        players = sorted(self.player_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        winner = players[0][1]

        return {
            "response": FlexMessage(
                alt_text="نتائج اللعبة",
                contents=FlexContainer.from_dict(create_winner_card(winner, players, "انسان - حيوان - نبات - بلاد", theme=theme))
            ),
            "game_over": True
        }
