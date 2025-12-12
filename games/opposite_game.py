from games.base_game import BaseGame
import random
from typing import Dict, Any, Optional

class OppositeGame(BaseGame):
    """لعبة معرفة عكس الكلمات"""
    
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "ضد"
        
        self.opposites = {
            'كبير': ['صغير', 'قصير'], 'طويل': ['قصير'],
            'سريع': ['بطيء'], 'ساخن': ['بارد'],
            'نظيف': ['وسخ'], 'جديد': ['قديم'],
            'صعب': ['سهل'], 'قوي': ['ضعيف'],
            'غني': ['فقير'], 'سعيد': ['حزين'],
            'جميل': ['قبيح'], 'ثقيل': ['خفيف'],
            'عالي': ['منخفض'], 'واسع': ['ضيق'],
            'قريب': ['بعيد'], 'مفتوح': ['مغلق'],
            'نهار': ['ليل'], 'شمس': ['قمر'],
            'شتاء': ['صيف'], 'شرق': ['غرب'],
            'أبيض': ['أسود'], 'حلو': ['مر'],
            'حار': ['بارد'], 'جاف': ['رطب'],
            'مالح': ['حلو'], 'صحيح': ['خطأ'],
            'حي': ['ميت'], 'نور': ['ظلام'],
            'فوق': ['تحت'], 'يمين': ['يسار'],
            'أمام': ['خلف'], 'داخل': ['خارج'],
        }
        
        self.questions_list = list(self.opposites.items())
        random.shuffle(self.questions_list)
    
    def get_question(self):
        """الحصول على سؤال جديد"""
        word, opposites = self.questions_list[self.current_question % len(self.questions_list)]
        self.current_answer = opposites
        
        return self.build_question_message(
            f"ما عكس كلمة:\n{word}"
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
            word, _ = self.questions_list[self.current_question % len(self.questions_list)]
            self.previous_question = f"عكس {word}"
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
                
                word, _ = self.questions_list[self.current_question % len(self.questions_list)]
                self.previous_question = f"عكس {word}"
                self.previous_answer = correct_answer
                self.current_question += 1
                self.answered_users.clear()
                
                if self.current_question >= self.questions_count:
                    result = self.end_game()
                    result["points"] = points
                    return result
                
                return {"message": f"صحيح +{points}", "response": self.get_question(), "points": points}
        
        return None
