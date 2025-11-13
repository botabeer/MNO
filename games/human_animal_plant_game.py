import random
import re
from linebot.models import TextSendMessage
import google.generativeai as genai

class HumanAnimalPlantGame:
    def __init__(self, line_bot_api, use_ai=False, get_api_key=None, switch_key=None):
        self.line_bot_api = line_bot_api
        self.use_ai = use_ai
        self.get_api_key = get_api_key
        self.switch_key = switch_key
        self.current_category = None
        self.current_letter = None
        self.model = None
        self.current_question = 1
        self.max_questions = 10
        self.players_scores = {}
        self.hint_used = False
        
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
        
        # قاموس الفئات مع أمثلة كثيرة
        self.categories = {
            "إنسان": {
                "ا": ["أحمد", "إبراهيم", "أمل", "إيمان", "أمين", "إسلام", "أمير", "إلهام"],
                "م": ["محمد", "مريم", "ماجد", "منى", "مصطفى", "ميساء", "مالك", "مها"],
                "ع": ["علي", "عائشة", "عمر", "عبير", "عادل", "عبدالله", "عزيز", "عفاف"],
                "س": ["سعيد", "سارة", "سلمان", "سمية", "سالم", "سعاد", "سامي", "سلمى"],
                "ف": ["فاطمة", "فهد", "فيصل", "فريدة", "فارس", "فاتن", "فادي", "فوزية"],
                "ن": ["نورة", "ناصر", "نوف", "نايف", "نادية", "نبيل", "نور", "نهى"],
                "ح": ["حسن", "حنان", "حمد", "حصة", "حسين", "حليمة", "حاتم", "هند"],
                "ر": ["راشد", "رانيا", "رامي", "رشا", "رياض", "ريم", "رائد", "رباب"],
                "emoji": "👤"
            },
            "حيوان": {
                "ا": ["أسد", "أرنب", "أفعى", "إوز", "أيل"],
                "ن": ["نمر", "نسر", "نحلة", "نملة", "نعامة"],
                "ف": ["فيل", "فأر", "فهد", "فراشة", "فقمة"],
                "ج": ["جمل", "جاموس", "جرذ", "جراد"],
                "ق": ["قرد", "قط", "قنفذ", "قنديل"],
                "ح": ["حصان", "حمار", "حوت", "حمامة", "حرباء"],
                "د": ["دب", "ديك", "دجاجة", "دولفين"],
                "ز": ["زرافة", "زواحف"],
                "emoji": "🐾"
            },
            "نبات": {
                "ن": ["نخلة", "نعناع", "نرجس", "نبق"],
                "و": ["وردة", "ورد"],
                "ز": ["زيتون", "زهرة", "زنبق", "زعتر"],
                "ت": ["تفاح", "تمر", "توت", "تين"],
                "م": ["موز", "مانجو", "مشمش", "ملوخية"],
                "ب": ["برتقال", "بطيخ", "بصل", "بقدونس"],
                "ر": ["رمان", "ريحان"],
                "ع": ["عنب", "عدس"],
                "emoji": "🌱"
            },
            "جماد": {
                "ك": ["كرسي", "كتاب", "كوب", "كمبيوتر"],
                "ط": ["طاولة", "طبق", "طائرة"],
                "ق": ["قلم", "قارورة", "قفل"],
                "ب": ["باب", "بيت", "برج"],
                "س": ["سيارة", "سرير", "ساعة", "سفينة"],
                "ح": ["حاسوب", "حقيبة", "حجر"],
                "م": ["مفتاح", "مرآة", "مكتب"],
                "ن": ["نافذة", "نظارة"],
                "emoji": "📦"
            },
            "بلد": {
                "م": ["مصر", "المغرب", "ماليزيا", "المكسيك"],
                "س": ["سوريا", "السودان", "السعودية", "سنغافورة"],
                "ع": ["العراق", "عمان"],
                "ل": ["لبنان", "ليبيا"],
                "ا": ["الأردن", "الإمارات", "إسبانيا"],
                "ت": ["تونس", "تركيا", "تايلاند"],
                "ف": ["فرنسا", "فلسطين"],
                "ي": ["اليمن", "اليابان"],
                "emoji": "🌍"
            }
        }
        
        self.available_letters = ["ا", "م", "ع", "س", "ف", "ن", "ح", "ر", "ج", "ق", "د", "ز", "و", "ت", "ب", "ك", "ط", "ل", "ي"]
    
    def normalize_text(self, text):
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
        """اختيار مهمة جديدة بدون ترقيم"""
        if self.current_question > self.max_questions:
            return self.end_game()
        
        self.current_category = random.choice(list(self.categories.keys()))
        category_data = self.categories[self.current_category]
        
        available_in_category = [l for l in self.available_letters if l in category_data]
        self.current_letter = random.choice(available_in_category)
        self.hint_used = False
        
        return TextSendMessage(
            text=f"اذكر: {self.current_category}\nيبدأ بحرف: {self.current_letter}"
        )
    
    def get_hint(self):
        """تلميح: أمثلة أوليتين من نفس الفئة"""
        if self.hint_used:
            return TextSendMessage(text="تم استخدام التلميح مسبقاً")
        
        self.hint_used = True
        category_data = self.categories[self.current_category]
        examples = category_data.get(self.current_letter, [])
        hint = f"أمثلة: {', '.join(examples[:2])}"
        return TextSendMessage(text=f"تلميح:\n{hint}")
    
    def show_answer(self):
        """عرض الإجابة الصحيحة"""
        category_data = self.categories[self.current_category]
        examples = category_data.get(self.current_letter, [])
        msg = f"أمثلة صحيحة:\n{', '.join(examples[:3])}"
        
        self.current_question += 1
        
        if self.current_question <= self.max_questions:
            return self.next_question()
        else:
            return self.end_game()
    
    def end_game(self):
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
    
    def check_with_ai(self, answer):
        if not self.model:
            return False
        try:
            prompt = f"""هل '{answer}' من فئة {self.current_category} ويبدأ بحرف {self.current_letter}؟
            أجب بنعم أو لا فقط"""
            
            response = self.model.generate_content(prompt)
            ai_result = response.text.strip().lower()
            
            return 'نعم' in ai_result or 'yes' in ai_result
        except Exception as e:
            print(f"AI check error: {e}")
            if self.switch_key:
                self.switch_key()
            return False
    
    def check_answer(self, answer, user_id, display_name):
        if not self.current_category or not self.current_letter:
            return None
        
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
        
        user_answer = answer.strip()
        user_answer_normalized = self.normalize_text(user_answer)
        category_data = self.categories[self.current_category]
        valid_answers = category_data.get(self.current_letter, [])
        valid_answers_normalized = [self.normalize_text(ans) for ans in valid_answers]
        
        is_correct = False
        if self.use_ai:
            is_correct = self.check_with_ai(user_answer)
        
        if not is_correct and user_answer_normalized in valid_answers_normalized:
            is_correct = True
        
        if is_correct:
            points = 10 if not self.hint_used else 5
            
            if display_name not in self.players_scores:
                self.players_scores[display_name] = {'score': 0}
            self.players_scores[display_name]['score'] += points
            
            msg = f"صحيح يا {display_name}\n+{points} نقطة"
            
            self.current_question += 1
            
            if self.current_question <= self.max_questions:
                next_q = self.next_question()
                return {
                    'message': msg,
                    'points': points,
                    'won': True,
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
        
        return None
