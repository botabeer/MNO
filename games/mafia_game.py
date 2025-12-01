from linebot.models import TextSendMessage, FlexSendMessage
import random
from datetime import datetime, timedelta
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
        self.mafia_target = None
        self.doctor_target = None
        self.detective_check = None

    def start_game(self):
        self.phase = "registration"
        self.players = {}
        self.votes = {}
        self.night_actions = {}
        self.day = 0
        return self.registration_flex()

    def registration_flex(self):
        return FlexSendMessage(
            alt_text="لعبة المافيا - التسجيل",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "lg", "color": COLORS['white'], "align": "center"},
                                {"type": "text", "text": "لعبة المافيا", "size": "md", "color": COLORS['white'], "align": "center", "margin": "xs"}
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "10px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "انضم للعبة", "size": "lg", "color": COLORS['text_dark'], "weight": "bold"},
                                {"type": "text", "text": f"اللاعبين المسجلين: {len(self.players)}", "size": "md", "color": COLORS['text_light'], "margin": "md"},
                                {"type": "text", "text": f"الحد الأدنى: {MAFIA_CONFIG['min_players']} لاعبين", "size": "sm", "color": COLORS['text_light'], "margin": "xs"}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {"type": "message", "label": "انضم", "text": "انضم مافيا"},
                                    "style": "primary",
                                    "color": COLORS['primary'],
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {"type": "message", "label": "بدء اللعبة", "text": "بدء مافيا"},
                                    "style": "secondary",
                                    "height": "sm",
                                    "margin": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {"type": "message", "label": "شرح اللعبة", "text": "شرح مافيا"},
                                    "style": "secondary",
                                    "height": "sm",
                                    "margin": "sm"
                                }
                            ],
                            "margin": "lg"
                        }
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
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "lg", "color": COLORS['white'], "align": "center"},
                                {"type": "text", "text": "شرح لعبة المافيا", "size": "md", "color": COLORS['white'], "align": "center", "margin": "xs"}
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "10px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "الأدوار", "size": "lg", "color": COLORS['text_dark'], "weight": "bold"},
                                {"type": "text", "text": "🔪 المافيا: يقتل شخصاً كل ليلة", "size": "sm", "color": COLORS['text_light'], "margin": "md", "wrap": True},
                                {"type": "text", "text": "🔍 المحقق: يكشف دور شخص كل ليلة", "size": "sm", "color": COLORS['text_light'], "margin": "xs", "wrap": True},
                                {"type": "text", "text": "⚕️ الدكتور: يحمي شخصاً كل ليلة", "size": "sm", "color": COLORS['text_light'], "margin": "xs", "wrap": True},
                                {"type": "text", "text": "👤 المواطن: يصوت في النهار", "size": "sm", "color": COLORS['text_light'], "margin": "xs", "wrap": True}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "طريقة اللعب", "size": "lg", "color": COLORS['text_dark'], "weight": "bold"},
                                {"type": "text", "text": "🌙 الليل: أدوار سرية في الخاص", "size": "sm", "color": COLORS['text_light'], "margin": "md", "wrap": True},
                                {"type": "text", "text": "☀️ النهار: مناقشة وتصويت جماعي", "size": "sm", "color": COLORS['text_light'], "margin": "xs", "wrap": True},
                                {"type": "text", "text": "🏆 الفوز: المواطنون يقضون على المافيا أو المافيا تسيطر", "size": "sm", "color": COLORS['text_light'], "margin": "xs", "wrap": True}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "عودة للتسجيل", "text": "مافيا"},
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
        )

    def add_player(self, user_id, name):
        if self.phase != "registration":
            return {"response": TextSendMessage(text="اللعبة بدأت بالفعل")}
        
        if user_id in self.players:
            return {"response": TextSendMessage(text="أنت مسجل بالفعل")}
        
        self.players[user_id] = {"name": name, "role": None, "alive": True}
        return {"response": self.registration_flex()}

    def assign_roles(self):
        if len(self.players) < MAFIA_CONFIG["min_players"]:
            return {"response": TextSendMessage(text=f"عدد اللاعبين غير كافٍ. الحد الأدنى {MAFIA_CONFIG['min_players']} لاعبين")}

        roles = ["mafia", "detective", "doctor"]
        remaining = len(self.players) - len(roles)
        roles += ["citizen"] * remaining
        random.shuffle(roles)

        for uid, role in zip(self.players.keys(), roles):
            self.players[uid]["role"] = role
            self.send_role_private(uid, role)

        self.phase = "night"
        self.day = 1
        return {"response": [
            TextSendMessage(text="تم توزيع الأدوار في الخاص لكل لاعب"),
            self.night_flex()
        ]}

    def send_role_private(self, user_id, role):
        role_info = {
            "mafia": {"title": "أنت المافيا 🔪", "desc": "اختر شخصاً للقتل كل ليلة في الخاص", "color": "#8B0000"},
            "detective": {"title": "أنت المحقق 🔍", "desc": "افحص دور شخص كل ليلة في الخاص", "color": "#1E90FF"},
            "doctor": {"title": "أنت الدكتور ⚕️", "desc": "احمِ شخصاً كل ليلة في الخاص", "color": "#32CD32"},
            "citizen": {"title": "أنت مواطن 👤", "desc": "صوّت في النهار للقضاء على المافيا", "color": "#808080"}
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
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "lg", "color": "#FFFFFF", "align": "center"},
                                {"type": "text", "text": "دورك السري", "size": "md", "color": "#FFFFFF", "align": "center", "margin": "xs"}
                            ],
                            "backgroundColor": info["color"],
                            "paddingAll": "20px",
                            "cornerRadius": "10px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": info["title"], "size": "xl", "color": COLORS['text_dark'], "weight": "bold", "align": "center"},
                                {"type": "text", "text": info["desc"], "size": "sm", "color": COLORS['text_light'], "margin": "md", "wrap": True, "align": "center"}
                            ],
                            "margin": "lg"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )
        
        try:
            self.line_bot_api.push_message(user_id, flex)
        except Exception as e:
            print(f"خطأ في إرسال الدور للاعب {user_id}: {e}")

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
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "lg", "color": COLORS['white'], "align": "center"},
                                {"type": "text", "text": f"اليوم {self.day} - مرحلة الليل 🌙", "size": "md", "color": COLORS['white'], "align": "center", "margin": "xs"}
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "10px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "الأدوار الخاصة تعمل الآن", "size": "lg", "color": COLORS['text_dark'], "weight": "bold", "align": "center"},
                                {"type": "text", "text": "تحقق من رسائلك الخاصة", "size": "sm", "color": COLORS['text_light'], "margin": "md", "align": "center"},
                                {"type": "text", "text": f"اللاعبون الأحياء: {len(alive_players)}", "size": "sm", "color": COLORS['text_light'], "margin": "md", "align": "center"}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {"type": "message", "label": "حالة اللعبة", "text": "حالة مافيا"},
                                    "style": "secondary",
                                    "height": "sm"
                                }
                            ],
                            "margin": "lg"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

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
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "lg", "color": COLORS['white'], "align": "center"},
                                {"type": "text", "text": f"اليوم {self.day} - مرحلة النهار ☀️", "size": "md", "color": COLORS['white'], "align": "center", "margin": "xs"}
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "10px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "مناقشة ثم التصويت", "size": "lg", "color": COLORS['text_dark'], "weight": "bold", "align": "center"},
                                {"type": "text", "text": f"اللاعبون الأحياء: {len(alive_players)}", "size": "sm", "color": COLORS['text_light'], "margin": "md", "align": "center"}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {"type": "message", "label": "تصويت", "text": "تصويت مافيا"},
                                    "style": "primary",
                                    "color": COLORS['primary'],
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {"type": "message", "label": "حالة اللعبة", "text": "حالة مافيا"},
                                    "style": "secondary",
                                    "height": "sm",
                                    "margin": "sm"
                                }
                            ],
                            "margin": "lg"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

    def status_flex(self):
        alive = [p for p in self.players.values() if p["alive"]]
        dead = [p for p in self.players.values() if not p["alive"]]
        
        alive_text = "\n".join([f"✅ {p['name']}" for p in alive]) if alive else "لا يوجد"
        dead_text = "\n".join([f"❌ {p['name']}" for p in dead]) if dead else "لا يوجد"
        
        phase_text = {
            "registration": "التسجيل",
            "night": "🌙 الليل",
            "day": "☀️ النهار",
            "voting": "🗳️ التصويت",
            "ended": "انتهت"
        }
        
        return FlexSendMessage(
            alt_text="حالة لعبة المافيا",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "lg", "color": COLORS['white'], "align": "center"},
                                {"type": "text", "text": "حالة لعبة المافيا", "size": "md", "color": COLORS['white'], "align": "center", "margin": "xs"}
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "10px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": f"اليوم: {self.day}", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                                {"type": "text", "text": f"المرحلة: {phase_text.get(self.phase, self.phase)}", "size": "sm", "color": COLORS['text_light'], "margin": "xs"}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "اللاعبون الأحياء", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                                {"type": "text", "text": alive_text, "size": "sm", "color": COLORS['text_light'], "margin": "md", "wrap": True}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "اللاعبون المقتولون", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                                {"type": "text", "text": dead_text, "size": "sm", "color": COLORS['text_light'], "margin": "md", "wrap": True}
                            ],
                            "margin": "lg"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

    def voting_flex(self):
        alive = [p for p in self.players.values() if p["alive"]]
        
        buttons = [
            {
                "type": "button",
                "action": {"type": "message", "label": p["name"], "text": f"صوت {p['name']}"},
                "style": "secondary",
                "height": "sm",
                "margin": "xs" if i > 0 else "none"
            }
            for i, p in enumerate(alive[:10])
        ]
        
        return FlexSendMessage(
            alt_text="التصويت",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "lg", "color": COLORS['white'], "align": "center"},
                                {"type": "text", "text": "التصويت 🗳️", "size": "md", "color": COLORS['white'], "align": "center", "margin": "xs"}
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "10px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "صوّت على من تظن أنه المافيا", "size": "md", "color": COLORS['text_dark'], "weight": "bold", "align": "center", "wrap": True}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": buttons,
                            "margin": "lg"
                        }
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
            return {"response": [
                TextSendMessage(text="لم يتم التصويت. الانتقال لليل"),
                self.night_flex()
            ]}
        
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
        
        return {"response": [
            TextSendMessage(text=f"تم التصويت على {killed_name} وإعدامه"),
            self.night_flex()
        ]}

    def check_winner(self):
        mafia_count = sum(1 for p in self.players.values() if p["alive"] and p["role"] == "mafia")
        citizen_count = sum(1 for p in self.players.values() if p["alive"] and p["role"] != "mafia")
        
        if mafia_count == 0:
            self.phase = "ended"
            return {"response": self.winner_flex("المواطنون 🎉"), "game_over": True}
        
        if mafia_count >= citizen_count:
            self.phase = "ended"
            return {"response": self.winner_flex("المافيا 🔪"), "game_over": True}
        
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
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "بوت الحوت", "weight": "bold", "size": "lg", "color": COLORS['white'], "align": "center"},
                                {"type": "text", "text": "انتهت اللعبة 🏆", "size": "md", "color": COLORS['white'], "align": "center", "margin": "xs"}
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "10px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "الفائز", "size": "sm", "color": COLORS['text_light'], "align": "center"},
                                {"type": "text", "text": winner_team, "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center", "margin": "md"}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "إعادة", "text": "مافيا"},
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
        )

    def check_answer(self, text, user_id, display_name):
        text = text.strip()
        
        if text == "انضم مافيا":
            return self.add_player(user_id, display_name)
        
        if text == "بدء مافيا":
            return self.assign_roles()
        
        if text == "شرح مافيا":
            return {"response": self.explanation_flex()}
        
        if text == "حالة مافيا":
            return {"response": self.status_flex()}
        
        if text == "تصويت مافيا":
            if self.phase in ["day", "voting"]:
                self.phase = "voting"
                return {"response": self.voting_flex()}
            return {"response": TextSendMessage(text="ليس وقت التصويت")}
        
        if text.startswith("صوت "):
            target_name = text.replace("صوت ", "").strip()
            return self.vote(user_id, target_name)
        
        if text == "إنهاء تصويت":
            if self.phase == "voting":
                return self.end_voting()
        
        return None
