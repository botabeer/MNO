from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, QuickReply, QuickReplyButton, MessageAction
from apscheduler.schedulers.background import BackgroundScheduler
from ui_builder import UIBuilder
from games.game_manager import GameManager
from database import Database
import os
import logging
import re
import atexit
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

required_env_vars = ['LINE_CHANNEL_ACCESS_TOKEN', 'LINE_CHANNEL_SECRET']
for var in required_env_vars:
    if not os.getenv(var):
        logger.error(f"متغير البيئة {var} غير موجود")
        raise ValueError(f"متغير البيئة {var} مطلوب")

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

Database.init()
game_manager = GameManager(line_bot_api)

scheduler = BackgroundScheduler()
scheduler.add_job(func=Database.cleanup_inactive_users, trigger="interval", hours=24)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

group_registered_users = {}
withdrawn_users = {}
waiting_for_name = {}

def is_user_registered(group_id, user_id):
    return group_id in group_registered_users and user_id in group_registered_users[group_id]

def is_user_withdrawn(group_id, user_id):
    return group_id in withdrawn_users and user_id in withdrawn_users[group_id]

def register_user(group_id, user_id, display_name):
    if group_id not in group_registered_users:
        group_registered_users[group_id] = {}
    group_registered_users[group_id][user_id] = display_name
    if group_id in withdrawn_users and user_id in withdrawn_users[group_id]:
        del withdrawn_users[group_id][user_id]
    Database.register_or_update_user(user_id, display_name)

def withdraw_user(group_id, user_id):
    if group_id in group_registered_users and user_id in group_registered_users[group_id]:
        del group_registered_users[group_id][user_id]
    if group_id not in withdrawn_users:
        withdrawn_users[group_id] = {}
    withdrawn_users[group_id][user_id] = True
    return True

def get_user_display_name(group_id, user_id):
    if is_user_registered(group_id, user_id):
        return group_registered_users[group_id][user_id]
    stats = Database.get_user_stats(user_id)
    if stats and stats.get('display_name'):
        return stats['display_name']
    return None

def is_valid_name(name):
    if not name or len(name.strip()) == 0:
        return False
    return len(name.strip()) >= 1 and len(name.strip()) <= 50

def create_main_quick_reply():
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="العاب", text="العاب")),
        QuickReplyButton(action=MessageAction(label="نقاطي", text="نقاطي")),
        QuickReplyButton(action=MessageAction(label="الصدارة", text="الصدارة")),
        QuickReplyButton(action=MessageAction(label="مساعدة", text="مساعدة"))
    ])

def create_games_quick_reply():
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="اغنيه", text="اغنيه")),
        QuickReplyButton(action=MessageAction(label="ضد", text="ضد")),
        QuickReplyButton(action=MessageAction(label="سلسله", text="سلسله")),
        QuickReplyButton(action=MessageAction(label="اسرع", text="اسرع")),
        QuickReplyButton(action=MessageAction(label="لعبه", text="لعبه")),
        QuickReplyButton(action=MessageAction(label="تكوين", text="تكوين")),
        QuickReplyButton(action=MessageAction(label="فئه", text="فئه")),
        QuickReplyButton(action=MessageAction(label="مافيا", text="مافيا")),
        QuickReplyButton(action=MessageAction(label="سؤال", text="سؤال")),
        QuickReplyButton(action=MessageAction(label="تحدي", text="تحدي")),
        QuickReplyButton(action=MessageAction(label="اعتراف", text="اعتراف")),
        QuickReplyButton(action=MessageAction(label="توافق", text="توافق")),
        QuickReplyButton(action=MessageAction(label="بداية", text="بداية"))
    ])

