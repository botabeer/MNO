from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
from ui_builder import UIBuilder
from games import GameManager
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
game_manager = GameManager()

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
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
    group_id = event.source.group_id if hasattr(event.source, 'group_id') else None
    
    if text in ["بداية", "start"]:
        flex = FlexSendMessage(alt_text="البداية", contents=UIBuilder.create_start_window())
        line_bot_api.reply_message(event.reply_token, flex)
    
    elif text in ["مساعدة", "help"]:
        flex = FlexSendMessage(alt_text="المساعدة", contents=UIBuilder.create_help_window())
        line_bot_api.reply_message(event.reply_token, flex)
    
    elif text == "الألعاب":
        flex = FlexSendMessage(alt_text="الألعاب", contents=UIBuilder.create_games_menu())
        line_bot_api.reply_message(event.reply_token, flex)
    
    elif text == "لعبة الأغنية":
        q, opts = game_manager.get_song_question(user_id)
        flex = FlexSendMessage(alt_text="لعبة الأغنية", 
            contents=UIBuilder.create_game_window("لعبة الأغنية", q, opts, game_manager.get_progress(user_id, 'song')))
        line_bot_api.reply_message(event.reply_token, flex)
    
    elif text in ["سؤال", "سوال"]:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=game_manager.get_random_question()))
    
    elif text == "تحدي":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=game_manager.get_random_challenge()))
    
    elif text == "اعتراف":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=game_manager.get_random_confession()))
    
    elif text.startswith("منشن"):
        if not group_id:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="هذا الأمر يعمل فقط في المجموعات"))
            return
        if "عشوائي" in text:
            member = game_manager.get_random_member(group_id)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"تم اختيار: {member}"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="منشن تم"))
    
    elif text == "المافيا":
        if not group_id:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="لعبة المافيا تعمل فقط في المجموعات"))
            return
        flex = FlexSendMessage(alt_text="المافيا", contents=UIBuilder.create_mafia_window())
        line_bot_api.reply_message(event.reply_token, flex)
    
    elif text == "بدء المافيا":
        if not group_id:
            return
        game_manager.start_mafia(group_id)
        flex = FlexSendMessage(alt_text="المافيا بدأت", contents=UIBuilder.create_mafia_game(game_manager.get_mafia_state(group_id)))
        line_bot_api.reply_message(event.reply_token, flex)
    
    elif text == "النقاط":
        points = game_manager.get_user_points(user_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"نقاطك: {points}"))
    
    else:
        result = game_manager.check_answer(user_id, text)
        if result:
            prev_ans = game_manager.get_previous_answer(user_id)
            if result['correct']:
                q, opts = game_manager.get_song_question(user_id)
                flex = FlexSendMessage(alt_text="صحيح", 
                    contents=UIBuilder.create_game_window("لعبة الأغنية", q, opts, 
                        game_manager.get_progress(user_id, 'song'), prev_ans, True))
                line_bot_api.reply_message(event.reply_token, flex)
            else:
                flex = FlexSendMessage(alt_text="خطأ", 
                    contents=UIBuilder.create_result_window(False, prev_ans))
                line_bot_api.reply_message(event.reply_token, flex)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
