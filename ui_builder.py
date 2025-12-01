from constants import COLORS

class UIBuilder:
    """بناء واجهات احترافية بألوان بوت الحوت الجديدة"""
    
    @staticmethod
    def welcome_card(display_name):
        """نافذة الترحيب - تصميم نيون تركواز"""
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "size": "5xl",
                        "align": "center",
                        "color": COLORS['glow']
                    },
                    {
                        "type": "text",
                        "text": "بوت الحوت",
                        "weight": "bold",
                        "size": "xxl",
                        "color": COLORS['white'],
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": "W H A L E  B O T",
                        "size": "xs",
                        "color": COLORS['light'],
                        "align": "center",
                        "margin": "sm",
                        "style": "normal"
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
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"مرحباً {display_name}",
                                "size": "xl",
                                "color": COLORS['text_dark'],
                                "align": "center",
                                "wrap": True,
                                "weight": "bold"
                            },
                            {
                                "type": "text",
                                "text": "منصة الألعاب التفاعلية الذكية",
                                "size": "sm",
                                "color": COLORS['text_light'],
                                "align": "center",
                                "margin": "md",
                                "wrap": True
                            }
                        ],
                        "paddingAll": "md",
                        "backgroundColor": COLORS['background_medium'],
                        "cornerRadius": "lg"
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
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "🎮",
                                        "size": "xl",
                                        "flex": 0
                                    },
                                    {
                                        "type": "text",
                                        "text": "9 ألعاب متنوعة",
                                        "size": "md",
                                        "color": COLORS['text_dark'],
                                        "margin": "md",
                                        "flex": 1
                                    }
                                ],
                                "margin": "md"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "⚡",
                                        "size": "xl",
                                        "flex": 0
                                    },
                                    {
                                        "type": "text",
                                        "text": "تحديات يومية",
                                        "size": "md",
                                        "color": COLORS['text_dark'],
                                        "margin": "md",
                                        "flex": 1
                                    }
                                ],
                                "margin": "md"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "🏆",
                                        "size": "xl",
                                        "flex": 0
                                    },
                                    {
                                        "type": "text",
                                        "text": "نظام نقاط ومكافآت",
                                        "size": "md",
                                        "color": COLORS['text_dark'],
                                        "margin": "md",
                                        "flex": 1
                                    }
                                ],
                                "margin": "md"
                            }
                        ],
                        "margin": "lg"
                    }
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "24px",
                "spacing": "none"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "🚀 ابدأ الآن", "text": "انضم"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "📖 دليل الاستخدام", "text": "مساعدة"},
                        "style": "secondary",
                        "height": "sm",
                        "margin": "md"
                    }
                ],
                "backgroundColor": COLORS['background_medium'],
                "paddingAll": "20px",
                "spacing": "none"
            }
        }
    
    @staticmethod
    def help_card():
        """نافذة المساعدة - دليل شامل"""
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "📖 دليل الاستخدام",
                        "weight": "bold",
                        "size": "xxl",
                        "color": COLORS['white'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "جميع الأوامر والألعاب",
                        "size": "sm",
                        "color": COLORS['light'],
                        "align": "center",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": COLORS['background'],
                "paddingAll": "24px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    # الأوامر الأساسية
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "⚙️ الأوامر الأساسية",
                                "size": "lg",
                                "color": COLORS['primary'],
                                "weight": "bold"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    UIBuilder._help_item("انضم", "التسجيل في البوت"),
                                    UIBuilder._help_item("نقاطي", "عرض إحصائياتك"),
                                    UIBuilder._help_item("الصدارة", "لوحة المتصدرين"),
                                    UIBuilder._help_item("إيقاف", "إيقاف اللعبة الحالية")
                                ],
                                "margin": "md",
                                "spacing": "sm"
                            }
                        ],
                        "backgroundColor": COLORS['background_medium'],
                        "paddingAll": "md",
                        "cornerRadius": "lg"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": COLORS['border']
                    },
                    # الألعاب
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🎮 الألعاب المتاحة",
                                "size": "lg",
                                "color": COLORS['primary'],
                                "weight": "bold"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    UIBuilder._help_item("أغنية", "خمن المغني من الكلمات"),
                                    UIBuilder._help_item("لعبة", "إنسان حيوان نبات بلاد"),
                                    UIBuilder._help_item("سلسلة", "سلسلة الكلمات"),
                                    UIBuilder._help_item("أسرع", "الكتابة السريعة"),
                                    UIBuilder._help_item("ضد", "لعبة الأضداد"),
                                    UIBuilder._help_item("تكوين", "تكوين الكلمات"),
                                    UIBuilder._help_item("اختلاف", "اختلافات الصور"),
                                    UIBuilder._help_item("توافق", "نسبة التوافق"),
                                    UIBuilder._help_item("مافيا", "لعبة المافيا الجماعية")
                                ],
                                "margin": "md",
                                "spacing": "sm"
                            }
                        ],
                        "backgroundColor": COLORS['background_medium'],
                        "paddingAll": "md",
                        "cornerRadius": "lg",
                        "margin": "lg"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": COLORS['border']
                    },
                    # أوامر إضافية
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "💬 أوامر التفاعل",
                                "size": "lg",
                                "color": COLORS['primary'],
                                "weight": "bold"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    UIBuilder._help_item("سؤال", "سؤال عشوائي"),
                                    UIBuilder._help_item("تحدي", "تحدي عشوائي"),
                                    UIBuilder._help_item("اعتراف", "اعتراف عشوائي"),
                                    UIBuilder._help_item("منشن", "منشن عشوائي")
                                ],
                                "margin": "md",
                                "spacing": "sm"
                            }
                        ],
                        "backgroundColor": COLORS['background_medium'],
                        "paddingAll": "md",
                        "cornerRadius": "lg",
                        "margin": "lg"
                    }
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px",
                "spacing": "none"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "💡 نصيحة: استخدم 'لمح' للحصول على تلميح أثناء اللعب",
                        "size": "xs",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "wrap": True
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "🎮 ابدأ اللعب", "text": "أغنية"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm",
                        "margin": "md"
                    }
                ],
                "backgroundColor": COLORS['background_medium'],
                "paddingAll": "20px",
                "spacing": "none"
            }
        }
    
    @staticmethod
    def _help_item(command, description):
        """عنصر مساعدة"""
        return {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": "▸",
                    "size": "sm",
                    "color": COLORS['glow'],
                    "flex": 0
                },
                {
                    "type": "text",
                    "text": command,
                    "size": "sm",
                    "color": COLORS['text_dark'],
                    "weight": "bold",
                    "flex": 2,
                    "margin": "sm"
                },
                {
                    "type": "text",
                    "text": description,
                    "size": "xs",
                    "color": COLORS['text_light'],
                    "flex": 4,
                    "wrap": True
                }
            ],
            "spacing": "sm"
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
                        "text": "📊 إحصائياتك",
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
                "backgroundColor": COLORS['background'],
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
                                "color": COLORS['glow'],
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "نقطة",
                                "size": "md",
                                "color": COLORS['text_light'],
                                "align": "center",
                                "margin": "sm"
                            }
                        ],
                        "backgroundColor": COLORS['background_medium'],
                        "paddingAll": "lg",
                        "cornerRadius": "lg"
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
                            UIBuilder._stat_row("🎮 الألعاب", str(stats['games_played'])),
                            UIBuilder._stat_row("🏆 الفوز", str(stats['wins'])),
                            UIBuilder._stat_row("📈 معدل الفوز", f"{win_rate:.0f}%")
                        ],
                        "spacing": "md",
                        "margin": "lg"
                    }
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "24px",
                "spacing": "none"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "🏆 عرض الصدارة", "text": "الصدارة"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm"
                    }
                ],
                "backgroundColor": COLORS['background_medium'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def leaderboard_card(leaders):
        """لوحة الصدارة"""
        if not leaders:
            return UIBuilder._empty_leaderboard()
        
        player_items = []
        for i, leader in enumerate(leaders[:10], 1):
            if i == 1:
                rank_color = COLORS['gold']
                rank_text = "🥇"
                bg_color = COLORS['background_medium']
            elif i == 2:
                rank_color = COLORS['silver']
                rank_text = "🥈"
                bg_color = COLORS['background_medium']
            elif i == 3:
                rank_color = COLORS['bronze']
                rank_text = "🥉"
                bg_color = COLORS['background_medium']
            else:
                rank_color = COLORS['text_light']
                rank_text = f"{i}"
                bg_color = "none"
            
            player_items.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": rank_text,
                        "size": "xl" if i <= 3 else "lg",
                        "color": rank_color,
                        "weight": "bold",
                        "flex": 0,
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": leader['display_name'],
                        "size": "md",
                        "color": COLORS['text_dark'] if i <= 3 else COLORS['text_light'],
                        "flex": 3,
                        "margin": "md",
                        "wrap": True,
                        "weight": "bold" if i <= 3 else "regular"
                    },
                    {
                        "type": "text",
                        "text": str(leader['total_points']),
                        "size": "md",
                        "color": COLORS['glow'],
                        "flex": 1,
                        "align": "end",
                        "weight": "bold"
                    }
                ],
                "paddingAll": "md",
                "margin": "sm" if i > 1 else "none",
                "backgroundColor": bg_color,
                "cornerRadius": "md" if i <= 3 else "none"
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
                        "text": "🏆 لوحة الصدارة",
                        "weight": "bold",
                        "size": "xxl",
                        "color": COLORS['white'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "أفضل 10 لاعبين",
                        "size": "sm",
                        "color": COLORS['light'],
                        "align": "center",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": COLORS['background'],
                "paddingAll": "24px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": player_items,
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px",
                "spacing": "none"
            },
            "footer": {
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
                "backgroundColor": COLORS['background_medium'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def registration_success(display_name):
        """نجاح التسجيل"""
        return {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "✅",
                        "size": "5xl",
                        "align": "center",
                        "color": COLORS['success']
                    },
                    {
                        "type": "text",
                        "text": "تم التسجيل بنجاح",
                        "weight": "bold",
                        "size": "xl",
                        "color": COLORS['white'],
                        "align": "center",
                        "margin": "md"
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
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": display_name,
                                "size": "xl",
                                "color": COLORS['glow'],
                                "align": "center",
                                "wrap": True,
                                "weight": "bold"
                            },
                            {
                                "type": "text",
                                "text": "مرحباً بك في بوت الحوت ",
                                "size": "sm",
                                "color": COLORS['text_light'],
                                "align": "center",
                                "margin": "md",
                                "wrap": True
                            }
                        ],
                        "backgroundColor": COLORS['background_medium'],
                        "paddingAll": "lg",
                        "cornerRadius": "lg"
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
                                "text": "🎮 9 ألعاب في انتظارك",
                                "size": "sm",
                                "color": COLORS['text_dark'],
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "🏆 تنافس واجمع النقاط",
                                "size": "sm",
                                "color": COLORS['text_dark'],
                                "align": "center",
                                "margin": "sm"
                            },
                            {
                                "type": "text",
                                "text": "⚡ تحديات يومية جديدة",
                                "size": "sm",
                                "color": COLORS['text_dark'],
                                "align": "center",
                                "margin": "sm"
                            }
                        ],
                        "margin": "lg"
                    }
                ],
                "paddingAll": "24px",
                "backgroundColor": COLORS['card_bg'],
                "spacing": "none"
            },
            "footer": {
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
                        "margin": "md"
                    }
                ],
                "backgroundColor": COLORS['background_medium'],
                "paddingAll": "20px",
                "spacing": "none"
            }
        }
    
    # Helper Methods
    
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
                    "flex": 3
                },
                {
                    "type": "text",
                    "text": value,
                    "size": "lg",
                    "color": COLORS['text_dark'],
                    "flex": 2,
                    "align": "end",
                    "weight": "bold"
                }
            ],
            "paddingAll": "sm"
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
                        "align": "center",
                        "color": COLORS['text_light']
                    },
                    {
                        "type": "text",
                        "text": "لم تبدأ بعد",
                        "size": "xl",
                        "color": COLORS['text_dark'],
                        "align": "center",
                        "weight": "bold",
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": "سجل الآن وابدأ اللعب لجمع النقاط",
                        "size": "sm",
                        "color": COLORS['text_light'],
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
                        "type": "button",
                        "action": {"type": "message", "label": "🚀 ابدأ الآن", "text": "انضم"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm",
                        "margin": "xl"
                    }
                ],
                "paddingAll": "xxl",
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
                        "align": "center",
                        "color": COLORS['text_light']
                    },
                    {
                        "type": "text",
                        "text": "لا توجد بيانات",
                        "size": "xl",
                        "color": COLORS['text_dark'],
                        "align": "center",
                        "weight": "bold",
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": "كن أول من يسجل ويتصدر اللوحة",
                        "size": "sm",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "margin": "md",
                        "wrap": True
                    }
                ],
                "paddingAll": "xxl",
                "backgroundColor": COLORS['card_bg']
            }
        }
