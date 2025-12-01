"""
UI Builder - واجهات احترافية بألوان داكنة
==========================================
"""
from constants import COLORS

class UIBuilder:
    """بناء واجهات احترافية"""
    
    @staticmethod
    def welcome_card(display_name):
        """بطاقة الترحيب - تصميم أنيق ومريح"""
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
                                "text": "🎮",
                                "size": "5xl",
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "منصة الألعاب التفاعلية",
                                "weight": "bold",
                                "size": "xl",
                                "color": COLORS['primary'],
                                "align": "center",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": f"مرحباً {display_name}",
                                "size": "md",
                                "color": COLORS['text_dark'],
                                "align": "center",
                                "margin": "sm",
                                "wrap": True
                            }
                        ],
                        "spacing": "sm",
                        "paddingAll": "lg"
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
                            UIBuilder._step_item("1", "انضم للبوت", "✓"),
                            UIBuilder._step_item("2", "اختر لعبتك", "🎯"),
                            UIBuilder._step_item("3", "اجمع النقاط", "⭐")
                        ],
                        "spacing": "sm",
                        "margin": "lg",
                        "paddingAll": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "✨ 9 ألعاب متاحة ✨",
                                "size": "sm",
                                "color": COLORS['text_light'],
                                "align": "center"
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
                                "type": "button",
                                "action": {"type": "message", "label": "🎮 انضم الآن", "text": "انضم"},
                                "style": "primary",
                                "color": COLORS['primary'],
                                "height": "sm"
                            },
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "📖 دليل الألعاب", "text": "مساعدة"},
                                "style": "secondary",
                                "height": "sm",
                                "margin": "sm"
                            }
                        ],
                        "margin": "lg",
                        "paddingAll": "md"
                    }
                ],
                "paddingAll": "none",
                "backgroundColor": COLORS['card_bg'],
                "spacing": "none"
            }
        }
    
    @staticmethod
    def help_card():
        """بطاقة المساعدة - تصميم أنيق بأزرار"""
        return {
            "type": "carousel",
            "contents": [
                # البطاقة الأولى: الأوامر الأساسية
                {
                    "type": "bubble",
                    "size": "mega",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "⚙️",
                                "size": "4xl",
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "الأوامر الأساسية",
                                "weight": "bold",
                                "size": "lg",
                                "color": COLORS['text_dark'],
                                "align": "center",
                                "margin": "md"
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
                                        "type": "button",
                                        "action": {"type": "message", "label": "✓ انضم", "text": "انضم"},
                                        "style": "primary",
                                        "color": COLORS['success'],
                                        "height": "sm"
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "📊 نقاطي", "text": "نقاطي"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "margin": "sm"
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "🏆 الصدارة", "text": "الصدارة"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "margin": "sm"
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "⏹️ إيقاف", "text": "إيقاف"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "margin": "sm"
                                    }
                                ],
                                "margin": "lg",
                                "paddingAll": "md"
                            }
                        ],
                        "paddingAll": "lg",
                        "backgroundColor": COLORS['card_bg'],
                        "spacing": "sm"
                    }
                },
                # البطاقة الثانية: الألعاب الجزء 1
                {
                    "type": "bubble",
                    "size": "mega",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🎯",
                                "size": "4xl",
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "الألعاب - الجزء 1",
                                "weight": "bold",
                                "size": "lg",
                                "color": COLORS['text_dark'],
                                "align": "center",
                                "margin": "md"
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
                                        "type": "button",
                                        "action": {"type": "message", "label": "🎵 الأغنية", "text": "أغنية"},
                                        "style": "primary",
                                        "color": COLORS['primary'],
                                        "height": "sm"
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "🌿 إنسان حيوان نبات", "text": "لعبة"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "margin": "sm"
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "⛓️ سلسلة الكلمات", "text": "سلسلة"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "margin": "sm"
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "⚡ الكتابة السريعة", "text": "أسرع"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "margin": "sm"
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "🔄 الأضداد", "text": "ضد"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "margin": "sm"
                                    }
                                ],
                                "margin": "lg",
                                "paddingAll": "md"
                            }
                        ],
                        "paddingAll": "lg",
                        "backgroundColor": COLORS['card_bg'],
                        "spacing": "sm"
                    }
                },
                # البطاقة الثالثة: الألعاب الجزء 2
                {
                    "type": "bubble",
                    "size": "mega",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🎲",
                                "size": "4xl",
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "الألعاب - الجزء 2",
                                "weight": "bold",
                                "size": "lg",
                                "color": COLORS['text_dark'],
                                "align": "center",
                                "margin": "md"
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
                                        "type": "button",
                                        "action": {"type": "message", "label": "🔤 تكوين الكلمات", "text": "تكوين"},
                                        "style": "primary",
                                        "color": COLORS['info'],
                                        "height": "sm"
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "🔍 الاختلافات", "text": "اختلاف"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "margin": "sm"
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "💕 نسبة التوافق", "text": "توافق"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "margin": "sm"
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "🕵️ المافيا", "text": "مافيا"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "margin": "sm"
                                    }
                                ],
                                "margin": "lg",
                                "paddingAll": "md"
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
                                        "text": "💬 أوامر نصية",
                                        "size": "xs",
                                        "color": COLORS['text_light'],
                                        "align": "center",
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "text",
                                        "text": "سؤال • تحدي • اعتراف • منشن",
                                        "size": "xs",
                                        "color": COLORS['text_light'],
                                        "align": "center",
                                        "margin": "xs"
                                    }
                                ],
                                "margin": "lg",
                                "paddingAll": "sm"
                            }
                        ],
                        "paddingAll": "lg",
                        "backgroundColor": COLORS['card_bg'],
                        "spacing": "sm"
                    }
                }
            ]
        }
    
    @staticmethod
    def stats_card(display_name, stats):
        """بطاقة الإحصائيات - تصميم أنيق"""
        if not stats:
            return UIBuilder._empty_stats(display_name)
        
        win_rate = (stats['wins'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0
        
        return {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "📊",
                        "size": "4xl",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "إحصائياتك",
                        "weight": "bold",
                        "size": "lg",
                        "color": COLORS['text_dark'],
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": display_name,
                        "size": "sm",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "margin": "xs",
                        "wrap": True
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
                                "text": str(stats['total_points']),
                                "size": "5xl",
                                "weight": "bold",
                                "color": COLORS['primary'],
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "⭐ نقطة",
                                "size": "sm",
                                "color": COLORS['text_light'],
                                "align": "center",
                                "margin": "xs"
                            }
                        ],
                        "margin": "lg",
                        "paddingAll": "md"
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
                            UIBuilder._stat_row("🎮 الألعاب", str(stats['games_played'])),
                            UIBuilder._stat_row("🏆 الفوز", str(stats['wins'])),
                            UIBuilder._stat_row("📈 معدل الفوز", f"{win_rate:.0f}%")
                        ],
                        "spacing": "sm",
                        "paddingAll": "md"
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
                                "type": "button",
                                "action": {"type": "message", "label": "🏅 عرض الصدارة", "text": "الصدارة"},
                                "style": "primary",
                                "color": COLORS['primary'],
                                "height": "sm"
                            }
                        ],
                        "margin": "lg",
                        "paddingAll": "md"
                    }
                ],
                "paddingAll": "lg",
                "backgroundColor": COLORS['card_bg'],
                "spacing": "none"
            }
        }
    
    @staticmethod
    def leaderboard_card(leaders):
        """لوحة الصدارة - تصميم أنيق"""
        if not leaders:
            return UIBuilder._empty_leaderboard()
        
        player_items = []
        for i, leader in enumerate(leaders[:10], 1):
            # تحديد اللون والأيقونة
            if i == 1:
                emoji = "🥇"
                name_color = COLORS['gold']
                points_color = COLORS['gold']
            elif i == 2:
                emoji = "🥈"
                name_color = COLORS['silver']
                points_color = COLORS['silver']
            elif i == 3:
                emoji = "🥉"
                name_color = COLORS['bronze']
                points_color = COLORS['bronze']
            else:
                emoji = f"{i}."
                name_color = COLORS['text_dark']
                points_color = COLORS['primary']
            
            player_items.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": emoji,
                        "size": "xl" if i <= 3 else "md",
                        "color": name_color if i <= 3 else COLORS['text_light'],
                        "weight": "bold",
                        "flex": 0
                    },
                    {
                        "type": "text",
                        "text": leader['display_name'],
                        "size": "md",
                        "color": name_color,
                        "flex": 3,
                        "margin": "md",
                        "wrap": True,
                        "weight": "bold" if i <= 3 else "regular"
                    },
                    {
                        "type": "text",
                        "text": f"{leader['total_points']} ⭐",
                        "size": "md",
                        "color": points_color,
                        "flex": 2,
                        "align": "end",
                        "weight": "bold"
                    }
                ],
                "paddingAll": "md",
                "margin": "xs" if i > 1 else "none",
                "backgroundColor": COLORS['light'] if i <= 3 else "none"
            })
        
        return {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "🏆",
                        "size": "4xl",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "لوحة الصدارة",
                        "weight": "bold",
                        "size": "lg",
                        "color": COLORS['text_dark'],
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": COLORS['border']
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": player_items,
                        "margin": "lg",
                        "spacing": "xs"
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
                                "type": "button",
                                "action": {"type": "message", "label": "📊 إحصائياتي", "text": "نقاطي"},
                                "style": "secondary",
                                "height": "sm"
                            }
                        ],
                        "margin": "lg",
                        "paddingAll": "md"
                    }
                ],
                "paddingAll": "lg",
                "backgroundColor": COLORS['card_bg'],
                "spacing": "none"
            }
        }
    
    @staticmethod
    def registration_success(display_name):
        """نجاح التسجيل - تصميم أنيق"""
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
                                "color": COLORS['success'],
                                "align": "center",
                                "weight": "bold"
                            }
                        ],
                        "paddingAll": "lg"
                    },
                    {
                        "type": "text",
                        "text": "تم التسجيل بنجاح",
                        "size": "lg",
                        "weight": "bold",
                        "color": COLORS['text_dark'],
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": display_name,
                        "size": "md",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "margin": "sm",
                        "wrap": True
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
                                "type": "button",
                                "action": {"type": "message", "label": "🎮 ابدأ اللعب", "text": "أغنية"},
                                "style": "primary",
                                "color": COLORS['primary'],
                                "height": "sm"
                            },
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "📖 دليل الألعاب", "text": "مساعدة"},
                                "style": "secondary",
                                "height": "sm",
                                "margin": "sm"
                            }
                        ],
                        "margin": "lg",
                        "paddingAll": "md"
                    }
                ],
                "paddingAll": "lg",
                "backgroundColor": COLORS['card_bg'],
                "alignItems": "center",
                "spacing": "none"
            }
        }
    
    # Helper Methods
    
    @staticmethod
    def _step_item(num, text, emoji):
        """عنصر خطوة - أنيق"""
        return {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": emoji,
                    "size": "lg",
                    "color": COLORS['primary'],
                    "flex": 0
                },
                {
                    "type": "text",
                    "text": f"{num}. {text}",
                    "size": "sm",
                    "color": COLORS['text_dark'],
                    "flex": 1,
                    "margin": "md"
                }
            ],
            "spacing": "sm",
            "paddingAll": "xs"
        }
    
    @staticmethod
    def _stat_row(label, value):
        """صف إحصائية - أنيق"""
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
                    "flex": 1,
                    "align": "end",
                    "weight": "bold"
                }
            ],
            "paddingAll": "xs",
            "margin": "xs"
        }
    
    @staticmethod
    def _empty_stats(display_name):
        """إحصائيات فارغة - تصميم أنيق"""
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "📊",
                        "size": "5xl",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "لم تبدأ بعد",
                        "size": "lg",
                        "color": COLORS['text_dark'],
                        "align": "center",
                        "margin": "lg",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "سجل الآن وابدأ اللعب",
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
                                "type": "button",
                                "action": {"type": "message", "label": "🎮 ابدأ الآن", "text": "انضم"},
                                "style": "primary",
                                "color": COLORS['primary'],
                                "height": "sm"
                            }
                        ],
                        "margin": "lg",
                        "paddingAll": "md"
                    }
                ],
                "paddingAll": "xl",
                "backgroundColor": COLORS['card_bg']
            }
        }
    
    @staticmethod
    def _empty_leaderboard():
        """صدارة فارغة - تصميم أنيق"""
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "🏆",
                        "size": "5xl",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "لا توجد بيانات",
                        "size": "lg",
                        "color": COLORS['text_dark'],
                        "align": "center",
                        "margin": "lg",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "كن أول من يسجل",
                        "size": "sm",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "margin": "sm"
                    }
                ],
                "paddingAll": "xl",
                "backgroundColor": COLORS['card_bg']
            }
        }
