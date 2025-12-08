import os
import logging
import re
import atexit
import signal
import time
from datetime import datetime
from typing import Tuple
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
import threading

from flask import Flask, request, abort, jsonify

# حاول تحميل متغيرات البيئة من ملف .env إذا كان موجودًا (اختياري)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # لا نفشل إذا لم يكن python-dotenv مثبتًا
    pass

# استيراد LINE SDK (v3 as in original). إذا كانت المسارات مختلفة في مكتبتكم، عدِّل هنا.
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest,
    TextMessage, FlexMessage, FlexContainer, PushMessageRequest
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from apscheduler.schedulers.background import BackgroundScheduler

# استيرادات محلية
from ui_builder import UIBuilder
from games.game_manager import GameManager
from database import Database

# ---------- Logging ----------
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("mafia-bot")

# ---------- Config ----------
RATE_LIMIT_MESSAGES = int(os.getenv("RATE_LIMIT_MESSAGES", "50"))
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "3600"))  # seconds
MAX_NAME_LEN = int(os.getenv("MAX_NAME_LEN", "30"))
THREADPOOL_WORKERS = int(os.getenv("THREADPOOL_WORKERS", "4"))

REQUIRED_ENV = ['LINE_CHANNEL_ACCESS_TOKEN', 'LINE_CHANNEL_SECRET']

def ensure_env():
    missing = [v for v in REQUIRED_ENV if not os.getenv(v)]
    if missing:
        logger.error("Missing environment variables: %s", missing)
        raise RuntimeError(f"Missing environment variables: {missing}")

# ---------- Flask app ----------
app = Flask(__name__)

# ---------- LINE API init ----------
def init_line_api():
    ensure_env()
    try:
        config = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
        handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
        api_client = ApiClient(config)
        messaging_api = MessagingApi(api_client)
        logger.info("LINE API initialized")
        return handler, messaging_api
    except Exception as exc:
        logger.exception("Failed to initialize LINE API: %s", exc)
        raise

handler, line_bot_api = init_line_api()

# ---------- Database init ----------
try:
    Database.init()
    logger.info("Database initialized")
except Exception as exc:
    logger.exception("Database initialization failed: %s", exc)
    raise

# ---------- Game manager ----------
game_manager = GameManager(line_bot_api)

# ---------- Scheduler ----------
scheduler = BackgroundScheduler()
try:
    scheduler.add_job(Database.cleanup_inactive_users, 'interval', hours=24, id='cleanup_users')
    scheduler.start()
    logger.info("Scheduler started")
except Exception:
    logger.exception("Failed to start scheduler")

def _shutdown_scheduler(signum=None, frame=None):
    try:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown(wait=False)
    except Exception:
        logger.exception("Error shutting down scheduler")

signal.signal(signal.SIGTERM, _shutdown_scheduler)
signal.signal(signal.SIGINT, _shutdown_scheduler)
atexit.register(_shutdown_scheduler)

# ---------- In-memory / concurrency ----------
waiting_for_registration = set()
waiting_for_name_change = set()

# user_message_times: user_id -> deque(timestamps)
user_message_times = defaultdict(lambda: deque())
_user_message_times_lock = threading.Lock()

executor = ThreadPoolExecutor(max_workers=THREADPOOL_WORKERS)

