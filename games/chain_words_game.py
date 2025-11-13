"""
لعبة السلسلة - Chain Words
اللاعب يكمل كلمة بآخر حرف من الكلمة السابقة
"""

from linebot.models import TextSendMessage
import random
import logging

logger = logging.getLogger(__name__)


class ChainWordsGame:
    """لعبة سلسلة الكلمات"""
    
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.current_word = None
        self.last_letter = None
        self.used_words = set()
        
        # كلمات البداية
        self.start_words = [
            'سيارة', 'قلم', 'كتاب', 'بيت', 'شمس', 'قمر', 'نهر', 'جبل',
            'زهرة', 'طائر', 'سمك', 'شجرة', 'مدرسة', 'مسجد', 'باب', 'نافذة'
        ]
        
        # كلمات مقبولة لكل حرف
        self.words_by_letter = {
            'ة': ['تفاحة', 'برتقالة', 'موزة', 'مدرسة', 'جامعة'],
            'م': ['مدرسة', 'مسجد', 'ملعب', 'مطار', 'مكتب', 'منزل'],
            'ب': ['بيت', 'باب', 'بحر', 'برج', 'بستان'],
            'ت': ['تفاح', 'تمر', 'تين', 'توت'],
            'ن': ['نهر', 'نافذة', 'نخلة', 'نجم', 'نمر'],
            'س': ['سيارة', 'سمك', 'سماء', 'سفينة', 'سرير'],
            'ر': ['رمل', 'رياح', 'رمان', 'ريش', 'رسم'],
            'ل': ['ليمون', 'لوز', 'لون', 'لحم'],
            'ك': ['كتاب', 'كرسي', 'كوب', 'كمبيوتر'],
            'ه': ['هاتف', 'هواء', 'هرم'],
            'د': ['دجاج', 'دب', 'دولاب', 'درج'],
            'ج': ['جمل', 'جبل', 'جزر', 'جوز'],
            'ح': ['حديقة', 'حمام', 'حليب', 'حصان'],
            'خ': ['خروف', 'خيار', 'خبز', 'خوخ'],
            'ز': ['زيت', 'زهرة', 'زرافة'],
            'ش': ['شمس', 'شجرة', 'شاي', 'شباك'],
            'ص': ['صحراء', 'صقر', 'صورة'],
            'ض': ['ضفدع', 'ضوء'],
            'ط': ['طائر', 'طاولة', 'طريق', 'طماطم'],
            'ظ': ['ظل', 'ظرف'],
            'ع': ['عصفور', 'عنب', 'عسل', 'عين'],
            'غ': ['غزال', 'غرفة', 'غابة'],
            'ف': ['فيل', 'فراشة', 'فاكهة', 'فرن'],
            'ق': ['قطة', 'قلم', 'قمر', 'قهوة'],
            'و': ['وردة', 'ورق', 'وزن'],
            'ي': ['يد', 'يمين', 'يسار']
        }
    
    def start_game(self):
        """بدء سؤال جديد"""
        self.current_word = random.choice(self.start_words)
        self.last_letter = self.current_word[-1]
        self.used_words = {self.current_word}
        
        return TextSendMessage(
            text=f"سلسلة الكلمات!\n\n"
                 f"الكلمة: {self.current_word}\n\n"
                 f"اكتب كلمة تبدأ بحرف: {self.last_letter}\n\n"
                 f"جاوب - لعرض امثلة"
        )
    
    def check_answer(self, answer, user_id, display_name):
        """فحص الإجابة"""
        if not self.last_letter:
            return None
        
        answer_normalized = answer.strip().lower()
        
        if answer_normalized in ['جاوب', 'استسلم']:
            examples = self.words_by_letter.get(self.last_letter, ['لا توجد امثلة'])
            return {
                'points': 0,
                'won': False,
                'game_over': False,
                'response': TextSendMessage(
                    text=f"امثلة لحرف {self.last_letter}:\n" + '\n'.join(examples[:3])
                )
            }
        
        # فحص: هل الكلمة تبدأ بالحرف الصحيح؟
        if not answer_normalized.startswith(self.last_letter):
            return {
                'points': 0,
                'won': False,
                'response': TextSendMessage(
                    text=f"خطأ! يجب ان تبدأ بحرف: {self.last_letter}"
                )
            }
        
        # فحص: هل استخدمت من قبل؟
        if answer_normalized in self.used_words:
            return {
                'points': 0,
                'won': False,
                'response': TextSendMessage(text="هذه الكلمة استخدمت من قبل!")
            }
        
        # فحص: هل الكلمة صحيحة؟
        if len(answer_normalized) >= 2:
            self.used_words.add(answer_normalized)
            self.current_word = answer_normalized
            self.last_letter = answer_normalized[-1]
            
            return {
                'points': 5,
                'won': True,
                'game_over': False,
                'response': TextSendMessage(
                    text=f"ممتاز {display_name}!\n\n"
                         f"الكلمة التالية بحرف: {self.last_letter}\n"
                         f"النقاط: +5"
                )
            }
        else:
            return {
                'points': 0,
                'won': False,
                'response': TextSendMessage(text="كلمة قصيرة جدا!")
            }
