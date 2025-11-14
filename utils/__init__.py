"""
Utils Package
Helper functions and utilities
"""

from .helpers import normalize_text, get_user_profile_safe
from .database import init_db, update_user_points, get_user_stats, get_leaderboard

__all__ = [
    'normalize_text',
    'get_user_profile_safe',
    'init_db',
    'update_user_points',
    'get_user_stats',
    'get_leaderboard'
]
