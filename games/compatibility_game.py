from games.base_game import BaseGame
import re
from typing import Dict, Any, Optional
from linebot.v3.messaging import FlexMessage, FlexContainer

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
        c = self.get_theme_colors()
        
        contents = [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": "حاسبة التوافق",
                    "size": "xl",
                    "weight": "bold",
                    "color": c["white"],
                    "align": "center"
                }],
                "backgroundColor": c["primary"],
                "paddingAll": "15px",
                "cornerRadius": "10px"
            },
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "text",
                "text": "ادخل اسمين بينهما (و)",
                "size": "md",
                "color": c["text"],
                "align": "center",
                "weight": "bold",
                "margin": "lg"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "مثال:", "size": "sm", "color": c["text3"]},
                    {"type": "text", "text": "الحوت و عبير", "size": "sm", "color": c["text2"], "margin": "xs"}
                ],
                "backgroundColor": c["bg"],
                "paddingAll": "12px",
                "cornerRadius": "8px",
                "margin": "md"
            }
        ]
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px",
                "backgroundColor": c["card"]
            }
        }
        
        return FlexMessage(alt_text="حاسبة التوافق", contents=FlexContainer.from_dict(bubble))
    
    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        if not self.game_active:
            return None
        
        text = user_answer.strip()
        name1, name2 = self.parse_names(text)
        
        if not name1 or not name2:
            return {
                'response': self.build_text_message("الصيغة غير صحيحة\n\nاكتب: اسم و اسم\nمثال: الحوت و عبير"),
                'points': 0
            }
        
        if not self.is_valid_text(name1) or not self.is_valid_text(name2):
            return {
                'response': self.build_text_message("غير مسموح بالرموز او الارقام\n\nاكتب اسمين نصيين فقط"),
                'points': 0
            }
        
        percentage = self.calculate_compatibility(name1, name2)
        message_text = self.get_compatibility_message(percentage)
        
        c = self.get_theme_colors()
        
        # تحديد اللون حسب النسبة
        if percentage >= 75:
            result_color = c["success"]
        elif percentage >= 45:
            result_color = c["warning"]
        else:
            result_color = c["error"]
        
        contents = [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": "نتيجة التوافق",
                    "size": "xl",
                    "weight": "bold",
                    "color": c["white"],
                    "align": "center"
                }],
                "backgroundColor": c["primary"],
                "paddingAll": "15px",
                "cornerRadius": "10px"
            },
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": name1, "size": "lg", "weight": "bold", "color": c["text"], "align": "center"},
                    {"type": "text", "text": "و", "size": "sm", "color": c["text3"], "align": "center", "margin": "xs"},
                    {"type": "text", "text": name2, "size": "lg", "weight": "bold", "color": c["text"], "align": "center", "margin": "xs"}
                ],
                "margin": "lg"
            },
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": f"{percentage}%", "size": "3xl", "weight": "bold", "color": result_color, "align": "center"},
                    {"type": "text", "text": message_text, "size": "md", "color": c["text2"], "align": "center", "margin": "sm"}
                ],
                "margin": "lg"
            },
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "ملاحظة:", "size": "xs", "color": c["text3"]},
                    {"type": "text", "text": f"نفس النتيجة لو كتبت\n{name2} و {name1}", "size": "xs", "color": c["text3"], "wrap": True, "margin": "xs"}
                ],
                "backgroundColor": c["bg"],
                "paddingAll": "10px",
                "cornerRadius": "8px",
                "margin": "md"
            },
            {"type": "separator", "margin": "md", "color": c["border"]},
            {
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "اعادة", "text": "توافق"},
                        "style": "primary",
                        "color": c["primary"],
                        "height": "sm"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "البداية", "text": "بداية"},
                        "style": "secondary",
                        "height": "sm"
                    }
                ],
                "margin": "md"
            }
        ]
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px",
                "backgroundColor": c["card"]
            }
        }
        
        self.game_active = False
        
        return {
            'response': FlexMessage(alt_text="نتيجة التوافق", contents=FlexContainer.from_dict(bubble)),
            'points': 0,
            'game_over': True
        }
