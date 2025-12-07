# games/game_helpers.py
import unicodedata
import re
from typing import Tuple, List, Dict
from constants import COLORS

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.strip().lower()
    # remove diacritics
    text = "".join(ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch))
    # unify ta marbuta and ha
    text = text.replace("ة", "ه")
    text = re.sub(r"[^0-9\u0600-\u06FFa-z\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

def create_game_header(title: str) -> dict:
    return {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {"type": "text", "text": title, "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}
        ],
        "backgroundColor": COLORS['primary'],
        "paddingAll": "16px",
        "cornerRadius": "10px"
    }

def create_progress_box(current: int, total: int) -> dict:
    return {
        "type": "box",
        "layout": "baseline",
        "contents": [
            {"type": "text", "text": "السؤال", "size": "xs", "color": COLORS['text_light']},
            {"type": "text", "text": f"{current}/{total}", "size": "xs", "color": COLORS['primary'], "weight": "bold", "align": "end"}
        ],
        "margin": "md"
    }

def create_separator() -> dict:
    return {"type": "separator", "margin": "md", "color": COLORS['border']}

def create_action_buttons() -> list:
    return [
        {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {"type": "button", "action": {"type": "message", "label": "لمح", "text": "لمح"}, "style": "secondary", "height": "sm", "flex": 1},
                {"type": "button", "action": {"type": "message", "label": "جاوب", "text": "جاوب"}, "style": "primary", "height": "sm", "flex": 1}
            ],
            "spacing": "sm",
            "margin": "lg"
        }
    ]

def create_winner_card(winner: dict, sorted_players: List[Tuple[str, dict]], game_tag: str) -> dict:
    # winner is {'name': name, 'score': n}
    players_contents = []
    for i, p in enumerate(sorted_players[:8]):
        players_contents.append({
            "type": "box", "layout": "baseline",
            "contents": [
                {"type": "text", "text": f"{i+1}.", "size": "sm", "flex": 0},
                {"type": "text", "text": p[1]['name'], "size": "sm", "color": COLORS['text_dark'], "flex": 3, "margin": "sm"},
                {"type": "text", "text": f"{p[1]['score']} نقطة", "size": "sm", "color": COLORS['primary'], "weight": "bold", "align": "end", "flex": 2}
            ],
            "margin": "md" if i > 0 else "sm"
        })

    body = {
        "type": "box",
        "layout": "vertical",
        "spacing": "md",
        "contents": [
            create_game_header("انتهت اللعبة"),
            {
                "type": "box", "layout": "vertical", "contents": [
                    {"type": "text", "text": "الفائز", "size": "sm", "color": COLORS['text_light'], "align": "center"},
                    {"type": "text", "text": winner['name'], "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center", "margin": "xs"},
                    {"type": "text", "text": f"{winner['score']} نقطة", "size": "lg", "color": COLORS['success'], "align": "center", "margin": "xs"}
                ], "margin": "lg"
            },
            {"type": "separator", "margin": "lg", "color": COLORS['border']},
            {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "النتائج", "size": "md", "color": COLORS['text_dark'], "weight": "bold"}, *players_contents], "margin": "lg"},
            {"type": "separator", "margin": "lg", "color": COLORS['border']},
            {"type": "button", "action": {"type": "message", "label": "إعادة", "text": game_tag}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "lg"}
        ],
        "backgroundColor": COLORS['card_bg'],
        "paddingAll": "20px"
    }
    return {"type": "bubble", "body": body}

def create_hint_text(answer: str) -> str:
    if not answer:
        return ""
    first = answer[0]
    length = len(answer)
    return f"يبدأ بحرف: {first}\nعدد الحروف: {length}"
