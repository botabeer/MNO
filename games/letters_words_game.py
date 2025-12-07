from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import COLORS
from games.game_helpers import (
    normalize_text, create_game_header, create_progress_box,
    create_separator, create_action_buttons, create_winner_card
)

class LettersWordsGame:
    """
    لعبة تكوين الكلمات – النسخة المحسنة
    - إدارة أفضل للجولات
    - نظام تلميح محسّن
    - هيكلة أوضح للبيانات
    - حماية من الأخطاء
    - دعم تعدد اللاعبين بشكل أسرع وهجومي أقل
    """

    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api

        # التحديات منظمة بشكل أفضل
        self.challenges = [
            {"letters": "ق ل م ع ر ك", "answers": ["قلم", "علم", "عمر", "رقم", "ملك", "قرم", "عرق", "كرم", "لقم", "عقر"]},
            {"letters": "ك ت ا ب ر ل", "answers": ["كتاب", "باب", "كتب", "تراب", "بكر", "كبر", "بار", "كرت", "تبر", "ركب"]},
            {"letters": "م د ر س ه ل", "answers": ["مدرسه", "سهل", "درس", "سهم", "مدر", "رمل", "مهر", "هرم", "سرد", "مهد"]},
            {"letters": "ش ج ر ف ق ه", "answers": ["شجر", "فجر", "قهر", "شرف", "فرش", "جرف", "شقه", "رشق", "فرق", "جهر"]},
            {"letters": "ح د ي ق ه ل", "answers": ["حديقه", "قديح", "حقل", "دقيق", "حيل", "قلد", "لحد", "ديل", "حدل", "قيد"]},
            {"letters": "ب ي ت ك ر م", "answers": ["بيت", "كريم", "كبر", "ترك", "ريم", "كتم", "بكر", "يكتب", "تمر", "بكي"]},
            {"letters": "ن و ر س م ا", "answers": ["نور", "سمر", "مان", "سور", "نار", "رمس", "مرس", "روس", "سمن", "نوم"]},
            {"letters": "ف ل ج ر ب ح", "answers": ["فجر", "جرح", "حرب", "حفل", "فلج", "برج", "رحب", "جفل", "فرح", "لحب"]},
            {"letters": "س ل ا م و ن", "answers": ["سلام", "سلم", "مان", "سما", "لوم", "ماس", "سول", "نام", "نسل", "ملس"]},
            {"letters": "ع ل ي ا ن ب", "answers": ["علي", "عليا", "بني", "ليان", "بان", "بعل", "نيل", "عني", "نبي", "علن"]}
        ]

        # المتغيرات الأساسية
        self.total_questions = 5
        self.words_needed = 3

        # المتغيرات القابلة لإعادة الضبط
        self.reset_game()

    # --------------------------------------
    #            GAME RESET
    # --------------------------------------
    def reset_game(self):
        self.questions = random.sample(self.challenges, self.total_questions)
        self.current_question = 0
        self.valid_words = []
        self.player_scores = {}      # {user_id: {"name": "xx", "score": 0}}
        self.found_words = {}        # {user_id: [ "word1", "word2" ]}
        self.hints_used = {}         # {user_id: True}

    # --------------------------------------
    #             START GAME
    # --------------------------------------
    def start_game(self):
        self.reset_game()
        return self._show_question()

    # --------------------------------------
    #             SHOW QUESTION
    # --------------------------------------
    def _show_question(self):
        challenge = self.questions[self.current_question]
        letters = challenge['letters']

        # نجهّز الكلمات المسموحة
        self.valid_words = [normalize_text(w) for w in challenge["answers"]]

        flex_body = [
            create_game_header("تكوين الكلمات"),
            create_progress_box(self.current_question + 1, self.total_questions),
            create_separator(),

            # حروف التحدي
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": letters, "size": "xxl",
                     "color": COLORS["primary"], "weight": "bold", "align": "center"},
                    {
                        "type": "text",
                        "text": f"كوّن {self.words_needed} كلمات من هذه الحروف",
                        "size": "sm",
                        "color": COLORS["text_dark"],
                        "margin": "md",
                        "wrap": True,
                        "align": "center"
                    }
                ],
                "margin": "lg"
            },

            create_separator(),
            *create_action_buttons()
        ]

        return FlexMessage(
            alt_text="تكوين الكلمات",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": flex_body,
                    "backgroundColor": COLORS["card_bg"],
                    "paddingAll": "20px"
                }
            })
        )

    # --------------------------------------
    #            NEXT QUESTION
    # --------------------------------------
    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.found_words = {}
            self.hints_used = {}
            return self._show_question()

        return None  # النظام سيقوم بإنهاء اللعبة

    # --------------------------------------
    #           CHECK ANSWER
    # --------------------------------------
    def check_answer(self, text, user_id, display_name):
        text = text.strip()

        # ---------- نظام التلميح ----------
        if text.lower() in ["لمح", "تلميح"]:
            return self._handle_hint(user_id)

        # ---------- طلب الإجابة ----------
        if text.lower() in ["جاوب", "الحل"]:
            return self._handle_solution_request()

        # ---------- معالجة الكلمة ----------
        return self._handle_word_answer(text, user_id, display_name)

    # --------------------------------------
    #          HANDLE HINT SYSTEM
    # --------------------------------------
    def _handle_hint(self, user_id):
        if user_id in self.hints_used:
            return {"response": TextMessage(text="استخدمت التلميح مسبقاً"), "points": 0, "correct": False}

        self.hints_used[user_id] = True
        sample = self.questions[self.current_question]["answers"][0]
        return {
            "response": TextMessage(text=f"تلميح:\n• يبدأ بـ: {sample[0]}\n• عدد الحروف: {len(sample)}"),
            "points": 0,
            "correct": False
        }

    # --------------------------------------
    #      HANDLE REQUESTING FULL ANSWERS
    # --------------------------------------
    def _handle_solution_request(self):
        answers = self.questions[self.current_question]["answers"]
        partial = " - ".join(answers[:5])

        if self.current_question + 1 < self.total_questions:
            return {
                "response": TextMessage(text=f"بعض الكلمات الصحيحة:\n{partial}"),
                "points": 0,
                "correct": False,
                "next_question": True
            }

        return self._end_game()

    # --------------------------------------
    #      HANDLE NORMAL WORD ANSWERS
    # --------------------------------------
    def _handle_word_answer(self, text, user_id, display_name):
        word = normalize_text(text)

        # كلمة مكررة لنفس اللاعب
        if user_id in self.found_words and word in self.found_words[user_id]:
            return {"response": TextMessage(text="هذه الكلمة سبق وأن أدخلتها"), "points": 0, "correct": False}

        # كلمة غير صحيحة
        if word not in self.valid_words:
            return {"response": TextMessage(text="هذه الكلمة غير صحيحة"), "points": 0, "correct": False}

        # تسجيل اللاعب
        self.found_words.setdefault(user_id, [])
        self.found_words[user_id].append(word)

        self.player_scores.setdefault(user_id, {"name": display_name, "score": 0})
        self.player_scores[user_id]["score"] += 1

        found = len(self.found_words[user_id])

        if found >= self.words_needed:
            if self.current_question + 1 < self.total_questions:
                return {
                    "response": TextMessage(text=f"أحسنت يا {display_name}!\n+1 نقطة 🎉"),
                    "points": 1,
                    "correct": True,
                    "won": True,
                    "next_question": True
                }

            return self._end_game()

        return {
            "response": TextMessage(
                text=f"كلمة صحيحة! +1 نقطة\nتبقى: {self.words_needed - found}"
            ),
            "points": 1,
            "correct": True
        }

    # --------------------------------------
    #              END GAME
    # --------------------------------------
    def _end_game(self):
        if not self.player_scores:
            return {
                "response": TextMessage(text="انتهت اللعبة"),
                "points": 0,
                "correct": False,
                "won": False,
                "game_over": True
            }

        sorted_players = sorted(
            self.player_scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )

        winner = sorted_players[0][1]

        flex = create_winner_card(winner, sorted_players, "تكوين الكلمات")

        return {
            "response": FlexMessage(
                alt_text="نتائج اللعبة",
                contents=FlexContainer.from_dict(flex)
            ),
            "points": winner["score"],
            "correct": True,
            "won": True,
            "game_over": True
        }
