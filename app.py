from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
import os
from datetime import datetime
from collections import defaultdict
import threading
import logging

# استيراد الوظائف المساعدة
from utils.helpers import get_user_profile_safe, normalize_text, check_rate_limit, cleanup_old_games
from utils.database import init_db, update_user_points, get_user_stats, get_leaderboard
from utils.ui_components import get_quick_reply, get_more_quick_reply, get_winner_announcement, get_help_message, get_welcome_message, get_stats_message, get_leaderboard_message, get_join_message
from utils.gemini_config import get_gemini_api_key, switch_gemini_key, USE_AI

# استيراد الألعاب
from games.chain_words_game import ChainWordsGame
from games.fast_typing_game import FastTypingGame
from games.human_animal_plant_game import HumanAnimalPlantGame
from games.compatibility_game import CompatibilityGame
from games.opposite_game import OppositeGame
from games.emoji_game import EmojiGame
from games.song_game import SongGame

# إعداد السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# إعدادات LINE Bot
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'YOUR_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', 'YOUR_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# تخزين البيانات
active_games = {}
registered_players = set()
user_message_count = defaultdict(lambda: {'count': 0, 'reset_time': datetime.now()})

# أقفال thread-safe
games_lock = threading.Lock()
players_lock = threading.Lock()

# تهيئة قاعدة البيانات
init_db()

# بدء خيط التنظيف
cleanup_thread = threading.Thread(
    target=cleanup_old_games, 
    args=(active_games, games_lock), 
    daemon=True
)
cleanup_thread.start()

# خريطة الألعاب بعد حذف الألعاب غير المرغوبة وترتيبها
GAMES_MAP = {
    'أغنية': (SongGame, 'أغنية'),
    'إيموجي': (EmojiGame, 'إيموجي'),
    'توافق': (CompatibilityGame, 'توافق'),
    'لعبة': (HumanAnimalPlantGame, 'لعبة'),
    'سلسلة': (ChainWordsGame, 'سلسلة'),
    'أسرع': (FastTypingGame, 'أسرع'),
    'ضد': (OppositeGame, 'ضد')
}

# أوامر جديدة
SPECIAL_COMMANDS = ['سؤال', 'تحدي', 'اعتراف', 'اختلافات']

# أوامر البوت الأساسية التي يجب الرد عليها فقط
BOT_COMMANDS = ['ابدأ', 'البداية', 'قائمة', 'البوت', 'مساعدة', 'انضم', 'تسجيل', 'join', 'انسحب', 'خروج', 'leave', 'إيقاف', 'ايقاف'] + list(GAMES_MAP.keys()) + SPECIAL_COMMANDS

# قائمة الأزرار الثابتة لكل الأوامر الأساسية
FIXED_QUICK_REPLIES = [
    {"type": "action", "action": {"type": "message", "label": "ابدأ", "text": "ابدأ"}},
    {"type": "action", "action": {"type": "message", "label": "مساعدة", "text": "مساعدة"}},
    {"type": "action", "action": {"type": "message", "label": "انضم", "text": "انضم"}},
    {"type": "action", "action": {"type": "message", "label": "انسحب", "text": "انسحب"}},
    {"type": "action", "action": {"type": "message", "label": "إيقاف", "text": "إيقاف"}}
]

def get_fixed_quick_reply():
    return {"items": FIXED_QUICK_REPLIES}

