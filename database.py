"""
Database - نظام قاعدة البيانات المحسن
======================================
"""

import sqlite3
import logging
from datetime import datetime
from threading import Lock

logger = logging.getLogger("mafia-bot")

class Database:
    """إدارة قاعدة البيانات"""
    
    DB_NAME = 'game_scores.db'
    _lock = Lock()
    
    @staticmethod
    def init():
        """تهيئة قاعدة البيانات"""
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            
            # جدول المستخدمين
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    line_name TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    total_points INTEGER DEFAULT 0,
                    games_played INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول تاريخ الألعاب
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
            
            # جدول لعبة المافيا
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mafia_games (
                    game_id TEXT PRIMARY KEY,
                    group_id TEXT NOT NULL,
                    status TEXT DEFAULT 'registration',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mafia_players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    role TEXT,
                    is_alive BOOLEAN DEFAULT 1,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES mafia_games(game_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("تم تهيئة قاعدة البيانات بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة قاعدة البيانات: {e}")
    
    @staticmethod
    def register_user(user_id, line_name, display_name):
        """تسجيل مستخدم جديد"""
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR IGNORE INTO users (user_id, line_name, display_name)
                    VALUES (?, ?, ?)
                ''', (user_id, line_name, display_name))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                logger.error(f"خطأ في تسجيل المستخدم: {e}")
                return False
    
    @staticmethod
    def update_user_name(user_id, line_name, display_name):
        """تحديث اسم المستخدم"""
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO users (user_id, line_name, display_name)
                    VALUES (?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        line_name = excluded.line_name,
                        display_name = excluded.display_name,
                        updated_at = CURRENT_TIMESTAMP
                ''', (user_id, line_name, display_name))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                logger.error(f"خطأ في تحديث اسم المستخدم: {e}")
                return False
    
    @staticmethod
    def is_user_registered(user_id):
        """التحقق من تسجيل المستخدم"""
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            
            cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            conn.close()
            return result is not None
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من التسجيل: {e}")
            return False
    
    @staticmethod
    def get_user_display_name(user_id):
        """الحصول على اسم العرض"""
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            
            cursor.execute('SELECT display_name FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            conn.close()
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الاسم: {e}")
            return None
    
    @staticmethod
    def update_user_points(user_id, display_name, points, won, game_type):
        """تحديث نقاط المستخدم"""
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                
                # تحديث النقاط الكلية
                cursor.execute('''
                    UPDATE users 
                    SET total_points = total_points + ?,
                        games_played = games_played + 1,
                        wins = wins + ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (points, 1 if won else 0, user_id))
                
                # إضافة سجل اللعبة
                cursor.execute('''
                    INSERT INTO game_history (user_id, game_type, points, won)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, game_type, points, won))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                logger.error(f"خطأ في تحديث النقاط: {e}")
                return False
    
    @staticmethod
    def get_user_stats(user_id):
        """الحصول على إحصائيات المستخدم"""
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT total_points, games_played, wins, display_name
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
            logger.error(f"خطأ في الحصول على الإحصائيات: {e}")
            return None
    
    @staticmethod
    def get_leaderboard(limit=10):
        """الحصول على لوحة الصدارة"""
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT display_name, total_points, games_played, wins
                FROM users
                WHERE games_played > 0
                ORDER BY total_points DESC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [{
                'display_name': r[0],
                'total_points': r[1],
                'games_played': r[2],
                'wins': r[3]
            } for r in results]
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الصدارة: {e}")
            return []
    
    @staticmethod
    def delete_user(user_id):
        """حذف مستخدم"""
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM game_history WHERE user_id = ?', (user_id,))
                cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                logger.error(f"خطأ في حذف المستخدم: {e}")
                return False
    
    # وظائف لعبة المافيا
    
    @staticmethod
    def create_mafia_game(game_id, group_id):
        """إنشاء لعبة مافيا جديدة"""
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO mafia_games (game_id, group_id, status)
                    VALUES (?, ?, 'registration')
                ''', (game_id, group_id))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                logger.error(f"خطأ في إنشاء لعبة المافيا: {e}")
                return False
    
    @staticmethod
    def add_mafia_player(game_id, user_id):
        """إضافة لاعب للعبة المافيا"""
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO mafia_players (game_id, user_id)
                    VALUES (?, ?)
                ''', (game_id, user_id))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                logger.error(f"خطأ في إضافة لاعب المافيا: {e}")
                return False
    
    @staticmethod
    def get_mafia_players(game_id):
        """الحصول على لاعبي المافيا"""
        try:
            conn = sqlite3.connect(Database.DB_NAME)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT mp.user_id, u.display_name, mp.role, mp.is_alive
                FROM mafia_players mp
                JOIN users u ON mp.user_id = u.user_id
                WHERE mp.game_id = ?
                ORDER BY mp.joined_at
            ''', (game_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [{
                'user_id': r[0],
                'display_name': r[1],
                'role': r[2],
                'is_alive': bool(r[3])
            } for r in results]
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على لاعبي المافيا: {e}")
            return []
    
    @staticmethod
    def update_mafia_roles(game_id, roles_dict):
        """تحديث أدوار لاعبي المافيا"""
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                
                for user_id, role in roles_dict.items():
                    cursor.execute('''
                        UPDATE mafia_players
                        SET role = ?
                        WHERE game_id = ? AND user_id = ?
                    ''', (role, game_id, user_id))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                logger.error(f"خطأ في تحديث أدوار المافيا: {e}")
                return False
    
    @staticmethod
    def end_mafia_game(game_id):
        """إنهاء لعبة المافيا"""
        with Database._lock:
            try:
                conn = sqlite3.connect(Database.DB_NAME)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE mafia_games
                    SET status = 'ended', ended_at = CURRENT_TIMESTAMP
                    WHERE game_id = ?
                ''', (game_id,))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                logger.error(f"خطأ في إنهاء لعبة المافيا: {e}")
                return False
