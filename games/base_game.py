import re
from typing import Dict, Any, Optional
from datetime import datetime

class BaseGame:
    def __init__(self, line_bot_api=None, questions_count: int = 5):
        self.line_bot_api = line_bot_api
        self.questions_count = questions_count
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
        if user_id in self.answered_users:
            return 0
        
        if user_id not in self.scores:
            self.scores[user_id] = {"name": display_name, "score": 0}
        
        self.scores[user_id]["score"] += points
        self.answered_users.add(user_id)
        
        return points
    
    def start_game(self):
        self.current_question = 0
        self.scores.clear()
        self.answered_users.clear()
        self.previous_question = None
        self.previous_answer = None
        self.game_active = True
        self.game_start_time = datetime.now()
        
        return self.get_question()
    
    def get_question(self):
        raise NotImplementedError("يجب تنفيذ get_question في الفئة الفرعية")
    
    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("يجب تنفيذ check_answer في الفئة الفرعية")
    
    def end_game(self) -> Dict[str, Any]:
        self.game_active = False
        
        if not self.scores:
            return {
                "game_over": True,
                "points": 0,
                "message": "انتهت اللعبة"
            }
        
        sorted_players = sorted(
            self.scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        winner = sorted_players[0][1]
        
        message = f"انتهت اللعبة\n\nالفائز: {winner['name']}\nالنقاط: {winner['score']}"
        
        if len(sorted_players) > 1:
            message += "\n\nالترتيب:\n"
            for i, (uid, data) in enumerate(sorted_players[:5], 1):
                message += f"{i}. {data['name']} - {data['score']}\n"
        
        return {
            "game_over": True,
            "points": winner["score"],
            "message": message
        }
    
    def build_text_message(self, text: str):
        from linebot.models import TextSendMessage
        return TextSendMessage(text=text)
    
    def build_question_message(self, question_text: str, additional_info: str = None):
        progress = f"{self.current_question + 1}/{self.questions_count}"
        
        message = f"{self.game_name}\n{progress}\n\n{question_text}"
        
        if additional_info:
            message += f"\n\n{additional_info}"
        
        if self.previous_question and self.previous_answer:
            prev_ans = self.previous_answer if isinstance(self.previous_answer, str) else self.previous_answer[0]
            message += f"\n\nالسؤال السابق:\n{self.previous_question}\nالاجابة: {prev_ans}"
        
        if self.supports_hint and self.supports_reveal:
            message += "\n\nاكتب: لمح - جاوب"
        
        return self.build_text_message(message)
