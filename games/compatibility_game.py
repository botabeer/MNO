# compatibility_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import hashlib
from constants import COLORS

class CompatibilityGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.waiting_for_names = True

    def start_game(self):
        return FlexMessage(
            alt_text="نسبة التوافق",
            contents=FlexContainer.from_dict({
                "type":"bubble",
                "body":{"type":"box","layout":"vertical","contents":[
                    {"type":"box","layout":"vertical","contents":[{"type":"text","text":"نسبة التوافق","size":"xl","weight":"bold","color":COLORS['white'],"align":"center"}],"backgroundColor":COLORS['primary'],"paddingAll":"16px","cornerRadius":"12px"},
                    {"type":"box","layout":"vertical","contents":[{"type":"text","text":"اكتب اسمين بهذا الشكل:","size":"md","color":COLORS['text_dark'],"align":"center"},{"type":"text","text":"اسم و اسم","size":"xl","color":COLORS['primary'],"align":"center","weight":"bold","margin":"md"}],"margin":"lg"},
                    {"type":"separator","margin":"lg","color":COLORS['border']},
                    {"type":"box","layout":"vertical","contents":[{"type":"text","text":"أمثلة: الحوت و عبير","size":"sm","color":COLORS['text_light']}],"margin":"lg"}
                ], "backgroundColor":COLORS['card_bg'],"paddingAll":"20px"}}
            })
        )

    def parse_names(self, text):
        text = text.strip()
        if " و " in text:
            parts = text.split(" و ")
            if len(parts)>=2:
                return parts[0].strip(), " ".join(parts[1:]).strip()
        # try other splits
        text = text.replace(" و", " و ").replace("و ", " و ")
        if " و " in text:
            parts = text.split(" و ")
            if len(parts)>=2:
                return parts[0].strip(), " ".join(parts[1:]).strip()
        return None, None

    def calculate_compatibility(self, name1, name2):
        names = sorted([name1.lower().strip(), name2.lower().strip()])
        combined = "".join(names)
        hash_value = int(hashlib.sha256(combined.encode()).hexdigest(), 16)
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
        if not self.waiting_for_names:
            return None
        name1, name2 = self.parse_names(answer)
        if not name1 or not name2:
            return {'response': TextMessage(text="يرجى كتابة اسمين بالشكل الصحيح:\n\nاسم و اسم\n\nمثال: الحوت و عبير"), 'points':0, 'correct':False}
        compatibility = self.calculate_compatibility(name1, name2)
        message = self.get_compatibility_message(compatibility)
        comp_color = self.get_compatibility_color(compatibility)
        self.waiting_for_names = False
        extra_text = "علاقة رائعة ومميزة" if compatibility>=90 else ("علاقة قوية ومتينة" if compatibility>=75 else ("علاقة جيدة ومستقرة" if compatibility>=60 else "علاقة تحتاج لبعض الجهد"))
        # create result flex
        result = FlexMessage(alt_text="نتيجة التوافق", contents=FlexContainer.from_dict({
            "type":"bubble","body":{"type":"box","layout":"vertical","spacing":"md","contents":[
                {"type":"box","layout":"vertical","contents":[{"type":"text","text":"نتيجة التوافق","weight":"bold","size":"xl","color":COLORS['white'],"align":"center"}],"backgroundColor":COLORS['primary'],"paddingAll":"12px","cornerRadius":"8px"},
                {"type":"text","text":f"{name1} و {name2}","size":"lg","weight":"bold","align":"center","color":COLORS['text_dark']},
                {"type":"separator","margin":"md","color":COLORS['border']},
                {"type":"box","layout":"vertical","contents":[{"type":"text","text":f\"{compatibility}%\",\"size\":\"5xl\",\"weight\":\"bold\",\"align\":\"center\",\"color\":comp_color}, {"type":"text","text":message,"size":"md","align":"center","color":comp_color},{"type":"text","text":extra_text,"size":"sm","align":"center","color":COLORS['text_light']}],"margin":"md"},
                {"type":"separator","margin":"md","color":COLORS['border']},
                {"type":"box","layout":"horizontal","contents":[{"type":"button","action":{"type":"message","label":"إعادة","text":"توافق"},"style":"primary","color":COLORS['primary']},{"type":"button","action":{"type":"message","label":"بداية","text":"بداية"},"style":"secondary"}],"spacing":"sm","margin":"md"}
            ], "backgroundColor":COLORS['card_bg'],"paddingAll":"16px"}}
        }))
        return {'response': result, 'points':0, 'correct':False, 'game_over':True}
