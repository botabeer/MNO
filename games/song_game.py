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

class SongGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.all_songs = [
            {"hint": "أغنية لعبدالمجيد عبدالله", "answer": "أحبك موت", "artist": "عبدالمجيد عبدالله"},
            {"hint": "أغنية لمحمد عبده", "answer": "الأماكن", "artist": "محمد عبده"},
            {"hint": "أغنية لراشد الماجد", "answer": "يا بعد عمري", "artist": "راشد الماجد"},
            {"hint": "أغنية لماجد المهندس", "answer": "بعثر خاطري", "artist": "ماجد المهندس"},
            {"hint": "أغنية لنوال الكويتية", "answer": "متعب عمري", "artist": "نوال الكويتية"},
            {"hint": "أغنية لعبدالله الرويشد", "answer": "خلاص سكرنا", "artist": "عبدالله الرويشد"},
            {"hint": "أغنية لنبيل شعيل", "answer": "حبيبي مجنني", "artist": "نبيل شعيل"},
            {"hint": "أغنية لكاظم الساهر", "answer": "زدني عشقاً", "artist": "كاظم الساهر"},
            {"hint": "أغنية لأصالة", "answer": "يا مغرور", "artist": "أصالة"},
            {"hint": "أغنية لإليسا", "answer": "عكس اللي شايفينها", "artist": "إليسا"},
            {"hint": "أغنية لعمرو دياب", "answer": "تملي معاك", "artist": "عمرو دياب"},
            {"hint": "أغنية لشيرين", "answer": "مشاعر", "artist": "شيرين"},
            {"hint": "أغنية لتامر حسني", "answer": "ناسيني ليه", "artist": "تامر حسني"},
            {"hint": "أغنية لوائل كفوري", "answer": "شو حلو", "artist": "وائل كفوري"},
            {"hint": "أغنية لنانسي عجرم", "answer": "آخ يا ألبي", "artist": "نانسي عجرم"}
        ]
        self.questions = []
        self.current_song = None
        self.hints_used = 0
        self.question_number = 0
        self.total_questions = 5
        self.player_scores = {}
    
    def start_game(self):
        self.questions = random.sample(self.all_songs, self.total_questions)
        self.question_number = 0
        self.player_scores = {}
        return self._next_question()
    
    def _next_question(self):
        self.question_number += 1
        self.current_song = self.questions[self.question_number - 1]
        self.hints_used = 0
        return TextSendMessage(
            text=f"▪️ لعبة الأغاني\n\nسؤال {self.question_number} من {self.total_questions}\n\n{self.current_song['hint']}\n\nخمن اسم الأغنية\n\n▫️ لمح - للحصول على تلميح\n▫️ جاوب - لعرض الإجابة"
        )
    
    def next_question(self):
        if self.question_number < self.total_questions:
            return self._next_question()
        return None
    
    def check_answer(self, answer, user_id, display_name):
        if not self.current_song:
            return None
        
        answer_lower = answer.strip().lower()
        
        # التلميح
        if answer_lower in ['لمح', 'تلميح', 'hint']:
            if self.hints_used == 0:
                hint = f"▫️ الفنان: {self.current_song['artist']}"
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
        
        # عرض الإجابة
        if answer_lower in ['جاوب', 'الجواب', 'answer']:
            response_text = f"▪️ الإجابة: {self.current_song['answer']}\n▫️ الفنان: {self.current_song['artist']}"
            
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
        
        # التحقق من الإجابة
        if normalize_text(answer) == normalize_text(self.current_song['answer']):
            points = 20 - (self.hints_used * 5)
            
            if user_id not in self.player_scores:
                self.player_scores[user_id] = {'name': display_name, 'score': 0}
            self.player_scores[user_id]['score'] += points
            
            if self.question_number < self.total_questions:
                response_text = f"▪️ صحيح {display_name}\n\n{self.current_song['answer']}\n{self.current_song['artist']}\n\n▫️ النقاط: {points}"
                return {
                    'response': TextSendMessage(text=response_text),
                    'points': points,
                    'correct': True,
                    'won': True,
                    'game_over': False,
                    'next_question': True
                }
            else:
                self.player_scores[user_id]['score'] += points
                return self._end_game()
        
        return None
    
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
