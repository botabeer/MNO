# games/constants.py
from datetime import timedelta

COLORS = {
    "primary": "#1E90FF",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "card_bg": "#FAFAFB",
    "white": "#FFFFFF",
    "text_dark": "#111827",
    "text_light": "#6B7280",
    "border": "#E5E7EB",
}

MAFIA_CONFIG = {
    "min_players": 4,
    "role_counts": {
        "mafia": 1,
        "detective": 1,
        "doctor": 1
    }
}

INACTIVITY_DAYS = 30
STORAGE_FILE = "data/storage.json"
GAMES_STATE_FILE = "data/games_state.json"
DEFAULT_QUESTIONS_PER_GAME = 5
DEFAULT_WORDS_NEEDED = 3
POINTS_PER_CORRECT_ANSWER = 1
POINTS_PER_WORD = 3
MAX_MESSAGES_PER_HOUR = 50
RATE_LIMIT_PERIOD = 3600
MAX_NAME_LENGTH = 30
MIN_NAME_LENGTH = 1

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
