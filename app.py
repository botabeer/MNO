# app.py (refactored)
import os
import logging
import re
import atexit
import signal
import time
from datetime import datetime
from typing import Optional, Tuple
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, request, abort, jsonify
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest,
    TextMessage, FlexMessage, FlexContainer, PushMessageRequest
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from apscheduler.schedulers.background import BackgroundScheduler

# المشروع يعتمد هذه الوحدات كما كانت عندك
from ui_builder import UIBuilder
from games.game_manager import GameManager
from database import Database

# ---------- Logging ----------
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mafia-bot")

# ---------- Config ----------
RATE_LIMIT_MESSAGES = int(os.getenv("RATE_LIMIT_MESSAGES", "50"))
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "3600"))  # seconds
MAX_NAME_LEN = int(os.getenv("MAX_NAME_LEN", "30"))
THREADPOOL_WORKERS = int(os.getenv("THREADPOOL_WORKERS", "4"))

required_env = ['LINE_CHANNEL_ACCESS_TOKEN', 'LINE_CHANNEL_SECRET']

def ensure_env():
    missing = [v for v in required_env if not os.getenv(v)]
    if missing:
        logger.error("Missing environment variables: %s", missing)
        raise RuntimeError(f"Missing environment variables: {missing}")

# ---------- Flask App ----------
app = Flask(__name__)

# ---------- LINE API Init ----------
def init_line_api():
    ensure_env()
    try:
        config = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
        handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
        api_client = ApiClient(config)
        messaging_api = MessagingApi(api_client)
        logger.info("LINE API initialized")
        return handler, messaging_api
    except Exception as e:
        logger.exception("Failed to initialize LINE API")
        raise

handler, line_bot_api = init_line_api()

# ---------- Database Init ----------
try:
    Database.init()
    logger.info("Database initialized")
except Exception:
    logger.exception("Database initialization failed")
    raise

# ---------- Game Manager ----------
game_manager = GameManager(line_bot_api)

# ---------- Scheduler ----------
scheduler = BackgroundScheduler()
scheduler.add_job(Database.cleanup_inactive_users, 'interval', hours=24, id='cleanup_users')
scheduler.start()
logger.info("Scheduler started")

def _shutdown_scheduler(signum=None, frame=None):
    try:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown(wait=False)
    except Exception:
        logger.exception("Error shutting down scheduler")

# handle signals for graceful shutdown
signal.signal(signal.SIGTERM, _shutdown_scheduler)
signal.signal(signal.SIGINT, _shutdown_scheduler)
atexit.register(_shutdown_scheduler)

# ---------- In-memory state (improved) ----------
# NOTE: For production with multiple processes, replace these with Redis or DB-backed keys.
waiting_for_registration = set()          # user ids waiting for registration
waiting_for_name_change = set()          # user ids waiting for name change

# rate-limiter: per-user deque of timestamps (most efficient pop-left)
user_message_times = defaultdict(lambda: deque())

# threadpool for background sends (avoid sleeping inside request)
executor = ThreadPoolExecutor(max_workers=THREADPOOL_WORKERS)

# ---------- NameFilter ----------
class NameFilter:
    BAD_WORDS = {
        'غبي','احمق','حمار','كلب','خنزير','قذر','وسخ',
        'حقير','نذل','خائن','كذاب','لعين','ملعون'
    }
    diacritics_re = re.compile(r'[\u064B-\u065F]')
    ws_re = re.compile(r'\s+')

    @staticmethod
    def normalize_arabic(text: str) -> str:
        if not text:
            return ""
        text = text.strip().lower()
        trans = str.maketrans({
            'أ':'ا','إ':'ا','آ':'ا',
            'ؤ':'و','ئ':'ي','ء':'',
            'ة':'ه','ى':'ي'
        })
        text = text.translate(trans)
        text = NameFilter.diacritics_re.sub('', text)
        text = NameFilter.ws_re.sub(' ', text)
        return text

    @classmethod
    def validate_name(cls, name: str) -> Tuple[bool, str]:
        if not name or not name.strip():
            return False, "الاسم لا يمكن ان يكون فارغا"

        name = name.strip()
        if len(name) > MAX_NAME_LEN:
            return False, f"الاسم طويل جدا (الحد الاقصى {MAX_NAME_LEN} حرف)"
        if len(name) < 1:
            return False, "الاسم قصير جدا (الحد الأدنى حرف واحد)"

        normalized = cls.normalize_arabic(name)
        for bad in cls.BAD_WORDS:
            if cls.normalize_arabic(bad) in normalized:
                return False, "الاسم يحتوي على كلمات غير لائقة"
        return True, ""

