"""
UI Builder - بناء واجهات Flex Message المحسنة
==============================================
"""

from constants import COLORS

class UIBuilder:
    """بناء واجهات احترافية بتصميم أنيق"""
    
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
                        "text": "منصة الألعاب التفاعلية",
                        "weight": "bold",
                        "size": "xl",
                        "color": COLORS['white'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": f"مرحباً {display_name}",
                        "size": "md",
                        "color": COLORS['white'],
                        "align": "center",
                        "margin": "sm"
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
                        "text": "للبدء في اللعب",
                        "size": "md",
                        "weight": "bold",
                        "color": COLORS['text_dark']
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
                            UIBuilder._step_box("1", "اضغط على زر انضم للتسجيل"),
                            UIBuilder._step_box("2", "اختر لعبتك المفضلة"),
                            UIBuilder._step_box("3", "اجمع النقاط وتصدر القائمة")
                        ],
                        "spacing": "sm",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "الألعاب المتاحة",
                                "size": "sm",
                                "weight": "bold",
                                "color": COLORS['text_dark'],
                                "margin": "lg"
                            },
                            {
                                "type": "text",
                                "text": "أغنية - لعبة - سلسلة - أسرع - ضد\nتكوين - اختلاف - توافق - مافيا",
                                "size": "xs",
                                "color": COLORS['text_light'],
                                "wrap": True,
                                "margin": "sm"
                            }
                        ]
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "20px",
                "spacing": "none"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
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
                        "spacing": "sm"
                    }
                ],
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
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "✓",
                                "size": "4xl",
                                "weight": "bold",
                                "color": COLORS['primary'],
                                "align": "center"
                            }
                        ],
                        "backgroundColor": COLORS['light'],
                        "cornerRadius": "full",
                        "width": "80px",
                        "height": "80px",
                        "alignItems": "center",
                        "justifyContent": "center"
                    },
                    {
                        "type": "text",
                        "text": "تم التسجيل بنجاح",
                        "size": "xl",
                        "weight": "bold",
                        "color": COLORS['primary'],
                        "align": "center",
                        "margin": "xl"
                    },
                    {
                        "type": "text",
                        "text": display_name,
                        "size": "lg",
                        "color": COLORS['text_dark'],
                        "align": "center",
                        "margin": "sm"
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": COLORS['border']
                    },
                    {
                        "type": "text",
                        "text": "يمكنك الآن اللعب وجمع النقاط",
                        "size": "sm",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "wrap": True,
                        "margin": "xl"
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "28px",
                "alignItems": "center"
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
                        "color": COLORS['white'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": display_name,
                        "size": "sm",
                        "color": COLORS['white'],
                        "align": "center",
                        "margin": "sm"
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
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": str(stats['total_points']),
                                "size": "4xl",
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
                        "paddingAll": "16px"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": COLORS['border']
                    },
                    UIBuilder._stat_row("الألعاب", str(stats['games_played'])),
                    UIBuilder._stat_row("الفوز", str(stats['wins'])),
                    UIBuilder._stat_row("معدل الفوز", f"{win_rate:.0f}%")
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "20px",
                "spacing": "md"
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
            bg_color = COLORS['primary'] if i == 1 else COLORS['secondary'] if i == 2 else COLORS['text_dark'] if i == 3 else COLORS['light']
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
                        "weight": "bold",
                        "align": "center"
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
                        "color": COLORS['white'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "أفضل اللاعبين",
                        "size": "sm",
                        "color": COLORS['white'],
                        "align": "center",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": COLORS['primary'],
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
                    ]),
                    {"type": "separator", "margin": "lg", "color": COLORS['border']},
                    UIBuilder._help_section("الأوامر النصية", [
                        ("سؤال", "سؤال عشوائي"),
                        ("تحدي", "تحدي عشوائي"),
                        ("اعتراف", "اعتراف عشوائي"),
                        ("منشن", "منشن عشوائي")
                    ])
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "20px",
                "spacing": "none"
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
    def game_winner_card(winner_name, total_score, game_type, correct=0, total=5):
        """بطاقة الفائز"""
        percentage = (correct / total * 100) if total > 0 else 0
        
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
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "الإجابات الصحيحة",
                                "size": "xs",
                                "color": COLORS['text_light'],
                                "flex": 3
                            },
                            {
                                "type": "text",
                                "text": f"{correct}/{total}",
                                "size": "sm",
                                "color": COLORS['text_dark'],
                                "flex": 1,
                                "align": "end",
                                "weight": "bold"
                            }
                        ],
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "نسبة النجاح",
                                "size": "xs",
                                "color": COLORS['text_light'],
                                "flex": 3
                            },
                            {
                                "type": "text",
                                "text": f"{percentage:.0f}%",
                                "size": "sm",
                                "color": COLORS['text_dark'],
                                "flex": 1,
                                "align": "end",
                                "weight": "bold"
                            }
                        ],
                        "margin": "sm"
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
                        "action": {"type": "message", "label": "لعبة جديدة", "text": game_type},
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
    def _step_box(number, text):
        """صندوق خطوة"""
        return {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": number,
                    "size": "sm",
                    "color": COLORS['primary'],
                    "flex": 0,
                    "weight": "bold"
                },
                {
                    "type": "text",
                    "text": text,
                    "size": "sm",
                    "color": COLORS['text_dark'],
                    "flex": 1,
                    "margin": "md",
                    "wrap": True
                }
            ],
            "spacing": "sm"
        }
    
    @staticmethod
    def _stat_row(label, value):
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
                    "size": "md",
                    "color": COLORS['text_dark'],
                    "flex": 3,
                    "align": "end",
                    "weight": "bold"
                }
            ]
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
