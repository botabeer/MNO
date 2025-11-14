from linebot.models import TextSendMessage
import random
import re
from itertools import permutations

# مثال قاموس عربي صغير (يمكن توسيعه بآلاف الكلمات)
ARABIC_DICTIONARY = [
    "قلم","برق","مرو","قلب","لعب","عرب","عمل","قمل",
    "كتاب","تلب","بكر","كلم","ملك","تلك","لبك",
    "مدرس","درس","سهل","مدر","درسه","رمد","هلم",
    "شجر","فجر","قهر","جرش","شرف","قش",
    "حديق","حديقه","دقيق","حقل","قلد","قديح",
    "بيت","كرم","كريم","ترك","تبي","ريم","كب",
    "نور","سمر","سور","نار","مرس","مان",
    "فجر","جرح","حرب","حفل","فلج","برج",
    "سلام","سلم","سما","لوم","ماس","سوم","لام","منل",
    "عصفور","عصف","صفر","فرع","صوري","رعص","فور","وري",
    # يمكن إضافة المزيد من الكلمات العربية هنا لتصبح ديناميكية
]

class LettersWordsGame:
    def __init__(self, line_bot_api, use_ai=False, ask_ai=None):
        self.line_bot_api = line_bot_api
        self.use_ai = use_ai
        self.ask_ai = ask_ai
        self.current_letters = None
        self.valid_words = []
        self.found_words = {}
        self.words_needed = 3
        self.scores = {}
        
        # تحديات 6 حروف
        self.challenges = [
            {"letters": "ق ل م ب ر و"},
            {"letters": "ك ت ا ب ر ل"},
            {"letters": "م د ر س ه ل"},
            {"letters": "ش ج ر ف ق ه"},
            {"letters": "ح د ي ق ه ل"},
            {"letters": "ب ي ت ك ر م"},
            {"letters": "ن و ر س م ا"},
            {"letters": "ف ل ج ر ب ح"},
            {"letters": "س ل ا م و ن"},
            {"letters": "ع ص ف و ر ي"},
            {"letters": "ك ه ر م ا ن"},
            {"letters": "ح س ن ي ن"},
            {"letters": "ف ا ر س ي"},
            {"letters": "م ط ر و د"},
            {"letters": "ن ج م ه ر"},
            {"letters": "و ر د ي ة"},
            {"letters": "ع ل م ي ن"},
            {"letters": "س ط و ر ي"},
            {"letters": "ج ب ل ي ن"},
            {"letters": "ب ح ر ي ن"},
            {"letters": "ل ي م ا ن ك"},
            {"letters": "س ي ا ر ة"},
            {"letters": "ط ا ل ب ي"},
            {"letters": "ب ن ي ن ك"},
            {"letters": "ح ف ظ ي"},
            {"letters": "ق ل و ب ي"},
            {"letters": "ن ه ر ا ي"},
            {"letters": "ح ل و ي ا"},
            {"letters": "ف د ا ي ه"},
            {"letters": "ع ب د ا ل"},
            {"letters": "م ر ح ب ا"},
            {"letters": "و س ا م ي"},
            {"letters": "ح ج ر ا ن"},
            {"letters": "ف ل و ك ي"},
            {"letters": "ق ن د و ل"},
            {"letters": "ش م ع و ر"},
            {"letters": "ر س ا م ي"},
            {"letters": "ن ج ح و ر"},
            {"letters": "ك ت ف ي ن"},
            {"letters": "ح ص ا ر ي"},
            {"letters": "ب ط ا ر ق"},
            {"letters": "م و ز ي ل"},
            {"letters": "ع ص ر ي ن"},
            {"letters": "س ك و ت ي"},
            {"letters": "ل و ن ي ن"},
            {"letters": "ج و د ي ن"},
            {"letters": "ف ر ح ا ت"},
            {"letters": "ح ل ي م و"},
            {"letters": "ن و ر ي ل"},
            {"letters": "ك ا ر م و"},
            {"letters": "ب ش ر ا ك"},
            {"letters": "س م ا ح ي"},
            {"letters": "ط ي ب ا ن"},
            {"letters": "ف ل ي س م"},
            {"letters": "ح ا د ر و"},
            {"letters": "ن ج و م ي"},
            {"letters": "ع م ر و د"},
            {"letters": "ك ل م ي ن"},
            {"letters": "ش ر ق ي ن"},
            {"letters": "ف ر ه ا د"},
            {"letters": "ب و ر ي ن"},
            {"letters": "ح م ا د ر"},
            {"letters": "س و ف ي ن"},
            {"letters": "ل ي و ن د"},
            {"letters": "م ح ر و ب"},
            {"letters": "ع ف ر و ن"},
            {"letters": "ك و ن د ي"},
            {"letters": "ن ا د ي ر"},
            {"letters": "ب ر ي ا ه"},
            {"letters": "ح س ر ي ن"},
            {"letters": "ف ر ا ه و"},
            {"letters": "م و س ي ق"},
            {"letters": "ع ل ي و ن"},
            {"letters": "ش ا ر ب ي"},
            {"letters": "ك ي م ا ن"},
            {"letters": "ن ف ر و د"},
            {"letters": "ح و ل ي ن"},
            {"letters": "ب ر ق ا د"},
            {"letters": "س م ا د ي"},
            {"letters": "ط و ر ي ن"},
            {"letters": "ف ي ل م ا"},
            {"letters": "ع ر ب و ن"},
            {"letters": "ك م ي ل و"},
            {"letters": "ن و ر ا ه"},
            {"letters": "ح س ن ا و"},
            {"letters": "م ط ر ي ن"},
            {"letters": "ب ا ر ك ي"},
            {"letters": "س ا ل و ن"},
            {"letters": "ط ا ل ق ي"},
            {"letters": "ف و ر ي ن"},
            {"letters": "ع م ا ر و"},
            {"letters": "ك ل ب ي ن"},
            {"letters": "ن و ر ي ا"},
            {"letters": "ح م ر ا ن"},
            {"letters": "ب ر ي ك ا"},
            {"letters": "س ي ل ا م"}
        ]
    
    def normalize_text(self, text):
        if not text:
            return ""
        text = text.strip().lower()
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '')
        text = text.replace('ة', 'ه').replace('ى', 'ي')
        text = re.sub(r'[\u064B-\u065F]', '', text)
        text = re.sub(r'\s+', '', text)
        return text
    
    def can_form_word(self, word, letters):
        letters_list = letters.replace(' ', '')
        word_letters = list(word)
        for char in word_letters:
            if char in letters_list:
                letters_list = letters_list.replace(char, '', 1)
            else:
                return False
        return True
    
    def verify_word_with_ai(self, word):
        if not self.use_ai or not self.ask_ai:
            return True
        try:
            prompt = f"هل '{word}' كلمة عربية صحيحة؟ أجب بنعم أو لا فقط"
            response = self.ask_ai(prompt)
            return response and 'نعم' in response
        except:
            return True
    
    def generate_valid_words_from_dictionary(self, letters):
        letters_set = set(letters.replace(' ',''))
        valid = []
        for word in ARABIC_DICTIONARY:
            word_norm = self.normalize_text(word)
            if all(c in letters_set for c in word_norm) and self.can_form_word(word_norm, letters):
                valid.append(word_norm)
        return valid
    
    def start_game(self):
        challenge = random.choice(self.challenges)
        self.current_letters = challenge['letters']
        # استخراج الكلمات الممكنة من القاموس
        self.valid_words = self.generate_valid_words_from_dictionary(self.current_letters)
        self.found_words = {}
        self.scores = {}
        return TextSendMessage(text=f"▪️ لعبة تكوين الكلمات\n\nالحروف: {self.current_letters}\n\nكوّن {self.words_needed} كلمات من هذه الحروف\n\nاكتب كلمة واحدة في كل رسالة")
    
    def check_answer(self, text, user_id, display_name):
        text = text.strip()
        if text in ['جاوب', 'الحل']:
            return {
                'correct': False,
                'game_over': True,
                'response': TextSendMessage(text=f"▪️ بعض الكلمات الصحيحة:\n\n{', '.join(self.valid_words[:10])}")
            }
        word_normalized = self.normalize_text(text)
        if user_id in self.found_words and word_normalized in self.found_words[user_id]:
            return TextSendMessage(text=f"▪️ {display_name} هذه الكلمة سبق وأن أدخلتها.")
        if not self.can_form_word(word_normalized, self.current_letters):
            return TextSendMessage(text=f"▪️ {display_name} هذه الكلمة لا يمكن تكوينها من الحروف المعطاة.")
        is_valid = word_normalized in self.valid_words or self.verify_word_with_ai(text)
        if not is_valid:
            return TextSendMessage(text=f"▪️ {display_name} هذه الكلمة غير صحيحة.")
        if user_id not in self.found_words:
            self.found_words[user_id] = []
        self.found_words[user_id].append(word_normalized)
        if user_id not in self.scores:
            self.scores[user_id] = {'name': display_name, 'score': 0}
        points = 5
        self.scores[user_id]['score'] += points
        words_count = len(self.found_words[user_id])
        if words_count >= self.words_needed:
            return {
                'correct': True,
                'points': points,
                'won': True,
                'game_over': True,
                'response': TextSendMessage(text=f"▪️ {display_name} فاز\n\nالكلمات: {', '.join(self.found_words[user_id])}\n\nإجمالي النقاط: {self.scores[user_id]['score']}")
            }
        return {
            'correct': True,
            'points': points,
            'response': TextSendMessage(text=f"▪️ {display_name}\n\nكلمة صحيحة: {text}\n+{points} نقطة\n\nالكلمات المتبقية: {self.words_needed - words_count}")
        }
