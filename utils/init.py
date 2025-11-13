"""
Utils Package - Game Bot Utilities
===================================
مجموعة أدوات مساعدة للبوت
"""

from .database import (
    init_db,
    get_db_connection,
    update_user_points,
    get_user_stats,
    get_leaderboard,
    get_user_game_history
)

from .helpers import (
    get_user_profile_safe,
    check_rate_limit,
    sanitize_text,
    format_number,
    get_time_greeting
)

from .ui_components import (
    create_flex_message,
    create_welcome_bubble,
    create_stats_bubble,
    create_leaderboard_bubble,
    create_game_result_bubble,
    get_quick_reply_buttons
)

from .gemini_config import (
    get_gemini_api_key,
    switch_gemini_key,
    is_ai_available
)

__all__ = [
    # Database
    'init_db',
    'get_db_connection',
    'update_user_points',
    'get_user_stats',
    'get_leaderboard',
    'get_user_game_history',
    
    # Helpers
    'get_user_profile_safe',
    'check_rate_limit',
    'sanitize_text',
    'format_number',
    'get_time_greeting',
    
    # UI Components
    'create_flex_message',
    'create_welcome_bubble',
    'create_stats_bubble',
    'create_leaderboard_bubble',
    'create_game_result_bubble',
    'get_quick_reply_buttons',
    
    # Gemini Config
    'get_gemini_api_key',
    'switch_gemini_key',
    'is_ai_available'
]

__version__ = '1.0.0'