# ---------- Helpers ----------
def get_source_key(event) -> str:
    src = event.source
    # group_id, room_id, user_id possibilities
    return getattr(src, 'group_id', None) or getattr(src, 'room_id', None) or getattr(src, 'user_id', None)

def reply_message(reply_token, messages):
    if not isinstance(messages, list):
        messages = [messages]
    try:
        line_bot_api.reply_message(ReplyMessageRequest(reply_token=reply_token, messages=messages))
    except Exception:
        logger.exception("Failed to reply message")

def push_message(to, messages):
    if not isinstance(messages, list):
        messages = [messages]
    try:
        line_bot_api.push_message(PushMessageRequest(to=to, messages=messages))
    except Exception:
        logger.exception("Failed to push message to %s", to)

def send_next_question_async(target_group):
    """Send next question in a thread to avoid blocking handler"""
    try:
        next_q = game_manager.next_question(target_group)
        if next_q:
            push_message(target_group, next_q)
    except Exception:
        logger.exception("Failed to send next question")

def is_bot_command(text: str) -> bool:
    if not text:
        return False
    text_lower = text.strip().lower()
    BOT_COMMANDS = {
        'بدايه','start','ابدا','بداية','مساعده','help','مساعدة',
        'العاب','ألعاب','تسجيل','تغيير','تغيير الاسم','انسحب','نقاطي',
        'احصائياتي','الصداره','المتصدرين','الصدارة','اللاعبين','ايقاف',
        'stop','إيقاف','سؤال','سوال','تحدي','اعتراف','منشن','توافق',
        'اغنيه','لعبه','سلسله','اسرع','ضد','تكوين','فئه','مافيا',
        'لمح','تلميح','جاوب','الجواب','الغاء','إلغاء','انضم مافيا',
        'بدء مافيا','شرح مافيا','إنهاء الليل','تصويت مافيا','إنهاء التصويت',
        'حالة مافيا'
    }
    if text_lower in BOT_COMMANDS:
        return True
    if any(text_lower.startswith(prefix) for prefix in ('صوت ', 'اقتل ', 'افحص ', 'احمي ')):
        return True
    return False

def check_rate_limit(user_id: str) -> bool:
    now = time.time()
    dq = user_message_times[user_id]
    # pop old timestamps
    while dq and now - dq[0] >= RATE_LIMIT_PERIOD:
        dq.popleft()
    if len(dq) >= RATE_LIMIT_MESSAGES:
        return False
    dq.append(now)
    return True

