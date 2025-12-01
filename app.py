from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
import os
from datetime import datetime
import threading
import time
import random
import logging
import sys

# الإعدادات
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("mafia-bot")

# الاستيراد
from constants import COMMANDS, GAMES, TEXT_COMMANDS, POINTS
from database import Database
from ui_builder import UIBuilder

# استيراد الألعاب
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'games'))
    from song_game import SongGame
    from human_animal_plant_game import HumanAnimalPlantGame
    from chain_words_game import ChainWordsGame
    from fast_typing_game import FastTypingGame
    from opposite_game import OppositeGame
    from letters_words_game import LettersWordsGame
    from differences_game import DifferencesGame
    from compatibility_game import CompatibilityGame
    from mafia_game import MafiaGame
    logger.info("تم تحميل جميع الألعاب")
except Exception as e:
    logger.error(f"خطأ في تحميل الألعاب: {e}")

app = Flask(__name__)

# إعداد LINE
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# الحالة
active_games = {}
games_lock = threading.Lock()

# قاعدة البيانات
Database.init()

def get_user_name_from_line(user_id):
    """
    الحصول على اسم المستخدم من LINE
    """
    try:
        profile = line_bot_api.get_profile(user_id)
        return profile.display_name
    except LineBotApiError as e:
        if e.status_code == 404:
            logger.warning(f"ملف مستخدم غير موجود: {user_id[-4:]}")
        else:
            logger.error(f"خطأ LINE API: {e}")
        return f"لاعب_{user_id[-4:]}"
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {e}")
        return f"لاعب_{user_id[-4:]}"

def update_user_name_in_db(user_id):
    """
    تحديث اسم المستخدم في قاعدة البيانات من LINE
    """
    try:
        line_name = get_user_name_from_line(user_id)
        Database.update_user_name(user_id, line_name, line_name)
        return line_name
    except Exception as e:
        logger.error(f"خطأ في تحديث الاسم: {e}")
        return f"لاعب_{user_id[-4:]}"

