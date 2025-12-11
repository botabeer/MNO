from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from ui_builder import UIBuilder
from games.game_manager import GameManager
from database import Database
from rate_limiter import RateLimiter
from session_manager import SessionManager
import os
import logging
import atexit

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

required_env_vars = ['LINE_CHANNEL_ACCESS_TOKEN', 'LINE_CHANNEL_SECRET']
for var in required_env_vars:
    if not os.getenv(var):
        logger.error(f"Missing required environment variable: {var}")
        raise ValueError(f"Environment variable {var} is required")

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

Database.init()
game_manager = GameManager(line_bot_api)
rate_limiter = RateLimiter()
session_manager = SessionManager()

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=Database.cleanup_inactive_users,
    trigger="interval",
    hours=24,
    id='cleanup_users',
    replace_existing=True
)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

def add_quick_reply(message):
    from linebot.models import QuickReply, QuickReplyButton, MessageAction
    quick_reply = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="العاب", text="العاب")),
        QuickReplyButton(action=MessageAction(label="اغنيه", text="اغنيه")),
        QuickReplyButton(action=MessageAction(label="ضد", text="ضد")),
        QuickReplyButton(action=MessageAction(label="سلسله", text="سلسله")),
        QuickReplyButton(action=MessageAction(label="اسرع", text="اسرع")),
        QuickReplyButton(action=MessageAction(label="لعبه", text="لعبه")),
        QuickReplyButton(action=MessageAction(label="تكوين", text="تكوين")),
        QuickReplyButton(action=MessageAction(label="فئه", text="فئه")),
        QuickReplyButton(action=MessageAction(label="سؤال", text="سؤال")),
        QuickReplyButton(action=MessageAction(label="تحدي", text="تحدي")),
        QuickReplyButton(action=MessageAction(label="اعتراف", text="اعتراف")),
        QuickReplyButton(action=MessageAction(label="منشن", text="منشن")),
        QuickReplyButton(action=MessageAction(label="توافق", text="توافق"))
    ])
    if isinstance(message, (TextSendMessage, FlexSendMessage)):
        message.quick_reply = quick_reply
    return message

def send_next_question_delayed(group_id, delay=1):
    def send_question():
        next_q = game_manager.next_question(group_id)
        if next_q:
            try:
                line_bot_api.push_message(group_id, add_quick_reply(next_q))
            except Exception as e:
                logger.error(f"Error sending next question: {e}")
    
    scheduler.add_job(
        func=send_question,
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=delay),
        id=f'next_question_{group_id}_{datetime.now().timestamp()}',
        replace_existing=False
    )

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature received")
        abort(400)
    except Exception as e:
        logger.error(f"Error processing callback: {e}", exc_info=True)
        abort(500)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        text = event.message.text.strip()
        user_id = event.source.user_id
        group_id = getattr(event.source, 'group_id', None) or user_id
        
        if not rate_limiter.is_allowed(user_id):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="لقد تجاوزت الحد المسموح من الرسائل، حاول لاحقاً")
            )
            return
        
        Database.update_last_activity(user_id)
        
        if session_manager.is_waiting_for_name(user_id):
            handle_name_input(event, text, user_id, group_id)
            return
        
        if session_manager.is_user_withdrawn(group_id, user_id):
            return
        
        display_name = session_manager.get_user_display_name(group_id, user_id) or "مستخدم"
        
        if handle_basic_commands(event, text, user_id, group_id, display_name):
            return
        
        if handle_game_commands(event, text, user_id, group_id, display_name):
            return
        
        handle_game_answers(event, text, user_id, group_id, display_name)
    
    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="حدث خطأ، الرجاء المحاولة مرة أخرى")
            )
        except:
            pass

def handle_name_input(event, text, user_id, group_id):
    from utils import is_valid_name
    
    if is_valid_name(text):
        display_name = text.strip()
        session_manager.register_user(group_id, user_id, display_name)
        session_manager.set_waiting_for_name(user_id, False)
        
        msg = add_quick_reply(TextSendMessage(
            text=f"تم التسجيل بنجاح\nاسمك: {display_name}\nيمكنك الآن اللعب وجمع النقاط"
        ))
    else:
        msg = add_quick_reply(TextSendMessage(
            text="الاسم غير صالح\nيرجى إدخال اسم صحيح (1-50 حرف)"
        ))
    
    line_bot_api.reply_message(event.reply_token, msg)

