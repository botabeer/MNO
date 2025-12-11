"""
محرك الألعاب الموحد - يدير جميع الألعاب
"""
import random
from linebot.models import TextSendMessage, FlexSendMessage
from utils import normalize_text, FlexBuilder
from constants import GAME_DATA, GAME_SETTINGS, POINTS

class BaseGame:
    """كلاس أساسي موحد لجميع الألعاب"""
    
    def __init__(self, game_type):
        self.game_type = game_type
        self.questions = []
        self.current_question = 0
        self.total_questions = GAME_SETTINGS['questions_per_game']
        self.player_scores = {}
        self.answered_users = set()
        self.first_correct_answer = False
        
        # بيانات اللعبة
        self.game_config = self._get_game_config()
    
    def _get_game_config(self):
        """الحصول على إعدادات اللعبة"""
        configs = {
            'song': {
                'name': 'لعبة الأغنية',
                'restart': 'اغنيه',
                'data': GAME_DATA['songs'],
                'question_format': lambda q: f"{q['lyrics']}\n\nمن المغني؟"
            },
            'opposite': {
                'name': 'لعبة الأضداد',
                'restart': 'ضد',
                'data': GAME_DATA['opposites'],
                'question_format': lambda q: f"ما هو عكس: {q['word']}"
            },
            'chain': {
                'name': 'سلسلة الكلمات',
                'restart': 'سلسله',
                'data': GAME_DATA['chain_words'],
                'question_format': lambda q: f"الكلمة: {q}\n\nاكتب كلمة تبدأ بحرف {q[-1]}"
            },
            'fast': {
                'name': 'الكتابة السريعة',
                'restart': 'اسرع',
                'data': GAME_DATA['fast_typing'],
                'question_format': lambda q: f"{q}\n\nاكتب النص بأسرع وقت"
            },
            'letters': {
                'name': 'تكوين الكلمات',
                'restart': 'تكوين',
                'data': GAME_DATA['letter_words'],
                'question_format': lambda q: f"{q['letters']}\n\nكون كلمات من هذه الحروف"
            },
            'category': {
                'name': 'فئة وحرف',
                'restart': 'فئه',
                'data': GAME_DATA['categories'],
                'question_format': lambda q: f"الفئة: {q['category']}\nالحرف: {q['letter']}"
            }
        }
        return configs.get(self.game_type, configs['song'])
    
    def start_game(self):
        """بدء اللعبة"""
        self.questions = random.sample(
            self.game_config['data'], 
            min(self.total_questions, len(self.game_config['data']))
        )
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        self.first_correct_answer = False
        
        return self._show_question()
    
    def _show_question(self):
        """عرض السؤال"""
        if self.current_question >= len(self.questions):
            return None
        
        question = self.questions[self.current_question]
        question_text = self.game_config['question_format'](question)
        
        self.first_correct_answer = False
        
        return FlexSendMessage(
            alt_text=self.game_config['name'],
            contents=FlexBuilder.create_question_card(
                self.game_config['name'],
                question_text,
                self.current_question + 1,
                self.total_questions
            )
        )
    
    def next_question(self):
        """الانتقال للسؤال التالي"""
        self.current_question += 1
        
        if self.current_question < self.total_questions:
            self.answered_users = set()
            self.first_correct_answer = False
            return self._show_question()
        
        return None
    
    def check_answer(self, text, user_id, display_name):
        """فحص الإجابة"""
        # تجاهل إذا كان هناك إجابة صحيحة
        if self.first_correct_answer:
            return None
        
        # تجاهل إذا كان المستخدم أجاب
        if user_id in self.answered_users:
            return None
        
        if self.current_question >= len(self.questions):
            return None
        
        question = self.questions[self.current_question]
        text_lower = text.strip().lower()
        
        # التلميح
        if text_lower in ['لمح', 'تلميح']:
            return self._handle_hint(question)
        
        # عرض الإجابة
        if text_lower in ['جاوب', 'الجواب', 'الحل']:
            return self._handle_show_answer(user_id, question)
        
        # التحقق من الإجابة
        return self._validate_answer(text, user_id, display_name, question)
    
    def _handle_hint(self, question):
        """معالجة التلميح"""
        answer = self._get_answer(question)
        hint_text = f"يبدأ بحرف: {answer[0]}\nعدد الحروف: {len(answer)}"
        
        return {
            'response': TextSendMessage(text=hint_text),
            'points': POINTS['hint'],
            'correct': False
        }
    
    def _handle_show_answer(self, user_id, question):
        """عرض الإجابة"""
        self.answered_users.add(user_id)
        self.first_correct_answer = True
        answer = self._get_answer(question)
        
        if self.current_question + 1 < self.total_questions:
            return {
                'response': TextSendMessage(text=f"الإجابة: {answer}"),
                'points': POINTS['show_answer'],
                'correct': False,
                'next_question': True
            }
        
        return self._end_game()
    
    def _validate_answer(self, text, user_id, display_name, question):
        """التحقق من صحة الإجابة"""
        normalized_answer = normalize_text(text)
        correct_answer = normalize_text(self._get_answer(question))
        
        if normalized_answer == correct_answer:
            return self._handle_correct_answer(user_id, display_name)
        
        return None
    
    def _get_answer(self, question):
        """الحصول على الإجابة الصحيحة"""
        if isinstance(question, dict):
            return question.get('answer', question.get('singer', ''))
        return question
    
    def _handle_correct_answer(self, user_id, display_name):
        """معالجة الإجابة الصحيحة"""
        if user_id not in self.player_scores:
            self.player_scores[user_id] = {'name': display_name, 'score': 0}
        
        points = POINTS['correct']
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
        """إنهاء اللعبة"""
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
                contents=FlexBuilder.create_winner_card(
                    self.game_config['name'],
                    winner,
                    sorted_players,
                    self.game_config['restart']
                )
            ),
            'points': winner['score'],
            'correct': True,
            'won': True,
            'game_over': True
        }
