# constants.py - Enhanced Constants
from datetime import timedelta

# ========== Color Theme ========== #
COLORS = {
    # Primary colors
    "primary": "#1E90FF",      # Dodger Blue - لون أساسي حيوي
    "success": "#10B981",      # Emerald Green - نجاح
    "warning": "#F59E0B",      # Amber - تحذير
    "danger": "#EF4444",       # Red - خطر
    
    # Background colors
    "card_bg": "#FAFAFB",      # Light Gray - خلفية البطاقات
    "white": "#FFFFFF",        # White - أبيض
    
    # Text colors
    "text_dark": "#111827",    # Almost Black - نص داكن
    "text_light": "#6B7280",   # Gray - نص فاتح
    
    # Border colors
    "border": "#E5E7EB",       # Light Gray - حدود
}

# ========== Mafia Game Configuration ========== #
MAFIA_CONFIG = {
    "min_players": 4,
    "role_counts": {
        "mafia": 1,
        "detective": 1,
        "doctor": 1
    }
}

# ========== User Activity Settings ========== #
INACTIVITY_DAYS = 30  # عدد أيام عدم النشاط قبل إزالة المستخدم

# ========== File Paths ========== #
STORAGE_FILE = "data/storage.json"
GAMES_STATE_FILE = "data/games_state.json"

# ========== Game Settings ========== #
DEFAULT_QUESTIONS_PER_GAME = 5
DEFAULT_WORDS_NEEDED = 3
POINTS_PER_CORRECT_ANSWER = 1
POINTS_PER_WORD = 3  # For games like human_animal

# ========== Rate Limiting ========== #
MAX_MESSAGES_PER_HOUR = 50
RATE_LIMIT_PERIOD = 3600  # seconds

# ========== Name Validation ========== #
MAX_NAME_LENGTH = 30
MIN_NAME_LENGTH = 1

# ========== Game Types ========== #
GAME_TYPES = {
    "song": "لعبة الأغنية",
    "chain": "سلسلة الكلمات",
    "opposite": "الأضداد",
    "fast_typing": "التايب السريع",
    "letters": "تكوين الكلمات",
    "category": "فئة وحرف",
    "human_animal": "إنسان حيوان نبات بلاد",
    "compatibility": "نسبة التوافق",
    "mafia": "المافيا"
}
