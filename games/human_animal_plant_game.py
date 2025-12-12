from games.base_game import BaseGame
import random
from typing import Dict, Any, Optional

class HumanAnimalGame(BaseGame):
    """لعبة إنسان حيوان نبات جماد بلاد"""
    
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "لعبة"
        
        self.letters = list("ابتجحدرزسشصطعفقكلمنهوي")
        random.shuffle(self.letters)
        self.categories = ["إنسان", "حيوان", "نبات", "جماد", "بلاد"]
        
        self.database = {
            "إنسان": {
                "م": ["محمد", "مريم", "مصطفى"], "أ": ["أحمد", "أمل", "أمير"],
                "ع": ["علي", "عمر", "عائشة"], "ف": ["فاطمة", "فهد", "فيصل"],
                "س": ["سارة", "سعيد", "سلمان"], "ر": ["رامي", "رنا", "رشيد"],
            },
            "حيوان": {
                "أ": ["أسد", "أرنب"], "ج": ["جمل", "جاموس"],
                "ح": ["حصان", "حمار"], "خ": ["خروف"],
                "د": ["دجاجة", "ديك"], "ف": ["فيل", "فهد"],
                "ق": ["قرد", "قطة"], "ن": ["نمر", "نعامة"],
            },
            "نبات": {
                "ت": ["تفاح", "تمر"], "ب": ["بطيخ", "برتقال"],
                "ر": ["رمان"], "ع": ["عنب"],
                "ف": ["فراولة"], "م": ["موز", "مشمش"],
            },
            "جماد": {
                "ب": ["باب", "بيت"], "ت": ["تلفاز", "تلفون"],
                "س": ["سيارة", "ساعة"], "ق": ["قلم", "قفل"],
                "ك": ["كرسي", "كتاب"], "م": ["مفتاح", "مكتب"],
            },
            "بلاد": {
                "أ": ["أمريكا", "ألمانيا"], "ب": ["بريطانيا", "البرازيل"],
                "ت": ["تركيا", "تونس"], "س": ["السعودية", "سوريا"],
                "ع": ["عمان", "العراق"], "ف": ["فرنسا", "فلسطين"],
                "م": ["مصر", "المغرب"], "ي": ["اليمن", "اليابان"],
            }
        }
        
        self.current_category = None
        self.current_letter = None
    
    def get_question(self):
        """الحصول على سؤال جديد"""
        self.current_letter = self.letters[self.current_question % len(self.letters)]
        self.current_category = random.choice(self.categories)
        
        return self.build_question_message(
            f"الفئة: {self.current_category}\nالحرف: {self.current_letter}"
        )
    
    def get_suggested_answer(self) -> Optional[str]:
        """الحصول على إجابة مقترحة"""
        if self.current_category in self.database:
            if self.current_letter in self.database[self.current_category]:
                answers = self.database[self.current_category][self.current_letter]
                if answers:
                    return random.choice(answers)
        return None
    
    def validate_answer(self, normalized_answer: str) -> bool:
        """التحقق من صحة الإجابة"""
        if not normalized_answer or len(normalized_answer) < 2:
            return False
        
        required_letter = self.normalize_text(self.current_letter)
        if normalized_answer[0] != required_letter:
            return False
        
        return True
    
    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        if not self.game_active or user_id in self.answered_users:
            return None
        
        normalized = self.normalize_text(user_answer)
        
        # التلميح
        if self.supports_hint and normalized == "لمح":
            suggested = self.get_suggested_answer()
            hint = f"تبدأ بـ: {suggested[0]}\nعدد الحروف: {len(suggested)}" if suggested else "فكر جيدا"
            return {"message": hint, "response": self.build_text_message(hint), "points": 0}
        
        # عرض الإجابة
        if self.supports_reveal and normalized == "جاوب":
            suggested = self.get_suggested_answer()
            reveal = f"مثال: {suggested}" if suggested else "لا توجد إجابة ثابتة"
            self.previous_question = f"{self.current_category} حرف {self.current_letter}"
            self.previous_answer = suggested or "متعددة"
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["message"] = f"{reveal}\n\n{result.get('message', '')}"
                return result
            
            return {"message": reveal, "response": self.get_question(), "points": 0}
        
        # التحقق من الإجابة
        is_valid = self.validate_answer(normalized)
        
        if not is_valid:
            return None
        
        points = self.add_score(user_id, display_name, 1)
        
        self.previous_question = f"{self.current_category} حرف {self.current_letter}"
        self.previous_answer = user_answer.strip()
        self.current_question += 1
        self.answered_users.clear()
        
        if self.current_question >= self.questions_count:
            result = self.end_game()
            result["points"] = points
            return result
        
        return {"message": f"صحيح +{points}", "response": self.get_question(), "points": points}
