from games.base_game import BaseGame
import random
from typing import Dict, Any, Optional

class CategoryGame(BaseGame):
    """لعبة الفئة والحرف"""
    
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "فئة"
        
        self.challenges = [
            {'category': 'المطبخ', 'letter': 'ق', 'answers': ['قدر', 'قلاية', 'قهوة']},
            {'category': 'حيوان', 'letter': 'ب', 'answers': ['بطة', 'بقرة', 'ببغاء']},
            {'category': 'فاكهة', 'letter': 'ت', 'answers': ['تفاح', 'توت', 'تمر']},
            {'category': 'خضار', 'letter': 'ب', 'answers': ['بصل', 'بطاطس', 'باذنجان']},
            {'category': 'بلاد', 'letter': 'س', 'answers': ['سعودية', 'سوريا', 'سودان']},
            {'category': 'اسم ولد', 'letter': 'م', 'answers': ['محمد', 'مصطفى', 'مالك']},
            {'category': 'اسم بنت', 'letter': 'ر', 'answers': ['ريم', 'رنا', 'رهف']},
            {'category': 'مهنة', 'letter': 'ط', 'answers': ['طبيب', 'طباخ', 'طيار']},
            {'category': 'رياضة', 'letter': 'ك', 'answers': ['كرة', 'كاراتيه', 'كريكت']},
            {'category': 'لون', 'letter': 'ا', 'answers': ['احمر', 'ازرق', 'اخضر']},
        ]
        
        self.questions = []
        self.first_correct_answer = False
    
    def start_game(self):
        """بدء اللعبة"""
        self.questions = random.sample(self.challenges, min(self.questions_count, len(self.challenges)))
        self.current_question = 0
        self.scores = {}
        self.answered_users = set()
        self.first_correct_answer = False
        return self.get_question()
    
    def get_question(self):
        """الحصول على سؤال جديد"""
        challenge = self.questions[self.current_question]
        self.first_correct_answer = False
        
        return self.build_question_message(
            f"الفئة: {challenge['category']}\nالحرف: {challenge['letter']}"
        )
    
    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        if self.first_correct_answer or user_id in self.answered_users:
            return None
        
        challenge = self.questions[self.current_question]
        normalized = self.normalize_text(user_answer)
        
        # التلميح
        if self.supports_hint and normalized == "لمح":
            sample = challenge['answers'][0]
            return {'response': self.build_text_message(f"يبدأ بحرف: {sample[0]}\nعدد الحروف: {len(sample)}"), 'points': 0}
        
        # عرض الإجابة
        if self.supports_reveal and normalized == "جاوب":
            answers = ' - '.join(challenge['answers'][:3])
            self.answered_users.add(user_id)
            self.first_correct_answer = True
            
            if self.current_question + 1 < self.questions_count:
                self.current_question += 1
                self.answered_users.clear()
                self.first_correct_answer = False
                return {'response': self.build_text_message(f"بعض الاجابات:\n{answers}"), 'points': 0, 'next_question': True}
            
            return self._end_game()
        
        # التحقق من الإجابة
        valid_answers = [self.normalize_text(ans) for ans in challenge['answers']]
        
        if normalized in valid_answers:
            points = self.add_score(user_id, display_name, 1)
            self.first_correct_answer = True
            
            if self.current_question + 1 < self.questions_count:
                self.current_question += 1
                self.answered_users.clear()
                self.first_correct_answer = False
                return {'response': self.build_text_message(f"اجابة صحيحة {display_name} +{points}"), 'points': points, 'next_question': True}
            
            return self._end_game()
        
        return None
    
    def _end_game(self):
        """إنهاء اللعبة"""
        if not self.scores:
            return {'response': self.build_text_message("انتهت اللعبة"), 'points': 0, 'game_over': True}
        
        sorted_players = sorted(self.scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        
        result_text = f"انتهت اللعبة\n\nالفائز: {winner['name']}\nالنقاط: {winner['score']}"
        
        if len(sorted_players) > 1:
            result_text += "\n\nالترتيب:\n"
            for i, (uid, data) in enumerate(sorted_players[:5], 1):
                result_text += f"{i}. {data['name']} - {data['score']}\n"
        
        return {'response': self.build_text_message(result_text), 'points': winner['score'], 'game_over': True}
