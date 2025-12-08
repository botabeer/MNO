import sqlite3
import logging
from threading import Lock
from datetime import datetime, timedelta
from constants import INACTIVITY_DAYS

logger = logging.getLogger(__name__)


class Database:
    """Database helper for managing user data, scores, and game history."""

    DB_NAME = "game_scores.db"
    _lock = Lock()

    # =============================
    #  Connection Helper
    # =============================
    @staticmethod
    def get_connection():
        """Returns a SQLite connection with WAL-mode enabled."""
        conn = sqlite3.connect(
            Database.DB_NAME, timeout=10.0, check_same_thread=False
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # =============================
    #  Initialize Database
    # =============================
    @staticmethod
    def init():
        """Creates tables and indexes if they do not exist."""
        try:
            with Database.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        display_name TEXT NOT NULL,
                        total_points INTEGER DEFAULT 0,
                        games_played INTEGER DEFAULT 0,
                        wins INTEGER DEFAULT 0,
                        is_active INTEGER DEFAULT 1,
                        is_withdrawn INTEGER DEFAULT 0,
                        last_activity TEXT DEFAULT CURRENT_TIMESTAMP,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS game_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        game_type TEXT NOT NULL,
                        points INTEGER DEFAULT 0,
                        won INTEGER DEFAULT 0,
                        played_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                    """
                )

                # Indexes
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_users_points ON users(total_points DESC, wins DESC)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_users_activity ON users(last_activity, is_active)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_game_history_user ON game_history(user_id, played_at)"
                )

                logger.info("Database initialized successfully")

        except Exception as e:
            logger.error("Database initialization error", exc_info=True)
            raise

    # =============================
    #  Utility Helper
    # =============================
    @staticmethod
    def _parse_datetime(dt_str):
        """Parses SQLite datetime formats safely."""
        if not dt_str:
            return None

        patterns = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
        ]

        for fmt in patterns:
            try:
                return datetime.strptime(dt_str, fmt)
            except:
                continue

        return None

    # =============================
    #  User Registration / Update
    # =============================
    @staticmethod
    def register_or_update_user(user_id, display_name):
        """Registers new user or updates existing profile."""
        with Database._lock:
            try:
                with Database.get_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        "SELECT 1 FROM users WHERE user_id = ?", (user_id,)
                    )
                    exists = cursor.fetchone()

                    if exists:
                        cursor.execute(
                            """
                            UPDATE users
                            SET display_name = ?,
                                is_active = 1,
                                is_withdrawn = 0,
                                last_activity = CURRENT_TIMESTAMP,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE user_id = ?
                            """,
                            (display_name, user_id),
                        )
                    else:
                        cursor.execute(
                            """
                            INSERT INTO users (user_id, display_name)
                            VALUES (?, ?)
                            """,
                            (user_id, display_name),
                        )

                    logger.info(f"User registered/updated: {display_name}")
                    return True

            except Exception as e:
                logger.error("Error registering user", exc_info=True)
                return False

    # =============================
    #  Update Last Activity
    # =============================
    @staticmethod
    def update_last_activity(user_id):
        """Updates the last activity timestamp for an active user."""
        with Database._lock:
            try:
                with Database.get_connection() as conn:
                    conn.execute(
                        """
                        UPDATE users
                        SET last_activity = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND is_active = 1 AND is_withdrawn = 0
                        """,
                        (user_id,),
                    )
                    return True
            except Exception:
                logger.error("Error updating activity", exc_info=True)
                return False

    # =============================
    #  Cleanup Inactive Users
    # =============================
    @staticmethod
    def cleanup_inactive_users():
        """Marks users as inactive if they haven't logged in within INACTIVITY_DAYS."""
        with Database._lock:
            try:
                cutoff = (datetime.now() - timedelta(days=INACTIVITY_DAYS)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                with Database.get_connection() as conn:
                    cursor = conn.execute(
                        """
                        UPDATE users
                        SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                        WHERE last_activity < ? AND is_active = 1
                        """,
                        (cutoff,),
                    )

                    count = cursor.rowcount
                    if count > 0:
                        logger.info(f"Deactivated {count} inactive users")

                    return count

            except Exception:
                logger.error("Error cleaning inactive users", exc_info=True)
                return 0

    # =============================
    #  User Status Checks
    # =============================
    @staticmethod
    def is_user_registered(user_id):
        """Checks if a user is active and not withdrawn."""
        try:
            with Database.get_connection() as conn:
                cur = conn.execute(
                    """
                    SELECT is_active, is_withdrawn 
                    FROM users 
                    WHERE user_id = ?
                    """,
                    (user_id,),
                )
                r = cur.fetchone()
                return bool(r and r["is_active"] == 1 and r["is_withdrawn"] == 0)

        except Exception:
            logger.error("Error checking user registration", exc_info=True)
            return False

    @staticmethod
    def is_user_withdrawn(user_id):
        """Returns True if user marked as withdrawn."""
        try:
            with Database.get_connection() as conn:
                cur = conn.execute(
                    "SELECT is_withdrawn FROM users WHERE user_id = ?",
                    (user_id,),
                )
                r = cur.fetchone()
                return bool(r and r["is_withdrawn"] == 1)

        except Exception:
            logger.error("Error checking user withdrawal", exc_info=True)
            return False

    # =============================
    #  Withdraw & Reactivate
    # =============================
    @staticmethod
    def withdraw_user(user_id):
        """Marks user as withdrawn."""
        with Database._lock:
            try:
                with Database.get_connection() as conn:
                    cur = conn.execute(
                        """
                        UPDATE users
                        SET is_withdrawn = 1,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                        """,
                        (user_id,),
                    )
                    return cur.rowcount > 0

            except Exception:
                logger.error("Error withdrawing user", exc_info=True)
                return False

    @staticmethod
    def reactivate_user(user_id):
        """Reactivates withdrawn or inactive user."""
        with Database._lock:
            try:
                with Database.get_connection() as conn:
                    cur = conn.execute(
                        """
                        UPDATE users
                        SET is_active = 1,
                            is_withdrawn = 0,
                            last_activity = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                        """,
                        (user_id,),
                    )
                    return cur.rowcount > 0

            except Exception:
                logger.error("Error reactivating user", exc_info=True)
                return False

    # =============================
    #  Fetch User Name
    # =============================
    @staticmethod
    def get_existing_user_name(user_id):
        """Returns user's display name."""
        try:
            with Database.get_connection() as conn:
                cur = conn.execute(
                    "SELECT display_name FROM users WHERE user_id = ?",
                    (user_id,),
                )
                row = cur.fetchone()
                return row["display_name"] if row else None

        except Exception:
            logger.error("Error fetching username", exc_info=True)
            return None

    # =============================
    #  Update Points + History
    # =============================
    @staticmethod
    def update_user_points(user_id, points, won, game_type):
        """Updates user score and inserts history entry."""
        with Database._lock:
            try:
                with Database.get_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        SELECT is_active, is_withdrawn
                        FROM users
                        WHERE user_id = ?
                        """,
                        (user_id,),
                    )
                    r = cursor.fetchone()

                    if not r or r["is_active"] != 1 or r["is_withdrawn"] == 1:
                        logger.warning(f"Point update denied for {user_id}")
                        return False

                    cursor.execute(
                        """
                        UPDATE users
                        SET total_points = total_points + ?,
                            games_played = games_played + 1,
                            wins = wins + ?,
                            last_activity = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                        """,
                        (points, int(won), user_id),
                    )

                    cursor.execute(
                        """
                        INSERT INTO game_history (user_id, game_type, points, won)
                        VALUES (?, ?, ?, ?)
                        """,
                        (user_id, game_type, points, int(won)),
                    )

                    logger.info(f"Points updated: {user_id} +{points}")
                    return True

            except Exception:
                logger.error("Error updating points", exc_info=True)
                return False

    # =============================
    #  Fetch Stats
    # =============================
    @staticmethod
    def get_user_stats(user_id):
        """Returns user's score statistics."""
        try:
            with Database.get_connection() as conn:
                cur = conn.execute(
                    """
                    SELECT total_points, games_played, wins, display_name
                    FROM users
                    WHERE user_id = ? AND is_withdrawn = 0
                    """,
                    (user_id,),
                )
                r = cur.fetchone()

                if not r:
                    return {
                        "total_points": 0,
                        "games_played": 0,
                        "wins": 0,
                        "display_name": "User",
                    }

                return {
                    "total_points": r["total_points"] or 0,
                    "games_played": r["games_played"] or 0,
                    "wins": r["wins"] or 0,
                    "display_name": r["display_name"],
                }

        except Exception:
            logger.error("Error fetching stats", exc_info=True)
            return {
                "total_points": 0,
                "games_played": 0,
                "wins": 0,
                "display_name": "User",
            }

    # =============================
    #  Leaderboard
    # =============================
    @staticmethod
    def get_leaderboard(limit=20):
        """Returns a leaderboard sorted by points."""
        try:
            with Database.get_connection() as conn:
                cur = conn.execute(
                    """
                    SELECT display_name, total_points, games_played, wins
                    FROM users
                    WHERE is_withdrawn = 0
                    ORDER BY total_points DESC, wins DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
                return [dict(r) for r in cur.fetchall()]

        except Exception:
            logger.error("Error fetching leaderboard", exc_info=True)
            return []

    # =============================
    #  Get All Players
    # =============================
    @staticmethod
    def get_all_players():
        """Returns all players with active/withdrawn status."""
        try:
            cutoff_date = datetime.now() - timedelta(days=INACTIVITY_DAYS)

            with Database.get_connection() as conn:
                cur = conn.execute(
                    """
                    SELECT display_name, total_points, games_played,
                           is_active, is_withdrawn, last_activity
                    FROM users
                    ORDER BY total_points DESC
                    """
                )

                players = []
                for r in cur.fetchall():
                    last = Database._parse_datetime(r["last_activity"])
                    active = (
                        r["is_active"] == 1
                        and r["is_withdrawn"] == 0
                        and last
                        and last >= cutoff_date
                    )

                    players.append(
                        {
                            "display_name": r["display_name"],
                            "total_points": r["total_points"],
                            "games_played": r["games_played"],
                            "active": active,
                            "withdrawn": r["is_withdrawn"] == 1,
                        }
                    )

                return players

        except Exception:
            logger.error("Error fetching players", exc_info=True)
            return []
