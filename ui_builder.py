"""
UI Builder - بناء واجهات Flex Message المحسنة بالألوان الجديدة
==============================================================
"""

from constants import COLORS

class UIBuilder:
    """بناء واجهات احترافية بتصميم أنيق"""
    
    @staticmethod
    def welcome_card(display_name):
        """بطاقة الترحيب"""
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "منصة الألعاب التفاعلية",
                        "weight": "bold",
                        "size": "xxl",
                        "color": COLORS['white'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": f"مرحباً {display_name}",
                        "size": "lg",
                        "color": COLORS['white'],
                        "align": "center",
                        "margin": "md"
                    }
                ],
                "backgroundColor": COLORS['primary'],
                "paddingAll": "28px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "للبدء في اللعب",
                        "size": "lg",
                        "weight": "bold",
                        "color": COLORS['text_dark'],
                        "align": "center"
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
                            UIBuilder._step_box("1", "اضغط على زر انضم للتسجيل", COLORS['primary']),
                            UIBuilder._step_box("2", "اختر لعبتك المفضلة", COLORS['secondary']),
                            UIBuilder._step_box("3", "اجمع النقاط وتصدر القائمة", COLORS['medium'])
                        ],
                        "spacing": "md",
                        "margin": "lg"
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": COLORS['border']
                    },
                    {
                        "type": "text",
                        "text": "الألعاب المتاحة",
                        "size": "md",
                        "weight": "bold",
                        "color": COLORS['text_dark'],
                        "margin": "xl"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "أغنية • لعبة • سلسلة • أسرع • ضد",
                                "size": "sm",
                                "color": COLORS['text_light'],
                                "align": "center",
                                "wrap": True
                            },
                            {
                                "type": "text",
                                "text": "تكوين • اختلاف • توافق • مافيا",
                                "size": "sm",
                                "color": COLORS['text_light'],
                                "align": "center",
                                "wrap": True,
                                "margin": "xs"
                            }
                        ],
                        "margin": "md"
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "24px",
                "spacing": "none"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "separator",
                        "color": COLORS['border']
                    },
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
                        "spacing": "sm",
                        "margin": "md"
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
            "size": "mega",
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
                                "size": "5xl",
                                "weight": "bold",
                                "color": COLORS['primary'],
                                "align": "center"
                            }
                        ],
                        "backgroundColor": COLORS['light'],
                        "cornerRadius": "full",
                        "width": "100px",
                        "height": "100px",
                        "alignItems": "center",
                        "justifyContent": "center"
                    },
                    {
                        "type": "text",
                        "text": "تم التسجيل بنجاح",
                        "size": "xxl",
                        "weight": "bold",
                        "color": COLORS['primary'],
                        "align": "center",
                        "margin": "xl"
                    },
                    {
                        "type": "text",
                        "text": display_name,
                        "size": "xl",
                        "color": COLORS['text_dark'],
                        "align": "center",
                        "margin": "md",
                        "wrap": True
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": COLORS['border']
                    },
                    {
                        "type": "text",
                        "text": "يمكنك الآن اللعب وجمع النقاط",
                        "size": "md",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "wrap": True,
                        "margin": "xl"
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "32px",
                "alignItems": "center"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "separator",
                        "color": COLORS['border']
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "ابدأ اللعب", "text": "أغنية"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm",
                        "margin": "md"
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
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "إحصائياتك",
                        "weight": "bold",
                        "size": "xxl",
                        "color": COLORS['white'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": display_name,
                        "size": "md",
                        "color": COLORS['white'],
                        "align": "center",
                        "margin": "sm",
                        "wrap": True
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
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": str(stats['total_points']),
                                "size": "5xl",
                                "weight": "bold",
                                "color": COLORS['primary'],
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "نقطة",
                                "size": "sm",
                                "color": COLORS['text_light'],
                                "align": "center",
                                "margin": "sm"
                            }
                        ],
                        "backgroundColor": COLORS['light'],
                        "cornerRadius": "lg",
                        "paddingAll": "20px"
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": COLORS['border']
                    },
                    UIBuilder._stat_row("الألعاب", str(stats['games_played']), COLORS['secondary']),
                    UIBuilder._stat_row("الفوز", str(stats['wins']), COLORS['primary']),
                    UIBuilder._stat_row("معدل الفوز", f"{win_rate:.0f}%", COLORS['medium'])
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "24px",
                "spacing": "md"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "separator",
                        "color": COLORS['border']
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "الصدارة", "text": "الصدارة"},
                        "style": "secondary",
                        "height": "sm",
                        "margin": "md"
                    }
                ],
                "backgroundColor": COLORS['background'],
                "paddingAll": "16px"
            }
        }
    
    @staticmethod
    def leaderboard_card(leaders):
        """لوحة الصدارة"""
        if not leaders:
            return UIBuilder._empty_leaderboard()
        
        player_items = []
        for i, leader in enumerate(leaders, 1):
            # تحديد اللون حسب المرتبة
            if i == 1:
                bg_color = COLORS['primary']
                text_color = COLORS['white']
            elif i == 2:
                bg_color = COLORS['secondary']
                text_color = COLORS['white']
            elif i == 3:
                bg_color = COLORS['medium']
                text_color = COLORS['white']
            else:
                bg_color = COLORS['light']
                text_color = COLORS['text_dark']
            
            player_items.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": str(i),
                        "size": "lg",
                        "color": text_color,
                        "flex": 0,
                        "weight": "bold",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": leader['display_name'],
                        "size": "md",
                        "color": text_color,
                        "flex": 4,
                        "margin": "lg",
                        "weight": "bold" if i <= 3 else "regular",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": str(leader['total_points']),
                        "size": "lg",
                        "color": text_color,
                        "flex": 1,
                        "align": "end",
                        "weight": "bold"
                    }
                ],
                "backgroundColor": bg_color,
                "cornerRadius": "lg",
                "paddingAll": "16px",
                "spacing": "md",
                "margin": "sm" if i > 1 else "none"
            })
        
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "لوحة الصدارة",
                        "weight": "bold",
                        "size": "xxl",
                        "color": COLORS['white'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "أفضل اللاعبين",
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
                "contents": player_items,
                "backgroundColor": COLORS['white'],
                "paddingAll": "20px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "separator",
                        "color": COLORS['border']
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "نقاطي", "text": "نقاطي"},
                        "style": "secondary",
                        "height": "sm",
                        "margin": "md"
                    }
                ],
                "backgroundColor": COLORS['background'],
                "paddingAll": "16px"
            }
        }
    
    @staticmethod
    def help_card():
        """بطاقة المساعدة"""
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "دليل الاستخدام",
                        "weight": "bold",
                        "size": "xxl",
                        "color": COLORS['white'],
                        "align": "center"
                    }
                ],
                "backgroundColor": COLORS['primary'],
                "paddingAll": "24px"
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
                    {"type": "separator", "margin": "xl", "color": COLORS['border']},
                    UIBuilder._help_section("أثناء اللعب", [
                        ("لمح", "الحصول على تلميح"),
                        ("جاوب", "عرض الإجابة")
                    ]),
                    {"type": "separator", "margin": "xl", "color": COLORS['border']},
                    {
                        "type": "text",
                        "text": "ملاحظة: الأوامر النصية (سؤال، تحدي، اعتراف، منشن) تعرض نصوص فقط",
                        "size": "xs",
                        "color": COLORS['medium'],
                        "align": "center",
                        "wrap": True,
                        "margin": "lg"
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "24px",
                "spacing": "none"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "separator",
                        "color": COLORS['border']
                    },
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
                                "action": {"type": "message", "label": "نقاطي", "text": "نقاطي"},
                                "style": "secondary",
                                "height": "sm"
                            }
                        ],
                        "spacing": "sm",
                        "margin": "md"
                    }
                ],
                "backgroundColor": COLORS['background'],
                "paddingAll": "16px"
            }
        }
    
    @staticmethod
    def game_winner_card(winner_name, total_score, game_type, correct=0, total=5):
        """بطاقة الفائز"""
        percentage = (correct / total * 100) if total > 0 else 0
        
        # تحديد المستوى حسب النسبة
        if percentage >= 90:
            level = "ممتاز"
            level_color = COLORS['primary']
        elif percentage >= 70:
            level = "جيد جداً"
            level_color = COLORS['secondary']
        elif percentage >= 50:
            level = "جيد"
            level_color = COLORS['medium']
        else:
            level = "مقبول"
            level_color = COLORS['text_light']
        
        return {
            "type": "bubble",
            "size": "mega",
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
                "backgroundColor": COLORS['secondary'],
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "الفائز",
                        "size": "md",
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
                                "size": "5xl",
                                "weight": "bold",
                                "color": COLORS['primary'],
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "نقطة",
                                "size": "sm",
                                "color": COLORS['text_light'],
                                "align": "center",
                                "margin": "sm"
                            }
                        ],
                        "backgroundColor": COLORS['light'],
                        "cornerRadius": "lg",
                        "paddingAll": "20px",
                        "margin": "xl"
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": COLORS['border']
                    },
                    UIBuilder._stat_row("الإجابات الصحيحة", f"{correct}/{total}", COLORS['primary']),
                    UIBuilder._stat_row("نسبة النجاح", f"{percentage:.0f}%", COLORS['secondary']),
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": level,
                                "size": "xl",
                                "weight": "bold",
                                "color": level_color,
                                "align": "center"
                            }
                        ],
                        "backgroundColor": COLORS['light'],
                        "cornerRadius": "md",
                        "paddingAll": "16px",
                        "margin": "xl"
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "24px",
                "spacing": "md"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "separator",
                        "color": COLORS['border']
                    },
                    {
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
                        "margin": "md"
                    }
                ],
                "backgroundColor": COLORS['background'],
                "paddingAll": "16px"
            }
        }
    
    # Helper Methods
    
    @staticmethod
    def _step_box(number, text, color):
        """صندوق خطوة"""
        return {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": number,
                            "size": "lg",
                            "color": COLORS['white'],
                            "weight": "bold",
                            "align": "center"
                        }
                    ],
                    "backgroundColor": color,
                    "cornerRadius": "full",
                    "width": "40px",
                    "height": "40px",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "flex": 0
                },
                {
                    "type": "text",
                    "text": text,
                    "size": "md",
                    "color": COLORS['text_dark'],
                    "flex": 1,
                    "margin": "md",
                    "wrap": True
                }
            ],
            "spacing": "md"
        }
    
    @staticmethod
    def _stat_row(label, value, color=None):
        """صف إحصائية"""
        if color is None:
            color = COLORS['text_dark']
        
        return {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": label,
                    "size": "md",
                    "color": COLORS['text_light'],
                    "flex": 3
                },
                {
                    "type": "text",
                    "text": value,
                    "size": "lg",
                    "color": color,
                    "flex": 2,
                    "align": "end",
                    "weight": "bold"
                }
            ],
            "margin": "md"
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
                        "size": "md",
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
                "margin": "md" if command_rows else "lg"
            })
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": title,
                    "weight": "bold",
                    "size": "lg",
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
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "إحصائياتك",
                        "size": "xxl",
                        "weight": "bold",
                        "color": COLORS['primary'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": display_name,
                        "size": "lg",
                        "color": COLORS['text_dark'],
                        "align": "center",
                        "margin": "sm",
                        "wrap": True
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": COLORS['border']
                    },
                    {
                        "type": "text",
                        "text": "لم تبدأ بعد",
                        "size": "lg",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "margin": "xl"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "ابدأ الآن", "text": "انضم"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "margin": "xl",
                        "height": "sm"
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "32px"
            }
        }
    
    @staticmethod
    def _empty_leaderboard():
        """صدارة فارغة"""
        return {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "لوحة الصدارة",
                        "size": "xxl",
                        "weight": "bold",
                        "color": COLORS['primary'],
                        "align": "center"
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": COLORS['border']
                    },
                    {
                        "type": "text",
                        "text": "لا توجد بيانات",
                        "size": "lg",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "margin": "xl"
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "32px"
            }
        }
