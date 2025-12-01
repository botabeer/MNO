from constants import COLORS

class UIBuilder:
    """بناء واجهات احترافية لبوت الحوت"""

    @staticmethod
    def welcome_card(display_name):
        """نافذة البداية"""
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "بوت الحوت",
                        "weight": "bold",
                        "size": "xxl",
                        "color": COLORS['white'],
                        "align": "center"
                    }
                ],
                "backgroundColor": COLORS['background'],
                "paddingAll": "24px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"مرحباً {display_name}",
                        "color": COLORS['text_dark'],
                        "size": "lg",
                        "align": "center",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": "ألعاب ترفيهية بدون تسجيل",
                        "size": "sm",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": COLORS['border']
                    },
                    {
                        "type": "text",
                        "text": "الأوامر المتاحة",
                        "size": "md",
                        "weight": "bold",
                        "color": COLORS['primary'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "سؤال - تحدي - اعتراف - منشن",
                        "size": "sm",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "24px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": COLORS['primary'],
                        "action": {
                            "type": "message",
                            "label": "انضم",
                            "text": "انضم"
                        }
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "margin": "md",
                        "action": {
                            "type": "message",
                            "label": "مساعدة",
                            "text": "مساعدة"
                        }
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "margin": "md",
                        "action": {
                            "type": "message",
                            "label": "انسحب",
                            "text": "انسحب"
                        }
                    }
                ],
                "backgroundColor": COLORS['background_medium'],
                "paddingAll": "20px"
            }
        }

    @staticmethod
    def help_card():
        """نافذة المساعدة"""
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "مساعدة",
                        "weight": "bold",
                        "size": "xxl",
                        "color": COLORS['white'],
                        "align": "center"
                    }
                ],
                "backgroundColor": COLORS['background'],
                "paddingAll": "24px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    UIBuilder._help_item("بداية", "إظهار شاشة البداية"),
                    UIBuilder._help_item("انضم", "الدخول إلى الألعاب"),
                    UIBuilder._help_item("انسحب", "الخروج من اللعبة"),
                    UIBuilder._help_item("سؤال", "سؤال عشوائي"),
                    UIBuilder._help_item("تحدي", "تحدي عشوائي"),
                    UIBuilder._help_item("اعتراف", "اعتراف عشوائي"),
                    UIBuilder._help_item("منشن", "اختيار عضو عشوائي")
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "24px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "العودة للبداية",
                            "text": "بداية"
                        },
                        "style": "primary",
                        "color": COLORS['primary']
                    }
                ],
                "backgroundColor": COLORS['background_medium'],
                "paddingAll": "20px"
            }
        }

    @staticmethod
    def _help_item(command, description):
        return {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": command,
                    "size": "md",
                    "color": COLORS['text_dark'],
                    "flex": 2
                },
                {
                    "type": "text",
                    "text": description,
                    "size": "sm",
                    "color": COLORS['text_light'],
                    "flex": 4,
                    "wrap": True
                }
            ],
            "spacing": "sm",
            "margin": "sm"
        }
