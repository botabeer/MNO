from linebot.models import TextSendMessage, ImageSendMessage
import random
import logging

logger = logging.getLogger(__name__)

class DifferencesGame:
    """لعبة الفروقات - ترسل الصورة ثم الحل عند كتابة 'جاوب'"""
    
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.active_users = {}

        # قائمة الألغاز (كل لغز له صورة ولها حل)
        self.puzzles = [
            {
                'puzzle': 'https://mrkzgulfup.com/uploads/176303338682671.jpeg',
                'solution': 'https://mrkzgulfup.com/uploads/176303338684742.jpeg'
            },
            {
                'puzzle': 'https://mrkzgulfup.com/uploads/176303338686833.jpeg',
                'solution': 'https://mrkzgulfup.com/uploads/176303338695684.jpeg'
            },
            {
                'puzzle': 'https://mrkzgulfup.com/uploads/176303338705925.jpeg',
                'solution': 'https://mrkzgulfup.com/uploads/176303338714356.jpeg'
            },
            {
                'puzzle': 'https://mrkzgulfup.com/uploads/176303338715787.jpeg',
                'solution': 'https://mrkzgulfup.com/uploads/176303338717158.jpeg'
            },
            {
                'puzzle': 'https://mrkzgulfup.com/uploads/176303338718499.jpeg',
                'solution': 'https://mrkzgulfup.com/uploads/1763033387254610.jpeg'
            },
            {
                'puzzle': 'https://mrkzgulfup.com/uploads/1763033387269511.jpeg',
                'solution': 'https://mrkzgulfup.com/uploads/1763033387284912.jpeg'
            },
            {
                'puzzle': 'https://mrkzgulfup.com/uploads/1763033387350313.jpeg',
                'solution': 'https://mrkzgulfup.com/uploads/176303338737714.jpeg'
            },
        ]

    def start_game(self, user_id=None):
        """بدء اللعبة وعرض أول لغز"""
        if not self.puzzles:
            return TextSendMessage(text="🚫 لا توجد صور حالياً.")

        puzzle = random.choice(self.puzzles)
        self.active_users[user_id] = puzzle

        return [
            ImageSendMessage(
                original_content_url=puzzle['puzzle'],
                preview_image_url=puzzle['puzzle']
            ),
            TextSendMessage(
                text="👀 ابحث عن الفروقات في الصورة!\n\n"
                     "📝 اكتب 'جاوب' لعرض الحل، أو 'التالي' للغز جديد 🔁"
            )
        ]

    def check_answer(self, text, user_id, display_name):
        """التحكم في أوامر اللاعب"""
        if user_id not in self.active_users:
            return TextSendMessage(text="❌ لم تبدأ اللعبة بعد. اكتب 'اختلاف' لبدء اللعب.")

        text = text.strip().lower()

        # أمر "جاوب" → عرض الحل
        if text == "جاوب":
            puzzle = self.active_users[user_id]
            return [
                ImageSendMessage(
                    original_content_url=puzzle['solution'],
                    preview_image_url=puzzle['solution']
                ),
                TextSendMessage(text="✅ هذا هو الحل! اكتب 'التالي' لتحدي جديد 🔄")
            ]

        # أمر "التالي" → عرض لغز جديد
        elif text in ["التالي", "next"]:
            new_puzzle = random.choice(self.puzzles)
            self.active_users[user_id] = new_puzzle
            return [
                ImageSendMessage(
                    original_content_url=new_puzzle['puzzle'],
                    preview_image_url=new_puzzle['puzzle']
                ),
                TextSendMessage(
                    text="🧩 لغز جديد!\n\n"
                         "ابحث عن الفروقات 👀\n"
                         "واكتب 'جاوب' لرؤية الحل 🔍"
                )
            ]

        # أي أمر غير معروف → تجاهل
        else:
            return None
