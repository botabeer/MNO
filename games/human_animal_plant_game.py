from __future__ import annotations
from typing import Dict, Any, Optional, List
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
import time
import re

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


class HumanAnimalPlantGame:
    """
    لعبة: إنسان - حيوان - نبات - بلاد
    لكل جولة يُعطى حرف، يكتب اللاعب 4 كلمات (كل واحدة في سطر منفصل) تبدأ بالحرف.
    التحسينات:
    - Type hints + docstrings
    - تحقّق أقوى للكلمات العربية
    - منع التكرار (نفس اللاعب لا يجيب مرتين في نفس الجولة)
    - احتساب النقاط مع بونص عند اكتمال الأربعة صحيحة
    - tie-break باستخدام توقيت أول إجابة لكل لاعب
    - رسائل متناسقة باستخدام game_helpers
    """

    MIN_WORD_LENGTH = 2           # أقل طول لكلمة مقبول
    POINTS_PER_WORD = 3           # نقاط لكل كلمة صحيحة
    BONUS_COMPLETE = 5            # بونص عند كتابة 4 كلمات صحيحة كاملة
    TOTAL_QUESTIONS_DEFAULT = 5

    # بعض أمثلة ممكن نستخدمها للتلميح (محدودة — جيد كبداية)
    EXAMPLES = {
        "ا": ["أميرة", "أسد", "أرز", "أردن"],
        "ب": ["بدر", "بقرة", "بطيخ", "بغداد"],
        "ت": ["تيم", "تمساح", "تفاح", "تونس"],
        "م": ["محمد", "ماعز", "موز", "مصر"],
        "س": ["سعود", "سمكة", "سبانخ", "سوريا"],
        # يمكن توسيع هذهالخريطة لاحقًا بسهولة
    }

    LETTERS = [
        'أ', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض',
        'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي'
    ]

    def __init__(self, line_bot_api, total_questions: int = TOTAL_QUESTIONS_DEFAULT):
        self.line_bot_api = line_bot_api
        self.total_questions = max(1, int(total_questions))

        # state
        self.letters_pool: List[str] = self.LETTERS.copy()
        self.questions: List[str] = []
        self.current_question: int = 0
        self.player_scores: Dict[str, Dict[str, Any]] = {}
        self.answered_users: set[str] = set()  # لمنع الإجابة مرتين في نفس الجولة
        # لتسجيل وقت الإجابة الأولى لكل لاعب (tie-break)
        # player_scores[user_id]['first_answer_ts']

    # -------------------------
    # Start game
    # -------------------------
    def start_game(self) -> FlexMessage:
        """تهيئة اللعبة واختيار أحرف عشوائية للدوارات ثم عرض السؤال الأول."""
        # sample distinct letters
        self.questions = safe_sample(self.letters_pool, self.total_questions)
        if not self.questions:
            # fallback to random picks
            self.questions = [random.choice(self.LETTERS) for _ in range(self.total_questions)]

        self.current_question = 0
        self.player_scores.clear()
        self.answered_users.clear()

        return self._show_question()

    # -------------------------
    # UI: show question
    # -------------------------
    def _show_question(self) -> FlexMessage:
        letter = self.questions[self.current_question]

        contents = [
            create_game_header("إنسان - حيوان - نبات - بلاد"),
            create_progress_box(self.current_question + 1, self.total_questions),
            create_separator(),
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": letter,
                        "size": "5xl",
                        "color": COLORS["primary"],
                        "weight": "bold",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "اكتب 4 كلمات تبدأ بهذا الحرف (كل كلمة في سطر منفصل).",
                        "size": "sm",
                        "color": COLORS["text_dark"],
                        "align": "center",
                        "margin": "md",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": "مثال:\nاسم\nحيوان\nنبات\nبلد",
                        "size": "xs",
                        "color": COLORS["text_light"],
                        "align": "center",
                        "margin": "xs"
                    }
                ],
                "margin": "lg"
            },
            create_separator(),
            *create_action_buttons()
        ]

        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": contents,
                "backgroundColor": COLORS["card_bg"],
                "paddingAll": "20px"
            }
        }
        return FlexMessage(alt_text="إنسان حيوان نبات بلاد", contents=FlexContainer.from_dict(bubble))

    # -------------------------
    # Next question
    # -------------------------
    def next_question(self) -> Optional[FlexMessage]:
        """Called by GameManager to push next question (if available)."""
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.answered_users.clear()
            return self._show_question()
        return None

    # -------------------------
    # Check answer
    # -------------------------
    def check_answer(self, text: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        """
        معالجة إجابة اللاعب:
        - يقبل 4 كلمات في أسطر منفصلة.
        - يحتسب عدد الكلمات الصحيحة (تبدأ بالحرف المطلوب بعد التطبيع).
        - يمنع الإجابة المكررة في نفس الجولة.
        - يعطي نقاط ومؤشرات: next_question / game_over
        """
        if not text:
            return None

        if user_id in self.answered_users:
            return None  # منع الإرسال المتكرر في نفس الجولة

        letter = self.questions[self.current_question]

        # normalize command words
        text_strip = text.strip()
        tl = text_strip.lower()

        if tl in ("لمح", "تلميح"):
            # hint: give an example if exists or generic hint
            example_list = self.EXAMPLES.get(letter)
            if example_list:
                example = example_list[0]
                hint = create_hint_text(example)
            else:
                hint = f"يفضل أسماء مثل: {letter}اسم، {letter}حيوان، {letter}نبات، {letter}بلد"
            return {"response": TextMessage(text=hint), "points": 0, "correct": False}

        if tl in ("جاوب", "الجواب"):
            # reveal short samples (up to 3 best-effort)
            sample = self._sample_for_letter(letter)
            self.answered_users.add(user_id)
            if self.current_question + 1 < self.total_questions:
                return {"response": TextMessage(text=f"بعض الأمثلة:\n{sample}"), "points": 0, "correct": False, "next_question": True}
            return self._end_game()

        # split lines, accept \n or ; or , etc
        lines = re.split(r'[\r\n;،,]+', text_strip)
        # keep non-empty trimmed lines
        words = [ln.strip() for ln in lines if ln.strip()]
        if not words:
            return None

        # validate each of first 4 words
        needed = min(4, len(words))
        valid_count = 0
        cleaned_words_seen = set()
        now_ts = time.time()

        for i in range(needed):
            w = words[i]
            # remove punctuation and digits, keep Arabic letters and spaces
            cleaned = re.sub(r'[^أ-يءؤئئً-ْـ\s]', '', w).strip()
            if len(cleaned) < self.MIN_WORD_LENGTH:
                continue
            # normalize for comparison
            normalized = normalize_text(cleaned)
            if not normalized:
                continue
            # ensure starts with letter (consider ة/ه equivalence)
            first = normalized[0]
            expected = self._normalize_letter(letter)
            if self._letters_match(expected, first):
                # prevent duplicate same word submitted by same player in this submission
                if normalized in cleaned_words_seen:
                    continue
                cleaned_words_seen.add(normalized)
                valid_count += 1

        if valid_count == 0:
            # لا كلمات صحيحة → تجاهل
            return None

        # award points
        points = valid_count * self.POINTS_PER_WORD
        if valid_count >= 4:
            points += self.BONUS_COMPLETE

        # record player's score and earliest answer ts for tie-break
        if user_id not in self.player_scores:
            self.player_scores[user_id] = {"name": display_name, "score": points, "first_answer_ts": now_ts}
        else:
            self.player_scores[user_id]["score"] += points
            # keep earliest timestamp
            if self.player_scores[user_id].get("first_answer_ts", now_ts) > now_ts:
                self.player_scores[user_id]["first_answer_ts"] = now_ts

        self.answered_users.add(user_id)

        # prepare response
        if self.current_question + 1 < self.total_questions:
            return {
                "response": TextMessage(text=f"إجابة صحيحة {display_name} — الكلمات الصحيحة: {valid_count}/4\n+{points} نقطة"),
                "points": points,
                "correct": True,
                "won": valid_count >= 4,
                "next_question": True
            }

        return self._end_game()

    # -------------------------
    # End game
    # -------------------------
    def _end_game(self) -> Dict[str, Any]:
        """إنهاء اللعبة وإظهار بطاقة الفائزين."""
        if not self.player_scores:
            return {"response": TextMessage(text="انتهت اللعبة بدون فائز"), "points": 0, "correct": False, "won": False, "game_over": True}

        # sort by score desc, tie-break: earliest first_answer_ts wins
        sorted_players = sorted(
            self.player_scores.items(),
            key=lambda x: (x[1].get("score", 0), -x[1].get("first_answer_ts", 0)),
            reverse=True
        )

        winner = sorted_players[0][1]
        winner_card = create_winner_card(winner, sorted_players, replay_text="لعبه")

        return {
            "response": FlexMessage(alt_text="نتائج اللعبة", contents=FlexContainer.from_dict(winner_card)),
            "points": winner["score"],
            "correct": True,
            "won": True,
            "game_over": True
        }

    # -------------------------
    # Helpers
    # -------------------------
    def _normalize_letter(self, ch: str) -> str:
        """Normalize letter for comparison (treat ة == ه)."""
        if not ch:
            return ""
        c = ch.strip().lower()
        if c in ("ة", "ه"):
            return "ه"
        # normalize alef variants
        c = c.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
        return c

    def _letters_match(self, expected: str, actual_first: str) -> bool:
        """Compare letters with Arabic equivalences."""
        if not expected or not actual_first:
            return False
        e = self._normalize_letter(expected)[0]
        a = self._normalize_letter(actual_first)[0]
        return e == a

    def _sample_for_letter(self, letter: str) -> str:
        """Return up to 3 sample words for the given letter (best effort)."""
        examples = self.EXAMPLES.get(letter, [])
        if examples:
            return " - ".join(examples[:3])
        # fallback: construct simple placeholders
        return " - ".join([f"{letter}اسم", f"{letter}حيوان", f"{letter}نبات"])
