import random
import re
from linebot.models import TextSendMessage
import google.generativeai as genai

class LettersWordsGame:
    def __init__(self, line_bot_api, use_ai=False, get_api_key=None, switch_key=None):
        self.line_bot_api = line_bot_api
        self.use_ai = use_ai
        self.get_api_key = get_api_key
        self.switch_key = switch_key
        self.available_letters = []
        self.used_words = set()
        self.model = None
        self.current_question = 1
        self.max_questions = 10
        self.players_scores = {}
        self.hint_used = False
        self.words_per_question = 2  # عدد الكلمات المطلوبة لكل سؤال
        self.current_round_words = 0
        
        # تهيئة AI
        if self.use_ai and self.get_api_key:
            try:
                api_key = self.get_api_key()
                if api_key:
                    genai.configure(api_key=api_key)
                    self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            except Exception as e:
                print(f"AI initialization error: {e}")
                self.use_ai = False
        
        # مجموعات الحروف
        self.letter_sets = [
            list("سيارةمنزل"),
            list("مدرسةكتاب"),
            list("طعامشراب"),
            list("شجرةزهرة"),
            list("سماءنجم"),
            list("بحرماء"),
            list("حديقةورد"),
            list("مكتبقلم"),
            list("سريرباب"),
            list("قمرليل")
        ]
        
        # كلمات صحيحة شائعة (موسّعة)
        self.valid_words = {
            "سيارة", "سير", "سار", "يسير", "منزل", "نزل", "زلة", "نزيل", "سيار",
            "مدرسة", "درس", "مدر", "سرد", "كتاب", "كتب", "تاب", "رسم", "دار",
            "طعام", "طام", "معط", "شراب", "شرب", "راب", "بار", "طبع",
            "شجرة", "شجر", "زهرة", "زهر", "هرة", "جرة",
            "سماء", "سما", "ماء", "نجم", "جمن", "سام",
            "بحر", "حرب", "ماء", "بار", "حبر",
            "حديقة", "ورد", "حدق", "وقد", "قدر",
            "مكتب", "قلم", "كتب", "ملك", "قبل",
            "سرير", "باب", "سير", "رسي", "بار",
            "قمر", "ليل", "مري", "قير", "ملي"
        }
    
    def normalize_text(self, text):
        """تطبيع النص للمقارنة"""
        text = text.strip().lower()
        text = re.sub(r'^ال', '', text)
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ة', 'ه')
        text = text.replace('ى', 'ي')
        text = re.sub(r'[\u064B-\u065F]', '', text)
        return text
    
    def start_game(self):
        self.current_question = 1
        self.players_scores = {}
        return self.next_question()
    
    def next_question(self):
        """الانتقال للسؤال التالي"""
        if self.current_question > self.max_questions:
            return self.end_game()
        
        self.available_letters = random.choice(self.letter_sets).copy()
        random.shuffle(self.available_letters)
        self.used_words.clear()
        self.hint_used = False
        self.current_round_words = 0
        
        letters_str = ' '.join(self.available_letters)
        return TextSendMessage(
            text=f"السؤال {self.current_question}/{self.max_questions}\n\nكون كلمتين من هذه الحروف:\n{letters_str}"
        )
    
    def get_hint(self):
        """الحصول على تلميح"""
        if self.hint_used:
            return TextSendMessage(text="تم استخدام التلميح مسبقاً")
        
        self.hint_used = True
        hint = "حاول تكوين كلمة من 3-4 أحرف"
        
        return TextSendMessage(text=f"تلميح:\n{hint}")
    
    def show_answer(self):
        """عرض كلمات مقترحة"""
        letters_str = ''.join(self.available_letters).lower()
        suggestions = []
        
        for word in self.valid_words:
            if len(word) >= 2:
                temp_letters = list(letters_str)
                valid = True
                for char in word:
                    if char in temp_letters:
                        temp_letters.remove(char)
                    else:
                        valid = False
                        break
                if valid:
                    suggestions.append(word)
        
        if suggestions:
            msg = f"كلمات مقترحة:\n{', '.join(suggestions[:3])}"
        else:
            msg = "لم نجد كلمات مقترحة"
        
        self.current_question += 1
        
        if self.current_question <= self.max_questions:
            next_q = self.next_question()
            return TextSendMessage(text=f"{msg}\n\n{next_q.text}")
        else:
            end_msg = self.end_game()
            return TextSendMessage(text=f"{msg}\n\n{end_msg.text}")
    
    def end_game(self):
        """إنهاء اللعبة وعرض النتائج"""
        if not self.players_scores:
            return TextSendMessage(text="انتهت اللعبة\nلم يشارك أحد")
        
        sorted_players = sorted(self.players_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        msg = "النتائج النهائية\n\n"
        for i, (name, data) in enumerate(sorted_players[:5], 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"  {i}."
            msg += f"{emoji} {name}: {data['score']} نقطة\n"
        
        winner = sorted_players[0]
        msg += f"\nالفائز: {winner[0]}"
        
        return TextSendMessage(text=msg)
    
    def check_word_with_ai(self, word):
        """التحقق من صحة الكلمة باستخدام AI"""
        if not self.model:
            return False
        
        try:
            prompt = f"هل '{word}' كلمة عربية صحيحة؟ أجب بنعم أو لا فقط"
            response = self.model.generate_content(prompt)
            ai_result = response.text.strip().lower()
            
            return 'نعم' in ai_result or 'yes' in ai_result
        except Exception as e:
            print(f"AI word check error: {e}")
            if self.switch_key:
                self.switch_key()
            return False
    
    def check_answer(self, answer, user_id, display_name):
        # التحقق من أوامر التلميح والإجابة
        if answer == 'لمح':
            return {
                'message': '',
                'points': 0,
                'game_over': False,
                'response': self.get_hint()
            }
        
        if answer == 'جاوب':
            return {
                'message': '',
                'points': 0,
                'game_over': self.current_question > self.max_questions,
                'response': self.show_answer()
            }
        
        user_word = answer.strip().lower()
        
        # التحقق من التكرار
        if user_word in self.used_words:
            return {
                'message': f"الكلمة '{user_word}' مستخدمة مسبقاً",
                'points': 0,
                'game_over': False,
                'response': TextSendMessage(text=f"الكلمة '{user_word}' مستخدمة مسبقاً")
            }
        
        # التحقق من توفر الحروف
        temp_letters = self.available_letters.copy()
        for letter in user_word:
            if letter in temp_letters:
                temp_letters.remove(letter)
            else:
                letters_str = ' '.join(self.available_letters)
                return {
                    'message': f"الحرف '{letter}' غير متوفر",
                    'points': 0,
                    'game_over': False,
                    'response': TextSendMessage(text=f"الحرف '{letter}' غير متوفر\nالحروف المتاحة: {letters_str}")
                }
        
        # التحقق من طول الكلمة
        if len(user_word) < 2:
            return {
                'message': "الكلمة يجب أن تكون حرفين على الأقل",
                'points': 0,
                'game_over': False,
                'response': TextSendMessage(text="الكلمة يجب أن تكون حرفين على الأقل")
            }
        
        # التحقق من صحة الكلمة
        is_valid = False
        
        # التحقق بالذكاء الاصطناعي أولاً
        if self.use_ai:
            is_valid = self.check_word_with_ai(user_word)
        
        # التحقق التقليدي كاحتياطي
        if not is_valid:
            normalized_word = self.normalize_text(user_word)
            normalized_valid = {self.normalize_text(w) for w in self.valid_words}
            is_valid = normalized_word in normalized_valid
        
        if not is_valid:
            return {
                'message': f"'{user_word}' ليست كلمة صحيحة",
                'points': 0,
                'game_over': False,
                'response': TextSendMessage(text=f"'{user_word}' ليست كلمة صحيحة")
            }
        
        # إجابة صحيحة
        self.used_words.add(user_word)
        self.current_round_words += 1
        points = 5 if not self.hint_used else 3
        
        if display_name not in self.players_scores:
            self.players_scores[display_name] = {'score': 0}
        self.players_scores[display_name]['score'] += points
        
        # التحقق من اكتمال الكلمتين
        if self.current_round_words >= self.words_per_question:
            msg = f"صحيح يا {display_name}"
            self.current_question += 1
            
            if self.current_question <= self.max_questions:
                next_q = self.next_question()
                return {
                    'message': msg,
                    'points': points,
                    'game_over': False,
                    'response': TextSendMessage(text=f"{msg}\n\n{next_q.text}")
                }
            else:
                end_msg = self.end_game()
                return {
                    'message': msg,
                    'points': points,
                    'won': True,
                    'game_over': True,
                    'response': TextSendMessage(text=f"{msg}\n\n{end_msg.text}")
                }
        else:
            remaining = self.words_per_question - self.current_round_words
            letters_str = ' '.join(self.available_letters)
            msg = f"صحيح يا {display_name}\nكلمة أخرى ({remaining} متبقية)\n\n{letters_str}"
            
            return {
                'message': msg,
                'points': points,
                'game_over': False,
                'response': TextSendMessage(text=msg)
            }
