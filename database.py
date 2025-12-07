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
        return sqlite3.connect(Database.DB_NAME, timeout=10.0, check_same_thread=False)
    
    @staticmethod
    def init():
        conn = None
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                total_points INTEGER DEFAULT 0,
                games_played INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                is_withdrawn INTEGER DEFAULT 0,
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
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_points ON users(total_points DESC, is_active)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_activity ON users(last_activity, is_active)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_game_history_user ON game_history(user_id, played_at)')
            conn.commit()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}", exc_info=True)
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def register_or_update_user(user_id, display_name):
        with Database._lock:
            conn = None
            try:
                conn = Database.get_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
                exists = cursor.fetchone()
                if exists:
                    cursor.execute('''UPDATE users 
                        SET display_name = ?, is_active = 1, is_withdrawn = 0,
                            last_activity = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    ''', (display_name, user_id))
                else:
                    cursor.execute('''INSERT INTO users 
                        (user_id, display_name, is_active, is_withdrawn, last_activity)
                        VALUES (?, ?, 1, 0, CURRENT_TIMESTAMP)
                    ''', (user_id, display_name))
                conn.commit()
                logger.info(f"User registered/updated: {display_name}")
                return True
            except Exception as e:
                logger.error(f"Error registering user: {e}", exc_info=True)
                return False
            finally:
                if conn:
                    conn.close()
    
    @staticmethod
    def update_last_activity(user_id):
        with Database._lock:
            conn = None
            try:
                conn = Database.get_connection()
                cursor = conn.cursor()
                cursor.execute('''UPDATE users 
                    SET last_activity = CURRENT_TIMESTAMP 
                    WHERE user_id = ? AND is_active = 1 AND is_withdrawn = 0
                ''', (user_id,))
                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Error updating activity: {e}")
                return False
            finally:
                if conn:
                    conn.close()
    
    @staticmethod
    def cleanup_inactive_users():
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
                    logger.info(f"Deactivated {deactivated_count} inactive users")
                return deactivated_count
            except Exception as e:
                logger.error(f"Error cleaning up users: {e}")
                return 0
            finally:
                if conn:
                    conn.close()
    
    @staticmethod
    def is_user_registered(user_id):
        conn = None
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT is_active, is_withdrawn FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result is not None and result[0] == 1 and result[1] == 0
        except Exception as e:
            logger.error(f"Error checking registration: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def is_user_withdrawn(user_id):
        conn = None
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT is_withdrawn FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result is not None and result[0] == 1
        except Exception as e:
            logger.error(f"Error checking withdrawal: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def withdraw_user(user_id):
        with Database._lock:
            conn = None
            try:
                conn = Database.get_connection()
                cursor = conn.cursor()
                cursor.execute('''UPDATE users 
                    SET is_withdrawn = 1, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (user_id,))
                withdrawn = cursor.rowcount > 0
                conn.commit()
                if withdrawn:
                    logger.info(f"User withdrew: {user_id}")
                return withdrawn
            except Exception as e:
                logger.error(f"Error withdrawing user: {e}")
                return False
            finally:
                if conn:
                    conn.close()
    
    @staticmethod
    def reactivate_user(user_id):
        with Database._lock:
            conn = None
            try:
                conn = Database.get_connection()
                cursor = conn.cursor()
                cursor.execute('''UPDATE users 
                    SET is_active = 1, is_withdrawn = 0, last_activity = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (user_id,))
                reactivated = cursor.rowcount > 0
                conn.commit()
                if reactivated:
                    logger.info(f"User reactivated: {user_id}")
                return reactivated
            except Exception as e:
                logger.error(f"Error reactivating user: {e}")
                return False
            finally:
                if conn:
                    conn.close()
    
    @staticmethod
    def get_existing_user_name(user_id):
        conn = None
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT display_name FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error fetching user name: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def update_user_points(user_id, points, won, game_type):
        with Database._lock:
            conn = None
            try:
                conn = Database.get_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT is_active, is_withdrawn FROM users WHERE user_id = ?', (user_id,))
                result = cursor.fetchone()
                if not result or result[0] != 1 or result[1] == 1:
                    logger.warning(f"Attempted to update points for inactive/withdrawn user: {user_id}")
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
                logger.info(f"Updated points for user {user_id}: +{points}")
                return True
            except Exception as e:
                logger.error(f"Error updating points: {e}")
                return False
            finally:
                if conn:
                    conn.close()
    
    @staticmethod
    def get_user_stats(user_id):
        conn = None
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute('''SELECT total_points, games_played, wins, display_name
                FROM users WHERE user_id = ? AND is_withdrawn = 0
            ''', (user_id,))
            result = cursor.fetchone()
            if result:
                return {
                    'total_points': result[0] or 0,
                    'games_played': result[1] or 0,
                    'wins': result[2] or 0,
                    'display_name': result[3] or 'User'
                }
            return {'total_points': 0, 'games_played': 0, 'wins': 0, 'display_name': 'User'}
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return {'total_points': 0, 'games_played': 0, 'wins': 0, 'display_name': 'User'}
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_leaderboard(limit=20):
        conn = None
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute('''SELECT display_name, total_points, games_played, wins
                FROM users WHERE is_withdrawn = 0
                ORDER BY total_points DESC, wins DESC LIMIT ?
            ''', (limit,))
            results = cursor.fetchall()
            return [{
                'display_name': r[0],
                'total_points': r[1],
                'games_played': r[2],
                'wins': r[3]
            } for r in results]
        except Exception as e:
            logger.error(f"Error fetching leaderboard: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_all_players():
        conn = None
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute('''SELECT display_name, total_points, games_played, is_active, is_withdrawn, last_activity
                FROM users ORDER BY total_points DESC
            ''')
            results = cursor.fetchall()
            cutoff_date = datetime.now() - timedelta(days=INACTIVITY_DAYS)
            players = []
            for r in results:
                try:
                    last_activity = datetime.strptime(r[5], '%Y-%m-%d %H:%M:%S')
                    active = r[3] == 1 and r[4] == 0 and last_activity >= cutoff_date
                except:
                    active = False
                players.append({
                    'display_name': r[0],
                    'total_points': r[1],
                    'games_played': r[2],
                    'active': active,
                    'withdrawn': r[4] == 1
                })
            return players
        except Exception as e:
            logger.error(f"Error fetching all players: {e}")
            return []
        finally:
            if conn:
                conn.close()
