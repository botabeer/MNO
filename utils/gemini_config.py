"""
Gemini AI Configuration
إعدادات وتكوين Gemini AI
"""

import os
import logging

logger = logging.getLogger(__name__)

# إعدادات Gemini AI (دعم متعدد المفاتيح)
GEMINI_API_KEYS = [
    os.getenv('GEMINI_API_KEY_1', ''),
    os.getenv('GEMINI_API_KEY_2', ''),
    os.getenv('GEMINI_API_KEY_3', '')
]

# تنقية المفاتيح الفارغة
GEMINI_API_KEYS = [key.strip() for key in GEMINI_API_KEYS if key and key.strip()]

# المتغيرات العامة
current_gemini_key_index = 0
USE_AI = bool(GEMINI_API_KEYS)

# طباعة معلومات التكوين
logger.info(f"📊 عدد مفاتيح Gemini المتاحة: {len(GEMINI_API_KEYS)}")
logger.info(f"🤖 استخدام AI: {'نعم' if USE_AI else 'لا'}")

def get_gemini_api_key():
    """
    الحصول على مفتاح Gemini API الحالي
    
    Returns:
        str or None: المفتاح الحالي أو None إذا لم يكن متوفراً
    """
    global current_gemini_key_index
    if GEMINI_API_KEYS:
        return GEMINI_API_KEYS[current_gemini_key_index]
    logger.warning("⚠️ لا توجد مفاتيح Gemini API متاحة")
    return None

def switch_gemini_key():
    """
    التبديل إلى المفتاح التالي في حالة نفاد الحصة
    
    Returns:
        bool: True إذا تم التبديل بنجاح، False إذا لم يكن هناك مفاتيح أخرى
    """
    global current_gemini_key_index
    
    if len(GEMINI_API_KEYS) > 1:
        current_gemini_key_index = (current_gemini_key_index + 1) % len(GEMINI_API_KEYS)
        logger.info(f"🔄 تم التبديل إلى مفتاح Gemini رقم: {current_gemini_key_index + 1}")
        return True
    
    logger.warning("⚠️ لا توجد مفاتيح إضافية للتبديل")
    return False

def reset_gemini_key():
    """إعادة تعيين المفتاح إلى الأول"""
    global current_gemini_key_index
    current_gemini_key_index = 0
    logger.info("🔄 تم إعادة تعيين مفتاح Gemini إلى الأول")