# ---------- Name filter ----------
class NameFilter:
    BAD_WORDS = {
        'غبي', 'احمق', 'حمار', 'كلب', 'خنزير', 'قذر', 'وسخ',
        'حقير', 'نذل', 'خائن', 'كذاب', 'لعين', 'ملعون'
    }
    diacritics_re = re.compile(r'[\u064B-\u065F]')
    ws_re = re.compile(r'\s+')

    @staticmethod
    def normalize_arabic(text: str) -> str:
        if not text:
            return ""
        text = text.strip().lower()
        trans = str.maketrans({
            'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
            'ؤ': 'و', 'ئ': 'ي', 'ء': '',
            'ة': 'ه', 'ى': 'ي'
        })
        text = text.translate(trans)
        text = NameFilter.diacritics_re.sub('', text)
        text = NameFilter.ws_re.sub(' ', text)
        return text

    @classmethod
    def validate_name(cls, name: str) -> Tuple[bool, str]:
        if not name or not name.strip():
            return False, "الاسم لا يمكن أن يكون فارغًا"
        name = name.strip()
        if len(name) > MAX_NAME_LEN:
            return False, f"الاسم طويل جدا (الحد الأقصى {MAX_NAME_LEN} حرفًا)"
        if len(name) < 1:
            return False, "الاسم قصير جدًا"
        normalized = cls.normalize_arabic(name)
        for bad in cls.BAD_WORDS:
            if cls.normalize_arabic(bad) in normalized:
                return False, "الاسم يحتوي على كلمات غير لائقة"
        return True, ""

# ---------- Helpers ----------
def get_source_key(event) -> str:
    """Return a stable key for the source: group_id or room_id or user_id."""
    src = getattr(event, 'source', None)
    if not src:
        return None
    return getattr(src, 'group_id', None) or getattr(src, 'room_id', None) or getattr(src, 'user_id', None)

def _safe_call_reply(request_obj):
    try:
        line_bot_api.reply_message(request_obj)
    except Exception:
        logger.exception("Failed to reply message: %s", request_obj)

def reply_message(reply_token, messages):
    """Wrap reply_message construction for v3 SDK objects."""
    if not isinstance(messages, list):
        messages = [messages]
    try:
        line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=reply_token, messages=messages)
        )
    except Exception:
        logger.exception("Failed to reply message")

def push_message(to, messages):
    if not isinstance(messages, list):
        messages = [messages]
    try:
        line_bot_api.push_message(
            PushMessageRequest(to=to, messages=messages)
        )
    except Exception:
        logger.exception("Failed to push message to %s", to)

def send_next_question_async(target_group):
    try:
        next_q = game_manager.next_question(target_group)
        if next_q:
            push_message(target_group, next_q)
    except Exception:
        logger.exception("Failed to send next question")

BOT_COMMANDS = {
    'بدايه', 'start', 'ابدا', 'بداية', 'مساعده', 'help', 'مساعدة',
    'العاب', 'ألعاب', 'تسجيل', 'تغيير', 'تغيير الاسم', 'انسحب', 'نقاطي',
    'احصائياتي', 'الصداره', 'المتصدرين', 'الصدارة', 'اللاعبين', 'ايقاف',
    'stop', 'إيقاف', 'سؤال', 'سوال', 'تحدي', 'اعتراف', 'منشن', 'توافق',
    'اغنيه', 'لعبه', 'سلسله', 'اسرع', 'ضد', 'تكوين', 'فئه', 'مافيا',
    'لمح', 'تلميح', 'جاوب', 'الجواب', 'الغاء', 'إلغاء', 'انضم مافيا',
    'بدء مافيا', 'شرح مافيا', 'إنهاء الليل', 'تصويت مافيا', 'إنهاء التصويت',
    'حالة مافيا'
}

def is_bot_command(text: str) -> bool:
    if not text:
        return False
    t = text.strip().lower()
    if t in BOT_COMMANDS:
        return True
    # verbs/prefixes like "صوت X" etc.
    for prefix in ('صوت ', 'اقتل ', 'افحص ', 'احمي '):
        if t.startswith(prefix):
            return True
    return False

def check_rate_limit(user_id: str) -> bool:
    """Return True if allowed, False if rate-limited."""
    now = time.time()
    with _user_message_times_lock:
        dq = user_message_times[user_id]
        # remove expired
        while dq and (now - dq[0]) >= RATE_LIMIT_PERIOD:
            dq.popleft()
        if len(dq) >= RATE_LIMIT_MESSAGES:
            return False
        dq.append(now)
    return True

