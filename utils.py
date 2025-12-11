import re
from functools import lru_cache

@lru_cache(maxsize=1000)
def normalize_text(text):
    if not text:
        return ""
    
    text = text.strip().lower()
    
    translation_table = str.maketrans({
        'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
        'ؤ': 'و', 'ئ': 'ي', 'ء': '',
        'ة': 'ه', 'ى': 'ي'
    })
    
    text = text.translate(translation_table)
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'\s+', '', text)
    
    return text

def is_valid_name(name):
    if not name or len(name.strip()) == 0:
        return False
    
    name = name.strip()
    
    if not (1 <= len(name) <= 50):
        return False
    
    dangerous_chars = ['<', '>', '"', "'", '\\', '\n', '\r', '\t']
    if any(char in name for char in dangerous_chars):
        return False
    
    if not re.match(r'^[\u0600-\u06FFa-zA-Z0-9\s]+$', name):
        return False
    
    return True
