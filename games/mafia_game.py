"""
لعبة المافيا - Mafia Game
لعبة اجتماعية بين المافيا والمواطنين
"""

from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
import logging
from constants import MAFIA_CONFIG, COLORS

logger = logging.getLogger(__name__)


class MafiaGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.players = {}
        self.phase = "registration"
        self.day = 0
        self.votes = {}
        self.night_actions = {}

    def start_game(self):
        """بدء التسجيل في اللعبة"""
        self.phase = "registration"
        self.players = {}
        self.votes = {}
        self.night_actions = {}
        self.day = 0
        logger.info("بدء لعبة المافيا - مرحلة التسجيل")
        return self.registration_flex()

    def registration_flex(self):
        """بطاقة التسجيل"""
        return FlexMessage(
            alt_text="لعبة المافيا - التسجيل",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [
                            {"type": "text", "text": "لعبة المافيا", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}
                        ], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                        
                        {"type": "box", "layout": "vertical", "contents": [
                            {"type": "text", "text": "مهم جداً", "size": "sm", "color": COLORS['warning'], "weight": "bold", "align": "center"},
                            {"type": "text", "text": "أضف البوت كصديق لاستلام دورك السري", "size": "xs", "color": COLORS['text_dark'], "wrap": True, "align": "center", "margin": "xs"}
                        ], "backgroundColor": f"{COLORS['warning']}1A", "paddingAll": "10px", "cornerRadius": "8px", "margin": "lg"},
                        
                        {"type": "box", "layout": "vertical", "contents": [
                            {"type": "text", "text": f"اللاعبون المسجلون: {len(self.players)}", "size": "md", "color": COLORS['text_dark'], "weight": "bold", "align": "center"},
                            {"type": "text", "text": f"الحد الأدنى: {MAFIA_CONFIG['min_players']} لاعبين", "size": "sm", "color": COLORS['text_light'], "margin": "xs", "align": "center"}
                        ], "margin": "lg"},
                        
                        {"type": "separator", "margin": "lg"},
                        
                        {"type": "box", "layout": "vertical", "contents": [
                            {"type": "button", "action": {"type": "message", "label": "انضم للعبة", "text": "انضم مافيا"}, "style": "primary", "color": COLORS['primary'], "height": "sm"},
                            {"type": "button", "action": {"type": "message", "label": "بدء اللعبة", "text": "بدء مافيا"}, "style": "secondary", "height": "sm", "margin": "sm"},
                            {"type": "button", "action": {"type": "message", "label": "شرح اللعبة", "text": "شرح مافيا"}, "style": "secondary", "height": "sm", "margin": "sm"}
                        ], "margin": "lg"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            })
        )

    def explanation_flex(self):
        """بطاقة شرح اللعبة"""
        return FlexMessage(
            alt_text="شرح لعبة المافيا",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [
                            {"type": "text", "text": "شرح لعبة المافيا", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}
                        ], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                        
                        {"type": "text", "text": "الفكرة الأساسية", "size": "md", "color": COLORS['text_dark'], "weight": "bold", "margin": "lg"},
                        {"type": "text", "text": "لعبة اجتماعية بين المافيا والمواطنين. المافيا يحاول يقتل الجميع والمواطنون يحاولون يكتشفونه", "size": "sm", "color": COLORS['text_light'], "wrap": True, "margin": "xs"},
                        
                        {"type": "separator", "margin": "md"},
                        {"type": "text", "text": "الأدوار", "size": "md", "color": COLORS['text_dark'], "weight": "bold", "margin": "md"},
                        
                        {"type": "box", "layout": "vertical", "contents": [
                            {"type": "text", "text": "المافيا: تختار شخص تقتله كل ليلة", "size": "sm", "color": "#8B0000", "wrap": True}
                        ], "margin": "sm", "backgroundColor": "#8B00001A", "paddingAll": "10px", "cornerRadius": "8px"},
                        
                        {"type": "box", "layout": "vertical", "contents": [
                            {"type": "text", "text": "المحقق: تفحص شخص كل ليلة لمعرفة دوره", "size": "sm", "color": "#1E90FF", "wrap": True}
                        ], "margin": "sm", "backgroundColor": "#1E90FF1A", "paddingAll": "10px", "cornerRadius": "8px"},
                        
                        {"type": "box", "layout": "vertical", "contents": [
                            {"type": "text", "text": "الدكتور: تحمي شخص من القتل كل ليلة", "size": "sm", "color": "#32CD32", "wrap": True}
                        ], "margin": "sm", "backgroundColor": "#32CD321A", "paddingAll": "10px", "cornerRadius": "8px"},
                        
                        {"type": "box", "layout": "vertical", "contents": [
                            {"type": "text", "text": "المواطن: تناقش وتصوت لاكتشاف المافيا", "size": "sm", "color": "#808080", "wrap": True}
                        ], "margin": "sm", "backgroundColor": "#8080801A", "paddingAll": "10px", "cornerRadius": "8px"},
                        
                        {"type": "separator", "margin": "lg"},
                        
                        {"type": "text", "text": "طريقة اللعب", "size": "md", "color": COLORS['text_dark'], "weight": "bold", "margin": "md"},
                        {"type": "text", "text": "1. الليل: الأدوار الخاصة تستخدم قدراتها في الخاص\n2. النهار: النقاش والتصويت في القروب\n3. التصويت: اختيار شخص للإعدام", "size": "xs", "color": COLORS['text_light'], "wrap": True, "margin": "xs"},
                        
                        {"type": "separator", "margin": "lg"},
                        {"type": "button", "action": {"type": "message", "label": "رجوع", "text": "مافيا"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "md"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            })
        )

    def add_player(self, user_id, name):
        """إضافة لاعب للعبة"""
        if self.phase != "registration":
            return {"response": TextMessage(text="اللعبة بدأت بالفعل")}
        
        if user_id in self.players:
            return {"response": TextMessage(text="أنت مسجل بالفعل")}
        
        self.players[user_id] = {"name": name, "role": None, "alive": True}
        logger.info(f"لاعب جديد انضم: {name}")
        return {"response": self.registration_flex()}

    def assign_roles(self):
        """توزيع الأدوار على اللاعبين"""
        if len(self.players) < MAFIA_CONFIG["min_players"]:
            return {"response": TextMessage(text=f"نحتاج {MAFIA_CONFIG['min_players']} لاعبين على الأقل")}
        
        # توزيع الأدوار
        roles = ["mafia", "detective", "doctor"] + ["citizen"] * (len(self.players) - 3)
        random.shuffle(roles)
        
        # إسناد الأدوار
        for uid, role in zip(self.players.keys(), roles):
            self.players[uid]["role"] = role
            self.send_role_private(uid, role)
        
        self.phase = "night"
        self.day = 1
        logger.info(f"تم توزيع الأدوار على {len(self.players)} لاعب")
        return {"response": [TextMessage(text="تم توزيع الأدوار بنجاح\nتحقق من رسائلك الخاصة لمعرفة دورك"), self.night_flex()]}

    def send_role_private(self, user_id, role):
        """إرسال الدور للاعب في الخاص"""
        role_info = {
            "mafia": {"title": "المافيا", "desc": "دورك: اقتل شخص واحد كل ليلة\nارسل في الخاص: اقتل [اسم اللاعب]", "color": "#8B0000"},
            "detective": {"title": "المحقق", "desc": "دورك: افحص شخص واحد كل ليلة\nارسل في الخاص: افحص [اسم اللاعب]", "color": "#1E90FF"},
            "doctor": {"title": "الدكتور", "desc": "دورك: احمِ شخص واحد كل ليلة\nارسل في الخاص: احمي [اسم اللاعب]\nأو: احمي نفسي", "color": "#32CD32"},
            "citizen": {"title": "مواطن", "desc": "دورك: ناقش وصوت في القروب لاكتشاف المافيا", "color": "#808080"}
        }
        
        info = role_info[role]
        flex = FlexMessage(
            alt_text="دورك في اللعبة",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [
                            {"type": "text", "text": "دورك السري", "size": "md", "color": "#FFFFFF", "align": "center"},
                            {"type": "text", "text": info["title"], "weight": "bold", "size": "xxl", "color": "#FFFFFF", "align": "center", "margin": "xs"}
                        ], "backgroundColor": info["color"], "paddingAll": "20px", "cornerRadius": "10px"},
                        
                        {"type": "text", "text": info["desc"], "size": "sm", "color": COLORS['text_dark'], "wrap": True, "margin": "lg", "align": "center"},
                        
                        {"type": "separator", "margin": "md"},
                        
                        {"type": "text", "text": "لا تشارك دورك مع أي شخص", "size": "xs", "color": COLORS['warning'], "align": "center", "margin": "md", "weight": "bold"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            })
        )
        
        try:
            self.line_bot_api.push_message(user_id, flex)
            logger.info(f"تم إرسال الدور للاعب: {self.players[user_id]['name']} - {role}")
            
            # إرسال قائمة اللاعبين للأدوار الخاصة
            if role != "citizen":
                import time
                time.sleep(1)
                self.send_action_buttons(user_id, role)
        except Exception as e:
            logger.error(f"خطأ في إرسال الدور للاعب {user_id}: {e}")

    def send_action_buttons(self, user_id, role):
        """إرسال أزرار الأفعال للأدوار الخاصة"""
        alive = [p for u, p in self.players.items() if p["alive"] and u != user_id]
        action = {"mafia": "اقتل", "detective": "افحص", "doctor": "احمي"}[role]
        
        buttons = []
        
        # زر حماية النفس للدكتور
        if role == "doctor":
            buttons.append({"type": "button", "action": {"type": "message", "label": "احمي نفسي", "text": f"{action} نفسي"}, "style": "primary", "height": "sm"})
        
        # أزرار اللاعبين الأحياء
        for p in alive[:10]:
            buttons.append({"type": "button", "action": {"type": "message", "label": p['name'], "text": f"{action} {p['name']}"}, "style": "secondary", "height": "sm", "margin": "xs"})
        
        flex = FlexMessage(
            alt_text="اختر هدفك",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": f"اختر من تريد {action}ه", "size": "lg", "weight": "bold", "align": "center", "color": COLORS['text_dark']},
                        {"type": "text", "text": "اضغط على اسم اللاعب من القائمة", "size": "xs", "color": COLORS['text_light'], "align": "center", "margin": "xs", "wrap": True},
                        {"type": "box", "layout": "vertical", "contents": buttons, "margin": "lg"}
                    ],
                    "paddingAll": "20px"
                }
            })
        )
        
        try:
            self.line_bot_api.push_message(user_id, flex)
            logger.info(f"تم إرسال أزرار الأفعال للاعب: {self.players[user_id]['name']}")
        except Exception as e:
            logger.error(f"خطأ في إرسال أزرار الأفعال: {e}")

    def night_flex(self):
        """بطاقة الليل"""
        return FlexMessage(
            alt_text="الليل",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [
                            {"type": "text", "text": f"الليل - اليوم {self.day}", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}
                        ], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                        
                        {"type": "text", "text": "حل الليل على القرية", "size": "md", "color": COLORS['text_dark'], "align": "center", "margin": "lg", "weight": "bold"},
                        
                        {"type": "text", "text": "الأدوار الخاصة تستخدم قدراتها في الخاص الآن", "size": "sm", "color": COLORS['text_light'], "align": "center", "wrap": True, "margin": "xs"},
                        
                        {"type": "separator", "margin": "md"},
                        
                        {"type": "text", "text": "المواطنون العاديون ينتظرون حتى الصباح", "size": "xs", "color": COLORS['text_light'], "align": "center", "wrap": True, "margin": "md"},
                        
                        {"type": "button", "action": {"type": "message", "label": "إنهاء الليل والانتقال للصباح", "text": "إنهاء الليل"}, "style": "primary", "color": COLORS['primary'], "margin": "lg"}
                    ],
                    "paddingAll": "20px"
                }
            })
        )

    def process_night(self):
        """معالجة أحداث الليل"""
        mafia_target = self.night_actions.get("mafia_target")
        doctor_target = self.night_actions.get("doctor_target")
        
        # التحقق من القتل
        if mafia_target and mafia_target != doctor_target:
            self.players[mafia_target]["alive"] = False
            victim_name = self.players[mafia_target]['name']
            msg = f"طلع الصباح وتم اكتشاف جثة {victim_name}"
            logger.info(f"تم قتل: {victim_name}")
        else:
            msg = "طلع الصباح ولم يقتل أحد الليلة الماضية"
            if mafia_target and mafia_target == doctor_target:
                logger.info(f"الدكتور حمى: {self.players[doctor_target]['name']}")
        
        self.night_actions = {}
        self.phase = "day"
        
        # التحقق من الفائز
        winner = self.check_winner()
        if winner:
            return winner
        
        return {"response": [TextMessage(text=msg), self.day_flex()]}

    def day_flex(self):
        """بطاقة النهار"""
        alive_players = [p['name'] for p in self.players.values() if p['alive']]
        alive_text = "\n".join([f"- {name}" for name in alive_players])
        
        return FlexMessage(
            alt_text="النهار",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [
                            {"type": "text", "text": f"النهار - اليوم {self.day}", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}
                        ], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                        
                        {"type": "text", "text": "وقت المناقشة والتصويت", "size": "md", "color": COLORS['text_dark'], "align": "center", "margin": "lg", "weight": "bold"},
                        
                        {"type": "text", "text": "ناقشوا بينكم واختاروا شخص واحد للإعدام بالتصويت", "size": "sm", "color": COLORS['text_light'], "align": "center", "wrap": True, "margin": "xs"},
                        
                        {"type": "separator", "margin": "md"},
                        
                        {"type": "text", "text": f"اللاعبون الأحياء: {len(alive_players)}", "size": "sm", "color": COLORS['text_dark'], "weight": "bold", "margin": "md"},
                        {"type": "text", "text": alive_text, "size": "xs", "color": COLORS['text_light'], "wrap": True, "margin": "xs"},
                        
                        {"type": "separator", "margin": "md"},
                        
                        {"type": "button", "action": {"type": "message", "label": "فتح صندوق التصويت", "text": "تصويت مافيا"}, "style": "primary", "color": COLORS['primary'], "margin": "lg"}
                    ],
                    "paddingAll": "20px"
                }
            })
        )

    def voting_flex(self):
        """بطاقة التصويت"""
        alive = [p for p in self.players.values() if p["alive"]]
        buttons = []
        
        for p in alive[:10]:
            buttons.append({"type": "button", "action": {"type": "message", "label": p["name"], "text": f"صوت {p['name']}"}, "style": "secondary", "height": "sm", "margin": "xs"})
        
        buttons.append({"type": "button", "action": {"type": "message", "label": "إنهاء التصويت وإعلان النتيجة", "text": "إنهاء التصويت"}, "style": "primary", "color": COLORS['primary'], "margin": "md"})
        
        return FlexMessage(
            alt_text="التصويت",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "صندوق التصويت", "weight": "bold", "size": "xl", "align": "center", "color": COLORS['text_dark']},
                        {"type": "text", "text": "اختر اللاعب الذي تشك أنه المافيا", "size": "sm", "color": COLORS['text_light'], "align": "center", "wrap": True, "margin": "xs"},
                        {"type": "separator", "margin": "md"},
                        {"type": "box", "layout": "vertical", "contents": buttons, "margin": "md"}
                    ],
                    "paddingAll": "20px"
                }
            })
        )

    def vote(self, user_id, target_name):
        """تسجيل صوت اللاعب"""
        if self.phase != "voting":
            return {"response": TextMessage(text="لم يبدأ التصويت بعد")}
        
        if user_id not in self.players or not self.players[user_id]["alive"]:
            return {"response": TextMessage(text="لا يمكنك التصويت")}
        
        for uid, p in self.players.items():
            if p["name"] == target_name and p["alive"]:
                self.votes[user_id] = uid
                logger.info(f"{self.players[user_id]['name']} صوت ضد {target_name}")
                return {"response": TextMessage(text=f"تم تسجيل صوتك ضد {target_name}")}
        
        return {"response": TextMessage(text="اسم اللاعب غير صحيح")}

    def end_voting(self):
        """إنهاء التصويت وإعلان النتيجة"""
        if not self.votes:
            self.phase = "night"
            self.day += 1
            logger.info("لا توجد أصوات - الانتقال لليل")
            return {"response": [TextMessage(text="لا توجد أصوات"), self.night_flex()]}
        
        # حساب الأصوات
        vote_counts = {}
        for voted_uid in self.votes.values():
            vote_counts[voted_uid] = vote_counts.get(voted_uid, 0) + 1
        
        killed_uid = max(vote_counts, key=vote_counts.get)
        self.players[killed_uid]["alive"] = False
        killed_name = self.players[killed_uid]["name"]
        vote_count = vote_counts[killed_uid]
        
        logger.info(f"تم إعدام: {killed_name} بـ {vote_count} صوت")
        
        self.votes = {}
        self.phase = "night"
        self.day += 1
        
        # التحقق من الفائز
        winner = self.check_winner()
        if winner:
            return winner
        
        return {"response": [TextMessage(text=f"تم إعدام {killed_name} بـ {vote_count} صوت"), self.night_flex()]}

    def check_winner(self):
        """التحقق من وجود فائز"""
        mafia_count = sum(1 for p in self.players.values() if p["alive"] and p["role"] == "mafia")
        citizen_count = sum(1 for p in self.players.values() if p["alive"] and p["role"] != "mafia")
        
        if mafia_count == 0:
            self.phase = "ended"
            logger.info("فاز المواطنون")
            return {"response": self.winner_flex("المواطنون"), "game_over": True}
        
        if mafia_count >= citizen_count:
            self.phase = "ended"
            logger.info("فازت المافيا")
            return {"response": self.winner_flex("المافيا"), "game_over": True}
        
        return None

    def winner_flex(self, winner_team):
        """بطاقة إعلان الفائز"""
        roles_content = []
        for uid, p in self.players.items():
            role_name = {"mafia": "المافيا", "detective": "المحقق", "doctor": "الدكتور", "citizen": "مواطن"}[p["role"]]
            role_color = {"mafia": "#8B0000", "detective": "#1E90FF", "doctor": "#32CD32", "citizen": "#808080"}[p["role"]]
            status = "حي" if p["alive"] else "ميت"
            status_color = COLORS['success'] if p["alive"] else COLORS['text_light']
            
            roles_content.append({
                "type": "box",
                "layout": "baseline",
                "contents": [
                    {"type": "text", "text": p["name"], "size": "sm", "flex": 3, "color": COLORS['text_dark']},
                    {"type": "text", "text": role_name, "size": "sm", "color": role_color, "flex": 2, "align": "center", "weight": "bold"},
                    {"type": "text", "text": status, "size": "xs", "color": status_color, "flex": 1, "align": "end"}
                ],
                "margin": "md" if len(roles_content) > 0 else "sm"
            })
        
        return FlexMessage(
            alt_text="نتيجة اللعبة",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [
                            {"type": "text", "text": "انتهت اللعبة", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}
                        ], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                        
                        {"type": "text", "text": "الفريق الفائز", "size": "sm", "color": COLORS['text_light'], "align": "center", "margin": "lg"},
                        {"type": "text", "text": winner_team, "size": "xxl", "color": COLORS['success'], "weight": "bold", "align": "center", "margin": "xs"},
                        
                        {"type": "separator", "margin": "lg"},
                        
                        {"type": "text", "text": "كشف أدوار اللاعبين", "size": "md", "color": COLORS['text_dark'], "weight": "bold", "margin": "lg"},
                        {"type": "text", "text": "الآن يمكنكم معرفة من كان كل لاعب", "size": "xs", "color": COLORS['text_light'], "align": "center", "margin": "xs"},
                        
                        {"type": "box", "layout": "vertical", "contents": [
                            {"type": "box", "layout": "baseline", "contents": [
                                {"type": "text", "text": "الاسم", "size": "xs", "flex": 3, "color": COLORS['text_light'], "weight": "bold"},
                                {"type": "text", "text": "الدور", "size": "xs", "flex": 2, "color": COLORS['text_light'], "align": "center", "weight": "bold"},
                                {"type": "text", "text": "الحالة", "size": "xs", "flex": 1, "color": COLORS['text_light'], "align": "end", "weight": "bold"}
                            ], "margin": "md"}
                        ], "backgroundColor": f"{COLORS['border']}50", "paddingAll": "8px", "cornerRadius": "8px", "margin": "md"},
                        
                        {"type": "box", "layout": "vertical", "contents": roles_content, "margin": "xs"},
                        
                        {"type": "separator", "margin": "lg"},
                        {"type": "button", "action": {"type": "message", "label": "لعب مرة أخرى", "text": "مافيا"}, "style": "primary", "color": COLORS['primary'], "margin": "lg"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            })
        )

    def check_answer(self, text, user_id, display_name):
        """معالجة أوامر اللعبة"""
        try:
            text = text.strip()
            
            # الأوامر العامة
            if text == "انضم مافيا":
                return self.add_player(user_id, display_name)
            
            if text == "بدء مافيا":
                return self.assign_roles()
            
            if text == "شرح مافيا":
                return {"response": self.explanation_flex()}
            
            # أوامر الليل
            if text == "إنهاء الليل" and self.phase == "night":
                return self.process_night()
            
            # أوامر النهار والتصويت
            if text == "تصويت مافيا" and self.phase == "day":
                self.phase = "voting"
                logger.info("بدء التصويت")
                return {"response": self.voting_flex()}
            
            if text.startswith("صوت ") and self.phase == "voting":
                target_name = text.replace("صوت ", "").strip()
                return self.vote(user_id, target_name)
            
            if text == "إنهاء التصويت" and self.phase == "voting":
                return self.end_voting()
            
            # أوامر الأدوار الخاصة (في الخاص)
            player_role = self.players.get(user_id, {}).get("role")
            
            # المافيا - القتل
            if text.startswith("اقتل ") and player_role == "mafia" and self.phase == "night":
                target_name = text.replace("اقتل ", "").strip()
                for uid, p in self.players.items():
                    if p["name"] == target_name and p["alive"] and uid != user_id:
                        self.night_actions["mafia_target"] = uid
                        logger.info(f"المافيا اختار قتل: {target_name}")
                        return {"response": TextMessage(text=f"تم اختيار {target_name} للقتل")}
                return {"response": TextMessage(text="اسم اللاعب غير صحيح أو اللاعب ميت")}
            
            # المحقق - الفحص
            if text.startswith("افحص ") and player_role == "detective" and self.phase == "night":
                target_name = text.replace("افحص ", "").strip()
                for uid, p in self.players.items():
                    if p["name"] == target_name and p["alive"] and uid != user_id:
                        result = "هذا الشخص هو المافيا" if p["role"] == "mafia" else "هذا الشخص بريء"
                        logger.info(f"المحقق فحص: {target_name} - النتيجة: {result}")
                        return {"response": TextMessage(text=f"نتيجة الفحص:\n{target_name}: {result}")}
                return {"response": TextMessage(text="اسم اللاعب غير صحيح أو اللاعب ميت")}
            
            # الدكتور - الحماية
            if text.startswith("احمي ") and player_role == "doctor" and self.phase == "night":
                target_name = text.replace("احمي ", "").strip()
                
                if target_name == "نفسي":
                    self.night_actions["doctor_target"] = user_id
                    logger.info(f"الدكتور حمى نفسه")
                    return {"response": TextMessage(text="تم حماية نفسك من القتل")}
                
                for uid, p in self.players.items():
                    if p["name"] == target_name and p["alive"]:
                        self.night_actions["doctor_target"] = uid
                        logger.info(f"الدكتور حمى: {target_name}")
                        return {"response": TextMessage(text=f"تم حماية {target_name} من القتل")}
                
                return {"response": TextMessage(text="اسم اللاعب غير صحيح أو اللاعب ميت")}
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في معالجة أمر المافيا: {e}")
            return None
    
    def next_question(self):
        """لا يوجد next_question في لعبة المافيا"""
        return None
