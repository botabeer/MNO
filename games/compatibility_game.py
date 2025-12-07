# games/compatibility_game.py - Enhanced Compatibility Game
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import hashlib
from constants import COLORS


class CompatibilityGame:
    """
    لعبة نسبة التوافق
    - بدون تسجيل
    - اكتب اسمين
    - احسب نسبة التوافق
    """

    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.waiting_for_names = True

    def start_game(self):
        """بدء اللعبة"""
        return FlexMessage(
            alt_text="نسبة التوافق",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [{
                                "type": "text",
                                "text": "نسبة التوافق",
                                "size": "xl",
                                "weight": "bold",
                                "color": COLORS['white'],
                                "align": "center"
                            }],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "16px",
                            "cornerRadius": "12px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "اكتب اسمين بهذا الشكل:",
                                    "size": "md",
                                    "color": COLORS['text_dark'],
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": "اسم و اسم",
                                    "size": "xl",
                                    "color": COLORS['primary'],
                                    "align": "center",
                                    "weight": "bold",
                                    "margin": "md"
                                }
                            ],
                            "margin": "lg"
                        },
                        {
                            "type": "separator",
                            "margin": "lg",
                            "color": COLORS['border']
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "size": "xs",
                                    "color": COLORS['text_light'],
                                    "weight": "bold"
                                },
                                {
                                    "type": "text",
                                    "size": "xs",
                                    "color": COLORS['text_light'],
                                    "wrap": True,
                                    "margin": "xs"
                                }
                            ],
                            "margin": "md"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            })
        )

    def parse_names(self, text: str):
        """استخراج الاسمين من النص"""
        text = text.strip()
        
        # Try different separators
        if " و " in text:
            parts = text.split(" و ")
            if len(parts) >= 2:
                return parts[0].strip(), " ".join(parts[1:]).strip()
        
        # Try without spaces
        text = text.replace(" و", " و ").replace("و ", " و ")
        if " و " in text:
            parts = text.split(" و ")
            if len(parts) >= 2:
                return parts[0].strip(), " ".join(parts[1:]).strip()
        
        return None, None

    def calculate_compatibility(self, name1: str, name2: str) -> int:
        """حساب نسبة التوافق"""
        # Sort names for consistency
        names = sorted([name1.lower().strip(), name2.lower().strip()])
        combined = "".join(names)
        
        # Use hash for pseudo-random but consistent result
        hash_value = int(hashlib.sha256(combined.encode()).hexdigest(), 16)
        compatibility = 50 + (hash_value % 51)  # Between 50-100
        
        return compatibility

    def get_compatibility_message(self, compatibility: int) -> str:
        """رسالة التوافق"""
        if compatibility >= 90:
            return "توافق مثالي"
        elif compatibility >= 75:
            return "توافق ممتاز"
        elif compatibility >= 60:
            return "توافق جيد"
        else:
            return "توافق متوسط"

    def get_compatibility_color(self, compatibility: int) -> str:
        """لون التوافق"""
        if compatibility >= 90:
            return "#E91E63"  # Pink
        elif compatibility >= 75:
            return "#9C27B0"  # Purple
        elif compatibility >= 60:
            return "#3F51B5"  # Indigo
        else:
            return COLORS['text_light']

    def get_extra_text(self, compatibility: int) -> str:
        """نص إضافي"""
        if compatibility >= 90:
            return "علاقة رائعة ومميزة جداً"
        elif compatibility >= 75:
            return "علاقة قوية ومتينة"
        elif compatibility >= 60:
            return "علاقة جيدة ومستقرة"
        else:
            return "علاقة تحتاج لبعض الجهد"

    def check_answer(self, answer: str, user_id: str, display_name: str):
        """فحص الإجابة"""
        if not self.waiting_for_names:
            return None

        name1, name2 = self.parse_names(answer)
        
        if not name1 or not name2:
            return {
                'response': TextMessage(
                    text="يرجى كتابة اسمين بالشكل الصحيح:\n\nاسم و اسم\n\nمثال: الحوت و عبير"
                ),
                'points': 0,
                'correct': False
            }

        # Calculate compatibility
        compatibility = self.calculate_compatibility(name1, name2)
        message = self.get_compatibility_message(compatibility)
        comp_color = self.get_compatibility_color(compatibility)
        extra_text = self.get_extra_text(compatibility)

        self.waiting_for_names = False

        # Create result card
        result = FlexMessage(
            alt_text="نتيجة التوافق",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [{
                                "type": "text",
                                "text": "نتيجة التوافق",
                                "weight": "bold",
                                "size": "xl",
                                "color": COLORS['white'],
                                "align": "center"
                            }],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "12px",
                            "cornerRadius": "8px"
                        },
                        {
                            "type": "text",
                            "text": f"{name1} و {name2}",
                            "size": "lg",
                            "weight": "bold",
                            "align": "center",
                            "color": COLORS['text_dark'],
                            "margin": "lg",
                            "wrap": True
                        },
                        {
                            "type": "separator",
                            "margin": "md",
                            "color": COLORS['border']
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"{compatibility}%",
                                    "size": "5xl",
                                    "weight": "bold",
                                    "align": "center",
                                    "color": comp_color
                                },
                                {
                                    "type": "text",
                                    "text": message,
                                    "size": "md",
                                    "align": "center",
                                    "color": comp_color,
                                    "margin": "sm",
                                    "weight": "bold"
                                },
                                {
                                    "type": "text",
                                    "text": extra_text,
                                    "size": "sm",
                                    "align": "center",
                                    "color": COLORS['text_light'],
                                    "wrap": True,
                                    "margin": "md"
                                }
                            ],
                            "margin": "md"
                        },
                        {
                            "type": "separator",
                            "margin": "md",
                            "color": COLORS['border']
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "إعادة",
                                        "text": "توافق"
                                    },
                                    "style": "primary",
                                    "color": COLORS['primary'],
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "البداية",
                                        "text": "بداية"
                                    },
                                    "style": "secondary",
                                    "height": "sm"
                                }
                            ],
                            "spacing": "sm",
                            "margin": "md"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "16px"
                }
            })
        )

        return {
            'response': result,
            'points': 0,
            'correct': False,
            'game_over': True
        }
