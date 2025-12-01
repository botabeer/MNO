"""
Constants - ثوابت بوت الحوت
==========================================
"""

# ألوان الثيم حسب واجهة الصورة
COLORS = {
    # اللون الأساسي (زر العنوان السماوي)
    'primary': '#18D0F0',          # سماوي فاقع
    'primary_medium': '#25BFD9',   # سماوي متوسط
    'primary_dark': '#149FB3',     # سماوي داكن

    # الخلفيات
    'background': '#1E2A36',       # كحلي داكن (خلفية عامة)
    'background_medium': '#243241',# أزرق رمادي داكن
    'card_bg': '#243140',          # خلفية الكرت

    # ألوان التوهج
    'glow': '#5EE5F6',             # سماوي متوهج
    'light': '#7DEEFF',            # سماوي فاتح

    # الحدود والنصوص
    'border': '#2F3E4E',           # حد أزرق رمادي
    'text_light': '#B8C3CC',       # رمادي فاتح للنص
    'text_dark': '#FFFFFF',       # أبيض صريح

    # أزرار الإجابة (الرمادي الفاتح)
    'button_light': '#E6EAF0',     
    'button_text': '#1E2A36',

    # ألوان أساسية إضافية
    'white': '#FFFFFF',
    'dark': '#1E2A36',
    'secondary': '#243140',
    'accent': '#18D0F0',
    'medium': '#25BFD9',

    # ألوان المراكز
    'gold': '#FFD700',
    'silver': '#C0C0C0',
    'bronze': '#CD7F32',

    # ألوان الحالات
    'success': '#25BFD9',
    'warning': '#18D0F0',
    'info': '#5EE5F6'
}

# نظام النقاط
POINTS = {
    'correct_answer': 10,
    'hint_penalty': -2,
    'show_answer_penalty': -5,
    'perfect_game_bonus': 20,
    'mafia_win': 15,
    'citizen_win': 10,
    'detective_win': 12,
    'doctor_win': 12
}

# عدد الأسئلة
QUESTIONS_PER_GAME = 5

# رسائل النجاح والفشل
MESSAGES = {
    'correct': ['إجابة صحيحة', 'ممتاز', 'صحيح', 'رائع', 'أحسنت'],
    'wrong': ['إجابة خاطئة', 'للأسف خطأ', 'غير صحيح', 'حاول مرة أخرى'],
    'timeout': 'انتهى الوقت',
    'hint_used': 'تلميح: {}',
    'game_stopped': 'تم إيقاف اللعبة',
    'not_registered': 'يجب التسجيل أولاً'
}

# أوامر البوت
COMMANDS = {
    'start': ['بداية', 'start', 'البوت', 'ابدأ'],
    'help': ['مساعدة', 'help', 'المساعدة'],
    'stats': ['نقاطي', 'إحصائياتي'],
    'leaderboard': ['الصدارة', 'المتصدرين'],
    'stop': ['إيقاف', 'stop'],
    'join': ['انضم', 'تسجيل'],
    'leave': ['انسحب', 'خروج'],
    'hint': ['لمح', 'تلميح'],
    'answer': ['جاوب', 'الجواب']
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
    'challenge': ['تحدي'],
    'confession': ['اعتراف'],
    'mention': ['منشن']
}

# إعدادات قاعدة البيانات
DB_NAME = 'game_scores.db'

# إعدادات المافيا
MAFIA_CONFIG = {
    'min_players': 4,
    'max_players': 12,
    'discussion_time': 120,
    'voting_time': 60,
    'night_time': 90,
    'roles': {
        4: {'mafia': 1, 'detective': 1, 'doctor': 0, 'citizen': 2},
        5: {'mafia': 1, 'detective': 1, 'doctor': 1, 'citizen': 2},
        6: {'mafia': 2, 'detective': 1, 'doctor': 1, 'citizen': 2},
        7: {'mafia': 2, 'detective': 1, 'doctor': 1, 'citizen': 3},
        8: {'mafia': 2, 'detective': 1, 'doctor': 1, 'citizen': 4},
        9: {'mafia': 3, 'detective': 1, 'doctor': 1, 'citizen': 4},
        10: {'mafia': 3, 'detective': 1, 'doctor': 1, 'citizen': 5},
        11: {'mafia': 3, 'detective': 1, 'doctor': 1, 'citizen': 6},
        12: {'mafia': 4, 'detective': 1, 'doctor': 1, 'citizen': 6}
    }
}
