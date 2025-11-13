"""
لعبة الفروقات - نسخة مبسطة جداً
فقط عرض صور واحدة تلو الأخرى
"""

from linebot.models import TextSendMessage, ImageSendMessage
import random
import logging

logger = logging.getLogger(__name__)


class DifferencesGame:
    """لعبة الفروقات - نسخة بسيطة"""
    
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.current_index = 0
        self.shown_images = []
        
        # ضع روابط صورك هنا (أكثر من 20 صورة)
        self.images = [
            'https://up6.cc/2025/10/176300269322041.jpeg',
            'https://up6.cc/2025/10/176300269324622.jpeg',
            'https://up6.cc/2025/10/176300269325883.jpeg',
            'https://up6.cc/2025/10/176300269328574.jpeg',
            'https://up6.cc/2025/10/176300269333045.jpeg',
            'https://up6.cc/2025/10/176300269328574.jpeg',
            'https://up6.cc/2025/10/176300292845955.jpeg',
            'https://up6.cc/2025/10/176300292842534.jpeg',
            'https://up6.cc/2025/10/176300292839723.jpeg',
            'https://up6.cc/2025/10/176300292838272.jpeg',
            'https://up6.cc/2025/10/176300292836241.jpeg',
            'https://up6.cc/2025/10/176300308283581.jpeg',
            'https://up6.cc/2025/10/176300308285072.jpeg',
            'https://up6.cc/2025/10/176300308289583.jpeg',
            'https://up6.cc/2025/10/176300308292614.jpeg',
            'https://up6.cc/2025/10/176300308294345.jpeg',
            'https://up6.cc/2025/10/176300322419141.jpeg',
            'https://up6.cc/2025/10/176300322424732.jpeg',
            'https://up6.cc/2025/10/176300322426263.jpeg',
            'https://up6.cc/2025/10/176300322433374.jpeg',
            'https://up6.cc/2025/10/176300322435875.jpeg',
        ]
    
    def start_game(self):
        """بدء اللعبة بأول صورة"""
        self.current_index = 0
        self.shown_images = []
        
        # اختيار صورة عشوائية
        available_images = [img for img in self.images if img not in self.shown_images]
        
        if not available_images:
            self.shown_images = []  # إعادة تعيين
            available_images = self.images
        
        current_image = random.choice(available_images)
        self.shown_images.append(current_image)
        self.current_index += 1
        
        return [
            ImageSendMessage(
                original_content_url=current_image,
                preview_image_url=current_image
            ),
            TextSendMessage(
                text=f"صورة {self.current_index}/5\n\n"
                     f"اوجد الفروقات!\n\n"
                     f"اكتب: تم او التالي\n"
                     f"للانتقال للصورة التالية"
            )
        ]
    
    def check_answer(self, answer, user_id, display_name):
        """فحص الإجابة - فقط للانتقال للصورة التالية"""
        answer_normalized = answer.strip().lower()
        
        # التحقق من الأوامر المسموحة
        if answer_normalized not in ['تم', 'التالي', 'next', 'done']:
            return None  # تجاهل أي رد آخر
        
        # التحقق من انتهاء الأسئلة (5 صور)
        if self.current_index >= 5:
            return {
                'points': 10,
                'won': True,
                'game_over': False,
                'response': TextSendMessage(
                    text=f"احسنت {display_name}!\n\n"
                         f"انتهيت من 5 صور\n"
                         f"النقاط: +10"
                )
            }
        
        # اختيار صورة جديدة
        available_images = [img for img in self.images if img not in self.shown_images]
        
        if not available_images:
            self.shown_images = []
            available_images = self.images
        
        current_image = random.choice(available_images)
        self.shown_images.append(current_image)
        self.current_index += 1
        
        # إرسال الصورة الجديدة مباشرة
        try:
            self.line_bot_api.push_message(
                user_id,
                [
                    ImageSendMessage(
                        original_content_url=current_image,
                        preview_image_url=current_image
                    ),
                    TextSendMessage(
                        text=f"صورة {self.current_index}/5\n\n"
                             f"اوجد الفروقات!\n\n"
                             f"اكتب: تم او التالي"
                    )
                ]
            )
        except Exception as e:
            logger.error(f"خطأ في إرسال الصورة: {e}")
        
        # إرجاع نقاط للاعب
        return {
            'points': 2,
            'won': True,
            'game_over': False,
            'response': None  # لا نرسل رد لأننا أرسلنا الصورة مباشرة
        }
