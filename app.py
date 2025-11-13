from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    QuickReply, QuickReplyButton, MessageAction,
    FlexSendMessage, BubbleContainer, BoxComponent, TextComponent
)
import os
from datetime import datetime, timedelta
import sqlite3
from collections import defaultdict
import threading
import time
import re
import logging

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    logger.info("تم استيراد جميع الألعاب بنجاح")
except Exception as e:
    logger.error(f"خطأ في استيراد الألعاب: {e}")

app = Flask(__name__)

# إعدادات LINE Bot
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'YOUR_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', 'YOUR_CHANNEL_SECRET')

if LINE_CHANNEL_ACCESS_TOKEN == 'YOUR_CHANNEL_ACCESS_TOKEN':
    logger.warning("⚠️ لم يتم تعيين LINE_CHANNEL_ACCESS_TOKEN")
if LINE_CHANNEL_SECRET == 'YOUR_CHANNEL_SECRET':
    logger.warning("⚠️ لم يتم تعيين LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# إعدادات Gemini AI
GEMINI_API_KEYS = [
    os.getenv('GEMINI_API_KEY_1', ''),
    os.getenv('GEMINI_API_KEY_2', ''),
    os.getenv('GEMINI_API_KEY_3', '')
]
GEMINI_API_KEYS = [key for key in GEMINI_API_KEYS if key]
current_gemini_key_index = 0
USE_AI = bool(GEMINI_API_KEYS)

logger.info(f"عدد مفاتيح Gemini المتاحة: {len(GEMINI_API_KEYS)}")
logger.info(f"استخدام AI: {USE_AI}")

def get_gemini_api_key():
    global current_gemini_key_index
    if GEMINI_API_KEYS:
        return GEMINI_API_KEYS[current_gemini_key_index]
    return None

def switch_gemini_key():
    global current_gemini_key_index
    if len(GEMINI_API_KEYS) > 1:
        current_gemini_key_index = (current_gemini_key_index + 1) % len(GEMINI_API_KEYS)
        logger.info(f"تم التبديل إلى مفتاح Gemini رقم: {current_gemini_key_index + 1}")
        return True
    return False

# تخزين الألعاب النشطة واللاعبين المسجلين
active_games = {}
registered_players = set()
user_message_count = defaultdict(lambda: {'count': 0, 'reset_time': datetime.now()})

# قفل thread-safe
games_lock = threading.Lock()
players_lock = threading.Lock()

# ألوان التصميم
COLOR_BG = "#FFFFFF"
COLOR_PRIMARY = "#000000"
COLOR_SECONDARY = "#888888"
COLOR_ACCENT = "#B0B0B0"

# قاعدة البيانات
DB_NAME = 'game_scores.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id TEXT PRIMARY KEY, 
                      display_name TEXT,
                      total_points INTEGER DEFAULT 0,
                      games_played INTEGER DEFAULT 0,
                      wins INTEGER DEFAULT 0,
                      last_played TEXT,
                      registered_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS game_history
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id TEXT,
                      game_type TEXT,
                      points INTEGER,
                      won INTEGER,
                      played_at TEXT DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (user_id) REFERENCES users(user_id))''')
        
        conn.commit()
        conn.close()
        logger.info("تم إنشاء قاعدة البيانات بنجاح")
    except Exception as e:
        logger.error(f"خطأ في إنشاء قاعدة البيانات: {e}")

init_db()

def update_user_points(user_id, display_name, points, won=False, game_type=""):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = c.fetchone()
        
        if user:
            new_points = user['total_points'] + points
            new_games = user['games_played'] + 1
            new_wins = user['wins'] + (1 if won else 0)
            c.execute('''UPDATE users SET total_points = ?, games_played = ?, 
                         wins = ?, last_played = ?, display_name = ?
                         WHERE user_id = ?''',
                      (new_points, new_games, new_wins, datetime.now().isoformat(), 
                       display_name, user_id))
        else:
            c.execute('''INSERT INTO users (user_id, display_name, total_points, 
                         games_played, wins, last_played) VALUES (?, ?, ?, ?, ?, ?)''',
                      (user_id, display_name, points, 1, 1 if won else 0, 
                       datetime.now().isoformat()))
        
        if game_type:
            c.execute('''INSERT INTO game_history (user_id, game_type, points, won) 
                         VALUES (?, ?, ?, ?)''',
                      (user_id, game_type, points, 1 if won else 0))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"خطأ في تحديث النقاط: {e}")
        return False

def get_user_stats(user_id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = c.fetchone()
        conn.close()
        return user
    except Exception as e:
        logger.error(f"خطأ في الحصول على الإحصائيات: {e}")
        return None

def get_leaderboard(limit=10):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''SELECT display_name, total_points, games_played, wins 
                     FROM users ORDER BY total_points DESC LIMIT ?''', (limit,))
        leaders = c.fetchall()
        conn.close()
        return leaders
    except Exception as e:
        logger.error(f"خطأ في الحصول على الصدارة: {e}")
        return []

