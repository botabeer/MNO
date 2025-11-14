from linebot.models import TextSendMessage
import random
import re

def normalize_text(text):
    if not text:
        return ""
    text = text.strip().lower()
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    text = text.replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '')
    text = text.replace('ة', 'ه').replace('ى', 'ي')
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'\s+', '', text)
    return text

class LettersWordsGame:
    def __init__(self, line_bot_api, use_ai=False, ask_ai=None):
        self.line_bot_api = line_bot_api
        self.use_ai = use_ai
        self.ask_ai = ask_ai
        
        self.all_challenges = [
            {"letters": "ق ل م ع ر ب", "words": ["قلم", "عمر", "رقم", "قلب", "لعب", "عرب", "عمل", "قمل"]},
            {"letters": "ك ت ا ب ل م", "words": ["كتاب", "كتب", "كلم", "ملك", "تلك", "بلك"]},
            {"letters": "م د ر س ه ل", "words": ["مدرسه", "درس", "مدر", "سرد", "سهل", "درسه"]},
            {"letters": "ش ج ر ه ق ف", "words": ["شجره", "جرش", "شجر", "قشر", "فجر", "شرف"]},
            {"letters": "ح د ي ق ه ل", "words": ["حديقه", "حديق", "قديح", "دقيق", "حقل", "قلد"]},
            {"letters": "ب ي ت ك ر م", "words": ["بيت", "كبير", "ترك", "كرم", "تبي", "ريم"]},
            {"letters": "ن و ر س م ا", "words": ["نور", "سمر", "مان", "نار", "سور", "مرس"]},
            {"letters": "ف ل ج ر ب ح", "words": ["فجر", "حرب", "فلج", "جرح", "حفل", "برج"]},
            {"letters": "ص ب ا ح ر ي", "words": ["صباح", "حار", "صحر", "بحر", "صبي", "حرب"]},
            {"letters": "ذ ه ب ن ج م", "words": ["ذهب", "نجم", "مذهب", "جمن", "نهج", "بهج"]},
            {"letters": "س ل ا م و", "words": ["سلام", "سلم", "سما", "لوم", "ماس", "سوم", "لام", "سوا"]},
            {"letters": "ك ل و ب ي", "words": ["كلب", "لوب", "بيل", "ليب", "بيك", "كوب", "كبي", "لوبى"]},
            {"letters": "ب ح ر ي ن", "words": ["بحر", "ربح", "حين", "نير", "برح", "رين", "بحين", "ربن"]},
            {"letters": "ش م س ي ء", "words": ["شمس", "ميس", "سيم", "شيء", "سهم", "سمس", "شمسئ", "ميسئ"]},
            {"letters": "ق م ر ي ن", "words": ["قمر", "نمر", "رمق", "منق", "قرم", "مرن", "قمين", "نقمر"]},
            {"letters": "و ر د ي ة", "words": ["ورد", "دير", "رود", "يدي", "روء", "يرد", "وردي", "ديرو"]},
            {"letters": "ط ي ر ا ن", "words": ["طير", "رطن", "نار", "يار", "رين", "طنا", "طيران", "نيري"]},
            {"letters": "ج ب ل ي ه", "words": ["جبل", "لبن", "هيج", "بلج", "جلد", "بيه", "جبليه", "لبجي"]},
            {"letters": "ف ا ك ه ة", "words": ["فاكهة", "كهف", "فهة", "أكه", "فهك", "كهة", "فكه", "كهفا"]},
            {"letters": "ر س ا ل ة", "words": ["رسالة", "سأل", "سرل", "رسم", "لرس", "سلا", "رسال", "سارل"]},
            {"letters": "س ي ا ر ة", "words": ["سيارة", "يارس", "رسي", "يار", "سير", "سيار", "سيا", "رسيه"]},
            {"letters": "ح ج ر ة ا", "words": ["حجرة", "جحر", "رحج", "جهر", "رحا", "حرا", "حجرا", "جحرا"]},
            {"letters": "م ط ع م و", "words": ["مطعم", "مطر", "مطو", "عمو", "موم", "عطم", "مطع", "موطا"]},
            {"letters": "ك ا ر ت و", "words": ["كارت", "رطو", "كار", "تور", "راك", "كرو", "كارتو", "راكو"]},
            {"letters": "ح ف ل ي ن", "words": ["حفل", "فيل", "لين", "نحل", "فنل", "فلح", "حفلن", "فنلي"]},
            {"letters": "ن ج م ي ء", "words": ["نجم", "جين", "منج", "جنم", "جمى", "نيج", "نجيم", "جينم"]},
            {"letters": "ش ا ج ر ة", "words": ["شجرة", "جرش", "رجة", "جرا", "رشه", "شجر", "شاجر", "جرشه"]},
            {"letters": "و ل د ي ن", "words": ["ولد", "دين", "لين", "نود", "ولد", "دينو", "ولدين", "دينول"]},
            {"letters": "ك ل م ا ت", "words": ["كلمات", "ملك", "مات", "تكلم", "كال", "لمت", "كلمت", "ملتك"]},
            {"letters": "ص ب ا ح ي", "words": ["صباح", "حبا", "صب", "باح", "صبي", "حير", "صباحي", "بحاص"]},
            {"letters": "ق ر ا ر ي", "words": ["قرار", "رقي", "قري", "راقي", "قر", "ريق", "قراري", "رقيق"]},
            {"letters": "ح ب ي ب ك", "words": ["حبيب", "حبك", "بك", "حب", "يك", "بيك", "حبيبي", "بكح"]},
            {"letters": "ف ن ا ن ي", "words": ["فنان", "نان", "فن", "نفي", "نيف", "انف", "فناني", "نانف"]},
            {"letters": "و ر ق ة ن", "words": ["ورقة", "رقة", "قور", "نار", "قر", "رنق", "ورقن", "قرون"]},
            {"letters": "س ف ي ن ة", "words": ["سفينة", "فين", "سفن", "نيف", "سنة", "فيس", "سفيني", "نيسف"]},
            {"letters": "ج د و ل ك", "words": ["جدول", "دول", "ولد", "جدو", "دلج", "لوك", "جدولك", "دولج"]},
            {"letters": "ر م ا د ي", "words": ["رمادي", "رمد", "ماد", "رمي", "أدام", "يرم", "رمادي", "مارد"]},
            {"letters": "ش م ا ل ي", "words": ["شمالي", "شمل", "مال", "لمي", "لش", "شم", "شمالي", "شملي"]},
            {"letters": "ط ا ق ة ك", "words": ["طاقة", "طاق", "قاطع", "كتا", "كط", "اط", "طاقه", "كتاق"]},
            {"letters": "و د ا ع ة", "words": ["وداع", "ودا", "دع", "اود", "واد", "اعد", "وداعي", "ادعو"]},
            {"letters": "ج و م ل ة", "words": ["جملة", "جمل", "ملة", "لجم", "جمو", "لم", "جملتي", "لمجه"]},
            {"letters": "ك ه ر ب ا", "words": ["كهربا", "كهر", "ربا", "بهك", "رهب", "كهرا", "كهربا", "هربك"]},
            {"letters": "س ل ا س ل", "words": ["سلسل", "سل", "لاس", "سلس", "لس", "سلا", "سلاسل", "لسلس"]},
            {"letters": "م س ا ج ل", "words": ["مسجل", "سجل", "جلم", "سما", "لجم", "سلم", "مساجل", "سملج"]},
            {"letters": "ر ق ي م ا", "words": ["رقيم", "قيم", "مرا", "قرم", "مرق", "رام", "رقيم", "مقر"]},
            {"letters": "ح ر و ف ك", "words": ["حروف", "حرف", "رفح", "كرف", "فرح", "حوك", "حرفك", "روفك"]},
            {"letters": "ب ل و ن ا", "words": ["بلون", "لون", "نبل", "نوبا", "لبن", "بول", "بلونا", "لبون"]},
            {"letters": "و ج ه ن ا", "words": ["وجه", "جنه", "نوج", "هوه", "نوه", "جهن", "وجهن", "نوجه"]},
            {"letters": "ك ر س ي ة", "words": ["كرسي", "سير", "ريس", "يسك", "ركس", "كريس", "كرسيه", "سريك"]},
            {"letters": "م ل و ن ي", "words": ["ملون", "لون", "نيم", "لوم", "ميل", "منو", "ملوني", "نومل"]},
            {"letters": "ح د ي د ا", "words": ["حديد", "حد", "ديد", "داح", "ديح", "حاد", "حديدا", "داحي"]},
            {"letters": "ش ي ك ل ا", "words": ["شيكلا", "شيك", "لكا", "كال", "شي", "لكي", "شيكلا", "كالش"]},
            {"letters": "ف ل ا س ف ة", "words": ["فلسفة", "فلس", "سف", "لاف", "سفه", "فسل", "فلسفه", "سفل"]},
            {"letters": "ر ع ي ن ا", "words": ["راعين", "رعي", "عين", "نار", "ران", "رينا", "راين", "عينر"]},
            {"letters": "ك ت ب ي ن", "words": ["كتبين", "كتب", "تين", "بكت", "تينك", "نك", "كتبين", "نبكت"]},
            {"letters": "س ل و ك ا", "words": ["سلوك", "سلو", "لوك", "كاس", "سلك", "لكو", "سلوكا", "كسلو"]},
            {"letters": "م و ق ع ن", "words": ["موقع", "وقا", "قوم", "منق", "موق", "قمن", "موقعن", "نقوم"]},
            {"letters": "ح و ل و ن", "words": ["حول", "لون", "نحو", "حل", "ول", "وح", "حولن", "نحوح"]},
            {"letters": "ج ر ي م ة", "words": ["جريمة", "جرم", "ريم", "مجر", "يرم", "جرة", "جريم", "مجره"]},
            {"letters": "ن ا ج ح ا", "words": ["ناجح", "نجا", "حان", "جان", "نحا", "جاح", "ناجحه", "حنجا"]},
            {"letters": "ط ب ي ب ا", "words": ["طبيب", "طب", "بيب", "باط", "بيط", "تب", "طبيبه", "بتاب"]},
            {"letters": "ك و ك ب ا", "words": ["كوكب", "كوك", "وكب", "كاب", "بوك", "كوك", "كوكبا", "بوكك"]},
            {"letters": "ق ل ب ي ن", "words": ["قلب", "لبن", "بقل", "نيل", "قبي", "قلن", "قلبي", "نقلب"]},
            {"letters": "س م ا ر ة", "words": ["سمارة", "سما", "مار", "رام", "سم", "مرس", "سماره", "رسم"]},
            {"letters": "ح ي ا ء ك", "words": ["حياء", "حيا", "ياك", "يك", "كحي", "يحا", "حياك", "يكحا"]},
            {"letters": "ش ب ا ك ة", "words": ["شبكة", "شبك", "بك", "كشب", "شك", "بكة", "شبكه", "كبش"]},
            {"letters": "م ن ا ر ي", "words": ["مناري", "منار", "نار", "ري", "مار", "مرن", "مناري", "رنام"]},
            {"letters": "و ر د ي ة", "words": ["ورديه", "ورد", "ردي", "دي", "وري", "وي", "ورديه", "ديور"]},
            {"letters": "ب ر و ز ي", "words": ["بروز", "بري", "روز", "ورز", "زب", "برز", "بروزي", "زبور"]},
            {"letters": "ج م ل ي ن", "words": ["جميل", "جمل", "لين", "مل", "ين", "جم", "جميلن", "لمج"]},
            {"letters": "ك ا ن ي ن", "words": ["كاني", "كان", "نين", "كان", "نكي", "ينك", "كانيه", "نكان"]},
            {"letters": "س ا ب ر ي", "words": ["صابر", "سبر", "ربا", "بر", "بري", "سار", "صابري", "ربيس"]}
        ]
        
        self.questions = []
        self.current_challenge = None
        self.found_words = set()
        self.hints_used = 0
        self.question_number = 0
        self.total_questions = 5
        self.player_scores = {}
        self.words_needed = 3
    
    def start_game(self):
        if self.use_ai and self.ask_ai:
            self._generate_ai_challenges()
        
        self.questions = random.sample(self.all_challenges, min(self.total_questions, len(self.all_challenges)))
        self.question_number = 0
        self.player_scores = {}
        return self._next_question()
    
    def _generate_ai_challenges(self):
        try:
            prompt = """اعطني 5 مجموعات من 6 حروف عربية مع 8 كلمات يمكن تكوينها من كل مجموعة.
الصيغة:
الحروف | الكلمات (مفصولة بفواصل)

مثال:
ق ل م ع ر ب | قلم، عمر، رقم، قلب، لعب، عرب، عمل، قمل"""
            
            response = self.ask_ai(prompt)
            if response:
                lines = response.strip().split('\n')
                new_challenges = []
                for line in lines:
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) == 2:
                            letters = parts[0].strip()
                            words = [w.strip() for w in parts[1].split('،') if w.strip()]
                            if len(words) >= 3:
                                new_challenges.append({
                                    'letters': letters,
                                    'words': words
                                })
                
                if new_challenges:
                    self.all_challenges = new_challenges
        except Exception as e:
            pass
    
    def _next_question(self):
        self.question_number += 1
        self.current_challenge = self.questions[self.question_number - 1]
        self.found_words = set()
        self.hints_used = 0
        return TextSendMessage(
            text=f"▪️ لعبة تكوين الكلمات\n\nسؤال {self.question_number} من {self.total_questions}\n\nالحروف: {self.current_challenge['letters']}\n\nكوّن {self.words_needed} كلمات صحيحة من هذه الحروف\n\n▫️ لمح - للحصول على تلميح\n▫️ جاوب - لعرض الإجابات"
        )
    
    def next_question(self):
        if self.question_number < self.total_questions:
            return self._next_question()
        return None
    
    def check_answer(self, answer, user_id, display_name):
        if not self.current_challenge:
            return None
        
        answer_lower = answer.strip().lower()
        
        if answer_lower in ['لمح', 'تلميح', 'hint']:
            if self.hints_used == 0:
                word = self.current_challenge['words'][0]
                first_letter = word[0]
                word_length = len(word)
                hint = f"▫️ مثال: يبدأ بحرف {first_letter} وعدد حروفه {word_length}"
                self.hints_used += 1
                return {
                    'response': TextSendMessage(text=hint),
                    'points': 0,
                    'correct': False,
                    'won': False,
                    'game_over': False
                }
            else:
                return {
                    'response': TextSendMessage(text="استخدمت التلميح"),
                    'points': 0,
                    'correct': False,
                    'won': False,
                    'game_over': False
                }
        
        if answer_lower in ['جاوب', 'الجواب', 'answer']:
            words_list = "، ".join(self.current_challenge['words'][:6])
            response_text = f"▪️ أمثلة من الإجابات:\n\n{words_list}"
            
            if self.question_number < self.total_questions:
                return {
                    'response': TextSendMessage(text=response_text),
                    'points': 0,
                    'correct': False,
                    'won': False,
                    'game_over': False,
                    'next_question': True
                }
            else:
                return self._end_game()
        
        normalized_answer = normalize_text(answer)
        
        for word in self.current_challenge['words']:
            if normalized_answer == normalize_text(word):
                if normalized_answer in self.found_words:
                    return {
                        'response': TextSendMessage(text="هذه الكلمة وجدتها بالفعل، اكتب كلمة أخرى"),
                        'points': 0,
                        'correct': False,
                        'won': False,
                        'game_over': False
                    }
                
                self.found_words.add(normalized_answer)
                points = 10
                
                if user_id not in self.player_scores:
                    self.player_scores[user_id] = {'name': display_name, 'score': 0}
                self.player_scores[user_id]['score'] += points
                
                if len(self.found_words) < self.words_needed:
                    remaining = self.words_needed - len(self.found_words)
                    response_text = f"▪️ صحيح {display_name}\n\n{answer} ✓\n\n▫️ النقاط: {points}\n▫️ باقي {remaining} كلمة"
                    return {
                        'response': TextSendMessage(text=response_text),
                        'points': points,
                        'correct': True,
                        'won': False,
                        'game_over': False
                    }
                else:
                    if self.question_number < self.total_questions:
                        response_text = f"▪️ ممتاز {display_name}\n\nأكملت التحدي\n\n▫️ النقاط: {points}"
                        return {
                            'response': TextSendMessage(text=response_text),
                            'points': points,
                            'correct': True,
                            'won': True,
                            'game_over': False,
                            'next_question': True
                        }
                    else:
                        return self._end_game()
        
        return {
            'response': TextSendMessage(text="كلمة غير صحيحة، حاول مرة أخرى"),
            'points': 0,
            'correct': False,
            'won': False,
            'game_over': False
        }
    
    def _end_game(self):
        if self.player_scores:
            sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
            winner = sorted_players[0][1]
            all_scores = [(data['name'], data['score']) for uid, data in sorted_players]
            
            from app import get_winner_card
            winner_card = get_winner_card(winner['name'], winner['score'], all_scores)
            
            return {
                'points': 0,
                'correct': False,
                'won': True,
                'game_over': True,
                'winner_card': winner_card
            }
        else:
            return {
                'response': TextSendMessage(text="انتهت اللعبة"),
                'points': 0,
                'correct': False,
                'won': False,
                'game_over': True
            }
