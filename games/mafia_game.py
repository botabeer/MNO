"""
Mafia Game - لعبة المافيا (موحدة مع نظام Flex)
==============================================
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
        self.group_id = None

    # ==================================================
    # نافذة موحدة للعبة المافيا بنفس قالب اللعب العام
    # ==================================================
    def _base_game_card(self, title, subtitle, content_lines):
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": COLORS['background'],
                "paddingAll": "16px",
                "contents": [
                    {
                        "type": "text",
                        "text": title,
                        "size": "xl",
                        "weight": "bold",
                        "color": COLORS['white'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": subtitle,
                        "size": "xs",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "margin": "xs"
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": COLORS['border']
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "md",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "text",
                                "text": line,
                                "size": "sm",
                                "color": COLORS['text_dark'],
                                "wrap": True
                            } for line in content_lines
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "10px",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "height": "sm",
                        "color": COLORS['primary'],
                        "action": {"type": "message", "label": "تصويت", "text": "حالة مافيا"}
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "height": "sm",
                        "action": {"type": "message", "label": "انسحاب", "text": "انسحب مافيا"}
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "height": "sm",
                        "action": {"type": "message", "label": "حالة", "text": "حالة مافيا"}
                    }
                ]
            }
        }

    # ==================================================
    # بدء التسجيل
    # ==================================================
    def start_game(self):
        self.start_time = datetime.now()
        return FlexSendMessage(
            alt_text="لعبة المافيا",
            contents=self._base_game_card(
                "لعبة المافيا",
                "مرحلة التسجيل",
                [
                    f"عدد اللاعبين: {len(self.players)}",
                    f"الحد الأدنى: {MAFIA_CONFIG['min_players']}",
                    f"الحد الأقصى: {MAFIA_CONFIG['max_players']}",
                    "للإنضمام: انضم مافيا",
                    "للبدء: بدء مافيا"
                ]
            )
        )

    # ==================================================
    # إضافة لاعب
    # ==================================================
    def add_player(self, user_id, display_name):
        if self.phase != 'registration':
            return {'success': False, 'message': 'اللعبة بدأت بالفعل'}

        if len(self.players) >= MAFIA_CONFIG['max_players']:
            return {'success': False, 'message': 'اللعبة ممتلئة'}

        if user_id in self.players:
            return {'success': False, 'message': 'أنت مسجل بالفعل'}

        self.players[user_id] = {
            'name': display_name,
            'role': None,
            'alive': True
        }

        return {
            'success': True,
            'message': f"{display_name} انضم\nالعدد: {len(self.players)}/{MAFIA_CONFIG['max_players']}"
        }

    # ==================================================
    # توزيع الأدوار
    # ==================================================
    def start_roles_assignment(self):
        if len(self.players) < MAFIA_CONFIG['min_players']:
            return {'success': False, 'message': 'عدد غير كافٍ من اللاعبين'}

        player_count = len(self.players)
        roles_config = MAFIA_CONFIG['roles'][player_count]

        roles = []
        roles += ['mafia'] * roles_config['mafia']
        roles += ['detective'] * roles_config['detective']
        roles += ['doctor'] * roles_config['doctor']

        remaining = player_count - len(roles)
        roles += ['citizen'] * remaining

        random.shuffle(roles)
        for uid, role in zip(self.players.keys(), roles):
            self.players[uid]['role'] = role

        self.phase = 'night'
        self.day_number = 1
        return {'success': True}

    # ==================================================
    # كرت الدور الخاص
    # ==================================================
    def get_role_message(self, user_id):
        role = self.players[user_id]['role']

        role_text = {
            "mafia": "أنت المافيا\nاقتل شخصاً كل ليلة",
            "detective": "أنت المحقق\nتحقق من شخص كل ليلة",
            "doctor": "أنت الدكتور\nاحم شخصاً كل ليلة",
            "citizen": "أنت مواطن\nشارك بالتصويت"
        }

        return FlexSendMessage(
            alt_text="دورك في المافيا",
            contents=self._base_game_card(
                "دورك في اللعبة",
                role,
                [role_text.get(role, "مواطن")]
            )
        )

    # ==================================================
    # حالة اللعبة الموحدة
    # ==================================================
    def get_game_status(self):
        alive_count = sum(1 for p in self.players.values() if p['alive'])

        return FlexSendMessage(
            alt_text="حالة المافيا",
            contents=self._base_game_card(
                f"اليوم {self.day_number}",
                self.phase,
                [
                    f"الأحياء: {alive_count}/{len(self.players)}",
                    f"المرحلة: {self.phase}"
                ]
            )
        )

    # ==================================================
    # استقبال أوامر اللعب
    # ==================================================
    def check_answer(self, text, user_id, display_name):

        text = text.strip()

        if text == 'انضم مافيا' and self.phase == 'registration':
            r = self.add_player(user_id, display_name)
            return {
                'correct': r['success'],
                'response': TextSendMessage(text=r['message']),
                'game_over': False
            }

        if text == 'بدء مافيا' and self.phase == 'registration':
            r = self.start_roles_assignment()
            if r['success']:
                return {
                    'correct': True,
                    'response': TextSendMessage(text='تم بدء اللعبة وتوزيع الأدوار'),
                    'game_over': False,
                    'assign_roles': True
                }
            else:
                return {
                    'correct': False,
                    'response': TextSendMessage(text=r['message']),
                    'game_over': False
                }

        if text == 'حالة مافيا':
            return {
                'correct': False,
                'response': self.get_game_status(),
                'game_over': False
            }

        if text == 'انسحب مافيا':
            if user_id in self.players:
                del self.players[user_id]
                return {
                    'correct': False,
                    'response': TextSendMessage(text='تم انسحابك من اللعبة'),
                    'game_over': False
                }

        return None
