"""
games/game_helpers.py

مجموعّة دوال مساعدة لبناء رسائل LINE (Flex) والمنطق المشترك للألعاب.

التحسينات:
- Type hints + docstrings
- واجهات مرنة لإنشاء أجزاء الواجهة (header, separator, buttons, winner card...)
- normalize_text محسّن ليتعامل مع العربية بشكل موثوق
- حماية من الأخطاء و fallbacks
- قابلية تمرير theme (colors dict) افتراضيًا من constants.COLORS
"""

from __future__ import annotations
import re
from typing import List, Dict, Any, Optional, Iterable, Tuple

from constants import COLORS as DEFAULT_COLORS

# -----------------------
# Text normalization
# -----------------------
_DIACRITICS_RE = re.compile(r'[\u064B-\u065F\u0610-\u061A\u06D6-\u06ED]')
_WS_RE = re.compile(r'\s+')

def normalize_text(text: Optional[str]) -> str:
    """
    Normalize Arabic text for reliable comparison.
    - remove diacritics
    - unify alef/hamza/taa etc.
    - remove punctuation and spaces
    - lowercase

    Returns empty string for falsy inputs.
    """
    if not text:
        return ""
    s = str(text).strip().lower()

    # Normalize Alef variations and other letters
    trans = str.maketrans({
        'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
        'ؤ': 'و', 'ئ': 'ي', 'ء': '',
        'ة': 'ه', 'ى': 'ي',
    })
    s = s.translate(trans)

    # remove diacritics and other special marks
    s = _DIACRITICS_RE.sub('', s)

    # remove common punctuation
    s = re.sub(r'[.,!?؛،\-ـ:()«»"\']', '', s)

    # collapse whitespace
    s = _WS_RE.sub('', s)

    return s

# -----------------------
# Small helpers
# -----------------------
def create_hint_text(word: str) -> str:
    """Return a short hint: first character + length (safe on empty word)."""
    if not word:
        return "لا يوجد تلميح"
    first = word[0]
    length = len(word)
    return f"يبدأ بحرف: {first}\nعدد الحروف: {length}"

# -----------------------
# Flex element builders
# -----------------------
ColorsType = Dict[str, str]

def _get_color(colors: Optional[ColorsType], key: str) -> str:
    """Safe getter for color keys (fallback to DEFAULT_COLORS)."""
    if colors and key in colors:
        return colors[key]
    return DEFAULT_COLORS.get(key, "#000000")

def create_game_header(title: str, subtitle: Optional[str] = None, colors: Optional[ColorsType] = None) -> Dict[str, Any]:
    """
    Create a standard header box for a Flex bubble.
    """
    contents: List[Dict[str, Any]] = [{
        "type": "text",
        "text": title,
        "weight": "bold",
        "size": "xl",
        "color": _get_color(colors, "white"),
        "align": "center"
    }]
    if subtitle:
        contents.append({
            "type": "text",
            "text": subtitle,
            "size": "sm",
            "color": _get_color(colors, "white"),
            "align": "center",
            "margin": "xs"
        })

    return {
        "type": "box",
        "layout": "vertical",
        "cornerRadius": "12px",
        "backgroundColor": _get_color(colors, "primary"),
        "paddingAll": "18px",
        "contents": contents
    }

def create_progress_box(current: int, total: int, colors: Optional[ColorsType] = None) -> Dict[str, Any]:
    """
    Small baseline box showing progress like "3/5".
    Ensures numbers are valid and returns a compact structure.
    """
    try:
        cur = int(current)
        tot = int(total) if int(total) > 0 else 1
    except Exception:
        cur, tot = 0, 1

    return {
        "type": "box",
        "layout": "baseline",
        "contents": [
            {"type": "text", "text": "السؤال", "size": "xs", "color": _get_color(colors, "text_light"), "flex": 0},
            {"type": "text", "text": f"{cur}/{tot}", "size": "xs", "color": _get_color(colors, "primary"), "weight": "bold", "align": "end"}
        ],
        "margin": "lg"
    }

def create_separator(colors: Optional[ColorsType] = None) -> Dict[str, Any]:
    """Return a separator element (simple wrapper)."""
    return {"type": "separator", "margin": "md", "color": _get_color(colors, "border")}

def create_button(label: str, text: str, style: str = "secondary", colors: Optional[ColorsType] = None, flex: int = 1) -> Dict[str, Any]:
    """
    Create a single button action that sends a message (type=message).
    style: 'primary'|'secondary' — color fallback handled.
    """
    btn = {
        "type": "button",
        "action": {"type": "message", "label": label, "text": text},
        "style": style,
        "height": "sm",
        "flex": flex
    }
    # only set color if primary style requested
    if style == "primary":
        btn["color"] = _get_color(colors, "primary")
    return btn

