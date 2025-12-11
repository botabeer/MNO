from games.base_game import BaseGame
import random
from typing import Dict, Any, Optional

class ScrambleGame(BaseGame):
    """لعبة ترتيب الحروف"""
    
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "ترتيب"
        
        self.words = [
            'مدرسة', 'كتاب', 'قلم', 'باب', 'نافذة',
            'طاولة', 'كرسي', 'سيارة', 'طائرة', 'قطار',
            'تفاحة', 'موز', 'برتقال', 'عنب', 'بطيخ',
            'شمس', 'قمر', 'نجمة', 'سماء', 'بحر',
            'أسد', 'نمر', 'فيل', 'زرافة', 'حصان',
            'ورد', 'شجرة', 'زهرة', 'عشب', 'ورقة',
            'منزل', 'مسجد', 'حديقة', 'ملعب', 'مطعم',
        ]
        
        random.shuffle(self.words)
        self.used_words = []
        self.current_scrambled = None
    
    def scramble_word(self, word: str) -> str:
        """خلط الحروف"""
        letters = list(word)
        attempts = 0
        while attempts < 10:
            random.shuffle(letters)
            scrambled = ' '.join(letters)
            if scrambled.replace(' ', '') != word:
                return scrambled
            attempts += 1
        return ' '.join(word[::-1])
    
    def get_question(self):
        """الحصول على سؤال جديد"""
        available = [w for w in self.words if w not in self.used_words]
        if not available:
            self.used_words = []
            available = self.words.copy()
        
        word = random.choice(available)
        self.used_words.append(word)
        self.current_answer = word
        self.current_scrambled = self.scramble_word(word)
        
        return self.build_question_message(
            f"رتب الحروف:\n{self.current_scrambled}",
            f"عدد الحروف: {len(word)}"
        )
    
    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        if not self.game_active or user_id in self.answered_users:
            return None
        
        normalized = self.normalize_text(user_answer)
        
        # التلميح
        if self.supports_hint and normalized == "لمح":
            hint = f"تبدأ بـ: {self.current_answer[0]}\nعدد الحروف: {len(self.current_answer)}"
            return {"message": hint, "response": self.build_text_message(hint), "points": 0}
        
        # عرض الإجابة
        if self.supports_reveal and normalized == "جاوب":
            reveal = f"الاجابة: {self.current_answer}"
            self.previous_question = self.current_scrambled
            self.previous_answer = self.current_answer
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["message"] = f"{reveal}\n\n{result.get('message', '')}"
                return result
            
            return {"message": reveal, "response": self.get_question(), "points": 0}
        
        # التحقق من الإجابة
        if normalized == self.normalize_text(self.current_answer):
            points = self.add_score(user_id, display_name, 1)
            
            self.previous_question = self.current_scrambled
            self.previous_answer = self.current_answer
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = points
                return result
            
            return {"message": f"صحيح +{points}", "response": self.get_question(), "points": points}
        
        return None
