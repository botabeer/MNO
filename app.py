from flask import Flask, request, abort, jsonify
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

# المتغيرات العامة
active_games = {}
registered_players = set()
user_message_count = defaultdict(lambda: {'count': 0, 'reset_time': datetime.now()})

# قفل للمعالجة المتزامنة
games_lock = threading.Lock()
players_lock = threading.Lock()

# قاعدة البيانات
DB_NAME = 'game_scores.db'

def get_db_connection():
    """إنشاء اتصال بقاعدة البيانات"""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """تهيئة قاعدة البيانات"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # جدول المستخدمين
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            total_points INTEGER DEFAULT 0,
            games_played INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            last_played TEXT,
            registered_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # جدول تاريخ الألعاب
        c.execute('''CREATE TABLE IF NOT EXISTS game_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            game_type TEXT NOT NULL,
            points INTEGER DEFAULT 0,
            won INTEGER DEFAULT 0,
            played_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )''')
        
        # فهرس للأداء
        c.execute('''CREATE INDEX IF NOT EXISTS idx_user_points 
                     ON users(total_points DESC)''')
        
        conn.commit()
        conn.close()
        logger.info("✅ قاعدة البيانات جاهزة")
    except Exception as e:
        logger.error(f"❌ خطأ في تهيئة قاعدة البيانات: {e}")

init_db()

def update_user_points(user_id, display_name, points, won=False, game_type=""):
    """تحديث نقاط المستخدم"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # التحقق من وجود المستخدم
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = c.fetchone()
        
        if user:
            # تحديث بيانات المستخدم
            c.execute('''UPDATE users 
                         SET total_points = ?, 
                             games_played = ?, 
                             wins = ?, 
                             last_played = ?, 
                             display_name = ? 
                         WHERE user_id = ?''',
                      (user['total_points'] + points,
                       user['games_played'] + 1,
                       user['wins'] + (1 if won else 0),
                       datetime.now().isoformat(),
                       display_name,
                       user_id))
        else:
            # إضافة مستخدم جديد
            c.execute('''INSERT INTO users 
                         (user_id, display_name, total_points, games_played, wins, last_played) 
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (user_id, display_name, points, 1, 1 if won else 0, 
                       datetime.now().isoformat()))
        
        # حفظ السجل
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
    """الحصول على إحصائيات المستخدم"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = c.fetchone()
        conn.close()
        return user
    except Exception as e:
        logger.error(f"❌ خطأ في جلب الإحصائيات: {e}")
        return None

def get_leaderboard(limit=10):
    """الحصول على لوحة الصدارة"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''SELECT display_name, total_points, games_played, wins 
                     FROM users 
                     ORDER BY total_points DESC 
                     LIMIT ?''', (limit,))
        leaders = c.fetchall()
        conn.close()
        return leaders
    except Exception as e:
        logger.error(f"❌ خطأ في جلب الصدارة: {e}")
        return []

