"""
لعبة كلمة ولون
اللاعب يقول لون الكلمة وليس الكلمة نفسها
"""

from linebot.models import TextSendMessage
import random
import logging

logger = logging.getLogger(__name__)


class WordColorGame:
    """لعبة الكلمة واللون"""
    
    def __init__(self, line_bot_api, use_ai=False, get_api_key=None, switch_key=None):
        self.line_bot_api = line_bot_api
        self.current_word = None
        self.current_color = None
        
        # الكلمات والألوان
        self.words = ['احمر', 'ازرق', 'اخضر', 'اصفر', 'برتقالي', 'بنفسجي', 'اسود', 'ابيض']
        self.colors_emoji = {
            'احمر': '🔴',
            'ازرق': '🔵',
            'اخضر': '🟢',
            'اصفر': '🟡',
            'برتقالي': '🟠',
            'بنفسجي': '🟣',
            'اسود': '⚫',
            'ابيض': '⚪'
        }
    
    def start_game(self):
        """بدء سؤال جديد"""
        self.current_word = random.choice(self.words)
        self.current_color = random.choice(self.words)
        
        # التأكد من أن اللون يختلف عن الكلمة لزيادة الصعوبة
        while self.current_color == self.current_word:
            self.current_color = random.choice(self.words)
        
        emoji = self.colors_emoji[self.current_color]
        
        return TextSendMessage(
            text=f"ما هو لون الكلمة؟\n\n"
                 f"{emoji} {self.current_word}\n\n"
                 f"جاوب - لعرض الاجابة"
        )
    
    def check_answer(self, answer, user_id, display_name):
        """فحص الإجابة"""
        if not self.current_color:
            return None
        
        answer_normalized = answer.strip().lower()
        
        if answer_normalized in ['جاوب', 'استسلم']:
            return {
                'points': 0,
                'won': False,
                'game_over': False,
                'response': TextSendMessage(
                    text=f"الاجابة الصحيحة: {self.current_color}"
                )
            }
        
        if answer_normalized == self.current_color.lower():
            return {
                'points': 5,
                'won': True,
                'game_over': False,
                'response': TextSendMessage(
                    text=f"ممتاز {display_name}!\n\nالنقاط: +5"
                )
            }
        else:
            return {
                'points': 0,
                'won': False,
                'response': TextSendMessage(text="خطأ! حاول مرة اخرى")
            }
