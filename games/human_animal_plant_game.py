from linebot.models import TextSendMessage
import random
import re

class HumanAnimalPlantGame:
    def __init__(self, line_bot_api, use_ai=False, ask_ai=None):
        self.line_bot_api = line_bot_api
        self.use_ai = use_ai
        self.ask_ai = ask_ai
        self.current_letter = None
        self.answers = {}
        self.scores = {}
        
        self.letters = [
            'أ', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 
            'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 
            'ل', 'م', 'ن', 'ه', 'و', 'ي'
        ]
        
        self.valid_answers = {
            'human': ['أحمد', 'محمد', 'علي', 'فاطمة', 'عائشة', 'خديجة', 'حسن', 'حسين'],
            'animal': ['أسد', 'نمر', 'فيل', 'حصان', 'جمل', 'غزال', 'ذئب', 'كلب'],
            'plant': ['ورد', 'ياسمين', 'نخلة', 'زيتون', 'تفاح', 'موز', 'عنب', 'برتقال'],
            'country': ['مصر', 'سعودية', 'عراق', 'سوريا', 'اردن', 'لبنان', 'كويت', 'امارات']
        }
    
    def normalize_text(self, text):
        """تطبيع النص"""
        if not text:
            return ""
        text = text.strip().lower()
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '')
        text = text.replace('ة', 'ه').replace('ى', 'ي')
        text = re.sub(r'[\u064B-\u065F]', '', text)
        text = re.sub(r'\s+', '', text)
        return text
    
    def start_game(self):
        """بدء اللعبة"""
        self.current_letter = random.choice(self.letters)
        self.answers = {}
        self.scores = {}
        
        message = (
            f"▪️ لعبة إنسان حيوان نبات بلاد\n\n"
            f"الحرف: {self.current_letter}\n\n"
            f"اكتب إجاباتك بهذا الشكل:\n"
            f"إنسان: ...\n"
            f"حيوان: ...\n"
            f"نبات: ...\n"
            f"بلاد: ..."
        )
        return TextSendMessage(text=message)
    
    def check_answer(self, text, user_id, display_name):
        """فحص الإجابة"""
        if user_id in self.answers:
            return None
        
        lines = text.strip().split('\n')
        if len(lines) < 4:
            return None
        
        user_answers = {}
        categories = ['إنسان', 'حيوان', 'نبات', 'بلاد']
        categories_en = ['human', 'animal', 'plant', 'country']
        
        for line in lines:
            for i, cat in enumerate(categories):
                if cat in line or categories_en[i] in line.lower():
                    parts = line.split(':')
                    if len(parts) == 2:
                        answer = parts[1].strip()
                        if answer and answer[0] == self.current_letter:
                            user_answers[categories_en[i]] = answer
        
        if len(user_answers) < 4:
            return {
                'correct': False,
                'response': TextSendMessage(
                    text=f"▫️ يرجى تقديم إجابات لجميع الفئات بالشكل الصحيح"
                )
            }
        
        points = 0
        correct_count = 0
        
        for cat in categories_en:
            if cat in user_answers:
                answer = user_answers[cat]
                if answer[0] == self.current_letter:
                    points += 3
                    correct_count += 1
        
        self.answers[user_id] = user_answers
        
        if user_id not in self.scores:
            self.scores[user_id] = {'name': display_name, 'score': 0}
        self.scores[user_id]['score'] += points
        
        return {
            'correct': True,
            'points': points,
            'won': correct_count == 4,
            'game_over': True,
            'response': TextSendMessage(
                text=f"▪️ إجابة {display_name}\n\n"
                     f"إجابات صحيحة: {correct_count}/4\n"
                     f"+{points} نقطة"
            )
        }
