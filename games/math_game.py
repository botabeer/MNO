"""
لعبة الرياضيات المحدثة - Math Game
عمليات حسابية متنوعة بصعوبة متدرجة
"""

from base_game import BaseGame
from linebot.models import TextSendMessage
import random


class MathGame(BaseGame):
    """لعبة الرياضيات - عمليات حسابية"""
    
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, 'رياضيات')
        self.operations = ['+', '-', '×', '÷']
        self.difficulty_levels = {
            1: {'min': 1, 'max': 10},      # سهل
            2: {'min': 10, 'max': 50},     # متوسط
            3: {'min': 20, 'max': 100},    # صعب
            4: {'min': 50, 'max': 200},    # صعب جداً
            5: {'min': 100, 'max': 500}    # خبير
        }
    
    def _generate_question(self):
        """توليد سؤال رياضيات جديد"""
        # تحديد مستوى الصعوبة بناءً على رقم السؤال
        difficulty = min(self.current_question, 5)
        range_vals = self.difficulty_levels[difficulty]
        
        # اختيار عملية عشوائية
        operation = random.choice(self.operations)
        
        if operation == '+':
            num1 = random.randint(range_vals['min'], range_vals['max'])
            num2 = random.randint(range_vals['min'], range_vals['max'])
            answer = num1 + num2
            question = f"{num1} + {num2}"
        
        elif operation == '-':
            num1 = random.randint(range_vals['min'], range_vals['max'])
            num2 = random.randint(range_vals['min'], num1)  # num2 أصغر من num1
            answer = num1 - num2
            question = f"{num1} - {num2}"
        
        elif operation == '×':
            # أرقام أصغر للضرب
            num1 = random.randint(2, min(20, range_vals['max'] // 10))
            num2 = random.randint(2, min(20, range_vals['max'] // 10))
            answer = num1 * num2
            question = f"{num1} × {num2}"
        
        else:  # ÷
            # إنشاء قسمة بدون باقي
            num2 = random.randint(2, min(15, range_vals['max'] // 20))
            answer = random.randint(2, range_vals['max'] // num2)
            num1 = num2 * answer
            question = f"{num1} ÷ {num2}"
        
        self.current_answer = str(answer)
        self.current_operation = operation
        self.used_hints = False
        
        # تحديد مستوى الصعوبة بالنجوم
        stars = "⭐" * difficulty
        
        message = f"➕ سؤال {self.current_question} من {self.max_questions}\n"
        message += f"{stars} المستوى: {difficulty}\n\n"
        message += f"❓ احسب: {question} = ?\n\n"
        message += f"━━━━━━━━━━━━━━━━\n"
        message += f"💡 للتلميح: لمح | 📊 النقاط: {self.total_score}"
        
        return TextSendMessage(text=message)
    
    def _check_answer_logic(self, user_answer):
        """فحص الإجابة"""
        try:
            # إزالة المسافات وتحويل الفواصل العربية إلى نقاط
            user_answer = user_answer.strip().replace('٫', '.').replace('،', '.')
            
            # تحويل الأرقام العربية إلى إنجليزية
            arabic_to_english = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
            user_answer = user_answer.translate(arabic_to_english)
            
            # المقارنة
            return float(user_answer) == float(self.current_answer)
        except ValueError:
            return False
    
    def _get_hint(self):
        """الحصول على تلميح"""
        answer_num = int(self.current_answer)
        
        if self.current_operation == '+':
            hint = f"الناتج أكبر من {answer_num - 5}"
        elif self.current_operation == '-':
            hint = f"الناتج بين {max(0, answer_num - 3)} و {answer_num + 3}"
        elif self.current_operation == '×':
            hint = f"الناتج {'زوجي' if answer_num % 2 == 0 else 'فردي'}"
        else:  # ÷
            hint = f"الناتج عدد {'صحيح' if float(self.current_answer).is_integer() else 'عشري'}"
        
        return hint


# مثال على الاستخدام:
"""
from linebot import LineBotApi

line_bot_api = LineBotApi('YOUR_TOKEN')
game = MathGame(line_bot_api)

# بدء اللعبة - سيبدأ من مستوى سهل ويزيد تدريجياً
start_message = game.start_game()

# فحص إجابات
result1 = game.check_answer("15", "user123", "أحمد")  # سؤال 1
result2 = game.check_answer("42", "user123", "أحمد")  # سؤال 2
# ... حتى 5 أسئلة

# بعد السؤال الخامس، سيظهر نافذة الفوز تلقائياً
"""
