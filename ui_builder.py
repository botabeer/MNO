from constants import COLORS


class UIBuilder:
    """
    UI Builder
    - يبني كروت LINE Flex بشكل منظم
    - يستخدم دوال مساعدة لتقليل التكرار
    """

    # ========== BASIC ELEMENT BUILDERS ========== #

    @staticmethod
    def header(title: str, subtitle: str | None = None):
        """Header موحد لجميع الكروت"""
        contents = [{
            "type": "text",
            "text": title,
            "weight": "bold",
            "size": "xl",
            "color": COLORS["white"],
            "align": "center"
        }]

        if subtitle:
            contents.append({
                "type": "text",
                "text": subtitle,
                "size": "sm",
                "color": COLORS["white"],
                "align": "center",
                "margin": "xs"
            })

        return {
            "type": "box",
            "layout": "vertical",
            "cornerRadius": "12px",
            "backgroundColor": COLORS["primary"],
            "paddingAll": "20px",
            "contents": contents
        }

    @staticmethod
    def footer():
        """Footer ثابت لجميع الكروت"""
        return {
            "type": "box",
            "layout": "vertical",
            "margin": "md",
            "contents": [
                {"type": "text", "text": "تم إنشاء هذا البوت بواسطة", "size": "xxs",
                 "color": COLORS["text_light"], "align": "center"},
                {"type": "text", "text": "عبير الدوسري 2025", "size": "xs",
                 "weight": "bold", "color": COLORS["text_light"], "align": "center", "margin": "xs"}
            ]
        }

    @staticmethod
    def separator():
        return {"type": "separator", "margin": "md", "color": COLORS["border"]}

    @staticmethod
    def button(label: str, text: str, style="secondary", flex=1):
        """زر موحد"""
        color = COLORS["primary"] if style == "primary" else None
        return {
            "type": "button",
            "action": {"type": "message", "label": label, "text": text},
            "style": style,
            "height": "sm",
            "flex": flex,
            "color": color
        }

    # ========== CARD WRAPPER ========== #

    @staticmethod
    def card(contents):
        """Container عام لجميع البابلز"""
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "20px",
                "backgroundColor": COLORS["card_bg"],
                "spacing": "md",
                "contents": contents
            }
        }

    # ========== CARDS ========== #

    @staticmethod
    def welcome_card(display_name: str, is_registered: bool):
        status = f"مسجل | {display_name}" if is_registered else "غير مسجل"
        status_color = COLORS["success"] if is_registered else COLORS["warning"]

        return UIBuilder.card([
            UIBuilder.header("بوت الحوت"),
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "مرحبا", "size": "lg", "weight": "bold",
                     "align": "center", "color": COLORS["text_dark"]},
                    {"type": "text", "text": status, "size": "md",
                     "color": status_color, "align": "center", "margin": "xs", "weight": "bold"},
                ],
                "margin": "lg"
            },
            UIBuilder.separator(),
            # حساب
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "الحساب", "size": "md", "weight": "bold",
                     "color": COLORS["text_dark"]},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "xs",
                        "contents": [
                            UIBuilder.button("تسجيل", "تسجيل", "primary"),
                            UIBuilder.button("تغيير", "تغيير"),
                            UIBuilder.button("انسحب", "انسحب"),
                        ]
                    }
                ]
            },
            UIBuilder.separator(),
            # الاحصائيات
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "الاحصائيات", "size": "md", "weight": "bold",
                     "color": COLORS["text_dark"]},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "xs",
                        "contents": [
                            UIBuilder.button("نقاطي", "نقاطي"),
                            UIBuilder.button("الصدارة", "الصدارة"),
                        ]
                    }
                ]
            },
            UIBuilder.separator(),
            # القوائم
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "القوائم", "size": "md", "weight": "bold",
                     "color": COLORS["text_dark"]},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "xs",
                        "contents": [
                            UIBuilder.button("العاب", "العاب", "primary"),
                            UIBuilder.button("مساعدة", "مساعدة"),
                        ]
                    }
                ]
            },
            UIBuilder.separator(),
            UIBuilder.footer()
        ])

    @staticmethod
    def games_menu_card(is_registered: bool):
        return UIBuilder.card([
            UIBuilder.header("بوت الحوت", "قائمة الالعاب"),
            {"type": "text", "text": "استمتع باللعب", "align": "center", "color": COLORS["success"]},

            # ألعاب تتطلب تسجيل
            {
                "type": "box",
                "layout": "vertical",
                "spacing": "xs",
                "contents": [
                    UIBuilder._btn_row(["اغنيه", "ضد", "تكوين"]),
                    UIBuilder._btn_row(["سلسله", "اسرع", "لعبه"]),
                    UIBuilder._btn_row(["توافق", "فئة", ("مافيا", "primary")]),
                ]
            },

            UIBuilder.separator(),
            {"type": "text", "text": "العاب ترفيهية بدون تسجيل", "align": "center", "color": COLORS["warning"]},
            UIBuilder._btn_row(["سؤال", "منشن"]),
            UIBuilder._btn_row(["اعتراف", "تحدي"]),

            UIBuilder.separator(),
            UIBuilder.button("العودة للبداية", "بداية", "primary"),
            UIBuilder.separator(),
            UIBuilder.footer()
        ])

    @staticmethod
    def _btn_row(buttons):
        """Helper: يبني صف أزرار"""
        row = []
        for b in buttons:
            if isinstance(b, tuple):
                label, style = b
                row.append(UIBuilder.button(label, label, style))
            else:
                row.append(UIBuilder.button(b, b))
        return {"type": "box", "layout": "horizontal", "spacing": "xs", "contents": row}

    @staticmethod
    def help_card():
        sections = [
            ("الاساسية", "بداية - تسجيل - نقاطي - الصدارة"),
            ("بدون تسجيل", "سؤال - تحدي - اعتراف - منشن - توافق"),
            ("الالعاب", "فئة - اغنية - ضد - تكوين - سلسلة - اسرع - لعبة - مافيا"),
            ("اثناء اللعب", "لمح - جاوب - ايقاف"),
            ("النقاط", "اجابة صحيحة = 1 نقطة | تلميح او جاوب = 0 نقطة"),
        ]

        contents = [UIBuilder.header("دليل الاوامر")]

        for title, text in sections:
            contents.append({
                "type": "box",
                "layout": "vertical",
                "margin": "md",
                "contents": [
                    {"type": "text", "text": title, "color": COLORS["primary"],
                     "weight": "bold", "size": "md"},
                    {"type": "text", "text": text, "color": COLORS["text_light"],
                     "size": "sm", "margin": "sm", "wrap": True},
                ]
            })
            contents.append(UIBuilder.separator())

        contents.append(UIBuilder.button("العودة للبداية", "بداية", "primary"))
        contents.append(UIBuilder.footer())

        return UIBuilder.card(contents)

    @staticmethod
    def stats_card(display_name, stats):
        stats = stats or {"total_points": 0, "games_played": 0, "wins": 0}
        win_rate = round((stats["wins"] / stats["games_played"] * 100) if stats["games_played"] > 0 else 0)

        return UIBuilder.card([
            UIBuilder.header("احصائياتك"),
            {
                "type": "text",
                "text": display_name,
                "align": "center",
                "size": "xl",
                "weight": "bold",
                "color": COLORS["text_dark"],
                "margin": "lg",
            },
            UIBuilder.separator(),

            UIBuilder._stats_row("النقاط", stats["total_points"], COLORS["primary"]),
            UIBuilder._stats_row("الالعاب", stats["games_played"], COLORS["text_dark"]),
            UIBuilder._stats_row("الفوز", stats["wins"], COLORS["success"]),
            UIBuilder._stats_row("نسبة الفوز", f"{win_rate}%", COLORS["primary"]),
        ])

    @staticmethod
    def _stats_row(label, value, color):
        return {
            "type": "box",
            "layout": "baseline",
            "margin": "md",
            "contents": [
                {"type": "text", "text": label, "size": "sm", "color": COLORS["text_light"], "flex": 0},
                {"type": "text", "text": str(value), "size": "lg", "color": color,
                 "weight": "bold", "align": "end", "flex": 1},
            ]
        }


# END FILE
