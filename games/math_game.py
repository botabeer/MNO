from games.base_game import BaseGame
import random
from typing import Dict, Any, Optional

class MathGame(BaseGame):
    """لعبة العمليات الحسابية"""
    
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "رياضيات"
        
        self.difficulty_levels = {
            1: {"name": "سهل", "min": 1, "max": 20, "ops": ['+', '-']},
            2: {"name": "متوسط", "min": 10, "max": 50, "ops": ['+', '-', 'x']},
            3: {"name": "صعب", "min": 20, "max": 100, "ops": ['+', '-', 'x']},
        }
        
        self.current_question_data = None
    
    def generate_math_question(self):
        """توليد سؤال رياضي"""
        level = min(self.current_question + 1, 3)
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
        else:  # x
            a = random.randint(2, 12)
            b = random.randint(2, 12)
            answer = a * b
            question = f"{a} x {b} = ؟"
        
        return {
            "question": question,
            "answer": str(answer),
            "level": level,
            "level_name": config["name"]
        }
    
    def get_question(self):
        """الحصول على سؤال جديد"""
        q_data = self.generate_math_question()
        self.current_question_data = q_data
        self.current_answer = q_data["answer"]
        
        return self.build_question_message(
            q_data["question"],
            f"المستوى: {q_data['level_name']}"
        )
    
    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        if not self.game_active or user_id in self.answered_users:
            return None
        
        answer = user_answer.strip()
        normalized = self.normalize_text(answer)
        
        # التلميح
        if self.supports_hint and normalized == "لمح":
            hint = f"الجواب من {len(self.current_answer)} رقم" if len(self.current_answer) == 1 else f"الجواب من {len(self.current_answer)} ارقام"
            return {"message": hint, "response": self.build_text_message(hint), "points": 0}
        
        # عرض الإجابة
        if self.supports_reveal and normalized == "جاوب":
            reveal = f"الجواب: {self.current_answer}"
            self.previous_question = self.current_question_data["question"] if self.current_question_data else None
            self.previous_answer = self.current_answer
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["message"] = f"{reveal}\n\n{result.get('message', '')}"
                return result
            
            return {"message": reveal, "response": self.get_question(), "points": 0}
        
        # التحقق من الإجابة
        try:
            user_num = int(answer)
        except:
            return None
        
        if user_num == int(self.current_answer):
            points = self.add_score(user_id, display_name, 1)
            
            self.previous_question = self.current_question_data["question"] if self.current_question_data else None
            self.previous_answer = self.current_answer
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = points
                return result
            
            return {"message": f"صحيح +{points}", "response": self.get_question(), "points": points}
        
        return None
