from linebot.models import TextSendMessage, FlexSendMessage
import random
import re
from constants import COLORS

ARABIC_DICTIONARY = ["قلم","برق","مرو","قلب","لعب","عرب","عمل","قمل","كتاب","تلب","بكر","كلم","ملك","تلك","لبك","مدرس","درس","سهل","مدر","درسه","رمد","هلم","شجر","فجر","قهر","جرش","شرف","قش","حديق","حديقه","دقيق","حقل","قلد","قديح","بيت","كرم","كريم","ترك","تبي","ريم","كب","نور","سمر","سور","نار","مرس","مان","فجر","جرح","حرب","حفل","فلج","برج","سلام","سلم","سما","لوم","ماس","سوم","لام","منل"]

def normalize_text(text):
    if not text:
        return ""
    text = text.strip().lower()
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '').replace('ة', 'ه').replace('ى', 'ي')
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'\s+', '', text)
    return text

class LettersWordsGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.challenges = [
            {"letters": "ق ل م ب ر و"}, {"letters": "ك ت ا ب ر ل"},
            {"letters": "م د ر س ه ل"}, {"letters": "ش ج ر ف ق ه"},
            {"letters": "ح د ي ق ه ل"}, {"letters": "ب ي ت ك ر م"},
            {"letters": "ن و ر س م ا"}, {"letters": "ف ل ج ر ب ح"},
            {"letters": "س ل ا م و ن"}
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.found_words = {}
        self.valid_words = []
        self.words_needed = 3
        self.previous_answer = None
        self.hints_used = {}

    def start_game(self):
        self.questions = random.sample(self.challenges, self.total_questions)
        self.current_question = 0
        self.player_scores = {}
        self.found_words = {}
        self.previous_answer = None
        self.hints_used = {}
        return self._show_question()

    def _show_question(self):
        challenge = self.questions[self.current_question]
        letters = challenge['letters']
        self.valid_words = self._generate_valid_words(letters)
        return FlexSendMessage(
            alt_text="تكوين الكلمات",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "تكوين الكلمات", "weight": "bold", "size": "xl", "color": COLORS['white']}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "10px"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": f"جولة {self.current_question + 1} من {self.total_questions}", "size": "sm", "color": COLORS['text_light']}, {"type": "text", "text": letters, "size": "xxl", "color": COLORS['primary'], "weight": "bold", "margin": "md", "align": "center"}, {"type": "text", "text": f"كوّن {self.words_needed} كلمات من هذه الحروف", "size": "sm", "color": COLORS['text_dark'], "margin": "md", "wrap": True}], "margin": "lg", "spacing": "sm"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "box", "layout": "horizontal", "contents": [{"type": "button", "action": {"type": "message", "label": "لمح", "text": "لمح"}, "style": "secondary", "height": "sm"}, {"type": "button", "action": {"type": "message", "label": "جاوب", "text": "جاوب"}, "style": "secondary", "height": "sm"}], "spacing": "sm", "margin": "lg"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

    def _generate_valid_words(self, letters):
        letters_set = set(letters.replace(' ',''))
        valid = []
        for word in ARABIC_DICTIONARY:
            word_norm = normalize_text(word)
            if all(c in letters_set for c in word_norm) and self._can_form_word(word_norm, letters):
                valid.append(word_norm)
        return valid

    def _can_form_word(self, word, letters):
        letters_list = letters.replace(' ', '')
        for char in list(word):
            if char in letters_list:
                letters_list = letters_list.replace(char, '', 1)
            else:
                return False
        return True

    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.found_words = {}
            self.hints_used = {}
            return self._show_question()
        return None

    def check_answer(self, text, user_id, display_name):
        text = text.strip()

        if text.lower() in ['لمح', 'تلميح']:
            if user_id not in self.hints_used and len(self.valid_words) > 0:
                self.hints_used[user_id] = True
                sample_word = self.valid_words[0]
                return {'response': TextSendMessage(text=f"يبدأ بحرف: {sample_word[0]}\nعدد الحروف: {len(sample_word)}"), 'points': 0, 'correct': False}
            return {'response': TextSendMessage(text="استخدمت التلميح"), 'points': 0, 'correct': False}

        if text.lower() in ['جاوب', 'الحل']:
            some_words = ', '.join(self.valid_words[:5])
            self.previous_answer = some_words
            if self.current_question + 1 < self.total_questions:
                return {'response': TextSendMessage(text=f"بعض الكلمات الصحيحة:\n{some_words}"), 'points': 0, 'correct': False, 'next_question': True}
            return self._end_game()

        word_normalized = normalize_text(text)

        if user_id in self.found_words and word_normalized in self.found_words[user_id]:
            return {'response': TextSendMessage(text="هذه الكلمة سبق وأن أدخلتها"), 'points': 0, 'correct': False}

        letters = self.questions[self.current_question]['letters']
        if not self._can_form_word(word_normalized, letters):
            return {'response': TextSendMessage(text="هذه الكلمة لا يمكن تكوينها من الحروف"), 'points': 0, 'correct': False}

        is_valid = word_normalized in self.valid_words
        if not is_valid:
            return {'response': TextSendMessage(text="هذه الكلمة غير صحيحة"), 'points': 0, 'correct': False}

        self.found_words.setdefault(user_id, [])
        self.found_words[user_id].append(word_normalized)
        self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})

        points = 5 if user_id not in self.hints_used else 3
        self.player_scores[user_id]['score'] += points
        words_count = len(self.found_words[user_id])

        if words_count >= self.words_needed:
            found_words_text = ', '.join(self.found_words[user_id])
            self.previous_answer = found_words_text
            if self.current_question + 1 < self.total_questions:
                return {'response': TextSendMessage(text=f"اجابة صحيحة {display_name}\nالكلمات: {found_words_text}\n+{self.player_scores[user_id]['score']} نقطة"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
            return self._end_game()

        return {'response': TextSendMessage(text=f"كلمة صحيحة: {text}\n+{points} نقطة\nالكلمات المتبقية: {self.words_needed - words_count}"), 'points': points, 'correct': True}

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextSendMessage(text="انتهت اللعبة"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        players_text = "\n".join([f"{i+1}. {p[1]['name']}: {p[1]['score']} نقطة" for i, p in enumerate(sorted_players[:5])])
        winner_card = FlexSendMessage(
            alt_text="نتائج اللعبة",
            contents={"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": [{"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "انتهت اللعبة", "weight": "bold", "size": "xl", "color": COLORS['white']}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "10px"}, {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "الفائز", "size": "sm", "color": COLORS['text_light']}, {"type": "text", "text": winner['name'], "size": "xxl", "color": COLORS['primary'], "weight": "bold", "margin": "xs"}, {"type": "text", "text": f"{winner['score']} نقطة", "size": "lg", "color": COLORS['text_dark'], "margin": "xs"}], "margin": "lg", "spacing": "xs"}, {"type": "separator", "margin": "lg", "color": COLORS['border']}, {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "النتائج", "size": "sm", "color": COLORS['text_light']}, {"type": "text", "text": players_text, "size": "sm", "color": COLORS['text_dark'], "wrap": True, "margin": "md"}], "margin": "lg"}, {"type": "separator", "margin": "lg", "color": COLORS['border']}, {"type": "button", "action": {"type": "message", "label": "إعادة", "text": "تكوين"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "lg"}], "backgroundColor": COLORS['card_bg'], "paddingAll": "20px"}}
        )
        return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
