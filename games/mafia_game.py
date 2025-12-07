# mafia_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import MAFIA_CONFIG, COLORS

class MafiaGame:
    """
    لعبة المافيا: تصميم مبسط للربط مع LINE بوت.
    - التسجيل عبر "انضم مافيا"
    - بدء عبر "بدء مافيا" (يتطلب على الأقل MAFIA_CONFIG['min_players'])
    - الأدوار تُرسل في الخاص لكل لاعب
    - الأوامر في الخاص: "اقتل <الاسم>" للمغتال، "افحص <الاسم>" للمحقق، "احمي <الاسم>|نفسي" للدكتور
    - النهار: "تصويت مافيا" ثم "صوت <الاسم>" ثم "إنهاء التصويت"
    """
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.players = {}  # uid -> {name, role, alive}
        self.phase = "registration"
        self.day = 0
        self.votes = {}
        self.night_actions = {}
        self.group_id = None

    # ... registration, flex builders كما في نسخةك القديمة ...
    # سأستخدم نسخة مصقولة من الكود الذي أعطيتني إياه مع تنظيف الأخطاء:
    def registration_flex(self):
        from games.game_helpers import create_separator
        return FlexMessage(alt_text="لعبة المافيا - التسجيل", contents=FlexContainer.from_dict({
            "type":"bubble","body":{"type":"box","layout":"vertical","contents":[
                {"type":"box","layout":"vertical","contents":[{"type":"text","text":"بوت الحوت","weight":"bold","size":"lg","color":COLORS['white']},{"type":"text","text":"لعبة المافيا","size":"md","color":COLORS['white']}], "backgroundColor":COLORS['primary'],"paddingAll":"16px","cornerRadius":"8px"},
                {"type":"text","text":"انضم للعبة","size":"lg","color":COLORS['text_dark'],"weight":"bold","margin":"lg"},
                {"type":"text","text":f"اللاعبين المسجلين: {len(self.players)}","size":"sm","color":COLORS['text_light']},
                {"type":"separator","margin":"lg","color":COLORS['border']},
                {"type":"box","layout":"vertical","contents":[
                    {"type":"button","action":{"type":"message","label":"انضم","text":"انضم مافيا"},"style":"primary","color":COLORS['primary']},
                    {"type":"button","action":{"type":"message","label":"بدء اللعبة","text":"بدء مافيا"},"style":"secondary","margin":"sm"},
                    {"type":"button","action":{"type":"message","label":"شرح اللعبة","text":"شرح مافيا"},"style":"secondary","margin":"sm"}
                ],"margin":"lg"}
            ], "backgroundColor":COLORS['card_bg'],"paddingAll":"16px"}}
        ))

    def explanation_flex(self):
        return FlexMessage(alt_text="شرح لعبة المافيا", contents=FlexContainer.from_dict({
            "type":"bubble","body":{"type":"box","layout":"vertical","contents":[
                {"type":"box","layout":"vertical","contents":[{"type":"text","text":"شرح المافيا","weight":"bold","size":"lg","color":COLORS['white']}],"backgroundColor":COLORS['primary'],"paddingAll":"12px","cornerRadius":"8px"},
                {"type":"text","text":"الخطوات للمبتدئ:","size":"md","color":COLORS['text_dark']},
                {"type":"text","text":"1) اضغط انضم (بالمجموعة)\n2) من يملك صلاحية يبدأ اللعبة عبر 'بدء مافيا'\n3) تفحص الخاص لمعرفة دورك\n4) بالليل: ادخل أمر دورك في الخاص (مثال: 'اقتل اسم')\n5) بالنهار: ناقش وصوّت عبر 'تصويت مافيا' ثم 'صوت اسم' ثم 'إنهاء التصويت'","size":"sm","color":COLORS['text_light'],"wrap":True,"margin":"md"}
            ], "backgroundColor":COLORS['card_bg'],"paddingAll":"16px"}}
        ))

    def add_player(self, user_id, name):
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
            self.send_role_private(uid, role)
        self.phase = "night"
        self.day = 1
        return {"response": [TextMessage(text="تم توزيع الأدوار في الخاص لكل لاعب"), self.night_flex()]}

    def send_role_private(self, user_id, role):
        role_info = {
            "mafia": {"title":"أنت المافيا","desc":"دورك: قتل شخص كل ليلة","color":"#8B0000"},
            "detective": {"title":"أنت المحقق","desc":"دورك: فحص شخص كل ليلة","color":"#1E90FF"},
            "doctor": {"title":"أنت الدكتور","desc":"دورك: حماية شخص كل ليلة","color":"#32CD32"},
            "citizen": {"title":"أنت مواطن","desc":"دورك: التصويت بالنهار","color":"#808080"}
        }
        info = role_info[role]
        contents = [
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"دورك السري","size":"lg","color":"#FFFFFF","align":"center"}],"backgroundColor":info['color'],"paddingAll":"12px","cornerRadius":"8px"},
            {"type":"text","text":info['title'],"size":"xl","weight":"bold","align":"center","margin":"lg"},
            {"type":"text","text":info['desc'],"size":"sm","color":COLORS['text_light'],"margin":"md"}
        ]
        flex = FlexMessage(alt_text="دورك في المافيا", contents=FlexContainer.from_dict({"type":"bubble","body":{"type":"box","layout":"vertical","contents":contents,"backgroundColor":COLORS['card_bg'],"paddingAll":"16px"}}))
        try:
            self.line_bot_api.push_message(user_id, flex)
        except Exception as e:
            print("خطأ عند إرسال الدور:", e)

    def night_flex(self):
        alive_players = [p for p in self.players.values() if p["alive"]]
        return FlexMessage(alt_text="مرحلة الليل", contents=FlexContainer.from_dict({
            "type":"bubble","body":{"type":"box","layout":"vertical","contents":[
                {"type":"text","text":f"اليوم {self.day} - الليل","size":"md","color":COLORS['white'],"align":"center","backgroundColor":COLORS['primary'],"paddingAll":"12px","cornerRadius":"8px"},
                {"type":"text","text":"تحقق من رسائلك الخاصة لاستخدام دورك الليلي","size":"sm","color":COLORS['text_light'],"align":"center","margin":"md"}
            ], "backgroundColor":COLORS['card_bg'],"paddingAll":"16px"}}
        ))

    def process_night(self):
        msgs = []
        mafia_target = self.night_actions.get("mafia_target")
        doctor_target = self.night_actions.get("doctor_target")
        if mafia_target:
            if mafia_target == doctor_target:
                msgs.append("طلع النهار... لم يُقتل أحد الليلة!")
            else:
                self.players[mafia_target]["alive"] = False
                msgs.append(f"طلع النهار... تم قتل {self.players[mafia_target]['name']}")
        else:
            msgs.append("طلع النهار... لم يُقتل أحد الليلة!")
        self.night_actions = {}
        self.phase = "day"
        winner = self.check_winner()
        if winner:
            return winner
        return {"response": [TextMessage(text=m) for m in msgs] + [self.day_flex()]}

    def day_flex(self):
        alive = [p for p in self.players.values() if p["alive"]]
        return FlexMessage(alt_text="مرحلة النهار", contents=FlexContainer.from_dict({
            "type":"bubble","body":{"type":"box","layout":"vertical","contents":[
                {"type":"text","text":f"اليوم {self.day} - النهار","size":"md","color":COLORS['white'],"align":"center","backgroundColor":COLORS['primary'],"paddingAll":"12px","cornerRadius":"8px"},
                {"type":"text","text":"ناقش ثم صوت لاعدام المشكوك به","size":"sm","color":COLORS['text_light'],"align":"center","margin":"md"}
            ], "backgroundColor":COLORS['card_bg'],"paddingAll":"16px"}}
        ))

    def vote(self, user_id, target_name):
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
            return {"response":[TextMessage(text="لم يتم التصويت. الانتقال لليل"), self.night_flex()]}
        counts = {}
        for uid in self.votes.values():
            counts[uid] = counts.get(uid,0) + 1
        killed = max(counts, key=counts.get)
        self.players[killed]['alive'] = False
        killed_name = self.players[killed]['name']
        self.votes = {}
        self.phase = "night"
        self.day += 1
        winner = self.check_winner()
        if winner:
            return winner
        return {"response":[TextMessage(text=f"تم التصويت على {killed_name} وإعدامه"), self.night_flex()]}

    def check_winner(self):
        mafia_count = sum(1 for p in self.players.values() if p['alive'] and p['role']=='mafia')
        citizens_count = sum(1 for p in self.players.values() if p['alive'] and p['role']!='mafia')
        if mafia_count == 0:
            self.phase = 'ended'
            return {"response": self.winner_flex("المواطنون"), "game_over": True}
        if mafia_count >= citizens_count:
            self.phase = 'ended'
            return {"response": self.winner_flex("المافيا"), "game_over": True}
        return None

    def winner_flex(self, winner_team):
        return FlexMessage(alt_text="انتهت اللعبة", contents=FlexContainer.from_dict({
            "type":"bubble","body":{"type":"box","layout":"vertical","contents":[
                {"type":"text","text":"انتهت اللعبة","size":"lg","weight":"bold","color":COLORS['white'],"align":"center","backgroundColor":COLORS['primary'],"paddingAll":"12px","cornerRadius":"8px"},
                {"type":"text","text":"الفائز","size":"sm","color":COLORS['text_light']},
                {"type":"text","text":winner_team,"size":"xl","color":COLORS['primary'],"weight":"bold","align":"center"}
            ], "backgroundColor":COLORS['card_bg'],"paddingAll":"16px"}}
        ))

    def check_answer(self, text, user_id, display_name):
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
            return {"response": TextMessage(text=f"اليوم: {self.day}\nالمرحلة: {self.phase}\nالحيون: {', '.join(alive)}\nالموتى: {', '.join(dead)}")}
        if text == "إنهاء الليل":
            if self.phase == "night":
                return self.process_night()
            return {"response": TextMessage(text="ليس وقت الليل الآن")}
        if text == "تصويت مافيا":
            if self.phase in ["day","voting"]:
                self.phase = "voting"
                return {"response": self.day_flex()}
            return {"response": TextMessage(text="ليس وقت التصويت الآن")}
        if text.startswith("صوت "):
            return self.vote(user_id, text.replace("صوت ","").strip())
        if text == "إنهاء التصويت":
            if self.phase == "voting":
                return self.end_voting()
            return {"response": TextMessage(text="ليس وقت التصويت")}
        if text.startswith("اقتل "):
            if user_id not in self.players or self.players[user_id]['role'] != 'mafia':
                return {"response": TextMessage(text="أنت لست المافيا")}
            if self.phase != "night":
                return {"response": TextMessage(text="ليس وقت الليل")}
            target_name = text.replace("اقتل ","").strip()
            for uid,p in self.players.items():
                if p['name']==target_name and p['alive'] and uid!=user_id:
                    self.night_actions['mafia_target'] = uid
                    return {"response": TextMessage(text=f"تم اختيار {target_name} كضحية")}
            return {"response": TextMessage(text="لا يوجد لاعب بهذا الاسم")}
        if text.startswith("افحص "):
            if user_id not in self.players or self.players[user_id]['role'] != 'detective':
                return {"response": TextMessage(text="أنت لست المحقق")}
            if self.phase != "night":
                return {"response": TextMessage(text="ليس وقت الليل")}
            target_name = text.replace("افحص ","").strip()
            for uid,p in self.players.items():
                if p['name']==target_name and p['alive'] and uid!=user_id:
                    role = p['role']
                    return {"response": TextMessage(text=f"نتيجة الفحص: {'مافيا' if role=='mafia' else 'بريء'}")}
            return {"response": TextMessage(text="لا يوجد لاعب بهذا الاسم")}
        if text.startswith("احمي "):
            if user_id not in self.players or self.players[user_id]['role'] != 'doctor':
                return {"response": TextMessage(text="أنت لست الدكتور")}
            if self.phase != "night":
                return {"response": TextMessage(text="ليس وقت الليل")}
            target_text = text.replace("احمي ","").strip()
            if target_text == "نفسي":
                self.night_actions['doctor_target'] = user_id
                return {"response": TextMessage(text="تم حمايتك الليلة")}
            for uid,p in self.players.items():
                if p['name']==target_text and p['alive']:
                    self.night_actions['doctor_target'] = uid
                    return {"response": TextMessage(text": f"تم حماية {target_text} الليلة")}
            return {"response": TextMessage(text="لا يوجد لاعب بهذا الاسم")}
        return None
