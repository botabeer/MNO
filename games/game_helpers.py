# games/game_helpers.py - Enhanced Game Helpers
import re
from constants import COLORS


def normalize_text(s: str) -> str:
    """
    تطبيع النص العربي للمقارنة
    - إزالة التشكيل
    - توحيد الحروف المتشابهة
    - إزالة المسافات الزائدة
    """
    if not isinstance(s, str):
        return ""
    
    s = s.strip().lower()
    
    # Remove tashkeel and tatweel
    s = re.sub(r'[\u064B-\u0652ـ]', '', s)
    
    # Normalize similar letters
    s = s.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    s = s.replace('ى', 'ي').replace('ؤ', 'و').replace('ئ', 'ي')
    s = s.replace('ة', 'ه')
    
    # Remove non-alphanumeric except Arabic and English
    s = re.sub(r'[^0-9\u0621-\u064A a-zA-Z]', '', s)
    
    return s


def create_game_header(title: str, subtitle: str = None):
    """Header موحد للألعاب"""
    contents = [{
        "type": "text",
        "text": title,
        "weight": "bold",
        "size": "xl",
        "color": COLORS['white'],
        "align": "center"
    }]
    
    if subtitle:
        contents.append({
            "type": "text",
            "text": subtitle,
            "size": "sm",
            "color": COLORS['white'],
            "align": "center",
            "margin": "xs"
        })
    
    return {
        "type": "box",
        "layout": "vertical",
        "contents": contents,
        "backgroundColor": COLORS['primary'],
        "paddingAll": "16px",
        "cornerRadius": "10px"
    }


def create_progress_box(current: int, total: int):
    """صندوق التقدم"""
    return {
        "type": "box",
        "layout": "baseline",
        "spacing": "sm",
        "contents": [
            {
                "type": "text",
                "text": "السؤال",
                "size": "xs",
                "color": COLORS['text_light'],
                "flex": 0
            },
            {
                "type": "text",
                "text": f"{current}/{total}",
                "size": "sm",
                "color": COLORS['primary'],
                "weight": "bold",
                "align": "end"
            }
        ],
        "margin": "md"
    }


def create_separator(margin="md"):
    """خط فاصل"""
    return {
        "type": "separator",
        "margin": margin,
        "color": COLORS['border']
    }


def create_action_buttons(show_hint=True, show_answer=True, show_stop=False):
    """أزرار الإجراءات"""
    buttons = []
    
    if show_hint:
        buttons.append({
            "type": "button",
            "action": {
                "type": "message",
                "label": "لمح",
                "text": "لمح"
            },
            "style": "secondary",
            "height": "sm"
        })
    
    if show_answer:
        buttons.append({
            "type": "button",
            "action": {
                "type": "message",
                "label": "جاوب",
                "text": "جاوب"
            },
            "style": "secondary",
            "height": "sm"
        })
    
    if show_stop:
        buttons.append({
            "type": "button",
            "action": {
                "type": "message",
                "label": "ايقاف",
                "text": "ايقاف"
            },
            "style": "secondary",
            "height": "sm",
            "color": COLORS['warning']
        })
    
    return [{
        "type": "box",
        "layout": "horizontal",
        "spacing": "sm",
        "contents": buttons,
        "margin": "lg"
    }]


def create_winner_card(winner: dict, all_players: list, game_name: str):
    """بطاقة الفائز"""
    contents = [
        create_game_header("انتهت اللعبة", f"لعبة {game_name}"),
        
        {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "margin": "lg",
            "contents": [
                {
                    "type": "text",
                    "text": "الفائز",
                    "size": "sm",
                    "color": COLORS['text_light'],
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": winner['name'],
                    "size": "xxl",
                    "color": COLORS['primary'],
                    "weight": "bold",
                    "align": "center",
                    "margin": "xs"
                },
                {
                    "type": "text",
                    "text": f"{winner['score']} نقطة",
                    "size": "lg",
                    "color": COLORS['success'],
                    "align": "center",
                    "weight": "bold",
                    "margin": "xs"
                }
            ]
        },
        
        create_separator()
    ]
    
    # Top players
    if len(all_players) > 1:
        contents.append({
            "type": "text",
            "text": "النتائج النهائية",
            "size": "sm",
            "color": COLORS['text_dark'],
            "weight": "bold",
            "margin": "md"
        })
        
        for i, (uid, player) in enumerate(all_players[:5], 1):
            medal = "" if i > 3 else ("🥇" if i == 1 else ("🥈" if i == 2 else "🥉"))
            
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "margin": "sm",
                "contents": [
                    {
                        "type": "text",
                        "text": f"{i}",
                        "size": "xs",
                        "color": COLORS['text_light'],
                        "flex": 0
                    },
                    {
                        "type": "text",
                        "text": player['name'],
                        "size": "sm",
                        "color": COLORS['text_dark'],
                        "flex": 2
                    },
                    {
                        "type": "text",
                        "text": f"{player['score']}",
                        "size": "sm",
                        "color": COLORS['primary'],
                        "weight": "bold",
                        "flex": 1,
                        "align": "end"
                    }
                ]
            })
    
    contents.append(create_separator())
    contents.append({
        "type": "box",
        "layout": "horizontal",
        "spacing": "sm",
        "margin": "md",
        "contents": [
            {
                "type": "button",
                "action": {
                    "type": "message",
                    "label": "لعب مرة اخرى",
                    "text": game_name
                },
                "style": "primary",
                "color": COLORS['primary'],
                "height": "sm"
            },
            {
                "type": "button",
                "action": {
                    "type": "message",
                    "label": "البداية",
                    "text": "بداية"
                },
                "style": "secondary",
                "height": "sm"
            }
        ]
    })
    
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": contents,
            "backgroundColor": COLORS['card_bg'],
            "paddingAll": "18px"
        }
    }


def create_hint_text(answer: str) -> str:
    """إنشاء نص التلميح"""
    if not answer:
        return "لا يوجد تلميح"
    
    answer = answer.strip()
    first_letter = answer[0]
    length = len(answer)
    
    return f"يبدأ بحرف: {first_letter}\nعدد الحروف: {length}"


def create_question_card(question_text: str, current: int, total: int, game_title: str):
    """بطاقة سؤال موحدة"""
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                create_game_header(game_title),
                create_progress_box(current, total),
                create_separator(),
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [{
                        "type": "text",
                        "text": question_text,
                        "size": "lg",
                        "weight": "bold",
                        "color": COLORS['text_dark'],
                        "align": "center",
                        "wrap": True
                    }],
                    "margin": "lg"
                },
                create_separator(),
                *create_action_buttons()
            ],
            "backgroundColor": COLORS['card_bg'],
            "paddingAll": "18px"
        }
    }
