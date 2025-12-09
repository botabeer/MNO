from constants import THEMES

class UIBuilder:
    @staticmethod
    def get_colors(theme="light"):
        return THEMES.get(theme, THEMES["light"])

    @staticmethod
    def _make_action(label, text=None, action_type="message", data=None, uri=None):
        if action_type == "message":
            return {"type": "message", "label": label, "text": text or label}
        if action_type == "uri":
            return {"type": "uri", "label": label, "uri": uri}
        return {"type": action_type, "label": label, "data": data or text or label}

    @staticmethod
    def header(title, subtitle=None, icon=None, theme="light"):
        colors = UIBuilder.get_colors(theme)
        contents = []
        if icon:
            contents.append({"type": "text", "text": icon, "size": "xxl", "align": "center"})
        contents.append({
            "type": "text", "text": title, "weight": "bold", "size": "xl",
            "color": colors["white"], "align": "center", "margin": "xs" if icon else "none"
        })
        if subtitle:
            contents.append({
                "type": "text", "text": subtitle, "size": "sm",
                "color": colors["white"], "align": "center", "wrap": True, "margin": "xs"
            })
        return {
            "type": "box", "layout": "vertical", "cornerRadius": "12px",
            "backgroundColor": colors["primary"], "paddingAll": "20px", "contents": contents
        }

    @staticmethod
    def footer(theme="light"):
        colors = UIBuilder.get_colors(theme)
        return {
            "type": "box", "layout": "vertical", "margin": "lg",
            "contents": [
                {"type": "separator", "color": colors["border"]},
                {
                    "type": "text", "text": "بوت الحوت", "size": "xs",
                    "color": colors["text_light"], "align": "center", "margin": "md"
                },
                {
                    "type": "text", "text": "عبير الدوسري 2025", "size": "xxs",
                    "color": colors["text_light"], "align": "center"
                }
            ]
        }

    @staticmethod
    def separator(margin="md", theme="light"):
        colors = UIBuilder.get_colors(theme)
        return {"type": "separator", "margin": margin, "color": colors["border"]}

    @staticmethod
    def button(label, text=None, style="secondary", color=None, action_type="message", uri=None, data=None, theme="light"):
        colors = UIBuilder.get_colors(theme)
        return {
            "type": "button", "style": style,
            "color": color or (colors["primary"] if style == "primary" else None),
            "height": "sm",
            "action": UIBuilder._make_action(label=label, text=text, action_type=action_type, data=data, uri=uri)
        }

    @staticmethod
    def button_row(buttons, theme="light"):
        btn_list = []
        for b in buttons:
            if isinstance(b, dict):
                b["theme"] = theme
                btn_list.append(UIBuilder.button(**b))
                continue
            if isinstance(b, tuple):
                label = b[0]
                text = b[1] if len(b) > 1 else b[0]
                style = b[2] if len(b) > 2 else "secondary"
                btn_list.append(UIBuilder.button(label, text, style, theme=theme))
                continue
            btn_list.append(UIBuilder.button(b, b, theme=theme))
        return {"type": "box", "layout": "horizontal", "spacing": "sm", "contents": btn_list}

    @staticmethod
    def card(contents, theme="light"):
        colors = UIBuilder.get_colors(theme)
        return {
            "type": "bubble",
            "body": {
                "type": "box", "layout": "vertical", "paddingAll": "20px",
                "backgroundColor": colors["card_bg"], "spacing": "md", "contents": contents
            }
        }

    @staticmethod
    def info_box(title, value, color=None, theme="light"):
        colors = UIBuilder.get_colors(theme)
        return {
            "type": "box", "layout": "baseline", "spacing": "sm",
            "contents": [
                {"type": "text", "text": title, "size": "sm", "color": colors["text_light"], "flex": 0},
                {
                    "type": "text", "text": str(value), "size": "md",
                    "color": color or colors["text_dark"], "weight": "bold", "align": "end", "flex": 1
                }
            ]
        }

    @staticmethod
    def section(title, content, theme="light"):
        colors = UIBuilder.get_colors(theme)
        return {
            "type": "box", "layout": "vertical", "spacing": "xs", "margin": "md",
            "contents": [
                {"type": "text", "text": title, "color": colors["primary"], "weight": "bold", "size": "sm"},
                {"type": "text", "text": content, "size": "xs", "wrap": True, "color": colors["text_light"]}
            ]
        }

    @staticmethod
    def welcome_card(display_name, is_registered, theme="light"):
        colors = UIBuilder.get_colors(theme)
        contents = [UIBuilder.header("مرحبا بك", display_name, theme=theme)]
        if is_registered:
            contents.append({
                "type": "text", "text": "انت مسجل بالفعل", "size": "md",
                "color": colors["success"], "align": "center", "margin": "lg", "weight": "bold"
            })
        else:
            contents.append({
                "type": "text", "text": "للبدء يرجى التسجيل اولا", "size": "sm",
                "color": colors["text_light"], "align": "center", "wrap": True, "margin": "lg"
            })
        contents.append(UIBuilder.separator(theme=theme))
        contents.append(UIBuilder.button_row([
            ("مساعدة", "مساعدة", "secondary"),
            ("العاب", "العاب", "primary"),
            ("ثيم", "تغيير الثيم", "secondary")
        ], theme=theme))
        contents.append(UIBuilder.footer(theme=theme))
        return UIBuilder.card(contents, theme=theme)

    @staticmethod
    def help_card(theme="light"):
        colors = UIBuilder.get_colors(theme)
        contents = [UIBuilder.header("المساعدة", theme=theme)]
        contents.append({
            "type": "text", "text": "الاوامر المتاحة", "size": "sm",
            "color": colors["text_dark"], "weight": "bold", "margin": "lg"
        })
        contents.append({
            "type": "text",
            "text": "تسجيل - انسحب - نقاطي - الصدارة - اللاعبين - العاب - سؤال - تحدي - اعتراف - منشن - توافق - ايقاف - تغيير الثيم",
            "size": "xs", "color": colors["text_light"], "wrap": True, "margin": "md"
        })
        contents.append(UIBuilder.separator(theme=theme))
        contents.append(UIBuilder.button_row([("بداية", "بداية", "primary")], theme=theme))
        contents.append(UIBuilder.footer(theme=theme))
        return UIBuilder.card(contents, theme=theme)

    @staticmethod
    def games_menu_card(is_registered, theme="light"):
        colors = UIBuilder.get_colors(theme)
        contents = [UIBuilder.header("قائمة الالعاب", theme=theme)]
        if not is_registered:
            contents.append({
                "type": "text", "text": "يجب التسجيل للعب", "size": "sm",
                "color": colors["warning"], "align": "center", "margin": "lg"
            })
            contents.append(UIBuilder.button_row([("تسجيل", "تسجيل", "primary")], theme=theme))
        else:
            contents.append({
                "type": "text", "text": "العاب بتسجيل", "size": "sm",
                "color": colors["text_dark"], "weight": "bold", "margin": "lg"
            })
            contents.append({
                "type": "text",
                "text": "اغنيه - لعبه - سلسله - اسرع - ضد - تكوين - سين - حروف",
                "size": "xs", "color": colors["text_light"], "wrap": True, "margin": "sm"
            })
            contents.append(UIBuilder.separator(theme=theme))
            contents.append({
                "type": "text", "text": "العاب بدون تسجيل", "size": "sm",
                "color": colors["text_dark"], "weight": "bold", "margin": "md"
            })
            contents.append({
                "type": "text", "text": "توافق - مافيا",
                "size": "xs", "color": colors["text_light"], "wrap": True, "margin": "sm"
            })
        contents.append(UIBuilder.separator(theme=theme))
        contents.append(UIBuilder.button_row([("بداية", "بداية", "primary")], theme=theme))
        contents.append(UIBuilder.footer(theme=theme))
        return UIBuilder.card(contents, theme=theme)

    @staticmethod
    def stats_card(display_name, stats, theme="light"):
        colors = UIBuilder.get_colors(theme)
        contents = [UIBuilder.header("احصائياتك", display_name, theme=theme)]
        contents.append(UIBuilder.info_box("النقاط", stats.get("total_points", 0), theme=theme))
        contents.append(UIBuilder.info_box("الالعاب", stats.get("games_played", 0), theme=theme))
        contents.append(UIBuilder.info_box("الفوز", stats.get("wins", 0), theme=theme))
        contents.append(UIBuilder.separator(theme=theme))
        contents.append(UIBuilder.button_row([("بداية", "بداية", "primary")], theme=theme))
        contents.append(UIBuilder.footer(theme=theme))
        return UIBuilder.card(contents, theme=theme)

    @staticmethod
    def leaderboard_card(leaders, theme="light"):
        colors = UIBuilder.get_colors(theme)
        contents = [UIBuilder.header("لوحة الصدارة", theme=theme)]
        for i, p in enumerate(leaders[:10], 1):
            medal = f"{i}. "
            contents.append({
                "type": "text",
                "text": f"{medal}{p.get('display_name', 'User')} - {p.get('total_points', 0)} نقطة",
                "size": "xs", "color": colors["text_dark"], "wrap": True, "margin": "sm"
            })
        contents.append(UIBuilder.separator(theme=theme))
        contents.append(UIBuilder.button_row([("بداية", "بداية", "primary")], theme=theme))
        contents.append(UIBuilder.footer(theme=theme))
        return UIBuilder.card(contents, theme=theme)

    @staticmethod
    def all_players_card(players, theme="light"):
        colors = UIBuilder.get_colors(theme)
        contents = [UIBuilder.header("جميع اللاعبين", theme=theme)]
        for p in players[:20]:
            status = "نشط" if p.get("active") else "غير نشط"
            contents.append({
                "type": "text",
                "text": f"{p.get('display_name', 'User')} - {p.get('total_points', 0)} نقطة - {status}",
                "size": "xs", "color": colors["text_dark"], "wrap": True, "margin": "sm"
            })
        contents.append(UIBuilder.separator(theme=theme))
        contents.append(UIBuilder.button_row([("بداية", "بداية", "primary")], theme=theme))
        contents.append(UIBuilder.footer(theme=theme))
        return UIBuilder.card(contents, theme=theme)

    @staticmethod
    def registration_card(theme="light"):
        colors = UIBuilder.get_colors(theme)
        contents = [UIBuilder.header("التسجيل", theme=theme)]
        contents.append({
            "type": "text", "text": "اكتب اسمك للتسجيل",
            "size": "sm", "color": colors["text_dark"], "align": "center", "margin": "lg"
        })
        contents.append(UIBuilder.separator(theme=theme))
        contents.append(UIBuilder.button_row([("الغاء", "الغاء", "secondary")], theme=theme))
        contents.append(UIBuilder.footer(theme=theme))
        return UIBuilder.card(contents, theme=theme)

    @staticmethod
    def registration_success_card(name, theme="light"):
        colors = UIBuilder.get_colors(theme)
        contents = [UIBuilder.header("تم التسجيل", theme=theme)]
        contents.append({
            "type": "text", "text": f"مرحبا {name}", "size": "md",
            "color": colors["success"], "align": "center", "weight": "bold", "margin": "lg"
        })
        contents.append(UIBuilder.separator(theme=theme))
        contents.append(UIBuilder.button_row([("العاب", "العاب", "primary")], theme=theme))
        contents.append(UIBuilder.footer(theme=theme))
        return UIBuilder.card(contents, theme=theme)

    @staticmethod
    def already_registered_card(name, theme="light"):
        colors = UIBuilder.get_colors(theme)
        contents = [UIBuilder.header("انت مسجل", theme=theme)]
        contents.append({
            "type": "text", "text": f"اسمك الحالي: {name}",
            "size": "sm", "color": colors["text_light"], "align": "center", "margin": "lg"
        })
        contents.append(UIBuilder.separator(theme=theme))
        contents.append(UIBuilder.button_row([("تغيير الاسم", "تغيير", "secondary")], theme=theme))
        contents.append(UIBuilder.footer(theme=theme))
        return UIBuilder.card(contents, theme=theme)

    @staticmethod
    def welcome_back_card(name, theme="light"):
        colors = UIBuilder.get_colors(theme)
        contents = [UIBuilder.header("مرحبا بعودتك", theme=theme)]
        contents.append({
            "type": "text", "text": f"اهلا {name}", "size": "md",
            "color": colors["success"], "align": "center", "weight": "bold", "margin": "lg"
        })
        contents.append(UIBuilder.footer(theme=theme))
        return UIBuilder.card(contents, theme=theme)

    @staticmethod
    def need_registration_card(theme="light"):
        colors = UIBuilder.get_colors(theme)
        contents = [UIBuilder.header("يجب التسجيل", theme=theme)]
        contents.append({
            "type": "text", "text": "يجب التسجيل اولا لاستخدام هذه الميزة",
            "size": "sm", "color": colors["warning"], "align": "center", "wrap": True, "margin": "lg"
        })
        contents.append(UIBuilder.separator(theme=theme))
        contents.append(UIBuilder.button_row([("تسجيل", "تسجيل", "primary")], theme=theme))
        contents.append(UIBuilder.footer(theme=theme))
        return UIBuilder.card(contents, theme=theme)

    @staticmethod
    def change_name_card(current_name, theme="light"):
        colors = UIBuilder.get_colors(theme)
        contents = [UIBuilder.header("تغيير الاسم", theme=theme)]
        contents.append({
            "type": "text", "text": f"اسمك الحالي: {current_name}",
            "size": "sm", "color": colors["text_light"], "align": "center", "margin": "lg"
        })
        contents.append({
            "type": "text", "text": "اكتب الاسم الجديد",
            "size": "sm", "color": colors["text_dark"], "align": "center", "margin": "md"
        })
        contents.append(UIBuilder.separator(theme=theme))
        contents.append(UIBuilder.button_row([("الغاء", "الغاء", "secondary")], theme=theme))
        contents.append(UIBuilder.footer(theme=theme))
        return UIBuilder.card(contents, theme=theme)

    @staticmethod
    def name_changed_card(new_name, theme="light"):
        colors = UIBuilder.get_colors(theme)
        contents = [UIBuilder.header("تم التغيير", theme=theme)]
        contents.append({
            "type": "text", "text": f"اسمك الجديد: {new_name}",
            "size": "md", "color": colors["success"], "align": "center", "weight": "bold", "margin": "lg"
        })
        contents.append(UIBuilder.footer(theme=theme))
        return UIBuilder.card(contents, theme=theme)

    @staticmethod
    def theme_changed_card(new_theme, theme="light"):
        colors = UIBuilder.get_colors(theme)
        theme_name = "فاتح" if new_theme == "light" else "داكن"
        contents = [UIBuilder.header("تم تغيير الثيم", theme=theme)]
        contents.append({
            "type": "text", "text": f"الثيم الحالي: {theme_name}",
            "size": "md", "color": colors["success"], "align": "center", "weight": "bold", "margin": "lg"
        })
        contents.append(UIBuilder.separator(theme=theme))
        contents.append(UIBuilder.button_row([("بداية", "بداية", "primary")], theme=theme))
        contents.append(UIBuilder.footer(theme=theme))
        return UIBuilder.card(contents, theme=theme)
