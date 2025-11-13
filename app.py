from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    QuickReply, QuickReplyButton, MessageAction,
    FlexSendMessage
)
import os
from datetime import datetime, timedelta
import sqlite3
from collections import defaultdict
import threading
import time
import re
import logging
import random

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
    from games.differences_game import DifferencesGame
    from games.compatibility_game import CompatibilityGame
    logger.info("✅ تم استيراد جميع الألعاب بنجاح")
except Exception as e:
    logger.error(f"❌ خطأ في استيراد الألعاب: {e}")

app = Flask(__name__)

# إعدادات LINE Bot
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'YOUR_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', 'YOUR_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# تخزين البيانات
active_games = {}
registered_players = set()
user_message_count = defaultdict(lambda: {'count': 0, 'reset_time': datetime.now()})

# أقفال thread-safe
games_lock = threading.Lock()
players_lock = threading.Lock()

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
        
        c.execute('''CREATE INDEX IF NOT EXISTS idx_user_points 
                     ON users(total_points DESC)''')
        
        conn.commit()
        conn.close()
        logger.info("✅ تم إنشاء قاعدة البيانات")
    except Exception as e:
        logger.error(f"❌ خطأ في قاعدة البيانات: {e}")

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
        logger.error(f"❌ خطأ في تحديث النقاط: {e}")
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
        logger.error(f"❌ خطأ في الإحصائيات: {e}")
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
        logger.error(f"❌ خطأ في الصدارة: {e}")
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

