from games.base_game import BaseGame
import random
from typing import Dict, Any, Optional

class WordColorGame(BaseGame):
    """لعبة اختبار Stroop للألوان"""
    
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "لون"
        
        self.color_names = ["أحمر", "أزرق", "أخضر", "أصفر", "برتقالي", "بنفسجي", "وردي"]
        
        self.current_word = None
        self.current_color_name = None
    
    def get_question(self):
        """الحصول على سؤال جديد"""
        word = random.choice(self.color_names)
        # 70% من الوقت اللون يختلف عن الكلمة
        color_name = random.choice([c for c in self.color_names if c != word]) if random.random() < 0.7 else word
        
        self.current_word = word
        self.current_color_name = color_name
        self.current_answer = [color_name]
        
        message = f"ما لون هذه الكلمة:\n\n{word}\n\nملاحظة: اللون مكتوب باللون {color_name}"
        
        return self.build_question_message(message)
    
    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        if not self.game_active or user_id in self.answered_users:
            return None
        
        normalized = self.normalize_text(user_answer)
        
        # التلميح
        if self.supports_hint and normalized == "لمح":
            hint = f"يبدأ بـ: {self.current_answer[0][0]}\nعدد الحروف: {len(self.current_answer[0])}"
            return {"message": hint, "response": self.build_text_message(hint), "points": 0}
        
        # عرض الإجابة
        if self.supports_reveal and normalized == "جاوب":
            reveal = f"اللون: {self.current_answer[0]}"
            self.previous_question = f"كلمة {self.current_word} ملونة بـ"
            self.previous_answer = self.current_answer[0]
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["message"] = f"{reveal}\n\n{result.get('message', '')}"
                return result
            
            return {"message": reveal, "response": self.get_question(), "points": 0}
        
        # التحقق من الإجابة
        correct = self.normalize_text(self.current_answer[0])
        
        if normalized == correct:
            points = self.add_score(user_id, display_name, 1)
            
            self.previous_question = f"كلمة {self.current_word} ملونة بـ"
            self.previous_answer = self.current_answer[0]
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = points
                return result
            
            return {"message": f"صحيح +{points}", "response": self.get_question(), "points": points}
        
        return None
