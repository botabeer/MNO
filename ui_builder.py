# ui_builder.py — UI System V2 (Improved & Clean)
from constants import COLORS


class UIBuilder:
    """
    UI Builder V2 — نسخة محسّنة، نظيفة، قابلة للتوسّع.
    """

    # =============================
    #   INTERNAL ACTION HANDLER
    # =============================

    @staticmethod
    def _make_action(label: str, text: str = None, action_type="message", data=None, uri=None):
        """
        يدعم أنواع الأكشن:
        - message (افتراضي)
        - postback
        - uri
        - data actions
        """
        if action_type == "message":
            return {
                "type": "message",
                "label": label,
                "text": text or label
            }

        if action_type == "uri":
            return {
                "type": "uri",
                "label": label,
                "uri": uri
            }

        return {
            "type": action_type,
            "label": label,
            "data": data or text or label
        }

    # =============================
    #   PARTS
    # =============================

    @staticmethod
    def header(title: str, subtitle: str = None, icon: str = None):
        contents = []

        if icon:
            contents.append({
                "type": "text",
                "text": icon,
                "size": "xxl",
                "align": "center",
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
                "wrap": True,
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
        return {
            "type": "box",
            "layout": "vertical",
            "margin": "lg",
            "contents": [
                {"type": "separator", "color": COLORS["border"]},
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
                    "align": "center",
                }
            ]
        }

    @staticmethod
    def separator(margin="md"):
        return {"type": "separator", "margin": margin, "color": COLORS["border"]}

    # =============================
    #   BUTTON SYSTEM
    # =============================

    @staticmethod
    def button(label: str, text: str = None, style="secondary", color=None, action_type="message", uri=None, data=None):
        return {
            "type": "button",
            "style": style,
            "color": color or (COLORS["primary"] if style == "primary" else None),
            "height": "sm",
            "action": UIBuilder._make_action(
                label=label,
                text=text,
                action_type=action_type,
                data=data,
                uri=uri
            )
        }

    @staticmethod
    def button_row(buttons):
        """
        يدعم 5 صيغ:
        - "نص فقط"
        - ("label", "primary")
        - ("label", "text", "primary")
        - {"label":..., "text":..., "style":...}
        - {"label":..., "action_type":"uri", "uri":"..."}
        """
        btn_list = []

        for b in buttons:
            # dict
            if isinstance(b, dict):
                btn_list.append(UIBuilder.button(**b))
                continue

            # tuple
            if isinstance(b, tuple):
                label = b[0]
                text = b[1] if len(b) > 1 else b[0]
                style = b[2] if len(b) > 2 else "secondary"
                btn_list.append(UIBuilder.button(label, text, style))
                continue

            # simple text
            btn_list.append(UIBuilder.button(b, b))

        return {
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "contents": btn_list
        }

    # =============================
    #   CONTENT BLOCKS
    # =============================

    @staticmethod
    def card(contents):
        """Bubble جاهز"""
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
                    "size": "xs",
                    "wrap": True,
                    "color": COLORS["text_light"],
                }
            ]
        }

    # =============================
    #   READY-MADE CARDS (Screens)
    # =============================

    @staticmethod
    def simple_screen(title, subtitle=None, icon=None, body_lines=None, buttons=None):
        """
        واجهة جاهزة للاستخدام — مرنة جدًا
        """
        contents = [UIBuilder.header(title, subtitle, icon)]

        if body_lines:
            for line in body_lines:
                contents.append({
                    "type": "text",
                    "text": "• " + line,
                    "wrap": True,
                    "size": "sm",
                    "color": COLORS["text_dark"],
                    "margin": "md"
                })

        if buttons:
            contents.append(UIBuilder.button_row(buttons))

        contents.append(UIBuilder.footer())

        return UIBuilder.card(contents)
