from games.base_game import BaseGame
import random
from typing import Dict, Any, Optional

class LettersGame(BaseGame):
    """لعبة تكوين كلمات من حروف"""
    
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "تكوين"
        
        self.letter_sets = [
            {'letters': ['ق', 'ل', 'م', 'ع', 'ر', 'ب'], 'words': ['قلم', 'علم', 'عمر', 'رقم', 'قلب']},
            {'letters': ['ك', 'ت', 'ا', 'ب', 'م', 'ل'], 'words': ['كتاب', 'كتب', 'مكتب', 'ملك']},
            {'letters': ['د', 'ر', 'س', 'ة', 'م', 'ا'], 'words': ['مدرسة', 'درس', 'مدرس', 'سدر']},
            {'letters': ['ح', 'د', 'ي', 'ق', 'ة', 'ر'], 'words': ['حديقة', 'حديد', 'قرد', 'دقيق']},
            {'letters': ['ب', 'ح', 'ر', 'ي', 'ة', 'س'], 'words': ['بحيرة', 'بحر', 'سير', 'حرب']},
            {'letters': ['ش', 'ج', 'ر', 'ة', 'م', 'ن'], 'words': ['شجرة', 'شجر', 'نجم', 'رجم']},
            {'letters': ['ت', 'م', 'ر', 'ي', 'ن', 'س'], 'words': ['تمر', 'تمرين', 'ترس', 'سمر']},
            {'letters': ['ل', 'ب', 'ن', 'ح', 'ة', 'ي'], 'words': ['لبن', 'حلب', 'نبل', 'نحل']},
            {'letters': ['خ', 'ب', 'ز', 'ر', 'ن', 'م'], 'words': ['خبز', 'خزن', 'برز', 'زمن']},
            {'letters': ['م', 'ا', 'ء', 'ي', 'ر', 'ن'], 'words': ['ماء', 'مرء', 'نار', 'راء']},
        ]
        
        random.shuffle(self.letter_sets)
        self.current_set = None
        self.found_words = set()
        self.required_words = 3
    
    def get_question(self):
        """الحصول على سؤال جديد"""
        q_data = self.letter_sets[self.current_question % len(self.letter_sets)]
        self.current_set = q_data
        self.current_answer = q_data['words']
        self.found_words.clear()
        
        letters_display = ' '.join(q_data['letters'])
        
        return self.build_question_message(
            f"كون كلمات من:\n{letters_display}",
            f"مطلوب {self.required_words} كلمات"
        )
    
    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        if not self.game_active:
            return None
        
        normalized = self.normalize_text(user_answer)
        
        # التلميح
        if self.supports_hint and normalized == "لمح":
            remaining = [w for w in self.current_answer if self.normalize_text(w) not in self.found_words]
            if remaining:
                word = remaining[0]
                hint = f"تبدأ بـ: {word[0]}\nعدد الحروف: {len(word)}"
            else:
                hint = "لا توجد تلميحات"
            return {"message": hint, "response": self.build_text_message(hint), "points": 0}
        
        # عرض الإجابة
        if self.supports_reveal and normalized == "جاوب":
            words = ' - '.join(self.current_answer[:5])
            self.current_question += 1
            self.answered_users.clear()
            self.found_words.clear()
            
            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["message"] = f"كلمات ممكنة: {words}\n\n{result.get('message', '')}"
                return result
            
            return {"message": f"كلمات ممكنة: {words}", "response": self.get_question(), "points": 0}
        
        # التحقق من الإجابة
        valid_words = [self.normalize_text(w) for w in self.current_answer]
        
        if normalized not in valid_words or normalized in self.found_words:
            return None
        
        self.found_words.add(normalized)
        points = 1
        
        # تحديث النقاط فقط عند الإجابة الأولى
        if user_id not in self.answered_users:
            self.scores.setdefault(user_id, {'name': display_name, 'score': 0})
            self.scores[user_id]['score'] += points
        
        # التحقق من إكمال العدد المطلوب
        if len(self.found_words) >= self.required_words:
            self.answered_users.add(user_id)
            self.current_question += 1
            self.answered_users.clear()
            self.found_words.clear()
            
            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = points
                return result
            
            return {"message": f"تم +{points}", "response": self.get_question(), "points": points}
        
        remaining = self.required_words - len(self.found_words)
        return {"message": f"صحيح تبقى {remaining}\n+{points}", "response": self.build_text_message(f"صحيح تبقى {remaining}\n+{points}"), "points": points}
