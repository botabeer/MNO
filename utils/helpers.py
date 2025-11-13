"""
ملف الدوال المساعدة للبوت
"""
import os
import random
import unicodedata
import logging

logger = logging.getLogger(__name__)


def normalize_text(text):
    """
    تطبيع النص العربي وإزالة المسافات الزائدة
    
    Args:
        text: النص المراد تطبيعه
        
    Returns:
        str: النص المطبّع
    """
    if not text:
        return ""
    
    # إزالة المسافات من البداية والنهاية
    text = text.strip()
    
    # تطبيع الأحرف العربية
    text = unicodedata.normalize('NFKC', text)
    
    return text


def load_lines_from_file(filename):
    """
    قراءة الأسطر من ملف نصي
    
    Args:
        filename: مسار الملف
        
    Returns:
        list: قائمة بالأسطر
    """
    if not os.path.exists(filename):
        logger.warning(f"⚠️ الملف غير موجود: {filename}")
        return []
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            logger.info(f"✅ تم قراءة {len(lines)} سطر من {filename}")
            return lines
    except Exception as e:
        logger.error(f"❌ خطأ في قراءة الملف {filename}: {e}")
        return []


def get_random_line(filename):
    """
    الحصول على سطر عشوائي من ملف
    
    Args:
        filename: مسار الملف
        
    Returns:
        str: سطر عشوائي أو رسالة خطأ
    """
    lines = load_lines_from_file(filename)
    if not lines:
        return "لا توجد بيانات متاحة"
    
    return random.choice(lines)


def get_user_profile_safe(line_bot_api, user_id):
    """
    الحصول على معلومات المستخدم بشكل آمن
    
    Args:
        line_bot_api: واجهة LINE Bot API
        user_id: معرف المستخدم
        
    Returns:
        Profile object أو None
    """
    try:
        profile = line_bot_api.get_profile(user_id)
        return profile
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على معلومات المستخدم {user_id}: {e}")
        return None


def format_time_remaining(seconds):
    """
    تنسيق الوقت المتبقي
    
    Args:
        seconds: عدد الثواني
        
    Returns:
        str: وقت منسق
    """
    if seconds < 60:
        return f"{seconds} ثانية"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} دقيقة"
    else:
        hours = seconds // 3600
        return f"{hours} ساعة"


def validate_arabic_text(text, min_length=1, max_length=100):
    """
    التحقق من صحة النص العربي
    
    Args:
        text: النص المراد التحقق منه
        min_length: الحد الأدنى للطول
        max_length: الحد الأقصى للطول
        
    Returns:
        tuple: (bool: صحيح/خطأ, str: رسالة الخطأ إن وجدت)
    """
    if not text:
        return False, "النص فارغ"
    
    text = text.strip()
    
    if len(text) < min_length:
        return False, f"النص قصير جداً (الحد الأدنى {min_length} حرف)"
    
    if len(text) > max_length:
        return False, f"النص طويل جداً (الحد الأقصى {max_length} حرف)"
    
    return True, ""


def check_rate_limit(user_id, user_message_count, max_messages=30, time_window=3600):
    """
    التحقق من حد الرسائل للمستخدم
    
    Args:
        user_id: معرف المستخدم
        user_message_count: قاموس عدد الرسائل
        max_messages: الحد الأقصى للرسائل
        time_window: نافذة الوقت بالثواني
        
    Returns:
        bool: True إذا كان ضمن الحد، False إذا تجاوز
    """
    from datetime import datetime, timedelta
    
    current_time = datetime.now()
    
    if user_id not in user_message_count:
        user_message_count[user_id] = {
            "count": 1,
            "reset_time": current_time + timedelta(seconds=time_window)
        }
        return True
    
    user_data = user_message_count[user_id]
    
    # إعادة تعيين العداد إذا انتهت النافذة الزمنية
    if current_time >= user_data["reset_time"]:
        user_data["count"] = 1
        user_data["reset_time"] = current_time + timedelta(seconds=time_window)
        return True
    
    # زيادة العداد
    user_data["count"] += 1
    
    # التحقق من تجاوز الحد
    if user_data["count"] > max_messages:
        return False
    
    return True


def cleanup_old_games(active_games, games_lock, max_age=3600):
    """
    تنظيف الألعاب القديمة
    
    Args:
        active_games: قاموس الألعاب النشطة
        games_lock: قفل للحماية من التزامن
        max_age: العمر الأقصى بالثواني (افتراضي: ساعة)
    """
    import time
    from datetime import datetime
    
    while True:
        try:
            time.sleep(1800)  # 30 دقيقة
            current_time = datetime.now()
            
            with games_lock:
                expired_games = []
                
                for game_id, game_data in active_games.items():
                    age = (current_time - game_data["created_at"]).seconds
                    if age > max_age:
                        expired_games.append(game_id)
                
                for game_id in expired_games:
                    del active_games[game_id]
                    logger.info(f"🧹 تم حذف اللعبة المنتهية: {game_id}")
                
                if expired_games:
                    logger.info(f"🧹 تم تنظيف {len(expired_games)} لعبة منتهية")
                    
        except Exception as e:
            logger.error(f"❌ خطأ في عملية التنظيف: {e}")


def create_game_id(user_id, game_type):
    """
    إنشاء معرف فريد للعبة
    
    Args:
        user_id: معرف المستخدم
        game_type: نوع اللعبة
        
    Returns:
        str: معرف فريد
    """
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{game_type}_{user_id}_{timestamp}"


def get_random_emoji(category="positive"):
    """
    الحصول على إيموجي عشوائي
    
    Args:
        category: فئة الإيموجي (positive, negative, neutral, game)
        
    Returns:
        str: إيموجي عشوائي
    """
    emojis = {
        "positive": ["🎉", "✨", "🌟", "💫", "🎊", "🏆", "👏", "💪", "🔥", "⭐"],
        "negative": ["😔", "💔", "😢", "😞", "😕", "😟", "😥", "😰", "😓"],
        "neutral": ["🤔", "🧐", "🤨", "😐", "😑", "🙂", "😊", "☺️"],
        "game": ["🎮", "🎯", "🎲", "🃏", "🎰", "🎪", "🎭", "🎨", "🎬", "🎤"]
    }
    
    return random.choice(emojis.get(category, emojis["neutral"]))


def truncate_text(text, max_length=100, suffix="..."):
    """
    اختصار النص الطويل
    
    Args:
        text: النص
        max_length: الطول الأقصى
        suffix: اللاحقة (...)
        
    Returns:
        str: النص المختصر
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].strip() + suffix
