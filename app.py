"""
LINE Bot Game Server - خادم ألعاب LINE Bot
==========================================
نظام ألعاب تفاعلي محسّن مع تصميم احترافي
"""

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from datetime import datetime
import threading
import time
import logging

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# استيراد الأدوات المساعدة
try:
    from utils import (
        init_db, update_user_points, get_user_stats, get_leaderboard,
        get_user_profile_safe, check_rate_limit, sanitize_text,
        create_welcome_bubble, create_stats_bubble, create_leaderboard_bubble,
        create_help_bubble, create_flex_message, get_quick_reply_buttons,
        get_gemini_api_key, switch_gemini_key, is_ai_available
    )
    logger.info("✅ تم استيراد الأدوات المساعدة بنجاح")
except Exception as e:
    logger.error(f"❌ خطأ في استيراد الأدوات: {e}")
    raise

# استيراد الألعاب
try:
    from games.song_game import SongGame
    from games.human_animal_plant_game import HumanAnimalPlantGame
    from games.chain_words_game import ChainWordsGame
    from games.fast_typing_game import FastTypingGame
    from games.opposite_game import OppositeGame
    from games.letters_words_game import LettersWordsGame
    from games.make_words import MakeWordsGame
    from games.differences_game import DifferencesGame
    from games.compatibility_game import CompatibilityGame
    logger.info("✅ تم استيراد جميع الألعاب بنجاح")
except Exception as e:
    logger.error(f"❌ خطأ في استيراد الألعاب: {e}")
    raise

# إنشاء تطبيق Flask
app = Flask(__name__)

# إعدادات LINE Bot
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '')

if not LINE_CHANNEL_ACCESS_TOKEN or LINE_CHANNEL_ACCESS_TOKEN == '':
    logger.error("❌ لم يتم تعيين LINE_CHANNEL_ACCESS_TOKEN")
    raise ValueError("LINE_CHANNEL_ACCESS_TOKEN is required")

if not LINE_CHANNEL_SECRET or LINE_CHANNEL_SECRET == '':
    logger.error("❌ لم يتم تعيين LINE_CHANNEL_SECRET")
    raise ValueError("LINE_CHANNEL_SECRET is required")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# تهيئة قاعدة البيانات
init_db()

# تخزين الألعاب النشطة واللاعبين المسجلين
active_games = {}
registered_players = set()

# قفل thread-safe
games_lock = threading.Lock()
players_lock = threading.Lock()

# قاموس الألعاب المتاحة
GAMES_MAP = {
    'أغنية': (SongGame, 'أغنية', False),
    'لعبة': (HumanAnimalPlantGame, 'إنسان حيوان نبات', True),
    'سلسلة': (ChainWordsGame, 'سلسلة الكلمات', False),
    'أسرع': (FastTypingGame, 'أسرع كتابة', False),
    'ضد': (OppositeGame, 'لعبة الأضداد', False),
    'كوّن': (LettersWordsGame, 'تكوين الكلمات', True),
    'تكوين': (LettersWordsGame, 'تكوين الكلمات', True),
    'اختلاف': (DifferencesGame, 'إيجاد الاختلافات', False),
    'توافق': (CompatibilityGame, 'لعبة التوافق', False)
}

def cleanup_old_games():
    """
    تنظيف الألعاب القديمة تلقائياً
    """
    while True:
        try:
            time.sleep(600)  # كل 10 دقائق
            now = datetime.now()
            to_delete = []
            
            with games_lock:
                for game_id, game_data in active_games.items():
                    created_at = game_data.get('created_at', now)
                    if (now - created_at).total_seconds() > 1800:  # 30 دقيقة
                        to_delete.append(game_id)
                
                for game_id in to_delete:
                    del active_games[game_id]
                    logger.info(f"🧹 تم حذف لعبة قديمة: {game_id}")
        
        except Exception as e:
            logger.error(f"❌ خطأ في التنظيف: {e}")

