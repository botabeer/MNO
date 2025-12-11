from games.base_game import BaseGame, normalize_text
from constants import COLORS
import random

class OppositeGame(BaseGame):
    """لعبة الأضداد - اذكر عكس الكلمة"""
    
    ALL_WORDS = [
        {"word": "كبير", "opposite": "صغير"},
        {"word": "طويل", "opposite": "قصير"},
        {"word": "سريع", "opposite": "بطيء"},
        {"word": "ساخن", "opposite": "بارد"},
        {"word": "نظيف", "opposite": "وسخ"},
        {"word": "قوي", "opposite": "ضعيف"},
        {"word": "سهل", "opposite": "صعب"},
        {"word": "جميل", "opposite": "قبيح"},
        {"word": "غني", "opposite": "فقير"},
        {"word": "فوق", "opposite": "تحت"},
        {"word": "يمين", "opposite": "يسار"},
        {"word": "أمام", "opposite": "خلف"},
        {"word": "داخل", "opposite": "خارج"},
        {"word": "قريب", "opposite": "بعيد"},
        {"word": "جديد", "opposite": "قديم"},
        {"word": "ثقيل", "opposite": "خفيف"},
        {"word": "مظلم", "opposite": "مضيء"},
        {"word": "صادق", "opposite": "كاذب"},
        {"word": "شجاع", "opposite": "جبان"},
        {"word": "نشيط", "opposite": "كسول"}
    ]
    
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, total_questions=5)
    
    def _load_questions(self):
        """تحميل أسئلة الأضداد"""
        return random.sample(self.ALL_WORDS, min(self.total_questions, len(self.ALL_WORDS)))
    
    def _get_correct_answer(self, question):
        """الحصول على الضد الصحيح"""
        return question['opposite']
    
    def _get_game_name(self):
        """اسم اللعبة"""
        return "لعبة الأضداد"
    
    def _get_restart_command(self):
        """أمر إعادة اللعب"""
        return "ضد"
    
    def _build_question_content(self, question):
        """بناء محتوى السؤال"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [{
                "type": "text",
                "text": f"ما هو عكس {question['word']}",
                "size": "lg",
                "color": COLORS['text_dark'],
                "wrap": True,
                "weight": "bold",
                "align": "center"
            }],
            "margin": "lg"
        }
