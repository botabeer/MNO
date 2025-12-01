"""
Constants - ثوابت بوت الحوت
==========================================
"""

# ألوان بوت الحوت (من الشعار)
COLORS = {
    'primary': '#00CED1',        # فيروزي/تركواز (لون الحوت)
    'primary_dark': '#008B8B',   # تركواز داكن
    'secondary': '#4B0082',      # بنفسجي عميق
    'accent': '#9370DB',         # بنفسجي فاتح
    'light': '#E0F7FA',          # فيروزي فاتح جداً
    'medium': '#48D1CC',         # فيروزي متوسط
    'dark': '#0A192F',           # أزرق داكن عميق
    'background': '#112240',     # خلفية داكنة مزرقة
    'text_light': '#8892B0',     # نص رمادي مزرق
    'text_dark': '#CCD6F6',      # نص فاتح مزرق
    'white': '#FFFFFF',
    'border': '#233554',         # حدود داكنة
    'gradient_start': '#00CED1',
    'gradient_end': '#4B0082',
    'shadow': '#000000',
    'card_bg': '#172A45',        # خلفية البطاقات
    'card_hover': '#1D3557',     # خلفية عند التمرير
    'gold': '#FFD700',           # ذهبي للمراكز الأولى
    'silver': '#C0C0C0',         # فضي للمركز الثاني
    'bronze': '#CD7F32',         # برونزي للمركز الثالث
    'success': '#10B981',        # أخضر للنجاح
    'warning': '#F59E0B',        # برتقالي للتحذير
    'info': '#3B82F6',           # أزرق للمعلومات
    'ocean_blue': '#006994',     # أزرق المحيط
    'sea_green': '#20B2AA'       # أخضر البحر
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
