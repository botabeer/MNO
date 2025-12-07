from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import COLORS
from games.game_helpers import normalize_text, create_game_header, create_progress_box, create_separator, create_action_buttons, create_winner_card

class CategoryLetterGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.challenges = [
            {"category": "المطبخ", "letter": "ق", "answers": ["قدر", "قلايه", "قهوه", "قنينه", "قباقيب"]},
            {"category": "حيوان", "letter": "ب", "answers": ["بطه", "بقره", "ببغاء", "بومه", "بعير"]},
            {"category": "فاكهه", "letter": "ت", "answers": ["تفاح", "توت", "تمر", "تين", "ترنج"]},
            {"category": "خضار", "letter": "ب", "answers": ["بصل", "بطاطس", "باذنجان", "بقدونس", "بروكلي"]},
            {"category": "بلاد", "letter": "س", "answers": ["سعوديه", "سوريا", "سودان", "سويسرا", "سويد"]},
            {"category": "اسم ولد", "letter": "م", "answers": ["محمد", "مصطفى", "مالك", "ماجد", "معاذ"]},
            {"category": "اسم بنت", "letter": "ر", "answers": ["ريم", "رنا", "رهف", "رغد", "رزان"]},
            {"category": "مهنه", "letter": "ط", "answers": ["طبيب", "طباخ", "طيار", "طالب", "طحان"]},
            {"category": "رياضه", "letter": "ك", "answers": ["كره", "كاراتيه", "كريكت", "كرلنج", "كرة سلة"]},
            {"category": "لون", "letter": "ا", "answers": ["احمر", "ازرق", "اخضر", "اصفر", "ابيض"]},
            {"category": "حيوان", "letter": "ف", "answers": ["فيل", "فار", "فهد", "فراشه", "فقمه"]},
            {"category": "نبات", "letter": "ن", "answers": ["نخل", "نعناع", "نرجس", "نارجيل", "نبق"]},
            {"category": "مدينه", "letter": "ج", "answers": ["جده", "جيزان", "جنيف", "جاكرتا", "جدة"]},
            {"category": "اكل", "letter": "ك", "answers": ["كبسه", "كفته", "كيك", "كريمه", "كشري"]},
            {"category": "شرب", "letter": "ع", "answers": ["عصير", "عرق سوس", "عرن", "عيران", "عسل"]}
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.answered_users = set()

    def start_game(self):
        self.questions = random.sample(self.challenges, self.total_questions)
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        return self._show_question()

    def _show_question(self):
        challenge = self.questions[self.current_question]
        
        contents = [
            create_game_header("فئه وحرف"),
            create_progress_box(self.current_question + 1, self.total_questions),
            create_separator(),
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": f"الفئه: {challenge['category']}", "size": "lg", "color": COLORS['text_dark'], "weight": "bold", "align": "center"},
                    {"type": "text", "text": f"الحرف: {challenge['letter']}", "size": "xxl", "color": COLORS['primary'], "weight": "bold", "margin": "md", "align": "center"}
                ],
                "margin": "lg"
            },
            create_separator(),
            *create_action_buttons()
        ]
        
        return FlexMessage(
            alt_text="فئه وحرف",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": contents,
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            })
        )

    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.answered_users = set()
            return self._show_question()
        return None

    def check_answer(self, text, user_id, display_name):
        if user_id in self.answered_users:
            return None
        
        challenge = self.questions[self.current_question]
        text = text.strip()

        if text.lower() in ['لمح', 'تلميح']:
            sample = challenge['answers'][0]
            return {'response': TextMessage(text=f"يبدا بحرف: {sample[0]}\nعدد الحروف: {len(sample)}"), 'points': 0, 'correct': False}

        if text.lower() in ['جاوب', 'الحل']:
            answers = ' - '.join(challenge['answers'][:3])
            self.answered_users.add(user_id)
            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"بعض الاجابات:\n{answers}"), 'points': 0, 'correct': False, 'next_question': True}
            return self._end_game()

        normalized = normalize_text(text)
        valid_answers = [normalize_text(ans) for ans in challenge['answers']]

        if normalized in valid_answers:
            points = 1
            self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})
            self.player_scores[user_id]['score'] += points
            self.answered_users.add(user_id)

            if self.current_question + 1 < self.total_questions:
                return {'response': TextMessage(text=f"اجابه صحيحه {display_name}\n+{points} نقطه"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
            return self._end_game()
        
        return None

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبه"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
        
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        
        winner_card_dict = create_winner_card(winner, sorted_players, "فئه")
        
        return {
            'response': FlexMessage(alt_text="نتائج اللعبه", contents=FlexContainer.from_dict(winner_card_dict)),
            'points': winner['score'],
            'correct': True,
            'won': True,
            'game_over': True
        }
