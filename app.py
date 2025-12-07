from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest,
    TextMessage, FlexMessage, FlexContainer
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from apscheduler.schedulers.background import BackgroundScheduler
from ui_builder import UIBuilder
from games.game_manager import GameManager
from database import Database
import os, logging, re, atexit, time
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

required_vars = ['LINE_CHANNEL_ACCESS_TOKEN', 'LINE_CHANNEL_SECRET']
for var in required_vars:
    if not os.getenv(var):
        logger.error(f"Missing environment variable: {var}")
        raise ValueError(f"Environment variable {var} is required")

try:
    configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
    handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
    api_client = ApiClient(configuration)
    line_bot_api = MessagingApi(api_client)
    logger.info("LINE Bot API initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize LINE Bot API: {e}")
    raise

try:
    Database.init()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise

game_manager = GameManager(line_bot_api)

scheduler = BackgroundScheduler()
scheduler.add_job(func=Database.cleanup_inactive_users, trigger="interval", hours=24, id='cleanup_users')
try:
    scheduler.start()
    logger.info("Scheduler started successfully")
except Exception as e:
    logger.error(f"Failed to start scheduler: {e}")

atexit.register(lambda: scheduler.shutdown())

waiting_for_registration = {}
waiting_for_name_change = {}
user_message_times = {}
RATE_LIMIT_MESSAGES = 50
RATE_LIMIT_PERIOD = 3600

def check_rate_limit(user_id):
    current_time = time.time()
    if user_id not in user_message_times:
        user_message_times[user_id] = []
    user_message_times[user_id] = [t for t in user_message_times[user_id] if current_time - t < RATE_LIMIT_PERIOD]
    if len(user_message_times[user_id]) >= RATE_LIMIT_MESSAGES:
        return False
    user_message_times[user_id].append(current_time)
    return True

BOT_COMMANDS = [
    'بدايه', 'start', 'ابدا', 'بداية', 'مساعده', 'help', 'مساعدة', 'العاب', 'ألعاب',
    'تسجيل', 'تغيير', 'تغيير الاسم', 'انسحب', 'نقاطي', 'احصائياتي', 'الصداره',
    'المتصدرين', 'الصدارة', 'اللاعبين', 'ايقاف', 'stop', 'إيقاف', 'سؤال', 'سوال',
    'تحدي', 'اعتراف', 'منشن', 'توافق', 'اغنيه', 'لعبه', 'سلسله', 'اسرع', 'ضد',
    'تكوين', 'فئه', 'مافيا', 'لمح', 'تلميح', 'جاوب', 'الجواب', 'الغاء', 'إلغاء',
    'انضم مافيا', 'بدء مافيا', 'شرح مافيا', 'إنهاء الليل', 'تصويت مافيا', 'إنهاء التصويت'
]

