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
    def get_connection():
        """الحصول على اتصال جديد"""
        return sqlite3.connect(Database.DB_NAME, timeout=10.0, check_same_thread=False)
    
    @staticmethod
    def init():
        """تهيئة قاعدة البيانات"""
        conn = None
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            
            # جدول المستخدمين
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                total_points INTEGER DEFAULT 0,
                games_played INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # جدول تاريخ الألعاب
            cursor.execute('''CREATE TABLE IF NOT EXISTS game_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                game_type TEXT NOT NULL,
                points INTEGER DEFAULT 0,
                won BOOLEAN DEFAULT 0,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )''')
            
            # الفهارس
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_points ON users(total_points DESC, is_active)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_activity ON users(last_activity, is_active)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_game_history_user ON game_history(user_id, played_at)')
            
            conn.commit()
            logger.info("تم تهيئة قاعدة البيانات بنجاح")
        except Exception as e:
            logger.error(f"خطأ تهيئة قاعدة البيانات: {e}", exc_info=True)
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def register_or_update_user(user_id, display_name):
        """تسجيل أو تحديث مستخدم"""
        with Database._lock:
            conn = None
            try:
                conn = Database.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
                exists = cursor.fetchone()
                
                if exists:
                    cursor.execute('''UPDATE users 
                        SET display_name = ?, is_active = 1, 
                            last_activity = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    ''', (display_name, user_id))
                else:
                    cursor.execute('''INSERT INTO users 
                        (user_id, display_name, is_active, last_activity)
                        VALUES (?, ?, 1, CURRENT_TIMESTAMP)
                    ''', (user_id, display_name))
                
                conn.commit()
                logger.info(f"تسجيل/تحديث مستخدم: {display_name}")
                return True
            except Exception as e:
                logger.error(f"خطأ في تسجيل المستخدم: {e}", exc_info=True)
                return False
            finally:
                if conn:
                    conn.close()
    
    @staticmethod
    def update_last_activity(user_id):
        """تحديث آخر نشاط"""
        with Database._lock:
            conn = None
            try:
                conn = Database.get_connection()
                cursor = conn.cursor()
                cursor.execute('''UPDATE users 
                    SET last_activity = CURRENT_TIMESTAMP 
                    WHERE user_id = ? AND is_active = 1
                ''', (user_id,))
                conn.commit()
                return True
            except Exception as e:
                logger.error(f"خطأ تحديث النشاط: {e}")
                return False
            finally:
                if conn:
                    conn.close()
    
    @staticmethod
    def cleanup_inactive_users():
        """تنظيف المستخدمين غير النشطين"""
        with Database._lock:
            conn = None
            try:
                conn = Database.get_connection()
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=INACTIVITY_DAYS)
                cutoff_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
                
                cursor.execute('''UPDATE users 
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE last_activity < ? AND is_active = 1
                ''', (cutoff_str,))
                
                deactivated_count = cursor.rowcount
                conn.commit()
                
                if deactivated_count > 0:
                    logger.info(f"تم إلغاء تفعيل {deactivated_count} مستخدم")
                
                return deactivated_count
            except Exception as e:
                logger.error(f"خطأ تنظيف المستخدمين: {e}")
                return 0
            finally:
                if conn:
                    conn.close()
    
    @staticmethod
    def is_user_registered(user_id):
        """التحقق من تسجيل المستخدم"""
        conn = None
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT is_active FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result is not None and result[0] == 1
        except Exception as e:
            logger.error(f"خطأ التحقق من التسجيل: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def delete_user(user_id):
        """إلغاء تفعيل مستخدم"""
        with Database._lock:
            conn = None
            try:
                conn = Database.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''UPDATE users 
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (user_id,))
                
                deactivated = cursor.rowcount > 0
                conn.commit()
                
                if deactivated:
                    logger.info(f"تم إلغاء تفعيل المستخدم {user_id}")
                return deactivated
            except Exception as e:
                logger.error(f"خطأ إلغاء التفعيل: {e}")
                return False
            finally:
                if conn:
                    conn.close()
    
    @staticmethod
    def reactivate_user(user_id):
        """إعادة تفعيل مستخدم"""
        with Database._lock:
            conn = None
            try:
                conn = Database.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''UPDATE users 
                    SET is_active = 1, last_activity = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (user_id,))
                
                reactivated = cursor.rowcount > 0
                conn.commit()
                
                if reactivated:
                    logger.info(f"تم إعادة تفعيل المستخدم {user_id}")
                return reactivated
            except Exception as e:
                logger.error(f"خطأ إعادة التفعيل: {e}")
                return False
            finally:
                if conn:
                    conn.close()
    
    @staticmethod
    def get_existing_user_name(user_id):
        """جلب اسم مستخدم موجود"""
        conn = None
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT display_name FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"خطأ في جلب اسم المستخدم: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def update_user_points(user_id, points, won, game_type):
        """تحديث نقاط المستخدم"""
        with Database._lock:
            conn = None
            try:
                conn = Database.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('SELECT is_active FROM users WHERE user_id = ?', (user_id,))
                result = cursor.fetchone()
                if not result or result[0] != 1:
                    logger.warning(f"محاولة تحديث نقاط لمستخدم غير مفعل: {user_id}")
                    return False
                
                cursor.execute('''UPDATE users
                    SET total_points = total_points + ?,
                        games_played = games_played + 1,
                        wins = wins + ?,
                        last_activity = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (points, 1 if won else 0, user_id))
                
                cursor.execute('''INSERT INTO game_history 
                    (user_id, game_type, points, won)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, game_type, points, won))
                
                conn.commit()
                logger.info(f"تحديث نقاط المستخدم {user_id}: +{points} نقطة")
                return True
            except Exception as e:
                logger.error(f"خطأ تحديث نقاط: {e}")
                return False
            finally:
                if conn:
                    conn.close()
    
    @staticmethod
    def get_user_stats(user_id):
        """جلب إحصائيات المستخدم"""
        conn = None
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute('''SELECT total_points, games_played, wins, display_name
                FROM users WHERE user_id = ? AND is_active = 1
            ''', (user_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    'total_points': result[0] or 0,
                    'games_played': result[1] or 0,
                    'wins': result[2] or 0,
                    'display_name': result[3] or 'مستخدم'
                }
            
            return {
                'total_points': 0,
                'games_played': 0,
                'wins': 0,
                'display_name': 'مستخدم'
            }
        except Exception as e:
            logger.error(f"خطأ جلب الإحصائيات: {e}")
            return {'total_points': 0, 'games_played': 0, 'wins': 0, 'display_name': 'مستخدم'}
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_leaderboard(limit=20):
        """جلب لوحة الصدارة"""
        conn = None
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute('''SELECT display_name, total_points, games_played, wins
                FROM users
                WHERE games_played > 0 AND is_active = 1
                ORDER BY total_points DESC, wins DESC
                LIMIT ?
            ''', (limit,))
            results = cursor.fetchall()
            return [
                {
                    'display_name': r[0], 
                    'total_points': r[1], 
                    'games_played': r[2], 
                    'wins': r[3]
                } 
                for r in results
            ]
        except Exception as e:
            logger.error(f"خطأ جلب الصدارة: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_all_players():
        """جلب جميع اللاعبين"""
        conn = None
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute('''SELECT display_name, total_points, games_played, is_active, last_activity
                FROM users
                ORDER BY is_active DESC, total_points DESC
            ''')
            results = cursor.fetchall()
            
            cutoff_date = datetime.now() - timedelta(days=INACTIVITY_DAYS)
            players = []
            for r in results:
                try:
                    last_activity = datetime.strptime(r[4], '%Y-%m-%d %H:%M:%S')
                    active = r[3] == 1 and last_activity >= cutoff_date
                except:
                    active = False
                    
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
        finally:
            if conn:
                conn.close()
