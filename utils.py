"""
أدوات مساعدة موحدة للتطبيق
"""
import re
from constants import COLORS

def normalize_text(text):
    """تطبيع النص العربي بشكل موحد"""
    if not text:
        return ""
    
    text = text.strip().lower()
    
    # استبدال الحروف المتشابهة
    replacements = {
        'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
        'ؤ': 'و', 'ئ': 'ي', 'ء': '',
        'ة': 'ه', 'ى': 'ي'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # إزالة التشكيل
    text = re.sub(r'[\u064B-\u065F]', '', text)
    
    # إزالة المسافات الزائدة
    text = re.sub(r'\s+', '', text)
    
    return text


def is_valid_name(name):
    """التحقق من صحة الاسم"""
    if not name or len(name.strip()) == 0:
        return False
    name = name.strip()
    return 1 <= len(name) <= 50


class FlexBuilder:
    """بناء رسائل Flex بشكل موحد"""
    
    @staticmethod
    def create_header(title, subtitle=None):
        """إنشاء رأس موحد"""
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
            "paddingAll": "20px",
            "cornerRadius": "12px"
        }
    
    @staticmethod
    def create_progress(current, total):
        """إنشاء شريط التقدم"""
        return {
            "type": "box",
            "layout": "baseline",
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
                    "size": "xs",
                    "color": COLORS['primary'],
                    "weight": "bold",
                    "align": "end"
                }
            ],
            "margin": "lg"
        }
    
    @staticmethod
    def create_separator():
        """إنشاء فاصل"""
        return {
            "type": "separator",
            "margin": "md",
            "color": COLORS['border']
        }
    
    @staticmethod
    def create_game_buttons():
        """أزرار اللعبة الموحدة"""
        return {
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "لمح",
                        "text": "لمح"
                    },
                    "style": "secondary",
                    "height": "sm",
                    "flex": 1
                },
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "جاوب",
                        "text": "جاوب"
                    },
                    "style": "secondary",
                    "height": "sm",
                    "flex": 1
                }
            ],
            "margin": "lg"
        }
    
    @staticmethod
    def create_question_card(game_name, question_text, current, total):
        """بطاقة سؤال موحدة"""
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    FlexBuilder.create_header(game_name),
                    FlexBuilder.create_progress(current, total),
                    FlexBuilder.create_separator(),
                    {
                        "type": "text",
                        "text": question_text,
                        "size": "lg",
                        "color": COLORS['text_dark'],
                        "wrap": True,
                        "weight": "bold",
                        "align": "center",
                        "margin": "lg"
                    },
                    FlexBuilder.create_separator(),
                    FlexBuilder.create_game_buttons()
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def create_winner_card(game_name, winner, all_players, restart_command):
        """بطاقة الفائز الموحدة"""
        players_list = []
        for i, (uid, player) in enumerate(all_players[:5]):
            players_list.append({
                "type": "box",
                "layout": "baseline",
                "contents": [
                    {
                        "type": "text",
                        "text": f"{i+1}.",
                        "size": "sm",
                        "flex": 0
                    },
                    {
                        "type": "text",
                        "text": player['name'],
                        "size": "sm",
                        "color": COLORS['text_dark'],
                        "flex": 3,
                        "margin": "sm"
                    },
                    {
                        "type": "text",
                        "text": f"{player['score']} نقطة",
                        "size": "sm",
                        "color": COLORS['primary'],
                        "weight": "bold",
                        "align": "end",
                        "flex": 2
                    }
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
                    FlexBuilder.create_header("انتهت اللعبة"),
                    {
                        "type": "box",
                        "layout": "vertical",
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
                                "margin": "xs"
                            }
                        ],
                        "margin": "lg"
                    },
                    FlexBuilder.create_separator(),
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "النتائج",
                                "size": "md",
                                "color": COLORS['text_dark'],
                                "weight": "bold"
                            },
                            *players_list
                        ],
                        "margin": "lg"
                    },
                    FlexBuilder.create_separator(),
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "اعادة اللعب",
                            "text": restart_command
                        },
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm",
                        "margin": "lg"
                    }
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
