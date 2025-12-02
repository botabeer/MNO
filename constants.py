COLORS = {
    'primary': '#00D9FF',
    'primary_dark': '#0099CC',
    'background': '#0A0E27',
    'background_light': '#151B3D',
    'card_bg': '#1A2145',
    'text': '#FFFFFF',
    'text_secondary': '#8B95C9',
    'success': '#00FF9D',
    'warning': '#FFB800',
    'error': '#FF4757',
    'border': '#2D3561',
    'progress_bg': '#1E2749',
    'progress_fill': '#00D9FF'
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
