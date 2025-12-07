import re
from constants import COLORS

def normalize_text(text):
    if not text:
        return ""
    text = text.strip().lower()
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    text = text.replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '')
    text = text.replace('ة', 'ه').replace('ى', 'ي')
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'\s+', '', text)
    return text

def create_hint_text(word):
    """إنشاء تلميح: أول حرف + عدد الحروف"""
    return f"يبدأ بحرف: {word[0]}\nعدد الحروف: {len(word)}"

def create_game_header(title):
    return {
        "type": "box",
        "layout": "vertical",
        "contents": [{"type": "text", "text": title, "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}],
        "backgroundColor": COLORS['primary'],
        "paddingAll": "20px",
        "cornerRadius": "12px"
    }

def create_progress_box(current, total):
    return {
        "type": "box",
        "layout": "baseline",
        "contents": [
            {"type": "text", "text": "السؤال", "size": "xs", "color": COLORS['text_light'], "flex": 0},
            {"type": "text", "text": f"{current}/{total}", "size": "xs", "color": COLORS['primary'], "weight": "bold", "align": "end"}
        ],
        "margin": "lg"
    }

def create_separator():
    return {"type": "separator", "margin": "md", "color": COLORS['border']}

def create_button_row(buttons):
    return {
        "type": "box",
        "layout": "horizontal",
        "contents": buttons,
        "spacing": "xs",
        "margin": "lg"
    }

def create_action_buttons():
    return [
        create_button_row([
            {"type": "button", "action": {"type": "message", "label": "لمح", "text": "لمح"}, "style": "secondary", "height": "sm", "flex": 1},
            {"type": "button", "action": {"type": "message", "label": "جاوب", "text": "جاوب"}, "style": "secondary", "height": "sm", "flex": 1}
        ]),
        {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {"type": "button", "action": {"type": "message", "label": "ايقاف", "text": "ايقاف"}, "style": "secondary", "height": "sm", "flex": 1},
                {"type": "button", "action": {"type": "message", "label": "تسجيل", "text": "تسجيل"}, "style": "secondary", "height": "sm", "flex": 1}
            ],
            "spacing": "xs",
            "margin": "sm"
        }
    ]

def create_winner_card(winner, players, replay_text):
    players_contents = []
    for i, p in enumerate(players[:5]):
        players_contents.append({
            "type": "box",
            "layout": "baseline",
            "contents": [
                {"type": "text", "text": f"{i+1}.", "size": "sm", "flex": 0},
                {"type": "text", "text": p[1]['name'], "size": "sm", "color": COLORS['text_dark'], "flex": 3, "margin": "sm"},
                {"type": "text", "text": f"{p[1]['score']} نقطة", "size": "sm", "color": COLORS['primary'], "weight": "bold", "align": "end", "flex": 2}
            ],
            "margin": "md" if i > 0 else "sm"
        })
    
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                create_game_header("انتهت اللعبة"),
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "الفائز", "size": "sm", "color": COLORS['text_light'], "align": "center"},
                        {"type": "text", "text": winner['name'], "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center", "margin": "xs"},
                        {"type": "text", "text": f"{winner['score']} نقطة", "size": "lg", "color": COLORS['success'], "align": "center", "margin": "xs"}
                    ],
                    "margin": "lg"
                },
                create_separator(),
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [{"type": "text", "text": "النتائج", "size": "md", "color": COLORS['text_dark'], "weight": "bold"}, *players_contents],
                    "margin": "lg"
                },
                create_separator(),
                {"type": "button", "action": {"type": "message", "label": "إعادة اللعب", "text": replay_text}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "lg"}
            ],
            "backgroundColor": COLORS['card_bg'],
            "paddingAll": "20px"
        }
    }
