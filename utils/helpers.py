"""
Helpers Module - وظائف مساعدة
==============================
مجموعة من الوظائف المساعدة للبوت
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

# تخزين معدل الرسائل للمستخدمين
user_message_count: Dict[str, Dict] = defaultdict(lambda: {
    'count': 0,
    'reset_time': datetime.now()
})

def get_user_profile_safe(line_bot_api, user_id: str) -> str:
    """
    الحصول على اسم المستخدم بشكل آمن
    
    Args:
        line_bot_api: واجهة LINE Bot API
        user_id: معرف المستخدم
        
    Returns:
        اسم المستخدم أو "مستخدم" في حالة الفشل
    """
    try:
        profile = line_bot_api.get_profile(user_id)
        return profile.display_name
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على الملف الشخصي لـ {user_id}: {e}")
        return "مستخدم"

def check_rate_limit(
    user_id: str,
    max_messages: int = 20,
    time_window: int = 60
) -> bool:
    """
    التحقق من معدل الرسائل لمنع الإزعاج
    
    Args:
        user_id: معرف المستخدم
        max_messages: أقصى عدد رسائل مسموح
        time_window: نافذة الوقت بالثواني
        
    Returns:
        True إذا كان المستخدم ضمن الحد المسموح
    """
    now = datetime.now()
    user_data = user_message_count[user_id]
    
    # إعادة تعيين العداد إذا انتهت النافذة الزمنية
    if now - user_data['reset_time'] > timedelta(seconds=time_window):
        user_data['count'] = 0
        user_data['reset_time'] = now
    
    # التحقق من الحد الأقصى
    if user_data['count'] >= max_messages:
        logger.warning(f"⚠️ {user_id} تجاوز حد الرسائل")
        return False
    
    user_data['count'] += 1
    return True

def sanitize_text(text: str) -> str:
    """
    تنظيف النص من المحارف الخاصة
    
    Args:
        text: النص المراد تنظيفه
        
    Returns:
        النص المنظف
    """
    if not text:
        return ""
    
    # إزالة المسافات الزائدة
    text = ' '.join(text.split())
    
    # إزالة الرموز الخطرة
    text = re.sub(r'[<>\"\'`]', '', text)
    
    return text.strip()

def format_number(number: int) -> str:
    """
    تنسيق الأرقام بفواصل
    
    Args:
        number: الرقم المراد تنسيقه
        
    Returns:
        الرقم المنسق (مثال: 1,000)
    """
    return "{:,}".format(number)

def get_time_greeting() -> str:
    """
    الحصول على تحية حسب الوقت
    
    Returns:
        التحية المناسبة
    """
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "صباح الخير ☀️"
    elif 12 <= hour < 17:
        return "مساء الخير 🌤️"
    elif 17 <= hour < 21:
        return "مساء الخير 🌆"
    else:
        return "مساء الخير 🌙"

def calculate_win_rate(wins: int, games_played: int) -> float:
    """
    حساب نسبة الفوز
    
    Args:
        wins: عدد الانتصارات
        games_played: عدد الألعاب
        
    Returns:
        نسبة الفوز (0-100)
    """
    if games_played == 0:
        return 0.0
    return round((wins / games_played) * 100, 1)

def get_level_info(total_points: int) -> Dict[str, any]:
    """
    الحصول على معلومات المستوى بناءً على النقاط
    
    Args:
        total_points: إجمالي النقاط
        
    Returns:
        معلومات المستوى (level, title, emoji, next_level_points)
    """
    levels = [
        (0, "مبتدئ", "🌱", 100),
        (100, "هاوي", "🌿", 250),
        (250, "محترف", "⭐", 500),
        (500, "خبير", "💎", 1000),
        (1000, "أسطورة", "👑", 2000),
        (2000, "بطل", "🏆", 5000),
        (5000, "إمبراطور", "⚡", 10000),
        (10000, "إله", "🌟", float('inf'))
    ]
    
    for i, (points, title, emoji, next_points) in enumerate(levels):
        if total_points < next_points:
            return {
                'level': i + 1,
                'title': title,
                'emoji': emoji,
                'points_needed': next_points - total_points,
                'next_level_points': next_points
            }
    
    # المستوى الأقصى
    return {
        'level': len(levels),
        'title': levels[-1][1],
        'emoji': levels[-1][2],
        'points_needed': 0,
        'next_level_points': float('inf')
    }

def format_duration(seconds: int) -> str:
    """
    تنسيق المدة الزمنية
    
    Args:
        seconds: المدة بالثواني
        
    Returns:
        المدة المنسقة (مثال: 2د 30ث)
    """
    if seconds < 60:
        return f"{seconds}ث"
    
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        if remaining_seconds > 0:
            return f"{minutes}د {remaining_seconds}ث"
        return f"{minutes}د"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if remaining_minutes > 0:
        return f"{hours}س {remaining_minutes}د"
    return f"{hours}س"

def get_achievement_emoji(achievement_type: str) -> str:
    """
    الحصول على إيموجي الإنجاز
    
    Args:
        achievement_type: نوع الإنجاز
        
    Returns:
        الإيموجي المناسب
    """
    achievements = {
        'first_win': '🎯',
        'win_streak_5': '🔥',
        'win_streak_10': '⚡',
        'games_played_10': '🎮',
        'games_played_50': '🏅',
        'games_played_100': '🏆',
        'points_1000': '💎',
        'points_5000': '👑',
        'perfect_score': '⭐',
        'speed_master': '⏱️',
        'comeback_king': '🦸'
    }
    return achievements.get(achievement_type, '🎖️')

def validate_player_name(name: str) -> bool:
    """
    التحقق من صحة اسم اللاعب
    
    Args:
        name: اسم اللاعب
        
    Returns:
        True إذا كان الاسم صحيحاً
    """
    if not name or len(name.strip()) == 0:
        return False
    
    if len(name) > 50:
        return False
    
    # التحقق من عدم وجود محارف خطرة
    dangerous_chars = ['<', '>', '"', "'", '`', '\\', '/', ';']
    if any(char in name for char in dangerous_chars):
        return False
    
    return True

def parse_compatibility_names(text: str) -> Optional[tuple]:
    """
    تحليل أسماء لعبة التوافق
    
    Args:
        text: النص المدخل
        
    Returns:
        (name1, name2) أو None
    """
    parts = text.strip().split()
    
    if len(parts) < 2:
        return None
    
    # إذا كان هناك أكثر من اسمين، نأخذ الأول والثاني
    name1 = parts[0].strip()
    name2 = parts[1].strip()
    
    if not validate_player_name(name1) or not validate_player_name(name2):
        return None
    
    return (name1, name2)

def get_random_emoji() -> str:
    """
    الحصول على إيموجي عشوائي
    
    Returns:
        إيموجي عشوائي
    """
    import random
    emojis = ['😊', '😎', '🎮', '🎯', '⭐', '💎', '🏆', '👑', '🔥', '⚡']
    return random.choice(emojis)

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    اختصار النص إذا كان طويلاً
    
    Args:
        text: النص
        max_length: الطول الأقصى
        
    Returns:
        النص المختصر
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def is_arabic_text(text: str) -> bool:
    """
    التحقق من أن النص عربي
    
    Args:
        text: النص المراد فحصه
        
    Returns:
        True إذا كان النص يحتوي على أحرف عربية
    """
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(arabic_pattern.search(text))
