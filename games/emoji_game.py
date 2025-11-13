import random
import re
from linebot.models import TextSendMessage

class EmojiGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.current_emojis = None
        self.correct_answer = None
        self.hints_list = []
        self.current_question = 1
        self.max_questions = 10
        self.players_scores = {}
        self.hint_used = False
        
        # قاموس الإيموجي والكلمات (موسّع)
        self.emoji_words = [
            {"emojis": "🌙 ⭐", "answer": "ليل", "hints": ["ليل", "سماء الليل", "نجوم"]},
            {"emojis": "☀️ 🏖️", "answer": "صيف", "hints": ["صيف", "شاطئ", "بحر"]},
            {"emojis": "📚 ✏️", "answer": "دراسة", "hints": ["دراسة", "مدرسة", "تعليم"]},
            {"emojis": "🍕 🍔", "answer": "طعام", "hints": ["طعام", "اكل", "غذاء"]},
            {"emojis": "⚽ 🏃", "answer": "رياضة", "hints": ["رياضة", "كرة", "لعب"]},
            {"emojis": "🏠 👨‍👩‍👧‍👦", "answer": "عائلة", "hints": ["عائلة", "اسرة", "اهل"]},
            {"emojis": "✈️ 🌍", "answer": "سفر", "hints": ["سفر", "رحلة", "سياحة"]},
            {"emojis": "💻 📱", "answer": "تقنية", "hints": ["تقنية", "تكنولوجيا", "حاسوب"]},
            {"emojis": "🌹 💐", "answer": "ورد", "hints": ["ورد", "زهور", "زهرة"]},
            {"emojis": "🚗 🛣️", "answer": "قيادة", "hints": ["قيادة", "سيارة", "طريق"]},
            {"emojis": "☕ 🍪", "answer": "قهوة", "hints": ["قهوة", "شاي", "مشروب"]},
            {"emojis": "🎵 🎸", "answer": "موسيقى", "hints": ["موسيقى", "اغاني", "غناء"]},
            {"emojis": "🐱 🐶", "answer": "حيوانات", "hints": ["حيوانات", "اليفة", "قط"]},
            {"emojis": "📖 🖊️", "answer": "كتابة", "hints": ["كتابة", "تاليف", "كتاب"]},
            {"emojis": "🌧️ ⛈️", "answer": "مطر", "hints": ["مطر", "امطار", "شتاء"]},
            {"emojis": "🍎 🍊", "answer": "فواكه", "hints": ["فواكه", "فاكهة", "تفاح"]},
            {"emojis": "🌊 🏄", "answer": "بحر", "hints": ["بحر", "محيط", "ماء"]},
            {"emojis": "🎂 🎉", "answer": "عيد ميلاد", "hints": ["عيد ميلاد", "احتفال", "حفلة"]},
            {"emojis": "🌲 🏕️", "answer": "تخييم", "hints": ["تخييم", "غابة", "طبيعة"]},
            {"emojis": "💰 💵", "answer": "مال", "hints": ["مال", "نقود", "فلوس"]}
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
    
    def start_game(self):
        self.current_question = 1
        self.players_scores = {}
        return self.next_question()
    
    def next_question(self):
        """الانتقال للسؤال التالي"""
        if self.current_question > self.max_questions:
            return self.end_game()
        
        emoji_data = random.choice(self.emoji_words)
        self.current_emojis = emoji_data["emojis"]
        self.correct_answer = emoji_data["answer"]
        self.hints_list = emoji_data["hints"]
        self.hint_used = False
        
        return TextSendMessage(
            text=f"السؤال {self.current_question}/{self.max_questions}\n\nخمن الكلمة من الإيموجي:\n{self.current_emojis}"
        )
    
    def get_hint(self):
        """الحصول على تلميح"""
        if self.hint_used:
            return TextSendMessage(text="تم استخدام التلميح مسبقاً")
        
        self.hint_used = True
        hint = f"تلميحات: {', '.join(self.hints_list[:2])}"
        
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
        if not self.current_emojis:
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
        hints_normalized = [self.normalize_text(h) for h in self.hints_list]
        
        if user_answer in hints_normalized:
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
