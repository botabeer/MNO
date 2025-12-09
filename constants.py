# constants.py
from datetime import timedelta

# ================== Themes - iOS Style ================== #
THEMES = {
    "light": {
        # iOS Light Theme - Clean & Modern
        "primary": "#007AFF",           # iOS Blue
        "success": "#34C759",           # iOS Green
        "warning": "#FF9500",           # iOS Orange
        "danger": "#FF3B30",            # iOS Red
        "card_bg": "#FFFFFF",           # Pure White
        "secondary_bg": "#F2F2F7",     # Light Gray
        "white": "#FFFFFF",
        "text_dark": "#000000",
        "text_light": "#8E8E93",       # iOS Gray
        "border": "#E5E5EA",           # Light Border
        "glass_bg": "rgba(255, 255, 255, 0.7)",  # Glassmorphism
        "shadow": "rgba(0, 0, 0, 0.1)"
    },
    "dark": {
        # iOS Dark Theme - Elegant & Eye-friendly
        "primary": "#0A84FF",           # iOS Blue (Dark)
        "success": "#30D158",           # iOS Green (Dark)
        "warning": "#FF9F0A",           # iOS Orange (Dark)
        "danger": "#FF453A",            # iOS Red (Dark)
        "card_bg": "#1C1C1E",           # Dark Gray
        "secondary_bg": "#2C2C2E",     # Lighter Dark Gray
        "white": "#FFFFFF",
        "text_dark": "#FFFFFF",
        "text_light": "#98989D",       # iOS Gray (Dark)
        "border": "#38383A",           # Dark Border
        "glass_bg": "rgba(28, 28, 30, 0.7)",  # Glassmorphism Dark
        "shadow": "rgba(0, 0, 0, 0.3)"
    }
}

COLORS = THEMES["light"]

# ================== Mafia Configuration ================== #
MAFIA_CONFIG = {
    "min_players": 4,
    "role_counts": {
        "mafia": 1,
        "detective": 1,
        "doctor": 1,
    }
}

# ================== User Settings ================== #
INACTIVITY_DAYS = 30
DEFAULT_THEME = "light"

# ================== File Paths ================== #
STORAGE_FILE = "data/storage.json"
GAMES_STATE_FILE = "data/games_state.json"

# ================== Game Settings ================== #
DEFAULT_QUESTIONS_PER_GAME = 5
DEFAULT_WORDS_NEEDED = 3
POINTS_PER_CORRECT_ANSWER = 1
POINTS_PER_WORD = 3

# ================== Rate Limiting ================== #
MAX_MESSAGES_PER_HOUR = 50
RATE_LIMIT_PERIOD = 3600

# ================== Name Validation ================== #
MAX_NAME_LENGTH = 30
MIN_NAME_LENGTH = 1

# ================== Game Types ================== #
GAME_TYPES = {
    "song": "الاغنية",
    "chain": "سلسلة الكلمات",
    "opposite": "الاضداد",
    "fast_typing": "التايب السريع",
    "letters": "تكوين الكلمات",
    "seen_jeem": "سين جيم",
    "human_animal": "انسان حيوان نبات بلاد",
    "compatibility": "نسبة التوافق",
    "mafia": "المافيا",
    "letter": "لعبة حروف"
}
