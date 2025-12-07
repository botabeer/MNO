# games/fast_typing_game.py - Enhanced Fast Typing Game
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
import time
from constants import COLORS
from games.game_helpers import (
    normalize_text, create_game_header, create_progress_box, 
    create_separator, create_winner_card
)


class FastTypingGame:
    """
    لعبة التايب السريع
    - 5 جولات
    - كتابة العبارة بالضبط
    - أول إجابة صحيحة يفوز
    - يقيس الوقت للترتيب
    """

    PHRASES = [
        "اكتب هذه العبارة بسرعة",
        "السماء زرقاء والشمس ساطعة",
        "التحدي يبدأ الآن",
        "النجاح يحتاج إلى صبر وعمل",
        "الوقت كالسيف إن لم تقطعه قطعك",
        "العلم نور والجهل ظلام",
        "الصديق وقت الضيق",
        "درهم وقاية خير من قنطار علاج",
        "من جد وجد ومن سار على الدرب وصل",
        "الحياة قصيرة فلا تضيعها",
        "اطلب العلم من المهد إلى اللحد",
        "القراءة غذاء العقل",
        "الصحة تاج على رؤوس الأصحاء",
        "العقل السليم في الجسم السليم",
        "الوطن أغلى ما نملك"
    ]

    def __init__(self, line_bot_api, total_questions=5):
        self.line_bot_api = line_bot_api
        self.total_questions = total_questions
        self.questions = []
        self.current_question = 0
        self.player_scores = {}
        self.question_answered = False
        self.question_start_time = None
        self.registered = set()

    def register_player(self, user_id: str, display_name: str):
        """تسجيل لاعب"""
        self.registered.add(user_id)
        return True

    def start_game(self):
        """بدء اللعبة"""
        self.questions = random.sample(
            self.PHRASES,
            min(self.total_questions, len(self.PHRASES))
        )
        self.current_question = 0
        self.player_scores = {}
        self.question_answered = False
        
        return self._show_question()

    def _show_question(self):
        """عرض السؤال"""
        phrase = self.questions[self.current_question]
        self.question_start_time = time.time()
        self.question_answered = False

        contents = [
            create_game_header("التايب السريع", "اكتب العبارة بسرعة"),
            create_progress_box(self.current_question + 1, self.total_questions),
            create_separator(),
            
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": phrase,
                        "size": "lg",
                        "weight": "bold",
                        "color": COLORS['primary'],
                        "align": "center",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": "اكتب العبارة كما هي بالضبط",
                        "size": "xs",
                        "color": COLORS['text_light'],
                        "align": "center",
                        "margin": "md",
                        "wrap": True
                    }
                ],
                "margin": "lg"
            },
            
            create_separator(),
            
            {
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "margin": "md",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "جاوب",
                            "text": "جاوب"
                        },
                        "style": "secondary",
                        "height": "sm"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "ايقاف",
                            "text": "ايقاف"
                        },
                        "style": "secondary",
                        "height": "sm",
                        "color": COLORS['warning']
                    }
                ]
            }
        ]

        return FlexMessage(
            alt_text="التايب السريع",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": contents,
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "18px"
                }
            })
        )

    def next_question(self):
        """السؤال التالي"""
        self.current_question += 1
        
        if self.current_question < self.total_questions:
            return self._show_question()
        
        return None

    def check_answer(self, answer: str, user_id: str, display_name: str):
        """فحص الإجابة"""
        # Ignore non-registered players
        if user_id not in self.registered:
            return None

        # If already answered, ignore
        if self.question_answered:
            return None

        phrase = self.questions[self.current_question]
        answer_lower = answer.strip().lower()

        # Handle answer reveal
        if answer_lower in ['جاوب', 'الجواب', 'الحل']:
            self.question_answered = True
            
            if self.current_question + 1 < self.total_questions:
                return {
                    'response': TextMessage(text=f"الإجابة: {phrase}"),
                    'points': 0,
                    'correct': False,
                    'next_question': True
                }
            else:
                return self._end_game()

        # Check exact match (normalized)
        if normalize_text(answer) == normalize_text(phrase):
            # Calculate time taken
            time_taken = time.time() - self.question_start_time
            
            # Initialize player if not exists
            self.player_scores.setdefault(user_id, {
                'name': display_name,
                'score': 0,
                'total_time': 0
            })
            
            # Add score and time
            self.player_scores[user_id]['score'] += 1
            self.player_scores[user_id]['total_time'] += time_taken
            
            self.question_answered = True

            time_msg = f"{time_taken:.1f} ثانية"

            if self.current_question + 1 < self.total_questions:
                return {
                    'response': TextMessage(
                        text=f"إجابة صحيحة {display_name}\n+1 نقطة\nالوقت: {time_msg}"
                    ),
                    'points': 1,
                    'correct': True,
                    'next_question': True
                }
            else:
                return self._end_game()

        return None

    def _end_game(self):
        """إنهاء اللعبة"""
        if not self.player_scores:
            return {
                'response': TextMessage(text="انتهت اللعبة بدون فائز"),
                'points': 0,
                'correct': False,
                'game_over': True
            }

        # Sort by score first, then by time
        sorted_players = sorted(
            self.player_scores.items(),
            key=lambda x: (-x[1]['score'], x[1]['total_time'])
        )

        winner = sorted_players[0][1]
        avg_time = winner['total_time'] / winner['score'] if winner['score'] > 0 else 0

        # Create custom winner card with time info
        winner_with_time = winner.copy()
        winner_with_time['name'] = f"{winner['name']} - متوسط الوقت: {avg_time:.1f}ث"

        return {
            'response': FlexMessage(
                alt_text="نتائج اللعبة",
                contents=FlexContainer.from_dict(
                    create_winner_card(winner_with_time, sorted_players, "التايب السريع")
                )
            ),
            'points': winner['score'],
            'correct': True,
            'won': True,
            'game_over': True
        }
