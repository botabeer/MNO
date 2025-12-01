"""
Constants - ثوابت بوت الحوت
==========================================
"""

# ألوان بوت الحوت - الثيم الجديد
COLORS = {
    # الألوان الأساسية - تركواز نيون
    'primary': '#3FE0E8',        # تركواز نيون فاتح
    'primary_medium': '#22BFCB', # تركواز متوسط مضيء
    'primary_dark': '#0FA3B1',   # أزرق سياني عميق
    
    # ألوان الخلفية الداكنة
    'background': '#050A10',     # أسود مزرق داكن جدًا
    'background_medium': '#08141E', # كحلي داكن
    'card_bg': '#1A2A33',        # رمادي مزرق غامق
    
    # ألوان التوهج واللمعان
    'glow': '#6FF3FF',           # سيان مشع
    'light': '#8CEBFF',          # أزرق كهربائي فاتح
    
    # ألوان محايدة
    'border': '#2B3A42',         # رمادي بارد داكن
    'text_light': '#4A5F6B',     # رمادي مزرق متوسط
    'text_dark': '#8CEBFF',      # أزرق كهربائي فاتح (للنصوص المهمة)
    
    # ألوان إضافية
    'white': '#FFFFFF',
    'dark': '#050A10',           # أسود مزرق
    'secondary': '#0FA3B1',      # أزرق سياني عميق
    'accent': '#6FF3FF',         # سيان مشع
    'medium': '#22BFCB',         # تركواز متوسط
    
    # ألوان المراكز
    'gold': '#FFD700',           # ذهبي للمركز الأول
    'silver': '#C0C0C0',         # فضي للمركز الثاني
    'bronze': '#CD7F32',         # برونزي للمركز الثالث
    
    # ألوان الحالات
    'success': '#22BFCB',        # تركواز للنجاح
    'warning': '#3FE0E8',        # تركواز نيون للتحذير
    'info': '#6FF3FF'            # سيان مشع للمعلومات
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
