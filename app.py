from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage,
    QuickReply, QuickReplyButton, MessageAction
)
from apscheduler.schedulers.background import BackgroundScheduler
from ui_builder import UIBuilder
from games.game_manager import GameManager
from database import Database
import os
import logging
import re
import atexit
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
waiting_for_registration = {}
waiting_for_name_change = {}

def get_quick_reply():
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="سؤال", text="سؤال")),
        QuickReplyButton(action=MessageAction(label="منشن", text="منشن")),
        QuickReplyButton(action=MessageAction(label="اعتراف", text="اعتراف")),
        QuickReplyButton(action=MessageAction(label="تحدي", text="تحدي")),
        QuickReplyButton(action=MessageAction(label="توافق", text="توافق")),
        QuickReplyButton(action=MessageAction(label="اغنية", text="اغنيه")),
        QuickReplyButton(action=MessageAction(label="ضد", text="ضد")),
        QuickReplyButton(action=MessageAction(label="تكوين", text="تكوين")),
        QuickReplyButton(action=MessageAction(label="سلسلة", text="سلسله")),
        QuickReplyButton(action=MessageAction(label="اسرع", text="اسرع")),
        QuickReplyButton(action=MessageAction(label="لعبه", text="لعبه")),
        QuickReplyButton(action=MessageAction(label="فئة", text="فئه")),
        QuickReplyButton(action=MessageAction(label="مافيا", text="مافيا"))
    ])

