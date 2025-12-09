# games/seen_jeem_game.py
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import THEMES
from games.game_helpers import normalize_text, create_game_header, create_progress_box, create_separator, create_action_buttons, create_winner_card
from database import Database

class SeenJeemGame:
    def __init__(self, line_bot_api, total_questions=5):
        self.line_bot_api = line_bot_api
        self.questions_data = [
            {"q": "س: ما هو الشيء الذي يمشي بلا رجلين ويبكي بلا عينين", "a": "السحاب"},
            {"q": "س: ما هو الشيء الذي له اسنان ولا يعض", "a": "المشط"},
            {"q": "س: ما هو الشيء الذي كلما زاد نقص", "a": "العمر"},
            {"q": "س: ما هو الشيء الذي يكتب ولا يقرا", "a": "القلم"},
            {"q": "س: ما هو الشيء الذي له عين ولا يرى", "a": "الابرة"},
            {"q": "س: ما هو الشيء الذي يوجد في القرن مرة وفي الدقيقة مرتين ولا يوجد في الساعة", "a": "حرف القاف"},
            {"q": "س: ما هو الشيء الذي ترميه كلما احتجت اليه", "a": "شبكة الصيد"},
            {"q": "س: ما هو الشيء الذي يقرصك ولا تراه", "a": "الجوع"},
            {"q": "س: ما هو الشيء الذي لا يدخل الا اذا ضربته على راسه", "a": "المسمار"},
            {"q": "س: ما هو الشيء الذي لونه اخضر في الارض واسود في السوق واحمر في البيت", "a": "الشاي"},
            {"q": "س: من هو الذي مات ولم يولد", "a": "ادم"},
            {"q": "س: ما هو اطول نهر في العالم", "a": "النيل"},
            {"q": "س: ما هي عاصمة السعودية", "a": "الرياض"},
            {"q": "س: كم عدد ايام السنة", "a": "365"},
            {"q": "س: ما هو الحيوان الملقب بسفينة الصحراء", "a": "الجمل"},
            {"q": "س: كم عدد الوان قوس قزح", "a": "7"},
            {"q": "س: ما هو اكبر كوكب في المجموعة الشمسية", "a": "المشتري"},
            {"q": "س: كم عدد قارات العالم", "a": "7"},
            {"q": "س: ما هي اصغر دولة في العالم", "a": "الفاتيكان"},
            {"q": "س: ما هو الحيوان الذي ينام واحدى عينيه مفتوحة", "a": "الدلفين"},
            {"q": "س: كم عدد اسنان الانسان البالغ", "a": "32"},
            {"q": "س: ما هو اسرع حيوان بري", "a": "الفهد"},
            {"q": "س: كم عدد عظام جسم الانسان", "a": "206"},
            {"q": "س: ما هي عاصمة فرنسا", "a": "باريس"},
            {"q": "س: ما هو اكبر محيط في العالم", "a": "الهادي"},
            {"q": "س: كم عدد ايام الاسبوع", "a": "7"},
            {"q": "س: ما هو الحيوان الذي لا يشرب الماء", "a": "الكنغر البري"},
            {"q": "س: كم عدد اشهر السنة", "a": "12"},
            {"q": "س: ما هي عاصمة مصر", "a": "القاهرة"},
            {"q": "س: ما هو اذكى حيوان", "a": "الدلفين"}
        ]
        self.total_questions = total_questions
        self.questions = []
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        self.registered = set()

    def register_player(self, uid, name):
        self.registered.add(uid)
        return True

    def start_game(self):
        self.questions = random.sample(self.questions_data, min(self.total_questions, len(self.questions_data)))
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        return self._show_question()

    def _show_question(self, theme="light"):
        colors = THEMES.get(theme, THEMES["light"])
        q_data = self.questions[self.current_question]
        
        contents = [
            create_game_header("سين جيم", theme=theme),
            create_progress_box(self.current_question + 1, self.total_questions, theme=theme),
            create_separator(theme=theme),
            {
                "type": "text",
                "text": q_data["q"],
                "size": "md",
                "color": colors["text_dark"],
                "wrap": True,
                "margin": "lg",
                "weight": "bold"
            },
            create_separator(theme=theme),
            *create_action_buttons(theme=theme)
        ]

        return FlexMessage(
            alt_text="سين جيم",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": contents,
                    "backgroundColor": colors["card_bg"],
                    "paddingAll": "18px"
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
        if user_id not in self.registered:
            return None
        if user_id in self.answered_users:
            return None

        q_data = self.questions[self.current_question]
        txt = text.strip().lower()
        theme = Database.get_user_theme(user_id)

        if txt in ['لمح', 'تلميح']:
            answer = q_data["a"]
            hint = f"يبدا بحرف: {answer[0]}\nعدد الحروف: {len(answer)}"
            return {'response': TextMessage(text=hint), 'points': 0, 'correct': False}

        if txt in ['جاوب', 'الجواب', 'الحل']:
            self.answered_users.add(user_id)
            if self.current_question + 1 < self.total_questions:
                return {
                    'response': TextMessage(text=f"الاجابة: {q_data['a']}"),
                    'points': 0,
                    'correct': False,
                    'next_question': True
                }
            return self._end_game(user_id)

        normalized = normalize_text(text)
        correct_answer = normalize_text(q_data["a"])

        if normalized == correct_answer or normalized in correct_answer or correct_answer in normalized:
            self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})
            self.player_scores[user_id]['score'] += 1
            self.answered_users.add(user_id)

            if self.current_question + 1 < self.total_questions:
                return {
                    'response': TextMessage(text=f"اجابة صحيحة {display_name}\n+1 نقطة"),
                    'points': 1,
                    'correct': True,
                    'next_question': True
                }
            return self._end_game(user_id)

        return None

    def _end_game(self, user_id):
        theme = Database.get_user_theme(user_id)
        if not self.player_scores:
            return {
                'response': TextMessage(text="انتهت اللعبة بدون فائز"),
                'points': 0,
                'correct': False,
                'game_over': True
            }

        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]

        return {
            'response': FlexMessage(
                alt_text="نتائج اللعبة",
                contents=FlexContainer.from_dict(create_winner_card(winner, sorted_players, "سين جيم", theme=theme))
            ),
            'points': winner['score'],
            'correct': True,
            'game_over': True
        }
