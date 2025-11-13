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
import json
import random
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
        filepath = os.path.join('games', filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                return lines
        return []
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل {filename}: {e}")
        return []

def load_json_file(filename):
    """تحميل ملفات JSON"""
    try:
        filepath = os.path.join('games', filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل {filename}: {e}")
        return None

# تحميل جميع الملفات
QUESTIONS = load_text_file('questions.txt')
CHALLENGES = load_text_file('challenges.txt')
CONFESSIONS = load_text_file('confessions.txt')
MORE_QUESTIONS = load_text_file('more_questions.txt')
PERSONALITY_GAMES = load_json_file('personality_games.json')
TIPS = load_json_file('tips.json')

def get_user_profile_safe(user_id):
    try:
        profile = line_bot_api.get_profile(user_id)
        return profile.display_name
    except Exception as e:
        logger.error(f"❌ خطأ في الملف الشخصي: {e}")
        return "مستخدم"

def get_permanent_quick_reply():
    """الأزرار الثابتة الدائمة"""
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="▫️انضم", text="انضم")),
        QuickReplyButton(action=MessageAction(label="▫️نقاطي", text="نقاطي")),
        QuickReplyButton(action=MessageAction(label="▫️الصدارة", text="الصدارة")),
        QuickReplyButton(action=MessageAction(label="▫️مساعدة", text="مساعدة")),
        QuickReplyButton(action=MessageAction(label="▫️أغنية", text="أغنية")),
        QuickReplyButton(action=MessageAction(label="▫️لعبة", text="لعبة")),
        QuickReplyButton(action=MessageAction(label="▫️سلسلة", text="سلسلة")),
        QuickReplyButton(action=MessageAction(label="▫️أسرع", text="أسرع")),
        QuickReplyButton(action=MessageAction(label="▫️ضد", text="ضد")),
        QuickReplyButton(action=MessageAction(label="▫️تكوين", text="تكوين")),
        QuickReplyButton(action=MessageAction(label="▫️اختلاف", text="اختلاف")),
        QuickReplyButton(action=MessageAction(label="▫️توافق", text="توافق")),
        QuickReplyButton(action=MessageAction(label="▫️إيقاف", text="إيقاف"))
    ])

def get_ios_card(title, items, footer_buttons=None):
    """بطاقة iOS موحدة"""
    contents = [
        {
            "type": "text",
            "text": title,
            "size": "xl",
            "weight": "bold",
            "color": "#1C1C1E",
            "align": "center"
        },
        {
            "type": "separator",
            "margin": "xl",
            "color": "#E5E5EA"
        }
    ]
    
    # إضافة العناصر
    for item in items:
        contents.append({
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": item.get('text', ''),
                    "size": item.get('size', 'sm'),
                    "color": item.get('color', '#1C1C1E'),
                    "wrap": True,
                    "align": item.get('align', 'start'),
                    "weight": item.get('weight', 'regular')
                }
            ],
            "backgroundColor": "#FFFFFF",
            "cornerRadius": "12px",
            "paddingAll": "16px",
            "margin": "md"
        })
    
    # إضافة أزرار القاع
    if footer_buttons:
        button_box = {
            "type": "box",
            "layout": "horizontal",
            "contents": [],
            "spacing": "sm",
            "margin": "xl"
        }
        
        for btn in footer_buttons:
            button_box["contents"].append({
                "type": "button",
                "action": {
                    "type": "message",
                    "label": btn['label'],
                    "text": btn['text']
                },
                "style": btn.get('style', 'secondary'),
                "color": btn.get('color', '#007AFF'),
                "height": "sm"
            })
        
        contents.append(button_box)
    
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": contents,
            "backgroundColor": "#F2F2F7",
            "paddingAll": "20px"
        }
    }

def get_help_card():
    """بطاقة المساعدة"""
    items = [
        {
            "text": "الأوامر الأساسية\n\n▫️ انضم - التسجيل في البوت\n▫️ نقاطي - عرض إحصائياتك\n▫️ الصدارة - أفضل اللاعبين\n▫️ إيقاف - إنهاء اللعبة الحالية",
            "weight": "bold"
        },
        {
            "text": "الألعاب المتاحة\n\n▫️ أغنية - خمن الأغنية\n▫️ لعبة - إنسان حيوان نبات\n▫️ سلسلة - سلسلة الكلمات\n▫️ أسرع - السرعة في الكتابة\n▫️ ضد - الكلمات المعاكسة\n▫️ تكوين - تكوين كلمات\n▫️ اختلاف - لعبة الاختلافات\n▫️ توافق - لعبة التوافق"
        },
        {
            "text": "أوامر إضافية\n\n▫️ سؤال - سؤال عشوائي\n▫️ تحدي - تحدي عشوائي\n▫️ اعتراف - اعتراف عشوائي\n▫️ اكثر - سؤال إضافي\n▫️ نصيحة - نصائح مفيدة"
        },
        {
            "text": "أثناء اللعب\n\n▫️ لمح - الحصول على تلميح\n▫️ جاوب - عرض الإجابة",
            "color": "#8E8E93"
        }
    ]
    
    return get_ios_card(
        "دليل الاستخدام",
        items,
        footer_buttons=[
            {"label": "انضم", "text": "انضم", "style": "primary"},
            {"label": "الألعاب", "text": "البداية"}
        ]
    )

