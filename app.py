from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, QuickReply, QuickReplyButton, MessageAction
from ui_builder import UIBuilder
from games.game_manager import GameManager
from database import Database
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

Database.init()
game_manager = GameManager(line_bot_api)

group_registered_users = {}

def get_user_name(user_id):
    try:
        profile = line_bot_api.get_profile(user_id)
        display_name = profile.display_name
        Database.register_or_update_user(user_id, display_name)
        return display_name
    except Exception as e:
        logger.error(f"خطا جلب اسم المستخدم {user_id}: {e}")
        stats = Database.get_user_stats(user_id)
        return stats.get('display_name', 'مستخدم') if stats else 'مستخدم'

def get_quick_reply():
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="سؤال", text="سؤال")),
        QuickReplyButton(action=MessageAction(label="منشن", text="منشن")),
        QuickReplyButton(action=MessageAction(label="اعتراف", text="اعتراف")),
        QuickReplyButton(action=MessageAction(label="تحدي", text="تحدي")),
        QuickReplyButton(action=MessageAction(label="توافق", text="توافق")),
        QuickReplyButton(action=MessageAction(label="فئة", text="فئة")),
        QuickReplyButton(action=MessageAction(label="اسرع", text="اسرع")),
        QuickReplyButton(action=MessageAction(label="سلسله", text="سلسله")),
        QuickReplyButton(action=MessageAction(label="مافيا", text="مافيا")),
        QuickReplyButton(action=MessageAction(label="لعبه", text="لعبه")),
        QuickReplyButton(action=MessageAction(label="اغنيه", text="اغنيه")),
        QuickReplyButton(action=MessageAction(label="ضد", text="ضد")),
        QuickReplyButton(action=MessageAction(label="تكوين", text="تكوين"))
    ])

def is_user_registered(group_id, user_id):
    if group_id not in group_registered_users:
        return False
    return user_id in group_registered_users[group_id]

def register_user(group_id, user_id, display_name):
    if group_id not in group_registered_users:
        group_registered_users[group_id] = {}
    group_registered_users[group_id][user_id] = display_name
    Database.register_or_update_user(user_id, display_name)