def check_rate_limit(user_id, max_messages=20, time_window=60):
    """فحص حد الرسائل"""
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
    """تحميل ملف نصي"""
    try:
        filepath = os.path.join('games', filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        logger.warning(f"⚠️ الملف غير موجود: {filename}")
        return []
    except Exception as e:
        logger.error(f"❌ خطأ في قراءة الملف {filename}: {e}")
        return []

def load_json_file(filename):
    """تحميل ملف JSON"""
    try:
        filepath = os.path.join('games', filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        logger.warning(f"⚠️ الملف غير موجود: {filename}")
        return None
    except Exception as e:
        logger.error(f"❌ خطأ في قراءة الملف {filename}: {e}")
        return None

# تحميل البيانات
QUESTIONS = load_text_file('questions.txt')
CHALLENGES = load_text_file('challenges.txt')
CONFESSIONS = load_text_file('confessions.txt')
MORE_QUESTIONS = load_text_file('more_questions.txt')
TIPS = load_json_file('tips.json')

def get_user_profile_safe(user_id):
    """الحصول على اسم المستخدم بشكل آمن"""
    try:
        profile = line_bot_api.get_profile(user_id)
        return profile.display_name
    except Exception as e:
        logger.error(f"❌ خطأ في جلب الملف الشخصي: {e}")
        return "مستخدم"

def get_quick_reply():
    """قائمة الأزرار السريعة - تصميم iOS"""
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="💭 سؤال", text="سؤال")),
        QuickReplyButton(action=MessageAction(label="🎯 تحدي", text="تحدي")),
        QuickReplyButton(action=MessageAction(label="🔓 اعتراف", text="اعتراف")),
        QuickReplyButton(action=MessageAction(label="➕ اكثر", text="اكثر")),
        QuickReplyButton(action=MessageAction(label="🎵 أغنية", text="أغنية")),
        QuickReplyButton(action=MessageAction(label="🎮 لعبة", text="لعبة")),
        QuickReplyButton(action=MessageAction(label="🔗 سلسلة", text="سلسلة")),
        QuickReplyButton(action=MessageAction(label="⚡ أسرع", text="أسرع")),
        QuickReplyButton(action=MessageAction(label="🔄 ضد", text="ضد")),
        QuickReplyButton(action=MessageAction(label="🔤 تكوين", text="تكوين")),
        QuickReplyButton(action=MessageAction(label="🔍 اختلاف", text="اختلاف")),
        QuickReplyButton(action=MessageAction(label="💕 توافق", text="توافق")),
        QuickReplyButton(action=MessageAction(label="ℹ️ مساعدة", text="مساعدة"))
    ])

def get_help_card():
    """بطاقة المساعدة - تصميم iOS"""
    return {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "دليل الاستخدام",
                    "size": "xxl",
                    "weight": "bold",
                    "color": "#000000",
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": "كل ما تحتاج معرفته",
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
                            "type": "text",
                            "text": "🎮 الأوامر الأساسية",
                            "size": "lg",
                            "weight": "bold",
                            "color": "#000000",
                            "margin": "lg"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "• انضم - للتسجيل في البوت",
                                    "size": "sm",
                                    "color": "#3C3C43",
                                    "wrap": True
                                },
                                {
                                    "type": "text",
                                    "text": "• نقاطي - عرض إحصائياتك الشخصية",
                                    "size": "sm",
                                    "color": "#3C3C43",
                                    "wrap": True,
                                    "margin": "sm"
                                },
                                {
                                    "type": "text",
                                    "text": "• الصدارة - عرض أفضل اللاعبين",
                                    "size": "sm",
                                    "color": "#3C3C43",
                                    "wrap": True,
                                    "margin": "sm"
                                },
                                {
                                    "type": "text",
                                    "text": "• إيقاف - إنهاء اللعبة الحالية",
                                    "size": "sm",
                                    "color": "#3C3C43",
                                    "wrap": True,
                                    "margin": "sm"
                                },
                                {
                                    "type": "text",
                                    "text": "• انسحب - الخروج من البوت",
                                    "size": "sm",
                                    "color": "#3C3C43",
                                    "wrap": True,
                                    "margin": "sm"
                                }
                            ],
                            "margin": "md"
                        }
                    ],
                    "backgroundColor": "#F2F2F7",
                    "cornerRadius": "12px",
                    "paddingAll": "16px",
                    "margin": "lg"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "🎯 أثناء اللعب",
                            "size": "lg",
                            "weight": "bold",
                            "color": "#000000",
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "• لمح - الحصول على تلميح مساعد",
                                    "size": "sm",
                                    "color": "#3C3C43",
                                    "wrap": True
                                },
                                {
                                    "type": "text",
                                    "text": "• جاوب - عرض الإجابة الصحيحة",
                                    "size": "sm",
                                    "color": "#3C3C43",
                                    "wrap": True,
                                    "margin": "sm"
                                }
                            ],
                            "margin": "md"
                        }
                    ],
                    "backgroundColor": "#F2F2F7",
                    "cornerRadius": "12px",
                    "paddingAll": "16px",
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "🎲 الألعاب المتاحة",
                            "size": "lg",
                            "weight": "bold",
                            "color": "#000000",
                            "margin": "md"
                        },
                        {
                            "type": "text",
                            "text": "أغنية • لعبة • سلسلة • أسرع\nضد • تكوين • اختلاف • توافق",
                            "size": "sm",
                            "color": "#3C3C43",
                            "wrap": True,
                            "margin": "md",
                            "align": "center"
                        }
                    ],
                    "backgroundColor": "#F2F2F7",
                    "cornerRadius": "12px",
                    "paddingAll": "16px",
                    "margin": "md"
                }
            ],
            "backgroundColor": "#FFFFFF",
            "paddingAll": "20px"
        }
    }

