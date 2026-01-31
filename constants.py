"""
ثوابت التطبيق المحسنة
"""

# الالوان - نظام موحد
COLORS = {
    'primary': '#6B9BD1',
    'success': '#52C5B6',
    'warning': '#F39C6B',
    'error': '#E17B7B',
    'white': '#FFFFFF',
    'text_dark': '#2C3E50',
    'text_light': '#95A5A6',
    'border': '#E8ECEF',
    'card_bg': '#FFFFFF'
}

# Themes للالعاب
THEMES = {
    'light': COLORS,
    'dark': {
        'primary': '#6B9BD1',
        'success': '#52C5B6',
        'warning': '#F39C6B',
        'error': '#E17B7B',
        'white': '#FFFFFF',
        'text_dark': '#FFFFFF',
        'text_light': '#B0B0B0',
        'border': '#333333',
        'card_bg': '#1E1E1E'
    }
}

# نظام النقاط
POINTS = {
    'correct': 1,
    'hint': 0,
    'show_answer': 0
}

# اعدادات الالعاب
GAME_SETTINGS = {
    'questions_per_game': 5,
    'time_limit_seconds': 30,
    'min_name_length': 1,
    'max_name_length': 50
}

# اعدادات قاعدة البيانات
DB_SETTINGS = {
    'name': 'game_scores.db',
    'inactivity_days': 30,
    'max_leaderboard': 20
}

# اعدادات لعبة المافيا
MAFIA_CONFIG = {
    'min_players': 4,
    'max_players': 15
}

# عدد ايام عدم النشاط قبل الحذف
INACTIVITY_DAYS = 30

# اوامر البوت
COMMANDS = {
    'start': ['بدايه', 'start', 'بداية'],
    'help': ['مساعده', 'help'],
    'games': ['العاب', 'العاب'],
    'register': ['تسجيل'],
    'change_name': ['تغيير'],
    'withdraw': ['انسحب'],
    'stats': ['نقاطي', 'احصائياتي'],
    'leaderboard': ['الصداره', 'الصدارة'],
    'stop': ['ايقاف', 'stop', 'ايقاف'],
    
    # العاب نصية
    'question': ['سؤال', 'سوال'],
    'challenge': ['تحدي'],
    'confession': ['اعتراف'],
    'mention': ['منشن'],
    
    # اثناء اللعبة
    'hint': ['لمح', 'تلميح'],
    'answer': ['جاوب', 'الجواب', 'الحل']
}

# خريطة الالعاب - ربط الاوامر بالكلاسات
GAME_MAP = {
    'اغنيه': 'SongGame',
    'ضد': 'OppositeGame',
    'سلسله': 'ChainWordsGame',
    'اسرع': 'FastTypingGame',
    'لعبه': 'HumanAnimalPlantGame',
    'تكوين': 'LettersWordsGame',
    'فئه': 'CategoryLetterGame',
    'توافق': 'CompatibilityGame',
    'مافيا': 'MafiaGame',
    'ذكاء': 'IqGame',
    'رياضيات': 'MathGame',
    'ترتيب': 'ScrambleGame'
}

# محتوى الالعاب
GAME_DATA = {
    'songs': [
        {'lyrics': 'رجعت لي ايام الماضي معاك', 'answer': 'ام كلثوم'},
        {'lyrics': 'جلست والخوف بعينيها تتامل فنجاني', 'answer': 'عبد الحليم حافظ'},
        {'lyrics': 'تملي معاك ولو حتى بعيد عني', 'answer': 'عمرو دياب'},
        {'lyrics': 'يا بنات يا بنات', 'answer': 'نانسي عجرم'},
        {'lyrics': 'قولي احبك كي تزيد وسامتي', 'answer': 'كاظم الساهر'},
        {'lyrics': 'انا لحبيبي وحبيبي الي', 'answer': 'فيروز'},
        {'lyrics': 'حبيبي يا كل الحياة اوعدني تبقى معايا', 'answer': 'تامر حسني'},
        {'lyrics': 'قلبي بيسالني عنك دخلك طمني وينك', 'answer': 'وائل كفوري'},
        {'lyrics': 'كيف ابين لك شعوري دون ما احكي', 'answer': 'عايض'},
        {'lyrics': 'اسخر لك غلا وتشوفني مقصر', 'answer': 'عايض'},
    ],
    
    'opposites': [
        {'word': 'كبير', 'answer': 'صغير'},
        {'word': 'طويل', 'answer': 'قصير'},
        {'word': 'سريع', 'answer': 'بطيء'},
        {'word': 'ساخن', 'answer': 'بارد'},
        {'word': 'نظيف', 'answer': 'وسخ'},
        {'word': 'قوي', 'answer': 'ضعيف'},
        {'word': 'سهل', 'answer': 'صعب'},
        {'word': 'جميل', 'answer': 'قبيح'},
        {'word': 'غني', 'answer': 'فقير'},
        {'word': 'فوق', 'answer': 'تحت'},
    ],
    
    'chain_words': [
        'قلم', 'كتاب', 'مدرسة', 'باب', 'نافذة', 
        'طاولة', 'كرسي', 'حديقة', 'شجرة', 'زهرة'
    ],
    
    'fast_typing': [
        'سبحان الله', 'الحمد لله', 'لا اله الا الله', 
        'الله اكبر', 'استغفر الله', 'لا حول ولا قوه الا بالله'
    ],
    
    'letters': ['ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر'],
    
    'categories': [
        {'category': 'المطبخ', 'letter': 'ق', 'answers': ['قدر', 'قلايه', 'قهوه']},
        {'category': 'حيوان', 'letter': 'ب', 'answers': ['بطه', 'بقره', 'ببغاء']},
        {'category': 'فاكهه', 'letter': 'ت', 'answers': ['تفاح', 'توت', 'تمر']},
    ],
    
    'letter_words': [
        {'letters': 'ق ل م ع ر ك', 'answers': ['قلم', 'علم', 'عمر', 'رقم', 'ملك']},
        {'letters': 'ك ت ا ب ر ل', 'answers': ['كتاب', 'باب', 'كتب', 'تراب']},
    ]
}
