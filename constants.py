COLORS = {
    'primary': '#00E5FF',
    'primary_dark': '#008B9E',
    'background': '#0A1628',
    'background_light': '#0D1B2E',
    'card_bg': '#0F1F35',
    'text': '#FFFFFF',
    'white': '#FFFFFF',
    'text_secondary': '#7FA8C9',
    'text_light': '#7FA8C9',
    'text_dark': '#E0F7FF',
    'success': '#00FFD4',
    'warning': '#FFB800',
    'error': '#FF4757',
    'border': '#1A3A52',
    'progress_bg': '#0D2438',
    'progress_fill': '#00E5FF',
    'glow': '#00E5FF',
    'shadow': 'rgba(0, 229, 255, 0.3)'
}

POINTS = {
    'correct_answer': 1,
    'hint_used': 0,
    'show_answer': 0
}

QUESTIONS_PER_GAME = 5

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

INACTIVITY_DAYS = 7