def check_rate_limit(user_id, max_messages=20, time_window=60):
    now = datetime.now()
    user_data = user_message_count[user_id]
    
    if now - user_data['reset_time'] > timedelta(seconds=time_window):
        user_data['count'] = 0
        user_data['reset_time'] = now
    
    if user_data['count'] >= max_messages:
        return False
    
    user_data['count'] += 1
    return True

def cleanup_old_games():
    while True:
        try:
            time.sleep(300)
            now = datetime.now()
            to_delete = []
            
            with games_lock:
                for game_id, game_data in active_games.items():
                    if now - game_data.get('created_at', now) > timedelta(minutes=10):
                        to_delete.append(game_id)
                
                for game_id in to_delete:
                    del active_games[game_id]
        except Exception as e:
            logger.error(f"خطأ في التنظيف: {e}")

cleanup_thread = threading.Thread(target=cleanup_old_games, daemon=True)
cleanup_thread.start()

def get_fixed_quick_reply():
    """الأزرار الثابتة"""
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="أغنية", text="أغنية")),
        QuickReplyButton(action=MessageAction(label="لعبة", text="لعبة")),
        QuickReplyButton(action=MessageAction(label="سلسلة", text="سلسلة")),
        QuickReplyButton(action=MessageAction(label="أسرع", text="أسرع")),
        QuickReplyButton(action=MessageAction(label="ضد", text="ضد")),
        QuickReplyButton(action=MessageAction(label="ترتيب", text="ترتيب")),
        QuickReplyButton(action=MessageAction(label="كوّن", text="كوّن")),
        QuickReplyButton(action=MessageAction(label="اختلاف", text="اختلاف")),
        QuickReplyButton(action=MessageAction(label="سؤال", text="سؤال")),
        QuickReplyButton(action=MessageAction(label="تحدي", text="تحدي")),
        QuickReplyButton(action=MessageAction(label="اعتراف", text="اعتراف")),
        QuickReplyButton(action=MessageAction(label="اكثر", text="اكثر"))
    ])

def create_flex_text_message(title, body):
    """إنشاء رسالة Flex أنيقة"""
    bubble = BubbleContainer(
        direction="ltr",
        body=BoxComponent(
            layout="vertical",
            spacing="md",
            contents=[
                TextComponent(text=title, weight="bold", size="lg", color=COLOR_PRIMARY),
                TextComponent(text=body, wrap=True, color=COLOR_SECONDARY, size="md")
            ],
            background_color=COLOR_BG,
            padding_all="12px",
            corner_radius="10px"
        )
    )
    return FlexSendMessage(alt_text=title, contents=bubble, quick_reply=get_fixed_quick_reply())

def get_welcome_message(display_name):
    title = f"مرحباً {display_name} 👋"
    body = "اختر اللعبة التي تريد لعبها من الأزرار أدناه أو استعرض الأوامر."
    return create_flex_text_message(title, body)