class NameFilter:
    @staticmethod
    def get_bad_words():
        return [
            'غبي', 'احمق', 'حمار', 'كلب', 'خنزير', 'قذر', 'وسخ', 'حقير', 'نذل',
            'خائن', 'كذاب', 'لعين', 'ملعون', 'عاهر', 'زاني', 'فاسق', 'منافق'
        ]
    
    @staticmethod
    def normalize_arabic(text):
        if not text:
            return ""
        text = text.lower().strip()
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '')
        text = text.replace('ة', 'ه').replace('ى', 'ي')
        text = re.sub(r'[\u064B-\u065F]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text
    
    @staticmethod
    def validate_name(name):
        if not name or name.strip() == "":
            return False, "الاسم لا يمكن ان يكون فارغا"
        
        if len(name.strip()) < 1:
            return False, "الاسم قصير جدا"
        
        if len(name.strip()) > 30:
            return False, "الاسم طويل جدا الحد الاقصى 30 حرف"
        
        if re.match(r'^[^a-zA-Zء-ي\s]+$', name):
            return False, "الاسم يحتوي على رموز غير صالحة"
        
        if re.match(r'^[\d]+$', name):
            return False, "الاسم لا يمكن ان يكون ارقام فقط"
        
        normalized_name = NameFilter.normalize_arabic(name)
        for bad_word in NameFilter.get_bad_words():
            normalized_bad = NameFilter.normalize_arabic(bad_word)
            if normalized_bad in normalized_name:
                return False, "الاسم يحتوي على كلمات غير لائقة"
        
        return True, ""

def is_user_registered(group_id, user_id):
    return group_id in group_registered_users and user_id in group_registered_users[group_id]

def register_user(group_id, user_id, display_name):
    if group_id not in group_registered_users:
        group_registered_users[group_id] = {}
    group_registered_users[group_id][user_id] = display_name
    Database.register_or_update_user(user_id, display_name)

def update_user_name(group_id, user_id, new_name):
    if group_id in group_registered_users and user_id in group_registered_users[group_id]:
        group_registered_users[group_id][user_id] = new_name
    Database.register_or_update_user(user_id, new_name)

def unregister_user(group_id, user_id):
    if group_id in group_registered_users and user_id in group_registered_users[group_id]:
        del group_registered_users[group_id][user_id]
        return True
    return False

def get_user_display_name(group_id, user_id):
    if is_user_registered(group_id, user_id):
        return group_registered_users[group_id][user_id]
    stats = Database.get_user_stats(user_id)
    if stats and stats.get('display_name'):
        return stats['display_name']
    return None

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
        logger.error(f"خطأ في معالجة الطلب: {e}")
        abort(500)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        text = event.message.text.strip()
        user_id = event.source.user_id
        group_id = getattr(event.source, 'group_id', None) or user_id
        
        Database.update_last_activity(user_id)

        if user_id in waiting_for_registration:
            if text.lower() in ["الغاء", "إلغاء"]:
                del waiting_for_registration[user_id]
                msg = TextSendMessage(text="تم الغاء التسجيل", quick_reply=get_quick_reply())
                line_bot_api.reply_message(event.reply_token, msg)
                return
            
            is_valid, error_msg = NameFilter.validate_name(text)
            if not is_valid:
                msg = TextSendMessage(text=f"{error_msg}\n\nاكتب اسم صحيح او اكتب الغاء", quick_reply=get_quick_reply())
                line_bot_api.reply_message(event.reply_token, msg)
                return
            
            register_group = waiting_for_registration[user_id]
            del waiting_for_registration[user_id]
            register_user(register_group, user_id, text)
            msg = TextSendMessage(text=f"تم التسجيل بنجاح\n\nاسمك {text}\n\nيمكنك الان اللعب وجمع النقاط", quick_reply=get_quick_reply())
            line_bot_api.reply_message(event.reply_token, msg)
            return
        
        if user_id in waiting_for_name_change:
            if text.lower() in ["الغاء", "إلغاء"]:
                del waiting_for_name_change[user_id]
                msg = TextSendMessage(text="تم الغاء تغيير الاسم", quick_reply=get_quick_reply())
                line_bot_api.reply_message(event.reply_token, msg)
                return
            
            is_valid, error_msg = NameFilter.validate_name(text)
            if not is_valid:
                msg = TextSendMessage(text=f"{error_msg}\n\nاكتب اسم صحيح او اكتب الغاء", quick_reply=get_quick_reply())
                line_bot_api.reply_message(event.reply_token, msg)
                return
            
            change_group = waiting_for_name_change[user_id]
            del waiting_for_name_change[user_id]
            update_user_name(change_group, user_id, text)
            msg = TextSendMessage(text=f"تم تغيير الاسم بنجاح الى {text}", quick_reply=get_quick_reply())
            line_bot_api.reply_message(event.reply_token, msg)
            return

        display_name = get_user_display_name(group_id, user_id) or "مستخدم"

        if text.lower() in ["بدايه", "start", "ابدا", "بداية"]:
            flex = FlexSendMessage(
                alt_text="مرحبا", 
                contents=UIBuilder.welcome_card(display_name, is_user_registered(group_id, user_id)),
                quick_reply=get_quick_reply()
            )
            line_bot_api.reply_message(event.reply_token, flex)
            return

        if text.lower() in ["مساعده", "help", "مساعدة"]:
            flex = FlexSendMessage(
                alt_text="المساعده", 
                contents=UIBuilder.help_card(),
                quick_reply=get_quick_reply()
            )
            line_bot_api.reply_message(event.reply_token, flex)
            return

        if text == "ألعاب" or text == "العاب":
            flex = FlexSendMessage(
                alt_text="قائمة الألعاب",
                contents=UIBuilder.games_menu_card(is_user_registered(group_id, user_id)),
                quick_reply=get_quick_reply()
            )
            line_bot_api.reply_message(event.reply_token, flex)
            return

        if text == "تسجيل":
            if is_user_registered(group_id, user_id):
                msg = TextSendMessage(text=f"انت مسجل بالفعل باسم {display_name}", quick_reply=get_quick_reply())
            else:
                waiting_for_registration[user_id] = group_id
                msg = TextSendMessage(text="مرحبا بك في التسجيل\n\nالرجاء كتابة اسمك\n\nالشروط\nمن حرف الى 30 حرف\nلا يحتوي على كلمات غير لائقة\n\nاكتب الغاء للالغاء", quick_reply=get_quick_reply())
            line_bot_api.reply_message(event.reply_token, msg)
            return

        if text == "تغيير" or text == "تغيير الاسم":
            if not is_user_registered(group_id, user_id):
                msg = TextSendMessage(text="يجب التسجيل اولا", quick_reply=get_quick_reply())
            else:
                waiting_for_name_change[user_id] = group_id
                msg = TextSendMessage(text=f"اسمك الحالي {display_name}\n\nالرجاء كتابة الاسم الجديد\n\nاكتب الغاء للالغاء", quick_reply=get_quick_reply())
            line_bot_api.reply_message(event.reply_token, msg)
            return

        if text == "انسحب":
            if unregister_user(group_id, user_id):
                msg = TextSendMessage(text="تم الغاء تسجيلك", quick_reply=get_quick_reply())
            else:
                msg = TextSendMessage(text="انت غير مسجل", quick_reply=get_quick_reply())
            line_bot_api.reply_message(event.reply_token, msg)
            return

        if text in ["نقاطي", "احصائياتي"]:
            if not is_user_registered(group_id, user_id):
                msg = TextSendMessage(text="يجب التسجيل اولا", quick_reply=get_quick_reply())
                line_bot_api.reply_message(event.reply_token, msg)
                return
            stats = Database.get_user_stats(user_id)
            flex = FlexSendMessage(
                alt_text="احصائياتك", 
                contents=UIBuilder.stats_card(display_name, stats),
                quick_reply=get_quick_reply()
            )
            line_bot_api.reply_message(event.reply_token, flex)
            return

        if text in ["الصداره", "المتصدرين", "الصدارة"]:
            leaders = Database.get_leaderboard(20)
            flex = FlexSendMessage(
                alt_text="لوحه الصداره", 
                contents=UIBuilder.leaderboard_card(leaders),
                quick_reply=get_quick_reply()
            )
            line_bot_api.reply_message(event.reply_token, flex)
            return
        
        if text == "اللاعبين":
            players = Database.get_all_players()
            flex = FlexSendMessage(
                alt_text="جميع اللاعبين", 
                contents=UIBuilder.all_players_card(players),
                quick_reply=get_quick_reply()
            )
            line_bot_api.reply_message(event.reply_token, flex)
            return

        if text in ["ايقاف", "stop", "إيقاف"]:
            stopped = game_manager.stop_game(group_id)
            msg = TextSendMessage(
                text="تم ايقاف اللعبه" if stopped else "لا توجد لعبه نشطه",
                quick_reply=get_quick_reply()
            )
            line_bot_api.reply_message(event.reply_token, msg)
            return

        if text in ["سؤال", "سوال"]:
            msg = TextSendMessage(text=game_manager.get_random_question(), quick_reply=get_quick_reply())
            line_bot_api.reply_message(event.reply_token, msg)
            return
        
        if text == "تحدي":
            msg = TextSendMessage(text=game_manager.get_random_challenge(), quick_reply=get_quick_reply())
            line_bot_api.reply_message(event.reply_token, msg)
            return
        
        if text == "اعتراف":
            msg = TextSendMessage(text=game_manager.get_random_confession(), quick_reply=get_quick_reply())
            line_bot_api.reply_message(event.reply_token, msg)
            return
        
        if text.startswith("منشن"):
            msg = TextSendMessage(text=game_manager.get_random_mention(), quick_reply=get_quick_reply())
            line_bot_api.reply_message(event.reply_token, msg)
            return
        
        if text == "توافق":
            response = game_manager.start_game("compatibility", group_id)
            if isinstance(response, FlexSendMessage):
                response.quick_reply = get_quick_reply()
            line_bot_api.reply_message(event.reply_token, response)
            return

        game_commands = {
            "اغنيه": "song", "لعبه": "human_animal", "سلسله": "chain",
            "اسرع": "fast_typing", "ضد": "opposite", "تكوين": "letters",
            "فئه": "category", "مافيا": "mafia"
        }

        if text in game_commands:
            if not is_user_registered(group_id, user_id) and text != "مافيا":
                msg = TextSendMessage(text="يجب التسجيل اولا", quick_reply=get_quick_reply())
                line_bot_api.reply_message(event.reply_token, msg)
                return
            
            response = game_manager.start_game(game_commands[text], group_id)
            if response:
                if isinstance(response, FlexSendMessage):
                    response.quick_reply = get_quick_reply()
                elif isinstance(response, TextSendMessage):
                    response.quick_reply = get_quick_reply()
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
                    if isinstance(response, list):
                        for r in response:
                            if isinstance(r, FlexSendMessage):
                                r.quick_reply = get_quick_reply()
                            elif isinstance(r, TextSendMessage):
                                r.quick_reply = get_quick_reply()
                        line_bot_api.reply_message(event.reply_token, response)
                    else:
                        if isinstance(response, FlexSendMessage):
                            response.quick_reply = get_quick_reply()
                        elif isinstance(response, TextSendMessage):
                            response.quick_reply = get_quick_reply()
                        line_bot_api.reply_message(event.reply_token, response)

                if result.get('next_question') and not result.get('game_over'):
                    next_q = game_manager.next_question(group_id)
                    if next_q:
                        try:
                            if isinstance(next_q, FlexSendMessage):
                                next_q.quick_reply = get_quick_reply()
                            time.sleep(1)
                            line_bot_api.push_message(group_id, next_q)
                        except Exception as e:
                            logger.error(f"خطأ في إرسال السؤال التالي: {e}")

                if result.get('game_over'):
                    game_manager.stop_game(group_id)
    
    except Exception as e:
        logger.error(f"خطأ في معالجة الرسالة: {e}", exc_info=True)

@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy', 'service': 'line-bot'}, 200

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
