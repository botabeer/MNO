from linebot.models import TextSendMessage, FlexSendMessage
import random
from constants import MAFIA_CONFIG, COLORS

class MafiaGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.players = {}
        self.phase = "registration"
        self.day = 0
        self.votes = {}
        self.night_actions = {}
        self.group_id = None

    def start_game(self):
        self.phase = "registration"
        self.players = {}
        self.votes = {}
        self.night_actions = {}
        self.day = 0
        return self.registration_flex()

    def registration_flex(self):
        return FlexSendMessage(
            alt_text="لعبة المافيا التسجيل",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "لعبة المافيا", "weight": "bold", "size": "lg", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "10px"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "مهم اضف البوت كصديق لاستلام دورك السري", "size": "xs", "color": COLORS['warning'], "weight": "bold", "wrap": True, "align": "center"}], "backgroundColor": f"{COLORS['warning']}1A", "paddingAll": "10px", "cornerRadius": "8px", "margin": "lg"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "انضم للعبة", "size": "lg", "color": COLORS['text_dark'], "weight": "bold"}, {"type": "text", "text": f"اللاعبين المسجلين {len(self.players)}", "size": "md", "color": COLORS['text_light'], "margin": "md"}, {"type": "text", "text": f"الحد الادنى {MAFIA_CONFIG['min_players']} لاعبين", "size": "sm", "color": COLORS['text_light'], "margin": "xs"}], "margin": "lg"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "button", "action": {"type": "message", "label": "انضم", "text": "انضم مافيا"}, "style": "primary", "color": COLORS['primary'], "height": "sm"}, {"type": "button", "action": {"type": "message", "label": "بدء اللعبة", "text": "بدء مافيا"}, "style": "secondary", "height": "sm", "margin": "sm"}, {"type": "button", "action": {"type": "message", "label": "شرح اللعبة", "text": "شرح مافيا"}, "style": "secondary", "height": "sm", "margin": "sm"}], "margin": "lg"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

    def explanation_flex(self):
        return FlexSendMessage(
            alt_text="شرح لعبة المافيا",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "شرح لعبة المافيا", "weight": "bold", "size": "lg", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "10px"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "في القروب", "size": "lg", "color": COLORS['primary'], "weight": "bold"}, {"type": "text", "text": "1 اضغط انضم", "size": "sm", "color": COLORS['text_light'], "margin": "md"}, {"type": "text", "text": "2 انتظر حتى يضغط 4 لاعبين على الاقل", "size": "sm", "color": COLORS['text_light'], "margin": "xs"}, {"type": "text", "text": "3 اضغط بدء اللعبة", "size": "sm", "color": COLORS['text_light'], "margin": "xs"}, {"type": "text", "text": "4 وقت النهار اضغط تصويت", "size": "sm", "color": COLORS['text_light'], "margin": "xs"}, {"type": "text", "text": "5 اضغط على اسم من تشك انه مافيا", "size": "sm", "color": COLORS['text_light'], "margin": "xs"}, {"type": "text", "text": "6 اضغط انهاء التصويت", "size": "sm", "color": COLORS['text_light'], "margin": "xs"}], "margin": "lg"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "في الخاص", "size": "lg", "color": COLORS['success'], "weight": "bold"}, {"type": "text", "text": "1 راح يوصلك دورك السري", "size": "sm", "color": COLORS['text_light'], "margin": "md"}, {"type": "text", "text": "2 اذا كنت مافيا راح تشوف نافذة فيها اسماء اضغط على اسم لتقتله", "size": "sm", "color": COLORS['text_light'], "margin": "xs", "wrap": True}, {"type": "text", "text": "3 اذا كنت محقق راح تشوف نافذة اضغط على اسم لتفحصه", "size": "sm", "color": COLORS['text_light'], "margin": "xs", "wrap": True}, {"type": "text", "text": "4 اذا كنت دكتور راح تشوف نافذة اضغط على اسم لتحميه", "size": "sm", "color": COLORS['text_light'], "margin": "xs", "wrap": True}, {"type": "text", "text": "5 اذا كنت مواطن لا يوجد لك دور في الليل", "size": "sm", "color": COLORS['text_light'], "margin": "xs", "wrap": True}], "margin": "lg"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "الفوز", "size": "lg", "color": COLORS['text_dark'], "weight": "bold"}, {"type": "text", "text": "المواطنون اقتلوا المافيا", "size": "sm", "color": COLORS['text_light'], "margin": "md"}, {"type": "text", "text": "المافيا كونوا اكثر من المواطنين", "size": "sm", "color": COLORS['text_light'], "margin": "xs"}], "margin": "lg"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "button", "action": {"type": "message", "label": "ابدا اللعب", "text": "مافيا"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "lg"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

    def add_player(self, user_id, name):
        if self.phase != "registration":
            return {"response": TextSendMessage(text="اللعبة بدأت بالفعل")}
        if user_id in self.players:
            return {"response": TextSendMessage(text="انت مسجل بالفعل")}
        self.players[user_id] = {"name": name, "role": None, "alive": True}
        return {"response": self.registration_flex()}

    def assign_roles(self):
        if len(self.players) < MAFIA_CONFIG["min_players"]:
            return {"response": TextSendMessage(text=f"عدد اللاعبين غير كاف الحد الادنى {MAFIA_CONFIG['min_players']} لاعبين")}
        roles = ["mafia", "detective", "doctor"]
        remaining = len(self.players) - len(roles)
        roles += ["citizen"] * remaining
        random.shuffle(roles)
        for uid, role in zip(self.players.keys(), roles):
            self.players[uid]["role"] = role
            self.send_role_private(uid, role)
        self.phase = "night"
        self.day = 1
        return {"response": [TextSendMessage(text="تم توزيع الادوار في الخاص لكل لاعب"), self.night_flex()]}

    def send_role_private(self, user_id, role):
        role_info = {
            "mafia": {"title": "انت المافيا", "desc": "دورك قتل شخص كل ليلة", "instruction": "راح توصلك نافذة فيها اسماء اللاعبين اضغط على الاسم اللي تبي تقتله", "color": "#8B0000"},
            "detective": {"title": "انت المحقق", "desc": "دورك فحص شخص كل ليلة", "instruction": "راح توصلك نافذة فيها اسماء اللاعبين اضغط على الاسم اللي تبي تفحصه", "color": "#1E90FF"},
            "doctor": {"title": "انت الدكتور", "desc": "دورك حماية شخص كل ليلة", "instruction": "راح توصلك نافذة فيها اسماء اللاعبين اضغط على الاسم اللي تبي تحميه او احمي نفسك", "color": "#32CD32"},
            "citizen": {"title": "انت مواطن", "desc": "دورك المشاركة في التصويت", "instruction": "ليس لك دور في الليل صوت في القروب وقت النهار", "color": "#808080"}
        }
        info = role_info[role]
        flex = FlexSendMessage(
            alt_text="دورك في لعبة المافيا",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "دورك السري", "weight": "bold", "size": "lg", "color": "#FFFFFF", "align": "center"}], "backgroundColor": info["color"], "paddingAll": "20px", "cornerRadius": "10px"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": info["title"], "size": "xxl", "color": COLORS['text_dark'], "weight": "bold", "align": "center"}], "margin": "lg"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "دورك", "size": "md", "color": COLORS['text_dark'], "weight": "bold"}, {"type": "text", "text": info["desc"], "size": "sm", "color": COLORS['text_light'], "margin": "md", "wrap": True}], "margin": "lg"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "كيف تلعب", "size": "md", "color": COLORS['text_dark'], "weight": "bold"}, {"type": "text", "text": info["instruction"], "size": "sm", "color": COLORS['primary'], "margin": "md", "wrap": True, "weight": "bold"}], "margin": "md"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "لا تشارك دورك مع احد", "size": "xs", "color": COLORS['text_light'], "align": "center", "wrap": True}], "margin": "md"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )
        try:
            self.line_bot_api.push_message(user_id, flex)
            if role != "citizen":
                import time
                time.sleep(1)
                self.send_action_buttons_private(user_id, role)
        except Exception as e:
            print(f"خطأ في ارسال الدور للاعب {user_id}: {e}")
    
    def send_action_buttons_private(self, user_id, role):
        alive_others = [p for uid, p in self.players.items() if p["alive"] and uid != user_id]
        role_configs = {
            "mafia": {"title": "اختر من تريد قتله", "action": "اقتل", "color": "#8B0000"},
            "detective": {"title": "اختر من تريد فحصه", "action": "افحص", "color": "#1E90FF"},
            "doctor": {"title": "اختر من تريد حمايته", "action": "احمي", "color": "#32CD32"}
        }
        config = role_configs.get(role, {})
        action_text = config.get("action", "اختر")
        buttons = []
        if role == "doctor":
            buttons.append({"type": "button", "action": {"type": "message", "label": "احمي نفسي", "text": f"{action_text} نفسي"}, "style": "primary", "color": config["color"], "height": "sm"})
            if alive_others:
                buttons.append({"type": "separator", "margin": "md", "color": COLORS['border']})
        for i, p in enumerate(alive_others[:13]):
            buttons.append({"type": "button", "action": {"type": "message", "label": f"{p['name']}", "text": f"{action_text} {p['name']}"}, "style": "secondary", "height": "sm", "margin": "xs" if (i > 0 or role == "doctor") else "none"})
        flex = FlexSendMessage(
            alt_text=config.get("title", "اختر هدفك"),
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": config.get("title", "اختر هدفك"), "size": "md", "color": "#FFFFFF", "align": "center", "wrap": True}], "backgroundColor": config.get("color", COLORS['primary']), "paddingAll": "20px", "cornerRadius": "10px"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": f"اللاعبون الاحياء {len(alive_others) + 1}", "size": "md", "color": COLORS['text_dark'], "weight": "bold"}], "margin": "lg"},
                        {"type": "box", "layout": "vertical", "contents": buttons, "margin": "md"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )
        try:
            self.line_bot_api.push_message(user_id, flex)
        except Exception as e:
            print(f"خطأ في ارسال الازرار للاعب {user_id}: {e}")

    def night_flex(self):
        alive_players = [p for p in self.players.values() if p["alive"]]
        return FlexSendMessage(
            alt_text="مرحلة الليل",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": f"اليوم {self.day} الليل", "size": "md", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "10px"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "الليل حل", "size": "xl", "color": COLORS['text_dark'], "weight": "bold", "align": "center"}, {"type": "text", "text": "تحقق من رسائلك الخاصة", "size": "sm", "color": COLORS['primary'], "margin": "md", "align": "center", "wrap": True}, {"type": "text", "text": f"اللاعبون الاحياء {len(alive_players)}", "size": "sm", "color": COLORS['text_light'], "margin": "md", "align": "center"}], "margin": "lg"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "button", "action": {"type": "message", "label": "انهاء الليل", "text": "إنهاء الليل"}, "style": "primary", "color": COLORS['primary'], "height": "sm"}], "margin": "lg"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )
    
    def process_night(self):
        messages = []
        mafia_target = self.night_actions.get("mafia_target")
        doctor_target = self.night_actions.get("doctor_target")
        if mafia_target:
            if mafia_target == doctor_target:
                messages.append("طلع النهار لم يقتل احد الليلة")
            else:
                self.players[mafia_target]["alive"] = False
                victim_name = self.players[mafia_target]["name"]
                messages.append(f"طلع النهار تم قتل {victim_name}")
        else:
            messages.append("طلع النهار لم يقتل احد الليلة")
        self.night_actions = {}
        self.phase = "day"
        winner_check = self.check_winner()
        if winner_check:
            return winner_check
        return {"response": [TextSendMessage(text=msg) for msg in messages] + [self.day_flex()]}

    def day_flex(self):
        alive_players = [p for p in self.players.values() if p["alive"]]
        return FlexSendMessage(
            alt_text="مرحلة النهار",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": f"اليوم {self.day} النهار", "size": "md", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "10px"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "مناقشة ثم التصويت", "size": "lg", "color": COLORS['text_dark'], "weight": "bold", "align": "center"}, {"type": "text", "text": f"اللاعبون الاحياء {len(alive_players)}", "size": "sm", "color": COLORS['text_light'], "margin": "md", "align": "center"}], "margin": "lg"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "button", "action": {"type": "message", "label": "تصويت", "text": "تصويت مافيا"}, "style": "primary", "color": COLORS['primary'], "height": "sm"}], "margin": "lg"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

    def voting_flex(self):
        alive = [p for p in self.players.values() if p["alive"]]
        buttons = []
        for i, p in enumerate(alive[:10]):
            buttons.append({"type": "button", "action": {"type": "message", "label": p["name"], "text": f"صوت {p['name']}"}, "style": "secondary", "height": "sm", "margin": "xs" if i > 0 else "none"})
        buttons.append({"type": "separator", "margin": "md"})
        buttons.append({"type": "button", "action": {"type": "message", "label": "انهاء التصويت", "text": "إنهاء التصويت"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "md"})
        return FlexSendMessage(
            alt_text="التصويت",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "التصويت", "size": "md", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "10px"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "اضغط على اسم من تظنه المافيا", "size": "md", "color": COLORS['text_dark'], "weight": "bold", "align": "center", "wrap": True}], "margin": "lg"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "box", "layout": "vertical", "contents": buttons, "margin": "lg"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

    def vote(self, user_id, target_name):
        if self.phase != "voting":
            return {"response": TextSendMessage(text="ليس وقت التصويت")}
        if user_id not in self.players or not self.players[user_id]["alive"]:
            return {"response": TextSendMessage(text="لا يمكنك التصويت")}
        for uid, p in self.players.items():
            if p["name"] == target_name and p["alive"]:
                self.votes[user_id] = uid
                return {"response": TextSendMessage(text=f"تم تصويتك لـ {target_name}")}
        return {"response": TextSendMessage(text="لا يوجد لاعب بهذا الاسم")}

    def end_voting(self):
        if not self.votes:
            self.phase = "night"
            self.day += 1
            return {"response": [TextSendMessage(text="لم يتم التصويت الانتقال لليل"), self.night_flex()]}
        vote_counts = {}
        for target_uid in self.votes.values():
            vote_counts[target_uid] = vote_counts.get(target_uid, 0) + 1
        killed_uid = max(vote_counts, key=vote_counts.get)
        self.players[killed_uid]["alive"] = False
        killed_name = self.players[killed_uid]["name"]
        self.votes = {}
        self.phase = "night"
        self.day += 1
        result = self.check_winner()
        if result:
            return result
        return {"response": [TextSendMessage(text=f"تم التصويت على {killed_name} واعدامه"), self.night_flex()]}

    def check_winner(self):
        mafia_count = sum(1 for p in self.players.values() if p["alive"] and p["role"] == "mafia")
        citizen_count = sum(1 for p in self.players.values() if p["alive"] and p["role"] != "mafia")
        if mafia_count == 0:
            self.phase = "ended"
            return {"response": self.winner_flex("المواطنون"), "game_over": True}
        if mafia_count >= citizen_count:
            self.phase = "ended"
            return {"response": self.winner_flex("المافيا"), "game_over": True}
        return None

    def winner_flex(self, winner_team):
        return FlexSendMessage(
            alt_text="نهاية لعبة المافيا",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "انتهت اللعبة", "weight": "bold", "size": "lg", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "10px"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "الفائز", "size": "sm", "color": COLORS['text_light'], "align": "center"}, {"type": "text", "text": winner_team, "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center", "margin": "md"}], "margin": "lg"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "button", "action": {"type": "message", "label": "اعادة", "text": "مافيا"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "lg"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

    def check_answer(self, text, user_id, display_name):
        text = text.strip()
        if text == "انضم مافيا":
            return self.add_player(user_id, display_name)
        if text == "بدء مافيا":
            return self.assign_roles()
        if text == "شرح مافيا":
            return {"response": self.explanation_flex()}
        if text == "إنهاء الليل":
            if self.phase == "night":
                return self.process_night()
            return {"response": TextSendMessage(text="ليس وقت الليل الان")}
        if text == "تصويت مافيا":
            if self.phase in ["day", "voting"]:
                self.phase = "voting"
                return {"response": self.voting_flex()}
            return {"response": TextSendMessage(text="ليس وقت التصويت الان")}
        if text.startswith("صوت "):
            target_name = text.replace("صوت ", "").strip()
            return self.vote(user_id, target_name)
        if text == "إنهاء التصويت":
            if self.phase == "voting":
                return self.end_voting()
            return {"response": TextSendMessage(text="ليس وقت التصويت")}
        if text.startswith("اقتل "):
            if user_id not in self.players or self.players[user_id]["role"] != "mafia":
                return {"response": TextSendMessage(text="انت لست المافيا")}
            if self.phase != "night":
                return {"response": TextSendMessage(text="ليس وقت الليل")}
            target_name = text.replace("اقتل ", "").strip()
            for uid, p in self.players.items():
                if p["name"] == target_name and p["alive"] and uid != user_id:
                    self.night_actions["mafia_target"] = uid
                    return {"response": TextSendMessage(text=f"تم الاختيار {target_name} سيتم قتله عند انهاء الليل")}
            return {"response": TextSendMessage(text="لا يوجد لاعب بهذا الاسم")}
        if text.startswith("افحص "):
            if user_id not in self.players or self.players[user_id]["role"] != "detective":
                return {"response": TextSendMessage(text="انت لست المحقق")}
            if self.phase != "night":
                return {"response": TextSendMessage(text="ليس وقت الليل")}
            target_name = text.replace("افحص ", "").strip()
            for uid, p in self.players.items():
                if p["name"] == target_name and p["alive"] and uid != user_id:
                    role = p["role"]
                    result_text = "مافيا" if role == "mafia" else "بريء"
                    return {"response": TextSendMessage(text=f"نتيجة الفحص {target_name} هو {result_text}")}
            return {"response": TextSendMessage(text="لا يوجد لاعب بهذا الاسم")}
        if text.startswith("احمي "):
            if user_id not in self.players or self.players[user_id]["role"] != "doctor":
                return {"response": TextSendMessage(text="انت لست الدكتور")}
            if self.phase != "night":
                return {"response": TextSendMessage(text="ليس وقت الليل")}
            target_text = text.replace("احمي ", "").strip()
            if target_text == "نفسي":
                self.night_actions["doctor_target"] = user_id
                return {"response": TextSendMessage(text="تم الاختيار سيتم حمايتك الليلة")}
            else:
                for uid, p in self.players.items():
                    if p["name"] == target_text and p["alive"]:
                        self.night_actions["doctor_target"] = uid
                        return {"response": TextSendMessage(text=f"تم الاختيار {target_text} سيتم حمايته الليلة")}
                return {"response": TextSendMessage(text="لا يوجد لاعب بهذا الاسم")}
        return None
    
    def next_question(self):
        return None
