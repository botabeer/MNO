from constants import COLORS

class UIBuilder:
    
    @staticmethod
    def welcome_card(display_name, is_registered=False):
        if is_registered:
            registration_status = f"مسجل | {display_name}"
            status_color = COLORS['success']
        else:
            registration_status = "غير مسجل"
            status_color = COLORS['warning']

        registration_buttons = {
            "type": "box",
            "layout": "horizontal",
            "spacing": "xs",
            "contents": [
                {"type": "button", "action": {"type": "message", "label": "تسجيل", "text": "تسجيل"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "flex": 1},
                {"type": "button", "action": {"type": "message", "label": "تغيير", "text": "تغيير"}, "style": "secondary", "height": "sm", "flex": 1},
                {"type": "button", "action": {"type": "message", "label": "انسحب", "text": "انسحب"}, "style": "secondary", "height": "sm", "flex": 1}
            ]
        }

        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                    {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "مرحبا", "size": "lg", "color": COLORS['text_dark'], "weight": "bold", "align": "center"}, {"type": "text", "text": registration_status, "size": "md", "color": status_color, "margin": "xs", "align": "center", "weight": "bold"}], "margin": "lg"},
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {"type": "box", "layout": "vertical", "spacing": "sm", "contents": [{"type": "text", "text": "الحساب", "size": "md", "color": COLORS['text_dark'], "weight": "bold"}, registration_buttons]},
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {"type": "box", "layout": "vertical", "spacing": "sm", "contents": [{"type": "text", "text": "الاحصائيات", "size": "md", "color": COLORS['text_dark'], "weight": "bold"}, {"type": "box", "layout": "horizontal", "spacing": "xs", "contents": [{"type": "button", "action": {"type": "message", "label": "نقاطي", "text": "نقاطي"}, "style": "secondary", "height": "sm", "flex": 1}, {"type": "button", "action": {"type": "message", "label": "الصدارة", "text": "الصدارة"}, "style": "secondary", "height": "sm", "flex": 1}]}]},
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {"type": "box", "layout": "vertical", "spacing": "sm", "contents": [{"type": "text", "text": "القوائم", "size": "md", "color": COLORS['text_dark'], "weight": "bold"}, {"type": "box", "layout": "horizontal", "spacing": "xs", "contents": [{"type": "button", "action": {"type": "message", "label": "العاب", "text": "العاب"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "flex": 1}, {"type": "button", "action": {"type": "message", "label": "مساعدة", "text": "مساعدة"}, "style": "secondary", "height": "sm", "flex": 1}]}]},
                    {"type": "separator", "margin": "lg", "color": COLORS['border']},
                    {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "تم انشاء هذا البوت بواسطة", "size": "xxs", "color": COLORS['text_light'], "align": "center"}, {"type": "text", "text": "عبير الدوسري 2025", "size": "xs", "color": COLORS['text_light'], "align": "center", "weight": "bold", "margin": "xs"}], "margin": "md"}
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
                    {"type": "box", "layout": "vertical", "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px", "contents": [{"type": "text", "text": "بوت الحوت", "size": "lg", "weight": "bold", "color": COLORS['white'], "align": "center"}, {"type": "text", "text": "قائمة الالعاب", "size": "sm", "color": COLORS['white'], "align": "center"}]},
                    {"type": "text", "text": "استمتع باللعب", "align": "center", "color": COLORS['success']},
                    {"type": "box", "layout": "vertical", "spacing": "xs", "contents": [{"type": "box", "layout": "horizontal", "contents": [{"type": "button", "action": {"type": "message", "label": "اغنيه", "text": "اغنيه"}, "flex": 1, "style": "secondary", "height": "sm"}, {"type": "button", "action": {"type": "message", "label": "ضد", "text": "ضد"}, "flex": 1, "style": "secondary", "height": "sm"}, {"type": "button", "action": {"type": "message", "label": "تكوين", "text": "تكوين"}, "flex": 1, "style": "secondary", "height": "sm"}], "spacing": "xs"}, {"type": "box", "layout": "horizontal", "contents": [{"type": "button", "action": {"type": "message", "label": "سلسله", "text": "سلسله"}, "flex": 1, "style": "secondary", "height": "sm"}, {"type": "button", "action": {"type": "message", "label": "اسرع", "text": "اسرع"}, "flex": 1, "style": "secondary", "height": "sm"}, {"type": "button", "action": {"type": "message", "label": "لعبه", "text": "لعبه"}, "flex": 1, "style": "secondary", "height": "sm"}], "spacing": "xs"}, {"type": "box", "layout": "horizontal", "contents": [{"type": "button", "action": {"type": "message", "label": "توافق", "text": "توافق"}, "flex": 1, "style": "secondary", "height": "sm"}, {"type": "button", "action": {"type": "message", "label": "فئة", "text": "فئه"}, "flex": 1, "style": "secondary", "height": "sm"}, {"type": "button", "action": {"type": "message", "label": "مافيا", "text": "مافيا"}, "style": "primary", "color": COLORS['primary'], "flex": 1, "height": "sm"}], "spacing": "xs"}]},
                    {"type": "separator", "margin": "md"},
                    {"type": "text", "text": "العاب ترفيهية بدون تسجيل", "align": "center", "color": COLORS['warning']},
                    {"type": "box", "layout": "horizontal", "contents": [{"type": "button", "action": {"type": "message", "label": "سؤال", "text": "سؤال"}, "flex": 1, "style": "secondary", "height": "sm"}, {"type": "button", "action": {"type": "message", "label": "منشن", "text": "منشن"}, "flex": 1, "style": "secondary", "height": "sm"}], "spacing": "xs"},
                    {"type": "box", "layout": "horizontal", "contents": [{"type": "button", "action": {"type": "message", "label": "اعتراف", "text": "اعتراف"}, "flex": 1, "style": "secondary", "height": "sm"}, {"type": "button", "action": {"type": "message", "label": "تحدي", "text": "تحدي"}, "flex": 1, "style": "secondary", "height": "sm"}], "spacing": "xs"},
                    {"type": "separator", "margin": "md"},
                    {"type": "button", "action": {"type": "message", "label": "العودة للبداية", "text": "بداية"}, "style": "primary", "color": COLORS['primary']},
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "تم انشاء هذا البوت بواسطة", "size": "xxs", "color": COLORS['text_light'], "align": "center"}, {"type": "text", "text": "عبير الدوسري 2025", "size": "xs", "color": COLORS['text_light'], "align": "center", "weight": "bold", "margin": "xs"}], "margin": "xs"}
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
                    {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "دليل الاوامر", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                    {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "الاساسية", "size": "md", "color": COLORS['primary'], "weight": "bold"}, {"type": "text", "text": "بداية - تسجيل - نقاطي - الصدارة", "size": "sm", "color": COLORS['text_light'], "margin": "sm", "wrap": True}], "margin": "lg"},
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "بدون تسجيل", "size": "md", "color": COLORS['primary'], "weight": "bold"}, {"type": "text", "text": "سؤال - تحدي - اعتراف - منشن - توافق", "size": "sm", "color": COLORS['text_light'], "margin": "sm", "wrap": True}], "margin": "md"},
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "الالعاب", "size": "md", "color": COLORS['primary'], "weight": "bold"}, {"type": "text", "text": "فئة - اغنية - ضد - تكوين - سلسلة - اسرع - لعبة - مافيا", "size": "sm", "color": COLORS['text_light'], "margin": "sm", "wrap": True}], "margin": "md"},
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "اثناء اللعب", "size": "md", "color": COLORS['primary'], "weight": "bold"}, {"type": "text", "text": "لمح - جاوب - ايقاف", "size": "sm", "color": COLORS['text_light'], "margin": "sm"}], "margin": "md"},
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "النقاط", "size": "md", "color": COLORS['success'], "weight": "bold"}, {"type": "text", "text": "اجابة صحيحة = 1 نقطة | تلميح او جاوب = 0 نقطة", "size": "xs", "color": COLORS['text_light'], "margin": "sm", "wrap": True}], "margin": "md"},
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {"type": "button", "action": {"type": "message", "label": "العودة للبداية", "text": "بداية"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "md"},
                    {"type": "separator", "margin": "lg", "color": COLORS['border']},
                    {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "تم انشاء هذا البوت بواسطة", "size": "xxs", "color": COLORS['text_light'], "align": "center"}, {"type": "text", "text": "عبير الدوسري 2025", "size": "xs", "color": COLORS['text_light'], "align": "center", "weight": "bold", "margin": "xs"}], "margin": "md"}
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
                    {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "احصائياتك", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                    {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": display_name, "size": "xl", "color": COLORS['text_dark'], "align": "center", "weight": "bold"}], "margin": "lg"},
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {"type": "box", "layout": "vertical", "spacing": "md", "contents": [{"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": "النقاط", "size": "sm", "color": COLORS['text_light'], "flex": 0}, {"type": "text", "text": str(stats['total_points']), "size": "xl", "color": COLORS['primary'], "weight": "bold", "align": "end"}]}, {"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": "الالعاب", "size": "sm", "color": COLORS['text_light'], "flex": 0}, {"type": "text", "text": str(stats['games_played']), "size": "lg", "color": COLORS['text_dark'], "weight": "bold", "align": "end"}]}, {"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": "الفوز", "size": "sm", "color": COLORS['text_light'], "flex": 0}, {"type": "text", "text": str(stats['wins']), "size": "lg", "color": COLORS['success'], "weight": "bold", "align": "end"}]}, {"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": "نسبة الفوز", "size": "sm", "color": COLORS['text_light'], "flex": 0}, {"type": "text", "text": f"{win_rate}%", "size": "lg", "color": COLORS['primary'], "weight": "bold", "align": "end"}]}], "margin": "lg"}
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }

    @staticmethod
    def leaderboard_card(leaders):
        leader_contents = []
        
        for i, l in enumerate(leaders[:20]):
            rank = f"{i+1}."
            leader_contents.append({"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": rank, "size": "sm", "flex": 0, "margin": "none"}, {"type": "text", "text": l['display_name'], "size": "sm", "color": COLORS['text_dark'], "flex": 3, "margin": "sm"}, {"type": "text", "text": str(l['total_points']), "size": "sm", "color": COLORS['primary'], "weight": "bold", "align": "end", "flex": 1}], "margin": "md" if i > 0 else "sm"})
        
        if not leader_contents:
            leader_contents.append({"type": "text", "text": "لا توجد احصائيات بعد", "size": "sm", "color": COLORS['text_light'], "align": "center"})
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "لوحة الصدارة", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
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
            player_contents.append({"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": status, "size": "xs", "flex": 0}, {"type": "text", "text": p['display_name'], "size": "sm", "color": COLORS['text_dark'], "flex": 3, "margin": "sm"}, {"type": "text", "text": str(p['total_points']), "size": "sm", "color": COLORS['text_light'], "align": "end", "flex": 1}], "margin": "md" if i > 0 else "sm"})
        
        if not player_contents:
            player_contents.append({"type": "text", "text": "لا يوجد لاعبون", "size": "sm", "color": COLORS['text_light'], "align": "center"})
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "جميع اللاعبين", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                    {"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": "نشط", "size": "xs", "color": COLORS['success'], "flex": 1}, {"type": "text", "text": "غير نشط", "size": "xs", "color": COLORS['text_light'], "flex": 1}], "margin": "lg"},
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    {"type": "box", "layout": "vertical", "contents": player_contents, "margin": "md"}
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
