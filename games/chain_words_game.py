from __future__ import annotations
from typing import Dict, Any, Optional, List, Tuple
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
import time

from constants import COLORS
from games.game_helpers import (
    normalize_text,
    create_game_header,
    create_progress_box,
    create_separator,
    create_action_buttons,
    create_winner_card,
    safe_sample,
    create_hint_text,
)


class ChainWordsGame:
    """
    لعبة سلسلة الكلمات (Chain Words).
    قواعد مبسطة:
    - يبدأ البوت بكلمة عشوائية من start_words.
    - يكتب اللاعب كلمة تبدأ بنفس حرف الكلمة الحالية (مع معالجة ة/ه وتهجي عربي).
    - كل إجابة صحيحة تمنح 1 نقطة.
    - يمنع تكرار الكلمات (بالمقارنة بعد التطبيع normalize_text).
    - تُجرى مجموع "max_rounds" جولات، ثم تُعرض النتائج.
    - يوجد أمر تلميح ('لمح'/'تلميح') وأمر عرض مثال ('جاوب'/'الجواب').
    """

    DEFAULT_START_WORDS = [
        "قلم", "كتاب", "مدرسة", "باب", "نافذة", "طاولة", "كرسي", "حديقة", "شجرة", "زهرة",
        "سماء", "بحر", "جبل", "نهر", "وادي", "صحراء", "غابة", "حقل", "مزرعة", "قرية"
    ]

    def __init__(self, line_bot_api, max_rounds: int = 5):
        self.line_bot_api = line_bot_api

        # game data
        self.start_words: List[str] = self.DEFAULT_START_WORDS.copy()
        self.current_word: Optional[str] = None
        self.used_words: set[str] = set()  # normalized words set
        self.round_count: int = 0
        self.max_rounds: int = max(1, int(max_rounds))

        # scoring & anti-cheat
        # player_scores: { user_id: {"name": str, "score": int, "first_answer_ts": float} }
        self.player_scores: Dict[str, Dict[str, Any]] = {}
        self.answered_users: set[str] = set()

    # ------------------------
    # Start / UI
    # ------------------------
    def start_game(self) -> FlexMessage:
        """Initialize game state and show the first word."""
        # pick a start word safely
        choices = safe_sample(self.start_words, 1)
        self.current_word = choices[0] if choices else random.choice(self.start_words)
        self.used_words = {normalize_text(self.current_word)}
        self.round_count = 0
        self.player_scores.clear()
        self.answered_users.clear()
        return self._show_question()

    def _show_question(self) -> FlexMessage:
        """Return FlexMessage showing the current word and instructions."""
        if not self.current_word:
            # fallback if something went wrong
            self.current_word = random.choice(self.start_words)

        last_letter = self._get_effective_last_letter(self.current_word)

        contents = [
            create_game_header("سلسلة الكلمات"),
            create_progress_box(self.round_count + 1, self.max_rounds),
            create_separator(),
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"الكلمة الحالية: {self.current_word}",
                        "size": "xxl",
                        "color": COLORS["primary"],
                        "weight": "bold",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": f"اكتب كلمة تبدأ بحرف: {last_letter}",
                        "size": "md",
                        "color": COLORS["text_dark"],
                        "wrap": True,
                        "margin": "md",
                        "align": "center"
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
        return FlexMessage(alt_text="سلسلة الكلمات", contents=FlexContainer.from_dict(bubble))

    # ------------------------
    # Next question (GameManager will call this to push)
    # ------------------------
    def next_question(self) -> Optional[FlexMessage]:
        """
        If there are remaining rounds, return next question UI.
        Note: round_count is incremented when a correct answer is accepted.
        """
        if self.round_count < self.max_rounds:
            self.answered_users.clear()
            # If we already reached max_rounds, end game
            if self.round_count >= self.max_rounds:
                return None
            return self._show_question()
        return None

    # ------------------------
    # Answer checking
    # ------------------------
    def check_answer(self, raw_text: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        """
        Process a user's message:
        - handle commands: hint/reveal
        - validate the word: starts with required letter and not used
        - award points and advance round if correct
        Returns a dict with keys similar to other games:
        {'response': MessageObject, 'points': int, 'correct': bool, 'won': bool, 'next_question': bool, 'game_over': bool}
        or None to indicate ignore/no-action.
        """
        text = (raw_text or "").strip()
        if not text:
            return None

        # ignore duplicated attempts in same round by same user
        if user_id in self.answered_users:
            return None

        text_lower = text.lower()

        # handle hint
        if text_lower in ("لمح", "تلميح"):
            example = self._example_for_current_letter()
            hint_text = create_hint_text(example) if example else "لا يوجد مثال متاح الآن"
            return {"response": TextMessage(text=hint_text), "points": 0, "correct": False}

        # handle reveal / give sample answers
        if text_lower in ("جاوب", "الجواب"):
            sample = self._sample_answers_for_current()  # returns string
            self.answered_users.add(user_id)
            if self.round_count + 1 < self.max_rounds:
                return {"response": TextMessage(text=sample), "points": 0, "correct": False, "next_question": True}
            return self._end_game()

        # validate normal word answer
        if not self.current_word:
            return None

        # Normalize comparison
        normalized_answer = normalize_text(text)
        if not normalized_answer:
            return None

        # check reuse
        if normalized_answer in self.used_words:
            return {"response": TextMessage(text="هذه الكلمة استُخدمت من قبل—جرّب كلمة أخرى"), "points": 0, "correct": False}

        # expected starting letter (effective)
        expected = self._get_effective_last_letter(self.current_word)
        # take first letter of answer (effective)
        first_letter = self._get_effective_first_letter(text)

        if not first_letter:
            return {"response": TextMessage(text=f"اكتب كلمة صحيحة تبدأ بحرف: {expected}"), "points": 0, "correct": False}

        # Accept if first letter matches expected (consider ة/ه equivalence)
        if self._letters_match(expected, first_letter):
            # mark as used
            self.used_words.add(normalized_answer)

            # award point & record timestamp for tie-break
            ts = time.time()
            self.player_scores.setdefault(user_id, {"name": display_name, "score": 0, "first_answer_ts": ts})
            # increment score
            self.player_scores[user_id]["score"] += 1
            # keep earliest timestamp (who answered earlier gets advantage in tie)
            if self.player_scores[user_id].get("first_answer_ts", 0) > ts:
                self.player_scores[user_id]["first_answer_ts"] = ts

            # update state
            self.current_word = text  # keep original text for display
            self.round_count += 1
            self.answered_users.add(user_id)

            # if more rounds remain, return quick success and signal next_question
            if self.round_count < self.max_rounds:
                return {
                    "response": TextMessage(text=f"إجابة صحيحة {display_name} 🎉\n+1 نقطة"),
                    "points": 1,
                    "correct": True,
                    "won": True,
                    "next_question": True
                }

            # last round done → end game
            return self._end_game()

        # otherwise wrong starting letter
        return {"response": TextMessage(text=f"يجب أن تبدأ الكلمة بحرف: {expected}"), "points": 0, "correct": False}

    # ------------------------
    # End game
    # ------------------------
    def _end_game(self) -> Dict[str, Any]:
        """Compose final results and winner card."""
        if not self.player_scores:
            return {"response": TextMessage(text="انتهت اللعبة بدون فائز"), "points": 0, "correct": False, "won": False, "game_over": True}

        # sort by score desc, tie-break: smaller first_answer_ts (earlier answers win)
        sorted_players = sorted(
            self.player_scores.items(),
            key=lambda x: (x[1].get("score", 0), -x[1].get("first_answer_ts", 0)),
            reverse=True
        )

        winner = sorted_players[0][1]

        winner_card = create_winner_card(winner, sorted_players, replay_text="سلسله")

        return {
            "response": FlexMessage(alt_text="نتائج اللعبة", contents=FlexContainer.from_dict(winner_card)),
            "points": winner["score"],
            "correct": True,
            "won": True,
            "game_over": True
        }

    # ------------------------
    # Helpers for letters & examples
    # ------------------------
    def _get_effective_last_letter(self, word: str) -> str:
        """Return a normalized 'last letter' to compare (treat 'ة' and 'ه' same)."""
        if not word:
            return ""
        w = word.strip()
        last = w[-1]
        if last in ("ة", "ه"):
            return "ه"
        return last

    def _get_effective_first_letter(self, word: str) -> str:
        """Return first letter of user's answer in normalized form or '' if invalid."""
        if not word:
            return ""
        w = word.strip()
        first = w[0].lower()
        if first in ("ة", "ه"):
            return "ه"
        return first

    def _letters_match(self, expected: str, actual: str) -> bool:
        """Compare letters with special Arabic equivalences."""
        if not expected or not actual:
            return False
        # Normalize hamzas/aleph differences for basic matching
        # use normalize_text to remove diacritics, but keep single letter comparisons simple
        exp_norm = normalize_text(expected)
        act_norm = normalize_text(actual)
        if not exp_norm or not act_norm:
            return False
        # if either maps to 'ه' treat as equal
        if exp_norm[0] == "ه" and act_norm[0] == "ه":
            return True
        return exp_norm[0] == act_norm[0]

    def _example_for_current_letter(self) -> Optional[str]:
        """Return one example word that starts with the expected letter (if possible)."""
        if not self.current_word:
            return None
        expected = self._get_effective_last_letter(self.current_word)
        # search defaults for a word starting with expected
        for w in self.start_words + list(self.used_words):
            if not w:
                continue
            # use raw check on original words first
            if normalize_text(w).startswith(normalize_text(expected)):
                return w
        # fallback: try to build simple example by prefixing letter with vowel-like char
        return expected + "ـ"  # visual fallback

    def _sample_answers_for_current(self) -> str:
        """Return a short string with sample answers (best-effort) for reveal command."""
        # try to generate small sample from used_words or start_words
        expected = self._get_effective_last_letter(self.current_word) if self.current_word else ""
        candidates: List[str] = []
        for w in self.start_words:
            if normalize_text(w).startswith(normalize_text(expected)):
                candidates.append(w)
        # return up to 3 distinct examples
        if not candidates:
            return "لا توجد أمثلة متاحة."
        return "بعض الأمثلة: " + " - ".join(candidates[:3])
