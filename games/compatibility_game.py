"""
لعبة التوافق بين الأسماء - نسخة محسّنة واحترافية
"""
from linebot.models import TextSendMessage
import random
import hashlib


class CompatibilityGame:
    """لعبة حساب نسبة التوافق بين اسمين"""
    
    def __init__(self, line_bot_api):
        """
        تهيئة اللعبة
        
        Args:
            line_bot_api: واجهة LINE Bot API
        """
        self.line_bot_api = line_bot_api
        self.active_sessions = {}
        
    def start_game(self):
        """بدء اللعبة وإرجاع رسالة الترحيب"""
        message = (
            "💞 لعبة التوافق 💞\n\n"
            "═══════════════════\n\n"
            "اكتشف نسبة التوافق بين أي اسمين!\n\n"
            "📝 طريقة اللعب:\n"
            "أرسل اسمين مفصولين بـ 'و'\n\n"
            "مثال: أحمد و فاطمة\n"
            "مثال: علي و سارة\n\n"
            "═══════════════════\n\n"
            "جرّب الآن! ✨"
        )
        return TextSendMessage(text=message)
    
    def calculate_compatibility(self, name1, name2):
        """
        حساب نسبة التوافق بطريقة ثابتة ومنطقية
        
        Args:
            name1: الاسم الأول
            name2: الاسم الثاني
            
        Returns:
            int: نسبة التوافق من 0-100
        """
        # استخدام hash لضمان نتيجة ثابتة لنفس الأسماء
        combined = f"{name1.lower()}{name2.lower()}"
        hash_value = int(hashlib.md5(combined.encode()).hexdigest(), 16)
        
        # توليد نسبة من 40-100 للحصول على نتائج إيجابية
        percentage = 40 + (hash_value % 61)
        return percentage
    
    def get_compatibility_emoji(self, percentage):
        """
        الحصول على إيموجي مناسب للنسبة
        
        Args:
            percentage: نسبة التوافق
            
        Returns:
            str: إيموجي مناسب
        """
        if percentage >= 90:
            return "💖💖💖💖💖"
        elif percentage >= 80:
            return "💖💖💖💖"
        elif percentage >= 70:
            return "💖💖💖"
        elif percentage >= 60:
            return "💖💖"
        else:
            return "💖"
    
    def get_compatibility_message(self, percentage):
        """
        الحصول على رسالة مناسبة للنسبة
        
        Args:
            percentage: نسبة التوافق
            
        Returns:
            str: رسالة وصفية
        """
        if percentage >= 95:
            return "توافق مثالي! توأم روح حقيقي! 🌟"
        elif percentage >= 85:
            return "توافق ممتاز! علاقة رائعة! ✨"
        elif percentage >= 75:
            return "توافق جيد جداً! استمرا معاً! 💫"
        elif percentage >= 65:
            return "توافق جيد! هناك إمكانية كبيرة! 🌸"
        elif percentage >= 55:
            return "توافق متوسط! يحتاج بعض الجهد! 🌿"
        else:
            return "توافق محدود! لكن لا شيء مستحيل! 🍀"
    
    def process_input(self, event):
        """
        معالجة إدخال المستخدم
        
        Args:
            event: حدث الرسالة من LINE
        """
        user_id = event.source.user_id
        text = event.message.text.strip()
        
        # التحقق من صيغة الإدخال
        if "و" not in text:
            error_msg = (
                "⚠️ صيغة غير صحيحة\n\n"
                "يرجى كتابة اسمين مفصولين بـ 'و'\n\n"
                "مثال: أحمد و فاطمة"
            )
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=error_msg)
            )
            return
        
        # استخراج الأسماء
        try:
            parts = text.split("و")
            if len(parts) != 2:
                raise ValueError("يجب إدخال اسمين فقط")
            
            name1 = parts[0].strip()
            name2 = parts[1].strip()
            
            # التحقق من أن الأسماء غير فارغة
            if not name1 or not name2:
                raise ValueError("الأسماء لا يمكن أن تكون فارغة")
            
            # التحقق من طول الأسماء
            if len(name1) > 30 or len(name2) > 30:
                raise ValueError("الأسماء طويلة جداً")
            
        except Exception as e:
            error_msg = (
                "⚠️ خطأ في الإدخال\n\n"
                "تأكد من كتابة اسمين صحيحين مفصولين بـ 'و'\n\n"
                "مثال: علي و ريم"
            )
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=error_msg)
            )
            return
        
        # حساب التوافق
        percentage = self.calculate_compatibility(name1, name2)
        emoji = self.get_compatibility_emoji(percentage)
        message = self.get_compatibility_message(percentage)
        
        # إنشاء رسالة النتيجة
        result_msg = (
            f"💞 نتيجة التوافق 💞\n\n"
            f"═══════════════════\n\n"
            f"👤 {name1}\n"
            f"💕\n"
            f"👤 {name2}\n\n"
            f"═══════════════════\n\n"
            f"📊 نسبة التوافق: {percentage}%\n\n"
            f"{emoji}\n\n"
            f"{message}\n\n"
            f"═══════════════════"
        )
        
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result_msg)
        )
    
    def stop_game(self, user_id):
        """
        إيقاف اللعبة للمستخدم
        
        Args:
            user_id: معرف المستخدم
        """
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]
