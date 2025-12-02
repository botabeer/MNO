from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, QuickReply, QuickReplyButton, MessageAction
from ui_builder import UIBuilder
from games.game_manager import GameManager
from database import Database
from registration_handler import RegistrationHandler
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# التحقق من وجود المتغيرات البيئية المطلوبة
required_env_vars = ['LINE_CHANNEL_ACCESS_TOKEN', 'LINE_CHANNEL_SECRET']
for var in required_env_vars:
    if not os.getenv(var):
        logger.error(f"متغير البيئة {var} غير موجود")
        raise ValueError(f"متغير البيئة {var} مطلوب")

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

Database.init()
game_manager = GameManager(line_bot_api)
registration_handler = RegistrationHandler()

# ذاكرة تخزين المستخدمين المسجلين
group_registered_users = {}

def get_quick_reply():
    """إنشاء Quick Reply مع أزرار محسّنة"""
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
    """التحقق من تسجيل المستخدم"""
    return group_id in group_registered_users and user_id in group_registered_users[group_id]

def register_user(group_id, user_id, display_name):
    """تسجيل مستخدم جديد"""
    if group_id not in group_registered_users:
        group_registered_users[group_id] = {}
    group_registered_users[group_id][user_id] = display_name
    Database.register_or_update_user(user_id, display_name)
    logger.info(f"تم تسجيل المستخدم {display_name} ({user_id}) في {group_id}")

def update_user_name(group_id, user_id, new_name):
    """تحديث اسم المستخدم"""
    if group_id in group_registered_users and user_id in group_registered_users[group_id]:
        group_registered_users[group_id][user_id] = new_name
    Database.register_or_update_user(user_id, new_name)
    logger.info(f"تم تحديث اسم المستخدم {user_id} إلى {new_name}")

def unregister_user(group_id, user_id):
    """إلغاء تسجيل مستخدم"""
    if group_id in group_registered_users and user_id in group_registered_users[group_id]:
        del group_registered_users[group_id][user_id]
        return True
    return False

def get_user_display_name(group_id, user_id):
    """الحصول على اسم المستخدم المخصص"""
    if is_user_registered(group_id, user_id):
        return group_registered_users[group_id][user_id]
    
    # محاولة جلب من قاعدة البيانات
    stats = Database.get_user_stats(user_id)
    if stats and stats.get('display_name'):
        return stats['display_name']
    
    return None

