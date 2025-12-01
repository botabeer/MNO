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

def get_user_name(user_id):
    try:
        profile = line_bot_api.get_profile(user_id)
        display_name = profile.display_name
        Database.register_or_update_user(user_id, display_name)
        return display_name
    except Exception as e:
        logger.error(f"خطأ جلب اسم المستخدم {user_id}: {e}")
        stats = Database.get_user_stats(user_id)
        return stats.get('display_name', 'مستخدم') if stats else 'مستخدم'

def get_quick_reply():
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="سؤال", text="سؤال")),
        QuickReplyButton(action=MessageAction(label="منشن", text="منشن")),
        QuickReplyButton(action=MessageAction(label="اعتراف", text="اعتراف")),
        QuickReplyButton(action=MessageAction(label="تحدي", text="تحدي")),
        QuickReplyButton(action=MessageAction(label="توافق", text="توافق")),
        QuickReplyButton(action=MessageAction(label="أسرع", text="أسرع")),
        QuickReplyButton(action=MessageAction(label="سلسلة", text="سلسلة")),
        QuickReplyButton(action=MessageAction(label="مافيا", text="مافيا")),
        QuickReplyButton(action=MessageAction(label="لعبة", text="لعبة")),
        QuickReplyButton(action=MessageAction(label="أغنية", text="أغنية")),
        QuickReplyButton(action=MessageAction(label="ضد", text="ضد")),
        QuickReplyButton(action=MessageAction(label="تكوين", text="تكوين")),
        QuickReplyButton(action=MessageAction(label="إيقاف", text="إيقاف"))
    ])

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

    if text.lower() in ["بداية", "start", "ابدأ"]:
        flex = FlexSendMessage(alt_text="مرحباً", contents=UIBuilder.welcome_card(display_name))
        line_bot_api.reply_message(event.reply_token, flex)
        return

    if text.lower() in ["مساعدة", "help"]:
        flex = FlexSendMessage(alt_text="المساعدة", contents=UIBuilder.help_card())
        line_bot_api.reply_message(event.reply_token, flex)
        return

    if text in ["انضم", "تسجيل"]:
        success = Database.register_or_update_user(user_id, display_name)
        msg = "تم التسجيل بنجاح" if success else "أنت مسجل بالفعل"
        flex = FlexSendMessage(alt_text=msg, contents=UIBuilder.registration_success(display_name))
        line_bot_api.reply_message(event.reply_token, flex)
        return

    if text in ["نقاطي", "إحصائياتي"]:
        stats = Database.get_user_stats(user_id)
        flex = FlexSendMessage(alt_text="إحصائياتك", contents=UIBuilder.stats_card(display_name, stats))
        line_bot_api.reply_message(event.reply_token, flex)
        return

    if text in ["الصدارة", "المتصدرين"]:
        leaders = Database.get_leaderboard(10)
        flex = FlexSendMessage(alt_text="لوحة الصدارة", contents=UIBuilder.leaderboard_card(leaders))
        line_bot_api.reply_message(event.reply_token, flex)
        return

    if text in ["إيقاف", "stop"]:
        stopped = game_manager.stop_game(group_id)
        msg = TextSendMessage(text="تم إيقاف اللعبة" if stopped else "لا توجد لعبة نشطة", quick_reply=quick_reply)
        line_bot_api.reply_message(event.reply_token, msg)
        return

    game_commands = {
        "أغنية": "song", "لعبة": "human_animal", "سلسلة": "chain",
        "أسرع": "fast_typing", "ضد": "opposite", "تكوين": "letters",
        "توافق": "compatibility", "مافيا": "mafia"
    }

    if text in game_commands:
        response = game_manager.start_game(game_commands[text], group_id)
        if response:
            line_bot_api.reply_message(event.reply_token, response)
        return

    if text in ["سؤال", "سوال"]:
        msg = TextSendMessage(text=game_manager.get_random_question(), quick_reply=quick_reply)
        line_bot_api.reply_message(event.reply_token, msg)
        return

    if text == "تحدي":
        msg = TextSendMessage(text=game_manager.get_random_challenge(), quick_reply=quick_reply)
        line_bot_api.reply_message(event.reply_token, msg)
        return

    if text == "اعتراف":
        msg = TextSendMessage(text=game_manager.get_random_confession(), quick_reply=quick_reply)
        line_bot_api.reply_message(event.reply_token, msg)
        return

    if text.startswith("منشن"):
        msg = TextSendMessage(text=game_manager.get_random_mention(), quick_reply=quick_reply)
        line_bot_api.reply_message(event.reply_token, msg)
        return

    result = game_manager.check_answer(group_id, text, user_id, display_name)
    if result:
        if result.get('correct') and result.get('points', 0) > 0 and Database.is_user_registered(user_id):
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
                    logger.error(f"خطأ إرسال السؤال التالي: {e}")

        if result.get('game_over'):
            game_manager.stop_game(group_id)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
