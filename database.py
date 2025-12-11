import sqlite3
import logging
from threading import Lock
from datetime import datetime, timedelta
from constants import INACTIVITY_DAYS
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class Database:
    """إدارة قاعدة البيانات SQLite"""
    
    DB_NAME = 'game_scores.db'
    _lock = Lock()
    
    @staticmethod
    @contextmanager
    def get_connection():
        """Context manager للاتصال بقاعدة البيانات"""
        conn = None
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            conn.row_factory = sqlite3.Row
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def init():
        """تهيئة قاعدة البيانات وإنشاء الجداول"""
        try:
            with Database.get_connection() as conn:
                cursor = conn.cursor()
                
                # جدول المستخدمين
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        display_name TEXT NOT NULL,
                        total_points INTEGER DEFAULT 0,
                        games_played INTEGER DEFAULT 0,
                        wins INTEGER DEFAULT 0,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # جدول سجل الألعاب
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS game_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        game_type TEXT NOT NULL,
                        points INTEGER DEFAULT 0,
                        won BOOLEAN DEFAULT 0,
                        played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                ''')
                
                # إنشاء فهرس للأداء
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_user_last_activity
                    ON users(last_activity)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_game_history_user
                    ON game_history(user_id, played_at)
                ''')
                
                logger.info("Database initialized successfully")
        
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    @staticmethod
    def register_or_update_user(user_id, display_name):
        """تسجيل مستخدم جديد أو تحديث الاسم"""
        with Database._lock:
            try:
                with Database.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO users (user_id, display_name, last_activity)
                        VALUES (?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(user_id) DO UPDATE SET
                            display_name = excluded.display_name,
                            last_activity = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                    ''', (user_id, display_name))
                    
                    logger.info(f"User registered/updated: {user_id}")
                    return True
            
            except Exception as e:
                logger.error(f"Error registering user {user_id}: {e}")
                return False
    
    @staticmethod
    def update_last_activity(user_id):
        """تحديث آخر نشاط للمستخدم"""
        try:
            with Database.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE users
                    SET last_activity = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (user_id,))
                
                return cursor.rowcount > 0
        
        except Exception as e:
            logger.error(f"Error updating activity for {user_id}: {e}")
            return False
    
    @staticmethod
    def cleanup_inactive_users():
        """حذف المستخدمين غير النشطين"""
        with Database._lock:
            try:
                with Database.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cutoff_date = datetime.now() - timedelta(days=INACTIVITY_DAYS)
                    
                    # حذف سجل الألعاب أولاً
                    cursor.execute('''
                        DELETE FROM game_history
                        WHERE user_id IN (
                            SELECT user_id FROM users
                            WHERE last_activity < ?
                        )
                    ''', (cutoff_date.strftime('%Y-%m-%d %H:%M:%S'),))
                    
                    # حذف المستخدمين
                    cursor.execute('''
                        DELETE FROM users
                        WHERE last_activity < ?
                    ''', (cutoff_date.strftime('%Y-%m-%d %H:%M:%S'),))
                    
                    deleted_count = cursor.rowcount
                    
                    if deleted_count > 0:
                        logger.info(f"Cleaned up {deleted_count} inactive users")
                    
                    return deleted_count
            
            except Exception as e:
                logger.error(f"Error cleaning up users: {e}")
                return 0
    
    @staticmethod
    def is_user_registered(user_id):
        """التحقق من تسجيل المستخدم"""
        try:
            with Database.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT user_id FROM users WHERE user_id = ?
                ''', (user_id,))
                
                return cursor.fetchone() is not None
        
        except Exception as e:
            logger.error(f"Error checking user {user_id}: {e}")
            return False
    
    @staticmethod
    def update_user_points(user_id, points, won, game_type):
        """تحديث نقاط المستخدم"""
        with Database._lock:
            try:
                with Database.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # تحديث إحصائيات المستخدم
                    cursor.execute('''
                        UPDATE users
                        SET total_points = total_points + ?,
                            games_played = games_played + 1,
                            wins = wins + ?,
                            last_activity = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    ''', (points, 1 if won else 0, user_id))
                    
                    # إضافة سجل اللعبة
                    cursor.execute('''
                        INSERT INTO game_history (user_id, game_type, points, won)
                        VALUES (?, ?, ?, ?)
                    ''', (user_id, game_type, points, won))
                    
                    logger.info(f"Updated points for {user_id}: +{points}")
                    return True
            
            except Exception as e:
                logger.error(f"Error updating points for {user_id}: {e}")
                return False
    
    @staticmethod
    def get_user_stats(user_id):
        """الحصول على إحصائيات المستخدم"""
        try:
            with Database.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT total_points, games_played, wins, display_name
                    FROM users
                    WHERE user_id = ?
                ''', (user_id,))
                
                row = cursor.fetchone()
                
                if row:
                    return {
                        'total_points': row[0],
                        'games_played': row[1],
                        'wins': row[2],
                        'display_name': row[3]
                    }
                
                return None
        
        except Exception as e:
            logger.error(f"Error getting stats for {user_id}: {e}")
            return None
    
    @staticmethod
    def get_leaderboard(limit=20):
        """الحصول على لوحة الصدارة"""
        try:
            with Database.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT display_name, total_points, games_played, wins
                    FROM users
                    WHERE games_played > 0
                    ORDER BY total_points DESC, wins DESC
                    LIMIT ?
                ''', (limit,))
                
                results = cursor.fetchall()
                
                return [
                    {
                        'display_name': row[0],
                        'total_points': row[1],
                        'games_played': row[2],
                        'wins': row[3]
                    }
                    for row in results
                ]
        
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    @staticmethod
    def get_user_game_history(user_id, limit=10):
        """الحصول على سجل ألعاب المستخدم"""
        try:
            with Database.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT game_type, points, won, played_at
                    FROM game_history
                    WHERE user_id = ?
                    ORDER BY played_at DESC
                    LIMIT ?
                ''', (user_id, limit))
                
                results = cursor.fetchall()
                
                return [
                    {
                        'game_type': row[0],
                        'points': row[1],
                        'won': bool(row[2]),
                        'played_at': row[3]
                    }
                    for row in results
                ]
        
        except Exception as e:
            logger.error(f"Error getting game history for {user_id}: {e}")
            return []
    
    @staticmethod
    def get_all_players():
        """الحصول على جميع اللاعبين"""
        try:
            with Database.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT display_name, total_points, games_played, last_activity
                    FROM users
                    ORDER BY total_points DESC
                ''')
                
                results = cursor.fetchall()
                cutoff_date = datetime.now() - timedelta(days=INACTIVITY_DAYS)
                
                players = []
                for row in results:
                    try:
                        last_activity = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S')
                        active = last_activity >= cutoff_date
                    except:
                        active = False
                    
                    players.append({
                        'display_name': row[0],
                        'total_points': row[1],
                        'games_played': row[2],
                        'active': active
                    })
                
                return players
        
        except Exception as e:
            logger.error(f"Error getting all players: {e}")
            return []
