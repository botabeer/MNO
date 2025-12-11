"""
ثوابت التطبيق
"""

# نظام الألوان
COLORS = {
    'primary': '#6B9BD1',
    'primary_dark': '#4A7BA7',
    'background': '#F5F7FA',
    'background_light': '#FFFFFF',
    'card_bg': '#FFFFFF',
    'text': '#2C3E50',
    'white': '#FFFFFF',
    'text_secondary': '#7F8C8D',
    'text_light': '#95A5A6',
    'text_dark': '#2C3E50',
    'success': '#52C5B6',
    'warning': '#F39C6B',
    'error': '#E17B7B',
    'border': '#E8ECEF',
    'progress_bg': '#E8ECEF',
    'progress_fill': '#6B9BD1',
    'glow': '#6B9BD1',
    'shadow': 'rgba(107, 155, 209, 0.15)'
}

# نظام النقاط
POINTS = {
    'correct_answer': 1,
    'hint_used': 0,
    'show_answer': 0
}

# عدد الأسئلة لكل لعبة
QUESTIONS_PER_GAME = 5

# إعدادات لعبة المافيا
MAFIA_CONFIG = {
    'min_players': 4,
    'max_players': 20,
    'roles': {
        'mafia': 1,
        'detective': 1,
        'doctor': 1,
        'citizen': 'remaining'
    },
    'phases': ['registration', 'night', 'day', 'voting', 'ended'],
    'night_duration': 60,
    'day_duration': 120,
    'voting_duration': 60
}

# عدد أيام عدم النشاط قبل الحذف
INACTIVITY_DAYS = 30

# حدود التطبيق
LIMITS = {
    'max_name_length': 50,
    'min_name_length': 1,
    'max_leaderboard_entries': 20,
    'max_game_history': 100
}

# الأوامر المتاحة
COMMANDS = {
    'basic': ['بدايه', 'start', 'ابدا', 'بداية', 'مساعده', 'help', 'مساعدة', 'العاب'],
    'account': ['تسجيل', 'تغيير', 'انسحب', 'نقاطي', 'احصائياتي'],
    'leaderboard': ['الصداره', 'المتصدرين', 'الصدارة'],
    'game_control': ['ايقاف', 'stop', 'إيقاف'],
    'no_registration': ['سؤال', 'سوال', 'تحدي', 'اعتراف', 'منشن', 'توافق'],
    'games': ['اغنيه', 'لعبه', 'سلسله', 'اسرع', 'ضد', 'تكوين', 'فئه', 'مافيا']
}

# رسائل النظام
MESSAGES = {
    'welcome': 'مرحباً بك في بوت الألعاب',
    'registration_required': 'يجب التسجيل أولاً للعب هذه اللعبة\nاكتب: تسجيل',
    'invalid_name': 'الاسم غير صالح\nيرجى إدخال اسم صحيح (1-50 حرف)',
    'game_stopped': 'تم إيقاف اللعبة',
    'no_active_game': 'لا توجد لعبة نشطة',
    'error': 'حدث خطأ، الرجاء المحاولة مرة أخرى'
}