# ---------- Webhook endpoint ----------
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.warning("Invalid signature on incoming request")
        abort(400)
    except Exception:
        logger.exception("Unhandled exception while handling webhook")
        abort(500)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    try:
        # safety checks
        if not getattr(event, 'message', None) or not getattr(event.message, 'text', None):
            logger.debug("Message or text is empty; ignoring")
            return

        text = event.message.text.strip()
        if not text:
            return

        user_id = getattr(event.source, 'user_id', None)
        if not user_id:
            # for group/room events, there might be no user_id; ignore non-identifiable messages
            logger.warning("Event without user_id; ignoring")
            return

        group_key = get_source_key(event)

        # If user withdrawn and not a bot command, ignore
        try:
            if Database.is_user_withdrawn(user_id) and not is_bot_command(text):
                logger.debug("User %s is withdrawn; ignoring non-command message", user_id)
                return
        except Exception:
            logger.exception("Failed to check withdrawn status for user %s", user_id)

        # Rate limiting
        if not check_rate_limit(user_id):
            logger.warning("Rate limit exceeded for user %s", user_id)
            reply_message(event.reply_token, TextMessage(text="لقد تجاوزت الحد الأقصى للرسائل. يرجى المحاولة لاحقًا"))
            return

        # Registration flow
        if user_id in waiting_for_registration:
            if text.lower() in {"انسحب", "إلغاء", "الغاء"}:
                waiting_for_registration.discard(user_id)
                reply_message(event.reply_token, TextMessage(text="تم إلغاء التسجيل"))
                return
            valid, err = NameFilter.validate_name(text)
            if not valid:
                reply_message(event.reply_token, TextMessage(text=f"{err}\n\nاكتب اسم صحيح أو اكتب إلغاء"))
                return
            waiting_for_registration.discard(user_id)
            try:
                Database.register_or_update_user(user_id, text)
                flex = FlexMessage(
                    alt_text="تم التسجيل بنجاح",
                    contents=FlexContainer.from_dict(UIBuilder.registration_success_card(text))
                )
                reply_message(event.reply_token, flex)
            except Exception:
                logger.exception("Failed to register user %s", user_id)
                reply_message(event.reply_token, TextMessage(text="حدث خطأ أثناء التسجيل"))
            return

        # Name change flow
        if user_id in waiting_for_name_change:
            if text.lower() in {"انسحب", "إلغاء", "الغاء"}:
                waiting_for_name_change.discard(user_id)
                reply_message(event.reply_token, TextMessage(text="تم إلغاء تغيير الاسم"))
                return
            valid, err = NameFilter.validate_name(text)
            if not valid:
                reply_message(event.reply_token, TextMessage(text=f"{err}\n\nاكتب اسم صحيح أو اكتب إلغاء"))
                return
            waiting_for_name_change.discard(user_id)
            try:
                Database.register_or_update_user(user_id, text)
                flex = FlexMessage(
                    alt_text="تم تغيير الاسم",
                    contents=FlexContainer.from_dict(UIBuilder.name_changed_card(text))
                )
                reply_message(event.reply_token, flex)
            except Exception:
                logger.exception("Failed to update name for user %s", user_id)
                reply_message(event.reply_token, TextMessage(text="حدث خطأ أثناء تغيير الاسم"))
            return

        # If message is not a bot command, treat as potential game answer
        if not is_bot_command(text):
            game = game_manager.get_game(group_key)
            if game:
                game_type = game_manager.active_games.get(group_key, {}).get('type', '')
                # registration check for certain games
                if game_type not in ['mafia', 'compatibility']:
                    try:
                        if not Database.is_user_registered(user_id):
                            reply_message(event.reply_token, TextMessage(text="يجب التسجيل أولًا للمشاركة في هذه اللعبة"))
                            return
                    except Exception:
                        logger.exception("Failed to check registration for user %s", user_id)
                try:
                    Database.update_last_activity(user_id)
                except Exception:
                    logger.exception("Failed to update last activity for user %s", user_id)
                # get display name
                try:
                    stats = Database.get_user_stats(user_id) or {}
                    display_name = stats.get('display_name', 'مستخدم')
                except Exception:
                    logger.exception("Failed to get stats for user %s", user_id)
                    display_name = 'مستخدم'
                try:
                    result = game_manager.check_answer(group_key, text, user_id, display_name)
                    if result:
                        # update points if awarded and not mafia/compatibility
                        if result.get('correct') and result.get('points', 0) > 0 and game_type not in ['mafia', 'compatibility']:
                            try:
                                Database.update_user_points(user_id, result['points'], result.get('won', False), game_type)
                            except Exception:
                                logger.exception("Failed to update points for user %s", user_id)
                        if result.get('response'):
                            reply_message(event.reply_token, result.get('response'))
                        if result.get('next_question') and not result.get('game_over'):
                            executor.submit(send_next_question_async, group_key)
                        if result.get('game_over'):
                            game_manager.stop_game(group_key)
                except Exception:
                    logger.exception("Error processing game answer for user %s", user_id)
                return

        # Update last activity for regular commands if user is registered
        try:
            if Database.is_user_registered(user_id):
                Database.update_last_activity(user_id)
        except Exception:
            logger.exception("Failed to update last activity for user %s", user_id)

        # Get display name for UI
        try:
            stats = Database.get_user_stats(user_id) or {}
            display_name = stats.get('display_name', 'مستخدم')
        except Exception:
            logger.exception("Failed to get user stats for %s", user_id)
            display_name = 'مستخدم'

        normalized_text = text.strip()

        # ---------- Commands ----------
        if normalized_text.lower() in {"بدايه", "start", "ابدا", "بداية"}:
            flex = FlexMessage(
                alt_text="مرحبا",
                contents=FlexContainer.from_dict(UIBuilder.welcome_card(display_name, Database.is_user_registered(user_id)))
            )
            reply_message(event.reply_token, flex)
            return

        if normalized_text.lower() in {"مساعده", "help", "مساعدة"}:
            flex = FlexMessage(
                alt_text="المساعدة",
                contents=FlexContainer.from_dict(UIBuilder.help_card())
            )
            reply_message(event.reply_token, flex)
            return

        if normalized_text in {"ألعاب", "العاب"}:
            flex = FlexMessage(
                alt_text="قائمة الألعاب",
                contents=FlexContainer.from_dict(UIBuilder.games_menu_card(Database.is_user_registered(user_id)))
            )
            reply_message(event.reply_token, flex)
            return

        if normalized_text == "تسجيل":
            try:
                if Database.is_user_registered(user_id):
                    flex = FlexMessage(
                        alt_text="مسجل بالفعل",
                        contents=FlexContainer.from_dict(UIBuilder.already_registered_card(display_name))
                    )
                    reply_message(event.reply_token, flex)
                else:
                    existing_name = Database.get_existing_user_name(user_id)
                    if existing_name:
                        Database.reactivate_user(user_id)
                        flex = FlexMessage(
                            alt_text="مرحبا بعودتك",
                            contents=FlexContainer.from_dict(UIBuilder.welcome_back_card(existing_name))
                        )
                        reply_message(event.reply_token, flex)
                    else:
                        waiting_for_registration.add(user_id)
                        flex = FlexMessage(
                            alt_text="التسجيل",
                            contents=FlexContainer.from_dict(UIBuilder.registration_card())
                        )
                        reply_message(event.reply_token, flex)
            except Exception:
                logger.exception("Error handling registration for user %s", user_id)
                reply_message(event.reply_token, TextMessage(text="حدث خطأ أثناء معالجة التسجيل"))
            return

        if normalized_text in {"تغيير", "تغيير الاسم"}:
            try:
                if not Database.is_user_registered(user_id):
                    flex = FlexMessage(
                        alt_text="يجب التسجيل أولًا",
                        contents=FlexContainer.from_dict(UIBuilder.need_registration_card())
                    )
                    reply_message(event.reply_token, flex)
                else:
                    waiting_for_name_change.add(user_id)
                    flex = FlexMessage(
                        alt_text="تغيير الاسم",
                        contents=FlexContainer.from_dict(UIBuilder.change_name_card(display_name))
                    )
                    reply_message(event.reply_token, flex)
            except Exception:
                logger.exception("Error handling name change for user %s", user_id)
                reply_message(event.reply_token, TextMessage(text="حدث خطأ أثناء تغيير الاسم"))
            return

        if normalized_text == "انسحب":
            try:
                if not Database.is_user_registered(user_id):
                    reply_message(event.reply_token, TextMessage(text="أنت غير مسجل"))
                else:
                    Database.withdraw_user(user_id)
                    reply_message(event.reply_token, TextMessage(text="تم الانسحاب. لن يتم احتساب إجاباتك بعد الآن"))
            except Exception:
                logger.exception("Error processing withdraw for user %s", user_id)
                reply_message(event.reply_token, TextMessage(text="حدث خطأ أثناء الانسحاب"))
            return

        if normalized_text in {"نقاطي", "احصائياتي"}:
            try:
                if not Database.is_user_registered(user_id):
                    reply_message(event.reply_token, TextMessage(text="يجب التسجيل أولًا"))
                    return
                stats = Database.get_user_stats(user_id)
                flex = FlexMessage(
                    alt_text="إحصائياتك",
                    contents=FlexContainer.from_dict(UIBuilder.stats_card(display_name, stats))
                )
                reply_message(event.reply_token, flex)
            except Exception:
                logger.exception("Error fetching stats for user %s", user_id)
                reply_message(event.reply_token, TextMessage(text="حدث خطأ أثناء جلب الإحصائيات"))
            return

        if normalized_text in {"الصداره", "المتصدرين", "الصدارة"}:
            try:
                leaders = Database.get_leaderboard(20)
                flex = FlexMessage(
                    alt_text="لوحة الصدارة",
                    contents=FlexContainer.from_dict(UIBuilder.leaderboard_card(leaders))
                )
                reply_message(event.reply_token, flex)
            except Exception:
                logger.exception("Error fetching leaderboard")
                reply_message(event.reply_token, TextMessage(text="حدث خطأ أثناء جلب لوحة الصدارة"))
            return

        if normalized_text == "اللاعبين":
            try:
                players = Database.get_all_players()
                flex = FlexMessage(
                    alt_text="جميع اللاعبين",
                    contents=FlexContainer.from_dict(UIBuilder.all_players_card(players))
                )
                reply_message(event.reply_token, flex)
            except Exception:
                logger.exception("Error fetching players")
                reply_message(event.reply_token, TextMessage(text="حدث خطأ أثناء جلب اللاعبين"))
            return

        if normalized_text in {"ايقاف", "stop", "إيقاف"}:
            try:
                stopped = game_manager.stop_game(group_key)
                msg = TextMessage(text="تم إيقاف اللعبة" if stopped else "لا توجد لعبة نشطة")
                reply_message(event.reply_token, msg)
            except Exception:
                logger.exception("Error stopping game for group %s", group_key)
                reply_message(event.reply_token, TextMessage(text="حدث خطأ أثناء محاولة إيقاف اللعبة"))
            return

        # Fun small commands
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

        # Map of user-visible command -> internal game key
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
            # require registration except mafia and compatibility (handled above)
            if normalized_text not in {"مافيا", "توافق"}:
                try:
                    if not Database.is_user_registered(user_id):
                        reply_message(event.reply_token, TextMessage(text="يجب التسجيل أولًا لبدء الألعاب"))
                        return
                except Exception:
                    logger.exception("Error checking registration before starting game for user %s", user_id)
            response = game_manager.start_game(game_commands[normalized_text], group_key)
            if response:
                reply_message(event.reply_token, response)
            return

    except Exception:
        logger.exception("Unhandled error in message handler")

# ---------- Health & index ----------
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'line-bot',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'name': 'Mafia Bot',
        'version': '3.0',
        'status': 'running'
    }), 200

# ---------- Main ----------
if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    logger.info("Starting locally on port %s", port)
    app.run(host='0.0.0.0', port=port, debug=os.getenv("FLASK_DEBUG", "0") == "1")
