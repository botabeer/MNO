from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os
import logging
import atexit
from threading import Lock

from database import Database
from game_engine import GameEngine
from ui_builder import UIBuilder

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# التحقق من المتغيرات البيئية
required_env = ['LINE_CHANNEL_ACCESS_TOKEN', 'LINE_CHANNEL_SECRET']
for var in required_env:
    if not os.getenv(var):
        raise ValueError(f"Missing {var}")

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# تهيئة المكونات
Database.init()
game_engine = GameEngine(line_bot_api)
ui_builder = UIBuilder()

# جدولة تنظيف المستخدمين غير النشطين
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=Database.cleanup_inactive_users,
    trigger="interval",
    hours=24,
    id='cleanup',
    replace_existing=True
)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

def add_quick_reply(message):
    """إضافة أزرار سريعة للرسائل"""
    from linebot.models import QuickReply, QuickReplyButton, MessageAction
    
    quick_reply = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="بداية", text="بداية")),
        QuickReplyButton(action=MessageAction(label="تسجيل", text="تسجيل")),
        QuickReplyButton(action=MessageAction(label="انسحب", text="انسحب")),
        QuickReplyButton(action=MessageAction(label="العاب", text="العاب")),
        QuickReplyButton(action=MessageAction(label="توافق", text="توافق")),
        QuickReplyButton(action=MessageAction(label="سؤال", text="سؤال")),
        QuickReplyButton(action=MessageAction(label="منشن", text="منشن")),
        QuickReplyButton(action=MessageAction(label="تحدي", text="تحدي")),
        QuickReplyButton(action=MessageAction(label="اعتراف", text="اعتراف")),
        QuickReplyButton(action=MessageAction(label="ايقاف", text="ايقاف")),
    ])
    
    if isinstance(message, (TextSendMessage, FlexSendMessage)):
        message.quick_reply = quick_reply
    return message

@app.route("/callback", methods=['POST'])
def callback():
    """معالج Webhook من LINE"""
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature")
        abort(400)
    except Exception as e:
        logger.error(f"Callback error: {e}", exc_info=True)
        abort(500)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """معالج الرسائل الرئيسي"""
    try:
        text = event.message.text.strip()
        user_id = event.source.user_id
        group_id = getattr(event.source, 'group_id', None) or user_id
        
        # تحديث آخر نشاط
        Database.update_last_activity(user_id)
        
        # معالجة الأوامر
        response = process_command(text, user_id, group_id)
        
        if response:
            if isinstance(response, list):
                for msg in response:
                    add_quick_reply(msg)
                line_bot_api.reply_message(event.reply_token, response)
            else:
                line_bot_api.reply_message(event.reply_token, add_quick_reply(response))
    
    except Exception as e:
        logger.error(f"Message handling error: {e}", exc_info=True)
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="حدث خطأ، حاول مرة أخرى")
            )
        except:
            pass

def process_command(text, user_id, group_id):
    """معالجة الأوامر والرسائل"""
    text_normalized = text.lower().strip()
    
    # التحقق من التسجيل
    user_data = Database.get_user_stats(user_id)
    is_registered = user_data is not None
    display_name = user_data['display_name'] if user_data else "مستخدم"
    
    # أوامر أساسية
    if text_normalized in ["بداية", "start", "بدايه"]:
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
    
    # التسجيل
    if text_normalized in ["تسجيل", "تغيير"]:
        return handle_registration(user_id, is_registered, display_name)
    
    # النقاط والإحصائيات
    if text_normalized in ["نقاطي", "احصائياتي"]:
        if not is_registered:
            return TextSendMessage(text="يجب التسجيل أولا\nاكتب: تسجيل")
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
    
    # إيقاف اللعبة
    if text_normalized in ["ايقاف", "stop", "إيقاف"]:
        stopped = game_engine.stop_game(group_id)
        return TextSendMessage(text="تم إيقاف اللعبة" if stopped else "لا توجد لعبة نشطة")
    
    # معالجة الألعاب
    game_response = game_engine.process_message(
        text=text,
        user_id=user_id,
        group_id=group_id,
        display_name=display_name,
        is_registered=is_registered
    )
    
    return game_response

def handle_registration(user_id, is_registered, current_name):
    """معالجة التسجيل"""
    # تخزين حالة انتظار الاسم
    game_engine.set_waiting_for_name(user_id, True)
    
    if is_registered:
        msg = f"أنت مسجل حاليا باسم: {current_name}\n\nأدخل الاسم الجديد:"
    else:
        msg = "أدخل اسمك للتسجيل:"
    
    return TextSendMessage(text=msg)

@app.route('/health', methods=['GET'])
def health_check():
    """فحص صحة الخدمة"""
    return {
        'status': 'healthy',
        'service': 'bot-alhoot',
        'timestamp': datetime.now().isoformat()
    }, 200

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    logger.info(f"Starting Bot Alhoot on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