def get_help_message():
    title = "📜 قائمة الأوامر المتاحة"
    body = (
        "- مساعدة: عرض قائمة الأوامر\n"
        "- انضم: الانضمام للعب\n"
        "- انسحب: الخروج من اللعبة\n"
        "- إيقاف: إيقاف اللعبة الحالية\n"
        "- نقاطي: عرض نقاطك\n"
        "- الصدارة: عرض قائمة الصدارة\n"
        "- الألعاب: استخدم الأزرار الثابتة لبدء أي لعبة"
    )
    return create_flex_text_message(title, body)

def get_join_message(display_name):
    title = f"✅ {display_name} تم تسجيلك"
    body = "الآن أنت جاهز للعب، اختر اللعبة من الأزرار أدناه."
    return create_flex_text_message(title, body)

def get_user_profile_safe(user_id):
    try:
        profile = line_bot_api.get_profile(user_id)
        return profile.display_name
    except Exception as e:
        logger.error(f"خطأ في الحصول على الملف الشخصي: {e}")
        return "مستخدم"

def start_game(game_id, game_class, game_type, user_id, event):
    try:
        with games_lock:
            # الألعاب التي تحتاج AI
            if game_class in [HumanAnimalPlantGame, LettersWordsGame]:
                game = game_class(line_bot_api, use_ai=USE_AI, 
                                get_api_key=get_gemini_api_key, 
                                switch_key=switch_gemini_key)
            # لعبة التوافق تحتاج معاملات خاصة
            elif game_class == CompatibilityGame:
                game = game_class(line_bot_api)
            else:
                game = game_class(line_bot_api)
            
            with players_lock:
                participants = registered_players.copy()
                participants.add(user_id)
            
            active_games[game_id] = {
                'game': game,
                'type': game_type,
                'created_at': datetime.now(),
                'participants': participants
            }
        
        response = game.start_game()
        line_bot_api.reply_message(event.reply_token, response)
        logger.info(f"بدأت لعبة {game_type} في {game_id}")
        return True
    except Exception as e:
        logger.error(f"خطأ في بدء اللعبة {game_type}: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=f"❌ حدث خطأ في بدء لعبة {game_type}. حاول مرة أخرى.",
                quick_reply=get_fixed_quick_reply()
            )
        )
        return False

