# games/game_helpers.py - مصلح بدون استيرادات دائرية
import re
from constants import THEMES

def normalize_text(text):
    """تطبيع النص العربي"""
    if not text:
        return ""
    text = text.strip().lower()
    trans = str.maketrans({'أ':'ا','إ':'ا','آ':'ا','ؤ':'و','ئ':'ي','ء':'','ة':'ه','ى':'ي'})
    text = text.translate(trans)
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def create_game_header(title, subtitle=None, theme="light"):
    """انشاء رأس اللعبة"""
    colors = THEMES.get(theme, THEMES["light"])
    contents = [{
        "type": "text",
        "text": title,
        "size": "xl",
        "weight": "bold",
        "color": colors["white"],
        "align": "center"
    }]
    if subtitle:
        contents.append({
            "type": "text",
            "text": subtitle,
            "size": "sm",
            "color": colors["white"],
            "align": "center",
            "wrap": True,
            "margin": "xs"
        })
    return {
        "type": "box",
        "layout": "vertical",
        "contents": contents,
        "backgroundColor": colors["primary"],
        "paddingAll": "16px",
        "cornerRadius": "12px"
    }

def create_progress_box(current, total, theme="light"):
    """انشاء صندوق التقدم"""
    colors = THEMES.get(theme, THEMES["light"])
    return {
        "type": "box",
        "layout": "baseline",
        "contents": [
            {"type": "text", "text": f"{current}", "size": "sm", "color": colors["text_light"], "flex": 0},
            {"type": "text", "text": f"من {total}", "size": "sm", "color": colors["text_light"], "align": "end", "flex": 1}
        ],
        "margin": "md"
    }

def create_separator(margin="md", theme="light"):
    """انشاء فاصل"""
    colors = THEMES.get(theme, THEMES["light"])
    return {"type": "separator", "margin": margin, "color": colors["border"]}

def create_action_buttons(theme="light"):
    """انشاء ازرار الاجراءات"""
    colors = THEMES.get(theme, THEMES["light"])
    return [
        {
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "action": {"type": "message", "label": "لمح", "text": "لمح"},
                    "style": "secondary",
                    "height": "sm"
                },
                {
                    "type": "button",
                    "action": {"type": "message", "label": "جاوب", "text": "جاوب"},
                    "style": "secondary",
                    "height": "sm",
                    "color": colors["warning"]
                }
            ]
        }
    ]

def create_winner_card(winner, all_players, game_name, theme="light"):
    """انشاء بطاقة الفائز"""
    colors = THEMES.get(theme, THEMES["light"])
    contents = [
        {
            "type": "box",
            "layout": "vertical",
            "contents": [{
                "type": "text",
                "text": f"نتائج {game_name}",
                "weight": "bold",
                "size": "xl",
                "color": colors["white"],
                "align": "center"
            }],
            "backgroundColor": colors["primary"],
            "paddingAll": "12px",
            "cornerRadius": "8px"
        },
        {
            "type": "text",
            "text": f"الفائز: {winner['name']}",
            "size": "lg",
            "weight": "bold",
            "align": "center",
            "color": colors["success"],
            "margin": "lg"
        },
        {
            "type": "text",
            "text": f"النقاط: {winner['score']}",
            "size": "md",
            "align": "center",
            "color": colors["text_dark"],
            "margin": "sm"
        },
        {"type": "separator", "margin": "md", "color": colors["border"]}
    ]

    for i, (uid, p) in enumerate(all_players[:5], 1):
        contents.append({
            "type": "text",
            "text": f"{i}. {p['name']} - {p['score']} نقطة",
            "size": "xs",
            "color": colors["text_dark"],
            "margin": "sm"
        })

    contents.append({"type": "separator", "margin": "md", "color": colors["border"]})
    contents.append({
        "type": "box",
        "layout": "horizontal",
        "spacing": "sm",
        "contents": [
            {
                "type": "button",
                "action": {"type": "message", "label": "اعادة", "text": game_name},
                "style": "primary",
                "color": colors["primary"],
                "height": "sm"
            },
            {
                "type": "button",
                "action": {"type": "message", "label": "البداية", "text": "بداية"},
                "style": "secondary",
                "height": "sm"
            }
        ],
        "margin": "md"
    })

    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": contents,
            "backgroundColor": colors["card_bg"],
            "paddingAll": "16px"
        }
    }

def create_question_card(question_text, current, total, game_name, theme="light"):
    """انشاء بطاقة السؤال"""
    colors = THEMES.get(theme, THEMES["light"])
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                create_game_header(game_name, theme=theme),
                create_progress_box(current, total, theme=theme),
                create_separator(theme=theme),
                {
                    "type": "text",
                    "text": question_text,
                    "size": "md",
                    "color": colors["text_dark"],
                    "wrap": True,
                    "align": "center",
                    "margin": "lg"
                },
                create_separator(theme=theme),
                *create_action_buttons(theme=theme)
            ],
            "backgroundColor": colors["card_bg"],
            "paddingAll": "18px"
        }
    }

def create_hint_text(answer, theme="light"):
    """انشاء نص التلميح"""
    return f"يبدا بحرف: {answer[0]}\nعدد الحروف: {len(answer)}"
