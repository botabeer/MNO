"""
Database Management - إدارة قاعدة البيانات
==========================================
جميع عمليات قاعدة البيانات في مكان واحد
"""

import sqlite3
from datetime import datetime
import logging
from constants import DB_NAME

logger = logging.getLogger(__name__)

class Database:
    """إدارة قاعدة البيانات"""
    
    @staticmethod
    def get_connection():
        """إنشاء اتصال آمن"""
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    @staticmethod
    def init():
        """إنشاء الجداول"""
        try:
            conn = Database.get_connection()
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
            
            # الفهارس
            c.execute('CREATE INDEX IF NOT EXISTS idx_user_points ON users(total_points DESC)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_game_history_user ON game_history(user_id, played_at DESC)')
            
            conn.commit()
            conn.close()
            logger.info("✅ قاعدة البيانات جاهزة")
            return True
        except Exception as e:
            logger.error(f"❌ خطأ إنشاء قاعدة البيانات: {e}")
            return False
    
    @staticmethod
    def ensure_user_exists(user_id):
        """التأكد من وجود المستخدم"""
        try:
            conn = Database.get_connection()
            c = conn.cursor()
            c.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            
            if not c.fetchone():
                display_name = f"لاعب_{user_id[-4:]}"
                c.execute('''INSERT INTO users (user_id, display_name, total_points, 
                             games_played, wins, last_played) 
                             VALUES (?, ?, 0, 0, 0, ?)''',
                          (user_id, display_name, datetime.now().isoformat()))
                conn.commit()
                logger.info(f"🆕 إنشاء سجل جديد: {display_name}")
            
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ خطأ ensure_user_exists: {e}")
            return False
    
    @staticmethod
    def update_user_points(user_id, display_name, points, won=False, game_type=""):
        """تحديث نقاط المستخدم"""
        try:
            conn = Database.get_connection()
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = c.fetchone()
            
            if user:
                c.execute('''UPDATE users SET total_points = ?, games_played = ?, wins = ?, 
                             last_played = ?, display_name = ? WHERE user_id = ?''',
                          (user['total_points'] + points, user['games_played'] + 1,
                           user['wins'] + (1 if won else 0), datetime.now().isoformat(),
                           display_name, user_id))
                
                if user['display_name'] != display_name:
                    logger.info(f"🔄 تحديث اسم: {user['display_name']} → {display_name}")
            else:
                c.execute('''INSERT INTO users (user_id, display_name, total_points, 
                             games_played, wins, last_played) VALUES (?, ?, ?, ?, ?, ?)''',
                          (user_id, display_name, points, 1, 1 if won else 0, datetime.now().isoformat()))
                logger.info(f"✅ إضافة مستخدم جديد: {display_name}")
            
            if game_type:
                c.execute('''INSERT INTO game_history (user_id, game_type, points, won) 
                             VALUES (?, ?, ?, ?)''', (user_id, game_type, points, 1 if won else 0))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ خطأ تحديث النقاط: {e}")
            return False
    
    @staticmethod
    def get_user_stats(user_id):
        """الحصول على إحصائيات المستخدم"""
        try:
            conn = Database.get_connection()
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = c.fetchone()
            conn.close()
            return user
        except Exception as e:
            logger.error(f"❌ خطأ الإحصائيات: {e}")
            return None
    
    @staticmethod
    def get_leaderboard(limit=10):
        """الحصول على لوحة الصدارة"""
        try:
            conn = Database.get_connection()
            c = conn.cursor()
            c.execute('''SELECT display_name, total_points, games_played, wins 
                         FROM users ORDER BY total_points DESC LIMIT ?''', (limit,))
            leaders = c.fetchall()
            conn.close()
            return leaders
        except Exception as e:
            logger.error(f"❌ خطأ الصدارة: {e}")
            return []
    
    @staticmethod
    def update_display_name(user_id, display_name):
        """تحديث اسم المستخدم"""
        try:
            conn = Database.get_connection()
            c = conn.cursor()
            c.execute('SELECT display_name FROM users WHERE user_id = ?', (user_id,))
            result = c.fetchone()
            
            if result:
                old_name = result['display_name']
                if old_name != display_name:
                    c.execute('UPDATE users SET display_name = ? WHERE user_id = ?',
                              (display_name, user_id))
                    conn.commit()
                    logger.info(f"🔄 تحديث اسم: {old_name} → {display_name}")
            else:
                c.execute('''INSERT INTO users (user_id, display_name, total_points, 
                             games_played, wins) VALUES (?, ?, 0, 0, 0)''',
                          (user_id, display_name))
                conn.commit()
                logger.info(f"✅ حفظ اسم جديد: {display_name}")
            
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ خطأ تحديث الاسم: {e}")
            return False
