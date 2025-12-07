# games/chain_words_game.py - Enhanced Chain Words Game
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from games.game_helpers import (
    normalize_text, create_winner_card, create_question_card
)


class ChainWordsGame:
    """
    لعبة سلسلة الكلمات
    - 5 جولات
    - كلمة تبدأ بآخر حرف من الكلمة السابقة
    - لا تكرار الكلمات
    - أول إجابة صحيحة
    """

    START_WORDS = [
        "قلم", "كتاب", "مدرسة", "باب", "نافذة", 
        "طاولة", "كرسي", "حديقة", "شجرة", "زهرة",
        "سيارة", "طائرة", "قطار", "سفينة", "جبل"
    ]

    def __init__(self, line_bot_api, total_rounds=5):
        self.line_bot_api = line_bot_api
        self.max_rounds = total_rounds
        self.current_word = None
        self.used_words = set()
        self.round_count = 0
        self.player_scores = {}
        self.answered_users = set()
        self.registered = set()

    def register_player(self, user_id: str, display_name: str):
        self.registered.add(user_id)
        return True

    def start_game(self):
        """بدء اللعبة"""
        self.current_word = random.choice(self.START_WORDS)
        self.used_words = {normalize_text(self.current_word)}
        self.round_count = 0
        self.player_scores = {}
        self.answered_users = set()
        
        return self._show_question()

    def _show_question(self):
        """عرض السؤال"""
        last_letter = self.current_word[-1]
        
        question_text = f"الكلمة الحالية: {self.current_word}\n\nاكتب كلمة تبدأ بحرف: {last_letter}"
        
        return FlexMessage(
            alt_text="سلسلة الكلمات",
            contents=FlexContainer.from_dict(
                create_question_card(
                    question_text,
                    self.round_count + 1,
                    self.max_rounds,
                    "سلسلة الكلمات"
                )
            )
        )

    def next_question(self):
        """السؤال التالي"""
        self.round_count += 1
        
        if self.round_count < self.max_rounds:
            self.answered_users = set()
            return self._show_question()
        
        return None

    def check_answer(self, answer: str, user_id: str, display_name: str):
        """فحص الإجابة"""
        if user_id not in self.registered:
            return None
        
        if user_id in self.answered_users:
            return None

        answer = answer.strip()
        last_letter = self.current_word[-1]
        answer_lower = answer.lower()

        # Handle hint
        if answer_lower in ['لمح', 'تلميح']:
            return {
                'response': TextMessage(
                    text=f"يبدأ بحرف: {last_letter}\nمثال: أي كلمة تبدأ بهذا الحرف"
                ),
                'points': 0,
                'correct': False
            }

        # Handle answer reveal
        if answer_lower in ['جاوب', 'الجواب', 'الحل']:
            self.answered_users.add(user_id)
            
            if self.round_count + 1 < self.max_rounds:
                return {
                    'response': TextMessage(
                        text=f"يمكنك كتابة أي كلمة تبدأ بحرف: {last_letter}"
                    ),
                    'points': 0,
                    'correct': False,
                    'next_question': True
                }
            else:
                return self._end_game()

        # Normalize letters for comparison
        normalized_last = 'ه' if last_letter in ['ة', 'ه'] else last_letter
        first_letter = answer[0]
        first_letter = 'ه' if first_letter in ['ة', 'ه'] else first_letter

        normalized_answer = normalize_text(answer)

        # Check if word was used before
        if normalized_answer in self.used_words:
            return {
                'response': TextMessage(text="هذه الكلمة استخدمت من قبل"),
                'points': 0,
                'correct': False
            }

        # Check if starts with correct letter
        if first_letter == normalized_last:
            self.used_words.add(normalized_answer)
            self.current_word = answer
            points = 1

            self.player_scores.setdefault(user_id, {
                'name': display_name,
                'score': 0
            })
            self.player_scores[user_id]['score'] += points
            self.answered_users.add(user_id)

            if self.round_count + 1 < self.max_rounds:
                return {
                    'response': TextMessage(
                        text=f"إجابة صحيحة {display_name}\n+{points} نقطة"
                    ),
                    'points': points,
                    'correct': True,
                    'next_question': True
                }
            else:
                return self._end_game()

        return {
            'response': TextMessage(
                text=f"يجب أن تبدأ الكلمة بحرف: {last_letter}"
            ),
            'points': 0,
            'correct': False
        }

    def _end_game(self):
        """إنهاء اللعبة"""
        if not self.player_scores:
            return {
                'response': TextMessage(text="انتهت اللعبة بدون فائز"),
                'points': 0,
                'correct': False,
                'game_over': True
            }

        sorted_players = sorted(
            self.player_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )

        winner = sorted_players[0][1]

        return {
            'response': FlexMessage(
                alt_text="نتائج اللعبة",
                contents=FlexContainer.from_dict(
                    create_winner_card(winner, sorted_players, "سلسلة الكلمات")
                )
            ),
            'points': winner['score'],
            'correct': True,
            'won': True,
            'game_over': True
        }
