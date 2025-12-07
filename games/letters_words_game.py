from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import COLORS
from games.game_helpers import normalize_text, create_game_header, create_progress_box, create_separator, create_action_buttons, create_winner_card

class LettersWordsGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.challenges = [
            {"letters": "ق ل م ع ر ك", "answers": ["قلم", "علم", "عمر", "رقم", "ملك", "قرم", "عرق", "كرم", "لقم", "عقر"]},
            {"letters": "ك ت ا ب ر ل", "answers": ["كتاب", "باب", "كتب", "تراب", "بكر", "كبر", "بار", "كرت", "تبر", "ركب"]},
            {"letters": "م د ر س ه ل", "answers": ["مدرسه", "سهل", "درس", "سهم", "مدر", "رمل", "مهر", "هرم", "سرد", "مهد"]},
            {"letters": "ش ج ر ف ق ه", "answers": ["شجر", "فجر", "قهر", "شرف", "فرش", "جرف", "شقه", "رشق", "فرق", "جهر"]},
            {"letters": "ح د ي ق ه ل", "answers": ["حديقه", "قديح", "حقل", "دقيق", "حيل", "قلد", "لحد", "ديل", "حدل", "قيد"]},
            {"letters": "ب ي ت ك ر م", "answers": ["بيت", "كريم", "كبر", "ترك", "ريم", "كتم", "بكر", "يكتب", "تمر", "بكي"]},
            {"letters": "ن و ر س م ا", "answers": ["نور", "سمر", "مان", "سور", "نار", "رمس", "مرس", "روس", "سمن", "نوم"]},
            {"letters": "ف ل ج ر ب ح", "answers": ["فجر", "جرح", "حرب", "حفل", "فلج", "برج", "رحب", "جفل", "فرح", "لحب"]},
            {"letters": "س ل ا م و ن", "answers": ["سلام", "سلم", "مان", "سما", "لوم", "ماس", "سول", "نام", "نسل", "ملس"]},
            {"letters": "ع ل ي ا ن ب", "answers": ["علي", "عليا", "بني", "ليان", "بان", "بعل", "نيل", "عني", "نبي", "علن"]}
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.found_words = {}
        self.valid_words = []
        self.words_needed = 3
        self.hints_used = {}

    def start_game(self):
        self.questions = random.sample(self.challenges, self.total_questions)
        self.current_question = 0
        self.player_scores = {}
        self.found_words = {}
        self.hints_used = {}
        return self._show_question()

    def _show_question(self):
        challenge = self.questions[self.current_question]
        letters = challenge['letters']
        self.valid_words = [normalize_text(word) for word in challenge['answers']]
        
        contents = [
            create_game_header("تكوين الكلمات"),
            create_progress_box(self.current_question + 1, self.total_questions),
            create_separator(),
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": letters, "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center"},
                    {"type": "text", "text": f"كون {self.words_needed} كلمات من هذه الحروف", "size": "sm", "color": COLORS['text_dark'], "margin": "md", "wrap": True, "align": "center"}
                ],
                "margin": "lg"
            },
            create_separator(),
            *create_action_buttons()
        ]
        
        return FlexMessage(
            alt_text="تكوين الكلمات",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": contents,
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            })
        )

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
            if user_id not in self.hints_used:
                self.hints_used[user_id] = True
                sample_word = self.questions[self.current_question]['answers'][0]
                return {'response': TextMessage(text=f"يبدا بحرف: {sample_word[0]}\nعدد الحروف: {len(sample_word)}"), 'points': 0, 'correct': False}
            return {'response': TextMessage(text="استخدمت التلميح"), 'points': 0, 'correct': False}

        if text.lower() in ['جاوب', 'الحل']:
            some_words = ' - '.join(self.questions[self.current_question]['answers'][:5])
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"بعض الكلمات الصحيحه:\n{some_words}"), 'points': 0, 'correct': False, 'next_question': True}
            return self._end_game()

        word_normalized = normalize_text(text)

        if user_id in self.found_words and word_normalized in self.found_words[user_id]:
            return {'response': TextMessage(text="هذه الكلمه سبق وان ادخلتها"), 'points': 0, 'correct': False}

        is_valid = word_normalized in self.valid_words
        if not is_valid:
            return {'response': TextMessage(text="هذه الكلمه غير صحيحه"), 'points': 0, 'correct': False}

        self.found_words.setdefault(user_id, [])
        self.found_words[user_id].append(word_normalized)
        self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})

        points = 1
        self.player_scores[user_id]['score'] += points
        words_count = len(self.found_words[user_id])

        if words_count >= self.words_needed:
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"اجابه صحيحه {display_name}\n+{points} نقطه"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
            return self._end_game()

        return {'response': TextMessage(text=f"كلمه صحيحه\n+{points} نقطه\nالكلمات المتبقيه: {self.words_needed - words_count}"), 'points': points, 'correct': True}

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبه"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
        
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        
        winner_card_dict = create_winner_card(winner, sorted_players, "تكوين")
        
        return {
            'response': FlexMessage(alt_text="نتائج اللعبه", contents=FlexContainer.from_dict(winner_card_dict)),
            'points': winner['score'],
            'correct': True,
            'won': True,
            'game_over': True
        }
