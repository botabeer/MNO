# game_helpers.py
import re
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
from constants import COLORS

def normalize_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip().lower()
    # Basic Arabic normalization (remove tatweel, diacritics, hamza variations)
    s = re.sub(r'[\u064B-\u0652ـ]', '', s)  # tashkeel
    s = s.replace('أ','ا').replace('إ','ا').replace('آ','ا').replace('ى','ي')
    s = s.replace('ؤ','و').replace('ئ','ي')
    s = re.sub(r'[^0-9\u0621-\u064A a-zA-Z]', '', s)
    return s

def create_game_header(title: str):
    return {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {"type": "text", "text": title, "weight": "bold", "size": "lg", "color": COLORS['white'], "align": "center"}
        ],
        "backgroundColor": COLORS['primary'],
        "paddingAll": "12px",
        "cornerRadius": "8px"
    }

def create_progress_box(current: int, total: int):
    return {"type": "text", "text": f"{current}/{total}", "size": "sm", "color": COLORS['text_light'], "align": "center", "margin": "md"}

def create_separator():
    return {"type": "separator", "margin": "lg", "color": COLORS['border']}

def create_action_buttons():
    return [
        {"type": "box", "layout": "horizontal", "contents": [
            {"type": "button", "action": {"type": "message", "label": "لمح", "text": "لمح"}, "style": "secondary", "height": "sm"},
            {"type": "button", "action": {"type": "message", "label": "جاوب", "text": "جاوب"}, "style": "secondary", "height": "sm"}
        ], "spacing": "sm", "margin": "lg"}
    ]

def create_winner_card(winner: dict, sorted_players: list, game_name: str):
    # winner is dict with 'name' and 'score'
    contents = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {"type":"text","text":"انتهت اللعبة","weight":"bold","size":"xl","color":COLORS['white']},
                {"type":"text","text":"الفائز","size":"sm","color":COLORS['text_light']},
                {"type":"text","text":winner['name'],"size":"xxl","color":COLORS['primary'],"weight":"bold"},
                {"type":"text","text":f"{winner['score']} نقطة","size":"sm","color":COLORS['success']}
            ],
            "backgroundColor": COLORS['card_bg'],
            "paddingAll": "16px"
        }
    }
    # append players list
    players_list = []
    for i, p in enumerate(sorted_players[:10]):
        players_list.append({"type":"text","text":f"{i+1}. {p[1]['name']} - {p[1]['score']}","size":"sm","color":COLORS['text_dark']})
    contents['body']['layout'] = 'vertical'
    contents['body']['contents'].extend([{"type":"separator","margin":"lg","color":COLORS['border']}] + players_list)
    return contents

def create_hint_text(answer: str) -> str:
    # returns first letter and length
    if not answer:
        return "لا يوجد تلميح"
    a = answer.strip()
    return f"يبدا بحرف: {a[0]}\nعدد الحروف: {len(a)}"
