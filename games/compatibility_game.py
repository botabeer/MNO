from linebot.models import TextSendMessage
import random

class CompatibilityGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.waiting_for_names = True
        self.name1 = None
        self.name2 = None
        
    def start_game(self):
        """بدء اللعبة"""
        return TextSendMessage(text="لعبة التوافق\n\nاكتب اسمين مفصولين بمسافة\nمثال: ميش عبير")
    
    def calculate_compatibility(self, name1, name2):
        """حساب نسبة التوافق"""
        # استخدام مجموع الأحرف لتوليد نسبة ثابتة لنفس الأسماء
        combined = name1 + name2
        total = sum(ord(char) for char in combined)
        percentage = (total % 91) + 10  # نسبة من 10 إلى 100
        return min(percentage, 100)
    
    def get_compatibility_message(self, percentage):
        """الحصول على رسالة بناءً على النسبة"""
        if percentage >= 90:
            return "علاقة مثالية! توافق استثنائي"
        elif percentage >= 80:
            return "توافق ممتاز! علاقة قوية جداً"
        elif percentage >= 70:
            return "توافق جيد جداً! علاقة واعدة"
        elif percentage >= 60:
            return "توافق جيد! يمكن أن تنجح العلاقة"
        elif percentage >= 50:
            return "توافق متوسط! تحتاج بعض الجهد"
        elif percentage >= 40:
            return "توافق ضعيف! تحديات كثيرة"
        elif percentage >= 30:
            return "توافق منخفض! علاقة صعبة"
        else:
            return "توافق ضعيف جداً! غير متوافقين"
    
    def get_compatibility_bar(self, percentage):
        """رسم شريط التوافق"""
        filled = int(percentage / 10)
        empty = 10 - filled
        return "■" * filled + "□" * empty
    
    def check_answer(self, text, user_id, display_name):
        """معالجة الإدخال"""
        if not self.waiting_for_names:
            return None
        
        # تقسيم الأسماء
        names = text.strip().split()
        
        if len(names) < 2:
            return {
                'message': "يرجى كتابة اسمين مفصولين بمسافة\nمثال: أحمد فاطمة",
                'points': 0,
                'won': False,
                'game_over': False
            }
        
        # أخذ أول اسمين فقط
        self.name1 = names[0]
        self.name2 = names[1]
        
        # حساب التوافق
        percentage = self.calculate_compatibility(self.name1, self.name2)
        bar = self.get_compatibility_bar(percentage)
        message = self.get_compatibility_message(percentage)
        
        # بناء الرسالة
        result_text = f"""نتيجة التوافق

{self.name1} ❤️ {self.name2}

{bar}
{percentage}%

{message}

هذه النتيجة للترفيه فقط"""
        
        self.waiting_for_names = False
        
        return {
            'message': result_text,
            'response': TextSendMessage(text=result_text),
            'points': 0,
            'won': False,
            'game_over': True
        }
