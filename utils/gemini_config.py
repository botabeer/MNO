"""
Gemini AI Configuration - إعدادات Gemini AI
===========================================
إدارة مفاتيح API والتبديل التلقائي
"""

import os
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

class GeminiConfig:
    """
    إدارة إعدادات Gemini AI
    """
    
    def __init__(self):
        """تهيئة الإعدادات"""
        self.api_keys: List[str] = self._load_api_keys()
        self.current_key_index: int = 0
        self.is_available: bool = len(self.api_keys) > 0
        
        logger.info(f"✅ تم تحميل {len(self.api_keys)} مفتاح Gemini API")
        
        if not self.is_available:
            logger.warning("⚠️ لا توجد مفاتيح Gemini API متاحة")
    
    def _load_api_keys(self) -> List[str]:
        """
        تحميل مفاتيح API من متغيرات البيئة
        
        Returns:
            قائمة بالمفاتيح الصالحة
        """
        keys = []
        
        # محاولة تحميل حتى 5 مفاتيح
        for i in range(1, 6):
            key = os.getenv(f'GEMINI_API_KEY_{i}', '').strip()
            if key and key != '' and len(key) > 20:
                keys.append(key)
                logger.info(f"✅ تم تحميل مفتاح Gemini {i}")
        
        # محاولة تحميل المفتاح الافتراضي
        default_key = os.getenv('GEMINI_API_KEY', '').strip()
        if default_key and default_key != '' and len(default_key) > 20:
            if default_key not in keys:
                keys.append(default_key)
                logger.info("✅ تم تحميل المفتاح الافتراضي")
        
        return keys
    
    def get_current_key(self) -> Optional[str]:
        """
        الحصول على المفتاح الحالي
        
        Returns:
            مفتاح API الحالي أو None
        """
        if not self.is_available:
            return None
        
        return self.api_keys[self.current_key_index]
    
    def switch_key(self) -> bool:
        """
        التبديل إلى المفتاح التالي
        
        Returns:
            True إذا تم التبديل بنجاح
        """
        if len(self.api_keys) <= 1:
            logger.warning("⚠️ لا يوجد مفاتيح إضافية للتبديل")
            return False
        
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        logger.info(f"🔄 تم التبديل إلى المفتاح رقم {self.current_key_index + 1}")
        return True
    
    def get_key_count(self) -> int:
        """
        الحصول على عدد المفاتيح المتاحة
        
        Returns:
            عدد المفاتيح
        """
        return len(self.api_keys)
    
    def is_ai_enabled(self) -> bool:
        """
        التحقق من تفعيل الذكاء الاصطناعي
        
        Returns:
            True إذا كان AI متاحاً
        """
        return self.is_available

# إنشاء نسخة واحدة من الإعدادات
_gemini_config = GeminiConfig()

def get_gemini_api_key() -> Optional[str]:
    """
    الحصول على مفتاح Gemini API الحالي
    
    Returns:
        مفتاح API أو None
    """
    return _gemini_config.get_current_key()

def switch_gemini_key() -> bool:
    """
    التبديل إلى مفتاح Gemini التالي
    
    Returns:
        True إذا تم التبديل بنجاح
    """
    return _gemini_config.switch_key()

def is_ai_available() -> bool:
    """
    التحقق من توفر الذكاء الاصطناعي
    
    Returns:
        True إذا كان AI متاحاً
    """
    return _gemini_config.is_ai_enabled()

def get_key_count() -> int:
    """
    الحصول على عدد مفاتيح API المتاحة
    
    Returns:
        عدد المفاتيح
    """
    return _gemini_config.get_key_count()

def reload_config():
    """
    إعادة تحميل الإعدادات
    """
    global _gemini_config
    _gemini_config = GeminiConfig()
    logger.info("🔄 تم إعادة تحميل إعدادات Gemini")
