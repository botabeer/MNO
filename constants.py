"""
Constants - ثوابت المشروع بألوان البوت الجديدة
===================================
"""

# ألوان التصميم من صور البوت (الأزرق المميز)
COLORS = {
    'primary': '#00D9FF',      # الأزرق الفاتح المميز من اللوجو
    'primary_dark': '#00B8D4',  # أزرق داكن قليلاً
    'secondary': '#1E3A5F',    # أزرق داكن للعناوين
    'dark_bg': '#0A1929',      # خلفية داكنة
    'light': '#E3F2FD',        # أزرق فاتح جداً
    'medium': '#64B5F6',       # أزرق متوسط
    'text_dark': '#1A237E',    # نص داكن
    'text_light': '#90CAF9',   # نص فاتح
    'white': '#FFFFFF',        # أبيض
    'border': '#42A5F5',       # حدود زرقاء
    'background': '#E1F5FE',   # خلفية فاتحة
    'success': '#00E676',      # أخضر للنجاح
    'error': '#FF5252',        # أحمر للخطأ
    'gradient_start': '#00D9FF',
    'gradient_end': '#1E3A5F'
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

# أوامر البوت - تحديث "ابدأ" ليصبح "بداية"
COMMANDS = {
    'start': ['بداية', 'start', 'البوت'],
    'help': ['مساعدة', 'help', 'المساعدة'],
    'stats': ['نقاطي', 'إحصائياتي', 'احصائياتي', 'احصائيات'],
    'leaderboard': ['الصدارة', 'المتصدرين', 'المتصدرون'],
    'stop': ['إيقاف', 'stop', 'ايقاف', 'توقف'],
    'join': ['انضم', 'تسجيل', 'join', 'انظم'],
    'leave': ['انسحب', 'خروج', 'leave', 'الغاء'],
    'hint': ['لمح', 'تلميح', 'hint'],
    'answer': ['جاوب', 'الجواب', 'answer', 'الحل']
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

# أوامر نصية (بدون Flex) - فقط النصوص
TEXT_COMMANDS = {
    'question': ['سؤال', 'سوال'],
    'challenge': ['تحدي', 'challenge'],
    'confession': ['اعتراف', 'confession', 'اعترف'],
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

# أوامر المافيا
MAFIA_COMMANDS = {
    'join': ['انضم مافيا', 'انضم للمافيا'],
    'start': ['بدء مافيا', 'ابدأ مافيا', 'بداية مافيا'],
    'kill': ['قتل'],
    'investigate': ['تحقق'],
    'protect': ['احم', 'حماية'],
    'vote': ['صوت'],
    'status': ['حالة', 'الحالة', 'وضع'],
    'alive': ['الأحياء', 'احياء']
}

# رسائل المافيا
MAFIA_MESSAGES = {
    'registration_open': 'لعبة المافيا - فتح التسجيل',
    'player_joined': '{} انضم للعبة ({})',
    'game_full': 'اللعبة ممتلئة',
    'already_joined': 'أنت مسجل بالفعل',
    'game_started': 'اللعبة بدأت - جاري توزيع الأدوار',
    'not_enough_players': 'عدد اللاعبين غير كافٍ (الحد الأدنى: {})',
    'night_begins': 'بدأت الليلة {} - المافيا والمحقق والدكتور يرسلون أوامرهم للبوت في الخاص',
    'day_begins': 'بدأ النهار {} - وقت النقاش',
    'voting_begins': 'وقت التصويت - صوتوا لطرد شخص',
    'victim_found': 'تم العثور على {} ميتاً',
    'no_victim': 'لم يحدث شيء في الليل',
    'player_executed': 'تم إعدام {} - الدور: {}',
    'mafia_wins': 'المافيا انتصرت',
    'citizens_win': 'المواطنون انتصروا',
    'vote_registered': 'تم تسجيل تصويتك',
    'action_registered': 'تم تسجيل إجراءك',
    'not_night': 'ليس وقت الليل',
    'not_voting': 'ليس وقت التصويت',
    'player_not_found': 'لم يتم العثور على اللاعب',
    'not_in_game': 'لست في اللعبة'
}

# أوصاف الأدوار
ROLE_DESCRIPTIONS = {
    'mafia': {
        'name': 'المافيا',
        'description': 'أنت من المافيا - مهمتك القضاء على المواطنين',
        'action': 'كل ليلة اختر ضحية بإرسال: قتل @الاسم',
        'win_condition': 'تنتصر عندما يصبح عدد المافيا مساوياً أو أكبر من المواطنين'
    },
    'detective': {
        'name': 'المحقق',
        'description': 'أنت المحقق - مهمتك اكتشاف المافيا',
        'action': 'كل ليلة تحقق من شخص بإرسال: تحقق @الاسم',
        'win_condition': 'تنتصر عندما يتم القضاء على جميع المافيا'
    },
    'doctor': {
        'name': 'الدكتور',
        'description': 'أنت الدكتور - مهمتك حماية المواطنين',
        'action': 'كل ليلة احم شخصاً بإرسال: احم @الاسم',
        'win_condition': 'تنتصر عندما يتم القضاء على جميع المافيا'
    },
    'citizen': {
        'name': 'مواطن',
        'description': 'أنت مواطن - مهمتك العثور على المافيا',
        'action': 'شارك في النقاش والتصويت لطرد المشتبه بهم',
        'win_condition': 'تنتصر عندما يتم القضاء على جميع المافيا'
    }
}

# مراحل لعبة المافيا
MAFIA_PHASES = {
    'registration': 'التسجيل',
    'night': 'الليل',
    'discussion': 'النقاش',
    'voting': 'التصويت',
    'ended': 'انتهت'
}
