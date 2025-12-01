‏from constants import COLORS

‏class UIBuilder:
    """بناء واجهات احترافية"""
    
‏    @staticmethod
‏    def welcome_card(display_name):
        """بطاقة الترحيب - تصميم بوت الحوت"""
‏        return {
‏            "type": "bubble",
‏            "size": "mega",
‏            "header": {
‏                "type": "box",
‏                "layout": "vertical",
‏                "contents": [
                    {
‏                        "type": "image",
‏                        "url": "https://i.imgur.com/placeholder.png",
‏                        "size": "xs",
‏                        "aspectMode": "cover",
‏                        "aspectRatio": "1:1",
‏                        "gravity": "center"
                    },
                    {
‏                        "type": "text",
‏                        "text": "بوت الحوت",
‏                        "weight": "bold",
‏                        "size": "xxl",
‏                        "color": COLORS['white'],
‏                        "align": "center",
‏                        "margin": "md"
                    }
                ],
‏                "backgroundColor": COLORS['primary'],
‏                "paddingAll": "24px"
            },
‏            "body": {
‏                "type": "box",
‏                "layout": "vertical",
‏                "contents": [
                    {
‏                        "type": "text",
‏                        "text": f"مرحباً {display_name}",
‏                        "size": "lg",
‏                        "color": COLORS['text_dark'],
‏                        "align": "center",
‏                        "wrap": True,
‏                        "weight": "bold"
                    },
                    {
‏                        "type": "text",
‏                        "text": "منصة الألعاب التفاعلية",
‏                        "size": "sm",
‏                        "color": COLORS['text_light'],
‏                        "align": "center",
‏                        "margin": "sm"
                    },
                    {
‏                        "type": "separator",
‏                        "margin": "lg",
‏                        "color": COLORS['border']
                    },
                    {
‏                        "type": "box",
‏                        "layout": "vertical",
‏                        "contents": [
                            {
‏                                "type": "text",
‏                                "text": "9 ألعاب متاحة",
‏                                "size": "md",
‏                                "color": COLORS['primary'],
‏                                "align": "center",
‏                                "weight": "bold"
                            }
                        ],
‏                        "margin": "lg"
                    }
                ],
‏                "backgroundColor": COLORS['card_bg'],
‏                "paddingAll": "20px"
            },
‏            "footer": {
‏                "type": "box",
‏                "layout": "vertical",
‏                "contents": [
                    {
‏                        "type": "button",
‏                        "action": {"type": "message", "label": "انضم الآن", "text": "انضم"},
‏                        "style": "primary",
‏                        "color": COLORS['primary'],
‏                        "height": "sm"
                    },
                    {
‏                        "type": "button",
‏                        "action": {"type": "message", "label": "دليل الألعاب", "text": "مساعدة"},
‏                        "style": "secondary",
‏                        "height": "sm",
‏                        "margin": "sm"
                    }
                ],
‏                "backgroundColor": COLORS['background'],
‏                "paddingAll": "16px"
            }
        }
    
‏    @staticmethod
‏    def help_card():
        """بطاقة المساعدة - تصميم بوت الحوت"""
