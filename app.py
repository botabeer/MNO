from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
from ui_builder import UIBuilder
from game_manager import GameManager
from database import Database
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# تهيئة قاعدة البيانات
Database.init()

# مدير الألعاب
game_manager = GameManager(line_bot_api)

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
    group_id = event.source.group_id if hasattr(event.source, 'group_id') else user_id
    
    try:
        # الحصول على اسم المستخدم
        profile = line_bot_api.get_profile(user_id)
        display_name = profile.display_name
    except:
        display_name = "مستخدم"
    
    # ===== الأوامر الأساسية =====
    
    if text in ["بداية", "start", "ابدأ"]:
        flex = FlexSendMessage(
            alt_text="مرحباً",
            contents=UIBuilder.welcome_card(display_name)
        )
        line_bot_api.reply_message(event.reply_token, flex)
        return
    
    if text in ["مساعدة", "help"]:
        flex = FlexSendMessage(
            alt_text="المساعدة",
            contents=UIBuilder.help_card()
        )
        line_bot_api.reply_message(event.reply_token, flex)
        return
    
    if text in ["انضم", "تسجيل"]:
        success = Database.register_user(user_id, display_name, display_name)
        if success:
            flex = FlexSendMessage(
                alt_text="تم التسجيل",
                contents=UIBuilder.registration_success(display_name)
            )
            line_bot_api.reply_message(event.reply_token, flex)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="أنت مسجل بالفعل!")
            )
        return
    
    if text in ["نقاطي", "إحصائياتي"]:
        stats = Database.get_user_stats(user_id)
        flex = FlexSendMessage(
            alt_text="إحصائياتك",
            contents=UIBuilder.stats_card(display_name, stats)
        )
        line_bot_api.reply_message(event.reply_token, flex)
        return
    
    if text in ["الصدارة", "المتصدرين"]:
        leaders = Database.get_leaderboard(10)
        flex = FlexSendMessage(
            alt_text="لوحة الصدارة",
            contents=UIBuilder.leaderboard_card(leaders)
        )
        line_bot_api.reply_message(event.reply_token, flex)
        return
    
    if text in ["إيقاف", "stop"]:
        game_manager.stop_game(group_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="تم إيقاف اللعبة")
        )
        return
    
    # ===== بدء الألعاب =====
    
    game_commands = {
        "أغنية": "song",
        "لعبة": "human_animal",
        "سلسلة": "chain",
        "أسرع": "fast_typing",
        "ضد": "opposite",
        "تكوين": "letters",
        "اختلاف": "differences",
        "توافق": "compatibility",
        "مافيا": "mafia"
    }
    
    if text in game_commands:
        response = game_manager.start_game(game_commands[text], group_id)
        if response:
            if isinstance(response, list):
                line_bot_api.reply_message(event.reply_token, response)
            else:
                line_bot_api.reply_message(event.reply_token, response)
        return
    
    # ===== النصوص العشوائية =====
    
    if text in ["سؤال", "سوال"]:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=game_manager.get_random_question())
        )
        return
    
    if text == "تحدي":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=game_manager.get_random_challenge())
        )
        return
    
    if text == "اعتراف":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=game_manager.get_random_confession())
        )
        return
    
    if text.startswith("منشن"):
        if "عشوائي" in text:
            member = game_manager.get_random_member(group_id)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"👤 {member}")
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=game_manager.get_random_mention())
            )
        return
    
    # ===== التحقق من الإجابات =====
    
    result = game_manager.check_answer(group_id, text, user_id, display_name)
    if result:
        # تحديث قاعدة البيانات
        if result.get('correct') and result.get('points', 0) > 0:
            Database.update_user_points(
                user_id,
                display_name,
                result['points'],
                result.get('won', False),
                game_manager.active_games.get(group_id, {}).get('type', 'unknown')
            )
        
        # إرسال الرد
        response = result.get('response')
        if response:
            if isinstance(response, list):
                line_bot_api.reply_message(event.reply_token, response)
            else:
                line_bot_api.reply_message(event.reply_token, response)
        
        # السؤال التالي
        if result.get('next_question'):
            next_q = game_manager.next_question(group_id)
            if next_q:
                if isinstance(next_q, list):
                    line_bot_api.push_message(group_id, next_q)
                else:
                    line_bot_api.push_message(group_id, next_q)
        
        # نهاية اللعبة
        if result.get('game_over'):
            game_manager.stop_game(group_id)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
