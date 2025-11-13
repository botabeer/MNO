"""
ملف إدارة قاعدة البيانات
نظام بسيط وفعّال لحفظ البيانات
"""
import sqlite3
import os
import logging
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# مسار قاعدة البيانات
DB_PATH = os.getenv("DATABASE_URL", "bot_data.db").replace("sqlite:///", "")


@contextmanager
def get_db_connection():
    """
    Context manager للاتصال بقاعدة البيانات
    
    Yields:
        sqlite3.Connection: اتصال قاعدة البيانات
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ خطأ في قاعدة البيانات: {e}")
        raise
    finally:
        if conn:
            conn.close()


def init_db():
    """تهيئة قاعدة البيانات وإنشاء الجداول"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # جدول اللاعبين
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    user_id TEXT PRIMARY KEY,
                    username TEXT,
                    total_score INTEGER DEFAULT 0,
                    games_played INTEGER DEFAULT 0,
                    games_won INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول الألعاب
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    game_id TEXT PRIMARY KEY,
                    game_type TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    score INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES players(user_id)
                )
            """)
            
            # جدول الإحصائيات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    game_type TEXT NOT NULL,
                    score INTEGER DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES players(user_id)
                )
            """)
            
            # إنشاء الفهارس
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_players_score 
                ON players(total_score DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_games_user 
                ON games(user_id, created_at DESC)
            """)
            
            logger.info("✅ تم تهيئة قاعدة البيانات بنجاح")
            
    except Exception as e:
        logger.error(f"❌ خطأ في تهيئة قاعدة البيانات: {e}")


# ========== دوال اللاعبين ==========

def add_player(user_id, username):
    """
    إضافة لاعب جديد أو تحديث بياناته
    
    Args:
        user_id: معرف المستخدم
        username: اسم المستخدم
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO players (user_id, username, last_active)
                VALUES (?, ?, ?)
            """, (user_id, username, datetime.now()))
            logger.info(f"✅ تم إضافة/تحديث اللاعب: {username} ({user_id})")
    except Exception as e:
        logger.error(f"❌ خطأ في إضافة اللاعب: {e}")


def get_player(user_id):
    """
    الحصول على معلومات اللاعب
    
    Args:
        user_id: معرف المستخدم
        
    Returns:
        dict: معلومات اللاعب أو None
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على اللاعب: {e}")
        return None


def update_player_score(user_id, score_change):
    """
    تحديث نقاط اللاعب
    
    Args:
        user_id: معرف المستخدم
        score_change: التغيير في النقاط (موجب أو سالب)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE players 
                SET total_score = total_score + ?,
                    last_active = ?
                WHERE user_id = ?
            """, (score_change, datetime.now(), user_id))
            logger.info(f"✅ تم تحديث نقاط اللاعب {user_id}: {score_change:+d}")
    except Exception as e:
        logger.error(f"❌ خطأ في تحديث النقاط: {e}")


def get_leaderboard(limit=10):
    """
    الحصول على قائمة الصدارة
    
    Args:
        limit: عدد اللاعبين المطلوب عرضهم
        
    Returns:
        list: قائمة باللاعبين [(username, score), ...]
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username, total_score 
                FROM players 
                WHERE total_score > 0
                ORDER BY total_score DESC 
                LIMIT ?
            """, (limit,))
            return [(row['username'], row['total_score']) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على قائمة الصدارة: {e}")
        return []


def get_player_rank(user_id):
    """
    الحصول على ترتيب اللاعب
    
    Args:
        user_id: معرف المستخدم
        
    Returns:
        int: ترتيب اللاعب أو None
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) + 1 as rank
                FROM players
                WHERE total_score > (
                    SELECT total_score FROM players WHERE user_id = ?
                )
            """, (user_id,))
            row = cursor.fetchone()
            return row['rank'] if row else None
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على الترتيب: {e}")
        return None


# ========== دوال الألعاب ==========

def create_game(game_id, game_type, user_id):
    """
    إنشاء لعبة جديدة
    
    Args:
        game_id: معرف اللعبة
        game_type: نوع اللعبة
        user_id: معرف المستخدم
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO games (game_id, game_type, user_id, status)
                VALUES (?, ?, ?, 'active')
            """, (game_id, game_type, user_id))
            logger.info(f"✅ تم إنشاء لعبة جديدة: {game_type} ({game_id})")
    except Exception as e:
        logger.error(f"❌ خطأ في إنشاء اللعبة: {e}")


def complete_game(game_id, score):
    """
    إكمال لعبة وحفظ النتيجة
    
    Args:
        game_id: معرف اللعبة
        score: النقاط النهائية
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE games 
                SET status = 'completed',
                    score = ?,
                    completed_at = ?
                WHERE game_id = ?
            """, (score, datetime.now(), game_id))
            logger.info(f"✅ تم إكمال اللعبة {game_id} بنقاط: {score}")
    except Exception as e:
        logger.error(f"❌ خطأ في إكمال اللعبة: {e}")


def get_player_games(user_id, limit=10):
    """
    الحصول على ألعاب اللاعب
    
    Args:
        user_id: معرف المستخدم
        limit: عدد الألعاب
        
    Returns:
        list: قائمة بالألعاب
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM games 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على ألعاب اللاعب: {e}")
        return []


# ========== دوال الإحصائيات ==========

def add_game_statistic(user_id, game_type, score):
    """
    إضافة إحصائية لعبة
    
    Args:
        user_id: معرف المستخدم
        game_type: نوع اللعبة
        score: النقاط
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO statistics (user_id, game_type, score)
                VALUES (?, ?, ?)
            """, (user_id, game_type, score))
            logger.info(f"✅ تم إضافة إحصائية: {game_type} - {score} نقطة")
    except Exception as e:
        logger.error(f"❌ خطأ في إضافة الإحصائية: {e}")


def get_game_statistics(user_id, game_type=None):
    """
    الحصول على إحصائيات اللاعب
    
    Args:
        user_id: معرف المستخدم
        game_type: نوع اللعبة (اختياري)
        
    Returns:
        dict: الإحصائيات
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if game_type:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as games_count,
                        AVG(score) as avg_score,
                        MAX(score) as max_score,
                        MIN(score) as min_score
                    FROM statistics
                    WHERE user_id = ? AND game_type = ?
                """, (user_id, game_type))
            else:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as games_count,
                        AVG(score) as avg_score,
                        MAX(score) as max_score,
                        MIN(score) as min_score
                    FROM statistics
                    WHERE user_id = ?
                """, (user_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else {}
            
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على الإحصائيات: {e}")
        return {}


# ========== دوال التنظيف ==========

def cleanup_old_games(days=7):
    """
    حذف الألعاب القديمة
    
    Args:
        days: عدد الأيام
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM games
                WHERE status = 'completed' 
                AND completed_at < datetime('now', '-' || ? || ' days')
            """, (days,))
            deleted = cursor.rowcount
            logger.info(f"🧹 تم حذف {deleted} لعبة قديمة")
    except Exception as e:
        logger.error(f"❌ خطأ في حذف الألعاب القديمة: {e}")
