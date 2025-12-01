"""
UI Builder - واجهات ثري دي احترافية بألوان الصورة
==================================================
"""
from constants import COLORS

class UIBuilder:
    """بناء واجهات ثري دي احترافية"""
    
    @staticmethod
    def welcome_card(display_name):
        """بطاقة الترحيب - تصميم ثري دي"""
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "منصة الألعاب",
                                "weight": "bold",
                                "size": "xxl",
                                "color": COLORS['white'],
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "التفاعلية",
                                "size": "lg",
                                "color": COLORS['light'],
                                "align": "center",
                                "margin": "xs"
                            }
                        ],
                        "paddingAll": "lg"
                    }
                ],
                "background": {
                    "type": "linearGradient",
                    "angle": "135deg",
                    "startColor": COLORS['gradient_start'],
                    "endColor": COLORS['gradient_end']
                },
                "paddingAll": "none"
            },
            "hero": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"مرحباً {display_name}",
                                "size": "xl",
                                "color": COLORS['primary'],
                                "weight": "bold",
                                "align": "center"
                            }
                        ],
                        "backgroundColor": COLORS['white'],
                        "cornerRadius": "xl",
                        "paddingAll": "lg",
                        "offsetTop": "-30px",
                        "position": "relative"
                    }
                ],
                "paddingAll": "lg"
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
                                "text": "خطوات البدء",
                                "size": "md",
                                "weight": "bold",
                                "color": COLORS['text_dark']
                            },
                            {
                                "type": "separator",
                                "margin": "md",
                                "color": COLORS['border']
                            }
                        ],
                        "spacing": "sm"
                    },
                    UIBuilder._3d_step("1", "انضم للبوت", COLORS['primary']),
                    UIBuilder._3d_step("2", "اختر لعبتك", COLORS['medium']),
                    UIBuilder._3d_step("3", "اجمع النقاط", COLORS['primary_dark']),
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "9 ألعاب متاحة",
                                "size": "sm",
                                "color": COLORS['text_light'],
                                "align": "center"
                            }
                        ],
                        "margin": "xl"
                    }
                ],
                "paddingAll": "lg",
                "spacing": "md"
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
                                "action": {"type": "message", "label": "الألعاب", "text": "أغنية"},
                                "style": "secondary",
                                "height": "sm"
                            }
                        ],
                        "spacing": "sm"
                    }
                ],
                "paddingAll": "lg"
            }
        }
    
    @staticmethod
    def help_card():
        """بطاقة المساعدة - تصميم ثري دي"""
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
                "background": {
                    "type": "linearGradient",
                    "angle": "135deg",
                    "startColor": COLORS['gradient_start'],
                    "endColor": COLORS['gradient_end']
                },
                "paddingAll": "xl"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    UIBuilder._help_section("الأوامر الأساسية", [
                        ("انضم", "التسجيل في البوت"),
                        ("نقاطي", "عرض إحصائياتك"),
                        ("الصدارة", "أفضل اللاعبين"),
                        ("إيقاف", "إنهاء اللعبة")
                    ]),
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "separator",
                                "color": COLORS['border']
                            }
                        ],
                        "margin": "xl"
                    },
                    UIBuilder._help_section("أثناء اللعب", [
                        ("لمح", "الحصول على تلميح"),
                        ("جاوب", "عرض الإجابة")
                    ]),
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "separator",
                                "color": COLORS['border']
                            }
                        ],
                        "margin": "xl"
                    },
                    UIBuilder._help_section("الألعاب المتاحة", [
                        ("أغنية", "تخمين المغني"),
                        ("لعبة", "إنسان حيوان نبات"),
                        ("سلسلة", "سلسلة الكلمات"),
                        ("أسرع", "الكتابة السريعة"),
                        ("ضد", "الأضداد"),
                        ("تكوين", "تكوين الكلمات"),
                        ("اختلاف", "إيجاد الاختلافات"),
                        ("توافق", "نسبة التوافق"),
                        ("مافيا", "لعبة المافيا")
                    ]),
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "الأوامر النصية: سؤال، تحدي، اعتراف، منشن",
                                "size": "xs",
                                "color": COLORS['text_light'],
                                "align": "center",
                                "wrap": True
                            }
                        ],
                        "margin": "xl"
                    }
                ],
                "paddingAll": "lg",
                "spacing": "none"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "ابدأ الآن", "text": "انضم"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm"
                    }
                ],
                "paddingAll": "lg"
            }
        }
    
    @staticmethod
    def game_question_card(game_type, question, question_num=1, total=5):
        """بطاقة سؤال اللعبة - تصميم ثري دي"""
        progress = int((question_num / total) * 100)
        
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": game_type,
                                "weight": "bold",
                                "size": "xl",
                                "color": COLORS['white'],
                                "flex": 3
                            },
                            {
                                "type": "text",
                                "text": f"{question_num}/{total}",
                                "size": "md",
                                "color": COLORS['light'],
                                "flex": 1,
                                "align": "end"
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [],
                                "backgroundColor": COLORS['primary'],
                                "height": "4px",
                                "width": f"{progress}%"
                            }
                        ],
                        "backgroundColor": COLORS['secondary'],
                        "height": "4px",
                        "margin": "md"
                    }
                ],
                "background": {
                    "type": "linearGradient",
                    "angle": "135deg",
                    "startColor": COLORS['gradient_start'],
                    "endColor": COLORS['gradient_end']
                },
                "paddingAll": "lg"
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
                                "text": question,
                                "size": "lg",
                                "color": COLORS['text_dark'],
                                "weight": "bold",
                                "align": "center",
                                "wrap": True
                            }
                        ],
                        "backgroundColor": COLORS['light'],
                        "cornerRadius": "lg",
                        "paddingAll": "xl"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "لمح",
                                        "size": "sm",
                                        "color": COLORS['medium'],
                                        "align": "center"
                                    }
                                ],
                                "backgroundColor": COLORS['secondary'],
                                "cornerRadius": "md",
                                "paddingAll": "sm",
                                "flex": 1
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "جاوب",
                                        "size": "sm",
                                        "color": COLORS['medium'],
                                        "align": "center"
                                    }
                                ],
                                "backgroundColor": COLORS['secondary'],
                                "cornerRadius": "md",
                                "paddingAll": "sm",
                                "flex": 1
                            }
                        ],
                        "spacing": "sm",
                        "margin": "lg"
                    }
                ],
                "paddingAll": "lg",
                "spacing": "md"
            }
        }
    
    @staticmethod
    def stats_card(display_name, stats):
        """بطاقة الإحصائيات - تصميم ثري دي"""
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
                        "color": COLORS['light'],
                        "align": "center",
                        "margin": "sm",
                        "wrap": True
                    }
                ],
                "background": {
                    "type": "linearGradient",
                    "angle": "135deg",
                    "startColor": COLORS['gradient_start'],
                    "endColor": COLORS['gradient_end']
                },
                "paddingAll": "xl"
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
                        "cornerRadius": "xl",
                        "paddingAll": "xl"
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": COLORS['border']
                    },
                    UIBuilder._3d_stat_row("الألعاب", str(stats['games_played'])),
                    UIBuilder._3d_stat_row("الفوز", str(stats['wins'])),
                    UIBuilder._3d_stat_row("معدل الفوز", f"{win_rate:.0f}%")
                ],
                "paddingAll": "lg",
                "spacing": "md"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "الصدارة", "text": "الصدارة"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm"
                    }
                ],
                "paddingAll": "lg"
            }
        }
    
    @staticmethod
    def leaderboard_card(leaders):
        """لوحة الصدارة - تصميم ثري دي"""
        if not leaders:
            return UIBuilder._empty_leaderboard()
        
        player_items = []
        for i, leader in enumerate(leaders[:10], 1):
            if i == 1:
                bg = f"linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%)"
                color = COLORS['white']
            elif i == 2:
                bg = f"linear-gradient(135deg, {COLORS['medium']} 0%, {COLORS['primary']} 100%)"
                color = COLORS['white']
            elif i == 3:
                bg = f"linear-gradient(135deg, {COLORS['primary_dark']} 0%, {COLORS['secondary']} 100%)"
                color = COLORS['white']
            else:
                bg = COLORS['light']
                color = COLORS['text_dark']
            
            player_items.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": str(i),
                        "size": "xl" if i <= 3 else "md",
                        "color": color,
                        "weight": "bold",
                        "flex": 0,
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": leader['display_name'],
                        "size": "md",
                        "color": color,
                        "flex": 3,
                        "margin": "lg",
                        "wrap": True,
                        "weight": "bold" if i <= 3 else "regular"
                    },
                    {
                        "type": "text",
                        "text": str(leader['total_points']),
                        "size": "lg" if i <= 3 else "md",
                        "color": color,
                        "flex": 1,
                        "align": "end",
                        "weight": "bold"
                    }
                ],
                "background": {
                    "type": "linearGradient",
                    "angle": "90deg",
                    "startColor": COLORS['primary'] if i <= 3 else COLORS['light'],
                    "endColor": COLORS['primary_dark'] if i <= 3 else COLORS['light']
                } if i <= 3 else None,
                "backgroundColor": COLORS['light'] if i > 3 else None,
                "cornerRadius": "lg",
                "paddingAll": "md",
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
                    }
                ],
                "background": {
                    "type": "linearGradient",
                    "angle": "135deg",
                    "startColor": COLORS['gradient_start'],
                    "endColor": COLORS['gradient_end']
                },
                "paddingAll": "xl"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": player_items,
                "paddingAll": "lg"
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
                "paddingAll": "lg"
            }
        }
    
    @staticmethod
    def registration_success(display_name):
        """نجاح التسجيل - تصميم ثري دي"""
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
                                "size": "5xl",
                                "color": COLORS['primary'],
                                "align": "center",
                                "weight": "bold"
                            }
                        ],
                        "backgroundColor": COLORS['light'],
                        "cornerRadius": "full",
                        "width": "100px",
                        "height": "100px",
                        "justifyContent": "center",
                        "alignItems": "center"
                    },
                    {
                        "type": "text",
                        "text": "تم التسجيل",
                        "size": "xxl",
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
                        "margin": "md",
                        "wrap": True
                    }
                ],
                "paddingAll": "xl",
                "alignItems": "center"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "ابدأ اللعب", "text": "أغنية"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm"
                    }
                ],
                "paddingAll": "lg"
            }
        }
    
    # Helper Methods
    
    @staticmethod
    def _3d_step(num, text, color):
        """خطوة ثري دي"""
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
                            "text": num,
                            "size": "lg",
                            "color": COLORS['white'],
                            "weight": "bold",
                            "align": "center"
                        }
                    ],
                    "background": {
                        "type": "linearGradient",
                        "angle": "135deg",
                        "startColor": color,
                        "endColor": COLORS['primary_dark']
                    },
                    "cornerRadius": "full",
                    "width": "40px",
                    "height": "40px",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "flex": 0
                },
                {
                    "type": "text",
                    "text": text,
                    "size": "md",
                    "color": COLORS['text_dark'],
                    "flex": 1,
                    "margin": "md"
                }
            ],
            "spacing": "md",
            "margin": "md"
        }
    
    @staticmethod
    def _3d_stat_row(label, value):
        """صف إحصائية ثري دي"""
        return {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": label,
                    "size": "md",
                    "color": COLORS['text_light'],
                    "flex": 2
                },
                {
                    "type": "text",
                    "text": value,
                    "size": "xl",
                    "color": COLORS['primary'],
                    "flex": 1,
                    "align": "end",
                    "weight": "bold"
                }
            ],
            "backgroundColor": COLORS['light'],
            "cornerRadius": "md",
            "paddingAll": "md",
            "margin": "sm"
        }
    
    @staticmethod
    def _help_section(title, items):
        """قسم مساعدة"""
        rows = []
        for cmd, desc in items:
            rows.append({
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
                        "size": "xs",
                        "color": COLORS['text_light'],
                        "flex": 3,
                        "wrap": True
                    }
                ],
                "margin": "sm" if rows else "md"
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
                *rows
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
                        "text": "لم تبدأ بعد",
                        "size": "xl",
                        "color": COLORS['text_light'],
                        "align": "center"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "ابدأ الآن", "text": "انضم"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "margin": "xl"
                    }
                ],
                "paddingAll": "xl"
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
                        "text": "لا توجد بيانات",
                        "size": "xl",
                        "color": COLORS['text_light'],
                        "align": "center"
                    }
                ],
                "paddingAll": "xl"
            }
        }
