"""
Database Module - إدارة قاعدة البيانات
======================================
نظام محسّن لإدارة البيانات والإحصائيات
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_NAME = 'game_scores.db'

@contextmanager
def get_db_connection():
    """
    Context manager لاتصال آمن بقاعدة البيانات
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        yield conn
    except Exception as e:
        logger.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def init_db() -> bool:
    """
    إنشاء جداول قاعدة البيانات
    Returns: True إذا نجحت العملية
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # جدول المستخدمين
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    total_points INTEGER DEFAULT 0,
                    games_played INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    current_streak INTEGER DEFAULT 0,
                    best_streak INTEGER DEFAULT 0,
                    last_played TEXT,
                    registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    avatar_emoji TEXT DEFAULT '👤'
                )
            ''')
            
            # جدول تاريخ الألعاب
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    game_type TEXT NOT NULL,
                    points INTEGER DEFAULT 0,
                    won INTEGER DEFAULT 0,
                    played_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    duration_seconds INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # جدول الإنجازات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    achievement_type TEXT NOT NULL,
                    unlocked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    UNIQUE(user_id, achievement_type)
                )
            ''')
            
            # إنشاء فهارس لتحسين الأداء
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_points 
                ON users(total_points DESC)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_game_history_user 
                ON game_history(user_id, played_at DESC)
            ''')
            
            conn.commit()
            logger.info("✅ تم إنشاء قاعدة البيانات بنجاح")
            return True
            
    except Exception as e:
        logger.error(f"❌ خطأ في إنشاء قاعدة البيانات: {e}")
        return False

def update_user_points(
    user_id: str,
    display_name: str,
    points: int,
    won: bool = False,
    game_type: str = "",
    duration: int = 0
) -> bool:
    """
    تحديث نقاط المستخدم وإحصائياته
    
    Args:
        user_id: معرف المستخدم
        display_name: اسم العرض
        points: النقاط المكتسبة
        won: هل فاز في اللعبة
        game_type: نوع اللعبة
        duration: مدة اللعبة بالثواني
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # التحقق من وجود المستخدم
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            
            if user:
                # تحديث البيانات الموجودة
                new_points = user['total_points'] + points
                new_games = user['games_played'] + 1
                new_wins = user['wins'] + (1 if won else 0)
                new_losses = user['losses'] + (0 if won else 1)
                
                # تحديث السلسلة
                if won:
                    new_streak = user['current_streak'] + 1
                    new_best_streak = max(new_streak, user['best_streak'])
                else:
                    new_streak = 0
                    new_best_streak = user['best_streak']
                
                cursor.execute('''
                    UPDATE users SET 
                        total_points = ?,
                        games_played = ?,
                        wins = ?,
                        losses = ?,
                        current_streak = ?,
                        best_streak = ?,
                        last_played = ?,
                        display_name = ?
                    WHERE user_id = ?
                ''', (
                    new_points, new_games, new_wins, new_losses,
                    new_streak, new_best_streak,
                    datetime.now().isoformat(),
                    display_name, user_id
                ))
            else:
                # إنشاء مستخدم جديد
                cursor.execute('''
                    INSERT INTO users (
                        user_id, display_name, total_points,
                        games_played, wins, losses,
                        current_streak, best_streak, last_played
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, display_name, points,
                    1, 1 if won else 0, 0 if won else 1,
                    1 if won else 0, 1 if won else 0,
                    datetime.now().isoformat()
                ))
            
            # إضافة سجل اللعبة
            if game_type:
                cursor.execute('''
                    INSERT INTO game_history (
                        user_id, game_type, points, won, duration_seconds
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (user_id, game_type, points, 1 if won else 0, duration))
            
            conn.commit()
            logger.info(f"✅ تم تحديث نقاط {display_name}: +{points}")
            return True
            
    except Exception as e:
        logger.error(f"❌ خطأ في تحديث النقاط: {e}")
        return False

def get_user_stats(user_id: str) -> Optional[Dict]:
    """
    الحصول على إحصائيات المستخدم
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            
            if user:
                return dict(user)
            return None
            
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على الإحصائيات: {e}")
        return None

def get_leaderboard(limit: int = 10) -> List[Dict]:
    """
    الحصول على لوحة الصدارة
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    display_name,
                    total_points,
                    games_played,
                    wins,
                    avatar_emoji,
                    best_streak
                FROM users
                ORDER BY total_points DESC, wins DESC
                LIMIT ?
            ''', (limit,))
            
            leaders = cursor.fetchall()
            return [dict(row) for row in leaders]
            
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على الصدارة: {e}")
        return []

def get_user_game_history(user_id: str, limit: int = 10) -> List[Dict]:
    """
    الحصول على تاريخ ألعاب المستخدم
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    game_type,
                    points,
                    won,
                    played_at,
                    duration_seconds
                FROM game_history
                WHERE user_id = ?
                ORDER BY played_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            history = cursor.fetchall()
            return [dict(row) for row in history]
            
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على التاريخ: {e}")
        return []

def get_user_rank(user_id: str) -> Optional[int]:
    """
    الحصول على ترتيب المستخدم
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) + 1 as rank
                FROM users
                WHERE total_points > (
                    SELECT total_points FROM users WHERE user_id = ?
                )
            ''', (user_id,))
            
            result = cursor.fetchone()
            return result['rank'] if result else None
            
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على الترتيب: {e}")
        return None

def unlock_achievement(user_id: str, achievement_type: str) -> bool:
    """
    فتح إنجاز للمستخدم
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO achievements (user_id, achievement_type)
                VALUES (?, ?)
            ''', (user_id, achievement_type))
            
            conn.commit()
            return cursor.rowcount > 0
            
    except Exception as e:
        logger.error(f"❌ خطأ في فتح الإنجاز: {e}")
        return False

def get_user_achievements(user_id: str) -> List[str]:
    """
    الحصول على إنجازات المستخدم
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT achievement_type
                FROM achievements
                WHERE user_id = ?
                ORDER BY unlocked_at DESC
            ''', (user_id,))
            
            achievements = cursor.fetchall()
            return [row['achievement_type'] for row in achievements]
            
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على الإنجازات: {e}")
        return []
