"""
ثوابت التطبيق المُحسّنة
"""

# الألوان - نظام موحد
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

# Themes للألعاب
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

# إعدادات الألعاب
GAME_SETTINGS = {
    'questions_per_game': 5,
    'time_limit_seconds': 30,
    'min_name_length': 1,
    'max_name_length': 50
}

# إعدادات قاعدة البيانات
DB_SETTINGS = {
    'name': 'game_scores.db',
    'inactivity_days': 30,
    'max_leaderboard': 20
}

# إعدادات لعبة المافيا
MAFIA_CONFIG = {
    'min_players': 4,
    'max_players': 15
}

# عدد أيام عدم النشاط قبل الحذف
INACTIVITY_DAYS = 30

# أوامر البوت
COMMANDS = {
    'start': ['بدايه', 'start', 'بداية'],
    'help': ['مساعده', 'help'],
    'games': ['العاب', 'ألعاب'],
    'register': ['تسجيل'],
    'change_name': ['تغيير'],
    'withdraw': ['انسحب'],
    'stats': ['نقاطي', 'احصائياتي'],
    'leaderboard': ['الصداره', 'الصدارة'],
    'stop': ['ايقاف', 'stop', 'إيقاف'],
    
    # الألعاب
    'song': ['اغنيه'],
    'opposite': ['ضد'],
    'chain': ['سلسله'],
    'fast': ['اسرع'],
    'human_animal': ['لعبه'],
    'letters': ['تكوين'],
    'category': ['فئه'],
    'compatibility': ['توافق'],
    'mafia': ['مافيا'],
    
    # ألعاب بدون تسجيل
    'question': ['سؤال', 'سوال'],
    'challenge': ['تحدي'],
    'confession': ['اعتراف'],
    'mention': ['منشن'],
    
    # أثناء اللعبة
    'hint': ['لمح', 'تلميح'],
    'answer': ['جاوب', 'الجواب', 'الحل']
}

# محتوى الألعاب
GAME_DATA = {
    'songs': [
        {'lyrics': 'رجعت لي أيام الماضي معاك', 'answer': 'أم كلثوم'},
        {'lyrics': 'جلست والخوف بعينيها تتأمل فنجاني', 'answer': 'عبد الحليم حافظ'},
        {'lyrics': 'تملي معاك ولو حتى بعيد عني', 'answer': 'عمرو دياب'},
        {'lyrics': 'يا بنات يا بنات', 'answer': 'نانسي عجرم'},
        {'lyrics': 'قولي أحبك كي تزيد وسامتي', 'answer': 'كاظم الساهر'},
        {'lyrics': 'أنا لحبيبي وحبيبي إلي', 'answer': 'فيروز'},
        {'lyrics': 'حبيبي يا كل الحياة اوعدني تبقى معايا', 'answer': 'تامر حسني'},
        {'lyrics': 'قلبي بيسألني عنك دخلك طمني وينك', 'answer': 'وائل كفوري'},
        {'lyrics': 'كيف أبيّن لك شعوري دون ما أحكي', 'answer': 'عايض'},
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
