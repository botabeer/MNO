import re
from typing import Dict, Any, Optional
from datetime import datetime

class BaseGame:
    def __init__(self, line_bot_api=None, questions_count: int = 5):
        self.line_bot_api = line_bot_api
        self.questions_count = 5  # ثابت 5 أسئلة دائماً
        self.current_question = 0
        self.current_answer = None
        self.previous_question = None
        self.previous_answer = None
        self.scores: Dict[str, Dict[str, Any]] = {}
        self.answered_users = set()
        self.game_active = False
        self.game_start_time: Optional[datetime] = None
        
        self.game_name = "لعبة"
        self.supports_hint = True
        self.supports_reveal = True
    
    def normalize_text(self, text: str) -> str:
        """تطبيع النص العربي"""
        if not text:
            return ""
        
        text = text.strip().lower()
        
        replacements = {
            'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
            'ى': 'ي', 'ة': 'ه', 'ؤ': 'و',
            'ئ': 'ي', 'ء': ''
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
        
        return text
    
    def add_score(self, user_id: str, display_name: str, points: int = 1) -> int:
        """إضافة نقاط للاعب - يمكن للاعب الإجابة مرة واحدة فقط لكل سؤال"""
        if user_id in self.answered_users:
            return 0
        
        if user_id not in self.scores:
            self.scores[user_id] = {"name": display_name, "score": 0}
        
        self.scores[user_id]["score"] += points
        self.answered_users.add(user_id)
        
        return points
    
    def start_game(self):
        """بدء اللعبة"""
        self.current_question = 0
        self.scores.clear()
        self.answered_users.clear()
        self.previous_question = None
        self.previous_answer = None
        self.game_active = True
        self.game_start_time = datetime.now()
        
        return self.get_question()
    
    def get_question(self):
        """الحصول على سؤال جديد - يجب تنفيذها في الفئة الفرعية"""
        raise NotImplementedError("يجب تنفيذ get_question في الفئة الفرعية")
    
    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        """التحقق من الإجابة - يجب تنفيذها في الفئة الفرعية"""
        raise NotImplementedError("يجب تنفيذ check_answer في الفئة الفرعية")
    
    def move_to_next_question(self):
        """الانتقال للسؤال التالي"""
        self.current_question += 1
        self.answered_users.clear()
        
        if self.current_question >= self.questions_count:
            return None
        
        return self.get_question()
    
    def end_game(self) -> Dict[str, Any]:
        """إنهاء اللعبة وإعلان الفائز"""
        self.game_active = False
        
        if not self.scores:
            message = "انتهت اللعبة - لا يوجد فائز"
            return {
                "game_over": True,
                "points": 0,
                "message": message,
                "response": self.build_text_message(message)
            }
        
        sorted_players = sorted(
            self.scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        winner = sorted_players[0][1]
        winner_id = sorted_players[0][0]
        
        message = f"انتهت اللعبة - {self.game_name}\n\n"
        message += f"الفائز: {winner['name']}\n"
        message += f"النقاط: {winner['score']}/{self.questions_count}\n"
        
        if len(sorted_players) > 1:
            message += "\nالترتيب النهائي:\n"
            for i, (_, data) in enumerate(sorted_players[:5], 1):
                message += f"{i}. {data['name']} - {data['score']} نقطة\n"
        
        return {
            "game_over": True,
            "points": winner["score"],
            "winner_id": winner_id,
            "message": message,
            "response": self.build_text_message(message)
        }
    
    def build_text_message(self, text: str):
        """بناء رسالة نصية"""
        from linebot.models import TextSendMessage
        return TextSendMessage(text=text)
    
    def build_question_message(self, question_text: str, additional_info: str = None):
        """بناء رسالة السؤال"""
        progress = f"السؤال {self.current_question + 1} من {self.questions_count}"
        
        message = f"{self.game_name}\n"
        message += f"{progress}\n"
        message += f"{'=' * 25}\n\n"
        message += f"{question_text}\n"
        
        if additional_info:
            message += f"\nمعلومة: {additional_info}"
        
        if self.previous_question and self.previous_answer:
            prev_ans = (
                self.previous_answer
                if isinstance(self.previous_answer, str)
                else self.previous_answer[0]
            )
            message += f"\n\n{'=' * 25}\n"
            message += f"السؤال السابق:\n{self.previous_question}\n"
            message += f"الإجابة: {prev_ans}"
        
        if self.supports_hint and self.supports_reveal:
            message += f"\n\n{'=' * 25}\n"
            message += "اكتب: لمح (للتلميح)\n"
            message += "اكتب: جاوب (لعرض الإجابة)"
        
        return self.build_text_message(message)
