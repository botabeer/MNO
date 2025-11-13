from linebot.models import TextSendMessage
import random

class NameCompatibilityGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.active_games = {}

    def start(self, event):
        """بدء لعبة التوافق بالأسماء"""
        user_id = event.source.user_id
        self.active_games[user_id] = True
        msg = "💞 أرسل اسمين (مثلاً: أحمد و سارة) وسأحسب نسبة التوافق بينهما!"
        self.line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))

    def check_compatibility(self, event):
        """التحقق من الأسماء وحساب التوافق"""
        user_id = event.source.user_id
        if user_id not in self.active_games:
            return

        text = event.message.text.strip()
        if "و" not in text:
            msg = "❗ اكتب الأسماء بهذا الشكل: (اسم و اسم)"
            self.line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
            return

        try:
            name1, name2 = [x.strip() for x in text.split("و", 1)]
        except Exception:
            msg = "⚠️ صيغة غير صحيحة، جرب مثلاً: (علي و ريم)"
            self.line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
            return

        # حساب نسبة توافق عشوائية (مع ثبات طفيف بناءً على الاسم)
        seed = sum(ord(c) for c in name1 + name2)
        random.seed(seed)
        percentage = random.randint(40, 100)

        hearts = "💖" * (percentage // 20)
        msg = f"💞 نسبة التوافق بين {name1} و {name2}: {percentage}% {hearts}"
        self.line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))

        del self.active_games[user_id]