# بدء خيط التنظيف
cleanup_thread = threading.Thread(target=cleanup_old_games, daemon=True)
cleanup_thread.start()

def start_game(game_id: str, game_key: str, user_id: str, event) -> bool:
    """
    بدء لعبة جديدة
    
    Args:
        game_id: معرف اللعبة
        game_key: مفتاح اللعبة من GAMES_MAP
        user_id: معرف المستخدم
        event: حدث LINE
    
    Returns:
        True إذا بدأت اللعبة بنجاح
    """
    try:
        if game_key not in GAMES_MAP:
            logger.error(f"❌ لعبة غير معروفة: {game_key}")
            return False
        
        game_class, game_type, needs_ai = GAMES_MAP[game_key]
        
        with games_lock:
            # إنشاء نسخة اللعبة
            if needs_ai:
                game = game_class(
                    line_bot_api,
                    use_ai=is_ai_available(),
                    get_api_key=get_gemini_api_key,
                    switch_key=switch_gemini_key
                )
            else:
                game = game_class(line_bot_api)
            
            # تسجيل اللاعبين
            with players_lock:
                participants = registered_players.copy()
                participants.add(user_id)
            
            # حفظ اللعبة
            active_games[game_id] = {
                'game': game,
                'type': game_type,
                'key': game_key,
                'created_at': datetime.now(),
                'participants': participants
            }
        
        # بدء اللعبة
        response = game.start_game()
        line_bot_api.reply_message(event.reply_token, response)
        logger.info(f"🎮 بدأت لعبة {game_type} في {game_id}")
        return True
    
    except Exception as e:
        logger.error(f"❌ خطأ في بدء اللعبة {game_key}: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=f"❌ حدث خطأ في بدء اللعبة. حاول مرة أخرى.",
                quick_reply=get_quick_reply_buttons()
            )
        )
        return False