def get_stats_card(user_id, display_name):
    """بطاقة الإحصائيات - تصميم iOS"""
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
                        "text": "إحصائياتك",
                        "size": "xxl",
                        "weight": "bold",
                        "color": "#000000",
                        "align": "center"
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
                                "type": "text",
                                "text": "📊",
                                "size": "5xl",
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "لم تبدأ اللعب بعد",
                                "size": "md",
                                "color": "#8E8E93",
                                "align": "center",
                                "margin": "md",
                                "wrap": True
                            },
                            {
                                "type": "text",
                                "text": "اكتب \"انضم\" للبدء",
                                "size": "sm",
                                "color": "#8E8E93",
                                "align": "center",
                                "margin": "sm"
                            }
                        ],
                        "margin": "xl",
                        "spacing": "sm"
                    }
                ],
                "backgroundColor": "#FFFFFF",
                "paddingAll": "24px"
            }
        }
    
    win_rate = (stats['wins'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0
    
    return {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "إحصائياتك",
                    "size": "xxl",
                    "weight": "bold",
                    "color": "#000000",
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": display_name,
                    "size": "md",
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
                                    "text": "🏆 النقاط الكلية",
                                    "size": "sm",
                                    "color": "#8E8E93",
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": str(stats['total_points']),
                                    "size": "xl",
                                    "weight": "bold",
                                    "color": "#000000",
                                    "align": "end"
                                }
                            ],
                            "backgroundColor": "#F2F2F7",
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
                                            "size": "xl",
                                            "weight": "bold",
                                            "color": "#000000",
                                            "align": "center"
                                        },
                                        {
                                            "type": "text",
                                            "text": "ألعاب",
                                            "size": "xs",
                                            "color": "#8E8E93",
                                            "align": "center",
                                            "margin": "sm"
                                        }
                                    ],
                                    "backgroundColor": "#F2F2F7",
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
                                            "size": "xl",
                                            "weight": "bold",
                                            "color": "#000000",
                                            "align": "center"
                                        },
                                        {
                                            "type": "text",
                                            "text": "فوز",
                                            "size": "xs",
                                            "color": "#8E8E93",
                                            "align": "center",
                                            "margin": "sm"
                                        }
                                    ],
                                    "backgroundColor": "#F2F2F7",
                                    "cornerRadius": "12px",
                                    "paddingAll": "16px",
                                    "flex": 1,
                                    "margin": "md"
                                }
                            ],
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"{win_rate:.1f}%",
                                    "size": "xl",
                                    "weight": "bold",
                                    "color": "#000000",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": "معدل الفوز",
                                    "size": "xs",
                                    "color": "#8E8E93",
                                    "align": "center",
                                    "margin": "sm"
                                }
                            ],
                            "backgroundColor": "#F2F2F7",
                            "cornerRadius": "12px",
                            "paddingAll": "16px",
                            "margin": "md"
                        }
                    ],
                    "margin": "xl"
                }
            ],
            "backgroundColor": "#FFFFFF",
            "paddingAll": "20px"
        }
    }

