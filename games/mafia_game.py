from linebot.models import TextSendMessage, FlexSendMessage
import random
from datetime import datetime, timedelta
from constants import MAFIA_CONFIG, COLORS

class MafiaGame:

    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.players = {}   # user_id: {name, role, alive}
        self.phase = "registration"
        self.day = 0
        self.votes = {}
        self.group_id = None

    # ======================
    # START GAME
    # ======================
    def start_game(self):
        self.phase = "registration"
        return self.registration_flex()

    # ======================
    # REGISTRATION FLEX
    # ======================
    def registration_flex(self):
        return FlexSendMessage(
            alt_text="تسجيل المافيا",
            contents={
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "lg", "color": COLORS["white"], "align": "center"},
                        {"type": "text", "text": "لعبة المافيا", "size": "sm", "color": COLORS["white"], "align": "center"}
                    ],
                    "backgroundColor": COLORS["primary"]
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": f"اللاعبين: {len(self.players)}", "color": COLORS["text_dark"]}
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "انضم", "text": "انضم مافيا"},
                            "style": "primary",
                            "color": COLORS["primary"]
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "بدء", "text": "بدء مافيا"},
                            "style": "secondary"
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "شرح اللعبة", "text": "شرح مافيا"},
                            "style": "secondary"
                        }
                    ]
                }
            }
        )

    # ======================
    # ADD PLAYER
    # ======================
    def add_player(self, user_id, name):
        if self.phase != "registration":
            return "اللعبة بدأت"
        if user_id in self.players:
            return "أنت مسجل"
        self.players[user_id] = {"name": name, "role": None, "alive": True}
        return f"تم تسجيلك يا {name}"

    # ======================
    # ASSIGN ROLES (PRIVATE)
    # ======================
    def assign_roles(self):
        if len(self.players) < MAFIA_CONFIG["min_players"]:
            return "عدد اللاعبين غير كافٍ"

        roles = []
        roles += ["mafia"] * 1
        roles += ["detective"] * 1
        roles += ["doctor"] * 1
        remaining = len(self.players) - len(roles)
        roles += ["citizen"] * remaining
        random.shuffle(roles)

        for uid, role in zip(self.players.keys(), roles):
            self.players[uid]["role"] = role
            self.send_role_private(uid, role)

        self.phase = "night"
        self.day = 1
        return "تم توزيع الأدوار"

    # ======================
    # SEND ROLE FLEX (PRIVATE)
    # ======================
    def send_role_private(self, user_id, role):
        roles_text = {
            "mafia": "أنت مافيا",
            "detective": "أنت محقق",
            "doctor": "أنت دكتور",
            "citizen": "أنت مواطن"
        }

        flex = FlexSendMessage(
            alt_text="دورك",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "دورك في اللعبة", "weight": "bold"},
                        {"type": "text", "text": roles_text[role]}
                    ]
                }
            }
        )

        self.line_bot_api.push_message(user_id, flex)

    # ======================
    # GAME STATUS FLEX
    # ======================
    def status_flex(self):
        alive = [p["name"] for p in self.players.values() if p["alive"]]

        buttons = [
            {
                "type": "button",
                "action": {"type": "message", "label": name, "text": f"صوت {name}"}
            } for name in alive
        ]

        return FlexSendMessage(
            alt_text="حالة المافيا",
            contents={
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": f"اليوم {self.day}", "color": COLORS["white"], "align": "center"}
                    ],
                    "backgroundColor": COLORS["primary"]
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": f"المرحلة: {self.phase}"},
                        {"type": "text", "text": "اللاعبون الأحياء:"},
                        {"type": "text", "text": "\n".join(alive)}
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": buttons
                }
            }
        )

    # ======================
    # VOTING
    # ======================
    def vote(self, user_id, name):
        if self.phase != "voting":
            return "ليس وقت التصويت"

        for uid, p in self.players.items():
            if p["name"] == name and p["alive"]:
                self.votes[user_id] = uid
                return f"تم تصويتك لـ {name}"
        return "لا يوجد لاعب بهذا الاسم"

    # ======================
    # END VOTING
    # ======================
    def end_voting(self):
        results = {}
        for target in self.votes.values():
            results[target] = results.get(target, 0) + 1

        if not results:
            return "لم يتم التصويت"

        killed = max(results, key=results.get)
        self.players[killed]["alive"] = False

        self.phase = "night"
        self.day += 1
        self.votes = {}

        return self.check_winner()

    # ======================
    # CHECK WINNER
    # ======================
    def check_winner(self):
        mafia = sum(1 for p in self.players.values() if p["alive"] and p["role"] == "mafia")
        citizens = sum(1 for p in self.players.values() if p["alive"] and p["role"] != "mafia")

        if mafia == 0:
            self.phase = "ended"
            return self.winner_flex("المواطنون")

        if mafia >= citizens:
            self.phase = "ended"
            return self.winner_flex("المافيا")

        return self.status_flex()

    # ======================
    # WINNER FLEX
    # ======================
    def winner_flex(self, winner):
        return FlexSendMessage(
            alt_text="نهاية اللعبة",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "انتهت اللعبة", "weight": "bold"},
                        {"type": "text", "text": f"الفائز: {winner}"}
                    ]
                }
            }
        )

    # ======================
    # MAIN HANDLER
    # ======================
    def check_answer(self, text, user_id, display_name):

        if text == "انضم مافيا":
            return {"response": TextSendMessage(text=self.add_player(user_id, display_name))}

        if text == "بدء مافيا":
            result = self.assign_roles()
            return {"response": TextSendMessage(text=result)}

        if text == "شرح مافيا":
            return {"response": TextSendMessage(text="اللعبة تعتمد على ادوار سرية وتصويت جماعي")}

        if text.startswith("صوت "):
            name = text.replace("صوت ", "")
            return {"response": TextSendMessage(text=self.vote(user_id, name))}

        return None
