from games.base_game import BaseGame
import random
from typing import Dict, Any, Optional

class IqGame(BaseGame):
    """لعبة الألغاز والذكاء"""
    
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "ذكاء"
        
        self.riddles = [
            {"q": "ما الشيء الذي يمشي بلا أرجل ويبكي بلا عيون", "a": ["السحاب", "الغيم"]},
            {"q": "له رأس ولكن لا عين له", "a": ["الدبوس", "المسمار", "الإبرة"]},
            {"q": "شيء كلما زاد نقص", "a": ["العمر", "الوقت"]},
            {"q": "يكتب ولا يقرأ أبدا", "a": ["القلم"]},
            {"q": "له أسنان كثيرة ولكنه لا يعض", "a": ["المشط"]},
            {"q": "يوجد في الماء ولكن الماء يميته", "a": ["الملح"]},
            {"q": "يتكلم بجميع اللغات دون أن يتعلمها", "a": ["الصدى"]},
            {"q": "شيء كلما أخذت منه كبر", "a": ["الحفرة"]},
            {"q": "يخترق الزجاج ولا يكسره", "a": ["الضوء", "النور"]},
            {"q": "يسمع بلا أذن ويتكلم بلا لسان", "a": ["الهاتف", "الجوال"]},
            {"q": "ما هو الشيء الذي تراه ولا تستطيع لمسه", "a": ["الظل"]},
            {"q": "له عينان ولا يرى", "a": ["المقص"]},
            {"q": "أخضر في الأرض وأسود في السوق وأحمر في البيت", "a": ["الشاي"]},
            {"q": "ما هو الشيء الذي لا يمشي إلا بالضرب", "a": ["المسمار"]},
            {"q": "له أوراق وليس شجرا", "a": ["الكتاب"]},
            {"q": "ما هو الشيء الذي يقرصك ولا تراه", "a": ["الجوع"]},
            {"q": "يمتلئ بالثقوب ويحفظ الماء", "a": ["الإسفنج"]},
            {"q": "يسير بلا قدمين ويدخل الأذنين", "a": ["الصوت"]},
            {"q": "يولد كبيرا ويموت صغيرا", "a": ["الشمعة"]},
            {"q": "له رقبة وليس له رأس", "a": ["الزجاجة"]},
            {"q": "تستطيع كسره دون لمسه", "a": ["الوعد"]},
            {"q": "ما هو الشيء الذي لا يتكلم ولكن إذا ضربته صاح", "a": ["الجرس"]},
            {"q": "ما هو الشيء الذي إذا سميته كسر", "a": ["الصمت"]},
            {"q": "ما هو الشيء الذي تذبحه وتبكي عليه", "a": ["البصل"]},
            {"q": "يأكل ولا يشبع", "a": ["النار"]},
            {"q": "له مفتاح ولا يفتح", "a": ["البيانو"]},
            {"q": "له يد واحدة ولا يستطيع التصفيق", "a": ["الساعة"]},
            {"q": "ما هو الشيء الذي له أربع أرجل ولا يمشي", "a": ["الكرسي", "الطاولة"]},
            {"q": "يصعد ولا ينزل", "a": ["العمر"]},
        ]
        
        random.shuffle(self.riddles)
        self.used_riddles = []
    
    def get_question(self):
        """الحصول على سؤال جديد"""
        available = [r for r in self.riddles if r not in self.used_riddles]
        if not available:
            self.used_riddles = []
            available = self.riddles.copy()
        
        riddle = random.choice(available)
        self.used_riddles.append(riddle)
        self.current_answer = riddle["a"]
        
        return self.build_question_message(riddle['q'])
    
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
            self.previous_question = self.used_riddles[-1]["q"] if self.used_riddles else None
            self.previous_answer = answers_text
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["message"] = f"الاجابة: {answers_text}\n\n{result.get('message', '')}"
                return result
            
            return {"message": f"الاجابة: {answers_text}", "response": self.get_question(), "points": 0}
        
        # التحقق من الإجابة
        for correct in self.current_answer:
            if self.normalize_text(correct) == normalized:
                points = self.add_score(user_id, display_name, 1)
                
                self.previous_question = self.used_riddles[-1]["q"] if self.used_riddles else None
                self.previous_answer = correct
                self.current_question += 1
                self.answered_users.clear()
                
                if self.current_question >= self.questions_count:
                    result = self.end_game()
                    result["points"] = points
                    return result
                
                return {"message": f"صحيح +{points}", "response": self.get_question(), "points": points}
        
        return None