def start_game(game_id, game_class, game_type, user_id, event):
    try:
        with games_lock:
            if game_class in [HumanAnimalPlantGame, ChainWordsGame]:
                game = game_class(line_bot_api, use_ai=USE_AI, get_api_key=get_gemini_api_key, switch_key=switch_gemini_key)
            else:
                game = game_class(line_bot_api)
            
            with players_lock:
                participants = registered_players.copy()
                participants.add(user_id)
            
            active_games[game_id] = {
                'game': game,
                'type': game_type,
                'created_at': datetime.now(),
                'participants': participants,
                'question_count': 0,
                'max_questions': 5,
                'player_scores': defaultdict(int)
            }
        
        response = game.start_game()
        line_bot_api.reply_message(event.reply_token, response)
        logger.info(f"بدأت لعبة {game_type} في {game_id}")
        return True
        
    except Exception as e:
        logger.error(f"خطأ في بدء اللعبة {game_type}: {e}", exc_info=True)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"❌ حدث خطأ في بدء لعبة {game_type}: {e}", quick_reply=get_fixed_quick_reply())
        )
        return False

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    logger.info(f"📩 استلمنا webhook: {body}")
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("❌ توقيع غير صالح")
        return 'Invalid signature', 400
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة webhook: {e}", exc_info=True)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        user_id = event.source.user_id
        text = event.message.text.strip()
        text_normalized = normalize_text(text)
        
        # تجاهل أي رسالة ليست من أوامر البوت
        if text_normalized not in [normalize_text(cmd) for cmd in BOT_COMMANDS]:
            logger.info(f"📌 تجاهل الرسالة: {text}")
            return
        
        display_name = get_user_profile_safe(user_id, line_bot_api)
        game_id = event.source.group_id if hasattr(event.source, 'group_id') else user_id
        
        if not check_rate_limit(user_id, user_message_count):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="⚠️ عدد كبير من الرسائل! انتظر دقيقة.", quick_reply=get_fixed_quick_reply())
            )
            return
        
        # === أوامر البداية + مساعدة ===
        if text_normalized in ['ابدأ', 'البداية', 'قائمة', 'البوت', 'مساعدة']:
            flex_message = get_welcome_message(display_name)
            help_message = get_help_message()
            combined_flex = {
                "type": "carousel",
                "contents": [flex_message, help_message]
            }
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text="مرحباً + مساعدة", contents=combined_flex, quick_reply=get_fixed_quick_reply())
            )
            return
        
        # الانضمام
        if text_normalized in ['انضم', 'تسجيل', 'join']:
            with players_lock:
                if user_id not in registered_players:
                    registered_players.add(user_id)
                    with games_lock:
                        for gid, game_data in active_games.items():
                            if 'participants' not in game_data:
                                game_data['participants'] = set()
                            game_data['participants'].add(user_id)
                    join_message = get_join_message(display_name)
                    line_bot_api.reply_message(
                        event.reply_token,
                        FlexSendMessage(alt_text="تم التسجيل", contents=join_message, quick_reply=get_fixed_quick_reply())
                    )
                    logger.info(f"انضم لاعب جديد: {display_name}")
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"أنت مسجل بالفعل يا {display_name}", quick_reply=get_fixed_quick_reply())
                    )
            return
        
        # الانسحاب
        if text_normalized in ['انسحب', 'خروج', 'leave']:
            with players_lock:
                if user_id in registered_players:
                    registered_players.remove(user_id)
                    with games_lock:
                        for gid, game_data in active_games.items():
                            if 'participants' in game_data and user_id in game_data['participants']:
                                game_data['participants'].remove(user_id)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"تم انسحابك يا {display_name}", quick_reply=get_fixed_quick_reply())
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="أنت غير مسجل", quick_reply=get_fixed_quick_reply())
                    )
            return
        
        # إيقاف اللعبة
        if text_normalized in ['إيقاف', 'ايقاف']:
            with games_lock:
                if game_id in active_games:
                    game_type = active_games[game_id]['type']
                    del active_games[game_id]
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"تم إيقاف لعبة {game_type}", quick_reply=get_fixed_quick_reply())
                    )
            return
        
        # الألعاب
        if text_normalized in [normalize_text(cmd) for cmd in GAMES_MAP.keys()]:
            for cmd, (game_class, game_type) in GAMES_MAP.items():
                if text_normalized == normalize_text(cmd):
                    start_game(game_id, game_class, game_type, user_id, event)
            return
        
        # SPECIAL_COMMANDS
        if text_normalized in [normalize_text(cmd) for cmd in SPECIAL_COMMANDS]:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"لقد اخترت الأمر: {text}", quick_reply=get_fixed_quick_reply())
            )
            return
        
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الرسالة: {e}", exc_info=True)
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"❌ حدث خطأ غير متوقع: {e}", quick_reply=get_fixed_quick_reply())
            )
        except Exception as inner_e:
            logger.error(f"❌ فشل إرسال رسالة الخطأ: {inner_e}", exc_info=True)

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"❌ خطأ غير متوقع في Flask: {error}", exc_info=True)
    return 'Internal Server Error', 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 بدء الخادم على المنفذ {port}")
    logger.info(f"📊 اللاعبون المسجلون: {len(registered_players)}")
    logger.info(f"🎮 الألعاب النشطة: {len(active_games)}")
    app.run(host='0.0.0.0', port=port, debug=False)
