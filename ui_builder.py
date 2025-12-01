"""
UI Builder - واجهات احترافية بوت الحوت
==========================================
"""
from constants import COLORS

class UIBuilder:
    """بناء واجهات احترافية"""
    
    @staticmethod
    def welcome_card(display_name):
        """بطاقة الترحيب - تصميم بوت الحوت"""
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "image",
                        "url": "https://i.imgur.com/placeholder.png",
                        "size": "xs",
                        "aspectMode": "cover",
                        "aspectRatio": "1:1",
                        "gravity": "center"
                    },
                    {
                        "type": "text",
                        "text": "بوت الحوت",
                        "weight": "bold",
                        "size": "xxl",
                        "color": COLORS['white'],
                        "align": "center",
                        "margin": "md"
                    }
                ],
                "backgroundColor": COLORS['primary'],
                "paddingAll": "24px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"مرحباً {display_name}",
                        "size": "lg",
                        "color": COLORS['text_dark'],
                        "align": "center",
                        "wrap": True,
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "منصة الألعاب التفاعلية",
                        "size": "sm",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "margin": "sm"
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
                                "text": "9 ألعاب متاحة",
                                "size": "md",
                                "color": COLORS['primary'],
                                "align": "center",
                                "weight": "bold"
                            }
                        ],
                        "margin": "lg"
                    }
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "انضم الآن", "text": "انضم"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "دليل الألعاب", "text": "مساعدة"},
                        "style": "secondary",
                        "height": "sm",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": COLORS['background'],
                "paddingAll": "16px"
            }
        }