class NameFilter:
    @staticmethod
    def get_bad_words():
        return ['غبي', 'احمق', 'حمار', 'كلب', 'خنزير', 'قذر', 'وسخ', 'حقير', 'نذل', 'خائن', 'كذاب', 'لعين', 'ملعون']
    
    @staticmethod
    def normalize_arabic(text):
        if not text:
            return ""
        text = text.lower().strip()
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '')
        text = text.replace('ة', 'ه').replace('ى', 'ي')
        text = re.sub(r'[\u064B-\u065F]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text
    
    @staticmethod
    def validate_name(name):
        if not name or name.strip() == "":
            return False, "الاسم لا يمكن ان يكون فارغا"
        name = name.strip()
        if len(name) > 30:
            return False, "الاسم طويل جدا (الحد الاقصى 30 حرف)"
        if len(name) < 1:
            return False, "الاسم قصير جدا (الحد الأدنى حرف واحد)"
        normalized_name = NameFilter.normalize_arabic(name)
        for bad_word in NameFilter.get_bad_words():
            normalized_bad = NameFilter.normalize_arabic(bad_word)
            if normalized_bad in normalized_name:
                return False, "الاسم يحتوي على كلمات غير لائقة"
        return True, ""

def is_bot_command(text):
    text_lower = text.lower()
    for cmd in BOT_COMMANDS:
        if text_lower == cmd.lower():
            return True
    if text_lower.startswith(('صوت ', 'اقتل ', 'افحص ', 'احمي ')):
        return True
    return False

def is_user_registered(user_id):
    return Database.is_user_registered(user_id)

def is_user_withdrawn(user_id):
    return Database.is_user_withdrawn(user_id)

def get_user_display_name(user_id):
    stats = Database.get_user_stats(user_id)
    if stats and stats.get('display_name'):
        return stats['display_name']
    return None

def reply_message(reply_token, messages):
    try:
        if not isinstance(messages, list):
            messages = [messages]
        line_bot_api.reply_message(ReplyMessageRequest(reply_token=reply_token, messages=messages))
    except Exception as e:
        logger.error(f"Error sending reply: {e}")

def push_message(to, messages):
    try:
        if not isinstance(messages, list):
            messages = [messages]
        line_bot_api.push_message(PushMessageRequest(to=to, messages=messages))
    except Exception as e:
        logger.error(f"Error sending push message: {e}")

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature")
        abort(400)
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        abort(500)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    try:
        text = event.message.text.strip()
        user_id = event.source.user_id
        group_id = getattr(event.source, 'group_id', None) or user_id
        
        if is_user_withdrawn(user_id) and not is_bot_command(text):
            return
        
        if not check_rate_limit(user_id):
            logger.warning(f"Rate limit exceeded for user: {user_id}")
            msg = TextMessage(text="لقد تجاوزت الحد الأقصى للرسائل. انتظر قليلاً")
            reply_message(event.reply_token, msg)
            return
        
        if user_id in waiting_for_registration:
            if text.lower() in ["انسحب", "إلغاء", "الغاء"]:
                del waiting_for_registration[user_id]
                msg = TextMessage(text="تم الغاء التسجيل")
                reply_message(event.reply_token, msg)
                return
            is_valid, error_msg = NameFilter.validate_name(text)
            if not is_valid:
                msg = TextMessage(text=f"{error_msg}\n\nاكتب اسم صحيح او اكتب الغاء")
                reply_message(event.reply_token, msg)
                return
            del waiting_for_registration[user_id]
            Database.register_or_update_user(user_id, text)
            flex = FlexMessage(alt_text="تم التسجيل بنجاح", contents=FlexContainer.from_dict(UIBuilder.registration_success_card(text)))
            reply_message(event.reply_token, flex)
            return
        
        if user_id in waiting_for_name_change:
            if text.lower() in ["انسحب", "إلغاء", "الغاء"]:
                del waiting_for_name_change[user_id]
                msg = TextMessage(text="تم الغاء تغيير الاسم")
                reply_message(event.reply_token, msg)
                return
            is_valid, error_msg = NameFilter.validate_name(text)
            if not is_valid:
                msg = TextMessage(text=f"{error_msg}\n\nاكتب اسم صحيح او اكتب الغاء")
                reply_message(event.reply_token, msg)
                return
            del waiting_for_name_change[user_id]
            Database.register_or_update_user(user_id, text)
            flex = FlexMessage(alt_text="تم تغيير الاسم", contents=FlexContainer.from_dict(UIBuilder.name_changed_card(text)))
            reply_message(event.reply_token, flex)
            return

        if not is_bot_command(text):
            game = game_manager.get_game(group_id)
            if game:
                game_type = game_manager.active_games.get(group_id, {}).get('type', '')
                if game_type not in ['mafia', 'compatibility'] and not is_user_registered(user_id):
                    return
                try:
                    Database.update_last_activity(user_id)
                except:
                    pass
                display_name = get_user_display_name(user_id) or "مستخدم"
                result = game_manager.check_answer(group_id, text, user_id, display_name)
                if result:
                    if result.get('correct') and result.get('points', 0) > 0 and game_type not in ['mafia', 'compatibility']:
                        if is_user_registered(user_id):
                            Database.update_user_points(user_id, result['points'], result.get('won', False), game_type)
                    response = result.get('response')
                    if response:
                        reply_message(event.reply_token, response)
                    if result.get('next_question') and not result.get('game_over'):
                        time.sleep(2)
                        next_q = game_manager.next_question(group_id)
                        if next_q:
                            try:
                                push_message(group_id, next_q)
                            except Exception as e:
                                logger.error(f"Error sending next question: {e}")
                    if result.get('game_over'):
                        game_manager.stop_game(group_id)
                return

        try:
            if is_user_registered(user_id):
                Database.update_last_activity(user_id)
        except:
            pass

        display_name = get_user_display_name(user_id) or "مستخدم"

        if text.lower() in ["بدايه", "start", "ابدا", "بداية"]:
            flex = FlexMessage(alt_text="مرحبا", contents=FlexContainer.from_dict(UIBuilder.welcome_card(display_name, is_user_registered(user_id))))
            reply_message(event.reply_token, flex)
            return

        if text.lower() in ["مساعده", "help", "مساعدة"]:
            flex = FlexMessage(alt_text="المساعده", contents=FlexContainer.from_dict(UIBuilder.help_card()))
            reply_message(event.reply_token, flex)
            return

        if text in ["ألعاب", "العاب"]:
            flex = FlexMessage(alt_text="قائمة الألعاب", contents=FlexContainer.from_dict(UIBuilder.games_menu_card(is_user_registered(user_id))))
            reply_message(event.reply_token, flex)
            return

        if text == "تسجيل":
            if is_user_registered(user_id):
                flex = FlexMessage(alt_text="مسجل بالفعل", contents=FlexContainer.from_dict(UIBuilder.already_registered_card(display_name)))
                reply_message(event.reply_token, flex)
            else:
                existing_name = Database.get_existing_user_name(user_id)
                if existing_name:
                    Database.reactivate_user(user_id)
                    flex = FlexMessage(alt_text="مرحباً بعودتك", contents=FlexContainer.from_dict(UIBuilder.welcome_back_card(existing_name)))
                    reply_message(event.reply_token, flex)
                else:
                    waiting_for_registration[user_id] = True
                    flex = FlexMessage(alt_text="التسجيل", contents=FlexContainer.from_dict(UIBuilder.registration_card()))
                    reply_message(event.reply_token, flex)
            return

        if text in ["تغيير", "تغيير الاسم"]:
            if not is_user_registered(user_id):
                flex = FlexMessage(alt_text="يجب التسجيل أولاً", contents=FlexContainer.from_dict(UIBuilder.need_registration_card()))
                reply_message(event.reply_token, flex)
            else:
                waiting_for_name_change[user_id] = True
                flex = FlexMessage(alt_text="تغيير الاسم", contents=FlexContainer.from_dict(UIBuilder.change_name_card(display_name)))
                reply_message(event.reply_token, flex)
            return

        if text == "انسحب":
            if not is_user_registered(user_id):
                msg = TextMessage(text="انت غير مسجل")
            else:
                Database.withdraw_user(user_id)
                msg = TextMessage(text="تم الانسحاب. لن يتم احتساب اجاباتك بعد الآن")
            reply_message(event.reply_token, msg)
            return

        if text in ["نقاطي", "احصائياتي"]:
            if not is_user_registered(user_id):
                msg = TextMessage(text="يجب التسجيل اولا")
                reply_message(event.reply_token, msg)
                return
            stats = Database.get_user_stats(user_id)
            flex = FlexMessage(alt_text="احصائياتك", contents=FlexContainer.from_dict(UIBuilder.stats_card(display_name, stats)))
            reply_message(event.reply_token, flex)
            return

        if text in ["الصداره", "المتصدرين", "الصدارة"]:
            leaders = Database.get_leaderboard(20)
            flex = FlexMessage(alt_text="لوحه الصداره", contents=FlexContainer.from_dict(UIBuilder.leaderboard_card(leaders)))
            reply_message(event.reply_token, flex)
            return
        
        if text == "اللاعبين":
            players = Database.get_all_players()
            flex = FlexMessage(alt_text="جميع اللاعبين", contents=FlexContainer.from_dict(UIBuilder.all_players_card(players)))
            reply_message(event.reply_token, flex)
            return

        if text in ["ايقاف", "stop", "إيقاف"]:
            stopped = game_manager.stop_game(group_id)
            msg = TextMessage(text="تم ايقاف اللعبه" if stopped else "لا توجد لعبه نشطه")
            reply_message(event.reply_token, msg)
            return

        if text in ["سؤال", "سوال"]:
            msg = TextMessage(text=game_manager.get_random_question())
            reply_message(event.reply_token, msg)
            return
        
        if text == "تحدي":
            msg = TextMessage(text=game_manager.get_random_challenge())
            reply_message(event.reply_token, msg)
            return
        
        if text == "اعتراف":
            msg = TextMessage(text=game_manager.get_random_confession())
            reply_message(event.reply_token, msg)
            return
        
        if text.startswith("منشن"):
            msg = TextMessage(text=game_manager.get_random_mention())
            reply_message(event.reply_token, msg)
            return
        
        if text == "توافق":
            response = game_manager.start_game("compatibility", group_id)
            reply_message(event.reply_token, response)
            return

        game_commands = {"اغنيه": "song", "لعبه": "human_animal", "سلسله": "chain", "اسرع": "fast_typing", "ضد": "opposite", "تكوين": "letters", "فئه": "category", "مافيا": "mafia"}

        if text in game_commands:
            if text not in ["مافيا", "توافق"] and not is_user_registered(user_id):
                msg = TextMessage(text="يجب التسجيل اولا لبدء الالعاب")
                reply_message(event.reply_token, msg)
                return
            response = game_manager.start_game(game_commands[text], group_id)
            if response:
                reply_message(event.reply_token, response)
            return
    except AttributeError as e:
        logger.error(f"Message structure error: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)

@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy', 'service': 'line-bot', 'timestamp': datetime.now().isoformat()}, 200

@app.route('/', methods=['GET'])
def index():
    return {'name': 'Mafia Bot', 'version': '2.0', 'status': 'running'}, 200

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    logger.info(f"Starting application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
