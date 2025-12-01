"""
UI Builder - بناء واجهات Flex Message
=====================================
"""

from constants import COLORS

class UIBuilder:
    """بناء واجهات احترافية"""
    
    @staticmethod
    def welcome_card(display_name):
        """بطاقة الترحيب"""
        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "مرحباً بك",
                        "weight": "bold",
                        "size": "xl",
                        "color": COLORS['primary'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": display_name,
                        "size": "md",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "للبدء اضغط على زر انضم",
                        "size": "sm",
                        "color": COLORS['text_dark'],
                        "align": "center",
                        "wrap": True
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": COLORS['border']
                    },
                    {
                        "type": "text",
                        "text": "الألعاب المتاحة",
                        "weight": "bold",
                        "size": "md",
                        "color": COLORS['text_dark'],
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": "أغنية، لعبة، سلسلة، أسرع، ضد، تكوين، اختلاف، توافق، مافيا",
                        "size": "xs",
                        "color": COLORS['text_light'],
                        "wrap": True,
                        "margin": "sm"
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "20px"
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "انضم", "text": "انضم"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "مساعدة", "text": "مساعدة"},
                        "style": "secondary",
                        "height": "sm"
                    }
                ],
                "spacing": "sm",
                "backgroundColor": COLORS['background'],
                "paddingAll": "16px"
            }
        }
    
    @staticmethod
    def registration_success(display_name):
        """بطاقة نجاح التسجيل"""
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "تم التسجيل بنجاح",
                        "size": "xl",
                        "weight": "bold",
                        "color": COLORS['primary'],
                        "align": "center"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": COLORS['border']
                    },
                    {
                        "type": "text",
                        "text": display_name,
                        "size": "lg",
                        "weight": "bold",
                        "color": COLORS['text_dark'],
                        "align": "center",
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": "يمكنك الآن اللعب وجمع النقاط",
                        "size": "sm",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "wrap": True,
                        "margin": "md"
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "24px"
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "ابدأ اللعب", "text": "أغنية"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm"
                    }
                ],
                "backgroundColor": COLORS['background'],
                "paddingAll": "16px"
            }
        }
    
    @staticmethod
    def stats_card(display_name, stats):
        """بطاقة الإحصائيات"""
        if not stats:
            return UIBuilder._empty_stats(display_name)
        
        win_rate = (stats['wins'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0
        
        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "إحصائياتك",
                        "weight": "bold",
                        "size": "xl",
                        "color": COLORS['primary'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": display_name,
                        "size": "sm",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    UIBuilder._stat_row("النقاط", str(stats['total_points']), True),
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    UIBuilder._stat_row("الألعاب", str(stats['games_played'])),
                    UIBuilder._stat_row("الفوز", str(stats['wins'])),
                    UIBuilder._stat_row("معدل الفوز", f"{win_rate:.0f}%")
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "20px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "الصدارة", "text": "الصدارة"},
                        "style": "secondary",
                        "height": "sm"
                    }
                ],
                "backgroundColor": COLORS['background'],
                "paddingAll": "12px"
            }
        }
    
    @staticmethod
    def leaderboard_card(leaders):
        """لوحة الصدارة"""
        if not leaders:
            return UIBuilder._empty_leaderboard()
        
        player_items = []
        for i, leader in enumerate(leaders, 1):
            bg_color = COLORS['secondary'] if i <= 3 else COLORS['light']
            text_color = COLORS['white'] if i <= 3 else COLORS['text_dark']
            
            player_items.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": str(i),
                        "size": "sm",
                        "color": text_color,
                        "flex": 0,
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": leader['display_name'],
                        "size": "sm",
                        "color": text_color,
                        "flex": 3,
                        "margin": "md",
                        "weight": "bold" if i <= 3 else "regular",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": str(leader['total_points']),
                        "size": "sm",
                        "color": text_color,
                        "flex": 1,
                        "align": "end",
                        "weight": "bold" if i <= 3 else "regular"
                    }
                ],
                "backgroundColor": bg_color,
                "cornerRadius": "md",
                "paddingAll": "12px",
                "spacing": "md",
                "margin": "xs" if i > 1 else "none"
            })
        
        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "لوحة الصدارة",
                        "weight": "bold",
                        "size": "xl",
                        "color": COLORS['primary'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "أفضل اللاعبين",
                        "size": "sm",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": player_items,
                "backgroundColor": COLORS['white'],
                "paddingAll": "20px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "نقاطي", "text": "نقاطي"},
                        "style": "secondary",
                        "height": "sm"
                    }
                ],
                "backgroundColor": COLORS['background'],
                "paddingAll": "12px"
            }
        }
    
    @staticmethod
    def help_card():
        """بطاقة المساعدة"""
        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "دليل الاستخدام",
                        "weight": "bold",
                        "size": "xl",
                        "color": COLORS['primary'],
                        "align": "center"
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    UIBuilder._help_section("الأوامر الأساسية", [
                        ("انضم", "التسجيل في البوت"),
                        ("انسحب", "إلغاء التسجيل"),
                        ("نقاطي", "عرض إحصائياتك"),
                        ("الصدارة", "أفضل اللاعبين"),
                        ("إيقاف", "إنهاء اللعبة")
                    ]),
                    {"type": "separator", "margin": "lg", "color": COLORS['border']},
                    UIBuilder._help_section("أثناء اللعب", [
                        ("لمح", "الحصول على تلميح"),
                        ("جاوب", "عرض الإجابة")
                    ])
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "20px"
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "انضم", "text": "انضم"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "نقاطي", "text": "نقاطي"},
                        "style": "secondary",
                        "height": "sm"
                    }
                ],
                "spacing": "sm",
                "backgroundColor": COLORS['background'],
                "paddingAll": "16px"
            }
        }
    
    @staticmethod
    def game_winner_card(winner_name, total_score, game_type):
        """بطاقة الفائز"""
        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "انتهت اللعبة",
                        "weight": "bold",
                        "size": "xl",
                        "color": COLORS['white'],
                        "align": "center"
                    }
                ],
                "backgroundColor": COLORS['primary'],
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "الفائز",
                        "size": "sm",
                        "color": COLORS['text_light'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": winner_name,
                        "size": "xxl",
                        "weight": "bold",
                        "color": COLORS['primary'],
                        "align": "center",
                        "margin": "sm",
                        "wrap": True
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": str(total_score),
                                "size": "3xl",
                                "weight": "bold",
                                "color": COLORS['primary'],
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "نقطة",
                                "size": "xs",
                                "color": COLORS['text_light'],
                                "align": "center",
                                "margin": "xs"
                            }
                        ],
                        "backgroundColor": COLORS['light'],
                        "cornerRadius": "md",
                        "paddingAll": "16px",
                        "margin": "lg"
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "24px"
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "لعب مرة أخرى", "text": game_type},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "الصدارة", "text": "الصدارة"},
                        "style": "secondary",
                        "height": "sm"
                    }
                ],
                "spacing": "sm",
                "backgroundColor": COLORS['background'],
                "paddingAll": "16px"
            }
        }
    
    # Helper Methods
    
    @staticmethod
    def _stat_row(label, value, highlight=False):
        """صف إحصائية"""
        return {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": label,
                    "size": "sm",
                    "color": COLORS['text_light'],
                    "flex": 2
                },
                {
                    "type": "text",
                    "text": value,
                    "size": "xl" if highlight else "md",
                    "color": COLORS['primary'] if highlight else COLORS['text_dark'],
                    "flex": 3,
                    "align": "end",
                    "weight": "bold"
                }
            ],
            "margin": "md" if not highlight else "none"
        }
    
    @staticmethod
    def _help_section(title, commands):
        """قسم المساعدة"""
        command_rows = []
        for cmd, desc in commands:
            command_rows.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": cmd,
                        "size": "sm",
                        "color": COLORS['primary'],
                        "flex": 2,
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": desc,
                        "size": "sm",
                        "color": COLORS['text_light'],
                        "flex": 5,
                        "wrap": True
                    }
                ],
                "spacing": "md",
                "margin": "sm" if command_rows else "md"
            })
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": title,
                    "weight": "bold",
                    "size": "md",
                    "color": COLORS['text_dark']
                },
                {
                    "type": "separator",
                    "margin": "md",
                    "color": COLORS['border']
                },
                *command_rows
            ]
        }
    
    @staticmethod
    def _empty_stats(display_name):
        """إحصائيات فارغة"""
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "إحصائياتك",
                        "size": "xl",
                        "weight": "bold",
                        "color": COLORS['primary'],
                        "align": "center"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": COLORS['border']
                    },
                    {
                        "type": "text",
                        "text": "لم تبدأ بعد",
                        "size": "md",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "margin": "xl"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "ابدأ الآن", "text": "انضم"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "margin": "xl"
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "24px"
            }
        }
    
    @staticmethod
    def _empty_leaderboard():
        """صدارة فارغة"""
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "لوحة الصدارة",
                        "size": "xl",
                        "weight": "bold",
                        "color": COLORS['primary'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "لا توجد بيانات",
                        "size": "md",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "margin": "xl"
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "24px"
            }
        }
