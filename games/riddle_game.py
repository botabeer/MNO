import random
import re
from linebot.models import TextSendMessage
import google.generativeai as genai

class RiddleGame:
    def __init__(self, line_bot_api, use_ai=False, get_api_key=None, switch_key=None):
        self.line_bot_api = line_bot_api
        self.use_ai = use_ai
        self.get_api_key = get_api_key
        self.switch_key = switch_key
        self.current_riddle = None
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
        
        # مجموعة ألغاز كبيرة
        self.riddles = [
            {"riddle": "له أسنان ولا يعض، ما هو؟", "answer": "مشط"},
            {"riddle": "يسير بلا قدمين ويدخل الأذنين، ما هو؟", "answer": "صوت"},
            {"riddle": "كلما زاد نقص، ما هو؟", "answer": "عمر"},
            {"riddle": "له رأس ولا عين له، ما هو؟", "answer": "دبوس"},
            {"riddle": "يكتب ولا يقرأ، ما هو؟", "answer": "قلم"},
            {"riddle": "له عين ولا يرى، ما هو؟", "answer": "ابرة"},
            {"riddle": "يجري ولا يمشي، ما هو؟", "answer": "ماء"},
            {"riddle": "أخت خالك وليست خالتك، من هي؟", "answer": "امي"},
            {"riddle": "شيء موجود في السماء إذا أضفت له حرف أصبح في الأرض؟", "answer": "نجم"},
            {"riddle": "ما هو الشيء الذي يمشي ويقف وليس له أرجل؟", "answer": "ساعة"},
            {"riddle": "بيت بلا أبواب ولا نوافذ، ما هو؟", "answer": "بيض"},
            {"riddle": "له عنق ولا رأس له، ما هو؟", "answer": "زجاجة"},
            {"riddle": "أمشي بدون قدمين وأطير بلا جناحين وأبكي بلا عينين، من أنا؟", "answer": "سحابة"},
            {"riddle": "أنا في الماء ولدت وفي الماء أموت، من أنا؟", "answer": "ثلج"},
            {"riddle": "له أوراق وليس بشجر، ما هو؟", "answer": "كتاب"},
            {"riddle": "يحرق نفسه ليضيء للآخرين، ما هو؟", "answer": "شمعة"},
            {"riddle": "له قلب ولا يحب، ما هو؟", "answer": "شجرة"},
            {"riddle": "يسمع بلا أذن ويتكلم بلا لسان، ما هو؟", "answer": "تلفون"},
            {"riddle": "كلما أخذت منه كبر، ما هو؟", "answer": "حفرة"},
            {"riddle": "له أربع أرجل ولا يستطيع المشي، ما هو؟", "answer": "كرسي"}
        ]
    
    def normalize_text(self, text):
        """تطبيع النص للمقارنة"""
        text = text.strip().lower()
        text = re.sub(r'^ال', '', text)
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ة', 'ه')
        text = text.replace('ى', 'ي')
        text = re.sub(r'[\u064B-\u065F]', '', text)
        return text
    
    def generate_ai_riddle(self):
        """توليد لغز باستخدام AI"""
        if not self.model:
            return None
        
        try:
            prompt = """أنشئ لغز عربي بسيط.
            
            الرد يجب أن يكون بالصيغة التالية فقط:
            اللغز: [اللغز هنا]
            الإجابة: [الإجابة]
            
            اللغز يجب أن يكون سهل ومفهوم."""
            
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            lines = text.split('\n')
            riddle = None
            answer = None
            
            for line in lines:
                if 'اللغز:' in line or 'لغز:' in line:
                    riddle = line.split(':', 1)[1].strip()
                elif 'الإجابة:' in line or 'إجابة:' in line or 'الجواب:' in line:
                    answer = line.split(':', 1)[1].strip()
            
            if riddle and answer:
                return {"riddle": riddle, "answer": answer}
            
        except Exception as e:
            print(f"AI riddle generation error: {e}")
            if self.switch_key:
                self.switch_key()
        
        return None
    
    def start_game(self):
        self.current_question = 1
        self.players_scores = {}
        return self.next_question()
    
    def next_question(self):
        """الانتقال للسؤال التالي"""
        if self.current_question > self.max_questions:
            return self.end_game()
        
        # محاولة توليد لغز بالذكاء الاصطناعي
        riddle_data = None
        if self.use_ai:
            riddle_data = self.generate_ai_riddle()
        
        if not riddle_data:
            riddle_data = random.choice(self.riddles)
        
        self.current_riddle = riddle_data["riddle"]
        self.correct_answer = riddle_data["answer"]
        self.hint_used = False
        
        return TextSendMessage(
            text=f"السؤال {self.current_question}/{self.max_questions}\n\n{self.current_riddle}"
        )
    
    def get_hint(self):
        """الحصول على تلميح"""
        if self.hint_used:
            return TextSendMessage(text="تم استخدام التلميح مسبقاً")
        
        self.hint_used = True
        first_letter = self.correct_answer[0]
        hint = f"يبدأ بحرف: {first_letter}\nعدد الأحرف: {len(self.correct_answer)}"
        
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
    
    def check_answer(self, answer, user_id, display_name):
        if not self.current_riddle:
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
        
        if user_answer == correct_answer or correct_answer in user_answer:
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