def get_leaderboard_card():
    """لوحة الصدارة - تصميم iOS"""
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
                        "text": "لوحة الصدارة",
                        "size": "xxl",
                        "weight": "bold",
                        "color": "#000000",
                        "align": "center"
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": "#E5E5EA"
                    },
                    {
                        "type": "text",
                        "text": "🏆",
                        "size": "5xl",
                        "align": "center",
                        "margin": "xl"
                    },
                    {
                        "type": "text",
                        "text": "لا توجد بيانات بعد",
                        "size": "md",
                        "color": "#8E8E93",
                        "align": "center",
                        "margin": "md"
                    }
                ],
                "backgroundColor": "#FFFFFF",
                "paddingAll": "24px"
            }
        }
    
    player_items = []
    medals = ["🥇", "🥈", "🥉"]
    
    for i, leader in enumerate(leaders, 1):
        # تحديد الألوان حسب الترتيب
        if i == 1:
            bg_color = "#000000"
            text_color = "#FFFFFF"
            medal = medals[0]
        elif i == 2:
            bg_color = "#3C3C43"
            text_color = "#FFFFFF"
            medal = medals[1]
        elif i == 3:
            bg_color = "#636366"
            text_color = "#FFFFFF"
            medal = medals[2]
        else:
            bg_color = "#F2F2F7"
            text_color = "#000000"
            medal = f"{i}"
        
        player_items.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": medal,
                    "size": "lg",
                    "color": text_color,
                    "flex": 0,
                    "weight": "bold"
                },
                {
                    "type": "text",
                    "text": leader['display_name'],
                    "size": "md",
                    "color": text_color,
                    "flex": 3,
                    "margin": "md",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": str(leader['total_points']),
                    "size": "md",
                    "color": text_color,
                    "flex": 1,
                    "align": "end",
                    "weight": "bold"
                }
            ],
            "backgroundColor": bg_color,
            "cornerRadius": "12px",
            "paddingAll": "14px",
            "margin": "sm" if i > 1 else "lg"
        })
    
    return {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "لوحة الصدارة",
                    "size": "xxl",
                    "weight": "bold",
                    "color": "#000000",
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": "أفضل 10 لاعبين",
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
                    "contents": player_items,
                    "margin": "md"
                }
            ],
            "backgroundColor": "#FFFFFF",
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
        if isinstance(response, TextSendMessage):
            response.quick_reply = get_quick_reply()
        
        line_bot_api.reply_message(event.reply_token, response)
        logger.info(f"✅ بدأت لعبة {game_type} للمستخدم {user_id}")
        return True
    except Exception as e:
        logger.error(f"❌ خطأ في بدء اللعبة {game_type}: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="❌ حدث خطأ في بدء اللعبة", quick_reply=get_quick_reply())
        )
        return False

# ==================== Flask Routes ====================

