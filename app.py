from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest, PushMessageRequest,
    TextMessage, FlexMessage, FlexContainer, QuickReply, QuickReplyItem, MessageAction
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from apscheduler.schedulers.background import BackgroundScheduler
from ui_builder import UIBuilder
from games.game_manager import GameManager
from database import Database
import os, logging, re, atexit, time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

for var in ['LINE_CHANNEL_ACCESS_TOKEN', 'LINE_CHANNEL_SECRET']:
    if not os.getenv(var):
        logger.error(f"متغير البيئة {var} غير موجود")
        raise ValueError(f"متغير البيئة {var} مطلوب")

configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)

Database.init()
game_manager = GameManager(line_bot_api)

scheduler = BackgroundScheduler()
scheduler.add_job(func=Database.cleanup_inactive_users, trigger="interval", hours=24)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

waiting_for_registration = {}
waiting_for_name_change = {}

BOT_COMMANDS = [
    'بدايه', 'start', 'ابدا', 'بداية', 'مساعده', 'help', 'مساعدة', 'ألعاب', 'العاب', 'تسجيل', 
    'تغيير', 'تغيير الاسم', 'انسحب', 'نقاطي', 'احصائياتي', 'الصداره', 'المتصدرين', 'الصدارة', 
    'اللاعبين', 'ايقاف', 'stop', 'إيقاف', 'سؤال', 'سوال', 'تحدي', 'اعتراف', 'منشن', 'توافق', 
    'اغنيه', 'لعبه', 'سلسله', 'اسرع', 'ضد', 'تكوين', 'فئه', 'مافيا', 'لمح', 'تلميح', 'جاوب', 
    'الجواب', 'الغاء', 'إلغاء', 'انضم مافيا', 'بدء مافيا', 'شرح مافيا', 'إنهاء الليل', 
    'تصويت مافيا', 'إنهاء التصويت'
]

def get_quick_reply():
    return QuickReply(items=[
        QuickReplyItem(action=MessageAction(label="سؤال", text="سؤال")),
        QuickReplyItem(action=MessageAction(label="منشن", text="منشن")),
        QuickReplyItem(action=MessageAction(label="اعتراف", text="اعتراف")),
        QuickReplyItem(action=MessageAction(label="تحدي", text="تحدي")),
        QuickReplyItem(action=MessageAction(label="توافق", text="توافق")),
        QuickReplyItem(action=MessageAction(label="اغنية", text="اغنيه")),
        QuickReplyItem(action=MessageAction(label="ضد", text="ضد")),
        QuickReplyItem(action=MessageAction(label="تكوين", text="تكوين")),
        QuickReplyItem(action=MessageAction(label="سلسلة", text="سلسله")),
        QuickReplyItem(action=MessageAction(label="اسرع", text="اسرع")),
        QuickReplyItem(action=MessageAction(label="لعبه", text="لعبه")),
        QuickReplyItem(action=MessageAction(label="فئة", text="فئه")),
        QuickReplyItem(action=MessageAction(label="مافيا", text="مافيا"))
    ])

class NameFilter:
    @staticmethod
    def get_bad_words():
        return ['غبي', 'احمق', 'حمار', 'كلب', 'خنزير', 'قذر', 'وسخ', 'حقير', 'نذل', 'خائن', 'كذاب', 'لعين', 'ملعون', 'عاهر', 'زاني', 'فاسق', 'منافق']
    
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
        
        name = name.strip()
        if len(name) > 30:
            return False, "الاسم طويل جدا (الحد الاقصى 30 حرف)"
        
        normalized_name = NameFilter.normalize_arabic(name)
        for bad_word in NameFilter.get_bad_words():
            normalized_bad = NameFilter.normalize_arabic(bad_word)
            if normalized_bad in normalized_name:
                return False, "الاسم يحتوي على كلمات غير لائقة"
        
        return True, ""

def is_bot_command(text):
    text_lower = text.lower()
    for cmd in BOT_COMMANDS:
        if text_lower == cmd.lower():
            return True
    if text_lower.startswith(('صوت ', 'اقتل ', 'افحص ', 'احمي ')):
        return True
    return False

def is_user_registered(user_id):
    return Database.is_user_registered(user_id)

def get_user_display_name(user_id):
    stats = Database.get_user_stats(user_id)
    if stats and stats.get('display_name'):
        return stats['display_name']
    return None

def reply_message(reply_token, messages):
    try:
        if not isinstance(messages, list):
            messages = [messages]
        line_bot_api.reply_message(ReplyMessageRequest(reply_token=reply_token, messages=messages))
    except Exception as e:
        logger.error(f"خطأ في إرسال الرد: {e}")

