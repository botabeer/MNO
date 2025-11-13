"""
ملف إعدادات Gemini AI (اختياري)
يمكن استخدامه للألعاب الذكية مثل إنسان حيوان نبات والسلسلة
"""
import os

# هل نستخدم AI في الألعاب؟
USE_AI = os.getenv("USE_AI", "false").lower() == "true"

# مفاتيح Gemini
GEMINI_KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3")
]

# تصفية المفاتيح الفارغة
GEMINI_KEYS = [key for key in GEMINI_KEYS if key]

# إعدادات Gemini
GEMINI_MODEL = "gemini-pro"
GEMINI_TEMPERATURE = 0.7
GEMINI_MAX_TOKENS = 500

def get_gemini_api_key():
    """الحصول على أول مفتاح متاح"""
    return GEMINI_KEYS[0] if GEMINI_KEYS else None

def switch_gemini_key(current_key):
    """التبديل إلى المفتاح التالي"""
    if not GEMINI_KEYS or current_key not in GEMINI_KEYS:
        return get_gemini_api_key()
    
    current_idx = GEMINI_KEYS.index(current_key)
    next_idx = (current_idx + 1) % len(GEMINI_KEYS)
    return GEMINI_KEYS[next_idx]

def is_ai_enabled():
    """هل AI مفعّل؟"""
    return USE_AI and bool(GEMINI_KEYS)