@app.route('/', methods=['GET'])
def home():
    """الصفحة الرئيسية - تصميم iOS"""
    total_users = len(registered_players)
    active_games_count = len(active_games)
    
    return f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LINE Bot - منصة الألعاب</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'SF Pro Display', sans-serif;
                background: #000000;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            
            .container {{
                background: #FFFFFF;
                border-radius: 24px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                padding: 48px;
                max-width: 600px;
                width: 100%;
                animation: fadeIn 0.6s ease-out;
            }}
            
            @keyframes fadeIn {{
                from {{
                    opacity: 0;
                    transform: translateY(20px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
            }}
            
            .icon {{
                font-size: 64px;
                margin-bottom: 16px;
            }}
            
            h1 {{
                color: #000000;
                font-size: 32px;
                font-weight: 700;
                margin-bottom: 8px;
                letter-spacing: -0.5px;
            }}
            
            .subtitle {{
                color: #8E8E93;
                font-size: 16px;
                font-weight: 400;
            }}
            
            .status-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 16px;
                margin: 32px 0;
            }}
            
            .status-card {{
                background: #F2F2F7;
                border-radius: 16px;
                padding: 24px;
                text-align: center;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }}
            
            .status-card:hover {{
                transform: translateY(-4px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
            }}
            
            .status-value {{
                color: #000000;
                font-size: 36px;
                font-weight: 700;
                margin-bottom: 8px;
                display: block;
            }}
            
            .status-label {{
                color: #8E8E93;
                font-size: 14px;
                font-weight: 500;
            }}
            
            .info-section {{
                background: #F2F2F7;
                border-radius: 16px;
                padding: 24px;
                margin-top: 24px;
            }}
            
            .info-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 16px 0;
                border-bottom: 1px solid #E5E5EA;
            }}
            
            .info-row:last-child {{
                border-bottom: none;
            }}
            
            .info-label {{
                color: #8E8E93;
                font-size: 15px;
                font-weight: 500;
            }}
            
            .info-value {{
                color: #000000;
                font-size: 15px;
                font-weight: 600;
            }}
            
            .status-badge {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: #34C759;
                color: #FFFFFF;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 600;
            }}
            
            .pulse {{
                width: 8px;
                height: 8px;
                background: #FFFFFF;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{
                    opacity: 1;
                }}
                50% {{
                    opacity: 0.5;
                }}
            }}
            
            .footer {{
                text-align: center;
                margin-top: 32px;
                padding-top: 24px;
                border-top: 1px solid #E5E5EA;
            }}
            
            .footer-text {{
                color: #8E8E93;
                font-size: 13px;
                line-height: 1.6;
            }}
            
            .games-list {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 8px;
                margin-top: 16px;
            }}
            
            .game-badge {{
                background: #E5E5EA;
                color: #3C3C43;
                padding: 8px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                text-align: center;
            }}
            
            @media (max-width: 600px) {{
                .container {{
                    padding: 32px 24px;
                }}
                
                h1 {{
                    font-size: 28px;
                }}
                
                .status-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .games-list {{
                    grid-template-columns: repeat(2, 1fr);
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="icon">🎮</div>
                <h1>منصة الألعاب</h1>
                <p class="subtitle">LINE Bot Gaming Platform</p>
            </div>
            
            <div class="status-grid">
                <div class="status-card">
                    <span class="status-value">{total_users}</span>
                    <span class="status-label">لاعب مسجل</span>
                </div>
                <div class="status-card">
                    <span class="status-value">{active_games_count}</span>
                    <span class="status-label">لعبة نشطة</span>
                </div>
            </div>
            
            <div class="info-section">
                <div class="info-row">
                    <span class="info-label">حالة الخادم</span>
                    <span class="status-badge">
                        <span class="pulse"></span>
                        يعمل
                    </span>
                </div>
                <div class="info-row">
                    <span class="info-label">عدد الألعاب</span>
                    <span class="info-value">8 ألعاب</span>
                </div>
                <div class="info-row">
                    <span class="info-label">إصدار API</span>
                    <span class="info-value">LINE Bot v2</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Framework</span>
                    <span class="info-value">Flask + Python</span>
                </div>
            </div>
            
            <div class="info-section">
                <div style="color: #8E8E93; font-size: 13px; font-weight: 600; margin-bottom: 12px;">
                    الألعاب المتاحة
                </div>
                <div class="games-list">
                    <div class="game-badge">🎵 أغنية</div>
                    <div class="game-badge">🎯 لعبة</div>
                    <div class="game-badge">🔗 سلسلة</div>
                    <div class="game-badge">⚡ أسرع</div>
                    <div class="game-badge">🔄 ضد</div>
                    <div class="game-badge">🔤 تكوين</div>
                    <div class="game-badge">🔍 اختلاف</div>
                    <div class="game-badge">💕 توافق</div>
                </div>
            </div>
            
            <div class="footer">
                <p class="footer-text">
                    Powered by LINE Bot API<br>
                    © 2024 Gaming Platform
                </p>
            </div>
        </div>
    </body>
    </html>
    """, 200