def load_text_file(filename):
    """تحميل ملف نصي"""
    try:
        filepath = os.path.join('games', filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        return []
    except Exception as e:
        logger.error(f"خطأ تحميل {filename}: {e}")
        return []

# تحميل الملفات النصية
QUESTIONS = load_text_file('questions.txt')
CHALLENGES = load_text_file('challenges.txt')
CONFESSIONS = load_text_file('confessions.txt')
MENTION_QUESTIONS = load_text_file('more_questions.txt')

def start_game(game_id, game_class, game_type, user_id):
    """بدء لعبة جديدة"""
    try:
        with games_lock:
            game = game_class(line_bot_api)
            active_games[game_id] = {
                'game': game,
                'type': game_type,
                'created_at': datetime.now(),
                'answered_users': set()
            }
        
        response = game.start_game()
        return response
    except Exception as e:
        logger.error(f"خطأ بدء {game_type}: {e}")
        return TextSendMessage(text="حدث خطأ في بدء اللعبة")

@app.route("/", methods=['GET'])
def home():
    """الصفحة الرئيسية"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>بوت الألعاب</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 16px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                padding: 40px;
                max-width: 500px;
                width: 100%;
            }}
            h1 {{ 
                color: #1a1a1a; 
                font-size: 2em; 
                margin-bottom: 10px; 
                text-align: center; 
            }}
            .status {{
                background: #f5f5f5;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
            }}
            .status-item {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #ddd;
            }}
            .status-item:last-child {{ border-bottom: none; }}
            .label {{ color: #666; }}
            .value {{ color: #1a1a1a; font-weight: bold; }}
            .footer {{ 
                text-align: center; 
                margin-top: 20px; 
                color: #999; 
                font-size: 0.8em; 
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>بوت الألعاب</h1>
            <div class="status">
                <div class="status-item">
                    <span class="label">حالة الخادم</span>
                    <span class="value">يعمل</span>
                </div>
                <div class="status-item">
                    <span class="label">ألعاب نشطة</span>
                    <span class="value">{len(active_games)}</span>
                </div>
                <div class="status-item">
                    <span class="label">الألعاب المتاحة</span>
                    <span class="value">9</span>
                </div>
            </div>
            <div class="footer">منصة ألعاب تفاعلية</div>
        </div>
    </body>
    </html>
    """

@app.route("/callback", methods=['POST'])
def callback():
    """معالج Webhook"""
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        abort(400)
    
    body = request.get_data(as_text=True)
    logger.info("استلام webhook")
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("توقيع غير صالح")
        abort(400)
    except Exception as e:
        logger.error(f"خطأ في معالجة الحدث: {e}")
    
    return 'OK', 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """معالج الرسائل الرئيسي - صامت ويستجيب للأوامر فقط"""
    try:
        user_id = event.source.user_id
        text = event.message.text.strip() if event.message.text else ""
        
        if not user_id or not text:
            return
        
        # الحصول على معرف اللعبة
        game_id = getattr(event.source, 'group_id', user_id)
        
        # تحديث اسم المستخدم تلقائياً
        display_name = update_user_name_in_db(user_id)
        
        logger.info(f"{display_name} ({user_id[-4:]}): {text[:50]}")
        
        # === الأوامر الأساسية ===
        
        if text in COMMANDS['start']:
            line_bot_api.reply_message(event.reply_token,
                FlexSendMessage(alt_text=f"مرحباً {display_name}",
                    contents=UIBuilder.welcome_card(display_name)))
            return
        
        if text in COMMANDS['help']:
            line_bot_api.reply_message(event.reply_token,
                FlexSendMessage(alt_text="المساعدة",
                    contents=UIBuilder.help_card()))
            return
        
        if text in COMMANDS['stats']:
            stats = Database.get_user_stats(user_id)
            line_bot_api.reply_message(event.reply_token,
                FlexSendMessage(alt_text="إحصائياتك",
                    contents=UIBuilder.stats_card(display_name, stats)))
            return
        
        if text in COMMANDS['leaderboard']:
            leaders = Database.get_leaderboard()
            line_bot_api.reply_message(event.reply_token,
                FlexSendMessage(alt_text="الصدارة",
                    contents=UIBuilder.leaderboard_card(leaders)))
            return
        
        if text in COMMANDS['join']:
            # التسجيل مع حفظ الاسم من LINE
            Database.register_user(user_id, display_name, display_name)
            line_bot_api.reply_message(event.reply_token,
                FlexSendMessage(alt_text="تم التسجيل",
                    contents=UIBuilder.registration_success(display_name)))
            return
        
        if text in COMMANDS['stop']:
            with games_lock:
                if game_id in active_games:
                    game_type = active_games[game_id]['type']
                    del active_games[game_id]
                    line_bot_api.reply_message(event.reply_token,
                        TextSendMessage(text=f"تم إيقاف لعبة {game_type}"))
                else:
                    line_bot_api.reply_message(event.reply_token,
                        TextSendMessage(text="لا توجد لعبة نشطة"))
            return
        
        # === الأوامر النصية (بدون Flex) ===
        
        if text in TEXT_COMMANDS['question'] and QUESTIONS:
            line_bot_api.reply_message(event.reply_token,
                TextSendMessage(text=random.choice(QUESTIONS)))
            return
        
        if text in TEXT_COMMANDS['challenge'] and CHALLENGES:
            line_bot_api.reply_message(event.reply_token,
                TextSendMessage(text=random.choice(CHALLENGES)))
            return
        
        if text in TEXT_COMMANDS['confession'] and CONFESSIONS:
            line_bot_api.reply_message(event.reply_token,
                TextSendMessage(text=random.choice(CONFESSIONS)))
            return
        
        if text in TEXT_COMMANDS['mention'] and MENTION_QUESTIONS:
            line_bot_api.reply_message(event.reply_token,
                TextSendMessage(text=random.choice(MENTION_QUESTIONS)))
            return
        
        # === بدء الألعاب ===
        
        games_map = {
            'أغنية': SongGame,
            'لعبة': HumanAnimalPlantGame,
            'سلسلة': ChainWordsGame,
            'أسرع': FastTypingGame,
            'ضد': OppositeGame,
            'تكوين': LettersWordsGame,
            'اختلاف': DifferencesGame,
            'توافق': CompatibilityGame,
            'مافيا': MafiaGame
        }
        
        if text in games_map:
            response = start_game(game_id, games_map[text], text, user_id)
            if response:
                line_bot_api.reply_message(event.reply_token, response)
            return
        
        # === معالجة إجابات الألعاب النشطة ===
        
        if game_id in active_games:
            # التحقق من التسجيل
            if not Database.is_user_registered(user_id):
                return  # صامت - لا يرد على غير المسجلين
            
            game_data = active_games[game_id]
            
            # التحقق من أن اللاعب لم يجب بعد
            if user_id in game_data.get('answered_users', set()):
                return  # صامت
            
            game = game_data['game']
            game_type = game_data['type']
            
            try:
                result = game.check_answer(text, user_id, display_name)
                if result:
                    # تسجيل الإجابة
                    if result.get('correct', False):
                        game_data.setdefault('answered_users', set()).add(user_id)
                    
                    # تحديث النقاط
                    points = result.get('points', 0)
                    if points > 0:
                        Database.update_user_points(user_id, display_name, points,
                            result.get('won', False), game_type)
                    
                    # إنهاء اللعبة
                    if result.get('game_over', False):
                        with games_lock:
                            if game_id in active_games:
                                del active_games[game_id]
                    
                    # إرسال الرد
                    response = result.get('response')
                    if response:
                        line_bot_api.reply_message(event.reply_token, response)
                return
            except Exception as e:
                logger.error(f"خطأ معالجة إجابة: {e}")
                return
        
        # صامت - لا يرد على رسائل غير معروفة
        
    except Exception as e:
        logger.error(f"خطأ في handle_message: {e}", exc_info=True)

def cleanup_old_games():
    """تنظيف الألعاب القديمة"""
    while True:
        try:
            time.sleep(300)
            now = datetime.now()
            to_delete = []
            
            with games_lock:
                for game_id, game_data in active_games.items():
                    age = (now - game_data.get('created_at', now)).total_seconds()
                    if age > 900:  # 15 دقيقة
                        to_delete.append(game_id)
                
                for game_id in to_delete:
                    del active_games[game_id]
                
                if to_delete:
                    logger.info(f"حذف {len(to_delete)} لعبة قديمة")
        
        except Exception as e:
            logger.error(f"خطأ التنظيف: {e}")

# تشغيل التنظيف
cleanup_thread = threading.Thread(target=cleanup_old_games, daemon=True)
cleanup_thread.start()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info("="*50)
    logger.info("بوت الألعاب - بدء التشغيل")
    logger.info(f"المنفذ: {port}")
    logger.info(f"الألعاب: {len(active_games)}")
    logger.info("="*50)
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
