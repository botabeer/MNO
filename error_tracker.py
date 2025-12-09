import logging
import traceback
import sys
from datetime import datetime
from functools import wraps
from pathlib import Path

logger = logging.getLogger(__name__)

class ErrorTracker:
    """مستكشف الاخطاء المتقدم - يسجل جميع الاخطاء بتفاصيل كاملة"""
    
    ERROR_LOG_FILE = "logs/errors.log"
    
    @staticmethod
    def setup_logging():
        """اعداد نظام تسجيل الاخطاء"""
        Path("logs").mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(ErrorTracker.ERROR_LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        logger.addHandler(file_handler)
    
    @staticmethod
    def log_error(error, context="", user_id=None, extra_data=None):
        """تسجيل الخطأ مع التفاصيل الكاملة"""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "user_id": user_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "file": None,
            "line": None,
            "function": None,
            "traceback": traceback.format_exc(),
            "extra_data": extra_data or {}
        }
        
        if exc_traceback:
            tb = traceback.extract_tb(exc_traceback)
            if tb:
                last_frame = tb[-1]
                error_info["file"] = last_frame.filename
                error_info["line"] = last_frame.lineno
                error_info["function"] = last_frame.name
        
        error_message = f"""
{'='*60}
خطأ جديد تم اكتشافه
{'='*60}
الوقت: {error_info['timestamp']}
السياق: {error_info['context']}
المستخدم: {error_info['user_id'] or 'غير محدد'}
نوع الخطأ: {error_info['error_type']}
رسالة الخطأ: {error_info['error_message']}
الملف: {error_info['file']}
السطر: {error_info['line']}
الدالة: {error_info['function']}
{'='*60}
التتبع الكامل:
{error_info['traceback']}
{'='*60}
بيانات اضافية:
{error_info['extra_data']}
{'='*60}
        """
        
        logger.error(error_message)
        
        return error_info
    
    @staticmethod
    def track_function(context=""):
        """ديكوريتر لتتبع الاخطاء في الدوال"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    ErrorTracker.log_error(
                        e,
                        context=f"{context} - {func.__name__}",
                        extra_data={
                            "args": str(args)[:200],
                            "kwargs": str(kwargs)[:200]
                        }
                    )
                    raise
            return wrapper
        return decorator
    
    @staticmethod
    def safe_execute(func, *args, context="", **kwargs):
        """تنفيذ آمن مع تتبع الاخطاء"""
        try:
            result = func(*args, **kwargs)
            return result, None
        except Exception as e:
            error_info = ErrorTracker.log_error(
                e,
                context=context or f"safe_execute: {func.__name__}",
                extra_data={
                    "function": func.__name__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys())
                }
            )
            return None, error_info
    
    @staticmethod
    def get_recent_errors(limit=10):
        """قراءة آخر الاخطاء من الملف"""
        try:
            if not Path(ErrorTracker.ERROR_LOG_FILE).exists():
                return []
            
            with open(ErrorTracker.ERROR_LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return lines[-limit*10:]
        except Exception as e:
            logger.error(f"فشل قراءة ملف الاخطاء: {e}")
            return []

ErrorTracker.setup_logging()
