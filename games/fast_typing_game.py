from games.base_game import BaseGame
import random
import time
from typing import Dict, Any, Optional

class FastGame(BaseGame):
    """لعبة الكتابة السريعة"""
    
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "اسرع"
        self.supports_hint = False
        self.supports_reveal = False
        
        self.round_time = 20  # ثانية
        self.round_start_time = None
        
        self.phrases = [
            'سبحان الله', 'الحمد لله', 'الله أكبر',
            'لا إله إلا الله', 'استغفر الله',
            'لا حول ولا قوة إلا بالله',
            'رب اغفر لي', 'توكل على الله',
            'الصبر مفتاح الفرج', 'من جد وجد',
            'العلم نور', 'كن محسنا',
            'الدال على الخير كفاعله',
            'رب زدني علما', 'اتق الله',
        ]
        
        random.shuffle(self.phrases)
        self.used_phrases = []
    
    def get_question(self):
        """الحصول على سؤال جديد"""
        available = [p for p in self.phrases if p not in self.used_phrases]
        if not available:
            self.used_phrases = []
            available = self.phrases.copy()
        
        phrase = random.choice(available)
        self.used_phrases.append(phrase)
        self.current_answer = phrase
        self.round_start_time = time.time()
        
        return self.build_question_message(
            phrase,
            f"الوقت: {self.round_time} ثانية\nاكتب النص بالضبط"
        )
    
    def _time_expired(self) -> bool:
        """التحقق من انتهاء الوقت"""
        if not self.round_start_time:
            return False
        return (time.time() - self.round_start_time) > self.round_time
    
    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        if not self.game_active:
            return None
        
        # التحقق من انتهاء الوقت
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
        
        text = user_answer.strip()
        time_taken = time.time() - self.round_start_time
        
        # التحقق من الإجابة
        if text == self.current_answer:
            points = self.add_score(user_id, display_name, 1)
            
            self.previous_question = self.current_answer
            self.previous_answer = self.current_answer
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = points
                return result
            
            msg = f"صحيح\nالوقت: {time_taken:.1f}s\n+{points}"
            return {"message": msg, "response": self.get_question(), "points": points}
        
        return None
