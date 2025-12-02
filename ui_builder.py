from constants import COLORS

class UIBuilder:

    @staticmethod
    def welcome_card(display_name, is_registered=False):
        """نافذة البداية"""
        if is_registered:
            register_button = {
                "type": "button",
                "action": {"type": "message", "label": "تغيير الاسم ✏️", "text": "تغيير الاسم"},
                "style": "secondary",
                "height": "sm"
            }
            unregister_button = {
                "type": "button",
                "action": {"type": "message", "label": "انسحب", "text": "انسحب"},
                "style": "secondary",
                "height": "sm",
                "margin": "sm"
            }
            registration_status = f"مسجل باسم: {display_name}"
            status_color = COLORS['success']
        else:
            register_button = {
                "type": "button",
                "action": {"type": "message", "label": "تسجيل جديد 📝", "text": "تسجيل"},
                "style": "primary",
                "color": COLORS['primary'],
                "height": "sm"
            }
            unregister_button = None
            registration_status = "غير مسجل"
            status_color = COLORS['text_light']
        
        button_contents = [register_button]
        if unregister_button:
            button_contents.append(unregister_button)
        
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
                            {"type": "text","size": "xxl", "align": "center"},
                            {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center", "margin": "md"}
                        ],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "12px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "مرحباً 👋", "size": "lg", "color": COLORS['text_dark'], "weight": "bold", "align": "center"},
                            {"type": "text", "text": registration_status, "size": "sm", "color": status_color, "margin": "xs", "align": "center"},
                            {"type": "separator", "margin": "md", "color": COLORS['border']},
                            {"type": "text", "text": "يمكنك استخدام البوت في الخاص والقروبات", "size": "xs", "color": COLORS['text_light'], "margin": "md", "wrap": True, "align": "center"}
                        ],
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "🎮 التسجيل", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                            *button_contents
                        ],
                        "margin": "lg",
                        "spacing": "sm"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "📊 الإحصائيات", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {"type": "button", "action": {"type": "message", "label": "نقاطي", "text": "نقاطي"}, "style": "secondary", "height": "sm", "flex": 1},
                                    {"type": "button", "action": {"type": "message", "label": "الصدارة", "text": "الصدارة"}, "style": "secondary", "height": "sm", "flex": 1}
                                ],
                                "spacing": "sm",
                                "margin": "sm"
                            }
                        ],
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "🎲 القوائم", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {"type": "button", "action": {"type": "message", "label": "الألعاب", "text": "ألعاب"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "flex": 1},
                                    {"type": "button", "action": {"type": "message", "label": "مساعدة", "text": "مساعدة"}, "style": "secondary", "height": "sm", "flex": 1}
                                ],
                                "spacing": "sm",
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
        """قائمة الألعاب"""
        game_buttons = [
            {"label": "🎵 أغنية", "text": "اغنيه"},
            {"label": "🔄 ضد", "text": "ضد"},
            {"label": "🔤 تكوين", "text": "تكوين"},
            {"label": "🔗 سلسلة", "text": "سلسله"},
            {"label": "⚡ أسرع", "text": "اسرع"},
            {"label": "🌍 لعبة", "text": "لعبه"},
            {"label": "🎯 فئة", "text": "فئه"},
            {"label": "🕵️ مافيا", "text": "مافيا"}
        ]
        
        buttons = []
        for i, btn in enumerate(game_buttons):
            buttons.append({
                "type": "button",
                "action": {"type": "message", "label": btn["label"], "text": btn["text"]},
                "style": "secondary",
                "height": "sm",
                "margin": "xs" if i > 0 else "none"
            })
        
        note_text = "⚠️ تحتاج للتسجيل أولاً" if not is_registered else "✅ استمتع باللعب!"
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
                            {"type": "text", "text": "🎮", "size": "xxl", "align": "center"},
                            {"type": "text", "text": "قائمة الألعاب", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center", "margin": "md"}
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
                        "contents": buttons,
                        "margin": "md",
                        "spacing": "xs"
                    },
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "🏠 العودة للبداية", "text": "بداية"},
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
        """نافذة المساعدة"""
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
                            {"type": "text", "text": "❓", "size": "xxl", "align": "center"},
                            {"type": "text", "text": "دليل الأوامر", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center", "margin": "md"}
                        ],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "12px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "الأوامر الأساسية", "size": "md", "color": COLORS['primary'], "weight": "bold"},
                            {"type": "text", "text": "بداية • تسجيل • نقاطي • الصدارة", "size": "sm", "color": COLORS['text_light'], "margin": "sm", "wrap": True}
                        ],
                        "margin": "lg"
                    },
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "أوامر بدون تسجيل", "size": "md", "color": COLORS['primary'], "weight": "bold"},
                            {"type": "text", "text": "سؤال • تحدي • اعتراف • منشن • توافق", "size": "sm", "color": COLORS['text_light'], "margin": "sm", "wrap": True}
                        ],
                        "margin": "md"
                    },
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "الألعاب مع نقاط", "size": "md", "color": COLORS['primary'], "weight": "bold"},
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
                            {"type": "text", "text": "نظام النقاط", "size": "md", "color": COLORS['success'], "weight": "bold"},
                            {"type": "text", "text": "✅ إجابة صحيحة = 1 نقطة\n⚠️ تلميح / جاوب = 0 نقطة", "size": "xs", "color": COLORS['text_light'], "margin": "sm", "wrap": True}
                        ],
                        "margin": "md"
                    },
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "🏠 العودة للبداية", "text": "بداية"},
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
        """نافذة الإحصائيات"""
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
                            {"type": "text", "text": "📊", "size": "xxl", "align": "center"},
                            {"type": "text", "text": "إحصائياتك", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center", "margin": "md"}
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
        """نافذة لوحة الصدارة"""
        leader_contents = []
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, l in enumerate(leaders[:20]):
            medal = medals[i] if i < 3 else f"{i+1}."
            
            leader_contents.append({
                "type": "box",
                "layout": "baseline",
                "contents": [
                    {"type": "text", "text": medal, "size": "sm", "flex": 0, "margin": "none"},
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
                            {"type": "text", "text": "🏆", "size": "xxl", "align": "center"},
                            {"type": "text", "text": "لوحة الصدارة", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center", "margin": "md"}
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
            status = "✅" if p.get('active', True) else "💤"
            
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
                            {"type": "text", "text": "👥", "size": "xxl", "align": "center"},
                            {"type": "text", "text": "جميع اللاعبين", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center", "margin": "md"}
                        ],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "12px"
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "contents": [
                            {"type": "text", "text": "✅ نشط", "size": "xs", "color": COLORS['success'], "flex": 1},
                            {"type": "text", "text": "💤 غير نشط", "size": "xs", "color": COLORS['text_light'], "flex": 1}
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
