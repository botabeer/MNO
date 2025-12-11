"""
لعبة رياضيات - Bot Mesh v20.1 FINAL
Created by: Abeer Aldosari © 2025
✅ نقطة واحدة لكل إجابة | ثيمات | سؤال سابق | أزرار | بدون وقت
"""

from games.base_game import BaseGame
import random
from typing import Dict, Any, Optional


class MathGame(BaseGame):
    """لعبة رياضيات"""

    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "رياضيات"
        self.supports_hint = True
        self.supports_reveal = True

        self.difficulty_levels = {
            1: {"name": "سهل", "min": 1, "max": 20, "ops": ['+', '-']},
            2: {"name": "متوسط", "min": 10, "max": 50, "ops": ['+', '-', '×']},
            3: {"name": "صعب", "min": 20, "max": 100, "ops": ['+', '-', '×']},
            4: {"name": "صعب جداً", "min": 50, "max": 200, "ops": ['+', '-', '×']},
            5: {"name": "خبير", "min": 100, "max": 500, "ops": ['+', '-', '×', '÷']}
        }

        self.current_question_data = None

    def generate_math_question(self):
        """توليد سؤال رياضي"""
        level = min(self.current_question + 1, 5)
        config = self.difficulty_levels[level]
        operation = random.choice(config["ops"])

        if operation == '+':
            a = random.randint(config["min"], config["max"])
            b = random.randint(config["min"], config["max"])
            answer = a + b
            question = f"{a} + {b} = ؟"
        elif operation == '-':
            a = random.randint(config["min"] + 10, config["max"])
            b = random.randint(config["min"], a - 1)
            answer = a - b
            question = f"{a} - {b} = ؟"
        elif operation == '×':
            max_factor = min(20, config["max"] // 10)
            a = random.randint(2, max_factor)
            b = random.randint(2, max_factor)
            answer = a * b
            question = f"{a} × {b} = ؟"
        else:
            result = random.randint(2, 20)
            divisor = random.randint(2, 15)
            a = result * divisor
            answer = result
            question = f"{a} ÷ {divisor} = ؟"

        return {
            "question": question,
            "answer": str(answer),
            "level": level,
            "level_name": config["name"]
        }

    def start_game(self):
        self.current_question = 0
        self.game_active = True
        self.previous_question = None
        self.previous_answer = None
        self.answered_users.clear()
        return self.get_question()

    def get_question(self):
        q_data = self.generate_math_question()
        self.current_question_data = q_data
        self.current_answer = q_data["answer"]

        return self.build_question_flex(
            question_text=q_data["question"],
            additional_info=f"المستوى {q_data['level_name']}"
        )

    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        if not self.game_active or user_id in self.answered_users:
            return None

        if self.team_mode and user_id not in self.joined_users:
            return None

        answer = user_answer.strip()
        normalized = self.normalize_text(answer)

        if self.can_use_hint() and normalized == "لمح":
            hint = f"الجواب من {len(self.current_answer)} رقم"
            if len(self.current_answer) > 1:
                hint = f"الجواب من {len(self.current_answer)} ارقام"
            return {"message": hint, "response": self._create_text_message(hint), "points": 0}

        if self.can_reveal_answer() and normalized == "جاوب":
            reveal = f"الجواب {self.current_answer}"
            self.previous_question = self.current_question_data["question"] if self.current_question_data else None
            self.previous_answer = self.current_answer
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["message"] = f"{reveal}\n\n{result.get('message', '')}"
                return result

            return {"message": reveal, "response": self.get_question(), "points": 0}

        if self.team_mode and normalized in ["لمح", "جاوب"]:
            return None

        try:
            user_num = int(answer)
        except:
            return None

        if user_num == int(self.current_answer):
            total_points = 1

            if self.team_mode:
                team = self.get_user_team(user_id) or self.assign_to_team(user_id)
                self.add_team_score(team, total_points)
            else:
                self.add_score(user_id, display_name, total_points)

            self.previous_question = self.current_question_data["question"] if self.current_question_data else None
            self.previous_answer = self.current_answer
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = total_points
                return result

            return {"message": f"صحيح +{total_points}", "response": self.get_question(), "points": total_points}

        return None
