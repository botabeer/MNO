from abc import ABC, abstractmethod
from linebot.models import FlexSendMessage, TextSendMessage
from constants import COLORS
import re
import random

def normalize_text(text):
    """تطبيع النص العربي بشكل موحد"""
    if not text:
        return ""
    
    text = text.strip().lower()
    
    # استبدال الحروف المتشابهة
    replacements = {
        'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
        'ؤ': 'و', 'ئ': 'ي', 'ء': '',
        'ة': 'ه', 'ى': 'ي'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # إزالة التشكيل
    text = re.sub(r'[\u064B-\u065F]', '', text)
    
    # إزالة المسافات الزائدة
    text = re.sub(r'\s+', '', text)
    
    return text

class BaseGame(ABC):
    """
    كلاس أساسي لجميع الألعاب
    يوفر البنية الأساسية والمنطق المشترك
    """
    
    def __init__(self, line_bot_api, total_questions=5):
        self.line_bot_api = line_bot_api
        self.total_questions = total_questions
        self.questions = []
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        self.first_correct_answer = False
    
    @abstractmethod
    def _load_questions(self):
        """
        تحميل الأسئلة للعبة
        يجب على كل لعبة تنفيذ هذه الدالة
        """
        pass
    
    @abstractmethod
    def _get_correct_answer(self, question):
        """
        الحصول على الإجابة الصحيحة للسؤال
        يجب على كل لعبة تنفيذ هذه الدالة
        """
        pass
    
    @abstractmethod
    def _get_game_name(self):
        """اسم اللعبة للعرض"""
        pass
    
    @abstractmethod
    def _get_restart_command(self):
        """أمر إعادة اللعب"""
        pass
    
    def start_game(self):
        """بداية اللعبة"""
        self.questions = self._load_questions()
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        self.first_correct_answer = False
        return self._show_question()
    
    def _show_question(self):
        """عرض السؤال الحالي"""
        if self.current_question >= len(self.questions):
            return None
        
        question = self.questions[self.current_question]
        progress = f"{self.current_question + 1}/{self.total_questions}"
        self.first_correct_answer = False
        
        return FlexSendMessage(
            alt_text=self._get_game_name(),
            contents=self._build_question_card(question, progress)
        )
    
    def _build_question_card(self, question, progress):
        """بناء كارت السؤال"""
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    self._build_header(),
                    self._build_progress(progress),
                    {"type": "separator", "margin": "md", "color": COLORS['border']},
                    self._build_question_content(question),
                    {"type": "separator", "margin": "lg", "color": COLORS['border']},
                    self._build_action_buttons()
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
    
    def _build_header(self):
        """بناء رأس اللعبة"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [{
                "type": "text",
                "text": self._get_game_name(),
                "weight": "bold",
                "size": "xl",
                "color": COLORS['white'],
                "align": "center"
            }],
            "backgroundColor": COLORS['primary'],
            "paddingAll": "20px",
            "cornerRadius": "12px"
        }
    
    def _build_progress(self, progress):
        """بناء شريط التقدم"""
        return {
            "type": "box",
            "layout": "baseline",
            "contents": [
                {
                    "type": "text",
                    "text": "السؤال",
                    "size": "xs",
                    "color": COLORS['text_light'],
                    "flex": 0
                },
                {
                    "type": "text",
                    "text": progress,
                    "size": "xs",
                    "color": COLORS['primary'],
                    "weight": "bold",
                    "align": "end"
                }
            ],
            "margin": "lg"
        }
    
    def _build_question_content(self, question):
        """
        بناء محتوى السؤال
        يمكن تخصيصه في كل لعبة
        """
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [{
                "type": "text",
                "text": str(question),
                "size": "lg",
                "color": COLORS['text_dark'],
                "wrap": True,
                "weight": "bold",
                "align": "center"
            }],
            "margin": "lg"
        }
    
    def _build_action_buttons(self):
        """بناء أزرار الإجراءات"""
        return {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "لمح",
                        "text": "لمح"
                    },
                    "style": "secondary",
                    "height": "sm",
                    "flex": 1
                },
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "جاوب",
                        "text": "جاوب"
                    },
                    "style": "secondary",
                    "height": "sm",
                    "flex": 1
                }
            ],
            "spacing": "sm",
            "margin": "lg"
        }
    
    def next_question(self):
        """الانتقال للسؤال التالي"""
        self.current_question += 1
        
        if self.current_question < self.total_questions:
            self.answered_users = set()
            self.first_correct_answer = False
            return self._show_question()
        
        return None
    
    def check_answer(self, text, user_id, display_name):
        """
        فحص الإجابة
        منطق موحد لجميع الألعاب
        """
        # تجاهل إذا كان هناك إجابة صحيحة بالفعل
        if self.first_correct_answer:
            return None
        
        # تجاهل إذا كان المستخدم أجاب بالفعل
        if user_id in self.answered_users:
            return None
        
        if self.current_question >= len(self.questions):
            return None
        
        question = self.questions[self.current_question]
        text_lower = text.strip().lower()
        
        # معالجة التلميح
        if text_lower in ['لمح', 'تلميح']:
            return self._handle_hint(question)
        
        # معالجة عرض الإجابة
        if text_lower in ['جاوب', 'الجواب', 'الحل']:
            return self._handle_show_answer(user_id, question)
        
        # التحقق من الإجابة
        return self._validate_answer(text, user_id, display_name, question)
    
    def _handle_hint(self, question):
        """معالجة طلب التلميح"""
        answer = self._get_correct_answer(question)
        hint_text = f"يبدأ بحرف: {answer[0]}\nعدد الحروف: {len(answer)}"
        
        return {
            'response': TextSendMessage(text=hint_text),
            'points': 0,
            'correct': False
        }
    
    def _handle_show_answer(self, user_id, question):
        """معالجة عرض الإجابة"""
        self.answered_users.add(user_id)
        self.first_correct_answer = True
        answer = self._get_correct_answer(question)
        
        if self.current_question + 1 < self.total_questions:
            return {
                'response': TextSendMessage(text=f"الإجابة: {answer}"),
                'points': 0,
                'correct': False,
                'next_question': True
            }
        
        return self._end_game()
    
    def _validate_answer(self, text, user_id, display_name, question):
        """
        التحقق من صحة الإجابة
        يمكن تخصيصه في كل لعبة
        """
        normalized_answer = normalize_text(text)
        correct_answer = normalize_text(self._get_correct_answer(question))
        
        if normalized_answer == correct_answer:
            return self._handle_correct_answer(user_id, display_name)
        
        return None
    
    def _handle_correct_answer(self, user_id, display_name, points=1):
        """معالجة الإجابة الصحيحة"""
        if user_id not in self.player_scores:
            self.player_scores[user_id] = {'name': display_name, 'score': 0}
        
        self.player_scores[user_id]['score'] += points
        self.answered_users.add(user_id)
        self.first_correct_answer = True
        
        if self.current_question + 1 < self.total_questions:
            return {
                'response': TextSendMessage(
                    text=f"إجابة صحيحة {display_name}\n+{points} نقطة"
                ),
                'points': points,
                'correct': True,
                'won': True,
                'next_question': True
            }
        
        return self._end_game()
    
    def _end_game(self):
        """إنهاء اللعبة وعرض النتائج"""
        if not self.player_scores:
            return {
                'response': TextSendMessage(text="انتهت اللعبة"),
                'points': 0,
                'correct': False,
                'won': False,
                'game_over': True
            }
        
        sorted_players = sorted(
            self.player_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        winner = sorted_players[0][1]
        
        return {
            'response': FlexSendMessage(
                alt_text="نتائج اللعبة",
                contents=self._build_winner_card(winner, sorted_players)
            ),
            'points': winner['score'],
            'correct': True,
            'won': True,
            'game_over': True
        }
    
    def _build_winner_card(self, winner, sorted_players):
        """بناء بطاقة الفائز"""
        players_list = []
        
        for i, (uid, player) in enumerate(sorted_players[:5]):
            rank = f"{i+1}."
            players_list.append({
                "type": "box",
                "layout": "baseline",
                "contents": [
                    {
                        "type": "text",
                        "text": rank,
                        "size": "sm",
                        "flex": 0
                    },
                    {
                        "type": "text",
                        "text": player['name'],
                        "size": "sm",
                        "color": COLORS['text_dark'],
                        "flex": 3,
                        "margin": "sm"
                    },
                    {
                        "type": "text",
                        "text": f"{player['score']} نقطة",
                        "size": "sm",
                        "color": COLORS['primary'],
                        "weight": "bold",
                        "align": "end",
                        "flex": 2
                    }
                ],
                "margin": "md" if i > 0 else "sm"
            })
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [{
                            "type": "text",
                            "text": "انتهت اللعبة",
                            "weight": "bold",
                            "size": "xl",
                            "color": COLORS['white'],
                            "align": "center"
                        }],
                        "backgroundColor": COLORS['primary'],
                        "paddingAll": "20px",
                        "cornerRadius": "12px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "الفائز",
                                "size": "sm",
                                "color": COLORS['text_light'],
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": winner['name'],
                                "size": "xxl",
                                "color": COLORS['primary'],
                                "weight": "bold",
                                "align": "center",
                                "margin": "xs"
                            },
                            {
                                "type": "text",
                                "text": f"{winner['score']} نقطة",
                                "size": "lg",
                                "color": COLORS['success'],
                                "align": "center",
                                "margin": "xs"
                            }
                        ],
                        "margin": "lg"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": COLORS['border']
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "النتائج",
                                "size": "md",
                                "color": COLORS['text_dark'],
                                "weight": "bold"
                            },
                            *players_list
                        ],
                        "margin": "lg"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": COLORS['border']
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "إعادة اللعب",
                            "text": self._get_restart_command()
                        },
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm",
                        "margin": "lg"
                    }
                ],
                "backgroundColor": COLORS['card_bg'],
                "paddingAll": "20px"
            }
        }
