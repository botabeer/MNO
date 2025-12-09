import sqlite3
import logging
from threading import Lock
from datetime import datetime, timedelta
from constants import INACTIVITY_DAYS

logger = logging.getLogger(__name__)

class Database:
    DB_NAME = 'game_scores.db'
    _lock = Lock()
    
    @staticmethod
    def init():
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                total_points INTEGER DEFAULT 0,
                games_played INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS game_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                game_type TEXT NOT NULL,
                points INTEGER DEFAULT 0,
                won BOOLEAN DEFAULT 0,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )''')
            
            conn.commit()
            conn.close()
            logger.info("تم تهيئة قاعدة البيانات")
        except Exception as e:
            logger.error(f"خطأ تهيئة DB: {e}")
    
    @staticmethod
    def register_or_update_user(user_id, display_name):
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO users (user_id, display_name, last_activity)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_id) DO UPDATE SET
                    display_name = excluded.display_name,
                    last_activity = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                ''', (user_id, display_name))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                logger.error(f"خطأ تسجيل: {e}")
                return False
    
    @staticmethod
    def update_last_activity(user_id):
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                cursor.execute('''UPDATE users SET last_activity = CURRENT_TIMESTAMP 
                    WHERE user_id = ?''', (user_id,))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                logger.error(f"خطأ تحديث النشاط: {e}")
                return False
    
    @staticmethod
    def cleanup_inactive_users():
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                cutoff_date = datetime.now() - timedelta(days=INACTIVITY_DAYS)
                
                cursor.execute('''DELETE FROM users 
                    WHERE last_activity < ? AND games_played = 0''', 
                    (cutoff_date.strftime('%Y-%m-%d %H:%M:%S'),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                conn.close()
                
                if deleted_count > 0:
                    logger.info(f"تم حذف {deleted_count} مستخدم غير نشط")
                
                return deleted_count
            except Exception as e:
                logger.error(f"خطأ تنظيف المستخدمين: {e}")
                return 0
    
    @staticmethod
    def is_user_registered(user_id):
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            logger.error(f"خطأ تحقق: {e}")
            return False
    
    @staticmethod
    def update_user_points(user_id, points, won, game_type):
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                
                cursor.execute('''UPDATE users
                    SET total_points = total_points + ?,
                        games_played = games_played + 1,
                        wins = wins + ?,
                        last_activity = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (points, 1 if won else 0, user_id))
                
                cursor.execute('''INSERT INTO game_history (user_id, game_type, points, won)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, game_type, points, won))
                
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                logger.error(f"خطأ تحديث نقاط: {e}")
                return False
    
    @staticmethod
    def get_user_stats(user_id):
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''SELECT total_points, games_played, wins, display_name
                FROM users WHERE user_id = ?
            ''', (user_id,))
            result = cursor.fetchone()
            conn.close()
            if result:
                return {
                    'total_points': result[0],
                    'games_played': result[1],
                    'wins': result[2],
                    'display_name': result[3]
                }
            return None
        except Exception as e:
            logger.error(f"خطأ احصائيات: {e}")
            return None
    
    @staticmethod
    def get_leaderboard(limit=20):
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''SELECT display_name, total_points, games_played, wins
                FROM users
                WHERE games_played > 0
                ORDER BY total_points DESC
                LIMIT ?
            ''', (limit,))
            results = cursor.fetchall()
            conn.close()
            return [{'display_name': r[0], 'total_points': r[1], 'games_played': r[2], 'wins': r[3]} for r in results]
        except Exception as e:
            logger.error(f"خطأ صدارة: {e}")
            return []
    
    @staticmethod
    def get_all_players():
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''SELECT display_name, total_points, games_played, last_activity
                FROM users
                ORDER BY total_points DESC
            ''')
            results = cursor.fetchall()
            conn.close()
            
            cutoff_date = datetime.now() - timedelta(days=INACTIVITY_DAYS)
            players = []
            for r in results:
                last_activity = datetime.strptime(r[3], '%Y-%m-%d %H:%M:%S')
                active = last_activity >= cutoff_date
                players.append({
                    'display_name': r[0],
                    'total_points': r[1],
                    'games_played': r[2],
                    'active': active
                })
            return players
        except Exception as e:
            logger.error(f"خطأ جلب اللاعبين: {e}")
            return []
