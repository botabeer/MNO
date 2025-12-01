from constants import COLORS

class UIBuilder:

    @staticmethod
    def welcome_card(display_name, is_registered=False):
        """نافذة البداية مع أزرار منظمة - زرين جنب بعض"""
        
        # صف الأزرار الأول: انضم + انسحب
        first_row = [
            {
                "type": "button",
                "action": {"type": "message", "label": "انضم", "text": "انضم"},
                "style": "secondary",
                "height": "sm",
                "flex": 1
            },
            {
                "type": "button",
                "action": {"type": "message", "label": "انسحب", "text": "انسحب"},
                "style": "secondary",
                "height": "sm",
                "flex": 1
            }
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
                            {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}
                        ],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "10px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": f"مرحباً {display_name}", "size": "lg", "color": COLORS['text_dark'], "margin": "md", "weight": "bold"},
                            {"type": "text", "text": "يمكنك استخدام البوت في الخاص والقروبات", "size": "sm", "color": COLORS['text_light'], "margin": "sm", "wrap": True}
                        ],
                        "margin": "lg"
                    },
                    {"type": "separator", "margin": "lg", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            # صف أول: انضم + انسحب
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": first_row,
                                "spacing": "sm"
                            },
                            # صف ثاني: نقاطي + الصدارة
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "نقاطي", "text": "نقاطي"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "الصدارة", "text": "الصدارة"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "flex": 1
                                    }
                                ],
                                "spacing": "sm",
                                "margin": "sm"
                            },
                            # صف ثالث: سؤال + منشن
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "سؤال", "text": "سؤال"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "منشن", "text": "منشن"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "flex": 1
                                    }
                                ],
                                "spacing": "sm",
                                "margin": "sm"
                            },
                            # صف رابع: اعتراف + تحدي
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "اعتراف", "text": "اعتراف"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "تحدي", "text": "تحدي"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "flex": 1
                                    }
                                ],
                                "spacing": "sm",
                                "margin": "sm"
                            },
                            # صف خامس: توافق + مساعدة
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "توافق", "text": "توافق"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "مساعدة", "text": "مساعدة"},
                                        "style": "secondary",
                                        "height": "sm",
                                        "flex": 1
                                    }
                                ],
                                "spacing": "sm",
                                "margin": "sm"
                            }
                        ],
                        "margin": "lg"
                    },
                    {"type": "separator", "margin": "lg", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "تم إنشاء هذا البوت بواسطة", "size": "xxs", "color": COLORS['text_light'], "align": "center"},
                            {"type": "text", "text": "عبير الدوسري @ 2025", "size": "xs", "color": COLORS['text_light'], "align": "center", "margin": "xs"}
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
        """نافذة المساعدة مع شرح واضح لجميع الأوامر"""
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
                            {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"},
                            {"type": "text", "text": "دليل الأوامر", "size": "md", "color": COLORS['white'], "align": "center", "margin": "xs"}
                        ],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "10px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "الأوامر الأساسية", "size": "md", "color": COLORS['primary'], "weight": "bold"},
                            {"type": "text", "text": "بداية - عرض القائمة الرئيسية", "size": "sm", "color": COLORS['text_light'], "margin": "sm"},
                            {"type": "text", "text": "مساعدة - عرض هذه القائمة", "size": "sm", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": "انضم - التسجيل في الألعاب", "size": "sm", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": "انسحب - إلغاء التسجيل", "size": "sm", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": "نقاطي - عرض إحصائياتك", "size": "sm", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": "الصدارة - عرض المتصدرين", "size": "sm", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": "إيقاف - إنهاء اللعبة الحالية", "size": "sm", "color": COLORS['text_light'], "margin": "xs"}
                        ],
                        "margin": "lg"
                    },
                    {"type": "separator", "margin": "lg", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "أوامر بدون تسجيل", "size": "md", "color": COLORS['primary'], "weight": "bold"},
                            {"type": "text", "text": "سؤال - سؤال عشوائي", "size": "sm", "color": COLORS['text_light'], "margin": "sm"},
                            {"type": "text", "text": "تحدي - تحدي عشوائي", "size": "sm", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": "اعتراف - اعتراف عشوائي", "size": "sm", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": "منشن - منشن عشوائي", "size": "sm", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": "توافق - حساب نسبة التوافق بين اسمين", "size": "sm", "color": COLORS['text_light'], "margin": "xs"}
                        ],
                        "margin": "lg"
                    },
                    {"type": "separator", "margin": "lg", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "ألعاب تحتاج تسجيل مع نقاط", "size": "md", "color": COLORS['primary'], "weight": "bold"},
                            {"type": "text", "text": "فئة - لعبة فئة وحرف", "size": "sm", "color": COLORS['text_light'], "margin": "sm"},
                            {"type": "text", "text": "أغنية - لعبة تخمين اسم المغني", "size": "sm", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": "ضد - لعبة الأضداد", "size": "sm", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": "تكوين - تكوين كلمات من حروف", "size": "sm", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": "سلسلة - سلسلة الكلمات", "size": "sm", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": "أسرع - لعبة الكتابة السريعة", "size": "sm", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": "لعبة - إنسان حيوان نبات بلاد", "size": "sm", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": "مافيا - لعبة المافيا الجماعية", "size": "sm", "color": COLORS['text_light'], "margin": "xs"}
                        ],
                        "margin": "lg"
                    },
                    {"type": "separator", "margin": "lg", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "أثناء اللعب", "size": "md", "color": COLORS['primary'], "weight": "bold"},
                            {"type": "text", "text": "لمح - الحصول على تلميح", "size": "sm", "color": COLORS['text_light'], "margin": "sm"},
                            {"type": "text", "text": "جاوب - عرض الإجابة الصحيحة", "size": "sm", "color": COLORS['text_light'], "margin": "xs"}
                        ],
                        "margin": "lg"
                    },
                    {"type": "separator", "margin": "lg", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "نظام النقاط", "size": "md", "color": COLORS['primary'], "weight": "bold"},
                            {"type": "text", "text": "إجابة صحيحة = 1 نقطة", "size": "sm", "color": COLORS['text_light'], "margin": "sm"},
                            {"type": "text", "text": "استخدام تلميح = 0 نقطة", "size": "sm", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": "طلب الجواب = 0 نقطة", "size": "sm", "color": COLORS['text_light'], "margin": "xs"},
                            {"type": "text", "text": "النقاط للمسجلين فقط", "size": "sm", "color": COLORS['text_dark'], "margin": "xs", "weight": "bold"}
                        ],
                        "margin": "lg"
                    },
                    {"type": "separator", "margin": "lg", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "تم إنشاء هذا البوت بواسطة", "size": "xxs", "color": COLORS['text_light'], "align": "center"},
                            {"type": "text", "text": "عبير الدوسري @ 2025", "size": "xs", "color": COLORS['text_light'], "align": "center", "margin": "xs"}
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
        """نافذة نجاح التسجيل"""
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
                            {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"},
                            {"type": "text", "text": "تم التسجيل بنجاح", "size": "md", "color": COLORS['white'], "align": "center", "margin": "xs"}
                        ],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "10px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": f"مرحباً {display_name}", "size": "lg", "color": COLORS['text_dark'], "margin": "md", "align": "center"},
                            {"type": "text", "text": "يمكنك الآن المشاركة في جميع الألعاب وكسب النقاط", "size": "sm", "color": COLORS['text_light'], "margin": "sm", "align": "center", "wrap": True}
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
        """نافذة الإحصائيات"""
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
                            {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"},
                            {"type": "text", "text": "إحصائياتك", "size": "md", "color": COLORS['white'], "align": "center", "margin": "xs"}
                        ],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "10px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": display_name, "size": "lg", "color": COLORS['text_dark'], "margin": "md", "align": "center", "weight": "bold"},
                            {"type": "text", "text": f"النقاط: {stats['total_points']}", "size": "md", "color": COLORS['text_light'], "margin": "md", "align": "center"},
                            {"type": "text", "text": f"الألعاب: {stats['games_played']}", "size": "md", "color": COLORS['text_light'], "margin": "xs", "align": "center"},
                            {"type": "text", "text": f"الفوز: {stats['wins']}", "size": "md", "color": COLORS['text_light'], "margin": "xs", "align": "center"}
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
        """نافذة لوحة الصدارة"""
        leader_contents = []
        
        for i, l in enumerate(leaders):
            leader_contents.append({
                "type": "text",
                "text": f"{i+1}. {l['display_name']} - {l['total_points']} نقطة",
                "size": "sm",
                "color": COLORS['text_light'],
                "margin": "xs"
            })
        
        if not leader_contents:
            leader_contents.append({
                "type": "text",
                "text": "لا توجد إحصائيات بعد",
                "size": "sm",
                "color": COLORS['text_light'],
                "align": "center"
            })
        
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
                            {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"},
                            {"type": "text", "text": "لوحة الصدارة", "size": "md", "color": COLORS['white'], "align": "center", "margin": "xs"}
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