def create_game_action_quick_reply():
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="لمح", text="لمح")),
        QuickReplyButton(action=MessageAction(label="جاوب", text="جاوب")),
        QuickReplyButton(action=MessageAction(label="ايقاف", text="ايقاف"))
    ])

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("توقيع غير صالح")
        abort(400)
    except Exception as e:
        logger.error(f"خطأ في معالجة الطلب {e}")
        abort(500)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        text = event.message.text.strip()
        user_id = event.source.user_id
        group_id = getattr(event.source, 'group_id', None) or user_id
        
        Database.update_last_activity(user_id)
        
        if user_id in waiting_for_name:
            if is_valid_name(text):
                display_name = text.strip()
                register_user(group_id, user_id, display_name)
                del waiting_for_name[user_id]
                msg = TextSendMessage(
                    text=f"تم التسجيل بنجاح\nاسمك {display_name}\nيمكنك الان اللعب وجمع النقاط",
                    quick_reply=create_main_quick_reply()
                )
            else:
                msg = TextSendMessage(text="الاسم غير صالح\nيرجى ادخال اسم صحيح حرف واحد على الاقل حد اقصى 50 حرف")
            line_bot_api.reply_message(event.reply_token, msg)
            return
        
        if is_user_withdrawn(group_id, user_id):
            return

        display_name = get_user_display_name(group_id, user_id) or "مستخدم"

        if text.lower() in ["بدايه", "start", "ابدا", "بداية"]:
            flex = FlexSendMessage(
                alt_text="مرحبا", 
                contents=UIBuilder.welcome_card(display_name, is_user_registered(group_id, user_id)),
                quick_reply=create_main_quick_reply()
            )
            line_bot_api.reply_message(event.reply_token, flex)
            return

        if text.lower() in ["مساعده", "help", "مساعدة"]:
            flex = FlexSendMessage(
                alt_text="المساعده", 
                contents=UIBuilder.help_card(),
                quick_reply=create_main_quick_reply()
            )
            line_bot_api.reply_message(event.reply_token, flex)
            return

        if text == "ألعاب" or text == "العاب":
            flex = FlexSendMessage(
                alt_text="قائمة الالعاب", 
                contents=UIBuilder.games_menu_card(is_user_registered(group_id, user_id)),
                quick_reply=create_games_quick_reply()
            )
            line_bot_api.reply_message(event.reply_token, flex)
            return

        if text == "تسجيل" or text == "تغيير":
            waiting_for_name[user_id] = True
            if is_user_registered(group_id, user_id):
                msg = TextSendMessage(text=f"انت مسجل حاليا باسم {display_name}\nادخل الاسم الجديد")
            else:
                msg = TextSendMessage(text="التسجيل\n\nادخل الاسم الذي تريده استخدام حرف واحد او ارقام")
            line_bot_api.reply_message(event.reply_token, msg)
            return

        if text == "انسحب":
            if withdraw_user(group_id, user_id):
                msg = TextSendMessage(
                    text="تم انسحابك من هذه الجلسة\nنقاطك محفوظة ويمكنك العودة في اي وقت بالضغط على تسجيل",
                    quick_reply=create_main_quick_reply()
                )
            else:
                msg = TextSendMessage(text="انت غير مسجل")
            line_bot_api.reply_message(event.reply_token, msg)
            return

        if text in ["نقاطي", "احصائياتي"]:
            stats = Database.get_user_stats(user_id)
            if not stats:
                msg = TextSendMessage(text="يجب التسجيل اولا\nاكتب تسجيل")
                line_bot_api.reply_message(event.reply_token, msg)
                return
            flex = FlexSendMessage(
                alt_text="احصائياتك", 
                contents=UIBuilder.stats_card(display_name, stats),
                quick_reply=create_main_quick_reply()
            )
            line_bot_api.reply_message(event.reply_token, flex)
            return

        if text in ["الصداره", "المتصدرين", "الصدارة"]:
            leaders = Database.get_leaderboard(20)
            flex = FlexSendMessage(
                alt_text="لوحه الصداره", 
                contents=UIBuilder.leaderboard_card(leaders),
                quick_reply=create_main_quick_reply()
            )
            line_bot_api.reply_message(event.reply_token, flex)
            return

        if text in ["ايقاف", "stop", "إيقاف"]:
            stopped = game_manager.stop_game(group_id)
            msg = TextSendMessage(
                text="تم ايقاف اللعبه" if stopped else "لا توجد لعبه نشطه",
                quick_reply=create_games_quick_reply()
            )
            line_bot_api.reply_message(event.reply_token, msg)
            return

        if text in ["سؤال", "سوال"]:
            msg = TextSendMessage(
                text=game_manager.get_random_question(),
                quick_reply=create_games_quick_reply()
            )
            line_bot_api.reply_message(event.reply_token, msg)
            return
        
        if text == "تحدي":
            msg = TextSendMessage(
                text=game_manager.get_random_challenge(),
                quick_reply=create_games_quick_reply()
            )
            line_bot_api.reply_message(event.reply_token, msg)
            return
        
        if text == "اعتراف":
            msg = TextSendMessage(
                text=game_manager.get_random_confession(),
                quick_reply=create_games_quick_reply()
            )
            line_bot_api.reply_message(event.reply_token, msg)
            return
        
        if text.startswith("منشن"):
            msg = TextSendMessage(
                text=game_manager.get_random_mention(),
                quick_reply=create_games_quick_reply()
            )
            line_bot_api.reply_message(event.reply_token, msg)
            return
        
        if text == "توافق":
            response = game_manager.start_game("compatibility", group_id)
            if isinstance(response, FlexSendMessage):
                response.quick_reply = create_game_action_quick_reply()
            line_bot_api.reply_message(event.reply_token, response)
            return

        game_commands = {
            "اغنيه": "song", "لعبه": "human_animal", "سلسله": "chain",
            "اسرع": "fast_typing", "ضد": "opposite", "تكوين": "letters",
            "فئه": "category", "مافيا": "mafia"
        }

        if text in game_commands:
            if not is_user_registered(group_id, user_id) and text != "مافيا" and text != "توافق":
                msg = TextSendMessage(text="يجب التسجيل اولا للعب هذه اللعبة\nاكتب تسجيل")
                line_bot_api.reply_message(event.reply_token, msg)
                return
            
            response = game_manager.start_game(game_commands[text], group_id)
            if response:
                if isinstance(response, FlexSendMessage):
                    response.quick_reply = create_game_action_quick_reply()
                line_bot_api.reply_message(event.reply_token, response)
            return

        game = game_manager.get_game(group_id)
        if game:
            if not is_user_registered(group_id, user_id):
                return
            
            result = game_manager.check_answer(group_id, text, user_id, display_name)
            if result:
                if result.get('correct') and result.get('points', 0) > 0:
                    Database.update_user_points(
                        user_id, 
                        result['points'], 
                        result.get('won', False), 
                        game_manager.active_games.get(group_id, {}).get('type', 'unknown')
                    )

                response = result.get('response')
                if response:
                    if isinstance(response, TextSendMessage):
                        response.quick_reply = create_game_action_quick_reply()
                    elif isinstance(response, FlexSendMessage):
                        response.quick_reply = create_game_action_quick_reply()
                    
                    if isinstance(response, list):
                        for r in response:
                            if isinstance(r, (TextSendMessage, FlexSendMessage)):
                                r.quick_reply = create_game_action_quick_reply()
                        line_bot_api.reply_message(event.reply_token, response)
                    else:
                        line_bot_api.reply_message(event.reply_token, response)

                if result.get('next_question') and not result.get('game_over'):
                    next_q = game_manager.next_question(group_id)
                    if next_q:
                        try:
                            time.sleep(1)
                            if isinstance(next_q, (TextSendMessage, FlexSendMessage)):
                                next_q.quick_reply = create_game_action_quick_reply()
                            line_bot_api.push_message(group_id, next_q)
                        except Exception as e:
                            logger.error(f"خطأ في ارسال السؤال التالي {e}")

                if result.get('game_over'):
                    game_manager.stop_game(group_id)
    
    except Exception as e:
        logger.error(f"خطأ في معالجة الرسالة {e}", exc_info=True)

@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy', 'service': 'line-bot'}, 200

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
