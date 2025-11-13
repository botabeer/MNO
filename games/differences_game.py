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
                'puzzle': 'https://up6.cc/2025/10/176300269322041.jpeg',
                'solution': 'https://up6.cc/2025/10/176300269324622.jpeg'
            },
            {
                'puzzle': 'https://up6.cc/2025/10/176300269325883.jpeg',
                'solution': 'https://up6.cc/2025/10/176300269328574.jpeg'
            },
            {
                'puzzle': 'https://up6.cc/2025/10/176300269333045.jpeg',
                'solution': 'https://up6.cc/2025/10/176300292845955.jpeg'
            },
            {
                'puzzle': 'https://up6.cc/2025/10/176300292842534.jpeg',
                'solution': 'https://up6.cc/2025/10/176300292839723.jpeg'
            },
            {
                'puzzle': 'https://up6.cc/2025/10/176300292838272.jpeg',
                'solution': 'https://up6.cc/2025/10/176300292836241.jpeg'
            },
            {
                'puzzle': 'https://up6.cc/2025/10/176300308283581.jpeg',
                'solution': 'https://up6.cc/2025/10/176300308285072.jpeg'
            },
            {
                'puzzle': 'https://up6.cc/2025/10/176300308289583.jpeg',
                'solution': 'https://up6.cc/2025/10/176300308292614.jpeg'
            },
            {
                'puzzle': 'https://up6.cc/2025/10/176300308294345.jpeg',
                'solution': 'https://up6.cc/2025/10/176300322419141.jpeg'
            },
            {
                'puzzle': 'https://up6.cc/2025/10/176300322424732.jpeg',
                'solution': 'https://up6.cc/2025/10/176300322426263.jpeg'
            },
            {
                'puzzle': 'https://up6.cc/2025/10/176300322433374.jpeg',
                'solution': 'https://up6.cc/2025/10/176300322435875.jpeg'
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