# ---------- Webhook Handler ----------
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.warning("Invalid signature")
        abort(400)
    except Exception:
        logger.exception("Error handling webhook")
        abort(500)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    try:
        text = (event.message.text or "").strip()
        user_id = getattr(event.source, 'user_id', None)
        if not user_id:
            logger.warning("No user_id in event source; ignoring")
            return

        group_key = get_source_key(event)

        # Ignore withdrawn users for non-bot commands
        try:
            if Database.is_user_withdrawn(user_id) and not is_bot_command(text):
                return
        except Exception:
            logger.exception("Failed to check withdrawn status")

        # rate limit
        if not check_rate_limit(user_id):
            logger.warning("Rate limit exceeded for %s", user_id)
            reply_message(event.reply_token, TextMessage(text="لقد تجاوزت الحد الأقصى للرسائل. انتظر قليلا"))
            return

        # registration flow
        if user_id in waiting_for_registration:
            if text.lower() in {"انسحب", "إلغاء", "الغاء"}:
                waiting_for_registration.discard(user_id)
                reply_message(event.reply_token, TextMessage(text="تم الغاء التسجيل"))
                return
            valid, err = NameFilter.validate_name(text)
            if not valid:
                reply_message(event.reply_token, TextMessage(text=f"{err}\n\nاكتب اسم صحيح او اكتب الغاء"))
                return
            waiting_for_registration.discard(user_id)
            try:
                Database.register_or_update_user(user_id, text)
            except Exception:
                logger.exception("Failed to register user %s", user_id)
                reply_message(event.reply_token, TextMessage(text="حدث خطأ أثناء التسجيل"))
                return
            flex = FlexMessage(alt_text="تم التسجيل بنجاح",
                               contents=FlexContainer.from_dict(UIBuilder.registration_success_card(text)))
            reply_message(event.reply_token, flex)
            return

        # name change flow
        if user_id in waiting_for_name_change:
            if text.lower() in {"انسحب", "إلغاء", "الغاء"}:
                waiting_for_name_change.discard(user_id)
                reply_message(event.reply_token, TextMessage(text="تم الغاء تغيير الاسم"))
                return
            valid, err = NameFilter.validate_name(text)
            if not valid:
                reply_message(event.reply_token, TextMessage(text=f"{err}\n\nاكتب اسم صحيح او اكتب الغاء"))
                return
            waiting_for_name_change.discard(user_id)
            try:
                Database.register_or_update_user(user_id, text)
            except Exception:
                logger.exception("Failed to update user name %s", user_id)
                reply_message(event.reply_token, TextMessage(text="حدث خطأ أثناء تغيير الاسم"))
                return
            flex = FlexMessage(alt_text="تم تغيير الاسم",
                               contents=FlexContainer.from_dict(UIBuilder.name_changed_card(text)))
            reply_message(event.reply_token, flex)
            return

        # game-answer handling for messages that are not bot commands
        if not is_bot_command(text):
            game = game_manager.get_game(group_key)
            if game:
                game_type = game_manager.active_games.get(group_key, {}).get('type', '')
                if game_type not in ['mafia', 'compatibility']:
                    try:
                        if not Database.is_user_registered(user_id):
                            return
                    except Exception:
                        logger.exception("Failed registration check")

                try:
                    Database.update_last_activity(user_id)
                except Exception:
                    logger.exception("Failed to update last activity")

                display_name = Database.get_user_stats(user_id).get('display_name') if Database.get_user_stats(user_id) else "مستخدم"
                result = game_manager.check_answer(group_key, text, user_id, display_name)
                if result:
                    # points update
                    if result.get('correct') and result.get('points', 0) > 0 and game_type not in ['mafia', 'compatibility']:
                        try:
                            Database.update_user_points(user_id, result['points'], result.get('won', False), game_type)
                        except Exception:
                            logger.exception("Failed to update points for %s", user_id)

                    if result.get('response'):
                        reply_message(event.reply_token, result.get('response'))

                    if result.get('next_question') and not result.get('game_over'):
                        # send next question asynchronously (avoid sleep)
                        executor.submit(send_next_question_async, group_key)

                    if result.get('game_over'):
                        game_manager.stop_game(group_key)
                return

        # update last activity
        try:
            if Database.is_user_registered(user_id):
                Database.update_last_activity(user_id)
        except Exception:
            logger.exception("Failed to update last activity")

        display_name = None
        try:
            stats = Database.get_user_stats(user_id)
            if stats:
                display_name = stats.get('display_name')
        except Exception:
            logger.exception("Failed to get user stats")

        display_name = display_name or "مستخدم"

        # ---- Basic commands ----
        normalized_text = text.strip()
        # welcome
        if normalized_text.lower() in {"بدايه", "start", "ابدا", "بداية"}:
            flex = FlexMessage(alt_text="مرحبا",
                               contents=FlexContainer.from_dict(UIBuilder.welcome_card(display_name, Database.is_user_registered(user_id))))
            reply_message(event.reply_token, flex)
            return

        if normalized_text.lower() in {"مساعده", "help", "مساعدة"}:
            flex = FlexMessage(alt_text="المساعده",
                               contents=FlexContainer.from_dict(UIBuilder.help_card()))
            reply_message(event.reply_token, flex)
            return

        if normalized_text in {"ألعاب", "العاب"}:
            flex = FlexMessage(alt_text="قائمة الألعاب",
                               contents=FlexContainer.from_dict(UIBuilder.games_menu_card(Database.is_user_registered(user_id))))
            reply_message(event.reply_token, flex)
            return

        if normalized_text == "تسجيل":
            try:
                if Database.is_user_registered(user_id):
                    flex = FlexMessage(alt_text="مسجل بالفعل",
                                       contents=FlexContainer.from_dict(UIBuilder.already_registered_card(display_name)))
                    reply_message(event.reply_token, flex)
                else:
                    existing_name = Database.get_existing_user_name(user_id)
                    if existing_name:
                        Database.reactivate_user(user_id)
                        flex = FlexMessage(alt_text="مرحبا بعودتك",
                                           contents=FlexContainer.from_dict(UIBuilder.welcome_back_card(existing_name)))
                        reply_message(event.reply_token, flex)
                    else:
                        waiting_for_registration.add(user_id)
                        flex = FlexMessage(alt_text="التسجيل",
                                           contents=FlexContainer.from_dict(UIBuilder.registration_card()))
                        reply_message(event.reply_token, flex)
            except Exception:
                logger.exception("Error handling registration command")
                reply_message(event.reply_token, TextMessage(text="حدث خطأ أثناء معالجة التسجيل"))
            return

        if normalized_text in {"تغيير", "تغيير الاسم"}:
            try:
                if not Database.is_user_registered(user_id):
                    flex = FlexMessage(alt_text="يجب التسجيل أولا",
                                       contents=FlexContainer.from_dict(UIBuilder.need_registration_card()))
                    reply_message(event.reply_token, flex)
                else:
                    waiting_for_name_change.add(user_id)
                    flex = FlexMessage(alt_text="تغيير الاسم",
                                       contents=FlexContainer.from_dict(UIBuilder.change_name_card(display_name)))
                    reply_message(event.reply_token, flex)
            except Exception:
                logger.exception("Error handling name change")
                reply_message(event.reply_token, TextMessage(text="حدث خطأ"))
            return

        if normalized_text == "انسحب":
            try:
                if not Database.is_user_registered(user_id):
                    reply_message(event.reply_token, TextMessage(text="انت غير مسجل"))
                else:
                    Database.withdraw_user(user_id)
                    reply_message(event.reply_token, TextMessage(text="تم الانسحاب. لن يتم احتساب اجاباتك بعد الآن"))
            except Exception:
                logger.exception("Error handling withdraw")
                reply_message(event.reply_token, TextMessage(text="حدث خطأ"))
            return

        if normalized_text in {"نقاطي", "احصائياتي"}:
            try:
                if not Database.is_user_registered(user_id):
                    reply_message(event.reply_token, TextMessage(text="يجب التسجيل اولا"))
                    return
                stats = Database.get_user_stats(user_id)
                flex = FlexMessage(alt_text="احصائياتك",
                                   contents=FlexContainer.from_dict(UIBuilder.stats_card(display_name, stats)))
                reply_message(event.reply_token, flex)
            except Exception:
                logger.exception("Error getting stats")
                reply_message(event.reply_token, TextMessage(text="حدث خطأ"))
            return

        if normalized_text in {"الصداره", "المتصدرين", "الصدارة"}:
            try:
                leaders = Database.get_leaderboard(20)
                flex = FlexMessage(alt_text="لوحه الصداره",
                                   contents=FlexContainer.from_dict(UIBuilder.leaderboard_card(leaders)))
                reply_message(event.reply_token, flex)
            except Exception:
                logger.exception("Error getting leaderboard")
                reply_message(event.reply_token, TextMessage(text="حدث خطأ"))
            return

        if normalized_text == "اللاعبين":
            try:
                players = Database.get_all_players()
                flex = FlexMessage(alt_text="جميع اللاعبين",
                                   contents=FlexContainer.from_dict(UIBuilder.all_players_card(players)))
                reply_message(event.reply_token, flex)
            except Exception:
                logger.exception("Error getting players")
                reply_message(event.reply_token, TextMessage(text="حدث خطأ"))
            return

        if normalized_text in {"ايقاف", "stop", "إيقاف"}:
            try:
                stopped = game_manager.stop_game(group_key)
                msg = TextMessage(text="تم ايقاف اللعبه" if stopped else "لا توجد لعبه نشطه")
                reply_message(event.reply_token, msg)
            except Exception:
                logger.exception("Error stopping game")
                reply_message(event.reply_token, TextMessage(text="حدث خطأ"))
            return

        if normalized_text in {"سؤال", "سوال"}:
            reply_message(event.reply_token, TextMessage(text=game_manager.get_random_question()))
            return

        if normalized_text == "تحدي":
            reply_message(event.reply_token, TextMessage(text=game_manager.get_random_challenge()))
            return

        if normalized_text == "اعتراف":
            reply_message(event.reply_token, TextMessage(text=game_manager.get_random_confession()))
            return

        if normalized_text.startswith("منشن"):
            reply_message(event.reply_token, TextMessage(text=game_manager.get_random_mention()))
            return

        if normalized_text == "توافق":
            response = game_manager.start_game("compatibility", group_key)
            if response:
                reply_message(event.reply_token, response)
            return

        # game mapping
        game_commands = {
            "اغنيه": "song",
            "لعبه": "human_animal",
            "سلسله": "chain",
            "اسرع": "fast_typing",
            "ضد": "opposite",
            "تكوين": "letters",
            "فئه": "category",
            "مافيا": "mafia"
        }
        if normalized_text in game_commands:
            if normalized_text not in {"مافيا", "توافق"}:
                try:
                    if not Database.is_user_registered(user_id):
                        reply_message(event.reply_token, TextMessage(text="يجب التسجيل اولا لبدء الالعاب"))
                        return
                except Exception:
                    logger.exception("Error checking registration before starting game")
            response = game_manager.start_game(game_commands[normalized_text], group_key)
            if response:
                reply_message(event.reply_token, response)
            return

    except Exception:
        logger.exception("Unhandled error in message handler")

# ---------- health & index ----------
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'line-bot', 'timestamp': datetime.utcnow().isoformat()}), 200

@app.route('/', methods=['GET'])
def index():
    return jsonify({'name': 'Mafia Bot', 'version': '2.0', 'status': 'running'}), 200

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    logger.info("Starting locally on port %s", port)
    # debug False in production
    app.run(host='0.0.0.0', port=port, debug=os.getenv("FLASK_DEBUG", "0") == "1")
