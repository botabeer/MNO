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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
    logger.info("✅ تم استيراد الألعاب")
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
    except:
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
    except:
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
    try:
        filepath = os.path.join('games', filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        return []
    except:
        return []

def load_json_file(filename):
    try:
        filepath = os.path.join('games', filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except:
        return None

QUESTIONS = load_text_file('questions.txt')
CHALLENGES = load_text_file('challenges.txt')
CONFESSIONS = load_text_file('confessions.txt')
MORE_QUESTIONS = load_text_file('more_questions.txt')
TIPS = load_json_file('tips.json')

def get_user_profile_safe(user_id):
    try:
        profile = line_bot_api.get_profile(user_id)
        return profile.display_name
    except:
        return "مستخدم"

def get_quick_reply():
    """الأزرار الثابتة"""
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="سؤال", text="سؤال")),
        QuickReplyButton(action=MessageAction(label="تحدي", text="تحدي")),
        QuickReplyButton(action=MessageAction(label="اعتراف", text="اعتراف")),
        QuickReplyButton(action=MessageAction(label="اكثر", text="اكثر")),
        QuickReplyButton(action=MessageAction(label="أغنية", text="أغنية")),
        QuickReplyButton(action=MessageAction(label="لعبة", text="لعبة")),
        QuickReplyButton(action=MessageAction(label="سلسلة", text="سلسلة")),
        QuickReplyButton(action=MessageAction(label="أسرع", text="أسرع")),
        QuickReplyButton(action=MessageAction(label="ضد", text="ضد")),
        QuickReplyButton(action=MessageAction(label="تكوين", text="تكوين")),
        QuickReplyButton(action=MessageAction(label="اختلاف", text="اختلاف")),
        QuickReplyButton(action=MessageAction(label="توافق", text="توافق")),
        QuickReplyButton(action=MessageAction(label="مساعدة", text="مساعدة"))
    ])

# =========================
# كود تشغيل السيرفر و Webhook
# =========================
@app.route("/", methods=['GET'])
def home():
    return f"<h1>منصة الألعاب - البوت يعمل</h1>"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# =========================
# معالج الرسائل
# =========================
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()
    display_name = get_user_profile_safe(user_id)

    # تجاهل الرسائل خارج الأوامر
    allowed_commands = ["سؤال","تحدي","اعتراف","اكثر","أغنية","لعبة","سلسلة","أسرع","ضد","تكوين","اختلاف","توافق","مساعدة"]
    if text not in allowed_commands:
        return

    if not check_rate_limit(user_id):
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text="⏱️ رجاءً انتظر قبل إرسال رسالة أخرى", quick_reply=get_quick_reply()))
        return

    if text == "مساعدة":
        card = FlexSendMessage(alt_text="مساعدة", contents=get_help_card())
        line_bot_api.reply_message(event.reply_token, card)
        return

    elif text == "سؤال":
        q = random.choice(QUESTIONS)
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text=f"▫️ سؤال:\n{q}", quick_reply=get_quick_reply()))
        return

    elif text == "تحدي":
        c = random.choice(CHALLENGES)
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text=f"▫️ تحدي:\n{c}", quick_reply=get_quick_reply()))
        return

    elif text == "اعتراف":
        a = random.choice(CONFESSIONS)
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text=f"▫️ اعتراف:\n{a}", quick_reply=get_quick_reply()))
        return

    elif text == "اكثر":
        m = random.choice(MORE_QUESTIONS)
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text=f"▫️ أكثر:\n{m}", quick_reply=get_quick_reply()))
        return

    elif text == "أغنية":
        if 'song_game' not in active_games:
            start_game('song_game', SongGame, 'أغنية', user_id, event)
        return

    elif text == "لعبة":
        if 'human_animal_plant' not in active_games:
            start_game('human_animal_plant', HumanAnimalPlantGame, 'لعبة', user_id, event)
        return

    elif text == "سلسلة":
        if 'chain_words' not in active_games:
            start_game('chain_words', ChainWordsGame, 'سلسلة', user_id, event)
        return

    elif text == "أسرع":
        if 'fast_typing' not in active_games:
            start_game('fast_typing', FastTypingGame, 'أسرع', user_id, event)
        return

    elif text == "ضد":
        if 'opposite' not in active_games:
            start_game('opposite', OppositeGame, 'ضد', user_id, event)
        return

    elif text == "تكوين":
        if 'letters_words' not in active_games:
            start_game('letters_words', LettersWordsGame, 'تكوين', user_id, event)
        return

    elif text == "اختلاف":
        if 'differences' not in active_games:
            start_game('differences', DifferencesGame, 'اختلاف', user_id, event)
        return

    elif text == "توافق":
        if 'compatibility' not in active_games:
            start_game('compatibility', CompatibilityGame, 'توافق', user_id, event)
        return

# =========================
# تنظيف الألعاب القديمة تلقائيًا
# =========================
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
                    logger.info(f"🗑️ حذف لعبة قديمة: {game_id}")
        except Exception as e:
            logger.error(f"❌ خطأ التنظيف: {e}")

cleanup_thread = threading.Thread(target=cleanup_old_games, daemon=True)
cleanup_thread.start()

# =========================
# خطأ عام
# =========================
@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"❌ خطأ: {error}", exc_info=True)
    return 'Internal Server Error', 500

# =========================
# تشغيل السيرفر
# =========================
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 الخادم على المنفذ {port}")
    logger.info(f"📊 اللاعبون المسجلون: {len(registered_players)}")
    logger.info(f"🎮 الألعاب النشطة: {len(active_games)}")
    app.run(host='0.0.0.0', port=port, debug=False)