def load_random_content(filename: str, default: str = "المحتوى غير متوفر") -> str:
    """
    تحميل محتوى عشوائي من ملف
    
    Args:
        filename: اسم الملف
        default: النص الافتراضي
    
    Returns:
        سطر عشوائي من الملف
    """
    try:
        import random
        filepath = os.path.join('games', filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        if lines:
            return random.choice(lines)
        return default
    
    except Exception as e:
        logger.error(f"❌ خطأ في قراءة {filename}: {e}")
        return default

@app.route("/", methods=['GET'])
def home():
    """
    الصفحة الرئيسية للخادم
    """
    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LINE Bot - Game Server</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                max-width: 600px;
                width: 100%;
                padding: 40px;
                text-align: center;
            }}
            .logo {{
                font-size: 80px;
                margin-bottom: 20px;
                animation: bounce 2s infinite;
            }}
            @keyframes bounce {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-20px); }}
            }}
            h1 {{
                color: #000;
                font-size: 2em;
                margin-bottom: 10px;
                font-weight: 600;
            }}
            .subtitle {{
                color: #6B7280;
                margin-bottom: 30px;
                font-size: 1.1em;
            }}
            .status {{
                background: #F9FAFB;
                padding: 20px;
                border-radius: 12px;
                margin: 20px 0;
                border: 2px solid #E5E7EB;
            }}
            .status h2 {{
                color: #10B981;
                margin-bottom: 15px;
                font-size: 1.5em;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }}
            .stat-card {{
                background: white;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }}
            .stat-card .number {{
                font-size: 2em;
                font-weight: bold;
                color: #000;
                margin: 10px 0;
            }}
            .stat-card .label {{
                color: #6B7280;
                font-size: 0.9em;
            }}
            .info {{
                color: #9CA3AF;
                font-size: 0.9em;
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #E5E7EB;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🎮</div>
            <h1>LINE Bot Game Server</h1>
            <p class="subtitle">خادم الألعاب التفاعلية</p>
            
            <div class="status">
                <h2>✅ الخادم يعمل بنجاح</h2>
                <p>البوت جاهز لاستقبال الرسائل والألعاب</p>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="label">الألعاب المتاحة</div>
                        <div class="number">9</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">اللاعبون المسجلون</div>
                        <div class="number">{len(registered_players)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">الألعاب النشطة</div>
                        <div class="number">{len(active_games)}</div>
                    </div>
                </div>
            </div>
            
            <div class="info">
                <p>🤖 Powered by LINE Messaging API</p>
                <p>🎨 تصميم احترافي ومريح للعين</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route("/callback", methods=['POST'])
def callback():
    """
    معالج webhook من LINE
    """
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("❌ توقيع غير صالح")
        abort(400)
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة webhook: {e}")
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """
    معالج الرسائل النصية
    """
    try:
        user_id = event.source.user_id
        text = sanitize_text(event.message.text)
        
        # التحقق من معدل الرسائل
        if not check_rate_limit(user_id):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="⚠️ عدد كبير من الرسائل! انتظر دقيقة من فضلك.",
                    quick_reply=get_quick_reply_buttons()
                )
            )
            return
        
        display_name = get_user_profile_safe(line_bot_api, user_id)
        game_id = event.source.group_id if hasattr(event.source, 'group_id') else user_id
        
        logger.info(f"📨 رسالة من {display_name}: {text[:50]}")
        
        # === الأوامر الأساسية ===
        
        if text in ['البداية', 'ابدأ', 'start', 'بدء']:
            line_bot_api.reply_message(
                event.reply_token,
                create_welcome_bubble(display_name)
            )
            return
        
        elif text in ['مساعدة', 'help', 'ساعدني']:
            line_bot_api.reply_message(
                event.reply_token,
                create_help_bubble()
            )
            return
        
        elif text in ['نقاطي', 'احصائياتي', 'stats']:
            stats = get_user_stats(user_id)
            if stats:
                line_bot_api.reply_message(
                    event.reply_token,
                    create_stats_bubble(stats)
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    create_flex_message(
                        'لم تلعب بعد 🎮',
                        'ابدأ بالتسجيل أولاً بكتابة "انضم" ثم اختر لعبتك المفضلة!'
                    )
                )
            return
        
        elif text in ['الصدارة', 'leaderboard', 'المتصدرين']:
            leaders = get_leaderboard()
            if leaders:
                line_bot_api.reply_message(
                    event.reply_token,
                    create_leaderboard_bubble(leaders)
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    create_flex_message(
                        'لوحة الصدارة فارغة 📊',
                        'كن أول من يسجل نقاطاً!'
                    )
                )
            return
        
        elif text in ['إيقاف', 'ايقاف', 'stop', 'انهاء']:
            with games_lock:
                if game_id in active_games:
                    game_type = active_games[game_id]['type']
                    del active_games[game_id]
                    line_bot_api.reply_message(
                        event.reply_token,
                        create_flex_message(
                            'تم إيقاف اللعبة ⏸️',
                            f'تم إيقاف لعبة {game_type} بنجاح'
                        )
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text="لا توجد لعبة نشطة حالياً",
                            quick_reply=get_quick_reply_buttons()
                        )
                    )
            return
        
        elif text in ['انضم', 'تسجيل', 'join', 'سجلني']:
            with players_lock:
                if user_id not in registered_players:
                    registered_players.add(user_id)
                    
                    with games_lock:
                        for gid, game_data in active_games.items():
                            if 'participants' not in game_data:
                                game_data['participants'] = set()
                            game_data['participants'].add(user_id)
                    
                    line_bot_api.reply_message(
                        event.reply_token,
                        create_flex_message(
                            f'مرحباً {display_name} ✅',
                            'تم تسجيلك بنجاح! الآن يمكنك اختيار أي لعبة من الأزرار أدناه.'
                        )
                    )
                    logger.info(f"✅ انضم لاعب جديد: {display_name}")
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text=f"أنت مسجل بالفعل يا {display_name} 😊",
                            quick_reply=get_quick_reply_buttons()
                        )
                    )
            return
        
        elif text in ['انسحب', 'خروج', 'leave']:
            with players_lock:
                if user_id in registered_players:
                    registered_players.remove(user_id)
                    line_bot_api.reply_message(
                        event.reply_token,
                        create_flex_message(
                            'تم الانسحاب 👋',
                            f'تم انسحابك يا {display_name}. نأمل أن تعود قريباً!'
                        )
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text="أنت غير مسجل أصلاً",
                            quick_reply=get_quick_reply_buttons()
                        )
                    )
            return
        
        # === بدء الألعاب ===
        
        if text in GAMES_MAP:
            start_game(game_id, text, user_id, event)
            return
        
        # === المحتوى الإضافي ===
        
        if text == 'سؤال':
            question = load_random_content('questions.txt', 'لا توجد أسئلة متاحة')
            line_bot_api.reply_message(
                event.reply_token,
                create_flex_message('❓ سؤال عشوائي', question)
            )
            return
        
        elif text == 'تحدي':
            challenge = load_random_content('challenges.txt', 'لا توجد تحديات متاحة')
            line_bot_api.reply_message(
                event.reply_token,
                create_flex_message('🎯 تحدي', challenge)
            )
            return
        
        elif text == 'اعتراف':
            confession = load_random_content('confessions.txt', 'لا توجد اعترافات متاحة')
            line_bot_api.reply_message(
                event.reply_token,
                create_flex_message('🤫 اعتراف', confession)
            )
            return
        
        elif text == 'اكثر':
            more = load_random_content('more_questions.txt', 'لا توجد أسئلة إضافية')
            line_bot_api.reply_message(
                event.reply_token,
                create_flex_message('💭 سؤال إضافي', more)
            )
            return
        
        # === معالجة إجابات الألعاب ===
        
        if game_id in active_games:
            game_data = active_games[game_id]
            
            with players_lock:
                is_registered = user_id in registered_players
            
            if not is_registered and 'participants' in game_data:
                if user_id not in game_data['participants']:
                    return
            
            game = game_data['game']
            game_type = game_data['type']
            
            try:
                result = game.check_answer(text, user_id, display_name)
                
                if result:
                    points = result.get('points', 0)
                    if points > 0:
                        update_user_points(
                            user_id, display_name, points,
                            result.get('won', False), game_type
                        )
                    
                    if result.get('game_over', False):
                        with games_lock:
                            if game_id in active_games:
                                del active_games[game_id]
                        
                        response = result.get('response')
                        if not response:
                            response = TextSendMessage(
                                text=result.get('message', 'انتهت اللعبة'),
                                quick_reply=get_quick_reply_buttons()
                            )
                    else:
                        response = result.get('response', TextSendMessage(
                            text=result.get('message', ''),
                            quick_reply=get_quick_reply_buttons()
                        ))
                    
                    if isinstance(response, TextSendMessage):
                        if not response.quick_reply:
                            response.quick_reply = get_quick_reply_buttons()
                    
                    line_bot_api.reply_message(event.reply_token, response)
                return
            
            except Exception as e:
                logger.error(f"❌ خطأ في معالجة إجابة اللعبة: {e}")
                return
    
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الرسالة: {e}", exc_info=True)

@app.errorhandler(Exception)
def handle_error(error):
    """
    معالج الأخطاء العامة
    """
    logger.error(f"❌ خطأ غير متوقع: {error}", exc_info=True)
    return 'Internal Server Error', 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 بدء الخادم على المنفذ {port}")
    logger.info(f"🤖 AI متاح: {is_ai_available()}")
    logger.info(f"🎮 عدد الألعاب: {len(GAMES_MAP)}")
    app.run(host='0.0.0.0', port=port, debug=False)
