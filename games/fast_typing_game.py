from linebot.models import TextSendMessage
import random
import time

class FastTypingGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.sentences = [
            "السرعة في الكتابة مهارة مهمة",
            "التدريب المستمر يحسن الأداء",
            "الممارسة تصنع الكمال",
            "الوقت من ذهب",
            "النجاح يحتاج إلى صبر وعمل"
        ]
        self.current_sentence = None
        self.start_time = None
    
    def start_game(self):
        self.current_sentence = random.choice(self.sentences)
        self.start_time = time.time()
        return TextSendMessage(
            text=f"⚡ لعبة أسرع\n\nاكتب هذه الجملة بأسرع وقت:\n\n{self.current_sentence}\n\n⏱️ الوقت بدأ!"
        )
    
    def check_answer(self, answer, user_id, display_name):
        if not self.current_sentence or not self.start_time:
            return None
        
        elapsed_time = time.time() - self.start_time
        
        if answer.strip() == self.current_sentence:
            points = max(10, int(30 - elapsed_time))
            return {
                'response': TextSendMessage(
                    text=f"✅ صحيح {display_name}!\n\n⏱️ الوقت: {elapsed_time:.2f} ثانية\n🎯 النقاط: +{points}"
                ),
                'points': points,
                'won': True,
                'game_over': True
            }
        else:
            return {
                'response': TextSendMessage(
                    text=f"❌ خطأ! حاول مرة أخرى\n\n⏱️ الوقت: {elapsed_time:.2f} ثانية"
                ),
                'points': 0,
                'won': False,
                'game_over': False
            }
