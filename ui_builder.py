from constants import COLORS

class UIBuilder:

    # =========================
    # نافذة البداية
    # =========================
    @staticmethod
    def start_card():
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": COLORS["background"],
                "paddingAll": "24px",
                "contents": [
                    {
                        "type": "text",
                        "text": "بوت الحوت",
                        "size": "xxl",
                        "weight": "bold",
                        "color": COLORS["primary"],
                        "align": "center"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": COLORS["card_bg"],
                "paddingAll": "24px",
                "spacing": "lg",
                "contents": [
                    {
                        "type": "text",
                        "text": "منصة ألعاب ترفيهية بدون تسجيل",
                        "color": COLORS["text_light"],
                        "align": "center",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": "أوامر اللعب: اسم اللعبة - لمح - جاوب - إيقاف",
                        "color": COLORS["text_light"],
                        "size": "sm",
                        "align": "center",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": "تم إنشاء هذا البوت بواسطة عبير الدوسري @ 2025",
                        "size": "xs",
                        "color": COLORS["text_light"],
                        "align": "center"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "backgroundColor": COLORS["background_medium"],
                "paddingAll": "16px",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "انضم", "text": "انضم"},
                        "style": "primary",
                        "color": COLORS["primary"]
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "انسحب", "text": "انسحب"},
                        "style": "secondary"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "مساعدة", "text": "مساعدة"},
                        "style": "secondary"
                    }
                ]
            }
        }

    # =========================
    # نافذة المساعدة
    # =========================
    @staticmethod
    def help_card():
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": COLORS["background"],
                "paddingAll": "24px",
                "contents": [
                    {
                        "type": "text",
                        "text": "مساعدة",
                        "size": "xxl",
                        "weight": "bold",
                        "color": COLORS["primary"],
                        "align": "center"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": COLORS["card_bg"],
                "paddingAll": "24px",
                "spacing": "md",
                "contents": [
                    {"type": "text", "text": "الألعاب تعمل بدون تسجيل", "color": COLORS["text_light"]},
                    {"type": "text", "text": "لمح للحصول على تلميح", "color": COLORS["text_light"]},
                    {"type": "text", "text": "جاوب لإرسال الإجابة", "color": COLORS["text_light"]},
                    {"type": "text", "text": "إيقاف لإنهاء اللعبة الحالية", "color": COLORS["text_light"]},
                    {"type": "separator"},
                    {
                        "type": "text",
                        "text": "تم إنشاء هذا البوت بواسطة عبير الدوسري @ 2025",
                        "size": "xs",
                        "color": COLORS["text_light"],
                        "align": "center"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "backgroundColor": COLORS["background_medium"],
                "paddingAll": "16px",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "انضم", "text": "انضم"},
                        "style": "primary",
                        "color": COLORS["primary"]
                    }
                ]
            }
        }

    # =========================
    # نافذة اللعب الموحدة
    # =========================
    @staticmethod
    def game_play_card(game_name, question, progress_ratio, vibration=False, win_flash=False):
        bar_width = int(progress_ratio * 100)

        effect_color = COLORS["success"] if win_flash else COLORS["primary"]
        border_color = COLORS["warning"] if vibration else COLORS["border"]

        return {
            "type": "bubble",
            "size": "mega",
            "styles": {"body": {"backgroundColor": COLORS["background"]}},
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "24px",
                "spacing": "lg",
                "contents": [
                    {
                        "type": "text",
                        "text": game_name,
                        "size": "xl",
                        "weight": "bold",
                        "color": effect_color,
                        "align": "center"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "paddingAll": "20px",
                        "backgroundColor": COLORS["background_medium"],
                        "cornerRadius": "lg",
                        "borderWidth": "2px",
                        "borderColor": border_color,
                        "contents": [
                            {
                                "type": "text",
                                "text": question,
                                "wrap": True,
                                "align": "center",
                                "size": "lg",
                                "color": COLORS["white"]
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "height": "10px",
                        "backgroundColor": COLORS["border"],
                        "cornerRadius": "lg",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "width": f"{bar_width}%",
                                "backgroundColor": COLORS["primary"],
                                "cornerRadius": "lg",
                                "contents": []
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "backgroundColor": COLORS["background_medium"],
                "paddingAll": "16px",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "لمح", "text": "لمح"},
                        "style": "secondary"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "جاوب", "text": "جاوب"},
                        "style": "primary",
                        "color": COLORS["primary"]
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "إيقاف", "text": "إيقاف"},
                        "style": "secondary"
                    }
                ]
            }
        }
