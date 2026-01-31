from games.base_game import BaseGame
import random
from typing import Dict, Any, Optional, List
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer

class MafiaGame(BaseGame):
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=1)
        self.game_name = "مافيا"
        self.supports_hint = False
        self.supports_reveal = False
        self.min_players = 4
        self.max_players = 20
        self.players = {}
        self.roles = {}
        self.alive_players = set()
        self.dead_players = set()
        self.mafia_members = set()
        self.civilians = set()
        self.doctor = None
        self.detective = None
        self.game_phase = "waiting"
        self.current_round = 0
        self.night_votes = {}
        self.day_votes = {}
        self.protected_player = None
        self.investigated_player = None
        self.mafia_target = None
        self.doctor_save = None
        self.detective_check = None

    def get_theme_colors(self):
        """الحصول على الوان الثيم"""
        return {
            'primary': '#6B9BD1',
            'success': '#52C5B6',
            'warning': '#F39C6B',
            'error': '#E17B7B',
            'white': '#FFFFFF',
            'text': '#2C3E50',
            'text2': '#7F8C8D',
            'text3': '#95A5A6',
            'border': '#E8ECEF',
            'bg': '#F9FAFB',
            'card': '#FFFFFF',
            'info': '#3498DB',
            'info_bg': '#EBF5FB'
        }

    def _create_flex_with_buttons(self, alt_text, bubble):
        """انشاء Flex Message"""
        return FlexMessage(alt_text=alt_text, contents=FlexContainer.from_dict(bubble))

    def _create_text_message(self, text):
        """انشاء رسالة نصية"""
        return TextMessage(text=text)

    def start_game(self):
        self.game_active = True
        self.game_phase = "joining"
        self.current_round = 0
        return self.get_joining_screen()

    def get_joining_screen(self):
        c = self.get_theme_colors()
        joined_count = len(self.players)
        contents = [
            {"type": "text", "text": "لعبة المافيا", "size": "xxl", "weight": "bold", "color": c["primary"], "align": "center"},
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "box", "layout": "vertical", "contents": [
                {"type": "text", "text": "شرح اللعبة", "size": "md", "weight": "bold", "color": c["text"], "align": "center"},
                {"type": "text", "text": "لعبة جماعية تنقسم فيها الادوار بين مافيا ومدنيين", "size": "xs", "color": c["text2"], "wrap": True, "margin": "sm"},
                {"type": "separator", "margin": "md", "color": c["border"]},
                {"type": "text", "text": "الادوار", "size": "sm", "weight": "bold", "color": c["text"], "margin": "md"},
                {"type": "box", "layout": "vertical", "contents": [
                    {"type": "text", "text": "مافيا: يحاولون قتل المدنيين ليلا", "size": "xs", "color": c["error"], "wrap": True},
                    {"type": "text", "text": "مدنيين: يصوتون لطرد المشتبهين نهارا", "size": "xs", "color": c["info"], "wrap": True, "margin": "xs"},
                    {"type": "text", "text": "دكتور: ينقذ لاعب واحد كل ليلة", "size": "xs", "color": c["success"], "wrap": True, "margin": "xs"},
                    {"type": "text", "text": "محقق: يكشف دور لاعب كل ليلة", "size": "xs", "color": c["warning"], "wrap": True, "margin": "xs"}
                ], "margin": "sm"}
            ], "backgroundColor": c["card"], "cornerRadius": "12px", "paddingAll": "16px", "borderWidth": "1px", "borderColor": c["border"], "margin": "md"},
            {"type": "box", "layout": "vertical", "contents": [
                {"type": "box", "layout": "horizontal", "contents": [
                    {"type": "text", "text": "اللاعبون المنضمون", "size": "sm", "weight": "bold", "color": c["text"], "flex": 1},
                    {"type": "text", "text": f"{joined_count}/{self.max_players}", "size": "lg", "weight": "bold", "color": c["primary"], "flex": 0}
                ]},
                {"type": "text", "text": f"الحد الادنى: {self.min_players} لاعبين", "size": "xs", "color": c["text3"], "margin": "sm"}
            ], "backgroundColor": c["info_bg"], "cornerRadius": "12px", "paddingAll": "12px", "margin": "lg"},
            {"type": "text", "text": "اكتب انضم للانضمام\nاكتب ابدا لبدء اللعبة", "size": "sm", "color": c["text2"], "align": "center", "wrap": True, "margin": "lg"}
        ]
        return self._create_flex_with_buttons(self.game_name,
            {"type": "bubble", "size": "mega", "body": {"type": "box", "layout": "vertical", "contents": contents,
            "paddingAll": "24px", "backgroundColor": c["bg"]}})

    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        if not self.game_active:
            return None
        
        normalized = self.normalize_text(user_answer)
        
        if self.game_phase == "joining":
            if normalized in ["انضم", "join"]:
                if user_id not in self.players and len(self.players) < self.max_players:
                    self.players[user_id] = display_name
                    return {
                        "message": f"{display_name} انضم - العدد: {len(self.players)}",
                        "response": self._create_text_message(f"{display_name} انضم - العدد: {len(self.players)}"),
                        "points": 0
                    }
            elif normalized in ["ابدا", "start", "بدا"]:
                if len(self.players) >= self.min_players:
                    return {
                        "message": "اللعبة قيد التطوير حاليا",
                        "response": self._create_text_message("لعبة المافيا قيد التطوير حاليا\nجرب العاب اخرى"),
                        "points": 0,
                        "game_over": True
                    }
                else:
                    return {
                        "message": f"يحتاج {self.min_players - len(self.players)} لاعبين اضافيين",
                        "response": self._create_text_message(f"يحتاج {self.min_players - len(self.players)} لاعبين اضافيين"),
                        "points": 0
                    }
        
        return None
