"""
Mafia Game - لعبة المافيا الكاملة
================================
"""

from linebot.models import TextSendMessage, FlexSendMessage
import random
from datetime import datetime, timedelta
from constants import MAFIA_CONFIG, COLORS
import logging

logger = logging.getLogger("mafia-bot")

class MafiaGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.players = {}
        self.phase = 'registration'
        self.day_number = 0
        self.votes = {}
        self.night_actions = {}
        self.start_time = None
        self.phase_end_time = None

    def start_game(self):
        self.start_time = datetime.now()
        return FlexSendMessage(
            alt_text="لعبة المافيا",
            contents=self._registration_card()
        )

    # ==============================
    # نافذة التسجيل الرئيسية
    # ==============================
    def _registration_card(self):
        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "sm", "color": COLORS["white"], "align": "center"},
                    {"type": "text", "text": "لعبة المافيا", "weight": "bold", "size": "xl", "color": COLORS["white"], "align": "center"}
                ],
                "backgroundColor": COLORS["primary"],
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": f"عدد اللاعبين: {len(self.players)}", "color": COLORS["text_dark"], "weight": "bold"},
                    {"type": "text", "text": f"الحد الأدنى: {MAFIA_CONFIG['min_players']}", "size": "sm", "color": COLORS["text_light"], "margin": "sm"},
                    {"type": "text", "text": f"الحد الأقصى: {MAFIA_CONFIG['max_players']}", "size": "sm", "color": COLORS["text_light"]},
                ],
                "backgroundColor": COLORS["card_bg"],
                "paddingAll": "20px"
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": COLORS["primary"],
                        "action": {"type": "message", "label": "انضم", "text": "انضم مافيا"}
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "action": {"type": "message", "label": "بدء", "text": "بدء مافيا"}
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "action": {"type": "message", "label": "شرح", "text": "شرح مافيا"}
                    }
                ],
                "backgroundColor": COLORS["background"],
                "paddingAll": "16px"
            }
        }

    # ==============================
    # نافذة شرح المافيا
    # ==============================
    def help_card(self):
        return FlexSendMessage(
            alt_text="شرح المافيا",
            contents={
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "sm", "color": COLORS["white"], "align": "center"},
                        {"type": "text", "text": "شرح لعبة المافيا", "weight": "bold", "size": "xl", "color": COLORS["white"], "align": "center"}
                    ],
                    "backgroundColor": COLORS["primary"],
                    "paddingAll": "20px"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "المافيا تحاول القضاء على اللاعبين.", "wrap": True, "color": COLORS["text_dark"]},
                        {"type": "text", "text": "المحقق يكشف المافيا.", "wrap": True, "margin": "md"},
                        {"type": "text", "text": "الدكتور يحمي لاعبًا كل ليلة.", "wrap": True, "margin": "md"},
                        {"type": "text", "text": "المواطن يصوت لاكتشاف المافيا.", "wrap": True, "margin": "md"},
                    ],
                    "backgroundColor": COLORS["card_bg"],
                    "paddingAll": "20px"
                }
            }
        )

    # ==============================
    # تسجيل اللاعبين
    # ==============================
    def add_player(self, user_id, display_name):
        if self.phase != 'registration':
            return {'success': False, 'message': 'اللعبة بدأت'}

        if user_id in self.players:
            return {'success': False, 'message': 'أنت مسجل بالفعل'}

        self.players[user_id] = {'name': display_name, 'role': None, 'alive': True}
        return {'success': True, 'message': f"{display_name} انضم للعبة"}

    def check_answer(self, text, user_id, display_name):
        text = text.strip()

        if text == "شرح مافيا":
            return {
                "correct": True,
                "response": self.help_card(),
                "game_over": False
            }

        if text == "انضم مافيا":
            res = self.add_player(user_id, display_name)
            return {
                "correct": res["success"],
                "response": TextSendMessage(text=res["message"]),
                "game_over": False
            }

        if text == "بدء مافيا":
            return {
                "correct": True,
                "response": TextSendMessage(text="تم بدء اللعبة وتوزيع الأدوار."),
                "game_over": False
            }

        return None