def handle_basic_commands(event, text, user_id, group_id, display_name):
    text_lower = text.lower()
    
    if text_lower in ["بدايه", "start", "ابدا", "بداية"]:
        flex = FlexSendMessage(
            alt_text="مرحبا",
            contents=UIBuilder.welcome_card(display_name, session_manager.is_user_registered(group_id, user_id))
        )
        line_bot_api.reply_message(event.reply_token, add_quick_reply(flex))
        return True
    
    if text_lower in ["مساعده", "help", "مساعدة"]:
        flex = FlexSendMessage(
            alt_text="المساعدة",
            contents=UIBuilder.help_card()
        )
        line_bot_api.reply_message(event.reply_token, add_quick_reply(flex))
        return True
    
    if text in ["ألعاب", "العاب"]:
        flex = FlexSendMessage(
            alt_text="قائمة الالعاب",
            contents=UIBuilder.games_menu_card(session_manager.is_user_registered(group_id, user_id))
        )
        line_bot_api.reply_message(event.reply_token, add_quick_reply(flex))
        return True
    
    if text in ["تسجيل", "تغيير"]:
        session_manager.set_waiting_for_name(user_id, True)
        
        if session_manager.is_user_registered(group_id, user_id):
            msg_text = f"أنت مسجل حالياً باسم: {display_name}\nأدخل الاسم الجديد"
        else:
            msg_text = "التسجيل\nأدخل الاسم الذي تريد استخدامه"
        
        msg = add_quick_reply(TextSendMessage(text=msg_text))
        line_bot_api.reply_message(event.reply_token, msg)
        return True
    
    if text == "انسحب":
        if session_manager.withdraw_user(group_id, user_id):
            msg_text = "تم انسحابك من هذه الجلسة\nنقاطك محفوظة ويمكنك العودة في أي وقت"
        else:
            msg_text = "أنت غير مسجل"
        
        msg = add_quick_reply(TextSendMessage(text=msg_text))
        line_bot_api.reply_message(event.reply_token, msg)
        return True
    
    if text in ["نقاطي", "احصائياتي"]:
        stats = Database.get_user_stats(user_id)
        if not stats:
            msg = add_quick_reply(TextSendMessage(
                text="يجب التسجيل أولاً\nاكتب: تسجيل"
            ))
            line_bot_api.reply_message(event.reply_token, msg)
            return True
        
        flex = FlexSendMessage(
            alt_text="احصائياتك",
            contents=UIBuilder.stats_card(display_name, stats)
        )
        line_bot_api.reply_message(event.reply_token, add_quick_reply(flex))
        return True
    
    if text in ["الصداره", "المتصدرين", "الصدارة"]:
        leaders = Database.get_leaderboard(20)
        flex = FlexSendMessage(
            alt_text="لوحة الصدارة",
            contents=UIBuilder.leaderboard_card(leaders)
        )
        line_bot_api.reply_message(event.reply_token, add_quick_reply(flex))
        return True
    
    if text_lower in ["ايقاف", "stop", "إيقاف"]:
        stopped = game_manager.stop_game(group_id)
        msg_text = "تم إيقاف اللعبة" if stopped else "لا توجد لعبة نشطة"
        msg = add_quick_reply(TextSendMessage(text=msg_text))
        line_bot_api.reply_message(event.reply_token, msg)
        return True
    
    return False

def handle_game_commands(event, text, user_id, group_id, display_name):
    if text in ["سؤال", "سوال"]:
        msg = add_quick_reply(TextSendMessage(
            text=game_manager.get_random_question()
        ))
        line_bot_api.reply_message(event.reply_token, msg)
        return True
    
    if text == "تحدي":
        msg = add_quick_reply(TextSendMessage(
            text=game_manager.get_random_challenge()
        ))
        line_bot_api.reply_message(event.reply_token, msg)
        return True
    
    if text == "اعتراف":
        msg = add_quick_reply(TextSendMessage(
            text=game_manager.get_random_confession()
        ))
        line_bot_api.reply_message(event.reply_token, msg)
        return True
    
    if text.startswith("منشن") or text == "منشن":
        msg = add_quick_reply(TextSendMessage(
            text=game_manager.get_random_mention()
        ))
        line_bot_api.reply_message(event.reply_token, msg)
        return True
    
    if text == "توافق":
        response = game_manager.start_game("compatibility", group_id)
        line_bot_api.reply_message(event.reply_token, add_quick_reply(response))
        return True
    
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
    
    if text in game_commands:
        if not session_manager.is_user_registered(group_id, user_id) and text not in ["مافيا", "توافق"]:
            msg = add_quick_reply(TextSendMessage(
                text="يجب التسجيل أولاً للعب هذه اللعبة\nاكتب: تسجيل"
            ))
            line_bot_api.reply_message(event.reply_token, msg)
            return True
        
        response = game_manager.start_game(game_commands[text], group_id)
        if response:
            line_bot_api.reply_message(event.reply_token, add_quick_reply(response))
        return True
    
    return False

def handle_game_answers(event, text, user_id, group_id, display_name):
    game = game_manager.get_game(group_id)
    if not game:
        return
    
    if not session_manager.is_user_registered(group_id, user_id):
        return
    
    result = game_manager.check_answer(group_id, text, user_id, display_name)
    if not result:
        return
    
    if result.get('correct') and result.get('points', 0) > 0:
        Database.update_user_points(
            user_id,
            result['points'],
            result.get('won', False),
            game_manager.active_games.get(group_id, {}).get('type', 'unknown')
        )
    
    response = result.get('response')
    if response:
        if isinstance(response, list):
            for r in response:
                add_quick_reply(r)
            line_bot_api.reply_message(event.reply_token, response)
        else:
            line_bot_api.reply_message(event.reply_token, add_quick_reply(response))
    
    if result.get('correct') and result.get('next_question') and not result.get('game_over'):
        send_next_question_delayed(group_id, delay=1)
    
    if result.get('game_over'):
        game_manager.stop_game(group_id)

@app.route('/health', methods=['GET'])
def health_check():
    return {
        'status': 'healthy',
        'service': 'line-bot',
        'timestamp': datetime.now().isoformat()
    }, 200

@app.errorhandler(404)
def not_found(error):
    return {'error': 'Not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return {'error': 'Internal server error'}, 500

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    
    logger.info(f"Starting bot on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
