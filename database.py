import sqlite3
import logging
from threading import Lock
from datetime import datetime, timedelta
from constants import INACTIVITY_DAYS
from contextlib import contextmanager
from queue import Queue

logger = logging.getLogger(__name__)

class DatabaseConnectionPool:
    def __init__(self, db_name, pool_size=10):
        self.db_name = db_name
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self._initialize_pool()
    
    def _initialize_pool(self):
        for _ in range(self.pool_size):
            conn = sqlite3.connect(
                self.db_name,
                check_same_thread=False,
                timeout=10.0
            )
            conn.row_factory = sqlite3.Row
            self.pool.put(conn)
    
    @contextmanager
    def get_connection(self):
        conn = self.pool.get()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            self.pool.put(conn)

db_pool = DatabaseConnectionPool('game_scores.db', pool_size=10)

class Database:
    _lock = Lock()
    _leaderboard_cache = None
    _leaderboard_cache_time = 0
    CACHE_TTL = 300
    
    @staticmethod
    @contextmanager
    def get_connection():
        with db_pool.get_connection() as conn:
            yield conn
    
    @staticmethod
    def init():
        try:
            with Database.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        display_name TEXT NOT NULL,
                        total_points INTEGER DEFAULT 0,
                        games_played INTEGER DEFAULT 0,
                        wins INTEGER DEFAULT 0,
                        theme TEXT DEFAULT 'light',
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
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
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_users_points_games
                    ON users(total_points DESC, games_played DESC)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_game_history_composite
                    ON game_history(user_id, played_at DESC, game_type)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_users_active
                    ON users(last_activity DESC)
                    WHERE games_played > 0
                ''')
                
                cursor.execute('ANALYZE')
                
                logger.info("Database initialized successfully")
        
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    @staticmethod
    def get_user_theme(user_id):
        try:
            with Database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT theme FROM users WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()
                return row[0] if row else 'light'
        except Exception as e:
            logger.error(f"Error getting theme for {user_id}: {e}")
            return 'light'
    
    @staticmethod
    def set_user_theme(user_id, theme):
        try:
            with Database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET theme = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (theme, user_id))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error setting theme for {user_id}: {e}")
            return False
    
    @staticmethod
    def register_or_update_user(user_id, display_name):
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
        with Database._lock:
            try:
                with Database.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cutoff_date = datetime.now() - timedelta(days=INACTIVITY_DAYS)
                    
                    cursor.execute('''
                        DELETE FROM game_history
                        WHERE user_id IN (
                            SELECT user_id FROM users
                            WHERE last_activity < ?
                        )
                    ''', (cutoff_date.strftime('%Y-%m-%d %H:%M:%S'),))
                    
                    cursor.execute('''
                        DELETE FROM users
                        WHERE last_activity < ?
                    ''', (cutoff_date.strftime('%Y-%m-%d %H:%M:%S'),))
                    
                    deleted_count = cursor.rowcount
                    
                    if deleted_count > 0:
                        logger.info(f"Cleaned up {deleted_count} inactive users")
                        Database._leaderboard_cache = None
                    
                    return deleted_count
            
            except Exception as e:
                logger.error(f"Error cleaning up users: {e}")
                return 0
    
    @staticmethod
    def is_user_registered(user_id):
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
        with Database._lock:
            try:
                with Database.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        UPDATE users
                        SET total_points = total_points + ?,
                            games_played = games_played + 1,
                            wins = wins + ?,
                            last_activity = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    ''', (points, 1 if won else 0, user_id))
                    
                    cursor.execute('''
                        INSERT INTO game_history (user_id, game_type, points, won)
                        VALUES (?, ?, ?, ?)
                    ''', (user_id, game_type, points, won))
                    
                    Database._leaderboard_cache = None
                    
                    logger.info(f"Updated points for {user_id}: +{points}")
                    return True
            
            except Exception as e:
                logger.error(f"Error updating points for {user_id}: {e}")
                return False
    
    @staticmethod
    def get_user_stats(user_id):
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
    def get_leaderboard(limit=20, force_refresh=False):
        from time import time
        now = time()
        
        if (not force_refresh and 
            Database._leaderboard_cache and 
            now - Database._leaderboard_cache_time < Database.CACHE_TTL):
            return Database._leaderboard_cache[:limit]
        
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
                
                leaders = [
                    {
                        'display_name': row[0],
                        'total_points': row[1],
                        'games_played': row[2],
                        'wins': row[3]
                    }
                    for row in results
                ]
                
                Database._leaderboard_cache = leaders
                Database._leaderboard_cache_time = now
                
                return leaders
        
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    @staticmethod
    def get_user_game_history(user_id, limit=10):
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
