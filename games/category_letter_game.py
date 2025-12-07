from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random

from constants import COLORS
from games.game_helpers import (
    normalize_text,
    create_game_header,
    create_progress_box,
    create_separator,
    create_action_buttons,
    create_winner_card,
    safe_sample,
    create_hint_text
)


class CategoryLetterGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api

        # كل الفئات + الحرف + الإجابات النموذجية
        self.challenges = [
            {"category": "المطبخ", "letter": "ق", "answers": ["قدر", "قلايه", "قهوه", "قنينه", "قباقيب"]},
            {"category": "حيوان", "letter": "ب", "answers": ["بطه", "بقره", "ببغاء", "بومه", "بعير"]},
            {"category": "فاكهه", "letter": "ت", "answers": ["تفاح", "توت", "تمر", "تين", "ترنج"]},
            {"category": "خضار", "letter": "ب", "answers": ["بصل", "بطاطس", "باذنجان", "بقدونس", "بروكلي"]},
            {"category": "بلاد", "letter": "س", "answers": ["سعوديه", "سوريا", "سودان", "سويسرا", "سويد"]},
            {"category": "اسم ولد", "letter": "م", "answers": ["محمد", "مصطفى", "مالك", "ماجد", "معاذ"]},
            {"category": "اسم بنت", "letter": "ر", "answers": ["ريم", "رنا", "رهف", "رغد", "رزان"]},
            {"category": "مهنه", "letter": "ط", "answers": ["طبيب", "طباخ", "طيار", "طالب", "طحان"]},
            {"category": "رياضه", "letter": "ك", "answers": ["كره", "كاراتيه", "كريكت", "كرلنج", "كرة سلة"]},
            {"category": "لون", "letter": "ا", "answers": ["احمر", "ازرق", "اخضر", "اصفر", "ابيض"]},
            {"category": "حيوان", "letter": "ف", "answers": ["فيل", "فار", "فهد", "فراشه", "فقمه"]},
            {"category": "نبات", "letter": "ن", "answers": ["نخل", "نعناع", "نرجس", "نارجيل", "نبق"]},
            {"category": "مدينه", "letter": "ج", "answers": ["جده", "جيزان", "جنيف", "جاكرتا", "جدة"]},
            {"category": "اكل", "letter": "ك", "answers": ["كبسه", "كفته", "كيك", "كريمه", "كشري"]},
            {"category": "شرب", "letter": "ع", "answers": ["عصير", "عرق سوس", "عرن", "عيران", "عسل"]}
        ]

        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.answered_users = set()

    # -------------------------------------------------------
    # بدء اللعبة
    # -------------------------------------------------------
    def start_game(self):
        self.questions = safe_sample(self.challenges, self.total_questions)
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        return self._show_question()

    # -------------------------------------------------------
    # عرض السؤال الحالي
    # -------------------------------------------------------
    def _show_question(self):
        c = self.questions[self.current_question]

        contents = [
            create_game_header("فئة وحرف"),
            create_progress_box(self.current_question + 1, self.total_questions),
            create_separator(),

            # السؤال نفسه
            {
                "type": "box",
                "layout": "vertical",
                "margin": "lg",
                "contents": [
                    {
                        "type": "text",
                        "text": f"الفئة: {c['category']}",
                        "size": "lg",
                        "color": COLORS["text_dark"],
                        "align": "center",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": f"الحرف: {c['letter']}",
                        "size": "xxl",
                        "color": COLORS["primary"],
                        "align": "center",
                        "weight": "bold",
                        "margin": "md"
                    }
                ]
            },

            create_separator(),
            *create_action_buttons()
        ]

        return FlexMessage(
            alt_text="فئة وحرف",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "paddingAll": "20px",
                    "backgroundColor": COLORS["card_bg"],
                    "contents": contents
                }
            })
        )

    # -------------------------------------------------------
    # سؤال جديد
    # -------------------------------------------------------
    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.answered_users = set()
            return self._show_question()
        return None

    # -------------------------------------------------------
    # التحقق من الإجابة
    # -------------------------------------------------------
    def check_answer(self, text, user_id, display_name):
        if user_id in self.answered_users:
            return None

        c = self.questions[self.current_question]
        text_original = text.strip()
        text_lower = text_original.lower()

        # ---- طلب تلميح ----
        if text_lower in ["لمح", "تلميح"]:
            hint = create_hint_text(c["answers"][0])
            return {"response": TextMessage(text=hint), "points": 0, "correct": False}

        # ---- طلب الحل ----
        if text_lower in ["جاوب", "الحل"]:
            sample = " - ".join(c["answers"][:3])
            self.answered_users.add(user_id)

            if self.current_question + 1 < self.total_questions:
                return {
                    "response": TextMessage(text=f"بعض الإجابات الصحيحة:\n{sample}"),
                    "points": 0,
                    "correct": False,
                    "next_question": True
                }

            return self._end_game()

        # ---- إجابة اللاعب ----
        normalized = normalize_text(text_original)
        valid = [normalize_text(a) for a in c["answers"]]

        if normalized in valid:
            # تسجيل النقاط
            self.player_scores.setdefault(user_id, {"name": display_name, "score": 0})
            self.player_scores[user_id]["score"] += 1
            self.answered_users.add(user_id)

            if self.current_question + 1 < self.total_questions:
                return {
                    "response": TextMessage(text=f"إجابة صحيحة {display_name} 🎉\n+1 نقطة"),
                    "points": 1,
                    "correct": True,
                    "won": True,
                    "next_question": True,
                }

            return self._end_game()

        # إجابة خاطئة → تجاهل
        return None

    # -------------------------------------------------------
    # نهاية اللعبة
    # -------------------------------------------------------
    def _end_game(self):
        if not self.player_scores:
            return {
                "response": TextMessage(text="انتهت اللعبة بدون فائز"),
                "points": 0,
                "correct": False,
                "won": False,
                "game_over": True
            }

        # فرز اللاعبين (score desc)
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        winner = sorted_players[0][1]

        winner_card = create_winner_card(
            winner,
            sorted_players,
            replay_text="فئة",
        )

        return {
            "response": FlexMessage(
                alt_text="نتائج اللعبة",
                contents=FlexContainer.from_dict(winner_card)
            ),
            "points": winner["score"],
            "correct": True,
            "won": True,
            "game_over": True
        }
