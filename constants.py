"""
Constants - ثوابت المشروع
========================
جميع الثوابت والإعدادات في مكان واحد
"""

# ألوان التصميم - أبيض، أسود، رمادي
COLORS = {
    'primary': '#1a1a1a',      # أسود غامق
    'secondary': '#4a4a4a',    # رمادي غامق
    'light': '#f5f5f5',        # رمادي فاتح
    'medium': '#9a9a9a',       # رمادي متوسط
    'text_dark': '#2a2a2a',    # نص أسود
    'text_light': '#6a6a6a',   # نص رمادي
    'white': '#ffffff',        # أبيض
    'border': '#e8e8e8',       # حدود
    'background': '#f8f8f8'    # خلفية
}

# نظام النقاط
POINTS = {
    'correct_answer': 10,
    'hint_penalty': -2,
    'show_answer_penalty': -5,
    'perfect_game_bonus': 20
}

# عدد الأسئلة
QUESTIONS_PER_GAME = 5

# رسائل النجاح والفشل
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
    ]
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
    'compatibility': 'توافق'
}

# أوامر نصية فقط (بدون Flex)
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
CLEANUP_INTERVAL = 300  # 5 دقائق
MAX_GAME_DURATION = 900  # 15 دقيقة
