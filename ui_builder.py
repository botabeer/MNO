from constants import COLORS

class UIBuilder:
    
    @staticmethod
    def _create_header(title, subtitle=None):
        contents = [{"type": "text", "text": title, "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}]
        if subtitle:
            contents.append({"type": "text", "text": subtitle, "size": "sm", "color": COLORS['white'], "align": "center", "margin": "xs"})
        return {"type": "box", "layout": "vertical", "contents": contents, "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"}
    
    @staticmethod
    def _create_footer():
        return {"type": "box", "layout": "vertical", "contents": [
            {"type": "text", "text": "تم انشاء هذا البوت بواسطة", "size": "xxs", "color": COLORS['text_light'], "align": "center"},
            {"type": "text", "text": "عبير الدوسري 2025", "size": "xs", "color": COLORS['text_light'], "align": "center", "weight": "bold", "margin": "xs"}
        ], "margin": "md"}
    
    @staticmethod
    def _create_separator():
        return {"type": "separator", "margin": "md", "color": COLORS['border']}
    
    @staticmethod
    def _create_button(label, text, style="secondary", flex=1):
        return {"type": "button", "action": {"type": "message", "label": label, "text": text}, "style": style, "height": "sm", "flex": flex, "color": COLORS['primary'] if style == "primary" else None}
    
    @staticmethod
    def welcome_card(display_name, is_registered=False):
        status = f"مسجل | {display_name}" if is_registered else "غير مسجل"
        status_color = COLORS['success'] if is_registered else COLORS['warning']
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    UIBuilder._create_header("بوت الحوت"),
                    {"type": "box", "layout": "vertical", "contents": [
                        {"type": "text", "text": "مرحبا", "size": "lg", "color": COLORS['text_dark'], "weight": "bold", "align": "center"},
                        {"type": "text", "text": status, "size": "md", "color": status_color, "margin": "xs", "align": "center", "weight": "bold"}
                    ], "margin": "lg"},
                    UIBuilder._create_separator(),
                    {"type": "box", "layout": "vertical", "spacing": "sm", "contents": [
                        {"type": "text", "text": "الحساب", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                        {"type": "box", "layout": "horizontal", "spacing": "xs", "contents": [
                            UIBuilder._create_button("تسجيل", "تسجيل", "primary"),
                            UIBuilder._create_button("تغيير", "تغيير"),
                            UIBuilder._create_button("انسحب", "انسحب")
                        ]}
                    ]},
                    UIBuilder._create_separator(),
                    {"type": "box", "layout": "vertical", "spacing": "sm", "contents": [
                        {"type": "text", "text": "الاحصائيات", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                        {"type": "box", "layout": "horizontal", "spacing": "xs", "contents": [
                            UIBuilder._create_button("نقاطي", "نقاطي"),
                            UIBuilder._create_button("الصدارة", "الصدارة")
                        ]}
                    ]},
                    UIBuilder._create_separator(),
                    {"type": "box", "layout": "vertical", "spacing": "sm", "contents": [
                        {"type": "text", "text": "القوائم", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                        {"type": "box", "layout": "horizontal", "spacing": "xs", "contents": [
                            UIBuilder._create_button("العاب", "العاب", "primary"),
                            UIBuilder._create_button("مساعدة", "مساعدة")
                        ]}
                    ]},
                    UIBuilder._create_separator(),
                    UIBuilder._create_footer()
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def games_menu_card(is_registered):
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    UIBuilder._create_header("بوت الحوت", "قائمة الالعاب"),
                    {"type": "text", "text": "استمتع باللعب", "align": "center", "color": COLORS['success']},
                    {"type": "box", "layout": "vertical", "spacing": "xs", "contents": [
                        {"type": "box", "layout": "horizontal", "contents": [
                            UIBuilder._create_button("اغنيه", "اغنيه"),
                            UIBuilder._create_button("ضد", "ضد"),
                            UIBuilder._create_button("تكوين", "تكوين")
                        ], "spacing": "xs"},
                        {"type": "box", "layout": "horizontal", "contents": [
                            UIBuilder._create_button("سلسله", "سلسله"),
                            UIBuilder._create_button("اسرع", "اسرع"),
                            UIBuilder._create_button("لعبه", "لعبه")
                        ], "spacing": "xs"},
                        {"type": "box", "layout": "horizontal", "contents": [
                            UIBuilder._create_button("توافق", "توافق"),
                            UIBuilder._create_button("فئة", "فئه"),
                            UIBuilder._create_button("مافيا", "مافيا", "primary")
                        ], "spacing": "xs"}
                    ]},
                    UIBuilder._create_separator(),
                    {"type": "text", "text": "العاب ترفيهية بدون تسجيل", "align": "center", "color": COLORS['warning']},
                    {"type": "box", "layout": "horizontal", "contents": [
                        UIBuilder._create_button("سؤال", "سؤال"),
                        UIBuilder._create_button("منشن", "منشن")
                    ], "spacing": "xs"},
                    {"type": "box", "layout": "horizontal", "contents": [
                        UIBuilder._create_button("اعتراف", "اعتراف"),
                        UIBuilder._create_button("تحدي", "تحدي")
                    ], "spacing": "xs"},
                    UIBuilder._create_separator(),
                    UIBuilder._create_button("العودة للبداية", "بداية", "primary"),
                    UIBuilder._create_separator(),
                    UIBuilder._create_footer()
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def help_card():
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    UIBuilder._create_header("دليل الاوامر"),
                    {"type": "box", "layout": "vertical", "contents": [
                        {"type": "text", "text": "الاساسية", "size": "md", "color": COLORS['primary'], "weight": "bold"},
                        {"type": "text", "text": "بداية - تسجيل - نقاطي - الصدارة", "size": "sm", "color": COLORS['text_light'], "margin": "sm", "wrap": True}
                    ], "margin": "lg"},
                    UIBuilder._create_separator(),
                    {"type": "box", "layout": "vertical", "contents": [
                        {"type": "text", "text": "بدون تسجيل", "size": "md", "color": COLORS['primary'], "weight": "bold"},
                        {"type": "text", "text": "سؤال - تحدي - اعتراف - منشن - توافق", "size": "sm", "color": COLORS['text_light'], "margin": "sm", "wrap": True}
                    ], "margin": "md"},
                    UIBuilder._create_separator(),
                    {"type": "box", "layout": "vertical", "contents": [
                        {"type": "text", "text": "الالعاب", "size": "md", "color": COLORS['primary'], "weight": "bold"},
                        {"type": "text", "text": "فئة - اغنية - ضد - تكوين - سلسلة - اسرع - لعبة - مافيا", "size": "sm", "color": COLORS['text_light'], "margin": "sm", "wrap": True}
                    ], "margin": "md"},
                    UIBuilder._create_separator(),
                    {"type": "box", "layout": "vertical", "contents": [
                        {"type": "text", "text": "اثناء اللعب", "size": "md", "color": COLORS['primary'], "weight": "bold"},
                        {"type": "text", "text": "لمح - جاوب - ايقاف", "size": "sm", "color": COLORS['text_light'], "margin": "sm"}
                    ], "margin": "md"},
                    UIBuilder._create_separator(),
                    {"type": "box", "layout": "vertical", "contents": [
                        {"type": "text", "text": "النقاط", "size": "md", "color": COLORS['success'], "weight": "bold"},
                        {"type": "text", "text": "اجابة صحيحة = 1 نقطة | تلميح او جاوب = 0 نقطة", "size": "xs", "color": COLORS['text_light'], "margin": "sm", "wrap": True}
                    ], "margin": "md"},
                    UIBuilder._create_separator(),
                    UIBuilder._create_button("العودة للبداية", "بداية", "primary"),
                    UIBuilder._create_separator(),
                    UIBuilder._create_footer()
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def stats_card(display_name, stats):
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
                    UIBuilder._create_header("احصائياتك"),
                    {"type": "box", "layout": "vertical", "contents": [
                        {"type": "text", "text": display_name, "size": "xl", "color": COLORS['text_dark'], "align": "center", "weight": "bold"}
                    ], "margin": "lg"},
                    UIBuilder._create_separator(),
                    {"type": "box", "layout": "vertical", "spacing": "md", "contents": [
                        {"type": "box", "layout": "baseline", "contents": [
                            {"type": "text", "text": "النقاط", "size": "sm", "color": COLORS['text_light'], "flex": 0},
                            {"type": "text", "text": str(stats['total_points']), "size": "xl", "color": COLORS['primary'], "weight": "bold", "align": "end"}
                        ]},
                        {"type": "box", "layout": "baseline", "contents": [
                            {"type": "text", "text": "الالعاب", "size": "sm", "color": COLORS['text_light'], "flex": 0},
                            {"type": "text", "text": str(stats['games_played']), "size": "lg", "color": COLORS['text_dark'], "weight": "bold", "align": "end"}
                        ]},
                        {"type": "box", "layout": "baseline", "contents": [
                            {"type": "text", "text": "الفوز", "size": "sm", "color": COLORS['text_light'], "flex": 0},
                            {"type": "text", "text": str(stats['wins']), "size": "lg", "color": COLORS['success'], "weight": "bold", "align": "end"}
                        ]},
                        {"type": "box", "layout": "baseline", "contents": [
                            {"type": "text", "text": "نسبة الفوز", "size": "sm", "color": COLORS['text_light'], "flex": 0},
                            {"type": "text", "text": f"{win_rate}%", "size": "lg", "color": COLORS['primary'], "weight": "bold", "align": "end"}
                        ]}
                    ], "margin": "lg"}
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def leaderboard_card(leaders):
        leader_contents = []
        for i, l in enumerate(leaders[:20]):
            leader_contents.append({
                "type": "box", "layout": "baseline",
                "contents": [
                    {"type": "text", "text": f"{i+1}.", "size": "sm", "flex": 0, "margin": "none"},
                    {"type": "text", "text": l['display_name'], "size": "sm", "color": COLORS['text_dark'], "flex": 3, "margin": "sm"},
                    {"type": "text", "text": str(l['total_points']), "size": "sm", "color": COLORS['primary'], "weight": "bold", "align": "end", "flex": 1}
                ],
                "margin": "md" if i > 0 else "sm"
            })
        
        if not leader_contents:
            leader_contents.append({"type": "text", "text": "لا توجد احصائيات بعد", "size": "sm", "color": COLORS['text_light'], "align": "center"})
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    UIBuilder._create_header("لوحة الصدارة"),
                    {"type": "box", "layout": "vertical", "contents": leader_contents, "margin": "lg"}
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def all_players_card(players):
        player_contents = []
        for i, p in enumerate(players[:30]):
            status = "نشط" if p.get('active', True) else "غير نشط"
            player_contents.append({
                "type": "box", "layout": "baseline",
                "contents": [
                    {"type": "text", "text": status, "size": "xs", "flex": 0},
                    {"type": "text", "text": p['display_name'], "size": "sm", "color": COLORS['text_dark'], "flex": 3, "margin": "sm"},
                    {"type": "text", "text": str(p['total_points']), "size": "sm", "color": COLORS['text_light'], "align": "end", "flex": 1}
                ],
                "margin": "md" if i > 0 else "sm"
            })
        
        if not player_contents:
            player_contents.append({"type": "text", "text": "لا يوجد لاعبون", "size": "sm", "color": COLORS['text_light'], "align": "center"})
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    UIBuilder._create_header("جميع اللاعبين"),
                    {"type": "box", "layout": "baseline", "contents": [
                        {"type": "text", "text": "نشط", "size": "xs", "color": COLORS['success'], "flex": 1},
                        {"type": "text", "text": "غير نشط", "size": "xs", "color": COLORS['text_light'], "flex": 1}
                    ], "margin": "lg"},
                    UIBuilder._create_separator(),
                    {"type": "box", "layout": "vertical", "contents": player_contents, "margin": "md"}
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def registration_card():
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    UIBuilder._create_header("التسجيل"),
                    {"type": "text", "text": "اكتب اسمك للتسجيل", "size": "md", "color": COLORS['text_dark'], "align": "center", "margin": "lg"},
                    {"type": "text", "text": "الحد الاقصى 30 حرف", "size": "xs", "color": COLORS['text_light'], "align": "center", "margin": "sm"}
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def registration_success_card(name):
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    UIBuilder._create_header("تم التسجيل بنجاح"),
                    {"type": "text", "text": f"مرحبا {name}", "size": "xl", "color": COLORS['success'], "align": "center", "weight": "bold", "margin": "lg"}
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def already_registered_card(name):
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    UIBuilder._create_header("مسجل بالفعل"),
                    {"type": "text", "text": f"انت مسجل باسم: {name}", "size": "md", "color": COLORS['text_dark'], "align": "center", "margin": "lg"}
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def welcome_back_card(name):
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    UIBuilder._create_header("مرحبا بعودتك"),
                    {"type": "text", "text": f"تم اعادة تفعيل حسابك: {name}", "size": "md", "color": COLORS['success'], "align": "center", "margin": "lg"}
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def change_name_card(old_name):
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    UIBuilder._create_header("تغيير الاسم"),
                    {"type": "text", "text": f"الاسم الحالي: {old_name}", "size": "sm", "color": COLORS['text_light'], "align": "center", "margin": "lg"},
                    {"type": "text", "text": "اكتب الاسم الجديد", "size": "md", "color": COLORS['text_dark'], "align": "center", "margin": "sm"}
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def name_changed_card(new_name):
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    UIBuilder._create_header("تم تغيير الاسم"),
                    {"type": "text", "text": f"الاسم الجديد: {new_name}", "size": "xl", "color": COLORS['success'], "align": "center", "weight": "bold", "margin": "lg"}
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def need_registration_card():
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    UIBuilder._create_header("يجب التسجيل اولا"),
                    {"type": "text", "text": "اكتب تسجيل للبدء", "size": "md", "color": COLORS['text_dark'], "align": "center", "margin": "lg"},
                    UIBuilder._create_separator(),
                    UIBuilder._create_button("تسجيل الان", "تسجيل", "primary")
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
