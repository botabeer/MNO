# games/mafia_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import MAFIA_CONFIG, COLORS
from storage import Storage

class MafiaGame:
    TAG = "مافيا"
    def __init__(self, line_bot_api, storage: Storage):
        self.line_bot_api = line_bot_api
        self.storage = storage
        self.reset_game()

    def reset_game(self):
        self.players = {}  # uid -> {"name":..., "role":..., "alive":True}
        self.phase = "registration"
        self.day = 0
        self.votes = {}
        self.night_actions = {}
        self.registered_order = []

    def start_game(self):
        self.reset_game()
        self.phase = "registration"
        return self.registration_flex()

    def registration_flex(self):
        return FlexMessage(
            alt_text="لعبة المافيا - التسجيل",
            contents=FlexContainer.from_dict({
                "type":"bubble","body":{"type":"box","layout":"vertical","contents":[
                    {"type":"box","layout":"vertical","contents":[{"type":"text","text":"بوت الحوت","weight":"bold","size":"lg","color":COLORS['white'],"align":"center"},{"type":"text","text":"لعبة المافيا","size":"md","color":COLORS['white'],"align":"center","margin":"xs"}],"backgroundColor":COLORS['primary'],"paddingAll":"20px","cornerRadius":"10px"},
                    {"type":"box","layout":"vertical","contents":[{"type":"text","text":"مهم: أضف البوت كصديق لاستلام دورك السري","size":"xs","color":COLORS['warning'],"weight":"bold","wrap":True,"align":"center"}],"backgroundColor":f"{COLORS['warning']}1A","paddingAll":"10px","cornerRadius":"8px","margin":"lg"},
                    {"type":"box","layout":"vertical","contents":[{"type":"text","text":"انضم للعبة","size":"lg","color":COLORS['text_dark'],"weight":"bold"},{"type":"text","text":f"اللاعبين المسجلين: {len(self.players)}","size":"md","color":COLORS['text_light'],"margin":"md"},{"type":"text","text":f"الحد الأدنى: {MAFIA_CONFIG['min_players']} لاعبين","size":"sm","color":COLORS['text_light'],"margin":"xs"}],"margin":"lg"},
                    {"type":"separator","margin":"lg","color":COLORS['border']},
                    {"type":"box","layout":"vertical","contents":[
                        {"type":"button","action":{"type":"message","label":"انضم","text":"انضم مافيا"},"style":"primary","color":COLORS['primary'],"height":"sm"},
                        {"type":"button","action":{"type":"message","label":"بدء اللعبة","text":"بدء مافيا"},"style":"secondary","height":"sm","margin":"sm"},
                        {"type":"button","action":{"type":"message","label":"شرح اللعبة","text":"شرح مافيا"},"style":"secondary","height":"sm","margin":"sm"}
                    ], "margin":"lg"}
                ], "backgroundColor":COLORS['card_bg'],"paddingAll":"20px"}}
            })
        )

    def explanation_flex(self):
        # شرح خطوة بخطوة للمبتدئين (ماذا يفعل في الخاص و ماذا في القروب)
        contents = [
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"بوت الحوت","weight":"bold","size":"lg","color":COLORS['white'],"align":"center"},{"type":"text","text":"شرح لعبة المافيا","size":"md","color":COLORS['white'],"align":"center","margin":"xs"}],"backgroundColor":COLORS['primary'],"paddingAll":"20px","cornerRadius":"10px"},
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"المبتدئ: ماذا تفعل؟","size":"lg","color":COLORS['text_dark'],"weight":"bold"},{"type":"text","text":"1) اضغط انضم ليتم تسجيلك.\n2) عندما يبدأ المشرف اللعبة، سترسل لك رسالة خاصة بدورك — لا تفصح عنه.\n3) إذا كنت تملك دور بالليل (مافيا/محقق/دكتور) ستتلقى رسالة خاصة بأزرار للاختيار.\n4) في النهار ناقش بالقروب وصوت باستخدام زر التصويت.","size":"sm","color":COLORS['text_light'],"margin":"md","wrap":True}],"margin":"lg"},
            {"type":"separator","margin":"lg","color":COLORS['border']},
            {"type":"button","action":{"type":"message","label":"ابدأ اللعب","text":"مافيا"},"style":"primary","color":COLORS['primary'],"height":"sm","margin":"lg"}
        ]
        bubble = {"type":"bubble","body":{"type":"box","layout":"vertical","spacing":"md","contents":contents,"backgroundColor":COLORS['card_bg'],"paddingAll":"20px"}}
        return FlexMessage(alt_text="شرح لعبة المافيا", contents=FlexContainer.from_dict(bubble))

    def add_player(self, user_id: str, name: str):
        if self.phase != "registration":
            return {"response": TextMessage(text="اللعبة بدأت بالفعل")}
        if user_id in self.players:
            return {"response": TextMessage(text="أنت مسجل بالفعل")}
        self.players[user_id] = {"name": name, "role": None, "alive": True}
        self.registered_order.append(user_id)
        # سجّل المستخدم في التخزين كبقيّة الألعاب
        self.storage.register_user(user_id, name)
        self.storage.register_user_for_game(user_id, self.TAG)
        return {"response": self.registration_flex()}

    def assign_roles(self):
        if len(self.players) < MAFIA_CONFIG["min_players"]:
            return {"response": TextMessage(text=f"عدد اللاعبين غير كافٍ. الحد الأدنى {MAFIA_CONFIG['min_players']} لاعبين")}
        # بناء قائمة أدوار
        roles = []
        for r,count in MAFIA_CONFIG['role_counts'].items():
            roles += [r]*count
        remaining = len(self.players) - len(roles)
        roles += ["citizen"] * remaining
        random.shuffle(roles)
        for uid, role in zip(list(self.players.keys()), roles):
            self.players[uid]["role"] = role
            self.send_role_private(uid, role)
        self.phase = "night"
        self.day = 1
        return {"response": [TextMessage(text="تم توزيع الأدوار في الخاص لكل لاعب"), self.night_flex()]}

    def send_role_private(self, user_id: str, role: str):
        role_info = {
            "mafia": {"title":"أنت المافيا","desc":"دورك: اختر ضحية بالخاص ليتم قتلها خلال الليل","color":"#8B0000"},
            "detective": {"title":"أنت المحقق","desc":"دورك: فحص لاعب لتعرف إن كان مافيا بالخاص","color":"#1E90FF"},
            "doctor": {"title":"أنت الدكتور","desc":"دورك: حماية لاعب من القتل خلال الليل","color":"#32CD32"},
            "citizen": {"title":"أنت مواطن","desc":"لا دور ليلي — شارك بنقاش النهار وصوّت","color":"#808080"}
        }
        info = role_info[role]
        contents = [
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"بوت الحوت","weight":"bold","size":"lg","color":"#FFFFFF","align":"center"},{"type":"text","text":"دورك السري","size":"md","color":"#FFFFFF","align":"center","margin":"xs"}],"backgroundColor":info['color'],"paddingAll":"20px","cornerRadius":"10px"},
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":info['title'],"size":"xxl","color":COLORS['text_dark'],"weight":"bold","align":"center"}],"margin":"lg"},
            {"type":"separator","margin":"lg","color":COLORS['border']},
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"دورك","size":"md","color":COLORS['text_dark'],"weight":"bold"},{"type":"text","text":info['desc'],"size":"sm","color":COLORS['text_light'],"margin":"md","wrap":True}],"margin":"lg"}
        ]
        if role != "citizen":
            contents.append({"type":"separator","margin":"lg","color":COLORS['border']})
            contents.append({"type":"box","layout":"vertical","contents":[{"type":"text","text":"انتظر نافذة الليل...","size":"sm","color":COLORS['primary'],"align":"center","weight":"bold"}],"margin":"md"})
        contents.append({"type":"separator","margin":"lg","color":COLORS['border']})
        contents.append({"type":"box","layout":"vertical","contents":[{"type":"text","text":"لا تشارك دورك مع أحد!","size":"xs","color":COLORS['text_light'],"align":"center","wrap":True}],"margin":"md"})
        flex = FlexMessage(alt_text="دورك في لعبة المافيا", contents=FlexContainer.from_dict({"type":"bubble","body":{"type":"box","layout":"vertical","contents":contents,"backgroundColor":COLORS['card_bg'],"paddingAll":"20px"}}))
        try:
            self.line_bot_api.push_message(user_id, flex)
        except Exception as e:
            print(f"Error sending role to {user_id}: {e}")

    def send_action_buttons_private(self, user_id: str, role: str):
        # إرسال أزرار خاصة لاختيار الضحية/الفحص/الحماية
        alive_others = [p for uid,p in self.players.items() if p["alive"] and uid != user_id]
        if not alive_others:
            # لا أحد للحركة
            try:
                self.line_bot_api.push_message(user_id, TextMessage(text="لا يوجد لاعبين متاحين للحركة."))
            except Exception:
                pass
            return
        # بناء أزرار بسيطة: كل زر يرسل رسالة نصية بالأمر المطلوب
        buttons = []
        if role == "doctor":
            buttons.append({"type":"button","action":{"type":"message","label":"احمي نفسي","text":"احمي نفسي"},"style":"primary","height":"sm"})
        for p in alive_others[:12]:
            if role == "mafia":
                label = p['name']; text = f"اقتل {p['name']}"
            elif role == "detective":
                label = p['name']; text = f"افحص {p['name']}"
            elif role == "doctor":
                label = p['name']; text = f"احمي {p['name']}"
            else:
                label = p['name']; text = p['name']
            buttons.append({"type":"button","action":{"type":"message","label":label,"text":text},"style":"secondary","height":"sm"})
        bubble = {"type":"bubble","body":{"type":"box","layout":"vertical","contents":[
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"اختر هدفك","weight":"bold","size":"lg","color":"#FFFFFF","align":"center"}],"backgroundColor":COLORS['primary'],"paddingAll":"16px","cornerRadius":"8px"},
            {"type":"box","layout":"vertical","contents":buttons,"margin":"lg"}
        ], "backgroundColor":COLORS['card_bg']}}
        try:
            self.line_bot_api.push_message(user_id, FlexMessage(alt_text="اختر هدفك", contents=FlexContainer.from_dict(bubble)))
        except Exception as e:
            print(f"Error pushing action buttons to {user_id}: {e}")

    def night_flex(self):
        alive_players = [p for p in self.players.values() if p["alive"]]
        bubble = {"type":"bubble","body":{"type":"box","layout":"vertical","contents":[
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"بوت الحوت","weight":"bold","size":"lg","color":COLORS['white'],"align":"center"},{"type":"text","text":f"اليوم {self.day} - الليل","size":"md","color":COLORS['white'],"align":"center","margin":"xs"}],"backgroundColor":COLORS['primary'],"paddingAll":"20px","cornerRadius":"10px"},
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"الليل حل — افحص رسائلك الخاصة لاستخدام دورك.","size":"sm","color":COLORS['text_light'],"margin":"md","align":"center"}],"margin":"lg"},
            {"type":"separator","margin":"lg","color":COLORS['border']},
            {"type":"box","layout":"vertical","contents":[{"type":"button","action":{"type":"message","label":"حالة اللعبة","text":"حالة مافيا"},"style":"secondary","height":"sm"},{"type":"button","action":{"type":"message","label":"إنهاء الليل","text":"إنهاء الليل"},"style":"primary","color":COLORS['primary'],"height":"sm","margin":"sm"}],"margin":"lg"}
        ], "backgroundColor":COLORS['card_bg'],"paddingAll":"20px"}}
        return FlexMessage(alt_text="مرحلة الليل", contents=FlexContainer.from_dict(bubble))

    def process_night(self):
        messages = []
        mafia_target = self.night_actions.get("mafia_target")
        doctor_target = self.night_actions.get("doctor_target")
        if mafia_target:
            if mafia_target == doctor_target:
                messages.append("طلع النهار... لم يُقتل أحد الليلة!")
            else:
                self.players[mafia_target]["alive"] = False
                victim_name = self.players[mafia_target]["name"]
                messages.append(f"طلع النهار... تم قتل {victim_name}")
        else:
            messages.append("طلع النهار... لم يُقتل أحد الليلة!")
        self.night_actions = {}
        self.phase = "day"
        winner_check = self.check_winner()
        if winner_check:
            return winner_check
        return {"response": [TextMessage(text=msg) for msg in messages] + [self.day_flex()]}

    def day_flex(self):
        alive_players = [p for p in self.players.values() if p["alive"]]
        bubble = {"type":"bubble","body":{"type":"box","layout":"vertical","contents":[
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"بوت الحوت","weight":"bold","size":"lg","color":COLORS['white'],"align":"center"},{"type":"text","text":f"اليوم {self.day} - مرحلة النهار","size":"md","color":COLORS['white'],"align":"center","margin":"xs"}],"backgroundColor":COLORS['primary'],"paddingAll":"20px","cornerRadius":"10px"},
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"مناقشة ثم التصويت","size":"lg","color":COLORS['text_dark'],"weight":"bold","align":"center"},{"type":"text","text":f"اللاعبون الأحياء: {len(alive_players)}","size":"sm","color":COLORS['text_light'],"margin":"md","align":"center"}],"margin":"lg"},
            {"type":"separator","margin":"lg","color":COLORS['border']},
            {"type":"box","layout":"vertical","contents":[{"type":"button","action":{"type":"message","label":"تصويت","text":"تصويت مافيا"},"style":"primary","color":COLORS['primary'],"height":"sm"},{"type":"button","action":{"type":"message","label":"حالة اللعبة","text":"حالة مافيا"},"style":"secondary","height":"sm","margin":"sm"}],"margin":"lg"}
        ], "backgroundColor":COLORS['card_bg'],"paddingAll":"20px"}}
        return FlexMessage(alt_text="مرحلة النهار", contents=FlexContainer.from_dict(bubble))

    def status_flex(self):
        alive = [p for p in self.players.values() if p["alive"]]
        dead = [p for p in self.players.values() if not p["alive"]]
        alive_text = "\n".join([f"نشط {p['name']}" for p in alive]) if alive else "لا يوجد"
        dead_text = "\n".join([f"متوفي {p['name']}" for p in dead]) if dead else "لا يوجد"
        phase_text = {"registration":"التسجيل","night":"الليل","day":"النهار","voting":"التصويت","ended":"انتهت"}
        bubble = {"type":"bubble","body":{"type":"box","layout":"vertical","contents":[
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"بوت الحوت","weight":"bold","size":"lg","color":COLORS['white'],"align":"center"},{"type":"text","text":"حالة لعبة المافيا","size":"md","color":COLORS['white'],"align":"center","margin":"xs"}],"backgroundColor":COLORS['primary'],"paddingAll":"20px","cornerRadius":"10px"},
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":f"اليوم: {self.day}","size":"md","color":COLORS['text_dark'],"weight":"bold"},{"type":"text","text":f"المرحلة: {phase_text.get(self.phase,self.phase)}","size":"sm","color":COLORS['text_light'],"margin":"xs"}],"margin":"lg"},
            {"type":"separator","margin":"lg","color":COLORS['border']},
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"اللاعبون الأحياء","size":"md","color":COLORS['text_dark'],"weight":"bold"},{"type":"text","text":alive_text,"size":"sm","color":COLORS['text_light'],"margin":"md","wrap":True}],"margin":"lg"},
            {"type":"separator","margin":"lg","color":COLORS['border']},
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"اللاعبون المقتولون","size":"md","color":COLORS['text_dark'],"weight":"bold"},{"type":"text","text":dead_text,"size":"sm","color":COLORS['text_light'],"margin":"md","wrap":True}],"margin":"lg"}
        ], "backgroundColor":COLORS['card_bg'],"paddingAll":"20px"}}
        return FlexMessage(alt_text="حالة لعبة المافيا", contents=FlexContainer.from_dict(bubble))

    def voting_flex(self):
        alive = [p for p in self.players.values() if p["alive"]]
        buttons = []
        for p in alive[:10]:
            buttons.append({"type":"button","action":{"type":"message","label":p['name'],"text":f"صوت {p['name']}"},"style":"secondary","height":"sm"})
        buttons.append({"type":"separator","margin":"md"})
        buttons.append({"type":"button","action":{"type":"message","label":"إنهاء التصويت","text":"إنهاء التصويت"},"style":"primary","color":COLORS['primary'],"height":"sm","margin":"md"})
        bubble = {"type":"bubble","body":{"type":"box","layout":"vertical","contents":[
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"بوت الحوت","weight":"bold","size":"lg","color":COLORS['white'],"align":"center"},{"type":"text","text":"التصويت","size":"md","color":COLORS['white'],"align":"center","margin":"xs"}],"backgroundColor":COLORS['primary'],"paddingAll":"20px","cornerRadius":"10px"},
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"اضغط على اسم من تظنه المافيا","size":"md","color":COLORS['text_dark'],"weight":"bold","align":"center","wrap":True}],"margin":"lg"},
            {"type":"separator","margin":"lg","color":COLORS['border']},
            {"type":"box","layout":"vertical","contents":buttons,"margin":"lg"}
        ], "backgroundColor":COLORS['card_bg'],"paddingAll":"20px"}}
        return FlexMessage(alt_text="التصويت", contents=FlexContainer.from_dict(bubble))

    def vote(self, user_id, target_name):
        if self.phase != "voting":
            return {"response": TextMessage(text="ليس وقت التصويت")}
        if user_id not in self.players or not self.players[user_id]["alive"]:
            return {"response": TextMessage(text="لا يمكنك التصويت")}
        for uid, p in self.players.items():
            if p["name"] == target_name and p["alive"]:
                self.votes[user_id] = uid
                self.storage.touch_user(user_id)
                return {"response": TextMessage(text=f"تم تصويتك لـ {target_name}")}
        return {"response": TextMessage(text="لا يوجد لاعب بهذا الاسم")}

    def end_voting(self):
        if not self.votes:
            self.phase = "night"
            self.day += 1
            return {"response": [TextMessage(text="لم يتم التصويت. الانتقال لليل"), self.night_flex()]}
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
        return {"response": [TextMessage(text=f"تم التصويت على {killed_name} وإعدامه"), self.night_flex()]}

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
        bubble = {"type":"bubble","body":{"type":"box","layout":"vertical","contents":[
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"بوت الحوت","weight":"bold","size":"lg","color":COLORS['white'],"align":"center"},{"type":"text","text":"انتهت اللعبة","size":"md","color":COLORS['white'],"align":"center","margin":"xs"}],"backgroundColor":COLORS['primary'],"paddingAll":"20px","cornerRadius":"10px"},
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"الفائز","size":"sm","color":COLORS['text_light'],"align":"center"},{"type":"text","text":winner_team,"size":"xxl","color":COLORS['primary'],"weight":"bold","align":"center","margin":"md"}],"margin":"lg"},
            {"type":"separator","margin":"lg","color":COLORS['border']},
            {"type":"button","action":{"type":"message","label":"إعادة","text":"مافيا"},"style":"primary","color":COLORS['primary'],"height":"sm","margin":"lg"}
        ], "backgroundColor":COLORS['card_bg'],"paddingAll":"20px"}}
        return FlexMessage(alt_text="نهاية لعبة المافيا", contents=FlexContainer.from_dict(bubble))

    def check_answer(self, text, user_id, display_name):
        text = text.strip()
        # واجهة أوامر مختصرة — تعامل مع رسائل خاصة وأوامر القروب
        if text == "انضم مافيا":
            return self.add_player(user_id, display_name)
        if text == "بدء مافيا":
            return self.assign_roles()
        if text == "شرح مافيا":
            return {"response": self.explanation_flex()}
        if text == "حالة مافيا":
            return {"response": self.status_flex()}
        if text == "إنهاء الليل":
            if self.phase == "night":
                return self.process_night()
            return {"response": TextMessage(text="ليس وقت الليل الآن")}
        if text == "تصويت مافيا":
            if self.phase in ["day", "voting"]:
                self.phase = "voting"
                return {"response": self.voting_flex()}
            return {"response": TextMessage(text="ليس وقت التصويت الآن")}
        if text.startswith("صوت "):
            target_name = text.replace("صوت ", "").strip()
            return self.vote(user_id, target_name)
        if text == "إنهاء التصويت":
            if self.phase == "voting":
                return self.end_voting()
            return {"response": TextMessage(text="ليس وقت التصويت")}
        if text.startswith("اقتل "):
            if user_id not in self.players or self.players[user_id]["role"] != "mafia":
                return {"response": TextMessage(text="أنت لست المافيا")}
            if self.phase != "night":
                return {"response": TextMessage(text="ليس وقت الليل")}
            target_name = text.replace("اقتل ", "").strip()
            for uid,p in self.players.items():
                if p["name"] == target_name and p["alive"] and uid != user_id:
                    self.night_actions["mafia_target"] = uid
                    return {"response": TextMessage(text=f"تم اختيار {target_name} كضحية (سيتم تنفيذ القرار عند إنهاء الليل)")}
            return {"response": TextMessage(text="لا يوجد لاعب بهذا الاسم")}
        if text.startswith("افحص "):
            if user_id not in self.players or self.players[user_id]["role"] != "detective":
                return {"response": TextMessage(text="أنت لست المحقق")}
            if self.phase != "night":
                return {"response": TextMessage(text="ليس وقت الليل")}
            target_name = text.replace("افحص ", "").strip()
            for uid,p in self.players.items():
                if p["name"] == target_name and p["alive"] and uid != user_id:
                    role = p["role"]
                    if role == "mafia":
                        return {"response": TextMessage(text=f"النتيجة: {target_name} هو مافيا")}
                    else:
                        return {"response": TextMessage(text=f"النتيجة: {target_name} بريء")}
            return {"response": TextMessage(text="لا يوجد لاعب بهذا الاسم")}
        if text.startswith("احمي "):
            if user_id not in self.players or self.players[user_id]["role"] != "doctor":
                return {"response": TextMessage(text="أنت لست الدكتور")}
            if self.phase != "night":
                return {"response": TextMessage(text="ليس وقت الليل")}
            target_text = text.replace("احمي ","").strip()
            if target_text == "نفسي" or target_text == "نفسي":
                self.night_actions["doctor_target"] = user_id
                return {"response": TextMessage(text="تم اختيار حماية نفسك الليلة")}
            for uid,p in self.players.items():
                if p["name"] == target_text and p["alive"]:
                    self.night_actions["doctor_target"] = uid
                    return {"response": TextMessage(text=f"تم اختيار حماية {target_text} الليلة")}
            return {"response": TextMessage(text="لا يوجد لاعب بهذا الاسم")}
        return None