@app.route("/callback", methods=['POST'])
def callback():
    """معالجة webhook من LINE"""
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("توقيع غير صالح")
        abort(400)
    except Exception as e:
        logger.error(f"خطأ في معالجة الطلب: {e}")
        abort(500)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """معالجة الرسائل النصية"""
    try:
        text = event.message.text.strip()
        user_id = event.source.user_id
        group_id = getattr(event.source, 'group_id', None) or user_id
        
        quick_reply = get_quick_reply()

        # أولاً: التحقق من حالة التسجيل أو تغيير الاسم
        if registration_handler.is_waiting_for_registration(user_id):
            if text.lower() in ["الغاء", "إلغاء", "cancel"]:
                registration_handler.cancel_registration(user_id)
                msg = TextSendMessage(text="تم إلغاء التسجيل", quick_reply=quick_reply)
                line_bot_api.reply_message(event.reply_token, msg)
                return
            
            result = registration_handler.process_registration(user_id, text)
            if result:
                if result['success']:
                    # نجح التسجيل
                    register_user(result['group_id'], user_id, result['name'])
                    line_bot_api.reply_message(event.reply_token, result['response'])
                else:
                    # فشل التحقق من الاسم
                    line_bot_api.reply_message(event.reply_token, result['response'])
                return
        
        if registration_handler.is_waiting_for_name_change(user_id):
            if text.lower() in ["الغاء", "إلغاء", "cancel"]:
                registration_handler.cancel_name_change(user_id)
                msg = TextSendMessage(text="تم إلغاء تغيير الاسم", quick_reply=quick_reply)
                line_bot_api.reply_message(event.reply_token, msg)
                return
            
            result = registration_handler.process_name_change(user_id, text)
            if result:
                if result['success']:
                    # نجح تغيير الاسم
                    update_user_name(result['group_id'], user_id, result['new_name'])
                    line_bot_api.reply_message(event.reply_token, result['response'])
                else:
                    # فشل التحقق من الاسم
                    line_bot_api.reply_message(event.reply_token, result['response'])
                return

        # الحصول على اسم المستخدم
        display_name = get_user_display_name(group_id, user_id) or "مستخدم"

        # قائمة الأوامر المسموحة
        allowed_commands = [
            "بدايه", "start", "ابدا", "بداية",
            "مساعده", "help", "مساعدة",
            "تسجيل",
            "تغيير الاسم", "تغيير اسم",
            "انسحب", "الغاء",
            "نقاطي", "احصائياتي",
            "الصداره", "المتصدرين",
            "ايقاف", "stop",
            "اغنيه", "لعبه", "سلسله", "اسرع", "ضد", "تكوين", "توافق", "مافيا", "فئه",
            "سؤال", "سوال", "تحدي", "اعتراف", "منشن",
            "لمح", "تلميح", "جاوب", "الجواب",
            "انضم مافيا", "بدء مافيا", "شرح مافيا", "حاله مافيا", "تصويت مافيا", 
            "انهاء تصويت", "إنهاء الليل"
        ]

        is_vote_command = text.startswith("صوت ")
        is_mafia_action = text.startswith(("اقتل ", "افحص ", "احمي "))
        
        game = game_manager.get_game(group_id)
        
        # تجاهل الرسائل التي ليست أوامر
        if not any(text.lower().startswith(cmd.lower()) for cmd in allowed_commands) \
           and not is_vote_command \
           and not is_mafia_action \
           and not game:
            return

        # الأوامر التي لا تحتاج تسجيل
        no_registration_commands = ["سؤال", "سوال", "تحدي", "اعتراف", "منشن", "توافق"]
        
        # معالجة أوامر البداية والمساعدة
        if text.lower() in ["بدايه", "start", "ابدا", "بداية"]:
            flex = FlexSendMessage(
                alt_text="مرحبا", 
                contents=UIBuilder.welcome_card(display_name, is_user_registered(group_id, user_id))
            )
            line_bot_api.reply_message(event.reply_token, flex)
            return

        if text.lower() in ["مساعده", "help", "مساعدة"]:
            flex = FlexSendMessage(alt_text="المساعده", contents=UIBuilder.help_card())
            line_bot_api.reply_message(event.reply_token, flex)
            return

        # معالجة التسجيل الجديد
        if text in ["تسجيل"]:
            if is_user_registered(group_id, user_id):
                msg = TextSendMessage(text=f"أنت مسجل بالفعل باسم: {display_name}", quick_reply=quick_reply)
                line_bot_api.reply_message(event.reply_token, msg)
            else:
                response = registration_handler.start_registration(user_id, group_id)
                line_bot_api.reply_message(event.reply_token, response)
            return

        # معالجة تغيير الاسم
        if text in ["تغيير الاسم", "تغيير اسم"]:
            if not is_user_registered(group_id, user_id):
                msg = TextSendMessage(text="يجب التسجيل أولاً باستخدام أمر: تسجيل", quick_reply=quick_reply)
                line_bot_api.reply_message(event.reply_token, msg)
            else:
                current_name = get_user_display_name(group_id, user_id)
                response = registration_handler.start_name_change(user_id, group_id, current_name)
                line_bot_api.reply_message(event.reply_token, response)
            return

        # معالجة الانسحاب
        if text in ["انسحب", "الغاء"]:
            if unregister_user(group_id, user_id):
                msg = TextSendMessage(text="تم إلغاء تسجيلك بنجاح", quick_reply=quick_reply)
            else:
                msg = TextSendMessage(text="أنت غير مسجل", quick_reply=quick_reply)
            line_bot_api.reply_message(event.reply_token, msg)
            return

        # معالجة الإحصائيات
        if text in ["نقاطي", "احصائياتي"]:
            if not is_user_registered(group_id, user_id):
                msg = TextSendMessage(
                    text="يجب التسجيل أولاً باستخدام أمر: تسجيل", 
                    quick_reply=quick_reply
                )
                line_bot_api.reply_message(event.reply_token, msg)
                return
            stats = Database.get_user_stats(user_id)
            flex = FlexSendMessage(
                alt_text="احصائياتك", 
                contents=UIBuilder.stats_card(display_name, stats)
            )
            line_bot_api.reply_message(event.reply_token, flex)
            return

        if text in ["الصداره", "المتصدرين"]:
            leaders = Database.get_leaderboard(10)
            flex = FlexSendMessage(
                alt_text="لوحه الصداره", 
                contents=UIBuilder.leaderboard_card(leaders)
            )
            line_bot_api.reply_message(event.reply_token, flex)
            return

        if text in ["ايقاف", "stop"]:
            stopped = game_manager.stop_game(group_id)
            msg = TextSendMessage(
                text="تم ايقاف اللعبه" if stopped else "لا توجد لعبه نشطه", 
                quick_reply=quick_reply
            )
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
                msg = response if response else TextSendMessage(
                    text="خطأ في بدء اللعبه", 
                    quick_reply=quick_reply
                )
            
            line_bot_api.reply_message(event.reply_token, msg)
            return

        # معالجة الألعاب
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
            if not is_user_registered(group_id, user_id) and text != "مافيا":
                msg = TextSendMessage(
                    text="يجب التسجيل أولاً باستخدام أمر: تسجيل", 
                    quick_reply=quick_reply
                )
                line_bot_api.reply_message(event.reply_token, msg)
                return
            
            response = game_manager.start_game(game_commands[text], group_id)
            if response:
                line_bot_api.reply_message(event.reply_token, response)
            return

        # معالجة الإجابات
        result = game_manager.check_answer(group_id, text, user_id, display_name)
        if result:
            # تحديث النقاط للمستخدمين المسجلين فقط
            if result.get('correct') and result.get('points', 0) > 0 and is_user_registered(group_id, user_id):
                Database.update_user_points(
                    user_id, 
                    result['points'], 
                    result.get('won', False), 
                    game_manager.active_games.get(group_id, {}).get('type', 'unknown')
                )

            response = result.get('response')
            if response:
                # إضافة quick_reply للرسائل
                if isinstance(response, TextSendMessage):
                    response.quick_reply = quick_reply
                elif isinstance(response, list):
                    for r in response:
                        if isinstance(r, TextSendMessage):
                            r.quick_reply = quick_reply
                line_bot_api.reply_message(event.reply_token, response)

            # إرسال السؤال التالي
            if result.get('next_question'):
                next_q = game_manager.next_question(group_id)
                if next_q:
                    try:
                        line_bot_api.push_message(group_id, next_q)
                    except Exception as e:
                        logger.error(f"خطأ في إرسال السؤال التالي: {e}")

            # إنهاء اللعبة
            if result.get('game_over'):
                game_manager.stop_game(group_id)
    
    except Exception as e:
        logger.error(f"خطأ في معالجة الرسالة: {e}", exc_info=True)

@app.route('/health', methods=['GET'])
def health_check():
    """فحص صحة التطبيق"""
    return {'status': 'healthy', 'service': 'line-bot'}, 200

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
