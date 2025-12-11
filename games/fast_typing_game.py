"""
لعبة أسرع - Bot Mesh v20.1 FINAL
Created by: Abeer Aldosari © 2025
✅ نقطة واحدة لكل إجابة | ثيمات | سؤال سابق | أزرار | مع وقت 20 ثانية
"""

from games.base_game import BaseGame
import random
import time
from typing import Dict, Any, Optional


class FastTypingGame(BaseGame):
    """لعبة أسرع - الوحيدة مع وقت"""

    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "أسرع"
        self.supports_hint = False
        self.supports_reveal = False

        self.round_time = 20
        self.round_start_time = None

        self.phrases = [
            "سبحان الله", "الحمد لله", "الله أكبر", "لا إله إلا الله",
            "رب اغفر لي", "توكل على الله", "الصبر مفتاح الفرج", "من جد وجد",
            "العلم نور", "راحة القلب في الذكر", "اللهم اهدنا", "كن محسنا",
            "الدال على الخير كفاعله", "رب زدني علما", "اتق الله", "خير الأمور أوسطها",
            "اللهم اشف مرضانا", "التواضع رفعة", "الصدق منجاة", "الصمت حكمة",
            "اللهم ارزقني رضاك", "النية الصالحة بركة", "استغفر الله العظيم", "من صبر ظفر",
            "العمل عبادة", "القناعة كنز", "اللهم يسر أموري", "الرحمة قوة",
            "لا تحقرن من المعروف شيئا", "الصلاة نور", "الدعاء سلاح المؤمن", "العفو عند المقدرة",
            "ذكر الله حياة القلوب", "العدل أساس الملك", "الأمانة شرف", "اللهم بارك لنا",
            "اغتنم وقتك", "خير الناس أنفعهم", "اللهم ثبت قلبي", "الصبر جميل",
            "اللسان مرآة العقل", "احفظ الله يحفظك", "الخير في العطاء", "اللهم توفنا مسلمين",
            "السكينة في الطاعة", "اجعل نيتك لله", "الحق أحق أن يتبع", "اللهم حسن الخاتمة",
            "التوبة بداية جديدة", "لا حول ولا قوة إلا بالله"
        ]

        random.shuffle(self.phrases)
        self.used_phrases = []

    def start_game(self):
        self.current_question = 0
        self.game_active = True
        self.previous_question = None
        self.previous_answer = None
        self.answered_users.clear()
        self.used_phrases.clear()
        return self.get_question()

    def get_question(self):
        available = [p for p in self.phrases if p not in self.used_phrases]
        if not available:
            self.used_phrases.clear()
            available = self.phrases.copy()

        phrase = random.choice(available)
        self.used_phrases.append(phrase)
        self.current_answer = phrase
        self.round_start_time = time.time()

        return self.build_question_flex(
            question_text=phrase,
            additional_info=f"الوقت {self.round_time} ثانية\nاكتب النص بالضبط"
        )

    def _time_expired(self) -> bool:
        if not self.round_start_time:
            return False
        return (time.time() - self.round_start_time) > self.round_time

    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        if not self.game_active:
            return None

        if self._time_expired():
            self.previous_question = self.current_answer
            self.previous_answer = self.current_answer
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["message"] = f"انتهى الوقت\n\n{result.get('message', '')}"
                return result

            return {"message": "انتهى الوقت", "response": self.get_question(), "points": 0}

        if user_id in self.answered_users:
            return None

        if self.team_mode and user_id not in self.joined_users:
            return None

        text = user_answer.strip()
        time_taken = time.time() - self.round_start_time

        if text == self.current_answer:
            self.answered_users.add(user_id)
            total_points = 1

            if self.team_mode:
                team = self.get_user_team(user_id) or self.assign_to_team(user_id)
                self.add_team_score(team, total_points)
            else:
                self.add_score(user_id, display_name, total_points)

            self.previous_question = self.current_answer
            self.previous_answer = self.current_answer
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = total_points
                return result

            msg = f"صحيح\nالوقت {time_taken:.1f}s\n+{total_points}"
            return {"message": msg, "response": self.get_question(), "points": total_points}

        return None
