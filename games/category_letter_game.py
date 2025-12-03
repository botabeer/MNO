from linebot.v3.messaging import TextMessage, FlexMessage
import random
import re
from constants import COLORS

def normalize_text(text):
    if not text:
        return ""
    text = text.strip().lower()
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '').replace('ة', 'ه').replace('ى', 'ي')
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'\s+', '', text)
    return text

class CategoryLetterGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.challenges = [
            {"category": "المطبخ", "letter": "ق", "answers": ["قدر", "قلايه", "قهوه", "قنينه"]},
            {"category": "حيوان", "letter": "ب", "answers": ["بطه", "بقره", "ببغاء", "بومه"]},
            {"category": "فاكهه", "letter": "ت", "answers": ["تفاح", "توت", "تمر", "تين"]},
            {"category": "خضار", "letter": "ب", "answers": ["بصل", "بطاطس", "باذنجان"]},
            {"category": "بلاد", "letter": "س", "answers": ["سعوديه", "سوريا", "سودان"]},
            {"category": "اسم ولد", "letter": "م", "answers": ["محمد", "مصطفى", "مالك"]},
            {"category": "اسم بنت", "letter": "ر", "answers": ["ريم", "رنا", "رهف"]},
            {"category": "مهنه", "letter": "ط", "answers": ["طبيب", "طباخ", "طيار"]},
            {"category": "رياضه", "letter": "ك", "answers": ["كره", "كاراتيه", "كريكت"]},
            {"category": "لون", "letter": "ا", "answers": ["احمر", "ازرق", "اخضر"]}
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
        progress = f"{self.current_question + 1}/{self.total_questions}"
        
        return FlexMessage(
            alt_text="فئه وحرف",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "فئه وحرف", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                        {"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": "السؤال", "size": "xs", "color": COLORS['text_light'], "flex": 0}, {"type": "text", "text": progress, "size": "xs", "color": COLORS['primary'], "weight": "bold", "align": "end"}], "margin": "lg"},
                        {"type": "separator", "margin": "md"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": f"الفئه: {challenge['category']}", "size": "lg", "color": COLORS['text_dark'], "weight": "bold", "align": "center"}, {"type": "text", "text": f"الحرف: {challenge['letter']}", "size": "xxl", "color": COLORS['primary'], "weight": "bold", "margin": "md", "align": "center"}], "margin": "lg"},
                        {"type": "separator", "margin": "lg"},
                        {"type": "box", "layout": "horizontal", "contents": [{"type": "button", "action": {"type": "message", "label": "لمح", "text": "لمح"}, "style": "secondary", "height": "sm"}, {"type": "button", "action": {"type": "message", "label": "جاوب", "text": "جاوب"}, "style": "secondary", "height": "sm"}], "spacing": "sm", "margin": "lg"}
                    ],
                    "paddingAll": "20px"
                }
            }
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

        if text.lower() in ['جاوب', 'الجواب', 'الحل']:
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
                return {'response': TextMessage(text=f"اجابه صحيحه {display_name} +{points}"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
            return self._end_game()
        
        return None

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextMessage(text="انتهت اللعبه"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
        
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        
        players_contents = []
        for i, p in enumerate(sorted_players[:5]):
            players_contents.append({
                "type": "box",
                "layout": "baseline",
                "contents": [
                    {"type": "text", "text": f"{i+1}.", "size": "sm", "flex": 0},
                    {"type": "text", "text": p[1]['name'], "size": "sm", "flex": 3, "margin": "sm"},
                    {"type": "text", "text": f"{p[1]['score']}", "size": "sm", "color": COLORS['primary'], "weight": "bold", "align": "end"}
                ],
                "margin": "md" if i > 0 else "sm"
            })
        
        winner_card = FlexMessage(
            alt_text="نتائج اللعبه",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "انتهت اللعبه", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "الفائز", "size": "sm", "color": COLORS['text_light'], "align": "center"}, {"type": "text", "text": winner['name'], "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center"}, {"type": "text", "text": f"{winner['score']} نقطه", "size": "lg", "color": COLORS['success'], "align": "center"}], "margin": "lg"},
                        {"type": "separator", "margin": "lg"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "النتائج", "size": "md", "weight": "bold"}, *players_contents], "margin": "lg"},
                        {"type": "button", "action": {"type": "message", "label": "اعادة اللعب", "text": "فئه"}, "style": "primary", "margin": "lg"}
                    ],
                    "paddingAll": "20px"
                }
            }
        )
        return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
