import re
from linebot import LineBotApi
import logging

logger = logging.getLogger(__name__)

def normalize_text(text):
    """
    تطبيع النص العربي لقبول جميع أشكال الحروف
    
    Args:
        text (str): النص المراد تطبيعه
    
    Returns:
        str: النص المطبّع
    """
    if not text:
        return ""
    
    text = text.strip().lower()
    
    # توحيد الهمزات
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    text = text.replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '')
    
    # توحيد التاء المربوطة والياء
    text = text.replace('ة', 'ه').replace('ى', 'ي')
    
    # إزالة الحركات (التشكيل)
    text = re.sub(r'[\u064B-\u065F]', '', text)
    
    # إزالة المسافات الزائدة
    text = re.sub(r'\s+', '', text)
    
    return text

def get_user_profile_safe(line_bot_api, user_id):
    """
    الحصول على معلومات المستخدم بشكل آمن
    
    Args:
        line_bot_api: LINE Bot API instance
        user_id (str): معرف المستخدم
    
    Returns:
        str: اسم المستخدم أو "مستخدم" في حالة الخطأ
    """
    try:
        profile = line_bot_api.get_profile(user_id)
        return profile.display_name
    except Exception as e:
        logger.error(f"خطأ في الحصول على الملف الشخصي: {e}")
        return "مستخدم"

def format_time(seconds):
    """
    تنسيق الوقت بالثواني
    
    Args:
        seconds (float): الوقت بالثواني
    
    Returns:
        str: الوقت المنسق
    """
    if seconds < 60:
        return f"{seconds:.2f} ثانية"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes} دقيقة و {secs:.0f} ثانية"

def validate_arabic_text(text, min_length=2):
    """
    التحقق من أن النص يحتوي على أحرف عربية
    
    Args:
        text (str): النص المراد التحقق منه
        min_length (int): الحد الأدنى لطول النص
    
    Returns:
        bool: True إذا كان النص صالحاً
    """
    if not text or len(text) < min_length:
        return False
    
    # التحقق من وجود حرف عربي واحد على الأقل
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(arabic_pattern.search(text))
