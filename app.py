from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
from ui_builder import UIBuilder
from games.game_manager import GameManager
from database import Database
import os
import logging

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# تهيئة قاعدة البيانات
Database.init()

# مدير الألعاب
game_manager = GameManager(line_bot_api)

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
    # group_id: إذا في مجموعة نستخدم group_id وإلا نستخدم user_id كمعرف الجلسة
    group_id = getattr(event.source, 'group_id', None) or user_id

    # ===== الحصول على اسم المستخدم من LINE أو من DB إذا تعذر =====
    try:
        profile = line_bot_api.get_profile(user_id)
        display_name = profile.display_name
    except Exception as e:
        # حاول المحافظة على الاسم المسجل إن وجد
        stats = Database.get_user_stats(user_id)
        if stats and stats.get('display_name'):
            display_name = stats.get('display_name')
        else:
            # خيار أخير: استخدم النص "مستخدم" فقط إن لم يتوفر اسم — هذا نادر
            display_name = "مستخدم"
        logger.info(f"تعذر جلب بروفايل LINE لـ {user_id}: {e}")

    # ===== الأوامر الأساسية =====

    if text.lower() in ["بداية", "start", "ابدأ"]:
        flex = FlexSendMessage(
            alt_text="مرحباً",
            contents=UIBuilder.welcome_card(display_name)
        )
        line_bot_api.reply_message(event.reply_token, flex)
        return

    if text.lower() in ["مساعدة", "help"]:
        flex = FlexSendMessage(
            alt_text="المساعدة",
            contents=UIBuilder.help_card()
        )
        line_bot_api.reply_message(event.reply_token, flex)
        return

    # تسجيل المستخدم — أمر "انضم" / "تسجيل"
    if text in ["انضم", "تسجيل"]:
        # خزن user_id و display_name كما هو من LINE
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

    # إظهار إحصائيات المستخدم (يستخدم display_name الموجود أو من DB)
    if text in ["نقاطي", "إحصائياتي"]:
        stats = Database.get_user_stats(user_id)
        flex = FlexSendMessage(
            alt_text="إحصائياتك",
            contents=UIBuilder.stats_card(display_name, stats)
        )
        line_bot_api.reply_message(event.reply_token, flex)
        return

    # لوحة الصدارة
    if text in ["الصدارة", "المتصدرين"]:
        leaders = Database.get_leaderboard(10)
        flex = FlexSendMessage(
            alt_text="لوحة الصدارة",
            contents=UIBuilder.leaderboard_card(leaders)
        )
        line_bot_api.reply_message(event.reply_token, flex)
        return

    # إيقاف اللعبة
    if text in ["إيقاف", "stop"]:
        stopped = game_manager.stop_game(group_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="تم إيقاف اللعبة" if stopped else "لا توجد لعبة نشطة")
        )
        return

    # ===== بدء الألعاب (أوامر الألعاب) =====

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
        # ابدأ اللعبة المناسبة — اللعبة سترجع Flex أو رسالة جاهزة
        response = game_manager.start_game(game_commands[text], group_id)
        if response:
            # response قد يكون من نوع FlexSendMessage أو TextSendMessage أو list — أرسله كما هو
            line_bot_api.reply_message(event.reply_token, response)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="تعذر بدء اللعبة"))
        return

    # ===== النصوص العشوائية (نص فقط) =====

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
        # إذا المستخدم طلب "منشن عشوائي" نستخدم get_random_member (حاليا placeholder)
        if "عشوائي" in text:
            member = game_manager.get_random_member(group_id)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=member)
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=game_manager.get_random_mention())
            )
        return

    # ===== التحقق من الإجابات (إعادة النتائج من game_manager) =====

    result = game_manager.check_answer(group_id, text, user_id, display_name)
    if result:
        # إذا النتيجة صحيحة وتحتوي نقاط — حدّث قاعدة البيانات فقط للمستخدمين المسجلين
        if result.get('correct') and result.get('points', 0) > 0:
            if Database.is_user_registered(user_id):
                Database.update_user_points(
                    user_id,
                    display_name,
                    result['points'],
                    result.get('won', False),
                    game_manager.active_games.get(group_id, {}).get('type', 'unknown')
                )
            else:
                # لم يسجل المستخدم؛ لا تُحتسب النقاط
                logger.info(f"لم يُحتسب نقاط لـ {user_id} لأنه غير مسجل")

        # إرسال الرد (قد يكون Flex أو Text)
        response = result.get('response')
        if response:
            line_bot_api.reply_message(event.reply_token, response)

        # إذا يوجد سؤال تالي أرسله (push لأن التفاعل الثاني قد لا يكون reply)
        if result.get('next_question'):
            next_q = game_manager.next_question(group_id)
            if next_q:
                # push to group/user
                try:
                    line_bot_api.push_message(group_id, next_q)
                except Exception as e:
                    logger.error(f"خطأ في ارسال السؤال التالي: {e}")

        # إنهاء اللعبة: أوقف اللعبة من الذاكرة
        if result.get('game_over'):
            game_manager.stop_game(group_id)

    # إن لم ينطبق أي شيء — تجاهل أو رد افتراضي (اختياري)
    return

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