‏        return {
‏            "type": "carousel",
‏            "contents": [
                # البطاقة الأولى: الأوامر الأساسية
                {
‏                    "type": "bubble",
‏                    "size": "mega",
‏                    "header": {
‏                        "type": "box",
‏                        "layout": "vertical",
‏                        "contents": [
                            {
‏                                "type": "text",
‏                                "text": "الأوامر الأساسية",
‏                                "weight": "bold",
‏                                "size": "xl",
‏                                "color": COLORS['white'],
‏                                "align": "center"
                            }
                        ],
‏                        "backgroundColor": COLORS['primary'],
‏                        "paddingAll": "20px"
                    },
‏                    "body": {
‏                        "type": "box",
‏                        "layout": "vertical",
‏                        "contents": [
                            {
‏                                "type": "button",
‏                                "action": {"type": "message", "label": "انضم", "text": "انضم"},
‏                                "style": "primary",
‏                                "color": COLORS['success'],
‏                                "height": "sm"
                            },
                            {
‏                                "type": "button",
‏                                "action": {"type": "message", "label": "نقاطي", "text": "نقاطي"},
‏                                "style": "secondary",
‏                                "height": "sm",
‏                                "margin": "sm"
                            },
                            {
‏                                "type": "button",
‏                                "action": {"type": "message", "label": "الصدارة", "text": "الصدارة"},
‏                                "style": "secondary",
‏                                "height": "sm",
‏                                "margin": "sm"
                            },
                            {
‏                                "type": "button",
‏                                "action": {"type": "message", "label": "إيقاف", "text": "إيقاف"},
‏                                "style": "secondary",
‏                                "height": "sm",
‏                                "margin": "sm"
                            }
                        ],
‏                        "paddingAll": "20px",
‏                        "backgroundColor": COLORS['card_bg']
                    }
                },
                # البطاقة الثانية: الألعاب
                {
‏                    "type": "bubble",
‏                    "size": "mega",
‏                    "header": {
‏                        "type": "box",
‏                        "layout": "vertical",
‏                        "contents": [
                            {
‏                                "type": "text",
‏                                "text": "الألعاب المتاحة",
‏                                "weight": "bold",
‏                                "size": "xl",
‏                                "color": COLORS['white'],
‏                                "align": "center"
                            }
                        ],
‏                        "backgroundColor": COLORS['secondary'],
‏                        "paddingAll": "20px"
                    },
‏                    "body": {
‏                        "type": "box",
‏                        "layout": "vertical",
‏                        "contents": [
                            {
‏                                "type": "button",
‏                                "action": {"type": "message", "label": "الأغنية", "text": "أغنية"},
‏                                "style": "primary",
‏                                "color": COLORS['primary'],
‏                                "height": "sm"
                            },
                            {
‏                                "type": "button",
‏                                "action": {"type": "message", "label": "إنسان حيوان نبات", "text": "لعبة"},
‏                                "style": "secondary",
‏                                "height": "sm",
‏                                "margin": "sm"
                            },
                            {
‏                                "type": "button",
‏                                "action": {"type": "message", "label": "سلسلة الكلمات", "text": "سلسلة"},
‏                                "style": "secondary",
‏                                "height": "sm",
‏                                "margin": "sm"
                            },
                            {
‏                                "type": "button",
‏                                "action": {"type": "message", "label": "الكتابة السريعة", "text": "أسرع"},
‏                                "style": "secondary",
‏                                "height": "sm",
‏                                "margin": "sm"
                            },
                            {
‏                                "type": "button",
‏                                "action": {"type": "message", "label": "الأضداد", "text": "ضد"},
‏                                "style": "secondary",
‏                                "height": "sm",
‏                                "margin": "sm"
                            }
                        ],
‏                        "paddingAll": "20px",
‏                        "backgroundColor": COLORS['card_bg']
                    }
                },
                # البطاقة الثالثة: المزيد من الألعاب
                {
‏                    "type": "bubble",
‏                    "size": "mega",
‏                    "header": {
‏                        "type": "box",
‏                        "layout": "vertical",
‏                        "contents": [
                            {
‏                                "type": "text",
‏                                "text": "ألعاب إضافية",
‏                                "weight": "bold",
‏                                "size": "xl",
‏                                "color": COLORS['white'],
‏                                "align": "center"
                            }
                        ],
‏                        "backgroundColor": COLORS['accent'],
‏                        "paddingAll": "20px"
                    },
‏                    "body": {
‏                        "type": "box",
‏                        "layout": "vertical",
‏                        "contents": [
                            {
‏                                "type": "button",
‏                                "action": {"type": "message", "label": "تكوين الكلمات", "text": "تكوين"},
‏                                "style": "primary",
‏                                "color": COLORS['info'],
‏                                "height": "sm"
                            },
                            {
‏                                "type": "button",
‏                                "action": {"type": "message", "label": "الاختلافات", "text": "اختلاف"},
‏                                "style": "secondary",
‏                                "height": "sm",
‏                                "margin": "sm"
                            },
                            {
‏                                "type": "button",
‏                                "action": {"type": "message", "label": "نسبة التوافق", "text": "توافق"},
‏                                "style": "secondary",
‏                                "height": "sm",
‏                                "margin": "sm"
                            },
                            {
‏                                "type": "button",
‏                                "action": {"type": "message", "label": "المافيا", "text": "مافيا"},
‏                                "style": "secondary",
‏                                "height": "sm",
‏                                "margin": "sm"
                            },
                            {
‏                                "type": "separator",
‏                                "margin": "lg",
‏                                "color": COLORS['border']
                            },
                            {
‏                                "type": "text",
‏                                "text": "أوامر نصية: سؤال - تحدي - اعتراف - منشن",
‏                                "size": "xs",
‏                                "color": COLORS['text_light'],
‏                                "align": "center",
‏                                "wrap": True,
‏                                "margin": "lg"
                            }
                        ],
‏                        "paddingAll": "20px",
‏                        "backgroundColor": COLORS['card_bg']
                    }
                }
            ]
        }
    
