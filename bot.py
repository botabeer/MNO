# bot.py
from linebot.v3.messaging import WebhookHandler, ReplyMessage  # استعمال حسب مكتبتك
# ملاحظة: هنا أمثلة اتصال بسيطة — عدّلها لتوافق مع طريقة إعداد line-bot-sdk لديك.
from storage import Storage
from games.song_game import SongGame
from games.chain_words import ChainWordsGame
from games.opposite_game import OppositeGame
from games.compatibility import CompatibilityGame
from games.mafia_game import MafiaGame
from constants import COLORS

# افترض لديك instance من line_bot_api من إعدادك
# from linebot.v3 import LineBotApi
# line_bot_api = LineBotApi("<token>")

class GameManager:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.storage = Storage()
        # instance of each game
        self.song_game = SongGame(line_bot_api, self.storage)
        self.chain_game = ChainWordsGame(line_bot_api, self.storage)
        self.opposite_game = OppositeGame(line_bot_api, self.storage)
        self.compat_game = CompatibilityGame(line_bot_api, self.storage)
        self.mafia_game = MafiaGame(line_bot_api, self.storage)
        # active game per chat (group_id -> {"tag": tag, "instance": obj})
        self.active_games = {}

    def handle_command(self, text: str, user_id: str, display_name: str, reply_to_group_id: str = None):
        """
        نقطة إدخال رئيسية: استقبل نص من المستخدم، وإرجاع كائن/قائمة ريسبونس
        هذا مثال إرشادي؛ عدّل ليتوافق مع webhook handling الخاص بك.
        """
        t = text.strip()
        # أوامر عامة
        if t == "قائمة الألعاب":
            return [TextMessage(text="الألعاب المتاحة: اغنيه، سلسله، ضد، توافق، مافيا")]
        if t == "انضم اغنيه":
            self.storage.register_user(user_id, display_name)
            self.storage.register_user_for_game(user_id, "اغنيه")
            return TextMessage(text="تم تسجيلك في لعبة الأغنية")
        if t == "انضم سلسله":
            self.storage.register_user(user_id, display_name)
            self.storage.register_user_for_game(user_id, "سلسله")
            return TextMessage(text="تم تسجيلك في لعبة السلسلة")
        if t == "انضم ضد":
            self.storage.register_user(user_id, display_name)
            self.storage.register_user_for_game(user_id, "ضد")
            return TextMessage(text="تم تسجيلك في لعبة الأضداد")
        if t == "انضم مافيا":
            return self.mafia_game.check_answer("انضم مافيا", user_id, display_name)

        # تشغيل الألعاب
        if t == "اغنيه":
            return self.song_game.start_game()
        if t == "سلسله":
            return self.chain_game.start_game()
        if t == "ضد":
            return self.opposite_game.start_game()
        if t == "توافق":
            return self.compat_game.start_game()
        if t == "مافيا":
            return self.mafia_game.start_game()

        # توجيه الإجابة إلى اللعبة النشطة في المجموعة (إن وُجدت)
        active = self.active_games.get(reply_to_group_id)
        if active:
            game_tag = active["tag"]
            instance = active["instance"]
            # تمرير الإجابة إلى instance
            res = instance.check_answer(t, user_id, display_name)
            # تعامل مع الترانزيشن next_question
            if res and res.get("next_question"):
                next_msg = instance.next_question()
                return [res["response"], next_msg] if next_msg else res["response"]
            return res["response"] if res and "response" in res else res

        # كحل افتراضي، حاول تمرير لكل لعبة مفترض أنها في محادثة خاصة
        # (مثال: المستخدم يجيب "جاوب" على لعبة الأغنية بالخاص)
        for g in [self.song_game, self.chain_game, self.opposite_game, self.compat_game, self.mafia_game]:
            res = g.check_answer(t, user_id, display_name)
            if res:
                if res.get("next_question"):
                    next_msg = g.next_question()
                    return [res["response"], next_msg] if next_msg else res["response"]
                return res["response"]
        return TextMessage(text="أمر غير معروف أو ليس هناك لعبة نشطة هنا.")
