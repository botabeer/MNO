from linebot.models import TextSendMessage, FlexSendMessage
import hashlib
from constants import COLORS

class CompatibilityGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.waiting_for_names = True

    def start_game(self):
        return FlexSendMessage(
            alt_text="نسبة التوافق",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "نسبة التوافق", "weight": "bold", "size": "xl", "color": COLORS['white']}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "10px"},
                        {"type": "box", "layout": "vertical", "contents": [
                            {"type": "text", "text": "اكتب اسمين بهذا الشكل:", "size": "md", "color": COLORS['text_dark'], "wrap": True},
                            {"type": "text", "text": "اسم و اسم", "size": "lg", "color": COLORS['primary'], "margin": "md", "weight": "bold", "align": "center"},
                            {"type": "text", "text": "مثال: محمد و فاطمة", "size": "sm", "color": COLORS['text_light'], "margin": "sm"},
                            {"type": "text", "text": "مثال: وداد و أحمد", "size": "sm", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": "مثال: أبو سعد و أم سعد", "size": "sm", "color": COLORS['text_light'], "margin": "xs"}
                        ], "margin": "lg", "spacing": "sm"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

    def parse_names(self, text):
        """استخراج الاسمين من النص بذكاء"""
        text = text.strip()
        
        # البحث عن " و " كفاصل
        if " و " in text:
            parts = text.split(" و ")
            if len(parts) >= 2:
                name1 = parts[0].strip()
                name2 = " ".join(parts[1:]).strip()
                return name1, name2
        
        # إذا لم يجد " و "، حاول البحث عن "و" محاطة بمسافات
        if " و" in text or "و " in text:
            text = text.replace(" و", " و ").replace("و ", " و ")
            text = " ".join(text.split())  # تنظيف المسافات المتعددة
            if " و " in text:
                parts = text.split(" و ")
                if len(parts) >= 2:
                    name1 = parts[0].strip()
                    name2 = " ".join(parts[1:]).strip()
                    return name1, name2
        
        return None, None

    def calculate_compatibility(self, name1, name2):
        """حساب نسبة التوافق بشكل ثابت لنفس الاسمين"""
        # ترتيب الأسماء أبجدياً لضمان نفس النتيجة سواء كان (أ و ب) أو (ب و أ)
        names = sorted([name1.lower().strip(), name2.lower().strip()])
        combined = "".join(names)
        
        # استخدام hash للحصول على نتيجة ثابتة
        hash_value = int(hashlib.md5(combined.encode()).hexdigest(), 16)
        
        # توليد نسبة بين 50 و 100
        compatibility = 50 + (hash_value % 51)
        
        return compatibility

    def get_compatibility_message(self, compatibility):
        """الحصول على رسالة مناسبة للنسبة"""
        if compatibility >= 90:
            return "توافق مثالي"
        elif compatibility >= 75:
            return "توافق ممتاز"
        elif compatibility >= 60:
            return "توافق جيد"
        else:
            return "توافق متوسط"

    def check_answer(self, answer, user_id, display_name):
        if not self.waiting_for_names:
            return None

        name1, name2 = self.parse_names(answer)

        if not name1 or not name2:
            return {
                'response': TextSendMessage(text="يرجى كتابة اسمين بالشكل الصحيح:\nاسم و اسم\n\nمثال: محمد و فاطمة"),
                'points': 0,
                'correct': False,
                'won': False,
                'game_over': False
            }

        # حساب نسبة التوافق
        compatibility = self.calculate_compatibility(name1, name2)
        message = self.get_compatibility_message(compatibility)

        self.waiting_for_names = False

        result_card = FlexSendMessage(
            alt_text="نتيجة التوافق",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "نسبة التوافق", "weight": "bold", "size": "xl", "color": COLORS['white']}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "10px"},
                        {"type": "box", "layout": "vertical", "contents": [
                            {"type": "text", "text": f"{name1} و {name2}", "size": "lg", "color": COLORS['text_dark'], "align": "center", "wrap": True},
                            {"type": "text", "text": f"{compatibility}%", "size": "5xl", "color": COLORS['primary'], "weight": "bold", "align": "center", "margin": "lg"},
                            {"type": "text", "text": message, "size": "lg", "color": COLORS['text_dark'], "align": "center", "margin": "md"}
                        ], "margin": "lg", "spacing": "sm"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "button", "action": {"type": "message", "label": "إعادة", "text": "توافق"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "lg"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

        return {'response': result_card, 'points': 0, 'correct': False, 'won': False, 'game_over': True}
    
    def next_question(self):
        return None