@app.route("/", methods=['GET'])
def home():
    return f"""
    <html>
        <head>
            <title>LINE Bot - Game Server</title>
            <style>
                body {{ font-family: Arial; text-align: center; padding: 50px; background: #f5f5f5; }}
                h1 {{ color: #00B900; }}
                .status {{ background: white; padding: 20px; border-radius: 10px; margin: 20px auto; max-width: 600px; }}
            </style>
        </head>
        <body>
            <h1>🎮 LINE Bot Game Server</h1>
            <div class="status">
                <h2>✅ الخادم يعمل بنجاح</h2>
                <p>البوت جاهز لاستقبال الرسائل</p>
                <p><strong>الألعاب المتاحة:</strong> 9 ألعاب</p>
                <p><strong>اللاعبون المسجلون:</strong> {len(registered_players)}</p>
                <p><strong>الألعاب النشطة:</strong> {len(active_games)}</p>
            </div>
        </body>
    </html>
    """

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
        logger.error(f"خطأ في معالجة webhook: {e}")
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        user_id = event.source.user_id
        text = event.message.text.strip()
        
        if not check_rate_limit(user_id):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="⚠️ عدد كبير من الرسائل! انتظر دقيقة.")
            )
            return
        
        display_name = get_user_profile_safe(user_id)
        game_id = event.source.group_id if hasattr(event.source, 'group_id') else user_id
        
        logger.info(f"رسالة من {display_name}: {text}")
        
        # الأوامر الأساسية
        if text in ['البداية', 'ابدأ', 'start']:
            line_bot_api.reply_message(event.reply_token, get_welcome_message(display_name))
            return
        
        elif text == 'مساعدة':
            line_bot_api.reply_message(event.reply_token, get_help_message())
            return
        
        elif text == 'نقاطي':
            stats = get_user_stats(user_id)
            if stats:
                title = f"📊 إحصائيات {display_name}"
                body = (
                    f"النقاط: {stats['total_points']}\n"
                    f"الألعاب: {stats['games_played']}\n"
                    f"الفوز: {stats['wins']}\n"
                    f"نسبة الفوز: {(stats['wins'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0:.1f}%"
                )
                line_bot_api.reply_message(event.reply_token, create_flex_text_message(title, body))
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="لم تلعب أي لعبة بعد\n\nاكتب 'انضم' للتسجيل والبدء", 
                                  quick_reply=get_fixed_quick_reply())
                )
            return
        
        elif text == 'الصدارة':
            leaders = get_leaderboard()
            if leaders:
                title = "🏆 لوحة الصدارة"
                body = "\n".join([f"{i+1}. {leader['display_name']}: {leader['total_points']} نقطة" 
                                 for i, leader in enumerate(leaders)])
                line_bot_api.reply_message(event.reply_token, create_flex_text_message(title, body))
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="لا توجد بيانات بعد", quick_reply=get_fixed_quick_reply())
                )
            return
        
        elif text in ['إيقاف', 'ايقاف', 'stop']:
            with games_lock:
                if game_id in active_games:
                    game_type = active_games[game_id]['type']
                    del active_games[game_id]
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"تم إيقاف لعبة {game_type}", 
                                      quick_reply=get_fixed_quick_reply())
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="لا توجد لعبة نشطة", quick_reply=get_fixed_quick_reply())
                    )
            return
        
        elif text in ['انضم', 'تسجيل', 'join']:
            with players_lock:
                if user_id not in registered_players:
                    registered_players.add(user_id)
                    
                    with games_lock:
                        for gid, game_data in active_games.items():
                            if 'participants' not in game_data:
                                game_data['participants'] = set()
                            game_data['participants'].add(user_id)
                    
                    line_bot_api.reply_message(event.reply_token, get_join_message(display_name))
                    logger.info(f"انضم لاعب جديد: {display_name}")
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"أنت مسجل بالفعل يا {display_name}", 
                                      quick_reply=get_fixed_quick_reply())
                    )
            return
        
        elif text in ['انسحب', 'خروج', 'leave']:
            with players_lock:
                if user_id in registered_players:
                    registered_players.remove(user_id)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"تم انسحابك يا {display_name}", 
                                      quick_reply=get_fixed_quick_reply())
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="أنت غير مسجل", quick_reply=get_fixed_quick_reply())
                    )
            return
        
        # بدء الألعاب
        games_map = {
            'أغنية': (SongGame, 'أغنية'),
            'لعبة': (HumanAnimalPlantGame, 'لعبة'),
            'سلسلة': (ChainWordsGame, 'سلسلة'),
            'أسرع': (FastTypingGame, 'أسرع'),
            'ضد': (OppositeGame, 'ضد'),
            'كوّن': (LettersWordsGame, 'تكوين'),
            'تكوين': (LettersWordsGame, 'تكوين'),
            'اختلاف': (DifferencesGame, 'اختلاف'),
            'توافق': (CompatibilityGame, 'توافق')
        }
        
        if text in games_map:
            game_class, game_type = games_map[text]
            
            # لعبة التوافق تحتاج معالجة خاصة
            if text == 'توافق':
                with games_lock:
                    with players_lock:
                        participants = registered_players.copy()
                        participants.add(user_id)
                    
                    game = CompatibilityGame(line_bot_api)
                    active_games[game_id] = {
                        'game': game,
                        'type': 'توافق',
                        'created_at': datetime.now(),
                        'participants': participants
                    }
                
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="💖 لعبة التوافق!\n\nاكتب اسمين مفصولين بمسافة\nمثال: أحمد فاطمة",
                        quick_reply=get_fixed_quick_reply()
                    )
                )
                return
            
            start_game(game_id, game_class, game_type, user_id, event)
            return
        
        # الأوامر الإضافية (سؤال، تحدي، اعتراف، اكثر)
        if text == 'سؤال':
            try:
                import random
                with open('games/questions.txt', 'r', encoding='utf-8') as f:
                    questions = [q.strip() for q in f.readlines() if q.strip()]
                question = random.choice(questions)
                title = "❓ سؤال عشوائي"
                line_bot_api.reply_message(event.reply_token, create_flex_text_message(title, question))
            except Exception as e:
                logger.error(f"خطأ في قراءة الأسئلة: {e}")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="❌ حدث خطأ في تحميل السؤال", quick_reply=get_fixed_quick_reply())
                )
            return
        
        elif text == 'تحدي':
            try:
                import random
                with open('games/challenges.txt', 'r', encoding='utf-8') as f:
                    challenges = [c.strip() for c in f.readlines() if c.strip()]
                challenge = random.choice(challenges)
                title = "🎯 تحدي"
                line_bot_api.reply_message(event.reply_token, create_flex_text_message(title, challenge))
            except Exception as e:
                logger.error(f"خطأ في قراءة التحديات: {e}")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="❌ حدث خطأ في تحميل التحدي", quick_reply=get_fixed_quick_reply())
                )
            return
        
        elif text == 'اعتراف':
            try:
                import random
                with open('games/confessions.txt', 'r', encoding='utf-8') as f:
                    confessions = [c.strip() for c in f.readlines() if c.strip()]
                confession = random.choice(confessions)
                title = "🤫 اعتراف"
                line_bot_api.reply_message(event.reply_token, create_flex_text_message(title, confession))
            except Exception as e:
                logger.error(f"خطأ في قراءة الاعترافات: {e}")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="❌ حدث خطأ في تحميل الاعتراف", quick_reply=get_fixed_quick_reply())
                )
            return
        
        elif text == 'اكثر':
            try:
                import random
                with open('games/more_questions.txt', 'r', encoding='utf-8') as f:
                    more = [m.strip() for m in f.readlines() if m.strip()]
                more_q = random.choice(more)
                title = "💭 سؤال إضافي"
                line_bot_api.reply_message(event.reply_token, create_flex_text_message(title, more_q))
            except Exception as e:
                logger.error(f"خطأ في قراءة الأسئلة الإضافية: {e}")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="❌ حدث خطأ في تحميل السؤال", quick_reply=get_fixed_quick_reply())
                )
            return
        
        # معالجة إجابات الألعاب النشطة
        if game_id in active_games:
            game_data = active_games[game_id]
            
            with players_lock:
                is_registered = user_id in registered_players
            
            if not is_registered and 'participants' in game_data and user_id not in game_data['participants']:
                return
            
            game = game_data['game']
            game_type = game_data['type']
            
            try:
                result = game.check_answer(text, user_id, display_name)
                
                if result:
                    points = result.get('points', 0)
                    if points > 0:
                        update_user_points(user_id, display_name, points, 
                                         result.get('won', False), game_type)
                    
                    if result.get('game_over', False):
                        with games_lock:
                            if game_id in active_games:
                                del active_games[game_id]
                        
                        response = TextSendMessage(
                            text=result.get('message', 'انتهت اللعبة'),
                            quick_reply=get_fixed_quick_reply()
                        )
                    else:
                        response = result.get('response', TextSendMessage(text=result.get('message', '')))
                        
                        if isinstance(response, TextSendMessage):
                            response.quick_reply = get_fixed_quick_reply()
                    
                    line_bot_api.reply_message(event.reply_token, response)
                return
            except Exception as e:
                logger.error(f"خطأ في معالجة إجابة اللعبة: {e}")
                return
    
    except Exception as e:
        logger.error(f"خطأ في معالجة الرسالة: {e}")

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"خطأ غير متوقع: {error}", exc_info=True)
    return 'Internal Server Error', 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 بدء الخادم على المنفذ {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
