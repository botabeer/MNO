from linebot.models import TextSendMessage
import random

class ChainWordsGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.current_word = None
        self.used_words = set()
    
    def start_game(self):
        start_words = ["قلم", "كتاب", "مدرسة", "باب", "نافذة"]
        self.current_word = random.choice(start_words)
        self.used_words = {self.current_word}
        return TextSendMessage(
            text=f"🔗 لعبة سلسلة الكلمات\n\nالكلمة: {self.current_word}\n\nاكتب كلمة تبدأ بآخر حرف ({self.current_word[-1]})"
        )
    
    def check_answer(self, answer, user_id, display_name):
        if not self.current_word:
            return None
        
        answer = answer.strip()
        last_letter = self.current_word[-1]
        
        # تطبيع الحروف
        if last_letter in ['ة', 'ه']:
            last_letter = 'ه'
        if answer and answer[0] in ['ة', 'ه']:
            answer = 'ه' + answer[1:]
        
        if answer in self.used_words:
            return {
                'response': TextSendMessage(text="❌ هذه الكلمة استخدمت من قبل"),
                'points': 0,
                'won': False,
                'game_over': False
            }
        
        if answer.startswith(last_letter):
            self.used_words.add(answer)
            old_word = self.current_word
            self.current_word = answer
            points = 5
            return {
                'response': TextSendMessage(
                    text=f"✅ صحيح {display_name}!\n\n{old_word} ← {answer}\n\nالآن اكتب كلمة تبدأ بـ ({answer[-1]})\n\n🎯 النقاط: +{points}"
                ),
                'points': points,
                'won': False,
                'game_over': False
            }
        else:
            return {
                'response': TextSendMessage(
                    text=f"❌ يجب أن تبدأ الكلمة بحرف ({last_letter})"
                ),
                'points': 0,
                'won': False,
                'game_over': False
            }
