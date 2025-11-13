"""
Database Functions
وظائف قاعدة البيانات
"""

import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
DB_NAME = 'game_scores.db'

def get_db_connection():
    """
    إنشاء اتصال آمن بقاعدة البيانات
    
    Returns:
        sqlite3.Connection: اتصال قاعدة البيانات
    """
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
        raise

def init_db():
    """إنشاء جداول قاعدة البيانات إذا لم تكن موجودة"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # جدول المستخدمين
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id TEXT PRIMARY KEY, 
                      display_name TEXT,
                      total_points INTEGER DEFAULT 0,
                      games_played INTEGER DEFAULT 0,
                      wins INTEGER DEFAULT 0,
                      last_played TEXT,
                      registered_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
        
        # جدول تاريخ الألعاب
        c.execute('''CREATE TABLE IF NOT EXISTS game_history
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id TEXT,
                      game_type TEXT,
                      points INTEGER,
                      won INTEGER,
                      played_at TEXT DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (user_id) REFERENCES users(user_id))''')
        
        # فهارس لتحسين الأداء
        c.execute('''CREATE INDEX IF NOT EXISTS idx_user_points 
                     ON users(total_points DESC)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_game_history_user 
                     ON game_history(user_id, played_at DESC)''')
        
        conn.commit()
        conn.close()
        logger.info("✅ تم إنشاء/التحقق من قاعدة البيانات بنجاح")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إنشاء قاعدة البيانات: {e}")
        raise

def update_user_points(user_id, display_name, points, won=False, game_type=""):
    """
    تحديث نقاط المستخدم في قاعدة البيانات
    
    Args:
        user_id: معرف المستخدم
        display_name: اسم المستخدم
        points: النقاط المكتسبة
        won: هل فاز المستخدم
        game_type: نوع اللعبة
        
    Returns:
        bool: True إذا نجحت العملية
    """
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # فحص إذا كان المستخدم موجود
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = c.fetchone()
        
        if user:
            # تحديث بيانات مستخدم موجود
            new_points = user['total_points'] + points
            new_games = user['games_played'] + 1
            new_wins = user['wins'] + (1 if won else 0)
            
            c.execute('''UPDATE users 
                         SET total_points = ?, 
                             games_played = ?, 
                             wins = ?, 
                             last_played = ?, 
                             display_name = ?
                         WHERE user_id = ?''',
                      (new_points, new_games, new_wins, 
                       datetime.now().isoformat(), display_name, user_id))
        else:
            # إضافة مستخدم جديد
            c.execute('''INSERT INTO users 
                         (user_id, display_name, total_points, games_played, wins, last_played) 
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (user_id, display_name, points, 1, 1 if won else 0, 
                       datetime.now().isoformat()))
        
        # تسجيل في تاريخ الألعاب
        if game_type:
            c.execute('''INSERT INTO game_history 
                         (user_id, game_type, points, won) 
                         VALUES (?, ?, ?, ?)''',
                      (user_id, game_type, points, 1 if won else 0))
        
        conn.commit()
        conn.close()
        logger.info(f"✅ تم تحديث نقاط {display_name}: +{points} نقطة")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في تحديث النقاط: {e}")
        return False

def get_user_stats(user_id):
    """
    الحصول على إحصائيات المستخدم
    
    Args:
        user_id: معرف المستخدم
        
    Returns:
        sqlite3.Row or None: بيانات المستخدم
    """
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = c.fetchone()
        conn.close()
        return user
        
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على الإحصائيات: {e}")
        return None

def get_leaderboard(limit=10):
    """
    الحصول على لوحة الصدارة
    
    Args:
        limit: عدد اللاعبين المطلوب
        
    Returns:
        list: قائمة اللاعبين الأفضل
    """
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
        logger.error(f"❌ خطأ في الحصول على الصدارة: {e}")
        return []

def get_user_rank(user_id):
    """
    الحصول على ترتيب المستخدم في الصدارة
    
    Args:
        user_id: معرف المستخدم
        
    Returns:
        int or None: ترتيب المستخدم
    """
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''SELECT COUNT(*) + 1 as rank
                     FROM users 
                     WHERE total_points > (
                         SELECT total_points 
                         FROM users 
                         WHERE user_id = ?
                     )''', (user_id,))
        result = c.fetchone()
        conn.close()
        return result['rank'] if result else None
        
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على الترتيب: {e}")
        return None
