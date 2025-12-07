# games/compatibility.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import hashlib
from constants import COLORS
from games.game_helpers import normalize_text
from storage import Storage

class CompatibilityGame:
    TAG = "توافق"
    def __init__(self, line_bot_api, storage: Storage):
        self.line_bot_api = line_bot_api
        self.storage = storage
        self.waiting_for_names = True

    def start_game(self):
        contents = [
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"نسبة التوافق","weight":"bold","size":"xl","color":COLORS['white'],"align":"center"}],"backgroundColor":COLORS['primary'],"paddingAll":"20px","cornerRadius":"12px"},
            {"type":"box","layout":"vertical","contents":[{"type":"text","text":"اكتب اسمين بهذا الشكل:","size":"md","color":COLORS['text_dark'],"wrap":True,"weight":"bold","align":"center"},{"type":"text","text":"اسم و اسم","size":"xl","color":COLORS['primary'],"margin":"md","weight":"bold","align":"center"}],"margin":"lg"},
        ]
        bubble = {"type":"bubble","body":{"type":"box","layout":"vertical","spacing":"md","contents":contents,"backgroundColor":COLORS['card_bg'],"paddingAll":"20px"}}
        return FlexMessage(alt_text="نسبة التوافق", contents=FlexContainer.from_dict(bubble))

    def parse_names(self, text: str):
        text = text.strip()
        if " و " in text:
            parts = text.split(" و ")
            if len(parts) >= 2:
                name1 = parts[0].strip()
                name2 = " ".join(parts[1:]).strip()
                return name1, name2
        # normalize simple variants
        text = text.replace(" و", " و ").replace("و ", " و ")
        text = " ".join(text.split())
        if " و " in text:
            parts = text.split(" و ")
            if len(parts) >= 2:
                name1 = parts[0].strip()
                name2 = " ".join(parts[1:]).strip()
                return name1, name2
        return None, None

    def calculate_compatibility(self, name1, name2):
        names = sorted([name1.lower().strip(), name2.lower().strip()])
        combined = "".join(names)
        hash_value = int(hashlib.md5(combined.encode()).hexdigest(), 16)
        compatibility = 50 + (hash_value % 51)
        return compatibility

    def get_compatibility_message(self, compatibility):
        if compatibility >= 90:
            return "توافق مثالي"
        elif compatibility >= 75:
            return "توافق ممتاز"
        elif compatibility >= 60:
            return "توافق جيد"
        else:
            return "توافق متوسط"

    def get_compatibility_color(self, compatibility):
        if compatibility >= 90:
            return "#FF1493"
        elif compatibility >= 75:
            return "#FF69B4"
        elif compatibility >= 60:
            return "#FFB6C1"
        else:
            return COLORS['text_light']

    def check_answer(self, answer, user_id, display_name):
        if not answer:
            return None
        user = self.storage.get_user(user_id)
        # For compatibility, registration not required — but we still touch activity if user exists
        if user:
            self.storage.touch_user(user_id)
        name1, name2 = self.parse_names(answer)
        if not name1 or not name2:
            return {'response': TextMessage(text="يرجى كتابة اسمين بالشكل الصحيح:\n\nاسم و اسم\n\nمثال: الحوت و عبير"), 'points':0,'correct':False}
        compatibility = self.calculate_compatibility(name1, name2)
        message = self.get_compatibility_message(compatibility)
        comp_color = self.get_compatibility_color(compatibility)
        if compatibility >= 90:
            extra_text = "علاقة رائعة ومميزة"
        elif compatibility >= 75:
            extra_text = "علاقة قوية ومتينة"
        elif compatibility >= 60:
            extra_text = "علاقة جيدة ومستقرة"
        else:
            extra_text = "علاقة تحتاج لبعض الجهد"

        # build card
        result_card = {
            "type":"bubble","body":{"type":"box","layout":"vertical","spacing":"md","contents":[
                {"type":"box","layout":"vertical","contents":[{"type":"text","text":"نتيجة التوافق","weight":"bold","size":"xl","color":COLORS['white'],"align":"center"}],"backgroundColor":COLORS['primary'],"paddingAll":"20px","cornerRadius":"12px"},
                {"type":"box","layout":"vertical","contents":[{"type":"text","text":f"{name1} و {name2}","size":"lg","color":COLORS['text_dark'],"align":"center","wrap":True,"weight":"bold"}],"margin":"lg"},
                {"type":"separator","margin":"lg","color":COLORS['border']},
                {"type":"box","layout":"vertical","contents":[
                    {"type":"box","layout":"vertical","contents":[{"type":"text","text":f"{compatibility}%","size":"5xl","color":comp_color,"weight":"bold","align":"center"}],"backgroundColor":f"{comp_color}1A","paddingAll":"20px","cornerRadius":"12px"},
                    {"type":"text","text":message,"size":"xl","color":comp_color,"weight":"bold","align":"center","margin":"lg"},
                    {"type":"text","text":extra_text,"size":"sm","color":COLORS['text_light'],"align":"center","margin":"sm"}
                ],"margin":"lg","spacing":"sm"},
                {"type":"separator","margin":"lg","color":COLORS['border']},
                {"type":"box","layout":"vertical","contents":[{"type":"text","text":"نفس النتيجة تظهر دائماً لنفس الأسماء","size":"xs","color":COLORS['text_light'],"align":"center","wrap":True}],"margin":"md"},
                {"type":"box","layout":"horizontal","contents":[{"type":"button","action":{"type":"message","label":"إعادة","text":"توافق"},"style":"primary","color":COLORS['primary'],"height":"sm","flex":1},{"type":"button","action":{"type":"message","label":"بداية","text":"بداية"},"style":"secondary","height":"sm","flex":1}],"spacing":"sm","margin":"lg"}
            ], "backgroundColor": COLORS['card_bg'], "paddingAll":"20px"}}
        return {'response': FlexMessage(alt_text="نتيجة التوافق", contents=FlexContainer.from_dict(result_card)), 'points':0,'correct':False,'won':False,'game_over':True}
