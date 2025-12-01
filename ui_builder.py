from constants import COLORS

class UIBuilder:

    @staticmethod
    def welcome_card(display_name):
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "xl", "color": COLORS['white']}
                        ],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "10px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": f"مرحباً {display_name}", "size": "lg", "color": COLORS['text_dark'], "margin": "md"},
                            {"type": "text", "text": "منصة ألعاب ترفيهية", "size": "sm", "color": COLORS['text_light'], "margin": "sm"}
                        ],
                        "margin": "lg"
                    }
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }

    @staticmethod
    def help_card():
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "المساعدة", "weight": "bold", "size": "xl", "color": COLORS['white']}
                        ],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "10px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "الأوامر المتاحة", "size": "md", "color": COLORS['text_dark'], "margin": "md"},
                            {"type": "text", "text": "لمح - تلميح", "size": "sm", "color": COLORS['text_light'], "margin": "sm"},
                            {"type": "text", "text": "جاوب - الإجابة", "size": "sm", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": "إيقاف - إنهاء اللعبة", "size": "sm", "color": COLORS['text_light'], "margin": "xs"}
                        ],
                        "margin": "lg"
                    }
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }

    @staticmethod
    def registration_success(display_name):
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "تم التسجيل", "weight": "bold", "size": "xl", "color": COLORS['white']}
                        ],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "10px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": f"مرحباً {display_name}", "size": "lg", "color": COLORS['text_dark'], "margin": "md"}
                        ],
                        "margin": "lg"
                    }
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }

    @staticmethod
    def stats_card(display_name, stats):
        if not stats:
            stats = {'total_points': 0, 'games_played': 0, 'wins': 0}
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "إحصائياتك", "weight": "bold", "size": "xl", "color": COLORS['white']}
                        ],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "10px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": display_name, "size": "lg", "color": COLORS['text_dark'], "margin": "md"},
                            {"type": "text", "text": f"النقاط: {stats['total_points']}", "size": "md", "color": COLORS['text_light'], "margin": "sm"},
                            {"type": "text", "text": f"الألعاب: {stats['games_played']}", "size": "md", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": f"الفوز: {stats['wins']}", "size": "md", "color": COLORS['text_light'], "margin": "xs"}
                        ],
                        "margin": "lg"
                    }
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }

    @staticmethod
    def leaderboard_card(leaders):
        leader_contents = [
            {"type": "text", "text": f"{i+1}. {l['display_name']} - {l['total_points']} نقطة", "size": "sm", "color": COLORS['text_light'], "margin": "xs"}
            for i, l in enumerate(leaders)
        ]
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "لوحة الصدارة", "weight": "bold", "size": "xl", "color": COLORS['white']}
                        ],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "10px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": leader_contents,
                        "margin": "lg"
                    }
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