def push_message(to, messages):
    try:
        if not isinstance(messages, list):
            messages = [messages]
        line_bot_api.push_message(PushMessageRequest(to=to, messages=messages))
    except Exception as e:
        logger.error(f"خطأ في إرسال push: {e}")

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

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    try:
        text = event.message.text.strip()
        user_id = event.source.user_id
        group_id = getattr(event.source, 'group_id', None) or user_id
        
        if user_id in waiting_for_registration:
            if text.lower() in ["انسحب", "إلغاء", "الغاء"]:
                del waiting_for_registration[user_id]
                msg = TextMessage(text="تم الغاء التسجيل", quick_reply=get_quick_reply())
                reply_message(event.reply_token, msg)
                return
            
            is_valid, error_msg = NameFilter.validate_name(text)
            if not is_valid:
                msg = TextMessage(text=f"{error_msg}\n\nاكتب اسم صحيح او اكتب الغاء", quick_reply=get_quick_reply())
                reply_message(event.reply_token, msg)
                return
            
            del waiting_for_registration[user_id]
            Database.register_or_update_user(user_id, text)
            msg = TextMessage(text=f"تم التسجيل بنجاح\nاسمك: {text}\nيمكنك الآن اللعب وجمع النقاط", quick_reply=get_quick_reply())
            reply_message(event.reply_token, msg)
            return
        
        if user_id in waiting_for_name_change:
            if text.lower() in ["انسحب", "إلغاء", "الغاء"]:
                del waiting_for_name_change[user_id]
                msg = TextMessage(text="تم الغاء تغيير الاسم", quick_reply=get_quick_reply())
                reply_message(event.reply_token, msg)
                return
            
            is_valid, error_msg = NameFilter.validate_name(text)
            if not is_valid:
                msg = TextMessage(text=f"{error_msg}\n\nاكتب اسم صحيح او اكتب الغاء", quick_reply=get_quick_reply())
                reply_message(event.reply_token, msg)
                return
            
            del waiting_for_name_change[user_id]
            Database.register_or_update_user(user_id, text)
            msg = TextMessage(text=f"تم تغيير الاسم بنجاح الى: {text}", quick_reply=get_quick_reply())
            reply_message(event.reply_token, msg)
            return

        if not is_bot_command(text):
            game = game_manager.get_game(group_id)
            if game and is_user_registered(user_id):
                try:
                    Database.update_last_activity(user_id)
                except:
                    pass
                
                display_name = get_user_display_name(user_id) or "مستخدم"
                result = game_manager.check_answer(group_id, text, user_id, display_name)
                
                if result:
                    if result.get('correct') and result.get('points', 0) > 0:
                        Database.update_user_points(
                            user_id, result['points'], result.get('won', False),
                            game_manager.active_games.get(group_id, {}).get('type', 'unknown')
                        )

                    response = result.get('response')
                    if response:
                        if isinstance(response, list):
                            for r in response:
                                if isinstance(r, (FlexMessage, TextMessage)):
                                    r.quick_reply = get_quick_reply()
                            reply_message(event.reply_token, response)
                        else:
                            if isinstance(response, (FlexMessage, TextMessage)):
                                response.quick_reply = get_quick_reply()
                            reply_message(event.reply_token, response)

                    if result.get('next_question') and not result.get('game_over'):
                        next_q = game_manager.next_question(group_id)
                        if next_q:
                            try:
                                if isinstance(next_q, FlexMessage):
                                    next_q.quick_reply = get_quick_reply()
                                time.sleep(1)
                                push_message(group_id, next_q)
                            except Exception as e:
                                logger.error(f"خطأ في إرسال السؤال التالي: {e}")

                    if result.get('game_over'):
                        game_manager.stop_game(group_id)
            return

        try:
            Database.update_last_activity(user_id)
        except:
            pass

        display_name = get_user_display_name(user_id) or "مستخدم"

        if text.lower() in ["بدايه", "start", "ابدا", "بداية"]:
            flex = FlexMessage(
                alt_text="مرحبا", 
                contents=FlexContainer.from_dict(UIBuilder.welcome_card(display_name, is_user_registered(user_id))),
                quick_reply=get_quick_reply()
            )
            reply_message(event.reply_token, flex)
            return

        if text.lower() in ["مساعده", "help", "مساعدة"]:
            flex = FlexMessage(
                alt_text="المساعده", 
                contents=FlexContainer.from_dict(UIBuilder.help_card()),
                quick_reply=get_quick_reply()
            )
            reply_message(event.reply_token, flex)
            return

        if text in ["ألعاب", "العاب"]:
            flex = FlexMessage(
                alt_text="قائمة الألعاب",
                contents=FlexContainer.from_dict(UIBuilder.games_menu_card(is_user_registered(user_id))),
                quick_reply=get_quick_reply()
            )
            reply_message(event.reply_token, flex)
            return

        if text == "تسجيل":
            if is_user_registered(user_id):
                msg = TextMessage(text=f"انت مسجل بالفعل باسم: {display_name}", quick_reply=get_quick_reply())
            else:
                existing_name = Database.get_existing_user_name(user_id)
                if existing_name:
                    Database.reactivate_user(user_id)
                    msg = TextMessage(text=f"مرحباً بعودتك\nتم إعادة تفعيل حسابك باسم: {existing_name}\n\nلتغيير الاسم اكتب: تغيير", quick_reply=get_quick_reply())
                else:
                    waiting_for_registration[user_id] = True
                    msg = TextMessage(text="اكتب اسمك في الشات الآن للعب\n\nاكتب الغاء للالغاء", quick_reply=get_quick_reply())
            reply_message(event.reply_token, msg)
            return

        if text in ["تغيير", "تغيير الاسم"]:
            if not is_user_registered(user_id):
                msg = TextMessage(text="يجب التسجيل اولا", quick_reply=get_quick_reply())
            else:
                waiting_for_name_change[user_id] = True
                msg = TextMessage(text=f"اسمك الحالي: {display_name}\n\nاكتب اسمك الجديد في الشات الآن\n\nاكتب الغاء للالغاء", quick_reply=get_quick_reply())
            reply_message(event.reply_token, msg)
            return

        if text == "انسحب":
            if not is_user_registered(user_id):
                msg = TextMessage(text="انت غير مسجل", quick_reply=get_quick_reply())
            else:
                Database.delete_user(user_id)
                msg = TextMessage(text="تم الغاء تسجيلك بنجاح", quick_reply=get_quick_reply())
            reply_message(event.reply_token, msg)
            return

        if text in ["نقاطي", "احصائياتي"]:
            if not is_user_registered(user_id):
                msg = TextMessage(text="يجب التسجيل اولا", quick_reply=get_quick_reply())
                reply_message(event.reply_token, msg)
                return
            stats = Database.get_user_stats(user_id)
            flex = FlexMessage(
                alt_text="احصائياتك", 
                contents=FlexContainer.from_dict(UIBuilder.stats_card(display_name, stats)),
                quick_reply=get_quick_reply()
            )
            reply_message(event.reply_token, flex)
            return

        if text in ["الصداره", "المتصدرين", "الصدارة"]:
            leaders = Database.get_leaderboard(20)
            flex = FlexMessage(
                alt_text="لوحه الصداره", 
                contents=FlexContainer.from_dict(UIBuilder.leaderboard_card(leaders)),
                quick_reply=get_quick_reply()
            )
            reply_message(event.reply_token, flex)
            return
        
        if text == "اللاعبين":
            players = Database.get_all_players()
            flex = FlexMessage(
                alt_text="جميع اللاعبين", 
                contents=FlexContainer.from_dict(UIBuilder.all_players_card(players)),
                quick_reply=get_quick_reply()
            )
            reply_message(event.reply_token, flex)
            return

        if text in ["ايقاف", "stop", "إيقاف"]:
            stopped = game_manager.stop_game(group_id)
            msg = TextMessage(text="تم ايقاف اللعبه" if stopped else "لا توجد لعبه نشطه", quick_reply=get_quick_reply())
            reply_message(event.reply_token, msg)
            return

        if text in ["سؤال", "سوال"]:
            msg = TextMessage(text=game_manager.get_random_question(), quick_reply=get_quick_reply())
            reply_message(event.reply_token, msg)
            return
        
        if text == "تحدي":
            msg = TextMessage(text=game_manager.get_random_challenge(), quick_reply=get_quick_reply())
            reply_message(event.reply_token, msg)
            return
        
        if text == "اعتراف":
            msg = TextMessage(text=game_manager.get_random_confession(), quick_reply=get_quick_reply())
            reply_message(event.reply_token, msg)
            return
        
        if text.startswith("منشن"):
            msg = TextMessage(text=game_manager.get_random_mention(), quick_reply=get_quick_reply())
            reply_message(event.reply_token, msg)
            return
        
        if text == "توافق":
            response = game_manager.start_game("compatibility", group_id)
            if isinstance(response, FlexMessage):
                response.quick_reply = get_quick_reply()
            reply_message(event.reply_token, response)
            return

        game_commands = {
            "اغنيه": "song", "لعبه": "human_animal", "سلسله": "chain",
            "اسرع": "fast_typing", "ضد": "opposite", "تكوين": "letters",
            "فئه": "category", "مافيا": "mafia"
        }

        if text in game_commands:
            if not is_user_registered(user_id) and text != "مافيا":
                msg = TextMessage(text="يجب التسجيل اولا لبدء الالعاب", quick_reply=get_quick_reply())
                reply_message(event.reply_token, msg)
                return
            
            response = game_manager.start_game(game_commands[text], group_id)
            if response:
                if isinstance(response, FlexMessage):
                    response.quick_reply = get_quick_reply()
                elif isinstance(response, TextMessage):
                    response.quick_reply = get_quick_reply()
                reply_message(event.reply_token, response)
            return
    
    except AttributeError as e:
        logger.error(f"خطأ في بنية الرسالة: {e}")
    except Exception as e:
        logger.error(f"خطأ في معالجة الرسالة: {e}", exc_info=True)

@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy', 'service': 'line-bot'}, 200

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
