from linebot.models import TextSendMessage, FlexSendMessage
import random
from constants import COLORS

class CompatibilityGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.waiting_for_names = True

    def start_game(self):
        return FlexSendMessage(
            alt_text="نسبة التوافق",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "نسبة التوافق", "weight": "bold", "size": "xl", "color": COLORS['white']}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "10px"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "اكتب اسمين مفصولين بمسافة", "size": "md", "color": COLORS['text_dark'], "wrap": True}, {"type": "text", "text": "مثال: أحمد فاطمة", "size": "sm", "color": COLORS['text_light'], "margin": "md"}], "margin": "lg", "spacing": "sm"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

    def check_answer(self, answer, user_id, display_name):
        if not self.waiting_for_names:
            return None

        parts = answer.strip().split()

        if len(parts) < 2:
            return {'response': TextSendMessage(text="يجب كتابة اسمين مفصولين بمسافة"), 'points': 0, 'correct': False, 'won': False, 'game_over': False}

        name1 = parts[0]
        name2 = ' '.join(parts[1:])
        compatibility = random.randint(50, 100)

        if compatibility >= 90:
            message = "توافق مثالي"
        elif compatibility >= 75:
            message = "توافق ممتاز"
        elif compatibility >= 60:
            message = "توافق جيد"
        else:
            message = "توافق متوسط"

        self.waiting_for_names = False

        result_card = FlexSendMessage(
            alt_text="نتيجة التوافق",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "نسبة التوافق", "weight": "bold", "size": "xl", "color": COLORS['white']}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "10px"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": f"{name1} و {name2}", "size": "lg", "color": COLORS['text_dark'], "align": "center", "wrap": True}, {"type": "text", "text": f"{compatibility}%", "size": "5xl", "color": COLORS['primary'], "weight": "bold", "align": "center", "margin": "lg"}, {"type": "text", "text": message, "size": "lg", "color": COLORS['text_dark'], "align": "center", "margin": "md"}], "margin": "lg", "spacing": "sm"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "button", "action": {"type": "message", "label": "إعادة", "text": "توافق"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "lg"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

        return {'response': result_card, 'points': 5, 'correct': True, 'won': True, 'game_over': True}
