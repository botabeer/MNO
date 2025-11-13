import random
import re
from linebot.models import TextSendMessage
import google.generativeai as genai

class OppositeGame:
    def __init__(self, line_bot_api, use_ai=False, get_api_key=None, switch_key=None):
        self.line_bot_api = line_bot_api
        self.use_ai = use_ai
        self.get_api_key = get_api_key
        self.switch_key = switch_key
        self.current_word = None
        self.correct_answer = None
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
        
        # قاموس الأضداد الكبير
        self.opposites = {
            "كبير": "صغير",
            "طويل": "قصير",
            "سريع": "بطيء",
            "حار": "بارد",
            "نظيف": "قذر",
            "قوي": "ضعيف",
            "غني": "فقير",
            "سعيد": "حزين",
            "جميل": "قبيح",
            "صعب": "سهل",
            "ثقيل": "خفيف",
            "جديد": "قديم",
            "واسع": "ضيق",
            "عالي": "منخفض",
            "نهار": "ليل",
            "شمس": "قمر",
            "صيف": "شتاء",
            "ذكي": "غبي",
            "شجاع": "جبان",
            "كريم": "بخيل",
            "أمين": "خائن",
            "صادق": "كاذب",
            "مفيد": "ضار",
            "ناجح": "فاشل",
            "حي": "ميت",
            "مريض": "صحيح",
            "قريب": "بعيد",
            "داخل": "خارج",
            "فوق": "تحت",
            "أمام": "خلف",
            "يمين": "يسار",
            "شرق": "غرب",
            "شمال": "جنوب",
            "صاعد": "نازل",
            "مفتوح": "مغلق",
            "ممتلئ": "فارغ",
            "مبلل": "جاف",
            "ناعم": "خشن",
            "لين": "قاسي",
            "حلو": "مر"
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
        
        self.current_word = random.choice(list(self.opposites.keys()))
        self.correct_answer = self.opposites[self.current_word]
        self.hint_used = False
        
        return TextSendMessage(
            text=f"السؤال {self.current_question}/{self.max_questions}\n\nما هو ضد:\n{self.current_word}"
        )
    
    def get_hint(self):
        """الحصول على تلميح"""
        if self.hint_used:
            return TextSendMessage(text="تم استخدام التلميح مسبقاً")
        
        self.hint_used = True
        first_letter = self.correct_answer[0]
        hint = f"يبدأ بحرف: {first_letter}"
        
        return TextSendMessage(text=f"تلميح:\n{hint}")
    
    def show_answer(self):
        """عرض الإجابة الصحيحة"""
        msg = f"الإجابة الصحيحة: {self.correct_answer}"
        
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
    
    def check_with_ai(self, answer):
        """التحقق من الإجابة باستخدام AI"""
        if not self.model:
            return False
        
        try:
            prompt = f"هل '{answer}' هو عكس أو ضد '{self.current_word}'؟ أجب بنعم أو لا فقط"
            response = self.model.generate_content(prompt)
            ai_result = response.text.strip().lower()
            
            return 'نعم' in ai_result or 'yes' in ai_result
        except Exception as e:
            print(f"AI check error: {e}")
            if self.switch_key:
                self.switch_key()
            return False
    
    def check_answer(self, answer, user_id, display_name):
        if not self.current_word:
            return None
        
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
        
        user_answer = self.normalize_text(answer)
        correct_answer = self.normalize_text(self.correct_answer)
        
        # التحقق باستخدام AI أولاً
        is_correct = False
        if self.use_ai:
            is_correct = self.check_with_ai(answer)
        
        # التحقق التقليدي كاحتياطي
        if not is_correct and user_answer == correct_answer:
            is_correct = True
        
        if is_correct:
            points = 10 if not self.hint_used else 5
            
            if display_name not in self.players_scores:
                self.players_scores[display_name] = {'score': 0}
            self.players_scores[display_name]['score'] += points
            
            msg = f"صحيح يا {display_name}"
            
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
