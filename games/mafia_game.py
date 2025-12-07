# games/mafia_game.py - Enhanced and Simplified Mafia Game
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer, PushMessageRequest
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
        return self.registration_flex()

    def registration_flex(self):
        player_count = len(self.players)
        min_players = MAFIA_CONFIG['min_players']
        
        status_color = COLORS['success'] if player_count >= min_players else COLORS['warning']
        status_text = f"{player_count} لاعب مسجل"
        
        if player_count < min_players:
            status_text += f"\nالحد الأدنى: {min_players} لاعبين"

        players_list = []
        for i, (uid, player) in enumerate(self.players.items(), 1):
            players_list.append({
                "type": "text",
                "text": f"{i}. {player['name']}",
                "size": "xs",
                "color": COLORS['text_dark'],
                "margin": "xs"
            })

        contents = [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": "لعبة المافيا",
                    "weight": "bold",
                    "size": "xl",
                    "color": COLORS['white'],
                    "align": "center"
                }],
                "backgroundColor": COLORS['primary'],
                "paddingAll": "16px",
                "cornerRadius": "10px"
            },
            {
                "type": "box",
                "layout": "vertical",
                "margin": "lg",
                "spacing": "sm",
                "contents": [{
                    "type": "text",
                    "text": status_text,
                    "size": "md",
                    "color": status_color,
                    "align": "center",
                    "weight": "bold"
                }]
            }
        ]

        if players_list:
            contents.append({
                "type": "separator",
                "margin": "md",
                "color": COLORS['border']
            })
            contents.append({
                "type": "box",
                "layout": "vertical",
                "spacing": "xs",
                "margin": "md",
                "contents": players_list
            })

        contents.extend([
            {"type": "separator", "margin": "md", "color": COLORS['border']},
            {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "margin": "md",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "انضم للعبة", "text": "انضم مافيا"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "بدء اللعبة", "text": "بدء مافيا"},
                        "style": "secondary",
                        "height": "sm"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "شرح اللعبة", "text": "شرح مافيا"},
                        "style": "secondary",
                        "height": "sm"
                    }
                ]
            }
        ])

        return FlexMessage(
            alt_text="لعبة المافيا",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": contents,
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "16px"
                }
            })
        )

    def explanation_flex(self):
        sections = [
            {"title": "الخطوة 1: التسجيل", "text": "اضغط 'انضم مافيا' في المجموعة"},
            {"title": "الخطوة 2: البدء", "text": "عند اكتمال العدد، اضغط 'بدء مافيا'"},
            {"title": "الخطوة 3: الدور", "text": "ستصلك رسالة خاصة بدورك في اللعبة"},
            {"title": "الليل - في الخاص", "text": "المافيا: اقتل اسم\nالمحقق: افحص اسم\nالدكتور: احمي اسم"},
            {"title": "النهار - في المجموعة", "text": "ناقش ثم اكتب 'تصويت مافيا'\nثم 'صوت اسم' للتصويت\nثم 'إنهاء التصويت'"},
            {"title": "الفوز", "text": "المافيا تفوز إذا ساوت عدد المواطنين\nالمواطنون يفوزون إذا قتلوا المافيا"}
        ]

        contents = [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": "شرح لعبة المافيا",
                    "weight": "bold",
                    "size": "lg",
                    "color": COLORS['white'],
                    "align": "center"
                }],
                "backgroundColor": COLORS['primary'],
                "paddingAll": "12px",
                "cornerRadius": "8px"
            }
        ]

        for section in sections:
            contents.append({
                "type": "box",
                "layout": "vertical",
                "spacing": "xs",
                "margin": "md",
                "contents": [
                    {"type": "text", "text": section['title'], "color": COLORS['primary'], "weight": "bold", "size": "sm"},
                    {"type": "text", "text": section['text'], "color": COLORS['text_light'], "size": "xs", "wrap": True, "margin": "xs"}
                ]
            })

        contents.extend([
            {"type": "separator", "margin": "md", "color": COLORS['border']},
            {
                "type": "button",
                "action": {"type": "message", "label": "فهمت، ابدأ اللعبة", "text": "انضم مافيا"},
                "style": "primary",
                "color": COLORS['primary'],
                "height": "sm",
                "margin": "md"
            }
        ])

        return FlexMessage(
            alt_text="شرح المافيا",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": contents,
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "16px"
                }
            })
        )

    def add_player(self, user_id: str, name: str):
        if self.phase != "registration":
            return {"response": TextMessage(text="اللعبة بدأت بالفعل")}
        
        if user_id in self.players:
            return {"response": TextMessage(text="أنت مسجل بالفعل")}
        
        self.players[user_id] = {"name": name, "role": None, "alive": True}
        return {"response": self.registration_flex()}

    def assign_roles(self):
        if len(self.players) < MAFIA_CONFIG["min_players"]:
            return {"response": TextMessage(text=f"عدد اللاعبين غير كافٍ. الحد الأدنى {MAFIA_CONFIG['min_players']} لاعبين")}

        roles = ["mafia", "detective", "doctor"]
        remaining = len(self.players) - len(roles)
        roles += ["citizen"] * remaining
        random.shuffle(roles)

        for uid, role in zip(list(self.players.keys()), roles):
            self.players[uid]["role"] = role
            self._send_role_private(uid, role)

        self.phase = "night"
        self.day = 1

        return {
            "response": [
                TextMessage(text="تم توزيع الأدوار في الخاص لكل لاعب\nتحقق من رسائلك الخاصة"),
                self._night_flex()
            ]
        }

    def _send_role_private(self, user_id: str, role: str):
        role_info = {
            "mafia": {"title": "أنت المافيا", "desc": "دورك: قتل شخص كل ليلة\nاكتب في الخاص: اقتل اسم", "color": "#8B0000"},
            "detective": {"title": "أنت المحقق", "desc": "دورك: فحص شخص كل ليلة\nاكتب في الخاص: افحص اسم", "color": "#1E90FF"},
            "doctor": {"title": "أنت الدكتور", "desc": "دورك: حماية شخص كل ليلة\nاكتب في الخاص: احمي اسم\nأو احمي نفسي", "color": "#32CD32"},
            "citizen": {"title": "أنت مواطن", "desc": "دورك: التصويت بالنهار\nساعد في كشف المافيا", "color": "#808080"}
        }

        info = role_info[role]
        
        flex = FlexMessage(
            alt_text="دورك في المافيا",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [{"type": "text", "text": "دورك السري", "size": "md", "color": "#FFFFFF", "align": "center"}],
                            "backgroundColor": info['color'],
                            "paddingAll": "12px",
                            "cornerRadius": "8px"
                        },
                        {"type": "text", "text": info['title'], "size": "xxl", "weight": "bold", "align": "center", "color": info['color'], "margin": "lg"},
                        {"type": "separator", "margin": "md", "color": COLORS['border']},
                        {"type": "text", "text": info['desc'], "size": "sm", "color": COLORS['text_dark'], "wrap": True, "align": "center", "margin": "md"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "16px"
                }
            })
        )

        try:
            self.line_bot_api.push_message(PushMessageRequest(to=user_id, messages=[flex]))
        except Exception as e:
            print(f"خطأ عند إرسال الدور: {e}")

    def _night_flex(self):
        alive_count = sum(1 for p in self.players.values() if p["alive"])
        
        return FlexMessage(
            alt_text="مرحلة الليل",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [{"type": "text", "text": f"اليوم {self.day} - الليل", "size": "lg", "color": COLORS['white'], "align": "center", "weight": "bold"}],
                            "backgroundColor": "#2C3E50",
                            "paddingAll": "14px",
                            "cornerRadius": "10px"
                        },
                        {"type": "text", "text": f"اللاعبون الأحياء: {alive_count}", "size": "sm", "color": COLORS['text_light'], "align": "center", "margin": "md"},
                        {"type": "separator", "margin": "md", "color": COLORS['border']},
                        {"type": "text", "text": "تحقق من رسائلك الخاصة\nاستخدم دورك الليلي", "size": "md", "color": COLORS['text_dark'], "align": "center", "wrap": True, "margin": "md"},
                        {"type": "separator", "margin": "md", "color": COLORS['border']},
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "إنهاء الليل والانتقال للنهار", "text": "إنهاء الليل"},
                            "style": "primary",
                            "color": COLORS['primary'],
                            "height": "sm",
                            "margin": "md"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "16px"
                }
            })
        )

    def process_night(self):
        msgs = []
        mafia_target = self.night_actions.get("mafia_target")
        doctor_target = self.night_actions.get("doctor_target")

        if mafia_target:
            if mafia_target == doctor_target:
                msgs.append("طلع النهار...\nلم يُقتل أحد الليلة! الدكتور أنقذه")
            else:
                self.players[mafia_target]["alive"] = False
                victim_name = self.players[mafia_target]['name']
                msgs.append(f"طلع النهار...\nتم قتل {victim_name}")
        else:
            msgs.append("طلع النهار...\nلم يُقتل أحد الليلة")

        self.night_actions = {}
        self.phase = "day"

        winner = self._check_winner()
        if winner:
            return winner

        return {"response": [TextMessage(text=m) for m in msgs] + [self._day_flex()]}

    def _day_flex(self):
        alive_players = [(uid, p) for uid, p in self.players.items() if p["alive"]]
        
        players_list = []
        for i, (uid, player) in enumerate(alive_players, 1):
            players_list.append({"type": "text", "text": f"{i}. {player['name']}", "size": "xs", "color": COLORS['text_dark'], "margin": "xs"})

        return FlexMessage(
            alt_text="مرحلة النهار",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [{"type": "text", "text": f"اليوم {self.day} - النهار", "size": "lg", "color": "#FFFFFF", "align": "center", "weight": "bold"}],
                            "backgroundColor": "#F39C12",
                            "paddingAll": "14px",
                            "cornerRadius": "10px"
                        },
                        {"type": "text", "text": "اللاعبون الأحياء:", "size": "sm", "color": COLORS['primary'], "weight": "bold", "margin": "md"},
                        {"type": "box", "layout": "vertical", "spacing": "xs", "contents": players_list},
                        {"type": "separator", "margin": "md", "color": COLORS['border']},
                        {"type": "text", "text": "ناقش من المشكوك به\nثم ابدأ التصويت", "size": "sm", "color": COLORS['text_light'], "align": "center", "wrap": True, "margin": "md"},
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "بدء التصويت", "text": "تصويت مافيا"},
                            "style": "primary",
                            "color": COLORS['primary'],
                            "height": "sm",
                            "margin": "md"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "16px"
                }
            })
        )

    def vote(self, user_id: str, target_name: str):
        if self.phase != "voting":
            return {"response": TextMessage(text="ليس وقت التصويت")}
        
        if user_id not in self.players or not self.players[user_id]["alive"]:
            return {"response": TextMessage(text="لا يمكنك التصويت")}
        
        for uid, p in self.players.items():
            if p["name"] == target_name and p["alive"]:
                self.votes[user_id] = uid
                return {"response": TextMessage(text=f"تم التصويت لـ {target_name}")}
        
        return {"response": TextMessage(text="لا يوجد لاعب بهذا الاسم")}

    def end_voting(self):
        if not self.votes:
            self.phase = "night"
            self.day += 1
            return {"response": [TextMessage(text="لم يتم التصويت. الانتقال لليل"), self._night_flex()]}

        counts = {}
        for uid in self.votes.values():
            counts[uid] = counts.get(uid, 0) + 1

        killed = max(counts, key=counts.get)
        self.players[killed]['alive'] = False
        killed_name = self.players[killed]['name']
        killed_role = self.players[killed]['role']

        self.votes = {}
        self.phase = "night"
        self.day += 1

        winner = self._check_winner()
        if winner:
            return winner

        return {
            "response": [
                TextMessage(text=f"تم التصويت على {killed_name} وإعدامه\nكان دوره: {self._translate_role(killed_role)}"),
                self._night_flex()
            ]
        }

    def _translate_role(self, role):
        roles = {"mafia": "المافيا", "detective": "المحقق", "doctor": "الدكتور", "citizen": "مواطن"}
        return roles.get(role, role)

    def _check_winner(self):
        mafia_count = sum(1 for p in self.players.values() if p['alive'] and p['role'] == 'mafia')
        citizens_count = sum(1 for p in self.players.values() if p['alive'] and p['role'] != 'mafia')

        if mafia_count == 0:
            self.phase = 'ended'
            return {"response": self._winner_flex("المواطنون"), "game_over": True}
        
        if mafia_count >= citizens_count:
            self.phase = 'ended'
            return {"response": self._winner_flex("المافيا"), "game_over": True}

        return None

    def _winner_flex(self, winner_team: str):
        return FlexMessage(
            alt_text="انتهت اللعبة",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [{"type": "text", "text": "انتهت اللعبة", "size": "lg", "weight": "bold", "color": COLORS['white'], "align": "center"}],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "14px",
                            "cornerRadius": "10px"
                        },
                        {"type": "text", "text": "الفائز", "size": "sm", "color": COLORS['text_light'], "align": "center", "margin": "lg"},
                        {"type": "text", "text": winner_team, "size": "xxl", "color": COLORS['success'], "weight": "bold", "align": "center", "margin": "xs"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "لعب مرة أخرى", "text": "مافيا"},
                            "style": "primary",
                            "color": COLORS['primary'],
                            "height": "sm",
                            "margin": "md"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "16px"
                }
            })
        )

    def check_answer(self, text: str, user_id: str, display_name: str):
        text = text.strip()

        if text == "انضم مافيا":
            return self.add_player(user_id, display_name)
        
        if text == "بدء مافيا":
            return self.assign_roles()
        
        if text == "شرح مافيا":
            return {"response": self.explanation_flex()}
        
        if text == "حالة مافيا":
            alive = [p['name'] for p in self.players.values() if p['alive']]
            dead = [p['name'] for p in self.players.values() if not p['alive']]
            status = f"اليوم: {self.day}\nالمرحلة: {self.phase}\n\nالأحياء ({len(alive)}):\n"
            status += "\n".join(alive) if alive else "لا أحد"
            status += f"\n\nالموتى ({len(dead)}):\n"
            status += "\n".join(dead) if dead else "لا أحد"
            return {"response": TextMessage(text=status)}

        if text == "إنهاء الليل":
            if self.phase == "night":
                return self.process_night()
            return {"response": TextMessage(text="ليس وقت الليل")}

        if text == "تصويت مافيا":
            if self.phase in ["day", "voting"]:
                self.phase = "voting"
                return {"response": TextMessage(text="بدأ التصويت\nاكتب: صوت اسم")}
            return {"response": TextMessage(text="ليس وقت التصويت")}
        
        if text.startswith("صوت "):
            target = text.replace("صوت ", "").strip()
            return self.vote(user_id, target)
        
        if text == "إنهاء التصويت":
            if self.phase == "voting":
                return self.end_voting()
            return {"response": TextMessage(text="ليس وقت التصويت")}

        if text.startswith("اقتل "):
            if user_id not in self.players or self.players[user_id]['role'] != 'mafia':
                return {"response": TextMessage(text="أنت لست المافيا")}
            if self.phase != "night":
                return {"response": TextMessage(text="ليس وقت الليل")}
            
            target_name = text.replace("اقتل ", "").strip()
            for uid, p in self.players.items():
                if p['name'] == target_name and p['alive'] and uid != user_id:
                    self.night_actions['mafia_target'] = uid
                    return {"response": TextMessage(text=f"تم اختيار {target_name} كضحية")}
            return {"response": TextMessage(text="لا يوجد لاعب بهذا الاسم")}

        if text.startswith("افحص "):
            if user_id not in self.players or self.players[user_id]['role'] != 'detective':
                return {"response": TextMessage(text="أنت لست المحقق")}
            if self.phase != "night":
                return {"response": TextMessage(text="ليس وقت الليل")}
            
            target_name = text.replace("افحص ", "").strip()
            for uid, p in self.players.items():
                if p['name'] == target_name and p['alive'] and uid != user_id:
                    role = p['role']
                    result = "مافيا" if role == 'mafia' else "بريء"
                    return {"response": TextMessage(text=f"نتيجة الفحص:\n{target_name} هو {result}")}
            return {"response": TextMessage(text="لا يوجد لاعب بهذا الاسم")}

        if text.startswith("احمي "):
            if user_id not in self.players or self.players[user_id]['role'] != 'doctor':
                return {"response": TextMessage(text="أنت لست الدكتور")}
            if self.phase != "night":
                return {"response": TextMessage(text="ليس وقت الليل")}
            
            target_text = text.replace("احمي ", "").strip()
            
            if target_text == "نفسي":
                self.night_actions['doctor_target'] = user_id
                return {"response": TextMessage(text="تم حمايتك الليلة")}
            
            for uid, p in self.players.items():
                if p['name'] == target_text and p['alive']:
                    self.night_actions['doctor_target'] = uid
                    return {"response": TextMessage(text=f"تم حماية {target_text} الليلة")}
            
            return {"response": TextMessage(text="لا يوجد لاعب بهذا الاسم")}

        return None
