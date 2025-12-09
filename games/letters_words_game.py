from linebot.models import TextSendMessage, FlexSendMessage
import random
import re
from constants import COLORS

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
            {"letters": "ق ل م ع ر ك", "answers": ["قلم", "علم", "عمر", "رقم", "ملك", "قرم", "عرق", "كرم", "لقم", "عقر"]},
            {"letters": "ك ت ا ب ر ل", "answers": ["كتاب", "باب", "كتب", "تراب", "بكر", "كبر", "بار", "كرت", "تبر", "ركب"]},
            {"letters": "م د ر س ه ل", "answers": ["مدرسه", "سهل", "درس", "سهم", "مدر", "رمل", "مهر", "هرم", "سرد", "مهد"]},
            {"letters": "ش ج ر ف ق ه", "answers": ["شجر", "فجر", "قهر", "شرف", "فرش", "جرف", "شقه", "رشق", "فرق", "جهر"]},
            {"letters": "ح د ي ق ه ل", "answers": ["حديقه", "قديح", "حقل", "دقيق", "حيل", "قلد", "لحد", "ديل", "حدل", "قيد"]},
            {"letters": "ب ي ت ك ر م", "answers": ["بيت", "كريم", "كبر", "ترك", "ريم", "كتم", "بكر", "يكتب", "تمر", "بكي"]},
            {"letters": "ن و ر س م ا", "answers": ["نور", "سمر", "مان", "سور", "نار", "رمس", "مرس", "روس", "سمن", "نوم"]},
            {"letters": "ف ل ج ر ب ح", "answers": ["فجر", "جرح", "حرب", "حفل", "فلج", "برج", "رحب", "جفل", "فرح", "لحب"]},
            {"letters": "س ل ا م و ن", "answers": ["سلام", "سلم", "مان", "سما", "لوم", "ماس", "سول", "نام", "نسل", "ملس"]},
            {"letters": "ع ل ي ا ن ب", "answers": ["علي", "عليا", "بني", "ليان", "بان", "بعل", "نيل", "عني", "نبي", "علن"]},
            {"letters": "ص ب ح ا ل ر", "answers": ["صباح", "حصار", "صبر", "بحر", "صحار", "حار", "صحر", "برح", "صلح", "حبل"]},
            {"letters": "ج م ي ل ا ه", "answers": ["جميل", "جميله", "ليل", "جمال", "ملاح", "حمل", "جال", "ملح", "ليم", "حلم"]},
            {"letters": "ط ف ل و ه ا", "answers": ["طفل", "طفله", "طول", "طوف", "فول", "لطف", "لوف", "طاف", "فله", "طلو"]},
            {"letters": "ق ر ا ن ء ب", "answers": ["قران", "نار", "قار", "نقر", "رقن", "قرن", "انر", "نرق", "قرب", "برق"]},
            {"letters": "ع ا ل م ي ه", "answers": ["عالم", "عالمي", "علم", "معلم", "ملح", "علي", "حمل", "عمل", "ملي", "حلم"]},
            {"letters": "ش م س ر و ق", "answers": ["شمس", "شرق", "مشروق", "سور", "شور", "قرش", "قوس", "سقر", "روش", "مرق"]},
            {"letters": "ج ب ل ا ر ه", "answers": ["جبل", "جبار", "جار", "برج", "بحر", "جره", "بار", "رجل", "جرب", "لهب"]},
            {"letters": "ق م ر ن و ج", "answers": ["قمر", "نجم", "نور", "قرن", "جرن", "مرج", "رجم", "قرم", "جمر", "رمق"]},
            {"letters": "ب ح ر ا ن ي", "answers": ["بحر", "بحري", "بحار", "بحران", "نار", "حرب", "حبر", "ناري", "حير", "بني"]},
            {"letters": "ن خ ل ا ج ز", "answers": ["نخل", "جزء", "نجز", "خزن", "زجل", "حزن", "لخن", "جزل", "نزل", "خجل"]},
            {"letters": "س و ق ل ب ا", "answers": ["سوق", "قلب", "باس", "سبل", "قبل", "بلا", "لبس", "سقل", "لقب", "سلب"]},
            {"letters": "ز ه ر و د ق", "answers": ["زهر", "زهور", "ورد", "ورده", "دور", "زور", "قرد", "دهر", "زرد", "هدر"]},
            {"letters": "ح ك م ه ل ا", "answers": ["حكم", "حكمه", "حلم", "ملح", "كلم", "حمل", "لحم", "كمل", "حلك", "لمح"]},
            {"letters": "ش ع ر ي ب ا", "answers": ["شعر", "شعري", "عرب", "بشر", "رشي", "بعر", "يشع", "ربع", "شري", "عري"]},
            {"letters": "ط ر ي ق ل ه", "answers": ["طريق", "طريقه", "قرط", "طير", "قرل", "طلق", "قلط", "طرق", "قري", "لطي"]},
            {"letters": "ص د ي ق ا ح", "answers": ["صديق", "حصاد", "صاد", "حديق", "صيد", "حديد", "صدق", "حقد", "قصد", "صحي"]},
            {"letters": "ت ر ا ب و م", "answers": ["تراب", "بوم", "ترم", "بات", "توم", "رمت", "بار", "روم", "متر", "مرت"]},
            {"letters": "ن ج و م ي ل", "answers": ["نجوم", "جمل", "جول", "نيل", "لجم", "ملي", "ليم", "مول", "جمي", "نجل"]},
            {"letters": "ق ص ر ا ي ع", "answers": ["قصر", "قصير", "عصر", "عصير", "قرص", "صعر", "رصع", "عرق", "قري", "صري"]},
            {"letters": "ه و ا ء ل ي", "answers": ["هواء", "ليل", "لي", "هوى", "اول", "ولي", "الي", "يول", "هلي", "ليه"]},
            {"letters": "خ ب ز ا ر ي", "answers": ["خبز", "خبار", "بخار", "خزي", "ريخ", "برخ", "زير", "خري", "بزر", "زبر"]},
            {"letters": "ف ر ح ا ن ب", "answers": ["فرح", "فرحان", "حران", "فان", "برح", "حفر", "نبح", "رحب", "فرن", "حرف"]},
            {"letters": "ص ف ا ء ل و", "answers": ["صفاء", "صفو", "صول", "فصل", "فول", "صلف", "وفا", "لصف", "فلص", "صلو"]},
            {"letters": "ح ي ا ت ن ف", "answers": ["حياه", "حيات", "فني", "نفي", "حني", "فتن", "يفن", "حتف", "تحي", "نحت"]},
            {"letters": "ج و ه ر ا ب", "answers": ["جوهر", "جار", "جهر", "هجر", "برج", "جور", "رجو", "جهاب", "جرب", "رجب"]},
            {"letters": "م س ج د ا ر", "answers": ["مسجد", "مدرس", "سدر", "رمس", "سجر", "جسم", "مجس", "رجس", "سمد", "جرس"]},
            {"letters": "ن ا س ل ي ب", "answers": ["ناس", "ليبيا", "بني", "سيل", "بان", "سني", "نيل", "باس", "نسل", "ليس"]},
            {"letters": "ع ز ي ز ا ه", "answers": ["عزيز", "عزه", "زها", "عزا", "زيه", "يزع", "عيز", "هزع", "عزي", "زعي"]},
            {"letters": "غ ر ي ب ا ن", "answers": ["غريب", "غار", "غبار", "نار", "برن", "غبي", "بين", "غرن", "غرب", "ريغ"]},
            {"letters": "ك ر ي م ه ل", "answers": ["كريم", "كريمه", "حليم", "حلم", "ملك", "ليم", "كلم", "مكر", "كمل", "لكم"]},
            {"letters": "س ر ي ع ا ب", "answers": ["سريع", "عصر", "سبع", "بعر", "سير", "رعي", "عبر", "رسع", "سعي", "عير"]},
            {"letters": "ق و ي ا ن ه", "answers": ["قوي", "قوه", "نقي", "يقن", "قون", "هون", "يوق", "قنو", "نوي", "قين"]},
            {"letters": "ض ع ي ف ا ر", "answers": ["ضعيف", "رفع", "عرف", "فرع", "ضفر", "فرض", "عفر", "رضع", "ضرع", "فعر"]},
            {"letters": "ح ل و ا ي ب", "answers": ["حلو", "حلوى", "حوب", "بلو", "حوي", "ليح", "يحل", "بول", "حيل", "لوح"]},
            {"letters": "م ر ا ح ي ل", "answers": ["مرح", "حرام", "رحيل", "ملح", "حمل", "ريح", "لحم", "حرم", "رحم", "لمح"]},
            {"letters": "س م ك ا ع ر", "answers": ["سمك", "عسكر", "سكر", "عرك", "سمع", "كسر", "عرم", "سرع", "كرم", "سعر"]},
            {"letters": "ط ي ر ا ن ب", "answers": ["طيران", "طير", "بري", "طين", "رين", "نبت", "طرن", "برن", "طرب", "نطر"]},
            {"letters": "ج ز ي ر ه ا", "answers": ["جزيره", "جزير", "جره", "زهر", "رزي", "جري", "زير", "رجي", "جرز", "هزر"]},
            {"letters": "ق ل ع ه ا ت", "answers": ["قلعه", "علقه", "عقل", "قعل", "علت", "قلت", "عتل", "تعل", "لقع", "قعت"]},
            {"letters": "م د ي ن ه ا", "answers": ["مدينه", "مدين", "ديم", "يمن", "منه", "نمي", "دين", "ميد", "دمن", "همد"]}
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
        progress = f"{self.current_question + 1}/{self.total_questions}"
        self.valid_words = [normalize_text(word) for word in challenge['answers']]
        
        return FlexSendMessage(
            alt_text="تكوين الكلمات",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "تكوين الكلمات", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "12px"
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {"type": "text", "text": "السؤال", "size": "xs", "color": COLORS['text_light'], "flex": 0},
                                {"type": "text", "text": progress, "size": "xs", "color": COLORS['primary'], "weight": "bold", "align": "end"}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "md", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": letters, "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center"},
                                {"type": "text", "text": f"كون {self.words_needed} كلمات من هذه الحروف", "size": "sm", "color": COLORS['text_dark'], "margin": "md", "wrap": True, "align": "center"}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "button", "action": {"type": "message", "label": "لمح", "text": "لمح"}, "style": "secondary", "height": "sm", "flex": 1},
                                {"type": "button", "action": {"type": "message", "label": "جاوب", "text": "جاوب"}, "style": "secondary", "height": "sm", "flex": 1}
                            ],
                            "spacing": "sm",
                            "margin": "lg"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "button", "action": {"type": "message", "label": "إيقاف", "text": "إيقاف"}, "style": "secondary", "height": "sm", "flex": 1},
                                {"type": "button", "action": {"type": "message", "label": "تسجيل", "text": "تسجيل"}, "style": "secondary", "height": "sm", "flex": 1}
                            ],
                            "spacing": "sm",
                            "margin": "sm"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
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
                return {'response': TextSendMessage(text=f"يبدا بحرف: {sample_word[0]}\nعدد الحروف: {len(sample_word)}"), 'points': 0, 'correct': False}
            return {'response': TextSendMessage(text="استخدمت التلميح"), 'points': 0, 'correct': False}

        if text.lower() in ['جاوب', 'الحل']:
            some_words = ' - '.join(self.questions[self.current_question]['answers'][:5])
            if self.current_question + 1 < self.total_questions:
                return {'response': TextSendMessage(text=f"بعض الكلمات الصحيحه:\n{some_words}"), 'points': 0, 'correct': False, 'next_question': True}
            return self._end_game()

        word_normalized = normalize_text(text)

        if user_id in self.found_words and word_normalized in self.found_words[user_id]:
            return {'response': TextSendMessage(text="هذه الكلمه سبق وان ادخلتها"), 'points': 0, 'correct': False}

        is_valid = word_normalized in self.valid_words
        if not is_valid:
            return {'response': TextSendMessage(text="هذه الكلمه غير صحيحه"), 'points': 0, 'correct': False}

        self.found_words.setdefault(user_id, [])
        self.found_words[user_id].append(word_normalized)
        self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})

        points = 1
        self.player_scores[user_id]['score'] += points
        words_count = len(self.found_words[user_id])

        if words_count >= self.words_needed:
            if self.current_question + 1 < self.total_questions:
                return {'response': TextSendMessage(text=f"اجابه صحيحه {display_name}\n+{points} نقطه"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
            return self._end_game()

        return {'response': TextSendMessage(text=f"كلمه صحيحه\n+{points} نقطه\nالكلمات المتبقيه: {self.words_needed - words_count}"), 'points': points, 'correct': True}

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextSendMessage(text="انتهت اللعبه"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
        
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        
        players_contents = []
        medals = ["🥇", "🥈", "🥉"]
        
        for i, p in enumerate(sorted_players[:5]):
            medal = medals[i] if i < 3 else f"{i+1}."
            players_contents.append({
                "type": "box",
                "layout": "baseline",
                "contents": [
                    {"type": "text", "text": medal, "size": "sm", "flex": 0},
                    {"type": "text", "text": p[1]['name'], "size": "sm", "color": COLORS['text_dark'], "flex": 3, "margin": "sm"},
                    {"type": "text", "text": f"{p[1]['score']} نقطه", "size": "sm", "color": COLORS['primary'], "weight": "bold", "align": "end", "flex": 2}
                ],
                "margin": "md" if i > 0 else "sm"
            })
        
        winner_card = FlexSendMessage(
            alt_text="نتائج اللعبه",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "انتهت اللعبه", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "12px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "الفائز", "size": "sm", "color": COLORS['text_light'], "align": "center"},
                                {"type": "text", "text": winner['name'], "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center", "margin": "xs"},
                                {"type": "text", "text": f"{winner['score']} نقطه", "size": "lg", "color": COLORS['success'], "align": "center", "margin": "xs"}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "النتائج", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                                *players_contents
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "إعادة اللعب", "text": "تكوين"},
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
        return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
