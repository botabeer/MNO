from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
import logging
import atexit
import sys

from database import Database
from game_manager import GameManager
from ui_builder import UIBuilder

# ------------------------
# Logging Configuration
# ------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ------------------------
# Flask App
# ------------------------
app = Flask(__name__)

# ------------------------
# Environment Variables
# ------------------------
required_env = ['LINE_CHANNEL_ACCESS_TOKEN', 'LINE_CHANNEL_SECRET']
for var in required_env:
    if not os.getenv(var):
        raise ValueError(f"Missing {var}")

ENV_MODE = os.getenv('ENV_MODE', 'dev').lower()  # dev / prod
DEBUG_MODE = ENV_MODE == 'dev'

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# ------------------------
# Initialize DB and Game Manager
# ------------------------
Database.init()
game_manager = GameManager(line_bot_api)
ui_builder = UIBuilder()

# ------------------------
# Scheduler Jobs
# ------------------------
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=Database.cleanup_inactive_users,
    trigger="interval",
    hours=24,
    id='cleanup',
    replace_existing=True
)
scheduler.add_job(
    func=lambda: game_manager.cleanup_inactive_games(30),
    trigger="interval",
    minutes=15,
    id='game_cleanup',
    replace_existing=True
)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# ------------------------
# Quick Reply Helper
# ------------------------
def add_quick_reply(message):
    from linebot.models import QuickReply, QuickReplyButton, MessageAction
    
    quick_reply = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="بداية", text="بداية")),
        QuickReplyButton(action=MessageAction(label="العاب", text="العاب")),
        QuickReplyButton(action=MessageAction(label="نقاطي", text="نقاطي")),
        QuickReplyButton(action=MessageAction(label="الصدارة", text="الصدارة")),
        QuickReplyButton(action=MessageAction(label="ايقاف", text="ايقاف"))
    ])
    
    if isinstance(message, (TextSendMessage, FlexSendMessage)):
        message.quick_reply = quick_reply
    return message

# ------------------------
# Webhook Endpoint
# ------------------------
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    logger.info(f"Received webhook: {body}")
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.warning("Invalid signature. Aborting request.")
        abort(400)
    except Exception as e:
        logger.error(f"Exception in webhook handling: {e}", exc_info=True)
        abort(500)
    
    return 'OK', 200

# ------------------------
# Message Handler
# ------------------------
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()
    group_id = getattr(event.source, 'group_id', None) or user_id
    
    logger.info(f"Message from {user_id} (group {group_id}): {text}")
    
    try:
        response = process_command(text, user_id, group_id)
        if response:
            if isinstance(response, list):
                for msg in response:
                    add_quick_reply(msg)
                line_bot_api.reply_message(event.reply_token, response)
            else:
                line_bot_api.reply_message(event.reply_token, add_quick_reply(response))
    except LineBotApiError as e:
        logger.error(f"LINE API Error: {e.status_code} {e.message}", exc_info=True)
    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)

# ------------------------
# Command Processing
# ------------------------
def process_command(text, user_id, group_id):
    text_normalized = text.lower().strip()
    user_data = Database.get_user_stats(user_id)
    is_registered = user_data is not None
    display_name = user_data['display_name'] if user_data else "مستخدم"
    
    if text_normalized in ["بداية", "start", "بدايه"]:
        Database.update_last_activity(user_id)
        return FlexSendMessage(
            alt_text="بوت الحوت",
            contents=ui_builder.welcome_card(display_name, is_registered)
        )
    
    if text_normalized in ["مساعدة", "help", "مساعده"]:
        return FlexSendMessage(
            alt_text="المساعدة",
            contents=ui_builder.help_card()
        )
    
    if text in ["العاب", "ألعاب"]:
        return FlexSendMessage(
            alt_text="قائمة الالعاب",
            contents=ui_builder.games_menu_card()
        )
    
    if text_normalized in ["تسجيل", "تغيير"]:
        game_manager.set_waiting_for_name(user_id, True)
        if is_registered:
            msg = f"انت مسجل حاليا باسم: {display_name}\n\nادخل الاسم الجديد:"
        else:
            msg = "ادخل اسمك للتسجيل:"
        return TextSendMessage(text=msg)
    
    if game_manager.is_waiting_for_name(user_id):
        name = text.strip()
        if len(name) < 2 or len(name) > 50:
            return TextSendMessage(text="الاسم غير صالح. يجب أن يكون بين حرفين و50 حرف.")
        success = Database.register_or_update_user(user_id, name)
        game_manager.set_waiting_for_name(user_id, False)
        if success:
            return TextSendMessage(text=f"تم التسجيل باسم: {name}")
        return TextSendMessage(text="حدث خطأ أثناء التسجيل.")

    if text_normalized in ["نقاطي", "احصائياتي"]:
        if not is_registered:
            return TextSendMessage(text="يجب التسجيل أولاً.")
        Database.update_last_activity(user_id)
        return FlexSendMessage(
            alt_text="احصائياتك",
            contents=ui_builder.stats_card(display_name, user_data)
        )

    if text_normalized in ["الصدارة", "المتصدرين", "الصداره"]:
        leaders = Database.get_leaderboard(20)
        return FlexSendMessage(
            alt_text="لوحة الصدارة",
            contents=ui_builder.leaderboard_card(leaders)
        )

    if text_normalized in ["ايقاف", "stop", "إيقاف", "انسحب", "انسحاب"]:
        stopped = game_manager.stop_game(group_id)
        if stopped:
            game_manager.add_withdrawn_user(group_id, user_id)
            return TextSendMessage(text="تم ايقاف اللعبة")
        return TextSendMessage(text="لا توجد لعبة نشطة لإيقافها.")

    game_response = game_manager.process_message(
        text=text,
        user_id=user_id,
        group_id=group_id,
        display_name=display_name,
        is_registered=is_registered
    )
    
    if game_response is None:
        return TextSendMessage(text="لا يمكن التعرف على الأمر. اكتب 'مساعدة' للمزيد.")
    
    return game_response

# ------------------------
# Health Check
# ------------------------
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'env_mode': ENV_MODE
    }), 200

# ------------------------
# Index
# ------------------------
@app.route('/', methods=['GET'])
def index():
    return f"Bot Alhoot ({ENV_MODE})", 200

# ------------------------
# Run App
# ------------------------
if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))

    if DEBUG_MODE:
        # ------------------------
        # Ngrok Tunnel for Dev
        # ------------------------
        try:
            from pyngrok import ngrok
            public_url = ngrok.connect(port).public_url
            logger.info(f" * Ngrok tunnel: {public_url}/callback")
            print(f" * Ngrok tunnel: {public_url}/callback")
        except ImportError:
            logger.warning("pyngrok not installed. Run 'pip install pyngrok' to use ngrok tunnel.")

    app.run(host='0.0.0.0', port=port, debug=DEBUG_MODE)
