import time
from datetime import datetime, timedelta
import logging
import re

logger = logging.getLogger(__name__)

def get_user_profile_safe(user_id, line_bot_api):
    """الحصول على اسم المستخدم بشكل آمن"""
    try:
        profile = line_bot_api.get_profile(user_id)
        return profile.display_name
    except Exception as e:
        logger.warning(f"تعذر الحصول على ملف المستخدم {user_id}: {e}")
        return f"لاعب_{user_id[-4:]}"

def normalize_text(text):
    """تطبيع النص للمقارنة (إزالة التشكيل والمسافات الزائدة)"""
    if not text:
        return ""
    
    # إزالة التشكيل العربي
    arabic_diacritics = re.compile("""
                             ّ    | # Tashdid
                             َ    | # Fatha
                             ً    | # Tanwin Fath
                             ُ    | # Damma
                             ٌ    | # Tanwin Damm
                             ِ    | # Kasra
                             ٍ    | # Tanwin Kasr
                             ْ    | # Sukun
                             ـ     # Tatwil/Kashida
                         """, re.VERBOSE)
    
    text = re.sub(arabic_diacritics, '', text)
    
    # توحيد الهمزات
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    text = text.replace('ة', 'ه')
    text = text.replace('ى', 'ي')
    
    # إزالة المسافات الزائدة وتحويل لأحرف صغيرة
    text = ' '.join(text.split()).strip().lower()
    
    return text

def check_rate_limit(user_id, user_message_count, max_messages=30, time_window=60):
    """فحص حد معدل الرسائل للمستخدم"""
    try:
        now = datetime.now()
        user_data = user_message_count[user_id]
        
        # إعادة تعيين العداد إذا مر وقت كافٍ
        if (now - user_data['reset_time']).total_seconds() > time_window:
            user_data['count'] = 0
            user_data['reset_time'] = now
        
        # زيادة العداد
        user_data['count'] += 1
        
        # فحص الحد الأقصى
        if user_data['count'] > max_messages:
            logger.warning(f"المستخدم {user_id} تجاوز حد المعدل: {user_data['count']} رسالة")
            return False
        
        return True
    except Exception as e:
        logger.error(f"خطأ في فحص حد المعدل: {e}")
        return True  # السماح بالرسالة في حالة الخطأ

def cleanup_old_games(active_games, games_lock, max_age_minutes=30):
    """تنظيف الألعاب القديمة بشكل دوري"""
    logger.info("بدأ خيط تنظيف الألعاب القديمة")
    
    while True:
        try:
            time.sleep(300)  # كل 5 دقائق
            
            now = datetime.now()
            games_to_remove = []
            
            with games_lock:
                for game_id, game_data in active_games.items():
                    created_at = game_data.get('created_at')
                    if created_at and (now - created_at).total_seconds() > (max_age_minutes * 60):
                        games_to_remove.append(game_id)
                
                for game_id in games_to_remove:
                    game_type = active_games[game_id].get('type', 'غير معروف')
                    del active_games[game_id]
                    logger.info(f"تم إزالة لعبة قديمة: {game_type} (ID: {game_id})")
            
            if games_to_remove:
                logger.info(f"تم تنظيف {len(games_to_remove)} لعبة قديمة")
        
        except Exception as e:
            logger.error(f"خطأ في تنظيف الألعاب: {e}", exc_info=True)

def format_time_elapsed(seconds):
    """تنسيق الوقت المنقضي"""
    if seconds < 60:
        return f"{int(seconds)} ثانية"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} دقيقة"
    else:
        hours = int(seconds / 3600)
        return f"{hours} ساعة"

def get_game_emoji(game_type):
    """الحصول على إيموجي مناسب لنوع اللعبة"""
    emojis = {
        'ذكاء': '🧠',
        'كلمة ولون': '🎨',
        'سلسلة': '🔗',
        'ترتيب': '🔤',
        'تكوين': '📝',
        'أسرع': '⚡',
        'لعبة': '🎯',
        'خمن': '🔍',
        'توافق': '💖',
        'رياضيات': '🔢',
        'ذاكرة': '🧩',
        'لغز': '❓',
        'ضد': '↔️',
        'إيموجي': '😊',
        'أغنية': '🎵'
    }
    return emojis.get(game_type, '🎮')

def sanitize_input(text, max_length=500):
    """تنظيف المدخلات من المحتوى الضار"""
    if not text:
        return ""
    
    # إزالة الأحرف الخاصة الضارة
    text = text.strip()
    
    # قص النص إذا كان طويلاً جداً
    if len(text) > max_length:
        text = text[:max_length]
    
    return text

def is_arabic_text(text):
    """فحص إذا كان النص يحتوي على أحرف عربية"""
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(arabic_pattern.search(text))

def calculate_accuracy(correct, total):
    """حساب نسبة الدقة"""
    if total == 0:
        return 0.0
    return round((correct / total) * 100, 1)

def get_rank_emoji(rank):
    """الحصول على إيموجي الترتيب"""
    if rank == 1:
        return "🥇"
    elif rank == 2:
        return "🥈"
    elif rank == 3:
        return "🥉"
    else:
        return f"#{rank}"

def format_number(number):
    """تنسيق الأرقام بفواصل"""
    return f"{number:,}".replace(',', '،')

def get_greeting():
    """الحصول على تحية مناسبة حسب الوقت"""
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "صباح الخير ☀️"
    elif 12 <= hour < 17:
        return "مساء الخير 🌤️"
    elif 17 <= hour < 21:
        return "مساء الخير 🌆"
    else:
        return "مساء الخير 🌙"

def validate_names(text):
    """التحقق من صحة الأسماء (للعبة التوافق)"""
    names = text.strip().split()
    
    if len(names) != 2:
        return None, "يجب إدخال اسمين فقط مفصولين بمسافة"
    
    name1, name2 = names
    
    # التحقق من طول الأسماء
    if len(name1) < 2 or len(name2) < 2:
        return None, "الأسماء يجب أن تكون أطول من حرفين"
    
    if len(name1) > 20 or len(name2) > 20:
        return None, "الأسماء يجب أن تكون أقصر من 20 حرفاً"
    
    return (name1, name2), None

def get_difficulty_level(score):
    """تحديد مستوى الصعوبة بناءً على النقاط"""
    if score < 50:
        return "مبتدئ", "🌱"
    elif score < 150:
        return "متوسط", "⭐"
    elif score < 300:
        return "متقدم", "🔥"
    elif score < 500:
        return "محترف", "💎"
    else:
        return "أسطوري", "👑"

def create_progress_bar(current, total, length=10):
    """إنشاء شريط تقدم نصي"""
    if total == 0:
        return "▱" * length
    
    filled = int((current / total) * length)
    empty = length - filled
    
    return "▰" * filled + "▱" * empty

def format_leaderboard_position(position):
    """تنسيق موضع لوحة الصدارة"""
    if position <= 3:
        return get_rank_emoji(position)
    elif position <= 10:
        return f"🏅 #{position}"
    else:
        return f"#{position}"
