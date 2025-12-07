"""
constants.py
-------------
هذا الملف يحتوي على جميع الثوابت العامة للمشروع، بما في ذلك
الألوان – الإعدادات – خصائص الألعاب – القيم الافتراضية.

تم تنظيم الثوابت وفقًا لـ:
1. إعدادات الواجهة UI
2. إعدادات الألعاب العامة
3. إعدادات لعبة المافيا
4. إعدادات النظام
"""

# ----------------------------------
# 🎨 UI COLORS & THEMES
# ----------------------------------

COLORS = {
    "primary": "#6B9BD1",
    "primary_dark": "#4A7BA7",

    "background": "#F5F7FA",
    "background_light": "#FFFFFF",
    "bg": "#F5F7FA",

    "card": "#FFFFFF",
    "card_bg": "#FFFFFF",

    "text": "#2C3E50",
    "text_dark": "#2C3E50",
    "text_secondary": "#7F8C8D",
    "text_light": "#95A5A6",

    "white": "#FFFFFF",

    "success": "#52C5B6",
    "warning": "#F39C6B",
    "error": "#E17B7B",
    "info": "#6B9BD1",

    "border": "#E8ECEF",
    "progress_bg": "#E8ECEF",
    "progress_fill": "#6B9BD1",

    # rgba غير مدعوم من LINE مباشرة لكنه يستخدم في تأثيرات UI
    "shadow": "rgba(107, 155, 209, 0.15)",

    "secondary": "#7F8C8D",
}

THEMES = {
    "default": COLORS
}

DEFAULT_THEME = "default"

# ----------------------------------
# 🧩 GAME GENERAL SETTINGS
# ----------------------------------

POINTS = {
    "correct_answer": 1,
    "hint_used": 0,
    "show_answer": 0
}

QUESTIONS_PER_GAME = 5

# ----------------------------------
# 🕵️‍♂️ MAFIA GAME SETTINGS
# ----------------------------------

MAFIA_CONFIG = {
    "min_players": 4,
    "max_players": 20,

    "roles": {
        "mafia": 1,
        "detective": 1,
        "doctor": 1,
        "citizen": "remaining"
    },

    "phases": [
        "registration",
        "night",
        "day",
        "voting",
        "ended"
    ],

    "night_duration": 60,   # seconds
    "day_duration": 120,    # seconds
    "voting_duration": 60   # seconds
}

# ----------------------------------
# 🛰 SYSTEM SETTINGS
# ----------------------------------

# مدة حذف بيانات المستخدم غير النشط
INACTIVITY_DAYS = 30