def unregister_user(group_id, user_id):
    if group_id in group_registered_users and user_id in group_registered_users[group_id]:
        del group_registered_users[group_id][user_id]
        return True
    return False

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    user_id = event.source.user_id
    group_id = getattr(event.source, 'group_id', None) or user_id
    
    display_name = get_user_name(user_id)
    
    quick_reply = get_quick_reply()

    allowed_commands = [
        "بدايه", "start", "ابدا",
        "مساعده", "help",
        "انضم", "تسجيل",
        "انسحب", "الغاء",
        "نقاطي", "احصائياتي",
        "الصداره", "المتصدرين",
        "ايقاف", "stop",
        "اغنيه", "لعبه", "سلسله", "اسرع", "ضد", "تكوين", "توافق", "مافيا", "فئه",
        "سؤال", "سوال", "تحدي", "اعتراف", "منشن",
        "لمح", "تلميح", "جاوب", "الجواب",
        "انضم مافيا", "بدء مافيا", "شرح مافيا", "حاله مافيا", "تصويت مافيا", "انهاء تصويت"
    ]

    is_vote_command = text.startswith("صوت ")
    
    game = game_manager.get_game(group_id)
    
    if not any(text.lower().startswith(cmd.lower()) for cmd in allowed_commands) and not is_vote_command and not game:
        return

    # الأوامر التي لا تحتاج تسجيل
    no_registration_commands = ["سؤال", "سوال", "تحدي", "اعتراف", "منشن", "توافق"]
    
    if text.lower() in ["بدايه", "start", "ابدا"]:
        flex = FlexSendMessage(alt_text="مرحبا", contents=UIBuilder.welcome_card(display_name, is_user_registered(group_id, user_id)))
        line_bot_api.reply_message(event.reply_token, flex)
        return

    if text.lower() in ["مساعده", "help"]:
        flex = FlexSendMessage(alt_text="المساعده", contents=UIBuilder.help_card())
        line_bot_api.reply_message(event.reply_token, flex)
        return

    if text in ["انضم", "تسجيل"]:
        if is_user_registered(group_id, user_id):
            msg = TextSendMessage(text="انت مسجل بالفعل", quick_reply=quick_reply)
        else:
            register_user(group_id, user_id, display_name)
            flex = FlexSendMessage(alt_text="تم التسجيل", contents=UIBuilder.registration_success(display_name))
            msg = flex
        line_bot_api.reply_message(event.reply_token, msg)
        return

    if text in ["انسحب", "الغاء"]:
        if unregister_user(group_id, user_id):
            msg = TextSendMessage(text="تم الغاء تسجيلك بنجاح", quick_reply=quick_reply)
        else:
            msg = TextSendMessage(text="انت غير مسجل", quick_reply=quick_reply)
        line_bot_api.reply_message(event.reply_token, msg)
        return

    if text in ["نقاطي", "احصائياتي"]:
        if not is_user_registered(group_id, user_id):
            msg = TextSendMessage(text="يجب التسجيل اولا باستخدام امر انضم", quick_reply=quick_reply)
            line_bot_api.reply_message(event.reply_token, msg)
            return
        stats = Database.get_user_stats(user_id)
        flex = FlexSendMessage(alt_text="احصائياتك", contents=UIBuilder.stats_card(display_name, stats))
        line_bot_api.reply_message(event.reply_token, flex)
        return

    if text in ["الصداره", "المتصدرين"]:
        leaders = Database.get_leaderboard(10)
        flex = FlexSendMessage(alt_text="لوحه الصداره", contents=UIBuilder.leaderboard_card(leaders))
        line_bot_api.reply_message(event.reply_token, flex)
        return

    if text in ["ايقاف", "stop"]:
        stopped = game_manager.stop_game(group_id)
        msg = TextSendMessage(text="تم ايقاف اللعبه" if stopped else "لا توجد لعبه نشطه", quick_reply=quick_reply)
        line_bot_api.reply_message(event.reply_token, msg)
        return

    # معالجة الأوامر التي لا تحتاج تسجيل
    if text.lower() in no_registration_commands:
        if text in ["سؤال", "سوال"]:
            msg = TextSendMessage(text=game_manager.get_random_question(), quick_reply=quick_reply)
        elif text == "تحدي":
            msg = TextSendMessage(text=game_manager.get_random_challenge(), quick_reply=quick_reply)
        elif text == "اعتراف":
            msg = TextSendMessage(text=game_manager.get_random_confession(), quick_reply=quick_reply)
        elif text.startswith("منشن"):
            msg = TextSendMessage(text=game_manager.get_random_mention(), quick_reply=quick_reply)
        elif text == "توافق":
            response = game_manager.start_game("compatibility", group_id)
            msg = response if response else TextSendMessage(text="خطا في بدء اللعبه", quick_reply=quick_reply)
        
        line_bot_api.reply_message(event.reply_token, msg)
        return

    # الألعاب التي تحتاج تسجيل
    game_commands = {
        "اغنيه": "song", "لعبه": "human_animal", "سلسله": "chain",
        "اسرع": "fast_typing", "ضد": "opposite", "تكوين": "letters",
        "فئه": "category", "مافيا": "mafia"
    }

    if text in game_commands:
        if not is_user_registered(group_id, user_id):
            msg = TextSendMessage(text="يجب التسجيل اولا باستخدام امر انضم", quick_reply=quick_reply)
            line_bot_api.reply_message(event.reply_token, msg)
            return
        
        response = game_manager.start_game(game_commands[text], group_id)
        if response:
            line_bot_api.reply_message(event.reply_token, response)
        return

    result = game_manager.check_answer(group_id, text, user_id, display_name)
    if result:
        if result.get('correct') and result.get('points', 0) > 0 and is_user_registered(group_id, user_id):
            Database.update_user_points(user_id, result['points'], result.get('won', False), game_manager.active_games.get(group_id, {}).get('type', 'unknown'))

        response = result.get('response')
        if response:
            if isinstance(response, TextSendMessage):
                response.quick_reply = quick_reply
            elif isinstance(response, list):
                for r in response:
                    if isinstance(r, TextSendMessage):
                        r.quick_reply = quick_reply
            line_bot_api.reply_message(event.reply_token, response)

        if result.get('next_question'):
            next_q = game_manager.next_question(group_id)
            if next_q:
                try:
                    line_bot_api.push_message(group_id, next_q)
                except Exception as e:
                    logger.error(f"خطا ارسال السؤال التالي: {e}")

        if result.get('game_over'):
            game_manager.stop_game(group_id)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