def create_button_row(actions: Iterable[Tuple[str, str, Optional[str]]], colors: Optional[ColorsType] = None) -> Dict[str, Any]:
    """
    Build a horizontal row of buttons.
    actions: iterable of tuples (label, text, style) where style optional.
    """
    contents: List[Dict[str, Any]] = []
    for item in actions:
        if isinstance(item, tuple):
            label, text = item[0], item[1]
            style = item[2] if len(item) > 2 else "secondary"
        else:
            label, text, style = str(item), str(item), "secondary"
        contents.append(create_button(label, text, style=style, colors=colors))
    return {"type": "box", "layout": "horizontal", "spacing": "xs", "contents": contents, "margin": "lg"}

def create_action_buttons(colors: Optional[ColorsType] = None) -> List[Dict[str, Any]]:
    """
    Common action buttons used across games (hint/reveal/stop/register).
    Returns a list of Flex elements (rows).
    """
    row1 = create_button_row([("لمح", "لمح"), ("جاوب", "جاوب")], colors)
    row2 = create_button_row([("ايقاف", "ايقاف"), ("تسجيل", "تسجيل")], colors)
    # optionally add spacing row2 margin smaller
    row2["margin"] = "sm"
    return [row1, row2]

# -----------------------
# Winner card builder
# -----------------------
def create_winner_card(winner: Dict[str, Any], players_sorted: List[Tuple[str, Dict[str, Any]]],
                       replay_text: str, title: Optional[str] = "انتهت اللعبة",
                       colors: Optional[ColorsType] = None, top_n: int = 5) -> Dict[str, Any]:
    """
    Build a Flex bubble (dict) that shows the winner and top players.
    - winner: dict with keys 'name', 'score', optionally 'time'
    - players_sorted: list of tuples (user_id, player_data) sorted by rank
    - replay_text: message text to trigger a replay
    - top_n: how many players to show (default 5)
    """
    players_contents: List[Dict[str, Any]] = []
    for i, (uid, pdata) in enumerate(players_sorted[:top_n]):
        name = pdata.get("name", "—")
        score = pdata.get("score", 0)
        players_contents.append({
            "type": "box",
            "layout": "baseline",
            "contents": [
                {"type": "text", "text": f"{i+1}.", "size": "sm", "flex": 0},
                {"type": "text", "text": name, "size": "sm", "color": _get_color(colors, "text_dark"), "flex": 3, "margin": "sm"},
                {"type": "text", "text": f"{score} نقطة", "size": "sm", "color": _get_color(colors, "primary"), "weight": "bold", "align": "end", "flex": 2}
            ],
            "margin": "md" if i > 0 else "sm"
        })

    # Winner display (safe keys)
    winner_name = winner.get("name", "—")
    winner_score = winner.get("score", 0)

    bubble_body_contents: List[Dict[str, Any]] = [
        create_game_header(title, colors=colors),
        {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "الفائز", "size": "sm", "color": _get_color(colors, "text_light"), "align": "center"},
                {"type": "text", "text": winner_name, "size": "xxl", "color": _get_color(colors, "primary"), "weight": "bold", "align": "center", "margin": "xs"},
                {"type": "text", "text": f"{winner_score} نقطة", "size": "lg", "color": _get_color(colors, "success"), "align": "center", "margin": "xs"}
            ],
            "margin": "lg"
        },
        create_separator(colors=colors),
        {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "النتائج", "size": "md", "color": _get_color(colors, "text_dark"), "weight": "bold"},
                *players_contents
            ],
            "margin": "lg"
        },
        create_separator(colors=colors),
        {
            "type": "box",
            "layout": "vertical",
            "contents": [
                create_button("إعادة اللعب", replay_text, style="primary", colors=colors)
            ],
            "margin": "lg"
        }
    ]

    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": bubble_body_contents,
            "backgroundColor": _get_color(colors, "card_bg"),
            "paddingAll": "20px"
        }
    }

# -----------------------
# Small utilities / examples
# -----------------------
def safe_sample(lines: List[str], n: int) -> List[str]:
    """Return up to n unique samples from lines (non-destructive)."""
    if not lines:
        return []
    n = max(0, int(n))
    if n >= len(lines):
        return lines.copy()
    import random
    return random.sample(lines, n)

# -----------------------
# Module test / usage example (only when run directly)
# -----------------------
if __name__ == "__main__":
    # quick sanity checks (won't run during import)
    assert normalize_text("أهلاً") == "اهلا"
    assert normalize_text("لا إلهَ إلاّ الله") == "لاالهالاالله"
    print("game_helpers OK")
