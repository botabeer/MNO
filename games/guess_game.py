from games.base_game import BaseGame
import random
from typing import Dict, Any, Optional, List

class GuessGame(BaseGame):
    """لعبة التخمين من فئة وحرف"""
    
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "خمن"
        
        self.items = {
            "المطبخ": {
                "ق": ["قدر", "قلاية"], "م": ["ملعقة", "مغرفة"],
                "س": ["سكين", "صحن"], "ف": ["فرن", "فنجان"],
            },
            "غرفة النوم": {
                "س": ["سرير", "ستارة"], "و": ["وسادة"],
                "م": ["مرآة", "مخدة"], "د": ["دولاب"],
            },
            "المدرسة": {
                "ق": ["قلم"], "د": ["دفتر", "دولاب"],
                "ك": ["كتاب", "كراسة"], "م": ["مسطرة"],
            },
            "الفواكه": {
                "ت": ["تفاح", "تمر"], "م": ["موز", "مشمش"],
                "ع": ["عنب"], "ب": ["برتقال", "بطيخ"],
            },
            "الحيوانات": {
                "ق": ["قطة", "قرد"], "ف": ["فيل", "فهد"],
                "أ": ["أسد", "أرنب"], "ج": ["جمل"],
            },
        }
        
        self.questions_list: List[Dict[str, Any]] = []
        for category, letters in self.items.items():
            for letter, words in letters.items():
                self.questions_list.append({
                    "category": category,
                    "letter": letter,
                    "answers": words
                })
        
        random.shuffle(self.questions_list)
    
    def get_question(self):
        """الحصول على سؤال جديد"""
        q_data = self.questions_list[self.current_question % len(self.questions_list)]
        self.current_answer = q_data["answers"]
        
        return self.build_question_message(
            f"الفئة: {q_data['category']}\nيبدأ بحرف: {q_data['letter']}"
        )
    
    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        if not self.game_active or user_id in self.answered_users:
            return None
        
        normalized = self.normalize_text(user_answer)
        
        # التلميح
        if self.supports_hint and normalized == "لمح":
            answer = self.current_answer[0]
            hint = f"تبدأ بـ: {answer[0]}\nعدد الحروف: {len(answer)}"
            return {"message": hint, "response": self.build_text_message(hint), "points": 0}
        
        # عرض الإجابة
        if self.supports_reveal and normalized == "جاوب":
            answers_text = " او ".join(self.current_answer)
            q_data = self.questions_list[self.current_question % len(self.questions_list)]
            self.previous_question = f"{q_data['category']} حرف {q_data['letter']}"
            self.previous_answer = answers_text
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["message"] = f"الاجابة: {answers_text}\n\n{result.get('message', '')}"
                return result
            
            return {"message": f"الاجابة: {answers_text}", "response": self.get_question(), "points": 0}
        
        # التحقق من الإجابة
        for correct_answer in self.current_answer:
            if self.normalize_text(correct_answer) == normalized:
                points = self.add_score(user_id, display_name, 1)
                
                q_data = self.questions_list[self.current_question % len(self.questions_list)]
                self.previous_question = f"{q_data['category']} حرف {q_data['letter']}"
                self.previous_answer = correct_answer
                self.current_question += 1
                self.answered_users.clear()
                
                if self.current_question >= self.questions_count:
                    result = self.end_game()
                    result["points"] = points
                    return result
                
                return {"message": f"صحيح +{points}", "response": self.get_question(), "points": points}
        
        return None
