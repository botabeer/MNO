"""
Constants - ثوابت المشروع المحسنة
===================================
"""

# ألوان التصميم الموحدة
COLORS = {
    'primary': '#1a1a1a',
    'secondary': '#4a4a4a',
    'light': '#f5f5f5',
    'medium': '#9a9a9a',
    'text_dark': '#2a2a2a',
    'text_light': '#6a6a6a',
    'white': '#ffffff',
    'border': '#e8e8e8',
    'background': '#f8f8f8',
    'success': '#2a2a2a',
    'error': '#4a4a4a'
}

# نظام النقاط
POINTS = {
    'correct_answer': 10,
    'hint_penalty': -2,
    'show_answer_penalty': -5,
    'perfect_game_bonus': 20,
    'mafia_win': 15,
    'citizen_win': 10
}

# عدد الأسئلة
QUESTIONS_PER_GAME = 5

# رسائل النجاح والفشل (بدون إيموجي)
MESSAGES = {
    'correct': [
        'إجابة صحيحة',
        'ممتاز',
        'صحيح',
        'رائع',
        'أحسنت'
    ],
    'wrong': [
        'إجابة خاطئة',
        'للأسف خطأ',
        'غير صحيح',
        'حاول مرة أخرى'
    ],
    'timeout': 'انتهى الوقت',
    'hint_used': 'تلميح: {}',
    'game_stopped': 'تم إيقاف اللعبة',
    'not_registered': 'يجب التسجيل أولاً - اكتب انضم'
}

# أوامر البوت
COMMANDS = {
    'start': ['البداية', 'ابدأ', 'start', 'البوت'],
    'help': ['مساعدة', 'help'],
    'stats': ['نقاطي', 'إحصائياتي', 'احصائياتي'],
    'leaderboard': ['الصدارة', 'المتصدرين'],
    'stop': ['إيقاف', 'stop', 'ايقاف'],
    'join': ['انضم', 'تسجيل', 'join'],
    'leave': ['انسحب', 'خروج'],
    'hint': ['لمح', 'تلميح', 'hint'],
    'answer': ['جاوب', 'الجواب', 'answer']
}

# أنواع الألعاب
GAMES = {
    'song': 'أغنية',
    'human_animal': 'لعبة',
    'chain': 'سلسلة',
    'fast_typing': 'أسرع',
    'opposite': 'ضد',
    'letters': 'تكوين',
    'differences': 'اختلاف',
    'compatibility': 'توافق',
    'mafia': 'مافيا'
}

# أوامر نصية (بدون Flex)
TEXT_COMMANDS = {
    'question': ['سؤال', 'سوال'],
    'challenge': ['تحدي', 'challenge'],
    'confession': ['اعتراف', 'confession'],
    'mention': ['منشن', 'mention']
}

# إعدادات قاعدة البيانات
DB_NAME = 'game_scores.db'

# إعدادات Rate Limiting
MAX_MESSAGES_PER_HOUR = 30
RATE_LIMIT_TIME_WINDOW = 60

# إعدادات التنظيف
CLEANUP_INTERVAL = 300
MAX_GAME_DURATION = 900

# إعدادات لعبة المافيا
MAFIA_CONFIG = {
    'min_players': 4,
    'max_players': 12,
    'discussion_time': 120,
    'voting_time': 60,
    'night_time': 30,
    'roles': {
        4: {'mafia': 1, 'citizen': 2, 'detective': 1},
        5: {'mafia': 1, 'citizen': 3, 'detective': 1},
        6: {'mafia': 2, 'citizen': 3, 'detective': 1},
        7: {'mafia': 2, 'citizen': 4, 'detective': 1},
        8: {'mafia': 2, 'citizen': 5, 'detective': 1},
        9: {'mafia': 3, 'citizen': 5, 'detective': 1},
        10: {'mafia': 3, 'citizen': 6, 'detective': 1},
        11: {'mafia': 3, 'citizen': 7, 'detective': 1},
        12: {'mafia': 4, 'citizen': 7, 'detective': 1}
    }
}
