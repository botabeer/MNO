"""
لعبة سلسلة - Bot Mesh v20.1 FINAL
Created by: Abeer Aldosari © 2025
✅ نقطة واحدة لكل إجابة | ثيمات | سؤال سابق | أزرار | بدون وقت
"""

from games.base_game import BaseGame
import random
from typing import Dict, Any, Optional


class ChainWordsGame(BaseGame):
    """لعبة سلسلة"""

    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "سلسلة"
        self.supports_hint = False
        self.supports_reveal = False

        self.starting_words = [
            "سيارة","تفاح","قلم","نجم","كتاب","باب","رمل","لعبة","حديقة","ورد",
            "دفتر","معلم","منزل","شمس","سفر","رياضة","علم","مدرسة","طائرة","عصير",
            "بحر","سماء","طريق","جبل","مدينة","شجرة","حاسب","هاتف","ساعة","مطر",
            "زهرة","سرير","مطبخ","نافذة","مفتاح","مصباح","وسادة","بطارية","لوحة",
            "حقيبة","مزرعة","قطار","مكتبة","مستشفى","ملعب","مسبح","مقهى","مكتب","مطار"
        ]

        self.last_word = None
        self.used_words = set()

    def start_game(self):
        self.current_question = 0
        self.game_active = True
        self.previous_question = None
        self.previous_answer = None
        self.last_word = random.choice(self.starting_words)
        self.used_words = {self.normalize_text(self.last_word)}
        self.answered_users.clear()
        return self.get_question()

    def get_question(self):
        required_letter = self.last_word[-1]

        return self.build_question_flex(
            question_text=f"الكلمة السابقة\n{self.last_word}",
            additional_info=f"ابدأ بحرف {required_letter}"
        )

    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        if not self.game_active:
            return None

        if user_id in self.answered_users:
            return None

        if self.team_mode and user_id not in self.joined_users:
            return None

        normalized_answer = self.normalize_text(user_answer)

        if normalized_answer in self.used_words:
            return None

        required_letter = self.normalize_text(self.last_word[-1])

        if normalized_answer and normalized_answer[0] == required_letter and len(normalized_answer) >= 2:
            self.used_words.add(normalized_answer)
            
            self.previous_question = f"كلمة تبدأ بـ {self.last_word[-1]}"
            self.previous_answer = user_answer.strip()
            
            self.last_word = user_answer.strip()
            
            total_points = 1

            if self.team_mode:
                team = self.get_user_team(user_id) or self.assign_to_team(user_id)
                self.add_team_score(team, total_points)
            else:
                self.add_score(user_id, display_name, total_points)

            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = total_points
                return result

            return {"message": f"صحيح +{total_points}", "response": self.get_question(), "points": total_points}

        return None
