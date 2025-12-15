from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
import logging
import atexit
import sys

from database import Database
from game_manager import GameManager
from ui_builder import UIBuilder

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

required_env = ['LINE_CHANNEL_ACCESS_TOKEN', 'LINE_CHANNEL_SECRET']
for var in required_env:
    if not os.getenv(var):
        raise ValueError(f"Missing {var}")

ENV_MODE = os.getenv('ENV_MODE', 'dev').lower()
DEBUG_MODE = ENV_MODE == 'dev'

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

Database.init()
game_manager = GameManager(line_bot_api)
ui_builder = UIBuilder()

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

COMMANDS = {
    'بداية', 'start', 'بدايه',
    'مساعدة', 'help', 'مساعده',
    'العاب', 'ألعاب',
    'تسجيل', 'تغيير',
    'نقاطي', 'احصائياتي',
    'الصدارة', 'المتصدرين', 'الصداره',
    'ايقاف', 'stop', 'إيقاف', 'انسحب', 'انسحاب',
    'اغنيه', 'ضد', 'سلسله', 'اسرع', 'لعبه', 'تكوين', 'فئه', 'توافق'
}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.warning("Invalid signature")
        abort(400)
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
    
    return 'OK', 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()
    group_id = getattr(event.source, 'group_id', None) or user_id
    
    try:
        response = process_command(text, user_id, group_id, event)
        if response:
            if isinstance(response, list):
                line_bot_api.reply_message(event.reply_token, response)
            else:
                line_bot_api.reply_message(event.reply_token, response)
    except LineBotApiError as e:
        logger.error(f"LINE API Error: {e.status_code}", exc_info=True)
    except Exception as e:
        logger.error(f"Message handling error: {e}", exc_info=True)

def process_command(text, user_id, group_id, event):
    text_normalized = text.lower().strip()
    user_data = Database.get_user_stats(user_id)
    is_registered = user_data is not None
    display_name = user_data['display_name'] if user_data else None
    
    if text_normalized not in COMMANDS:
        if game_manager.is_waiting_for_name(user_id):
            name = text.strip()
            if 2 <= len(name) <= 50:
                Database.register_or_update_user(user_id, name)
                game_manager.set_waiting_for_name(user_id, False)
                return None
            game_manager.set_waiting_for_name(user_id, False)
            return None
        
        if group_id in game_manager.active_games:
            if not is_registered:
                return None
            
            game_response = game_manager.process_message(
                text=text,
                user_id=user_id,
                group_id=group_id,
                display_name=display_name,
                is_registered=is_registered
            )
            return game_response
        
        return None
    
    if text_normalized in ['بداية', 'start', 'بدايه']:
        Database.update_last_activity(user_id)
        from linebot.models import FlexSendMessage
        return FlexSendMessage(
            alt_text="بوت الحوت",
            contents=ui_builder.welcome_card(display_name or "مستخدم", is_registered)
        )
    
    if text_normalized in ['مساعدة', 'help', 'مساعده']:
        from linebot.models import FlexSendMessage
        return FlexSendMessage(
            alt_text="المساعدة",
            contents=ui_builder.help_card()
        )
    
    if text in ['العاب', 'ألعاب']:
        from linebot.models import FlexSendMessage
        return FlexSendMessage(
            alt_text="قائمة الالعاب",
            contents=ui_builder.games_menu_card()
        )
    
    if text_normalized in ['تسجيل', 'تغيير']:
        game_manager.set_waiting_for_name(user_id, True)
        return None
    
    if text_normalized in ['نقاطي', 'احصائياتي']:
        if not is_registered:
            return None
        Database.update_last_activity(user_id)
        from linebot.models import FlexSendMessage
        return FlexSendMessage(
            alt_text="احصائياتك",
            contents=ui_builder.stats_card(display_name, user_data)
        )
    
    if text_normalized in ['الصدارة', 'المتصدرين', 'الصداره']:
        leaders = Database.get_leaderboard(20)
        from linebot.models import FlexSendMessage
        return FlexSendMessage(
            alt_text="لوحة الصدارة",
            contents=ui_builder.leaderboard_card(leaders)
        )
    
    if text_normalized in ['ايقاف', 'stop', 'إيقاف', 'انسحب', 'انسحاب']:
        game_manager.stop_game(group_id)
        return None
    
    if text_normalized in ['اغنيه', 'ضد', 'سلسله', 'اسرع', 'لعبه', 'تكوين', 'فئه', 'توافق']:
        if not is_registered:
            return None
        
        game_response = game_manager.process_message(
            text=text,
            user_id=user_id,
            group_id=group_id,
            display_name=display_name,
            is_registered=is_registered
        )
        return game_response
    
    return None

@app.route('/health', methods=['GET'])
def health_check():
    from flask import jsonify
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'env_mode': ENV_MODE
    }), 200

@app.route('/', methods=['GET'])
def index():
    return f"Bot Alhoot ({ENV_MODE})", 200

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    
    if DEBUG_MODE:
        try:
            from pyngrok import ngrok
            public_url = ngrok.connect(port).public_url
            logger.info(f"Ngrok tunnel: {public_url}/callback")
        except ImportError:
            logger.warning("pyngrok not installed")
    
    app.run(host='0.0.0.0', port=port, debug=DEBUG_MODE)