def get_main_menu(display_name):
    """القائمة الرئيسية"""
    items = [
        {
            "text": f"مرحباً {display_name}",
            "size": "md",
            "color": "#007AFF",
            "align": "center",
            "weight": "bold"
        },
        {
            "text": "اختر من الأزرار أدناه أو استخدم الأزرار الثابتة",
            "size": "xs",
            "color": "#8E8E93",
            "align": "center"
        }
    ]
    
    return get_ios_card(
        "منصة الألعاب",
        items,
        footer_buttons=[
            {"label": "انضم", "text": "انضم", "style": "primary"},
            {"label": "نقاطي", "text": "نقاطي"},
            {"label": "الصدارة", "text": "الصدارة"},
            {"label": "مساعدة", "text": "مساعدة"}
        ]
    )

def get_stats_card(user_id, display_name):
    """بطاقة الإحصائيات"""
    stats = get_user_stats(user_id)
    
    if not stats:
        items = [
            {
                "text": "لم تبدأ بعد",
                "size": "lg",
                "align": "center",
                "weight": "bold"
            },
            {
                "text": "ابدأ أول لعبة واجمع النقاط",
                "size": "sm",
                "color": "#8E8E93",
                "align": "center"
            }
        ]
        return get_ios_card("إحصائياتك", items, [{"label": "انضم الآن", "text": "انضم", "style": "primary"}])
    
    win_rate = (stats['wins'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0
    
    items = [
        {
            "text": display_name,
            "size": "md",
            "color": "#007AFF",
            "align": "center",
            "weight": "bold"
        },
        {
            "text": f"النقاط: {stats['total_points']}\nالألعاب: {stats['games_played']}\nالفوز: {stats['wins']}\nمعدل الفوز: {win_rate:.1f}%",
            "size": "sm",
            "weight": "bold"
        }
    ]
    
    return get_ios_card("إحصائياتك", items, [{"label": "الصدارة", "text": "الصدارة"}])

def get_leaderboard_card():
    """لوحة الصدارة"""
    leaders = get_leaderboard()
    
    if not leaders:
        items = [{"text": "لا توجد بيانات بعد", "align": "center"}]
        return get_ios_card("لوحة الصدارة", items)
    
    items = []
    for i, leader in enumerate(leaders, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        items.append({
            "text": f"{medal} {leader['display_name']} - {leader['total_points']} نقطة",
            "size": "sm",
            "weight": "bold" if i <= 3 else "regular"
        })
    
    return get_ios_card("لوحة الصدارة", items, [{"label": "نقاطي", "text": "نقاطي"}])

def get_text_content_card(title, content, command):
    """بطاقة للمحتوى النصي"""
    items = [
        {
            "text": content,
            "size": "sm",
            "align": "center"
        }
    ]
    
    return get_ios_card(
        title,
        items,
        footer_buttons=[{"label": f"{title} آخر", "text": command}]
    )

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
        
        # إضافة الأزرار الثابتة
        if isinstance(response, TextSendMessage):
            response.quick_reply = get_permanent_quick_reply()
        
        line_bot_api.reply_message(event.reply_token, response)
        logger.info(f"✅ بدأت لعبة {game_type}")
        return True
    except Exception as e:
        logger.error(f"❌ خطأ في بدء {game_type}: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=f"❌ حدث خطأ في بدء اللعبة",
                quick_reply=get_permanent_quick_reply()
            )
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
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
                h1 {{ color: #1C1C1E; font-size: 2em; margin-bottom: 10px; }}
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
                <h1>منصة الألعاب</h1>
                <p style="color: #8E8E93; margin: 10px 0;">LINE Bot Game Platform</p>
                <div class="status">
                    <div class="status-item">
                        <span class="label">حالة الخادم</span>
                        <span class="value">يعمل</span>
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
                TextSendMessage(
                    text="⚠️ عدد كبير من الرسائل! انتظر قليلاً.",
                    quick_reply=get_permanent_quick_reply()
                )
            )
            return
        
        display_name = get_user_profile_safe(user_id)
        game_id = event.source.group_id if hasattr(event.source, 'group_id') else user_id
        
        logger.info(f"💬 {display_name}: {text}")
        
        # الأوامر الأساسية
        if text in ['البداية', 'ابدأ', 'start', 'قائمة', 'البوت', 'مرحبا']:
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text="منصة الألعاب",
                    contents=get_main_menu(display_name),
                    quick_reply=get_permanent_quick_reply()
                )
            )
            return
        
        elif text in ['مساعدة', 'help', 'ساعدني', 'الأوامر']:
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text="المساعدة",
                    contents=get_help_card(),
                    quick_reply=get_permanent_quick_reply()
                )
            )
            return
        
        elif text in ['نقاطي', 'إحصائياتي', 'stats']:
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text="إحصائياتك",
                    contents=get_stats_card(user_id, display_name),
                    quick_reply=get_permanent_quick_reply()
                )
            )
            return
        
        elif text in ['الصدارة', 'المتصدرين', 'leaderboard']:
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text="لوحة الصدارة",
                    contents=get_leaderboard_card(),
                    quick_reply=get_permanent_quick_reply()
                )
            )
            return
        
        elif text in ['إيقاف', 'ايقاف', 'stop']:
            with games_lock:
                if game_id in active_games:
                    game_type = active_games[game_id]['type']
                    del active_games[game_id]
                    
                    items = [
                        {"text": f"تم إيقاف لعبة {game_type}", "align": "center"}
                    ]
                    
                    line_bot_api.reply_message(
                        event.reply_token,
                        FlexSendMessage(
                            alt_text="تم الإيقاف",
                            contents=get_ios_card("تم الإيقاف", items, [{"label": "لعبة جديدة", "text": "البداية", "style": "primary"}]),
                            quick_reply=get_permanent_quick_reply()
                        )
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text="لا توجد لعبة نشطة حالياً",
                            quick_reply=get_permanent_quick_reply()
                        )
                    )
            return
        
        elif text in ['انضم', 'تسجيل', 'join']:
            with players_lock:
                if user_id in registered_players:
                    items = [
                        {"text": f"مرحباً {display_name}", "align": "center", "weight": "bold"},
                        {"text": "أنت مسجل بالفعل\nيمكنك اللعب في جميع الألعاب", "align": "center", "color": "#8E8E93"}
                    ]
                    
                    line_bot_api.reply_message(
                        event.reply_token,
                        FlexSendMessage(
                            alt_text="مسجل",
                            contents=get_ios_card("أنت مسجل", items, [{"label": "اختر لعبة", "text": "البداية", "style": "primary"}]),
                            quick_reply=get_permanent_quick_reply()
                        )
                    )
                else:
                    registered_players.add(user_id)
                    
                    with games_lock:
                        for gid, game_data in active_games.items():
                            if 'participants' not in game_data:
                                game_data['participants'] = set()
                            game_data['participants'].add(user_id)
                    
                    items = [
                        {"text": f"مرحباً {display_name}", "align": "center", "size": "lg", "weight": "bold", "color": "#007AFF"},
                        {"text": "تم تسجيلك بنجاح", "align": "center", "weight": "bold"},
                        {"text": "يمكنك الآن اللعب وجمع النقاط", "align": "center", "color": "#8E8E93"}
                    ]
                    
                    line_bot_api.reply_message(
                        event.reply_token,
                        FlexSendMessage(
                            alt_text="تم التسجيل",
                            contents=get_ios_card("تم التسجيل", items, [{"label": "ابدأ اللعب", "text": "البداية", "style": "primary"}]),
                            quick_reply=get_permanent_quick_reply()
                        )
                    )
                    logger.info(f"✅ انضم: {display_name}")
            return
        
        elif text in ['انسحب', 'خروج', 'leave']:
            with players_lock:
                if user_id in registered_players:
                    registered_players.remove(user_id)
                    
                    with games_lock:
                        for gid, game_data in active_games.items():
                            if 'participants' in game_data and user_id in game_data['participants']:
                                game_data['participants'].remove(user_id)
                    
                    items = [
                        {"text": f"إلى اللقاء {display_name}", "align": "center"}
                    ]
                    
                    line_bot_api.reply_message(
                        event.reply_token,
                        FlexSendMessage(
                            alt_text="تم الانسحاب",
                            contents=get_ios_card("تم الانسحاب", items, [{"label": "انضم مجدداً", "text": "انضم"}]),
                            quick_reply=get_permanent_quick_reply()
                        )
                    )
                    logger.info(f"❌ انسحب: {display_name}")
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text="أنت غير مسجل\n\nاكتب 'انضم' للتسجيل",
                            quick_reply=get_permanent_quick_reply()
                        )
                    )
            return
        
        # الأوامر النصية
        elif text in ['سؤال', 'سوال']:
            if QUESTIONS:
                question = random.choice(QUESTIONS)
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text="سؤال",
                        contents=get_text_content_card("سؤال عشوائي", question, "سؤال"),
                        quick_reply=get_permanent_quick_reply()
                    )
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="❌ ملف الأسئلة غير متوفر",
                        quick_reply=get_permanent_quick_reply()
                    )
                )
            return
        
        elif text in ['تحدي', 'challenge']:
            if CHALLENGES:
                challenge = random.choice(CHALLENGES)
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text="تحدي",
                        contents=get_text_content_card("تحدي جديد", challenge, "تحدي"),
                        quick_reply=get_permanent_quick_reply()
                    )
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="❌ ملف التحديات غير متوفر",
                        quick_reply=get_permanent_quick_reply()
                    )
                )
            return
        
        elif text in ['اعتراف', 'confession']:
            if CONFESSIONS:
                confession = random.choice(CONFESSIONS)
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text="اعتراف",
                        contents=get_text_content_card("اعتراف", confession, "اعتراف"),
                        quick_reply=get_permanent_quick_reply()
                    )
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="❌ ملف الاعترافات غير متوفر",
                        quick_reply=get_permanent_quick_reply()
                    )
                )
            return
        
        elif text in ['اكثر', 'أكثر', 'more']:
            if MORE_QUESTIONS:
                more_q = random.choice(MORE_QUESTIONS)
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text="سؤال إضافي",
                        contents=get_text_content_card("سؤال إضافي", more_q, "اكثر"),
                        quick_reply=get_permanent_quick_reply()
                    )
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="❌ ملف الأسئلة الإضافية غير متوفر",
                        quick_reply=get_permanent_quick_reply()
                    )
                )
            return
        
        elif text in ['نصيحة', 'tip', 'نصائح']:
            if TIPS:
                # اختيار فئة عشوائية من النصائح
                categories = list(TIPS.keys())
                category = random.choice(categories)
                tip = random.choice(TIPS[category])
                
                items = [
                    {"text": f"فئة: {category}", "size": "xs", "color": "#8E8E93", "align": "center"},
                    {"text": tip, "size": "sm", "align": "center"}
                ]
                
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text="نصيحة",
                        contents=get_ios_card("نصيحة مفيدة", items, [{"label": "نصيحة أخرى", "text": "نصيحة"}]),
                        quick_reply=get_permanent_quick_reply()
                    )
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="❌ ملف النصائح غير متوفر",
                        quick_reply=get_permanent_quick_reply()
                    )
                )
            return
        
        # بدء الألعاب
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
                
                items = [
                    {"text": "اكتب اسمين مفصولين بمسافة", "align": "center"},
                    {"text": "مثال: أحمد فاطمة", "size": "xs", "color": "#007AFF", "align": "center"}
                ]
                
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text="لعبة التوافق",
                        contents=get_ios_card("لعبة التوافق", items),
                        quick_reply=get_permanent_quick_reply()
                    )
                )
                return
            
            start_game(game_id, game_class, game_type, user_id, event)
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
                    
                    response = result.get('response', TextSendMessage(text=result.get('message', '')))
                    
                    # إضافة الأزرار الثابتة
                    if isinstance(response, TextSendMessage):
                        response.quick_reply = get_permanent_quick_reply()
                    
                    line_bot_api.reply_message(event.reply_token, response)
                return
                
            except Exception as e:
                logger.error(f"❌ خطأ في معالجة اللعبة: {e}")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="❌ حدث خطأ. حاول مرة أخرى.",
                        quick_reply=get_permanent_quick_reply()
                    )
                )
                return
    
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الرسالة: {e}")

# تنظيف الألعاب القديمة
def cleanup_old_games():
    while True:
        try:
            time.sleep(300)  # كل 5 دقائق
            now = datetime.now()
            to_delete = []
            
            with games_lock:
                for game_id, game_data in active_games.items():
                    if now - game_data.get('created_at', now) > timedelta(minutes=10):
                        to_delete.append(game_id)
                
                for game_id in to_delete:
                    del active_games[game_id]
                    logger.info(f"🗑️ تم حذف لعبة قديمة: {game_id}")
        except Exception as e:
            logger.error(f"❌ خطأ في التنظيف: {e}")

cleanup_thread = threading.Thread(target=cleanup_old_games, daemon=True)
cleanup_thread.start()

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
