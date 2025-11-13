from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage,
    QuickReply, QuickReplyButton, MessageAction
)
import os
from datetime import datetime
from collections import defaultdict
import threading
import logging
import random

# استيراد الأدوات المساعدة
from utils.helpers import get_user_profile_safe, normalize_text, check_rate_limit, cleanup_old_games
from utils.database import init_db
from utils.ui_components import get_welcome_message, get_join_message, get_help_message
from utils.gemini_config import USE_AI

# مفاتيح Gemini
GEMINI_KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3")
]

def get_gemini_api_key():
    for key in GEMINI_KEYS:
        if key:
            return key
    return None

def switch_gemini_key(current_key):
    idx = GEMINI_KEYS.index(current_key) if current_key in GEMINI_KEYS else -1
    return GEMINI_KEYS[(idx + 1) % len(GEMINI_KEYS)]

# استيراد الألعاب
from games.chain_words_game import ChainWordsGame
from games.fast_typing_game import FastTypingGame
from games.human_animal_plant_game import HumanAnimalPlantGame
from games.compatibility_game import CompatibilityGame
from games.opposite_game import OppositeGame
from games.song_game import SongGame
from games.letters_words_game import LettersWordsGame
from games.make_words import MakeWordsGame
from games.differences_game import DifferencesGame
from games.name_compatibility import NameCompatibilityGame

# إعداد السجلات
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# إعداد LINE
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "YOUR_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "YOUR_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# بيانات
active_games = {}
registered_players = set()
user_message_count = defaultdict(lambda: {"count": 0, "reset_time": datetime.now()})
games_lock = threading.Lock()
players_lock = threading.Lock()

# قاعدة البيانات
init_db()

# خيط تنظيف
cleanup_thread = threading.Thread(
    target=cleanup_old_games, args=(active_games, games_lock), daemon=True
)
cleanup_thread.start()

# خريطة الألعاب
GAMES_MAP = {
    "أغنية": (SongGame, "أغنية"),
    "لعبة": (HumanAnimalPlantGame, "لعبة"),
    "سلسلة": (ChainWordsGame, "سلسلة"),
    "أسرع": (FastTypingGame, "أسرع"),
    "ضد": (OppositeGame, "ضد"),
    "ترتيب": (LettersWordsGame, "ترتيب"),
    "كوّن": (MakeWordsGame, "كوّن"),
    "اختلاف": (DifferencesGame, "اختلاف"),
    "توافق": (NameCompatibilityGame, "توافق")  # ✅ اللعبة الجديدة
}

SPECIAL_COMMANDS = ["سؤال", "تحدي", "اعتراف", "اكثر"]
BOT_COMMANDS = ["مساعدة", "انضم", "انسحب", "إيقاف", "لمح", "جاوب"] + list(GAMES_MAP.keys()) + SPECIAL_COMMANDS

# الأزرار الثابتة
def get_fixed_quick_reply_buttons():
    return QuickReply(
        items=[
            QuickReplyButton(action=MessageAction(label="أغنية", text="أغنية")),
            QuickReplyButton(action=MessageAction(label="لعبة", text="لعبة")),
            QuickReplyButton(action=MessageAction(label="سلسلة", text="سلسلة")),
            QuickReplyButton(action=MessageAction(label="أسرع", text="أسرع")),
            QuickReplyButton(action=MessageAction(label="ضد", text="ضد")),
            QuickReplyButton(action=MessageAction(label="ترتيب", text="ترتيب")),
            QuickReplyButton(action=MessageAction(label="كوّن", text="كوّن")),
            QuickReplyButton(action=MessageAction(label="اختلاف", text="اختلاف")),
            QuickReplyButton(action=MessageAction(label="توافق", text="توافق")),
            QuickReplyButton(action=MessageAction(label="سؤال", text="سؤال")),
            QuickReplyButton(action=MessageAction(label="تحدي", text="تحدي")),
            QuickReplyButton(action=MessageAction(label="اعتراف", text="اعتراف")),
            QuickReplyButton(action=MessageAction(label="اكثر", text="اكثر")),
        ]
    )

# بدء اللعبة
def start_game(game_id, game_class, game_type, user_id, event):
    try:
        with games_lock:
            if game_class in [HumanAnimalPlantGame, ChainWordsGame]:
                game = game_class(
                    line_bot_api, use_ai=USE_AI, get_api_key=get_gemini_api_key, switch_key=switch_gemini_key
                )
            else:
                game = game_class(line_bot_api)
            
            with players_lock:
                participants = registered_players.copy()
                participants.add(user_id)
            
            active_games[game_id] = {
                "game": game,
                "type": game_type,
                "created_at": datetime.now(),
                "participants": participants,
                "question_count": 0,
                "max_questions": 5,
                "player_scores": defaultdict(int),
            }

        response = game.start_game()
        line_bot_api.reply_message(event.reply_token, response)
        logger.info(f"🎮 بدأت لعبة {game_type} في {game_id}")
        return True

    except Exception as e:
        logger.error(f"❌ خطأ في بدء اللعبة {game_type}: {e}", exc_info=True)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"حدث خطأ في بدء لعبة {game_type}: {e}", quick_reply=get_fixed_quick_reply_buttons()),
        )
        return False

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    logger.info(f"📩 استلمنا webhook: {body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

# التعامل مع الرسائل
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = normalize_text(event.message.text)
    user_id = event.source.user_id

    if not user_text:
        return

    # تجاهل أي شيء خارج الأوامر
    if user_text not in BOT_COMMANDS:
        return

    # انضم
    if user_text == "انضم":
        registered_players.add(user_id)
        profile = get_user_profile_safe(line_bot_api, user_id)
        username = profile.display_name if profile else "مستخدم"
        line_bot_api.reply_message(event.reply_token, get_join_message(username))
        return

    # مساعدة
    if user_text == "مساعدة":
        line_bot_api.reply_message(event.reply_token, get_help_message())
        return

    # لمّح
    if user_text == "لمح":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="💡 هذا تلميح للعبة الحالية!", quick_reply=get_fixed_quick_reply_buttons()))
        return

    # جاوب
    if user_text == "جاوب":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="✅ الإجابة الصحيحة هي ...", quick_reply=get_fixed_quick_reply_buttons()))
        return

    # بدء الألعاب
    if user_text in GAMES_MAP:
        game_class, game_type = GAMES_MAP[user_text]
        game_id = f"{user_id}_{game_type}_{datetime.now().strftime('%H%M%S')}"
        start_game(game_id, game_class, game_type, user_id, event)
        return

    # أوامر خاصة
    if user_text in SPECIAL_COMMANDS:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"📌 أمر {user_text} قيد التنفيذ...", quick_reply=get_fixed_quick_reply_buttons()))
        return

# تشغيل السيرفر
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"🚀 بدء الخادم على المنفذ {port}")
    logger.info(f"📊 اللاعبون المسجلون: {len(registered_players)}")
    logger.info(f"🎮 الألعاب النشطة: {len(active_games)}")
    app.run(host="0.0.0.0", port=port)
