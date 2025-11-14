import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DB_NAME = 'game_scores.db'

def get_db_connection():
    """إنشاء اتصال آمن بقاعدة البيانات"""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """إنشاء جداول قاعدة البيانات"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # جدول المستخدمين
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id TEXT PRIMARY KEY,
                      display_name TEXT NOT NULL,
                      total_points INTEGER DEFAULT 0,
                      games_played INTEGER DEFAULT 0,
                      wins INTEGER DEFAULT 0,
                      last_played TEXT,
                      registered_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
        
        # جدول تاريخ الألعاب
        c.execute('''CREATE TABLE IF NOT EXISTS game_history
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id TEXT NOT NULL,
                      game_type TEXT NOT NULL,
                      points INTEGER DEFAULT 0,
                      won INTEGER DEFAULT 0,
                      played_at TEXT DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (user_id) REFERENCES users(user_id))''')
        
        # الفهارس
        c.execute('''CREATE INDEX IF NOT EXISTS idx_user_points 
                     ON users(total_points DESC)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_game_history_user 
                     ON game_history(user_id, played_at DESC)''')
        
        conn.commit()
        conn.close()
        logger.info("✅ تم إنشاء قاعدة البيانات بنجاح")
        return True
    except Exception as e:
        logger.error(f"❌ خطأ في إنشاء قاعدة البيانات: {e}")
        return False

def update_user_points(user_id, display_name, points, won=False, game_type=""):
    """تحديث نقاط المستخدم"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # التحقق من وجود المستخدم
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = c.fetchone()
        
        if user:
            # تحديث المستخدم الموجود
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
                      (user_id, display_name, points, 1, 
                       1 if won else 0, datetime.now().isoformat()))
        
        # إضافة سجل في تاريخ الألعاب
        if game_type:
            c.execute('''INSERT INTO game_history (user_id, game_type, points, won)
                         VALUES (?, ?, ?, ?)''',
                      (user_id, game_type, points, 1 if won else 0))
        
        conn.commit()
        conn.close()
        logger.info(f"✅ تم تحديث نقاط {display_name}: +{points}")
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
        logger.error(f"❌ خطأ في الحصول على الإحصائيات: {e}")
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
        logger.error(f"❌ خطأ في الحصول على الصدارة: {e}")
        return []

def get_user_game_history(user_id, limit=10):
    """الحصول على تاريخ ألعاب المستخدم"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''SELECT game_type, points, won, played_at
                     FROM game_history 
                     WHERE user_id = ?
                     ORDER BY played_at DESC
                     LIMIT ?''', (user_id, limit))
        history = c.fetchall()
        conn.close()
        return history
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على التاريخ: {e}")
        return []

def cleanup_old_data(days=90):
    """تنظيف البيانات القديمة"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # حذف سجلات الألعاب القديمة
        cutoff_date = datetime.now() - timedelta(days=days)
        c.execute('''DELETE FROM game_history 
                     WHERE played_at < ?''', (cutoff_date.isoformat(),))
        
        deleted = c.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"✅ تم حذف {deleted} سجل قديم")
        return deleted
    except Exception as e:
        logger.error(f"❌ خطأ في التنظيف: {e}")
        return 0
