from constants import COLORS

class UIBuilder:

    @staticmethod
    def welcome_card(display_name, is_registered=False):
        """نافذة البداية - تصميم احترافي"""
        # أزرار التسجيل الثلاثة
        if is_registered:
            registration_status = f"مسجل | {display_name}"
            status_color = COLORS['success']
            registration_buttons = {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "تسجيل", "text": "تسجيل"},
                        "style": "secondary",
                        "height": "sm",
                        "flex": 1
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "تغيير", "text": "تغيير"},
                        "style": "secondary",
                        "height": "sm",
                        "flex": 1,
                        "margin": "xs"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "انسحب", "text": "انسحب"},
                        "style": "secondary",
                        "height": "sm",
                        "flex": 1,
                        "margin": "xs"
                    }
                ],
                "spacing": "xs"
            }
        else:
            registration_status = "غير مسجل"
            status_color = COLORS['warning']
            registration_buttons = {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "تسجيل", "text": "تسجيل"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm",
                        "flex": 2
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "تغيير", "text": "تغيير"},
                        "style": "secondary",
                        "height": "sm",
                        "flex": 1,
                        "margin": "xs"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "انسحب", "text": "انسحب"},
                        "style": "secondary",
                        "height": "sm",
                        "flex": 1,
                        "margin": "xs"
                    }
                ],
                "spacing": "xs"
            }
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}
                        ],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "12px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "مرحباً", "size": "lg", "color": COLORS['text_dark'], "weight": "bold", "align": "center"},
                            {"type": "text", "text": registration_status, "size": "md", "color": status_color, "margin": "xs", "align": "center", "weight": "bold"}
                        ],
                        "margin": "lg"
                    },
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "الحساب", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                            registration_buttons
                        ],
                        "margin": "lg",
                        "spacing": "sm"
                    },
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "الإحصائيات", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {"type": "button", "action": {"type": "message", "label": "نقاطي", "text": "نقاطي"}, "style": "secondary", "height": "sm", "flex": 1},
                                    {"type": "button", "action": {"type": "message", "label": "الصدارة", "text": "الصدارة"}, "style": "secondary", "height": "sm", "flex": 1, "margin": "xs"}
                                ],
                                "spacing": "xs",
                                "margin": "sm"
                            }
                        ],
                        "margin": "md"
                    },
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "القوائم", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {"type": "button", "action": {"type": "message", "label": "ألعاب", "text": "ألعاب"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "flex": 1},
                                    {"type": "button", "action": {"type": "message", "label": "مساعدة", "text": "مساعدة"}, "style": "secondary", "height": "sm", "flex": 1, "margin": "xs"}
                                ],
                                "spacing": "xs",
                                "margin": "sm"
                            }
                        ],
                        "margin": "md"
                    }
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }

    @staticmethod
    def games_menu_card(is_registered):
        """قائمة الألعاب - تصميم شبكي أنيق"""
        game_buttons_row1 = {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {"type": "button", "action": {"type": "message", "label": "اغنيه", "text": "اغنيه"}, "style": "secondary", "height": "sm", "flex": 1},
                {"type": "button", "action": {"type": "message", "label": "ضد", "text": "ضد"}, "style": "secondary", "height": "sm", "flex": 1, "margin": "xs"},
                {"type": "button", "action": {"type": "message", "label": "تكوين", "text": "تكوين"}, "style": "secondary", "height": "sm", "flex": 1, "margin": "xs"}
            ],
            "spacing": "xs"
        }
        
        game_buttons_row2 = {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {"type": "button", "action": {"type": "message", "label": "سلسله", "text": "سلسله"}, "style": "secondary", "height": "sm", "flex": 1},
                {"type": "button", "action": {"type": "message", "label": "اسرع", "text": "اسرع"}, "style": "secondary", "height": "sm", "flex": 1, "margin": "xs"},
                {"type": "button", "action": {"type": "message", "label": "لعبه", "text": "لعبه"}, "style": "secondary", "height": "sm", "flex": 1, "margin": "xs"}
            ],
            "spacing": "xs",
            "margin": "xs"
        }
        
        game_buttons_row3 = {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {"type": "button", "action": {"type": "message", "label": "فئة", "text": "فئه"}, "style": "secondary", "height": "sm", "flex": 1},
                {"type": "button", "action": {"type": "message", "label": "مافيا", "text": "مافيا"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "flex": 1, "margin": "xs"}
            ],
            "spacing": "xs",
            "margin": "xs"
        }
        
        note_text = "تحتاج للتسجيل أولاً" if not is_registered else "استمتع باللعب"
        note_color = COLORS['error'] if not is_registered else COLORS['success']
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "قائمة الألعاب", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}
                        ],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "12px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": note_text, "size": "sm", "color": note_color, "align": "center", "weight": "bold"}
                        ],
                        "margin": "lg"
                    },
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            game_buttons_row1,
                            game_buttons_row2,
                            game_buttons_row3
                        ],
                        "margin": "md"
                    },
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "العودة للبداية", "text": "بداية"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm",
                        "margin": "md"
                    }
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }

    @staticmethod
    def help_card():
        """نافذة المساعدة - منظمة ومرتبة"""
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "دليل الأوامر", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}
                        ],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "12px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "الأساسية", "size": "md", "color": COLORS['primary'], "weight": "bold"},
                            {"type": "text", "text": "بداية • تسجيل • نقاطي • الصدارة", "size": "sm", "color": COLORS['text_light'], "margin": "sm", "wrap": True}
                        ],
                        "margin": "lg"
                    },
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "بدون تسجيل", "size": "md", "color": COLORS['primary'], "weight": "bold"},
                            {"type": "text", "text": "سؤال • تحدي • اعتراف • منشن • توافق", "size": "sm", "color": COLORS['text_light'], "margin": "sm", "wrap": True}
                        ],
                        "margin": "md"
                    },
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "الألعاب", "size": "md", "color": COLORS['primary'], "weight": "bold"},
                            {"type": "text", "text": "فئة • أغنية • ضد • تكوين • سلسلة • أسرع • لعبة • مافيا", "size": "sm", "color": COLORS['text_light'], "margin": "sm", "wrap": True}
                        ],
                        "margin": "md"
                    },
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "أثناء اللعب", "size": "md", "color": COLORS['primary'], "weight": "bold"},
                            {"type": "text", "text": "لمح • جاوب • إيقاف", "size": "sm", "color": COLORS['text_light'], "margin": "sm"}
                        ],
                        "margin": "md"
                    },
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "النقاط", "size": "md", "color": COLORS['success'], "weight": "bold"},
                            {"type": "text", "text": "إجابة صحيحة = 1 نقطة\nتلميح أو جاوب = 0 نقطة", "size": "xs", "color": COLORS['text_light'], "margin": "sm", "wrap": True}
                        ],
                        "margin": "md"
                    },
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "العودة للبداية", "text": "بداية"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm",
                        "margin": "md"
                    }
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }

    @staticmethod
    def stats_card(display_name, stats):
        """نافذة الإحصائيات - عرض جذاب"""
        if not stats:
            stats = {'total_points': 0, 'games_played': 0, 'wins': 0}
        
        win_rate = round((stats['wins'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0)
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "إحصائياتك", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}
                        ],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "12px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": display_name, "size": "xl", "color": COLORS['text_dark'], "align": "center", "weight": "bold"}
                        ],
                        "margin": "lg"
                    },
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {"type": "text", "text": "النقاط", "size": "sm", "color": COLORS['text_light'], "flex": 0},
                                    {"type": "text", "text": str(stats['total_points']), "size": "xl", "color": COLORS['primary'], "weight": "bold", "align": "end"}
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {"type": "text", "text": "الألعاب", "size": "sm", "color": COLORS['text_light'], "flex": 0},
                                    {"type": "text", "text": str(stats['games_played']), "size": "lg", "color": COLORS['text_dark'], "weight": "bold", "align": "end"}
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {"type": "text", "text": "الفوز", "size": "sm", "color": COLORS['text_light'], "flex": 0},
                                    {"type": "text", "text": str(stats['wins']), "size": "lg", "color": COLORS['success'], "weight": "bold", "align": "end"}
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {"type": "text", "text": "نسبة الفوز", "size": "sm", "color": COLORS['text_light'], "flex": 0},
                                    {"type": "text", "text": f"{win_rate}%", "size": "lg", "color": COLORS['primary'], "weight": "bold", "align": "end"}
                                ]
                            }
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
        """نافذة لوحة الصدارة - تصميم أنيق"""
        leader_contents = []
        
        for i, l in enumerate(leaders[:20]):
            rank = f"{i+1}."
            
            leader_contents.append({
                "type": "box",
                "layout": "baseline",
                "contents": [
                    {"type": "text", "text": rank, "size": "sm", "flex": 0, "margin": "none"},
                    {"type": "text", "text": l['display_name'], "size": "sm", "color": COLORS['text_dark'], "flex": 3, "margin": "sm"},
                    {"type": "text", "text": str(l['total_points']), "size": "sm", "color": COLORS['primary'], "weight": "bold", "align": "end", "flex": 1}
                ],
                "margin": "md" if i > 0 else "sm"
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
                "spacing": "md",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "لوحة الصدارة", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}
                        ],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "12px"
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

    @staticmethod
    def all_players_card(players):
        """نافذة جميع اللاعبين"""
        player_contents = []
        
        for i, p in enumerate(players[:30]):
            status = "نشط" if p.get('active', True) else "غير نشط"
            
            player_contents.append({
                "type": "box",
                "layout": "baseline",
                "contents": [
                    {"type": "text", "text": status, "size": "xs", "flex": 0},
                    {"type": "text", "text": p['display_name'], "size": "sm", "color": COLORS['text_dark'], "flex": 3, "margin": "sm"},
                    {"type": "text", "text": str(p['total_points']), "size": "sm", "color": COLORS['text_light'], "align": "end", "flex": 1}
                ],
                "margin": "md" if i > 0 else "sm"
            })
        
        if not player_contents:
            player_contents.append({
                "type": "text",
                "text": "لا يوجد لاعبون",
                "size": "sm",
                "color": COLORS['text_light'],
                "align": "center"
            })
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "جميع اللاعبين", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}
                        ],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "12px"
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "contents": [
                            {"type": "text", "text": "نشط", "size": "xs", "color": COLORS['success'], "flex": 1},
                            {"type": "text", "text": "غير نشط", "size": "xs", "color": COLORS['text_light'], "flex": 1}
                        ],
                        "margin": "lg"
                    },
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": player_contents,
                        "margin": "md"
                    }
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
