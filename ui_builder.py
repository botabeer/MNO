# ui_builder.py - Enhanced UI System
from constants import COLORS


class UIBuilder:
    """
    نظام UI Builder المحسّن
    - تصميم احترافي موحد
    - Flex Messages متطورة
    - سهل التوسع والصيانة
    """

    # ========== Core Building Blocks ========== #

    @staticmethod
    def header(title: str, subtitle: str = None, icon: str = None):
        """Header احترافي مع دعم أيقونات اختيارية"""
        contents = []
        
        if icon:
            contents.append({
                "type": "text",
                "text": icon,
                "size": "xxl",
                "align": "center",
                "margin": "none"
            })
        
        contents.append({
            "type": "text",
            "text": title,
            "weight": "bold",
            "size": "xl",
            "color": COLORS["white"],
            "align": "center",
            "margin": "xs" if icon else "none"
        })

        if subtitle:
            contents.append({
                "type": "text",
                "text": subtitle,
                "size": "sm",
                "color": COLORS["white"],
                "align": "center",
                "margin": "xs",
                "wrap": True
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
        """Footer موحد"""
        return {
            "type": "box",
            "layout": "vertical",
            "margin": "lg",
            "spacing": "xs",
            "contents": [
                {
                    "type": "separator",
                    "color": COLORS["border"]
                },
                {
                    "type": "text",
                    "text": "بوت الحوت",
                    "size": "xs",
                    "color": COLORS["text_light"],
                    "align": "center",
                    "margin": "md"
                },
                {
                    "type": "text",
                    "text": "عبير الدوسري 2025",
                    "size": "xxs",
                    "color": COLORS["text_light"],
                    "align": "center"
                }
            ]
        }

    @staticmethod
    def separator(margin="md"):
        """خط فاصل"""
        return {
            "type": "separator",
            "margin": margin,
            "color": COLORS["border"]
        }

    @staticmethod
    def button(label: str, text: str, style="secondary", color=None):
        """زر موحد وأنيق"""
        btn = {
            "type": "button",
            "action": {
                "type": "message",
                "label": label,
                "text": text
            },
            "style": style,
            "height": "sm"
        }
        
        if color:
            btn["color"] = color
        elif style == "primary":
            btn["color"] = COLORS["primary"]
            
        return btn

    @staticmethod
    def button_row(buttons):
        """صف أزرار أفقي"""
        btn_list = []
        for b in buttons:
            if isinstance(b, dict):
                btn_list.append(UIBuilder.button(**b))
            elif isinstance(b, tuple):
                label, style = b if len(b) == 2 else (b[0], "secondary")
                btn_list.append(UIBuilder.button(label, label, style))
            else:
                btn_list.append(UIBuilder.button(b, b))
        
        return {
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "contents": btn_list
        }

    @staticmethod
    def card(contents):
        """Container رئيسي للبطاقات"""
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

    @staticmethod
    def info_box(title: str, value: str, color=None):
        """صندوق معلومات"""
        return {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
                {
                    "type": "text",
                    "text": title,
                    "size": "sm",
                    "color": COLORS["text_light"],
                    "flex": 0
                },
                {
                    "type": "text",
                    "text": str(value),
                    "size": "md",
                    "color": color or COLORS["text_dark"],
                    "weight": "bold",
                    "align": "end",
                    "flex": 1
                }
            ]
        }

    @staticmethod
    def section(title: str, content: str):
        """قسم نصي"""
        return {
            "type": "box",
            "layout": "vertical",
            "spacing": "xs",
            "margin": "md",
            "contents": [
                {
                    "type": "text",
                    "text": title,
                    "color": COLORS["primary"],
                    "weight": "bold",
                    "size": "sm"
                },
                {
                    "type": "text",
                    "text": content,
                    "color": COLORS["text_light"],
                    "size": "xs",
                    "wrap": True,
                    "margin": "xs"
                }
            ]
        }

    # ========== Main Cards ========== #

    @staticmethod
    def welcome_card(display_name: str, is_registered: bool):
        """شاشة البداية الرئيسية"""
        status = f"مسجل | {display_name}" if is_registered else "غير مسجل"
        status_color = COLORS["success"] if is_registered else COLORS["warning"]

        return UIBuilder.card([
            UIBuilder.header("بوت الحوت", "مرحبا بك"),
            {
                "type": "box",
                "layout": "vertical",
                "spacing": "xs",
                "contents": [
                    {
                        "type": "text",
                        "text": "الحالة",
                        "size": "xs",
                        "color": COLORS["text_light"],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": status,
                        "size": "lg",
                        "color": status_color,
                        "align": "center",
                        "weight": "bold"
                    }
                ],
                "margin": "lg"
            },
            UIBuilder.separator(),
            
            # Account section
            {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "text",
                        "text": "الحساب",
                        "size": "md",
                        "weight": "bold",
                        "color": COLORS["text_dark"]
                    },
                    UIBuilder.button_row([
                        ("تسجيل", "primary"),
                        "تغيير",
                        "انسحب"
                    ])
                ]
            },
            
            UIBuilder.separator(),
            
            # Stats section
            {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "text",
                        "text": "الاحصائيات",
                        "size": "md",
                        "weight": "bold",
                        "color": COLORS["text_dark"]
                    },
                    UIBuilder.button_row([
                        "نقاطي",
                        "الصدارة",
                        "اللاعبين"
                    ])
                ]
            },
            
            UIBuilder.separator(),
            
            # Main actions
            {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "text",
                        "text": "القوائم",
                        "size": "md",
                        "weight": "bold",
                        "color": COLORS["text_dark"]
                    },
                    UIBuilder.button_row([
                        ("العاب", "primary"),
                        "مساعدة"
                    ])
                ]
            },
            
            UIBuilder.footer()
        ])

    @staticmethod
    def games_menu_card(is_registered: bool):
        """قائمة الألعاب المحسّنة"""
        return UIBuilder.card([
            UIBuilder.header("قائمة الألعاب", "اختر لعبتك المفضلة"),
            
            {
                "type": "text",
                "text": "الالعاب الرئيسية",
                "align": "center",
                "color": COLORS["primary"],
                "weight": "bold",
                "size": "sm",
                "margin": "lg"
            },
            
            UIBuilder.button_row([("اغنيه", "primary"), "ضد", "تكوين"]),
            UIBuilder.button_row(["سلسله", "اسرع", "لعبه"]),
            UIBuilder.button_row(["فئه", ("مافيا", "primary")]),
            
            UIBuilder.separator(),
            
            {
                "type": "text",
                "text": "العاب ترفيهية بدون تسجيل",
                "align": "center",
                "color": COLORS["warning"],
                "size": "sm"
            },
            
            UIBuilder.button_row(["سؤال", "تحدي"]),
            UIBuilder.button_row(["اعتراف", "منشن"]),
            UIBuilder.button_row([("توافق", "primary")]),
            
            UIBuilder.separator(),
            UIBuilder.button_row([("بداية", "primary")]),
            UIBuilder.footer()
        ])

    @staticmethod
    def help_card():
        """دليل الأوامر"""
        sections = [
            ("الاساسية", "بداية - تسجيل - نقاطي - الصدارة - اللاعبين"),
            ("بدون تسجيل", "سؤال - تحدي - اعتراف - منشن - توافق"),
            ("الالعاب", "اغنيه - ضد - تكوين - سلسله - اسرع - لعبه - فئه - مافيا"),
            ("اثناء اللعب", "لمح (اول حرف وعدد الحروف) - جاوب (الاجابة الصحيحة) - ايقاف"),
            ("النقاط", "اجابة صحيحة = 1 نقطة | تلميح او جاوب = 0 نقطة")
        ]

        contents = [UIBuilder.header("دليل الاوامر")]

        for title, text in sections:
            contents.append(UIBuilder.section(title, text))
            contents.append(UIBuilder.separator())

        contents.append(UIBuilder.button_row([("بداية", "primary")]))
        contents.append(UIBuilder.footer())

        return UIBuilder.card(contents)

    @staticmethod
    def stats_card(display_name: str, stats: dict):
        """بطاقة الإحصائيات"""
        stats = stats or {"total_points": 0, "games_played": 0, "wins": 0}
        win_rate = round(
            (stats["wins"] / stats["games_played"] * 100) 
            if stats["games_played"] > 0 else 0
        )

        return UIBuilder.card([
            UIBuilder.header("احصائياتك"),
            {
                "type": "text",
                "text": display_name,
                "align": "center",
                "size": "xl",
                "weight": "bold",
                "color": COLORS["text_dark"],
                "margin": "lg"
            },
            UIBuilder.separator(),
            UIBuilder.info_box("النقاط", stats["total_points"], COLORS["primary"]),
            UIBuilder.info_box("الالعاب", stats["games_played"], COLORS["text_dark"]),
            UIBuilder.info_box("الفوز", stats["wins"], COLORS["success"]),
            UIBuilder.info_box("نسبة الفوز", f"{win_rate}%", COLORS["primary"]),
            UIBuilder.separator(),
            UIBuilder.button_row([("بداية", "primary")]),
            UIBuilder.footer()
        ])

    @staticmethod
    def leaderboard_card(leaders: list):
        """لوحة الصدارة"""
        contents = [UIBuilder.header("لوحة الصدارة", "أفضل اللاعبين")]

        if not leaders:
            contents.append({
                "type": "text",
                "text": "لا يوجد لاعبون حاليا",
                "align": "center",
                "color": COLORS["text_light"],
                "margin": "lg"
            })
        else:
            for i, leader in enumerate(leaders[:10], 1):
                medal = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else ""))
                
                contents.append({
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "margin": "sm",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"{i}",
                            "size": "sm",
                            "color": COLORS["text_light"],
                            "flex": 0,
                            "align": "center"
                        },
                        {
                            "type": "text",
                            "text": leader.get('display_name', 'مستخدم'),
                            "size": "sm",
                            "color": COLORS["text_dark"],
                            "flex": 2,
                            "weight": "bold" if i <= 3 else "regular"
                        },
                        {
                            "type": "text",
                            "text": f"{leader.get('total_points', 0)}",
                            "size": "sm",
                            "color": COLORS["primary"],
                            "flex": 1,
                            "align": "end",
                            "weight": "bold"
                        }
                    ]
                })

        contents.append(UIBuilder.separator())
        contents.append(UIBuilder.button_row([("بداية", "primary")]))
        contents.append(UIBuilder.footer())

        return UIBuilder.card(contents)

    @staticmethod
    def all_players_card(players: list):
        """جميع اللاعبين"""
        contents = [UIBuilder.header("جميع اللاعبين")]

        if not players:
            contents.append({
                "type": "text",
                "text": "لا يوجد لاعبون",
                "align": "center",
                "color": COLORS["text_light"],
                "margin": "lg"
            })
        else:
            for player in players[:20]:
                status = "نشط" if player.get('active') else "غير نشط"
                status_color = COLORS["success"] if player.get('active') else COLORS["text_light"]
                
                contents.append({
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "margin": "sm",
                    "contents": [
                        {
                            "type": "text",
                            "text": player.get('display_name', 'مستخدم'),
                            "size": "sm",
                            "color": COLORS["text_dark"],
                            "flex": 2
                        },
                        {
                            "type": "text",
                            "text": f"{player.get('total_points', 0)}",
                            "size": "xs",
                            "color": COLORS["primary"],
                            "flex": 1,
                            "align": "center"
                        },
                        {
                            "type": "text",
                            "text": status,
                            "size": "xxs",
                            "color": status_color,
                            "flex": 1,
                            "align": "end"
                        }
                    ]
                })

        contents.append(UIBuilder.separator())
        contents.append(UIBuilder.button_row([("بداية", "primary")]))
        contents.append(UIBuilder.footer())

        return UIBuilder.card(contents)

    # ========== Registration Cards ========== #

    @staticmethod
    def registration_card():
        """بطاقة التسجيل"""
        return UIBuilder.card([
            UIBuilder.header("التسجيل"),
            {
                "type": "text",
                "text": "اكتب اسمك للتسجيل",
                "align": "center",
                "color": COLORS["text_dark"],
                "size": "md",
                "margin": "lg",
                "wrap": True
            },
            {
                "type": "text",
                "text": "الاسم يجب ان يكون مناسب وبدون كلمات غير لائقة",
                "align": "center",
                "color": COLORS["text_light"],
                "size": "xs",
                "margin": "md",
                "wrap": True
            },
            UIBuilder.separator(),
            UIBuilder.button_row([("الغاء", "secondary")]),
            UIBuilder.footer()
        ])

    @staticmethod
    def registration_success_card(name: str):
        """نجاح التسجيل"""
        return UIBuilder.card([
            UIBuilder.header("تم التسجيل بنجاح"),
            {
                "type": "text",
                "text": f"مرحبا {name}",
                "align": "center",
                "size": "xl",
                "weight": "bold",
                "color": COLORS["success"],
                "margin": "lg"
            },
            {
                "type": "text",
                "text": "يمكنك الآن اللعب والحصول على النقاط",
                "align": "center",
                "color": COLORS["text_light"],
                "size": "sm",
                "margin": "md",
                "wrap": True
            },
            UIBuilder.separator(),
            UIBuilder.button_row([("العاب", "primary"), "بداية"]),
            UIBuilder.footer()
        ])

    @staticmethod
    def already_registered_card(name: str):
        """مسجل بالفعل"""
        return UIBuilder.card([
            UIBuilder.header("مسجل بالفعل"),
            {
                "type": "text",
                "text": f"انت مسجل باسم: {name}",
                "align": "center",
                "color": COLORS["text_dark"],
                "margin": "lg",
                "wrap": True
            },
            UIBuilder.separator(),
            UIBuilder.button_row([("تغيير الاسم", "secondary"), ("بداية", "primary")]),
            UIBuilder.footer()
        ])

    @staticmethod
    def welcome_back_card(name: str):
        """مرحبا بعودتك"""
        return UIBuilder.card([
            UIBuilder.header("مرحبا بعودتك"),
            {
                "type": "text",
                "text": f"اهلا {name}",
                "align": "center",
                "size": "xl",
                "weight": "bold",
                "color": COLORS["success"],
                "margin": "lg"
            },
            {
                "type": "text",
                "text": "تم تفعيل حسابك مرة اخرى",
                "align": "center",
                "color": COLORS["text_light"],
                "size": "sm",
                "margin": "md"
            },
            UIBuilder.separator(),
            UIBuilder.button_row([("العاب", "primary"), "بداية"]),
            UIBuilder.footer()
        ])

    @staticmethod
    def change_name_card(current_name: str):
        """تغيير الاسم"""
        return UIBuilder.card([
            UIBuilder.header("تغيير الاسم"),
            {
                "type": "text",
                "text": f"الاسم الحالي: {current_name}",
                "align": "center",
                "color": COLORS["text_dark"],
                "margin": "lg"
            },
            {
                "type": "text",
                "text": "اكتب الاسم الجديد",
                "align": "center",
                "color": COLORS["text_light"],
                "size": "sm",
                "margin": "md"
            },
            UIBuilder.separator(),
            UIBuilder.button_row([("الغاء", "secondary")]),
            UIBuilder.footer()
        ])

    @staticmethod
    def name_changed_card(new_name: str):
        """تم تغيير الاسم"""
        return UIBuilder.card([
            UIBuilder.header("تم تغيير الاسم"),
            {
                "type": "text",
                "text": f"الاسم الجديد: {new_name}",
                "align": "center",
                "size": "lg",
                "weight": "bold",
                "color": COLORS["success"],
                "margin": "lg"
            },
            UIBuilder.separator(),
            UIBuilder.button_row([("بداية", "primary")]),
            UIBuilder.footer()
        ])

    @staticmethod
    def need_registration_card():
        """يجب التسجيل"""
        return UIBuilder.card([
            UIBuilder.header("يجب التسجيل اولا"),
            {
                "type": "text",
                "text": "يجب ان تكون مسجلا لاستخدام هذه الميزة",
                "align": "center",
                "color": COLORS["warning"],
                "margin": "lg",
                "wrap": True
            },
            UIBuilder.separator(),
            UIBuilder.button_row([("تسجيل", "primary"), "بداية"]),
            UIBuilder.footer()
        ])
