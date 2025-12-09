# constants.py
from datetime import timedelta

# ================== Themes ================== #
THEMES = {
    "light": {
        "primary": "#007AFF",
        "success": "#34C759",
        "warning": "#FF9500",
        "danger": "#FF3B30",
        "card_bg": "#F2F2F7",
        "white": "#FFFFFF",
        "text_dark": "#000000",
        "text_light": "#8E8E93",
        "border": "#C6C6C8",
        "secondary_bg": "#E5E5EA"
    },
    "dark": {
        "primary": "#0A84FF",
        "success": "#30D158",
        "warning": "#FF9F0A",
        "danger": "#FF453A",
        "card_bg": "#1C1C1E",
        "white": "#FFFFFF",
        "text_dark": "#FFFFFF",
        "text_light": "#8E8E93",
        "border": "#38383A",
        "secondary_bg": "#2C2C2E"
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
    "loreet": "لو ريت"
}
