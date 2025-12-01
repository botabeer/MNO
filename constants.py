"""
Constants - ثوابت المشروع بألوان جديدة
========================================
"""

# ألوان من الصور (أزرق سماوي وذهبي)
COLORS = {
    'primary': '#00D4FF',        # الأزرق السماوي الساطع
    'primary_dark': '#0099CC',   # أزرق داكن
    'secondary': '#1A1A2E',      # أسود مزرق داكن
    'accent': '#16213E',         # أزرق داكن جداً
    'light': '#E3F8FF',          # أزرق فاتح شفاف
    'medium': '#66D9FF',         # أزرق متوسط
    'dark': '#0A0E27',           # أسود للخلفيات
    'background': '#0F1419',     # خلفية داكنة
    'text_light': '#B3E5FC',     # نص أزرق فاتح
    'text_dark': '#FFFFFF',      # نص أبيض (تغيير من الأزرق الداكن)
    'white': '#FFFFFF',
    'border': '#4DD0E1',
    'gradient_start': '#00D4FF',
    'gradient_end': '#0066CC',
    'shadow': '#000000',
    'card_bg': '#1E2A35',        # خلفية البطاقات (داكنة)
    'gold': '#FFD700',           # ذهبي للمراكز الأولى
    'silver': '#C0C0C0',         # فضي للمركز الثاني
    'bronze': '#CD7F32'          # برونزي للمركز الثالث
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
    'start': ['بداية', 'start', 'البوت', 'ابدأ'],  # إضافة ابدأ
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

# أوامر نصية (بدون Flex) - يجب أن تبقى نصية
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
