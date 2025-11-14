from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    QuickReply, QuickReplyButton, MessageAction,
    FlexSendMessage, ImageSendMessage
)
import os
from datetime import datetime, timedelta
import sqlite3
from collections import defaultdict
import threading
import time
import json
import random
import re
import logging

# ✅ إعداد Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("game-bot")

# إعداد Gemini AI
USE_AI = False
ask_gemini = None

try:
    import google.generativeai as genai
    GEMINI_API_KEYS = [
        os.getenv('GEMINI_API_KEY_1', ''),
        os.getenv('GEMINI_API_KEY_2', ''),
        os.getenv('GEMINI_API_KEY_3', '')
    ]
    GEMINI_API_KEYS = [key for key in GEMINI_API_KEYS if key]
    current_gemini_key_index = 0
    USE_AI = bool(GEMINI_API_KEYS)
    
    if USE_AI:
        genai.configure(api_key=GEMINI_API_KEYS[0])
        model = genai.GenerativeModel('gemini-pro')
        logger.info(f"✅ Gemini AI جاهز - {len(GEMINI_API_KEYS)} مفاتيح")
        
        def ask_gemini(prompt, max_retries=2):
            """سؤال Gemini AI"""
            for attempt in range(max_retries):
                try:
                    response = model.generate_content(prompt)
                    return response.text.strip()
                except Exception as e:
                    logger.error(f"خطأ في Gemini (محاولة {attempt + 1}): {e}")
                    if attempt < max_retries - 1 and len(GEMINI_API_KEYS) > 1:
                        global current_gemini_key_index
                        current_gemini_key_index = (current_gemini_key_index + 1) % len(GEMINI_API_KEYS)
                        genai.configure(api_key=GEMINI_API_KEYS[current_gemini_key_index])
            return None
except Exception as e:
    USE_AI = False
    logger.warning(f"⚠️ Gemini AI غير متوفر: {e}")

# استيراد الألعاب
try:
    from games.song_game import SongGame
    from games.human_animal_plant_game import HumanAnimalPlantGame
    from games.chain_words_game import ChainWordsGame
    from games.fast_typing_game import FastTypingGame
    from games.opposite_game import OppositeGame
    from games.letters_words_game import LettersWordsGame
    from games.differences_game import DifferencesGame
    from games.compatibility_game import CompatibilityGame
    logger.info("✅ تم استيراد جميع الألعاب")
except Exception as e:
    logger.error(f"❌ خطأ استيراد الألعاب: {e}")

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'YOUR_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', 'YOUR_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

active_games = {}
registered_players = set()
user_message_count = defaultdict(lambda: {'count': 0, 'reset_time': datetime.now()})

games_lock = threading.Lock()
players_lock = threading.Lock()

DB_NAME = 'game_scores.db'

