# ========== guess_game.py ==========
"""لعبة التخمين بالفئات والحروف"""
from linebot.models import TextSendMessage
import random
import re

class GuessGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.current_question = 0
        self.max_questions = 5
        self.current_answer = []
        
        # قاعدة بيانات الكلمات مرتبة حسب الفئة والحرف
        self.items = {
            "المطبخ": {
                "ق": ["قدر", "قلاية"],
                "م": ["ملعقة", "مغرفة"],
                "س": ["سكين", "صحن"],
                "ف": ["فرن", "فنجان"],
                "ك": ["كوب", "كاسة"],
                "ط": ["طبق", "طنجرة"],
                "ش": ["شوكة"],
                "ب": ["برادة"],
                "غ": ["غلاية"]
            },
            "غرفة النوم": {
                "س": ["سرير"],
                "و": ["وسادة"],
                "م": ["مرآة", "مخدة"],
                "خ": ["خزانة"],
                "د": ["دولاب"],
                "ل": ["لحاف"],
                "ش": ["شراشف"],
                "ب": ["بطانية"]
            },
            "غرفة الجلوس": {
                "ك": ["كرسي", "كنب"],
                "ط": ["طاولة"],
                "ت": ["تلفاز", "تلفزيون"],
                "س": ["ستارة"],
                "ر": ["رف"],
                "م": ["مكتب"],
                "ش": ["شاشة"]
            },
            "الحمام": {
                "ص": ["صابون"],
                "م": ["مرحاض", "مغسلة", "مرآة", "منشفة"],
                "ش": ["شامبو", "شطاف"],
                "ف": ["فرشاة"],
                "ح": ["حوض"]
            },
            "المدرسة": {
                "ق": ["قلم"],
                "د": ["دفتر"],
                "ك": ["كتاب"],
                "م": ["مسطرة", "ممحاة", "محفظة"],
                "س": ["سبورة"],
                "ط": ["طاولة"],
                "ح": ["حقيبة"]
            },
            "السيارة": {
                "م": ["محرك", "مقود"],
                "ع": ["عجلة"],
                "ك": ["كرسي"],
                "ش": ["شباك"],
                "ب": ["باب", "بنزين"],
                "ف": ["فرامل"],
                "ر": ["رادار"]
            },
            "الحديقة": {
                "ش": ["شجرة"],
                "ز": ["زهرة"],
                "ع": ["عشب"],
                "ب": ["بركة"],
                "م": ["مقعد"],
                "ج": ["جذع"],
                "و": ["ورقة"]
            }
        }
        
        # إنشاء قائمة الأسئلة
        self.questions_list = []
        for category, letters_dict in self.items.items():
            for letter, words in letters_dict.items():
                if words:
                    self.questions_list.append({
                        "category": category,
                        "letter": letter,
                        "answers": words
                    })
        
        random.shuffle(self.questions_list)
    
    def normalize_text(self, text):
        """تطبيع النص للمقارنة"""
        text = text.strip().lower()
        text = re.sub(r'^ال', '', text)
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ة', 'ه')
        text = text.replace('ى', 'ي')
        text = re.sub(r'[\u064B-\u065F]', '', text)
        return text
    
    def start_game(self):
        """بدء اللعبة"""
        self.current_question = 0
        return self.get_question()
    
    def get_question(self):
        """الحصول على السؤال الحالي"""
        q_data = self.questions_list[self.current_question % len(self.questions_list)]
        self.current_answer = q_data["answers"]
        
        message = f"خمن الكلمة ({self.current_question + 1}/{self.max_questions})\n\n"
        message += f"الفئة: {q_data['category']}\n"
        message += f"يبدأ بحرف: {q_data['letter']}\n\n"
        message += "ما هو؟\n\n"
        message += "جاوب - لعرض الاجابة"
        
        return TextSendMessage(text=message)
    
    def check_answer(self, answer, user_id, display_name):
        """فحص الإجابة"""
        answer_normalized = answer.strip().lower()
        
        # أمر عرض الإجابة
        if answer_normalized in ['جاوب', 'استسلم']:
            answers_text = " او ".join(self.current_answer)
            self.current_question += 1
            
            if self.current_question >= self.max_questions:
                return {
                    'points': 0,
                    'won': False,
                    'game_over': False,
                    'response': TextSendMessage(
                        text=f"الاجابة الصحيحة: {answers_text}\n\n"
                             f"انتهت الاسئلة!"
                    )
                }
            
            next_q = self.get_question()
            return {
                'points': 0,
                'won': False,
                'response': TextSendMessage(
                    text=f"الاجابة الصحيحة: {answers_text}\n\n{next_q.text}"
                )
            }
        
        # فحص الإجابة
        normalized_answer = self.normalize_text(answer)
        
        for correct_answer in self.current_answer:
            if self.normalize_text(correct_answer) == normalized_answer:
                self.current_question += 1
                
                if self.current_question >= self.max_questions:
                    return {
                        'points': 10,
                        'won': True,
                        'game_over': False,
                        'response': TextSendMessage(
                            text=f"ممتاز {display_name}!\n\nالنقاط: +10"
                        )
                    }
                
                next_q = self.get_question()
                return {
                    'points': 10,
                    'won': True,
                    'response': TextSendMessage(
                        text=f"ممتاز {display_name}!\n\nالنقاط: +10\n\n{next_q.text}"
                    )
                }
        
        return {
            'points': 0,
            'won': False,
            'response': TextSendMessage(text="خطأ! حاول مرة اخرى")
        }
