from games.base_game import BaseGame
import re
from typing import Dict, Any, Optional

class CompatibilityGame(BaseGame):
    """لعبة حساب نسبة التوافق"""
    
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=1)
        self.game_name = "توافق"
        self.supports_hint = False
        self.supports_reveal = False
    
    def is_valid_text(self, text: str) -> bool:
        """التحقق من ان النص اسماء فقط"""
        if re.search(r"[@#0-9A-Za-z!$%^&*()_+=\[\]{};:'\"\\|,.<>/?~`]", text):
            return False
        return True
    
    def parse_names(self, text: str) -> tuple:
        """معالجة الاسماء من النص"""
        text = ' '.join(text.split())
        
        if ' و ' in text:
            parts = text.split(' و ', 1)
            name1 = parts[0].strip()
            name2 = parts[1].strip() if len(parts) > 1 else ""
            return (name1, name2) if name1 and name2 else (None, None)
        
        words = text.split()
        if 'و' in words:
            idx = words.index('و')
            name1 = ' '.join(words[:idx]).strip()
            name2 = ' '.join(words[idx+1:]).strip()
            return (name1, name2) if name1 and name2 else (None, None)
        
        return (None, None)
    
    def calculate_compatibility(self, name1: str, name2: str) -> int:
        """حساب نسبة التوافق"""
        n1 = self.normalize_text(name1)
        n2 = self.normalize_text(name2)
        
        names = sorted([n1, n2])
        combined = ''.join(names)
        
        seed = sum(ord(c) * (i + 1) for i, c in enumerate(combined))
        percentage = (seed % 81) + 20
        
        return percentage
    
    def get_compatibility_message(self, percentage: int) -> str:
        """رسالة التوافق"""
        if percentage >= 90:
            return "توافق عالي جدا"
        elif percentage >= 75:
            return "توافق عالي"
        elif percentage >= 60:
            return "توافق جيد"
        elif percentage >= 45:
            return "توافق متوسط"
        else:
            return "توافق منخفض"
    
    def start_game(self):
        """بدء اللعبة"""
        self.game_active = True
        return self.get_question()
    
    def get_question(self):
        """الحصول على السؤال"""
        return self.build_text_message(
            "ادخل اسمين بينهما (و)\nمثال: الحوت و عبير"
        )
    
    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        if not self.game_active:
            return None
        
        text = user_answer.strip()
        name1, name2 = self.parse_names(text)
        
        if not name1 or not name2:
            return {
                'response': self.build_text_message(
                    "الصيغة غير صحيحة\n\naكتب: اسم و اسم\nمثال: الحوت و عبير"
                ),
                'points': 0
            }
        
        if not self.is_valid_text(name1) or not self.is_valid_text(name2):
            return {
                'response': self.build_text_message(
                    "غير مسموح بالرموز او الارقام\n\nاكتب اسمين نصيين فقط"
                ),
                'points': 0
            }
        
        percentage = self.calculate_compatibility(name1, name2)
        message_text = self.get_compatibility_message(percentage)
        
        result_text = f"نتيجة التوافق\n\n{name1} و {name2}\n\nالنسبة: {percentage}%\n{message_text}\n\nملاحظة: نفس النتيجة لو كتبت\n{name2} و {name1}"
        
        self.game_active = False
        
        return {
            'response': self.build_text_message(result_text),
            'points': 0,
            'game_over': True
        }