def load_text_file(filename):
    """تحميل محتوى الملفات النصية"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            return lines
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل {filename}: {e}")
        return []

# تحميل الملفات النصية
QUESTIONS = load_text_file('questions.txt')
CHALLENGES = load_text_file('challenges.txt')
CONFESSIONS = load_text_file('confessions.txt')
MORE_QUESTIONS = load_text_file('more_questions.txt')

def get_user_profile_safe(user_id):
    try:
        profile = line_bot_api.get_profile(user_id)
        return profile.display_name
    except Exception as e:
        logger.error(f"❌ خطأ في الملف الشخصي: {e}")
        return "مستخدم"

def get_ios_style_card(title, subtitle, emoji, items):
    """تصميم بطاقة بأسلوب iOS - ظل خفيف وأنيق"""
    game_items = []
    
    for item in items:
        game_items.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": item['emoji'],
                    "size": "xl",
                    "flex": 0,
                    "align": "center"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": item['name'],
                            "size": "md",
                            "weight": "bold",
                            "color": "#1C1C1E"
                        },
                        {
                            "type": "text",
                            "text": item['description'],
                            "size": "xs",
                            "color": "#8E8E93",
                            "margin": "xs"
                        }
                    ],
                    "margin": "md",
                    "flex": 1
                },
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "▶",
                        "text": item['command']
                    },
                    "style": "link",
                    "height": "sm",
                    "flex": 0
                }
            ],
            "backgroundColor": "#FFFFFF",
            "cornerRadius": "12px",
            "paddingAll": "16px",
            "margin": "sm" if game_items else "none",
            "spacing": "md"
        })
    
    return {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": emoji,
                            "size": "3xl",
                            "flex": 0
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": title,
                                    "size": "xl",
                                    "weight": "bold",
                                    "color": "#1C1C1E"
                                },
                                {
                                    "type": "text",
                                    "text": subtitle,
                                    "size": "sm",
                                    "color": "#8E8E93",
                                    "margin": "xs"
                                }
                            ],
                            "margin": "md"
                        }
                    ],
                    "spacing": "md",
                    "margin": "none"
                },
                {
                    "type": "separator",
                    "margin": "xl",
                    "color": "#E5E5EA"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": game_items,
                    "margin": "xl",
                    "spacing": "none"
                }
            ],
            "backgroundColor": "#F2F2F7",
            "paddingAll": "20px"
        }
    }

def get_main_menu(display_name):
    """القائمة الرئيسية بتصميم iOS"""
    games = [
        {"emoji": "🎵", "name": "أغنية", "description": "خمن الأغنية", "command": "أغنية"},
        {"emoji": "🎮", "name": "لعبة", "description": "إنسان حيوان نبات", "command": "لعبة"},
        {"emoji": "🔗", "name": "سلسلة", "description": "سلسلة الكلمات", "command": "سلسلة"},
        {"emoji": "⚡", "name": "أسرع", "description": "السرعة في الكتابة", "command": "أسرع"}
    ]
    
    return get_ios_style_card(
        title="منصة الألعاب",
        subtitle=f"مرحباً {display_name}",
        emoji="🎯",
        items=games
    )

def get_more_games_menu():
    """المزيد من الألعاب"""
    games = [
        {"emoji": "🔄", "name": "ضد", "description": "الكلمات المعاكسة", "command": "ضد"},
        {"emoji": "✨", "name": "تكوين", "description": "تكوين كلمات", "command": "تكوين"},
        {"emoji": "🔍", "name": "اختلاف", "description": "لعبة الاختلافات", "command": "اختلاف"},
        {"emoji": "💖", "name": "توافق", "description": "لعبة التوافق", "command": "توافق"}
    ]
    
    return get_ios_style_card(
        title="ألعاب إضافية",
        subtitle="اختر لعبتك المفضلة",
        emoji="🎲",
        items=games
    )

def get_commands_menu():
    """قائمة الأوامر النصية"""
    commands = [
        {"emoji": "❓", "name": "سؤال", "description": "سؤال عشوائي", "command": "سؤال"},
        {"emoji": "🏆", "name": "تحدي", "description": "تحدي عشوائي", "command": "تحدي"},
        {"emoji": "💬", "name": "اعتراف", "description": "اعتراف عشوائي", "command": "اعتراف"},
        {"emoji": "➕", "name": "اكثر", "description": "سؤال إضافي", "command": "اكثر"}
    ]
    
    return get_ios_style_card(
        title="أوامر إضافية",
        subtitle="محتوى نصي متنوع",
        emoji="📝",
        items=commands
    )

def get_stats_card(user_id, display_name):
    """بطاقة الإحصائيات بأسلوب iOS"""
    stats = get_user_stats(user_id)
    
    if not stats:
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "لم تبدأ بعد",
                        "size": "xl",
                        "weight": "bold",
                        "color": "#1C1C1E",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "ابدأ أول لعبة واجمع النقاط",
                        "size": "sm",
                        "color": "#8E8E93",
                        "align": "center",
                        "margin": "md",
                        "wrap": True
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "انضم الآن",
                            "text": "انضم"
                        },
                        "style": "primary",
                        "color": "#007AFF",
                        "margin": "xl"
                    }
                ],
                "backgroundColor": "#F2F2F7",
                "paddingAll": "30px"
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
                    "size": "xl",
                    "weight": "bold",
                    "color": "#1C1C1E",
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": display_name,
                    "size": "sm",
                    "color": "#8E8E93",
                    "align": "center",
                    "margin": "sm"
                },
                {
                    "type": "separator",
                    "margin": "xl",
                    "color": "#E5E5EA"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "النقاط",
                                    "size": "sm",
                                    "color": "#8E8E93",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": str(stats['total_points']),
                                    "size": "xl",
                                    "weight": "bold",
                                    "color": "#007AFF",
                                    "align": "end",
                                    "flex": 1
                                }
                            ],
                            "backgroundColor": "#FFFFFF",
                            "cornerRadius": "12px",
                            "paddingAll": "16px"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": str(stats['games_played']),
                                            "size": "lg",
                                            "weight": "bold",
                                            "color": "#1C1C1E",
                                            "align": "center"
                                        },
                                        {
                                            "type": "text",
                                            "text": "ألعاب",
                                            "size": "xs",
                                            "color": "#8E8E93",
                                            "align": "center",
                                            "margin": "xs"
                                        }
                                    ],
                                    "backgroundColor": "#FFFFFF",
                                    "cornerRadius": "12px",
                                    "paddingAll": "16px",
                                    "flex": 1
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": str(stats['wins']),
                                            "size": "lg",
                                            "weight": "bold",
                                            "color": "#34C759",
                                            "align": "center"
                                        },
                                        {
                                            "type": "text",
                                            "text": "فوز",
                                            "size": "xs",
                                            "color": "#8E8E93",
                                            "align": "center",
                                            "margin": "xs"
                                        }
                                    ],
                                    "backgroundColor": "#FFFFFF",
                                    "cornerRadius": "12px",
                                    "paddingAll": "16px",
                                    "flex": 1
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": f"{win_rate:.0f}%",
                                            "size": "lg",
                                            "weight": "bold",
                                            "color": "#FF9500",
                                            "align": "center"
                                        },
                                        {
                                            "type": "text",
                                            "text": "معدل",
                                            "size": "xs",
                                            "color": "#8E8E93",
                                            "align": "center",
                                            "margin": "xs"
                                        }
                                    ],
                                    "backgroundColor": "#FFFFFF",
                                    "cornerRadius": "12px",
                                    "paddingAll": "16px",
                                    "flex": 1
                                }
                            ],
                            "spacing": "sm",
                            "margin": "sm"
                        }
                    ],
                    "margin": "xl",
                    "spacing": "none"
                }
            ],
            "backgroundColor": "#F2F2F7",
            "paddingAll": "20px"
        }
    }

def get_leaderboard_card():
    """لوحة الصدارة بأسلوب iOS"""
    leaders = get_leaderboard()
    
    if not leaders:
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "لا توجد بيانات",
                        "size": "xl",
                        "weight": "bold",
                        "color": "#1C1C1E",
                        "align": "center"
                    }
                ],
                "backgroundColor": "#F2F2F7",
                "paddingAll": "30px"
            }
        }
    
    player_items = []
    for i, leader in enumerate(leaders, 1):
        if i == 1:
            medal = "🥇"
            bg_color = "#FFD700"
            text_color = "#1C1C1E"
        elif i == 2:
            medal = "🥈"
            bg_color = "#C0C0C0"
            text_color = "#1C1C1E"
        elif i == 3:
            medal = "🥉"
            bg_color = "#CD7F32"
            text_color = "#FFFFFF"
        else:
            medal = f"{i}"
            bg_color = "#FFFFFF"
            text_color = "#1C1C1E"
        
        player_items.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": medal if i > 3 else medal,
                    "size": "md" if i > 3 else "xl",
                    "weight": "bold",
                    "color": text_color if i <= 3 else "#8E8E93",
                    "flex": 0,
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": leader['display_name'],
                    "size": "sm",
                    "weight": "bold" if i <= 3 else "regular",
                    "color": text_color if i <= 3 else "#1C1C1E",
                    "flex": 3,
                    "margin": "md"
                },
                {
                    "type": "text",
                    "text": str(leader['total_points']),
                    "size": "sm",
                    "weight": "bold",
                    "color": text_color if i <= 3 else "#007AFF",
                    "flex": 1,
                    "align": "end"
                }
            ],
            "backgroundColor": bg_color,
            "cornerRadius": "12px",
            "paddingAll": "14px",
            "margin": "sm" if i > 1 else "none",
            "spacing": "md"
        })
    
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": "🏆",
                            "size": "3xl",
                            "flex": 0
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "لوحة الصدارة",
                                    "size": "xl",
                                    "weight": "bold",
                                    "color": "#1C1C1E"
                                },
                                {
                                    "type": "text",
                                    "text": "أفضل اللاعبين",
                                    "size": "sm",
                                    "color": "#8E8E93",
                                    "margin": "xs"
                                }
                            ],
                            "margin": "md"
                        }
                    ],
                    "spacing": "md"
                },
                {
                    "type": "separator",
                    "margin": "xl",
                    "color": "#E5E5EA"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": player_items,
                    "margin": "xl",
                    "spacing": "none"
                }
            ],
            "backgroundColor": "#F2F2F7",
            "paddingAll": "20px"
        }
    }

def start_game(game_id, game_class, game_type, user_id, event):
    """بدء لعبة جديدة"""
    try:
        with games_lock:
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
        logger.info(f"✅ بدأت لعبة {game_type}")
        return True
    except Exception as e:
        logger.error(f"❌ خطأ في بدء {game_type}: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"❌ حدث خطأ في بدء اللعبة")
        )
        return False

@app.route("/", methods=['GET'])
def home():
    return f"""
    <html>
        <head>
            <title>LINE Bot - Game Platform</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }}
                .container {{
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    padding: 40px;
                    max-width: 500px;
                    width: 100%;
                    text-align: center;
                }}
                h1 {{ 
                    color: #1C1C1E;
                    font-size: 2em;
                    margin-bottom: 10px;
                }}
                .emoji {{ font-size: 3em; margin: 20px 0; }}
                .status {{
                    background: #F2F2F7;
                    border-radius: 12px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .status-item {{
                    display: flex;
                    justify-content: space-between;
                    padding: 10px 0;
                    border-bottom: 1px solid #E5E5EA;
                }}
                .status-item:last-child {{ border-bottom: none; }}
                .label {{ color: #8E8E93; font-size: 0.9em; }}
                .value {{ color: #007AFF; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="emoji">🎮</div>
                <h1>منصة الألعاب</h1>
                <p style="color: #8E8E93; margin: 10px 0;">LINE Bot Game Platform</p>
                <div class="status">
                    <div class="status-item">
                        <span class="label">حالة الخادم</span>
                        <span class="value">✅ يعمل</span>
                    </div>
                    <div class="status-item">
                        <span class="label">عدد الألعاب</span>
                        <span class="value">8 ألعاب</span>
                    </div>
                    <div class="status-item">
                        <span class="label">اللاعبون</span>
                        <span class="value">{len(registered_players)}</span>
                    </div>
                    <div class="status-item">
                        <span class="label">ألعاب نشطة</span>
                        <span class="value">{len(active_games)}</span>
                    </div>
                </div>
                <p style="color: #8E8E93; font-size: 0.85em; margin-top: 20px;">
                    تم التطوير بواسطة عبير الدوسري
                </p>
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
        logger.error("❌ توقيع غير صالح")
        abort(400)
    except Exception as e:
        logger.error(f"❌ خطأ في webhook: {e}")
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """معالج الرسائل الرئيسي"""
    try:
        user_id = event.source.user_id
        text = event.message.text.strip()
        
        if not check_rate_limit(user_id):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="⚠️ عدد كبير من الرسائل! انتظر قليلاً.")
            )
            return
        
        display_name = get_user_profile_safe(user_id)
        game_id = event.source.group_id if hasattr(event.source, 'group_id') else user_id
        
        logger.info(f"💬 {display_name}: {text}")
        
        # ═══════════════════════════════════════════
        # الأوامر الأساسية
        # ═══════════════════════════════════════════
        
        if text in ['البداية', 'ابدأ', 'start', 'قائمة', 'البوت', 'مرحبا', 'السلام عليكم']:
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text="منصة الألعاب",
                    contents=get_main_menu(display_name)
                )
            )
            return
        
        elif text in ['المزيد', 'أكثر', 'more', 'مزيد']:
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text="ألعاب إضافية",
                    contents=get_more_games_menu()
                )
            )
            return
        
        elif text in ['أوامر', 'الأوامر', 'commands']:
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text="الأوامر",
                    contents=get_commands_menu()
                )
            )
            return
        
        elif text in ['نقاطي', 'إحصائياتي', 'stats', 'النقاط']:
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text="إحصائياتك",
                    contents=get_stats_card(user_id, display_name)
                )
            )
            return
        
        elif text in ['الصدارة', 'المتصدرين', 'leaderboard', 'top']:
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text="لوحة الصدارة",
                    contents=get_leaderboard_card()
                )
            )
            return
        
        elif text in ['إيقاف', 'ايقاف', 'stop', 'انهاء']:
            with games_lock:
                if game_id in active_games:
                    game_type = active_games[game_id]['type']
                    del active_games[game_id]
                    
                    card = {
                        "type": "bubble",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "تم الإيقاف",
                                    "size": "xl",
                                    "weight": "bold",
                                    "color": "#1C1C1E",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": f"تم إيقاف لعبة {game_type}",
                                    "size": "sm",
                                    "color": "#8E8E93",
                                    "align": "center",
                                    "margin": "md"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "ابدأ لعبة جديدة",
                                        "text": "البداية"
                                    },
                                    "style": "primary",
                                    "color": "#007AFF",
                                    "margin": "xl"
                                }
                            ],
                            "backgroundColor": "#F2F2F7",
                            "paddingAll": "30px"
                        }
                    }
                    
                    line_bot_api.reply_message(
                        event.reply_token,
                        FlexSendMessage(alt_text="تم الإيقاف", contents=card)
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="لا توجد لعبة نشطة حالياً")
                    )
            return
        
        elif text in ['انضم', 'تسجيل', 'join', 'سجل']:
            with players_lock:
                if user_id in registered_players:
                    card = {
                        "type": "bubble",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "أنت مسجل بالفعل",
                                    "size": "xl",
                                    "weight": "bold",
                                    "color": "#34C759",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": f"مرحباً {display_name}\nيمكنك اللعب في جميع الألعاب",
                                    "size": "sm",
                                    "color": "#8E8E93",
                                    "align": "center",
                                    "margin": "md",
                                    "wrap": True
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "اختر لعبة",
                                        "text": "البداية"
                                    },
                                    "style": "primary",
                                    "color": "#007AFF",
                                    "margin": "xl"
                                }
                            ],
                            "backgroundColor": "#F2F2F7",
                            "paddingAll": "30px"
                        }
                    }
                    
                    line_bot_api.reply_message(
                        event.reply_token,
                        FlexSendMessage(alt_text="مسجل", contents=card)
                    )
                else:
                    registered_players.add(user_id)
                    
                    with games_lock:
                        for gid, game_data in active_games.items():
                            if 'participants' not in game_data:
                                game_data['participants'] = set()
                            game_data['participants'].add(user_id)
                    
                    card = {
                        "type": "bubble",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "🎉",
                                    "size": "3xl",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": "تم التسجيل بنجاح",
                                    "size": "xl",
                                    "weight": "bold",
                                    "color": "#1C1C1E",
                                    "align": "center",
                                    "margin": "md"
                                },
                                {
                                    "type": "text",
                                    "text": f"مرحباً بك {display_name}",
                                    "size": "md",
                                    "color": "#007AFF",
                                    "align": "center",
                                    "margin": "sm"
                                },
                                {
                                    "type": "separator",
                                    "margin": "xl",
                                    "color": "#E5E5EA"
                                },
                                {
                                    "type": "text",
                                    "text": "يمكنك الآن:\n• اللعب في جميع الألعاب\n• جمع النقاط\n• المنافسة على الصدارة",
                                    "size": "sm",
                                    "color": "#8E8E93",
                                    "align": "center",
                                    "wrap": True,
                                    "margin": "xl"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "ابدأ اللعب الآن",
                                        "text": "البداية"
                                    },
                                    "style": "primary",
                                    "color": "#007AFF",
                                    "margin": "xl"
                                }
                            ],
                            "backgroundColor": "#F2F2F7",
                            "paddingAll": "30px"
                        }
                    }
                    
                    line_bot_api.reply_message(
                        event.reply_token,
                        FlexSendMessage(alt_text="تم التسجيل", contents=card)
                    )
                    logger.info(f"✅ انضم: {display_name}")
            return
        
        elif text in ['انسحب', 'خروج', 'leave', 'إلغاء']:
            with players_lock:
                if user_id in registered_players:
                    registered_players.remove(user_id)
                    
                    with games_lock:
                        for gid, game_data in active_games.items():
                            if 'participants' in game_data and user_id in game_data['participants']:
                                game_data['participants'].remove(user_id)
                    
                    card = {
                        "type": "bubble",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "تم الانسحاب",
                                    "size": "xl",
                                    "weight": "bold",
                                    "color": "#FF3B30",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": f"إلى اللقاء {display_name}",
                                    "size": "sm",
                                    "color": "#8E8E93",
                                    "align": "center",
                                    "margin": "md"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "انضم مجدداً",
                                        "text": "انضم"
                                    },
                                    "style": "secondary",
                                    "margin": "xl"
                                }
                            ],
                            "backgroundColor": "#F2F2F7",
                            "paddingAll": "30px"
                        }
                    }
                    
                    line_bot_api.reply_message(
                        event.reply_token,
                        FlexSendMessage(alt_text="تم الانسحاب", contents=card)
                    )
                    logger.info(f"❌ انسحب: {display_name}")
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="أنت غير مسجل\n\nاكتب 'انضم' للتسجيل")
                    )
            return
        
        # ═══════════════════════════════════════════
        # الأوامر النصية (من الملفات)
        # ═══════════════════════════════════════════
        
        elif text in ['سؤال', 'سوال']:
            if QUESTIONS:
                question = random.choice(QUESTIONS)
                card = {
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "❓",
                                "size": "3xl",
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "سؤال عشوائي",
                                "size": "md",
                                "weight": "bold",
                                "color": "#1C1C1E",
                                "align": "center",
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "xl",
                                "color": "#E5E5EA"
                            },
                            {
                                "type": "text",
                                "text": question,
                                "size": "sm",
                                "color": "#1C1C1E",
                                "wrap": True,
                                "margin": "xl",
                                "align": "center"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "سؤال آخر",
                                    "text": "سؤال"
                                },
                                "style": "primary",
                                "color": "#007AFF",
                                "margin": "xl"
                            }
                        ],
                        "backgroundColor": "#F2F2F7",
                        "paddingAll": "30px"
                    }
                }
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(alt_text="سؤال", contents=card)
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="❌ ملف الأسئلة غير متوفر")
                )
            return
        
        elif text in ['تحدي', 'challenge']:
            if CHALLENGES:
                challenge = random.choice(CHALLENGES)
                card = {
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🏆",
                                "size": "3xl",
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "تحدي جديد",
                                "size": "md",
                                "weight": "bold",
                                "color": "#1C1C1E",
                                "align": "center",
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "xl",
                                "color": "#E5E5EA"
                            },
                            {
                                "type": "text",
                                "text": challenge,
                                "size": "sm",
                                "color": "#1C1C1E",
                                "wrap": True,
                                "margin": "xl",
                                "align": "center"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "تحدي آخر",
                                    "text": "تحدي"
                                },
                                "style": "primary",
                                "color": "#FF9500",
                                "margin": "xl"
                            }
                        ],
                        "backgroundColor": "#F2F2F7",
                        "paddingAll": "30px"
                    }
                }
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(alt_text="تحدي", contents=card)
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="❌ ملف التحديات غير متوفر")
                )
            return
        
        elif text in ['اعتراف', 'confession']:
            if CONFESSIONS:
                confession = random.choice(CONFESSIONS)
                card = {
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "💬",
                                "size": "3xl",
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "اعتراف",
                                "size": "md",
                                "weight": "bold",
                                "color": "#1C1C1E",
                                "align": "center",
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "xl",
                                "color": "#E5E5EA"
                            },
                            {
                                "type": "text",
                                "text": confession,
                                "size": "sm",
                                "color": "#1C1C1E",
                                "wrap": True,
                                "margin": "xl",
                                "align": "center"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "اعتراف آخر",
                                    "text": "اعتراف"
                                },
                                "style": "primary",
                                "color": "#34C759",
                                "margin": "xl"
                            }
                        ],
                        "backgroundColor": "#F2F2F7",
                        "paddingAll": "30px"
                    }
                }
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(alt_text="اعتراف", contents=card)
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="❌ ملف الاعترافات غير متوفر")
                )
            return
        
        elif text in ['اكثر', 'أكثر', 'more']:
            if MORE_QUESTIONS:
                more_q = random.choice(MORE_QUESTIONS)
                card = {
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "➕",
                                "size": "3xl",
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "سؤال إضافي",
                                "size": "md",
                                "weight": "bold",
                                "color": "#1C1C1E",
                                "align": "center",
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "xl",
                                "color": "#E5E5EA"
                            },
                            {
                                "type": "text",
                                "text": more_q,
                                "size": "sm",
                                "color": "#1C1C1E",
                                "wrap": True,
                                "margin": "xl",
                                "align": "center"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "سؤال آخر",
                                    "text": "اكثر"
                                },
                                "style": "primary",
                                "color": "#5856D6",
                                "margin": "xl"
                            }
                        ],
                        "backgroundColor": "#F2F2F7",
                        "paddingAll": "30px"
                    }
                }
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(alt_text="سؤال إضافي", contents=card)
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="❌ ملف الأسئلة الإضافية غير متوفر")
                )
            return
        
        # ═══════════════════════════════════════════
        # بدء الألعاب
        # ═══════════════════════════════════════════
        
        games_map = {
            'أغنية': (SongGame, 'أغنية'),
            'لعبة': (HumanAnimalPlantGame, 'لعبة'),
            'سلسلة': (ChainWordsGame, 'سلسلة'),
            'أسرع': (FastTypingGame, 'أسرع'),
            'ضد': (OppositeGame, 'ضد'),
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
                
                card = {
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "💖",
                                "size": "3xl",
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "لعبة التوافق",
                                "size": "xl",
                                "weight": "bold",
                                "color": "#1C1C1E",
                                "align": "center",
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "xl",
                                "color": "#E5E5EA"
                            },
                            {
                                "type": "text",
                                "text": "اكتب اسمين مفصولين بمسافة",
                                "size": "sm",
                                "color": "#8E8E93",
                                "align": "center",
                                "margin": "xl",
                                "wrap": True
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "مثال: أحمد فاطمة",
                                        "size": "xs",
                                        "color": "#007AFF",
                                        "align": "center"
                                    }
                                ],
                                "backgroundColor": "#FFFFFF",
                                "cornerRadius": "8px",
                                "paddingAll": "12px",
                                "margin": "lg"
                            }
                        ],
                        "backgroundColor": "#F2F2F7",
                        "paddingAll": "30px"
                    }
                }
                
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(alt_text="لعبة التوافق", contents=card)
                )
                return
            
            start_game(game_id, game_class, game_type, user_id, event)
            return
        
        # ═══════════════════════════════════════════
        # معالجة إجابات الألعاب النشطة
        # ═══════════════════════════════════════════
        
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
                    
                    response = result.get('response', TextSendMessage(text=result.get('message', '')))
                    line_bot_api.reply_message(event.reply_token, response)
                return
                
            except Exception as e:
                logger.error(f"❌ خطأ في معالجة اللعبة: {e}")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="❌ حدث خطأ. حاول مرة أخرى.")
                )
                return
    
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الرسالة: {e}")

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"❌ خطأ غير متوقع: {error}", exc_info=True)
    return 'Internal Server Error', 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 بدء الخادم على المنفذ {port}")
    logger.info(f"📊 اللاعبون المسجلون: {len(registered_players)}")
    logger.info(f"🎮 الألعاب النشطة: {len(active_games)}")
    app.run(host='0.0.0.0', port=port, debug=False)
