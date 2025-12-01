"""
UI Builder - واجهات احترافية بألوان داكنة
==========================================
"""
from constants import COLORS

class UIBuilder:
    """بناء واجهات احترافية"""
    
    @staticmethod
    def welcome_card(display_name):
        """بطاقة الترحيب - تصميم داكن"""
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
                                "size": "xxl",
                                "color": COLORS['primary'],
                                "align": "center",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": f"مرحباً {display_name}",
                                "size": "lg",
                                "color": COLORS['text_dark'],
                                "align": "center",
                                "margin": "md",
                                "wrap": True
                            }
                        ],
                        "spacing": "sm"
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
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
                        "spacing": "md",
                        "margin": "xl"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "9 ألعاب متاحة",
                                "size": "sm",
                                "color": COLORS['medium'],
                                "align": "center"
                            }
                        ],
                        "margin": "xl"
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
                        "margin": "xl"
                    }
                ],
                "paddingAll": "xl",
                "backgroundColor": COLORS['card_bg'],
                "spacing": "md"
            }
        }
    
    @staticmethod
    def help_card():
        """بطاقة المساعدة - بأزرار"""
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
                                "text": "⚙️ الأوامر الأساسية",
                                "weight": "bold",
                                "size": "xl",
                                "color": COLORS['primary'],
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
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "انضم - التسجيل", "text": "انضم"},
                                        "style": "primary",
                                        "color": COLORS['primary'],
                                        "height": "sm"
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "نقاطي - إحصائياتك", "text": "نقاطي"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "margin": "sm"
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "الصدارة - أفضل اللاعبين", "text": "الصدارة"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "margin": "sm"
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "إيقاف - إنهاء اللعبة", "text": "إيقاف"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "margin": "sm"
                                    }
                                ],
                                "margin": "lg"
                            }
                        ],
                        "paddingAll": "xl",
                        "backgroundColor": COLORS['card_bg']
                    }
                },
                # البطاقة الثانية: الألعاب
                {
                    "type": "bubble",
                    "size": "mega",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🎯 الألعاب المتاحة",
                                "weight": "bold",
                                "size": "xl",
                                "color": COLORS['primary'],
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
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "🎵 لعبة الأغنية", "text": "أغنية"},
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
                                "margin": "lg"
                            }
                        ],
                        "paddingAll": "xl",
                        "backgroundColor": COLORS['card_bg']
                    }
                },
                # البطاقة الثالثة: المزيد من الألعاب
                {
                    "type": "bubble",
                    "size": "mega",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🎲 ألعاب إضافية",
                                "weight": "bold",
                                "size": "xl",
                                "color": COLORS['primary'],
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
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "🔤 تكوين الكلمات", "text": "تكوين"},
                                        "style": "primary",
                                        "color": COLORS['primary'],
                                        "height": "sm"
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "🔍 إيجاد الاختلافات", "text": "اختلاف"},
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
                                        "action": {"type": "message", "label": "🕵️ لعبة المافيا", "text": "مافيا"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "margin": "sm"
                                    }
                                ],
                                "margin": "lg"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "💡 أوامر نصية: سؤال، تحدي، اعتراف، منشن",
                                        "size": "xs",
                                        "color": COLORS['text_light'],
                                        "align": "center",
                                        "wrap": True
                                    }
                                ],
                                "margin": "xl"
                            }
                        ],
                        "paddingAll": "xl",
                        "backgroundColor": COLORS['card_bg']
                    }
                }
            ]
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
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "📊 إحصائياتك",
                        "weight": "bold",
                        "size": "xxl",
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
                                "size": "md",
                                "color": COLORS['medium'],
                                "align": "center",
                                "margin": "sm"
                            }
                        ],
                        "margin": "xl"
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": COLORS['border']
                    },
                    UIBuilder._stat_row("🎮 الألعاب", str(stats['games_played'])),
                    UIBuilder._stat_row("🏆 الفوز", str(stats['wins'])),
                    UIBuilder._stat_row("📈 معدل الفوز", f"{win_rate:.0f}%"),
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
                        "margin": "xl"
                    }
                ],
                "paddingAll": "xl",
                "backgroundColor": COLORS['card_bg'],
                "spacing": "sm"
            }
        }
    
    @staticmethod
    def leaderboard_card(leaders):
        """لوحة الصدارة"""
        if not leaders:
            return UIBuilder._empty_leaderboard()
        
        player_items = []
        for i, leader in enumerate(leaders[:10], 1):
            # تحديد اللون واليموجي حسب المركز
            if i == 1:
                emoji = "🥇"
                color = COLORS['gold']
            elif i == 2:
                emoji = "🥈"
                color = COLORS['silver']
            elif i == 3:
                emoji = "🥉"
                color = COLORS['bronze']
            else:
                emoji = f"{i}."
                color = COLORS['text_dark']
            
            player_items.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": emoji,
                        "size": "xl" if i <= 3 else "md",
                        "color": color,
                        "weight": "bold",
                        "flex": 0
                    },
                    {
                        "type": "text",
                        "text": leader['display_name'],
                        "size": "md",
                        "color": COLORS['text_dark'],
                        "flex": 3,
                        "margin": "md",
                        "wrap": True,
                        "weight": "bold" if i <= 3 else "regular"
                    },
                    {
                        "type": "text",
                        "text": f"{leader['total_points']} ⭐",
                        "size": "md",
                        "color": COLORS['primary'],
                        "flex": 2,
                        "align": "end",
                        "weight": "bold"
                    }
                ],
                "paddingAll": "md",
                "margin": "sm" if i > 1 else "none"
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
                        "text": "🏆 لوحة الصدارة",
                        "weight": "bold",
                        "size": "xxl",
                        "color": COLORS['primary'],
                        "align": "center"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": COLORS['border']
                    },
                    *player_items,
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
                        "margin": "xl"
                    }
                ],
                "paddingAll": "xl",
                "backgroundColor": COLORS['card_bg']
            }
        }
    
    @staticmethod
    def registration_success(display_name):
        """نجاح التسجيل"""
        return {
            "type": "bubble",
            "body": {
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
                    },
                    {
                        "type": "text",
                        "text": "تم التسجيل بنجاح",
                        "size": "xl",
                        "weight": "bold",
                        "color": COLORS['primary'],
                        "align": "center",
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": display_name,
                        "size": "lg",
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
                        "margin": "xl"
                    }
                ],
                "paddingAll": "xl",
                "backgroundColor": COLORS['card_bg'],
                "alignItems": "center"
            }
        }
    
    # Helper Methods
    
    @staticmethod
    def _step_item(num, text, emoji):
        """عنصر خطوة"""
        return {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": emoji,
                    "size": "xl",
                    "color": COLORS['primary'],
                    "flex": 0
                },
                {
                    "type": "text",
                    "text": f"{num}. {text}",
                    "size": "md",
                    "color": COLORS['text_dark'],
                    "flex": 1,
                    "margin": "md"
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
                    "size": "md",
                    "color": COLORS['text_light'],
                    "flex": 2
                },
                {
                    "type": "text",
                    "text": value,
                    "size": "lg",
                    "color": COLORS['text_dark'],
                    "flex": 1,
                    "align": "end",
                    "weight": "bold"
                }
            ],
            "paddingAll": "sm",
            "margin": "sm"
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
                        "text": "📊",
                        "size": "5xl",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "لم تبدأ بعد",
                        "size": "xl",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": "سجل الآن وابدأ اللعب",
                        "size": "sm",
                        "color": COLORS['medium'],
                        "align": "center",
                        "margin": "md"
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
                        "margin": "xl"
                    }
                ],
                "paddingAll": "xl",
                "backgroundColor": COLORS['card_bg']
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
                        "text": "🏆",
                        "size": "5xl",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "لا توجد بيانات",
                        "size": "xl",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "margin": "lg"
                    }
                ],
                "paddingAll": "xl",
                "backgroundColor": COLORS['card_bg']
            }
        }
