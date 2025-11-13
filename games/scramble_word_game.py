"""
لعبة ترتيب الحروف
اللاعب يرتب الحروف المبعثرة ليكون كلمة صحيحة
"""

from linebot.models import TextSendMessage
import random
import logging

logger = logging.getLogger(__name__)


class ScrambleWordGame:
    """لعبة ترتيب الحروف"""
    
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.current_word = None
        self.scrambled = None
        
        # 40 كلمة متنوعة
        self.words = [
            'سيارة', 'مدرسة', 'مستشفى', 'كمبيوتر', 'تلفزيون',
            'هاتف', 'كتاب', 'قلم', 'مكتب', 'كرسي',
            'طاولة', 'نافذة', 'باب', 'سقف', 'جدار',
            'حديقة', 'زهرة', 'شجرة', 'فراشة', 'عصفور',
            'بحر', 'نهر', 'جبل', 'صحراء', 'سماء',
            'شمس', 'قمر', 'نجم', 'سحاب', 'مطر',
            'تفاح', 'موز', 'برتقال', 'عنب', 'تمر',
            'خبز', 'ماء', 'حليب', 'قهوة', 'شاي',
            'اسد', 'نمر', 'فيل', 'زرافة', 'حصان',
            'جمل', 'خروف', 'دجاج', 'سمك', 'حوت'
        ]
    
    def start_game(self):
        """بدء سؤال جديد"""
        self.current_word = random.choice(self.words)
        
        # خلط الحروف
        letters = list(self.current_word)
        random.shuffle(letters)
        self.scrambled = ''.join(letters)
        
        # التأكد من أن الكلمة اختلفت
        while self.scrambled == self.current_word:
            random.shuffle(letters)
            self.scrambled = ''.join(letters)
        
        return TextSendMessage(
            text=f"رتب الحروف:\n\n"
                 f"{self.scrambled}\n\n"
                 f"لمح - للحصول على تلميح\n"
                 f"جاوب - لعرض الاجابة"
        )
    
    def check_answer(self, answer, user_id, display_name):
        """فحص الإجابة"""
        if not self.current_word:
            return None
        
        answer_normalized = answer.strip().lower()
        
        if answer_normalized in ['لمح', 'تلميح']:
            hint = self.current_word[0] + '...'
            return {
                'points': 0,
                'won': False,
                'response': TextSendMessage(
                    text=f"تلميح: تبدأ بـ {hint}"
                )
            }
        
        if answer_normalized in ['جاوب', 'استسلم']:
            return {
                'points': 0,
                'won': False,
                'game_over': False,
                'response': TextSendMessage(
                    text=f"الاجابة الصحيحة: {self.current_word}"
                )
            }
        
        if answer_normalized == self.current_word.lower():
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
