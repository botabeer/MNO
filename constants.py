# constants.py
from datetime import timedelta

# ثيم الألوان (استخدمها في كل الألعاب)
COLORS = {
    "primary": "#1E90FF",
    "white": "#FFFFFF",
    "card_bg": "#FAFAFB",
    "text_dark": "#111827",
    "text_light": "#6B7280",
    "border": "#E5E7EB",
    "success": "#10B981",
    "warning": "#F59E0B"
}

# إعدادات خاصة بالمافيا
MAFIA_CONFIG = {
    "min_players": 4,
    "role_counts": {"mafia": 1, "detective": 1, "doctor": 1}
}

# مدة بقاء المستخدم نشط قبل إزالته من لوحة الصدارة (30 يومًا)
INACTIVITY_DAYS = 30

# مسميات المسارات للملفات (تغيير حسب حاجتك)
STORAGE_FILE = "data/storage.json"
GAMES_STATE_FILE = "data/games_state.json"