def normalize_text(text):
    """تطبيع النص لقبول جميع أشكال الحروف"""
    if not text:
        return ""
    text = text.strip().lower()
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    text = text.replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '')
    text = text.replace('ة', 'ه').replace('ى', 'ي')
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'\s+', '', text)
    return text

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id TEXT PRIMARY KEY, display_name TEXT,
                      total_points INTEGER DEFAULT 0, games_played INTEGER DEFAULT 0,
                      wins INTEGER DEFAULT 0, last_played TEXT,
                      registered_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS game_history
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT,
                      game_type TEXT, points INTEGER, won INTEGER,
                      played_at TEXT DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (user_id) REFERENCES users(user_id))''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_user_points ON users(total_points DESC)''')
        conn.commit()
        conn.close()
        logger.info("✅ قاعدة البيانات جاهزة")
    except Exception as e:
        logger.error(f"❌ خطأ قاعدة البيانات: {e}")

init_db()

def update_user_points(user_id, display_name, points, won=False, game_type=""):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = c.fetchone()
        
        if user:
            c.execute('''UPDATE users SET total_points = ?, games_played = ?, wins = ?, 
                         last_played = ?, display_name = ? WHERE user_id = ?''',
                      (user['total_points'] + points, user['games_played'] + 1,
                       user['wins'] + (1 if won else 0), datetime.now().isoformat(),
                       display_name, user_id))
        else:
            c.execute('''INSERT INTO users (user_id, display_name, total_points, 
                         games_played, wins, last_played) VALUES (?, ?, ?, ?, ?, ?)''',
                      (user_id, display_name, points, 1, 1 if won else 0, datetime.now().isoformat()))
        
        if game_type:
            c.execute('''INSERT INTO game_history (user_id, game_type, points, won) 
                         VALUES (?, ?, ?, ?)''', (user_id, game_type, points, 1 if won else 0))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ خطأ تحديث النقاط: {e}")
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
        logger.error(f"❌ خطأ إحصائيات: {e}")
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
        logger.error(f"❌ خطأ الصدارة: {e}")
        return []

def check_rate_limit(user_id, max_messages=30, time_window=60):
    now = datetime.now()
    user_data = user_message_count[user_id]
    if now - user_data['reset_time'] > timedelta(seconds=time_window):
        user_data['count'] = 0
        user_data['reset_time'] = now
    if user_data['count'] >= max_messages:
        return False
    user_data['count'] += 1
    return True

def load_text_file(filename):
    try:
        filepath = os.path.join('games', filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        return []
    except Exception as e:
        logger.error(f"❌ خطأ تحميل ملف {filename}: {e}")
        return []

QUESTIONS = load_text_file('questions.txt')
CHALLENGES = load_text_file('challenges.txt')
CONFESSIONS = load_text_file('confessions.txt')
MORE_QUESTIONS = load_text_file('more_questions.txt')

def get_user_profile_safe(user_id):
    try:
        profile = line_bot_api.get_profile(user_id)
        return profile.display_name
    except Exception as e:
        logger.error(f"❌ خطأ الملف الشخصي: {e}")
        return "مستخدم"

def get_quick_reply():
    """الأزرار الثابتة"""
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="▫️أغنية", text="أغنية")),
        QuickReplyButton(action=MessageAction(label="▫️لعبة", text="لعبة")),
        QuickReplyButton(action=MessageAction(label="▫️سلسلة", text="سلسلة")),
        QuickReplyButton(action=MessageAction(label="▫️أسرع", text="أسرع")),
        QuickReplyButton(action=MessageAction(label="▫️ضد", text="ضد")),
        QuickReplyButton(action=MessageAction(label="▫️تكوين", text="تكوين")),
        QuickReplyButton(action=MessageAction(label="▫️اختلاف", text="اختلاف")),
        QuickReplyButton(action=MessageAction(label="▫️توافق", text="توافق")),
        QuickReplyButton(action=MessageAction(label="▪️سؤال", text="سؤال")),
        QuickReplyButton(action=MessageAction(label="▪️تحدي", text="تحدي")),
        QuickReplyButton(action=MessageAction(label="▪️اعتراف", text="اعتراف")),
        QuickReplyButton(action=MessageAction(label="▪️اكثر", text="اكثر")),
        QuickReplyButton(action=MessageAction(label="▪️مساعدة", text="مساعدة"))
    ])

def get_welcome_card(display_name):
    """بطاقة الترحيب الصغيرة"""
    return {
        "type": "bubble",
        "size": "kilo",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "▪️",
                    "size": "xxl",
                    "color": "#000000",
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": "مرحباً بك",
                    "size": "lg",
                    "weight": "bold",
                    "color": "#000000",
                    "align": "center",
                    "margin": "md"
                },
                {
                    "type": "text",
                    "text": display_name,
                    "size": "md",
                    "color": "#666666",
                    "align": "center",
                    "margin": "xs"
                },
                {
                    "type": "separator",
                    "margin": "lg",
                    "color": "#DDDDDD"
                },
                {
                    "type": "text",
                    "text": "استخدم الأزرار أدناه\nللعب وجمع النقاط",
                    "size": "sm",
                    "color": "#333333",
                    "align": "center",
                    "wrap": True,
                    "margin": "lg"
                }
            ],
            "paddingAll": "20px",
            "backgroundColor": "#FFFFFF"
        }
    }

def get_registered_card(display_name):
    """بطاقة التسجيل الصغيرة"""
    return {
        "type": "bubble",
        "size": "kilo",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "✓",
                    "size": "xxl",
                    "color": "#000000",
                    "align": "center",
                    "weight": "bold"
                },
                {
                    "type": "text",
                    "text": "تم التسجيل",
                    "size": "lg",
                    "weight": "bold",
                    "color": "#000000",
                    "align": "center",
                    "margin": "md"
                },
                {
                    "type": "text",
                    "text": display_name,
                    "size": "md",
                    "color": "#666666",
                    "align": "center",
                    "margin": "xs"
                },
                {
                    "type": "separator",
                    "margin": "lg",
                    "color": "#DDDDDD"
                },
                {
                    "type": "text",
                    "text": "يمكنك الآن اللعب\nوجمع النقاط",
                    "size": "sm",
                    "color": "#333333",
                    "align": "center",
                    "wrap": True,
                    "margin": "lg"
                }
            ],
            "paddingAll": "20px",
            "backgroundColor": "#F8F8F8"
        }
    }

def get_winner_card_compact(winner_name, winner_score, all_scores):
    """بطاقة الفائز الصغيرة المحسّنة"""
    score_items = []
    for i, (name, score) in enumerate(all_scores[:5], 1):  # أول 5 فقط
        emoji = "▪️" if i == 1 else "▫️"
        score_items.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": f"{emoji} {i}",
                    "size": "xs",
                    "color": "#666666" if i > 1 else "#000000",
                    "flex": 0,
                    "weight": "bold" if i == 1 else "regular"
                },
                {
                    "type": "text",
                    "text": name[:15],  # تحديد طول الاسم
                    "size": "xs",
                    "color": "#333333" if i > 1 else "#000000",
                    "flex": 3,
                    "margin": "sm",
                    "weight": "bold" if i == 1 else "regular"
                },
                {
                    "type": "text",
                    "text": str(score),
                    "size": "xs",
                    "color": "#000000" if i == 1 else "#666666",
                    "flex": 1,
                    "align": "end",
                    "weight": "bold"
                }
            ],
            "margin": "sm" if i > 1 else "none"
        })
    
    return {
        "type": "bubble",
        "size": "kilo",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "انتهت اللعبة",
                    "size": "md",
                    "weight": "bold",
                    "color": "#000000",
                    "align": "center"
                },
                {
                    "type": "separator",
                    "margin": "md",
                    "color": "#DDDDDD"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "▪️",
                            "size": "xl",
                            "color": "#000000",
                            "align": "center"
                        },
                        {
                            "type": "text",
                            "text": winner_name[:20],
                            "size": "lg",
                            "weight": "bold",
                            "color": "#000000",
                            "align": "center",
                            "margin": "xs"
                        },
                        {
                            "type": "text",
                            "text": f"{winner_score} نقطة",
                            "size": "sm",
                            "color": "#666666",
                            "align": "center",
                            "margin": "xs"
                        }
                    ],
                    "backgroundColor": "#F5F5F5",
                    "cornerRadius": "8px",
                    "paddingAll": "12px",
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": score_items,
                    "backgroundColor": "#FAFAFA",
                    "cornerRadius": "8px",
                    "paddingAll": "10px",
                    "margin": "md"
                }
            ],
            "paddingAll": "16px",
            "backgroundColor": "#FFFFFF"
        }
    }

def get_help_card():
    """بطاقة المساعدة المحسّنة"""
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "لوحة الصدارة",
                    "size": "lg",
                    "weight": "bold",
                    "color": "#000000",
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": "أفضل اللاعبين",
                    "size": "xs",
                    "color": "#666666",
                    "align": "center",
                    "margin": "xs"
                },
                {
                    "type": "separator",
                    "margin": "md",
                    "color": "#DDDDDD"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": player_items,
                    "margin": "sm"
                }
            ],
            "backgroundColor": "#FFFFFF",
            "paddingAll": "16px"
        }
    }

def start_game(game_id, game_class, game_type, user_id, event):
    """بدء لعبة جديدة"""
    try:
        with games_lock:
            # التحقق من وجود لعبة نشطة
            if game_id in active_games:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="▪️ يوجد لعبة نشطة بالفعل\nاستخدم 'إيقاف' لإنهائها", 
                                  quick_reply=get_quick_reply())
                )
                return False
            
            # تمرير دوال AI للألعاب التي تحتاجها
            try:
                if game_class in [SongGame, HumanAnimalPlantGame, LettersWordsGame]:
                    game = game_class(line_bot_api, use_ai=USE_AI, ask_ai=ask_gemini)
                else:
                    game = game_class(line_bot_api)
            except Exception as e:
                logger.error(f"❌ خطأ إنشاء اللعبة: {e}")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="حدث خطأ في بدء اللعبة", quick_reply=get_quick_reply())
                )
                return False
            
            with players_lock:
                participants = registered_players.copy()
                participants.add(user_id)
            
            active_games[game_id] = {
                'game': game,
                'type': game_type,
                'created_at': datetime.now(),
                'participants': participants,
                'answered_users': set()
            }
        
        # بدء اللعبة
        try:
            response = game.start_game()
            if isinstance(response, TextSendMessage):
                response.quick_reply = get_quick_reply()
            elif isinstance(response, list):
                for r in response:
                    if isinstance(r, TextSendMessage):
                        r.quick_reply = get_quick_reply()
            
            line_bot_api.reply_message(event.reply_token, response)
            logger.info(f"✅ بدأت لعبة {game_type} للمستخدم {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في start_game: {e}")
            # حذف اللعبة الفاشلة
            with games_lock:
                if game_id in active_games:
                    del active_games[game_id]
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="حدث خطأ في بدء اللعبة", quick_reply=get_quick_reply())
            )
            return False
            
    except Exception as e:
        logger.error(f"❌ خطأ عام في start_game: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="حدث خطأ في بدء اللعبة", quick_reply=get_quick_reply())
        )
        return False

@app.route("/", methods=['GET'])
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>بوت الحُوت</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, sans-serif;
                background: linear-gradient(135deg, #2c2c2c 0%, #1a1a1a 100%);
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
            h1 {{ color: #000; font-size: 2em; margin-bottom: 10px; text-align: center; }}
            .status {{
                background: #F5F5F5;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
            }}
            .status-item {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #DDD;
            }}
            .status-item:last-child {{ border-bottom: none; }}
            .label {{ color: #666; }}
            .value {{ color: #000; font-weight: bold; }}
            .footer {{ text-align: center; margin-top: 20px; color: #999; font-size: 0.8em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>بوت الحُوت</h1>
            <div class="status">
                <div class="status-item">
                    <span class="label">حالة الخادم</span>
                    <span class="value">▪️ يعمل</span>
                </div>
                <div class="status-item">
                    <span class="label">AI Status</span>
                    <span class="value">{'✅ مفعّل' if USE_AI else '⚠️ معطّل'}</span>
                </div>
                <div class="status-item">
                    <span class="label">اللاعبون المسجلون</span>
                    <span class="value">▫️ {len(registered_players)}</span>
                </div>
                <div class="status-item">
                    <span class="label">ألعاب نشطة</span>
                    <span class="value">▫️ {len(active_games)}</span>
                </div>
            </div>
            <div class="footer">بوت الحُوت - منصة ألعاب تفاعلية</div>
        </div>
    </body>
    </html>
    """

@app.route("/health", methods=['GET'])
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_games": len(active_games),
        "registered_players": len(registered_players),
        "ai_enabled": USE_AI
    }, 200

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("❌ توقيع غير صالح")
        abort(400)
    except Exception as e:
        logger.error(f"❌ خطأ webhook: {e}")
    return 'OK'

@app.before_request
def validate_request():
    if request.path == '/callback' and request.method == 'POST':
        if not request.headers.get('X-Line-Signature'):
            abort(400)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """معالج الرسائل الرئيسي"""
    try:
        user_id = event.source.user_id
        text = event.message.text.strip()
        
        if not check_rate_limit(user_id):
            line_bot_api.reply_message(event.reply_token,
                TextSendMessage(text="▫️ انتظر قليلاً", quick_reply=get_quick_reply()))
            return
        
        display_name = get_user_profile_safe(user_id)
        game_id = event.source.group_id if hasattr(event.source, 'group_id') else user_id
        
        logger.info(f"📨 رسالة من {display_name}: {text}")
        
        # الأوامر الأساسية
        if text in ['البداية', 'ابدأ', 'start', 'البوت', 'بوت']:
            line_bot_api.reply_message(event.reply_token,
                FlexSendMessage(alt_text="مرحباً", 
                    contents=get_welcome_card(display_name), quick_reply=get_quick_reply()))
            return
        
        elif text in ['مساعدة', 'help', 'ساعدني']:
            line_bot_api.reply_message(event.reply_token,
                FlexSendMessage(alt_text="المساعدة", 
                    contents=get_help_card(), quick_reply=get_quick_reply()))
            return
        
        elif text in ['نقاطي', 'إحصائياتي', 'احصائياتي']:
            line_bot_api.reply_message(event.reply_token,
                FlexSendMessage(alt_text="إحصائياتك", 
                    contents=get_stats_card(user_id, display_name), quick_reply=get_quick_reply()))
            return
        
        elif text in ['الصدارة', 'المتصدرين', 'صدارة']:
            line_bot_api.reply_message(event.reply_token,
                FlexSendMessage(alt_text="الصدارة", 
                    contents=get_leaderboard_card(), quick_reply=get_quick_reply()))
            return
        
        elif text in ['إيقاف', 'stop', 'توقف']:
            with games_lock:
                if game_id in active_games:
                    game_type = active_games[game_id]['type']
                    del active_games[game_id]
                    line_bot_api.reply_message(event.reply_token,
                        TextSendMessage(text=f"▪️ تم إيقاف لعبة {game_type}", quick_reply=get_quick_reply()))
                else:
                    line_bot_api.reply_message(event.reply_token,
                        TextSendMessage(text="▫️ لا توجد لعبة نشطة", quick_reply=get_quick_reply()))
            return
        
        elif text in ['انضم', 'تسجيل', 'join', 'سجل']:
            with players_lock:
                if user_id in registered_players:
                    line_bot_api.reply_message(event.reply_token,
                        TextSendMessage(text=f"▪️ أنت مسجل بالفعل يا {display_name}",
                            quick_reply=get_quick_reply()))
                else:
                    registered_players.add(user_id)
                    with games_lock:
                        for gid, game_data in active_games.items():
                            if 'participants' not in game_data:
                                game_data['participants'] = set()
                            game_data['participants'].add(user_id)
                    
                    line_bot_api.reply_message(event.reply_token,
                        FlexSendMessage(alt_text="تم التسجيل", 
                            contents=get_registered_card(display_name), quick_reply=get_quick_reply()))
                    logger.info(f"✅ انضم: {display_name}")
            return
        
        elif text in ['انسحب', 'خروج', 'اخرج']:
            with players_lock:
                if user_id in registered_players:
                    registered_players.remove(user_id)
                    line_bot_api.reply_message(event.reply_token,
                        TextSendMessage(text=f"▫️ تم انسحابك يا {display_name}",
                            quick_reply=get_quick_reply()))
                    logger.info(f"❌ انسحب: {display_name}")
                else:
                    line_bot_api.reply_message(event.reply_token,
                        TextSendMessage(text="▫️ أنت غير مسجل", quick_reply=get_quick_reply()))
            return
        
        # الأوامر النصية
        elif text in ['سؤال', 'سوال']:
            if QUESTIONS:
                line_bot_api.reply_message(event.reply_token,
                    TextSendMessage(text=random.choice(QUESTIONS), quick_reply=get_quick_reply()))
            else:
                line_bot_api.reply_message(event.reply_token,
                    TextSendMessage(text="▫️ ملف الأسئلة غير متوفر", quick_reply=get_quick_reply()))
            return
        
        elif text in ['تحدي', 'challenge', 'تحديات']:
            if CHALLENGES:
                line_bot_api.reply_message(event.reply_token,
                    TextSendMessage(text=random.choice(CHALLENGES), quick_reply=get_quick_reply()))
            else:
                line_bot_api.reply_message(event.reply_token,
                    TextSendMessage(text="▫️ ملف التحديات غير متوفر", quick_reply=get_quick_reply()))
            return
        
        elif text in ['اعتراف', 'confession', 'اعترافات']:
            if CONFESSIONS:
                line_bot_api.reply_message(event.reply_token,
                    TextSendMessage(text=random.choice(CONFESSIONS), quick_reply=get_quick_reply()))
            else:
                line_bot_api.reply_message(event.reply_token,
                    TextSendMessage(text="▫️ ملف الاعترافات غير متوفر", quick_reply=get_quick_reply()))
            return
        
        elif text in ['اكثر', 'أكثر', 'more', 'اسئلة']:
            if MORE_QUESTIONS:
                line_bot_api.reply_message(event.reply_token,
                    TextSendMessage(text=random.choice(MORE_QUESTIONS), quick_reply=get_quick_reply()))
            else:
                line_bot_api.reply_message(event.reply_token,
                    TextSendMessage(text="▫️ ملف الأسئلة الإضافية غير متوفر", quick_reply=get_quick_reply()))
            return
        
        # بدء الألعاب
        games_map = {
            'أغنية': (SongGame, 'أغنية'),
            'اغنية': (SongGame, 'أغنية'),
            'لعبة': (HumanAnimalPlantGame, 'لعبة'),
            'سلسلة': (ChainWordsGame, 'سلسلة'),
            'سلسله': (ChainWordsGame, 'سلسلة'),
            'أسرع': (FastTypingGame, 'أسرع'),
            'اسرع': (FastTypingGame, 'أسرع'),
            'ضد': (OppositeGame, 'ضد'),
            'تكوين': (LettersWordsGame, 'تكوين'),
            'اختلاف': (DifferencesGame, 'اختلاف'),
            'توافق': (CompatibilityGame, 'توافق')
        }
        
        if text in games_map:
            game_class, game_type = games_map[text]
            
            # معالجة خاصة للعبة التوافق
            if text in ['توافق']:
                with games_lock:
                    if game_id in active_games:
                        line_bot_api.reply_message(event.reply_token,
                            TextSendMessage(text="▪️ يوجد لعبة نشطة بالفعل\nاستخدم 'إيقاف' لإنهائها", 
                                          quick_reply=get_quick_reply()))
                        return
                    
                    with players_lock:
                        participants = registered_players.copy()
                        participants.add(user_id)
                    
                    try:
                        game = CompatibilityGame(line_bot_api)
                        active_games[game_id] = {
                            'game': game,
                            'type': 'توافق',
                            'created_at': datetime.now(),
                            'participants': participants,
                            'answered_users': set()
                        }
                        line_bot_api.reply_message(event.reply_token,
                            TextSendMessage(text="▪️ لعبة التوافق\n\nاكتب اسمين مفصولين بمسافة\nمثال: أحمد فاطمة",
                                quick_reply=get_quick_reply()))
                        logger.info(f"✅ بدأت لعبة توافق")
                    except Exception as e:
                        logger.error(f"❌ خطأ في لعبة التوافق: {e}")
                        line_bot_api.reply_message(event.reply_token,
                            TextSendMessage(text="حدث خطأ في بدء اللعبة", quick_reply=get_quick_reply()))
                return
            
            # بدء الألعاب الأخرى
            start_game(game_id, game_class, game_type, user_id, event)
            return
        
        # معالجة إجابات الألعاب النشطة
        if game_id in active_games:
            game_data = active_games[game_id]
            
            with players_lock:
                is_registered = user_id in registered_players
            
            if not is_registered:
                return
            
            # منع الإجابة المتكررة من نفس المستخدم
            if 'answered_users' in game_data and user_id in game_data['answered_users']:
                return
            
            game = game_data['game']
            game_type = game_data['type']
            
            try:
                result = game.check_answer(text, user_id, display_name)
                if result:
                    # تسجيل المستخدم كمجيب إذا كانت الإجابة صحيحة
                    if result.get('correct', False):
                        if 'answered_users' not in game_data:
                            game_data['answered_users'] = set()
                        game_data['answered_users'].add(user_id)
                    
                    # تحديث النقاط
                    points = result.get('points', 0)
                    if points > 0:
                        update_user_points(user_id, display_name, points,
                            result.get('won', False), game_type)
                    
                    # الانتقال للسؤال التالي
                    if result.get('next_question', False):
                        game_data['answered_users'] = set()  # إعادة تعيين المجيبين
                        try:
                            next_q = game.next_question()
                            if next_q:
                                if isinstance(next_q, TextSendMessage):
                                    next_q.quick_reply = get_quick_reply()
                                elif isinstance(next_q, list):
                                    for r in next_q:
                                        if isinstance(r, TextSendMessage):
                                            r.quick_reply = get_quick_reply()
                                line_bot_api.reply_message(event.reply_token, next_q)
                        except Exception as e:
                            logger.error(f"❌ خطأ في السؤال التالي: {e}")
                        return
                    
                    # انتهاء اللعبة
                    if result.get('game_over', False):
                        with games_lock:
                            if game_id in active_games:
                                del active_games[game_id]
                        
                        # عرض بطاقة الفائز
                        if result.get('winner_card'):
                            line_bot_api.reply_message(event.reply_token,
                                FlexSendMessage(alt_text="الفائز", 
                                    contents=result['winner_card'], quick_reply=get_quick_reply()))
                        else:
                            response = result.get('response', TextSendMessage(text=result.get('message', '')))
                            if isinstance(response, TextSendMessage):
                                response.quick_reply = get_quick_reply()
                            line_bot_api.reply_message(event.reply_token, response)
                        return
                    
                    # عرض الرد
                    response = result.get('response', TextSendMessage(text=result.get('message', '')))
                    if isinstance(response, TextSendMessage):
                        response.quick_reply = get_quick_reply()
                    elif isinstance(response, list):
                        for r in response:
                            if isinstance(r, TextSendMessage):
                                r.quick_reply = get_quick_reply()
                    line_bot_api.reply_message(event.reply_token, response)
                return
            except Exception as e:
                logger.error(f"❌ خطأ معالجة إجابة اللعبة: {e}")
                return
    
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الرسالة: {e}")

def cleanup_old_games():
    """تنظيف الألعاب القديمة"""
    while True:
        try:
            time.sleep(300)  # كل 5 دقائق
            now = datetime.now()
            to_delete = []
            with games_lock:
                for game_id, game_data in active_games.items():
                    if now - game_data.get('created_at', now) > timedelta(minutes=15):
                        to_delete.append(game_id)
                for game_id in to_delete:
                    del active_games[game_id]
                    logger.info(f"🗑️ حذف لعبة قديمة: {game_id}")
        except Exception as e:
            logger.error(f"❌ خطأ التنظيف: {e}")

cleanup_thread = threading.Thread(target=cleanup_old_games, daemon=True)
cleanup_thread.start()

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"❌ خطأ غير متوقع: {error}", exc_info=True)
    return 'Internal Server Error', 500

@app.errorhandler(404)
def not_found(error):
    return 'Not Found', 404

@app.errorhandler(400)
def bad_request(error):
    return 'Bad Request', 400

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info("="*50)
    logger.info("🚀 بوت الحُوت - بدء التشغيل")
    logger.info(f"🔌 المنفذ: {port}")
    logger.info(f"🤖 AI: {'✅ مفعّل' if USE_AI else '⚠️ معطّل'}")
    logger.info(f"📊 اللاعبون المسجلون: {len(registered_players)}")
    logger.info(f"🎮 الألعاب النشطة: {len(active_games)}")
    logger.info("="*50)
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True) {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "دليل الاستخدام",
                    "size": "xl",
                    "weight": "bold",
                    "color": "#000000",
                    "align": "center"
                },
                {
                    "type": "separator",
                    "margin": "md",
                    "color": "#DDDDDD"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "الأوامر الأساسية",
                            "size": "sm",
                            "weight": "bold",
                            "color": "#000000"
                        },
                        {
                            "type": "text",
                            "text": "▫️ انضم - التسجيل\n▫️ نقاطي - إحصائياتك\n▫️ الصدارة - المتصدرين\n▫️ إيقاف - إنهاء اللعبة",
                            "size": "xs",
                            "color": "#333333",
                            "wrap": True,
                            "margin": "sm"
                        }
                    ],
                    "backgroundColor": "#F5F5F5",
                    "cornerRadius": "8px",
                    "paddingAll": "12px",
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "أثناء اللعب",
                            "size": "sm",
                            "weight": "bold",
                            "color": "#000000"
                        },
                        {
                            "type": "text",
                            "text": "▫️ لمح - تلميح\n▫️ جاوب - عرض الإجابة",
                            "size": "xs",
                            "color": "#333333",
                            "wrap": True,
                            "margin": "sm"
                        }
                    ],
                    "backgroundColor": "#F5F5F5",
                    "cornerRadius": "8px",
                    "paddingAll": "12px",
                    "margin": "sm"
                }
            ],
            "paddingAll": "16px",
            "backgroundColor": "#FFFFFF"
        },
        "footer": {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "button",
                    "action": {"type": "message", "label": "انضم", "text": "انضم"},
                    "style": "primary",
                    "color": "#000000",
                    "height": "sm"
                },
                {
                    "type": "button",
                    "action": {"type": "message", "label": "نقاطي", "text": "نقاطي"},
                    "style": "secondary",
                    "height": "sm"
                }
            ],
            "spacing": "sm",
            "backgroundColor": "#F8F8F8",
            "paddingAll": "12px"
        }
    }

def get_stats_card(user_id, display_name):
    """بطاقة الإحصائيات المحسّنة"""
    stats = get_user_stats(user_id)
    if not stats:
        return {
            "type": "bubble",
            "size": "kilo",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "إحصائياتك",
                        "size": "lg",
                        "weight": "bold",
                        "color": "#000000",
                        "align": "center"
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": "#DDDDDD"
                    },
                    {
                        "type": "text",
                        "text": "لم تبدأ بعد",
                        "size": "sm",
                        "color": "#666666",
                        "align": "center",
                        "margin": "lg"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "ابدأ الآن", "text": "انضم"},
                        "style": "primary",
                        "color": "#000000",
                        "margin": "md",
                        "height": "sm"
                    }
                ],
                "backgroundColor": "#FFFFFF",
                "paddingAll": "16px"
            }
        }
    
    win_rate = (stats['wins'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0
    
    return {
    "type": "bubble",
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": "إحصائياتك",
                "size": "lg",
                "weight": "bold",
                "color": "#000000",
                "align": "center"
            },
            {
                "type": "text",
                "text": display_name[:20],
                "size": "sm",
                "color": "#666666",
                "align": "center",
                "margin": "xs"
            },
            {
                "type": "separator",
                "margin": "md",
                "color": "#DDDDDD"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "النقاط", "size": "xs", "color": "#666666", "flex": 1},
                            {"type": "text", "text": str(stats['total_points']), "size": "xl", "weight": "bold", "color": "#000000", "flex": 1, "align": "end"}
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "sm",
                        "color": "#E5E5E5"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "الألعاب", "size": "xs", "color": "#666666", "flex": 1},
                            {"type": "text", "text": str(stats['games_played']), "size": "sm", "weight": "bold", "color": "#000000", "flex": 1, "align": "end"}
                        ],
                        "margin": "sm"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "الفوز", "size": "xs", "color": "#666666", "flex": 1},
                            {"type": "text", "text": str(stats['wins']), "size": "sm", "weight": "bold", "color": "#000000", "flex": 1, "align": "end"}
                        ],
                        "margin": "xs"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "معدل الفوز", "size": "xs", "color": "#666666", "flex": 1},
                            {"type": "text", "text": f"{win_rate:.0f}%", "size": "sm", "weight": "bold", "color": "#000000", "flex": 1, "align": "end"}
                        ],
                        "margin": "xs"
                    }
                ],
                "backgroundColor": "#F5F5F5",
                "cornerRadius": "8px",
                "paddingAll": "12px",
                "margin": "md"
            }
        ],
        "backgroundColor": "#FFFFFF",
        "paddingAll": "16px"
    },
    "footer": {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "button",
                "action": {"type": "message", "label": "الصدارة", "text": "الصدارة"},
                "style": "secondary",
                "height": "sm"
            }
        ],
        "backgroundColor": "#F8F8F8",
        "paddingAll": "10px"
    }
}

def get_leaderboard_card():
    """لوحة الصدارة المحسّنة"""
    leaders = get_leaderboard()
    if not leaders:
        return {
            "type": "bubble",
            "size": "kilo",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "لوحة الصدارة",
                        "size": "lg",
                        "weight": "bold",
                        "color": "#000000",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "لا توجد بيانات",
                        "size": "sm",
                        "color": "#666666",
                        "align": "center",
                        "margin": "lg"
                    }
                ],
                "backgroundColor": "#FFFFFF",
                "paddingAll": "16px"
            }
        }
    
    player_items = []
    for i, leader in enumerate(leaders[:8], 1):  # أول 8 فقط
        if i == 1:
            bg_color = "#000000"
            text_color = "#FFFFFF"
            rank = "▪️"
        elif i == 2:
            bg_color = "#333333"
            text_color = "#FFFFFF"
            rank = "▪️"
        elif i == 3:
            bg_color = "#666666"
            text_color = "#FFFFFF"
            rank = "▪️"
        else:
            bg_color = "#F5F5F5"
            text_color = "#000000"
            rank = "▫️"
        
        player_items.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {"type": "text", "text": f"{rank} {i}", "size": "xs", "color": text_color, "flex": 0, "weight": "bold"},
                {"type": "text", "text": leader['display_name'][:15], "size": "xs", "color": text_color, "flex": 3, "margin": "sm", "wrap": True},
                {"type": "text", "text": str(leader['total_points']), "size": "xs", "color": text_color, "flex": 1, "align": "end", "weight": "bold"}
            ],
            "backgroundColor": bg_color,
            "cornerRadius": "6px",
            "paddingAll": "10px",
            "margin": "xs" if i > 1 else "md"
        })
    
    return {
        "type": "bubble",
        "body":