‏    @staticmethod
‏    def stats_card(display_name, stats):
        """بطاقة الإحصائيات"""
‏        if not stats:
‏            return UIBuilder._empty_stats(display_name)
        
‏        win_rate = (stats['wins'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0
        
‏        return {
‏            "type": "bubble",
‏            "size": "mega",
‏            "header": {
‏                "type": "box",
‏                "layout": "vertical",
‏                "contents": [
                    {
‏                        "type": "text",
‏                        "text": "إحصائياتك",
‏                        "weight": "bold",
‏                        "size": "xl",
‏                        "color": COLORS['white'],
‏                        "align": "center"
                    },
                    {
‏                        "type": "text",
‏                        "text": display_name,
‏                        "size": "sm",
‏                        "color": COLORS['light'],
‏                        "align": "center",
‏                        "margin": "sm",
‏                        "wrap": True
                    }
                ],
‏                "backgroundColor": COLORS['primary'],
‏                "paddingAll": "20px"
            },
‏            "body": {
‏                "type": "box",
‏                "layout": "vertical",
‏                "contents": [
                    {
‏                        "type": "text",
‏                        "text": str(stats['total_points']),
‏                        "size": "5xl",
‏                        "weight": "bold",
‏                        "color": COLORS['primary'],
‏                        "align": "center"
                    },
                    {
‏                        "type": "text",
‏                        "text": "نقطة",
‏                        "size": "sm",
‏                        "color": COLORS['text_light'],
‏                        "align": "center",
‏                        "margin": "xs"
                    },
                    {
‏                        "type": "separator",
‏                        "margin": "lg",
‏                        "color": COLORS['border']
                    },
                    {
‏                        "type": "box",
‏                        "layout": "vertical",
‏                        "contents": [
‏                            UIBuilder._stat_row("الألعاب", str(stats['games_played'])),
‏                            UIBuilder._stat_row("الفوز", str(stats['wins'])),
‏                            UIBuilder._stat_row("معدل الفوز", f"{win_rate:.0f}%")
                        ],
‏                        "spacing": "sm",
‏                        "paddingAll": "md",
‏                        "margin": "lg"
                    }
                ],
‏                "backgroundColor": COLORS['card_bg'],
‏                "paddingAll": "20px"
            },
‏            "footer": {
‏                "type": "box",
‏                "layout": "vertical",
‏                "contents": [
                    {
‏                        "type": "button",
‏                        "action": {"type": "message", "label": "عرض الصدارة", "text": "الصدارة"},
‏                        "style": "primary",
‏                        "color": COLORS['primary'],
‏                        "height": "sm"
                    }
                ],
‏                "backgroundColor": COLORS['background'],
‏                "paddingAll": "16px"
            }
        }
    
‏    @staticmethod
‏    def leaderboard_card(leaders):
        """لوحة الصدارة"""
‏        if not leaders:
‏            return UIBuilder._empty_leaderboard()
        
‏        player_items = []
‏        for i, leader in enumerate(leaders[:10], 1):
‏            if i == 1:
‏                rank_color = COLORS['gold']
‏                rank_text = "1"
‏            elif i == 2:
‏                rank_color = COLORS['silver']
‏                rank_text = "2"
‏            elif i == 3:
‏                rank_color = COLORS['bronze']
‏                rank_text = "3"
‏            else:
‏                rank_color = COLORS['text_light']
‏                rank_text = str(i)
            
‏            player_items.append({
‏                "type": "box",
‏                "layout": "horizontal",
‏                "contents": [
                    {
‏                        "type": "text",
‏                        "text": rank_text,
‏                        "size": "xl" if i <= 3 else "md",
‏                        "color": rank_color,
‏                        "weight": "bold",
‏                        "flex": 0
                    },
                    {
‏                        "type": "text",
‏                        "text": leader['display_name'],
‏                        "size": "md",
‏                        "color": rank_color if i <= 3 else COLORS['text_dark'],
‏                        "flex": 3,
‏                        "margin": "md",
‏                        "wrap": True,
‏                        "weight": "bold" if i <= 3 else "regular"
                    },
                    {
‏                        "type": "text",
‏                        "text": str(leader['total_points']),
‏                        "size": "md",
‏                        "color": COLORS['primary'],
‏                        "flex": 1,
‏                        "align": "end",
‏                        "weight": "bold"
                    }
                ],
‏                "paddingAll": "md",
‏                "margin": "xs" if i > 1 else "none",
‏                "backgroundColor": COLORS['light'] if i <= 3 else "none"
            })
        
‏        return {
‏            "type": "bubble",
‏            "size": "mega",
‏            "header": {
‏                "type": "box",
‏                "layout": "vertical",
‏                "contents": [
                    {
‏                        "type": "text",
‏                        "text": "لوحة الصدارة",
‏                        "weight": "bold",
‏                        "size": "xl",
‏                        "color": COLORS['white'],
‏                        "align": "center"
                    }
                ],
‏                "backgroundColor": COLORS['primary'],
‏                "paddingAll": "20px"
            },
‏            "body": {
‏                "type": "box",
‏                "layout": "vertical",
‏                "contents": player_items,
‏                "backgroundColor": COLORS['card_bg'],
‏                "paddingAll": "20px",
‏                "spacing": "xs"
            },
‏            "footer": {
‏                "type": "box",
‏                "layout": "vertical",
‏                "contents": [
                    {
‏                        "type": "button",
‏                        "action": {"type": "message", "label": "إحصائياتي", "text": "نقاطي"},
‏                        "style": "secondary",
‏                        "height": "sm"
                    }
                ],
‏                "backgroundColor": COLORS['background'],
‏                "paddingAll": "16px"
            }
        }
    
‏    @staticmethod
‏    def registration_success(display_name):
        """نجاح التسجيل"""
‏        return {
‏            "type": "bubble",
‏            "header": {
‏                "type": "box",
‏                "layout": "vertical",
‏                "contents": [
                    {
‏                        "type": "text",
‏                        "text": "تم التسجيل بنجاح",
‏                        "weight": "bold",
‏                        "size": "xl",
‏                        "color": COLORS['white'],
‏                        "align": "center"
                    }
                ],
‏                "backgroundColor": COLORS['success'],
‏                "paddingAll": "20px"
            },
‏            "body": {
‏                "type": "box",
‏                "layout": "vertical",
‏                "contents": [
                    {
‏                        "type": "text",
‏                        "text": display_name,
‏                        "size": "lg",
‏                        "color": COLORS['text_dark'],
‏                        "align": "center",
‏                        "wrap": True,
‏                        "weight": "bold"
                    },
                    {
‏                        "type": "text",
‏                        "text": "مرحباً بك في بوت الحوت",
‏                        "size": "sm",
‏                        "color": COLORS['text_light'],
‏                        "align": "center",
‏                        "margin": "sm"
                    }
                ],
‏                "paddingAll": "20px",
‏                "backgroundColor": COLORS['card_bg']
            },
‏            "footer": {
‏                "type": "box",
‏                "layout": "vertical",
‏                "contents": [
                    {
‏                        "type": "button",
‏                        "action": {"type": "message", "label": "ابدأ اللعب", "text": "أغنية"},
‏                        "style": "primary",
‏                        "color": COLORS['primary'],
‏                        "height": "sm"
                    },
                    {
‏                        "type": "button",
‏                        "action": {"type": "message", "label": "دليل الألعاب", "text": "مساعدة"},
‏                        "style": "secondary",
‏                        "height": "sm",
‏                        "margin": "sm"
                    }
                ],
‏                "backgroundColor": COLORS['background'],
‏                "paddingAll": "16px"
            }
        }
    
‏    # Helper Methods
    
‏    @staticmethod
‏    def _stat_row(label, value):
        """صف إحصائية"""
‏        return {
‏            "type": "box",
‏            "layout": "horizontal",
‏            "contents": [
                {
‏                    "type": "text",
‏                    "text": label,
‏                    "size": "sm",
‏                    "color": COLORS['text_light'],
‏                    "flex": 2
                },
                {
‏                    "type": "text",
‏                    "text": value,
‏                    "size": "md",
‏                    "color": COLORS['text_dark'],
‏                    "flex": 1,
‏                    "align": "end",
‏                    "weight": "bold"
                }
            ],
‏            "paddingAll": "xs",
‏            "margin": "xs"
        }
    
‏    @staticmethod
‏    def _empty_stats(display_name):
        """إحصائيات فارغة"""
‏        return {
‏            "type": "bubble",
‏            "body": {
‏                "type": "box",
‏                "layout": "vertical",
‏                "contents": [
                    {
‏                        "type": "text",
‏                        "text": "لم تبدأ بعد",
‏                        "size": "lg",
‏                        "color": COLORS['text_dark'],
‏                        "align": "center",
‏                        "weight": "bold"
                    },
                    {
‏                        "type": "text",
‏                        "text": "سجل الآن وابدأ اللعب",
‏                        "size": "sm",
‏                        "color": COLORS['text_light'],
‏                        "align": "center",
‏                        "margin": "sm"
                    },
                    {
‏                        "type": "separator",
‏                        "margin": "lg",
‏                        "color": COLORS['border']
                    },
                    {
‏                        "type": "button",
‏                        "action": {"type": "message", "label": "ابدأ الآن", "text": "انضم"},
‏                        "style": "primary",
‏                        "color": COLORS['primary'],
‏                        "height": "sm",
‏                        "margin": "lg"
                    }
                ],
‏                "paddingAll": "xl",
‏                "backgroundColor": COLORS['card_bg']
            }
        }
    
‏    @staticmethod
‏    def _empty_leaderboard():
        """صدارة فارغة"""
‏        return {
‏            "type": "bubble",
‏            "body": {
‏                "type": "box",
‏                "layout": "vertical",
‏                "contents": [
                    {
‏                        "type": "text",
‏                        "text": "لا توجد بيانات",
‏                        "size": "lg",
‏                        "color": COLORS['text_dark'],
‏                        "align": "center",
‏                        "weight": "bold"
                    },
                    {
‏                        "type": "text",
‏                        "text": "كن أول من يسجل",
‏                        "size": "sm",
‏                        "color": COLORS['text_light'],
‏                        "align": "center",
‏                        "margin": "sm"
                    }
                ],
‏                "paddingAll": "xl",
‏                "backgroundColor": COLORS['card_bg']
            }
        }
