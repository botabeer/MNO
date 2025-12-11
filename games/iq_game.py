"""
لعبة ذكاء - Bot Mesh v20.1 FINAL
Created by: Abeer Aldosari © 2025
✅ نقطة واحدة لكل إجابة | ثيمات | سؤال سابق | أزرار
"""

from games.base_game import BaseGame
import random
from typing import Dict, Any, Optional


class IqGame(BaseGame):
    """لعبة ذكاء"""

    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "ذكاء"
        self.supports_hint = True
        self.supports_reveal = True
        
        self.riddles = [
            {"q": "ما الشيء الذي يمشي بلا أرجل ويبكي بلا عيون", "a": ["السحاب", "الغيم", "سحاب", "غيم"]},
            {"q": "له رأس ولكن لا عين له", "a": ["الدبوس", "المسمار", "الإبرة", "دبوس", "مسمار", "ابرة"]},
            {"q": "شيء كلما زاد نقص", "a": ["العمر", "الوقت", "عمر", "وقت"]},
            {"q": "يكتب ولا يقرأ أبداً", "a": ["القلم", "قلم"]},
            {"q": "له أسنان كثيرة ولكنه لا يعض", "a": ["المشط", "مشط"]},
            {"q": "يوجد في الماء ولكن الماء يميته", "a": ["الملح", "ملح"]},
            {"q": "يتكلم بجميع اللغات دون أن يتعلمها", "a": ["الصدى", "صدى"]},
            {"q": "شيء كلما أخذت منه كبر", "a": ["الحفرة", "حفرة"]},
            {"q": "يخترق الزجاج ولا يكسره", "a": ["الضوء", "النور", "ضوء", "نور"]},
            {"q": "يسمع بلا أذن ويتكلم بلا لسان", "a": ["الهاتف", "الجوال", "هاتف", "جوال"]},
            {"q": "ما هو الشيء الذي تراه ولا تستطيع لمسه", "a": ["الظل", "ظل"]},
            {"q": "ما هو الذي يمشي بلا قدمين", "a": ["الوقت", "وقت", "الزمن"]},
            {"q": "ما هو الشيء الذي إذا دخل الماء لا يبتل", "a": ["الضوء", "ضوء"]},
            {"q": "له عينان ولا يرى", "a": ["المقص", "مقص"]},
            {"q": "أخضر في الأرض وأسود في السوق وأحمر في البيت", "a": ["الشاي", "شاي"]},
            {"q": "ما هو الشيء الذي لا يمشي إلا بالضرب", "a": ["المسمار", "مسمار"]},
            {"q": "ما هو الشيء الذي إذا قطعته كبر", "a": ["الحبل", "حبل"]},
            {"q": "له أوراق وليس شجراً", "a": ["الكتاب", "كتاب"]},
            {"q": "ما هو الشيء الذي يقرصك ولا تراه", "a": ["الجوع", "جوع"]},
            {"q": "يمتلئ بالثقوب ويحفظ الماء", "a": ["الإسفنج", "اسفنج"]},
            {"q": "يسير بلا قدمين ويدخل الأذنين", "a": ["الصوت", "صوت"]},
            {"q": "يولد كبيراً ويموت صغيراً", "a": ["الشمعة", "شمعة"]},
            {"q": "له رقبة وليس له رأس", "a": ["الزجاجة", "زجاجة"]},
            {"q": "تستطيع كسره دون لمسه", "a": ["الوعد", "وعد"]},
            {"q": "ما هو الذي ينام ولا يستيقظ", "a": ["الموت", "موت"]},
            {"q": "أبيض في الليل وأسود في النهار", "a": ["الطريق", "طريق"]},
            {"q": "ما هو الشيء الذي لا يتكلم ولكن إذا ضربته صاح", "a": ["الجرس", "جرس"]},
            {"q": "ما هو الشيء الذي إذا سميته كسر", "a": ["الصمت", "صمت"]},
            {"q": "ما هو الشيء الذي تذبحه وتبكي عليه", "a": ["البصل", "بصل"]},
            {"q": "يطير بلا أجنحة", "a": ["الوقت", "وقت", "الزمن"]},
            {"q": "يسير بلا عيون", "a": ["الماء", "ماء"]},
            {"q": "يأكل ولا يشبع", "a": ["النار", "نار"]},
            {"q": "ما هو الشيء الذي تراه ولا تمسكه", "a": ["الهواء", "هواء"]},
            {"q": "له مفتاح ولا يفتح", "a": ["البيانو", "بيانو"]},
            {"q": "يتحرك دائماً حولك ولا تشعر به", "a": ["الهواء", "هواء"]},
            {"q": "يُرى ولا يُمس", "a": ["الظل", "ظل"]},
            {"q": "ما هو الشيء الذي كلما كبر صغر", "a": ["العمر", "عمر"]},
            {"q": "له يد واحدة ولا يستطيع التصفيق", "a": ["الساعة", "ساعة"]},
            {"q": "ما هو الشيء الذي له أربع أرجل ولا يمشي", "a": ["الكرسي", "كرسي", "الطاولة", "طاولة"]},
            {"q": "يصعد ولا ينزل", "a": ["العمر", "عمر"]},
        ]

        random.shuffle(self.riddles)
        self.used_riddles = []

    def start_game(self):
        self.current_question = 0
        self.game_active = True
        self.used_riddles = []
        self.previous_question = None
        self.previous_answer = None
        self.answered_users.clear()
        return self.get_question()

    def get_question(self):
        available = [r for r in self.riddles if r not in self.used_riddles]
        if not available:
            self.used_riddles = []
            available = self.riddles.copy()

        riddle = random.choice(available)
        self.used_riddles.append(riddle)
        self.current_answer = riddle["a"]

        return self.build_question_flex(
            question_text=riddle['q'],
            additional_info=None
        )

    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        if not self.game_active or user_id in self.answered_users:
            return None
        
        if self.team_mode and user_id not in self.joined_users:
            return None

        normalized = self.normalize_text(user_answer)

        if self.can_use_hint() and normalized == "لمح":
            if not self.current_answer:
                return None
            answer = self.current_answer[0]
            hint = f"تبدأ بـ {answer[0]}\nعدد الحروف {len(answer)}"
            return {"message": hint, "response": self._create_text_message(hint), "points": 0}

        if self.can_reveal_answer() and normalized == "جاوب":
            answers_text = " او ".join(self.current_answer)
            self.previous_question = self.used_riddles[-1]["q"] if self.used_riddles else None
            self.previous_answer = answers_text
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["message"] = f"الإجابة {answers_text}\n\n{result.get('message', '')}"
                return result

            return {"message": f"الإجابة {answers_text}", "response": self.get_question(), "points": 0}

        if self.team_mode and normalized in ["لمح", "جاوب"]:
            return None

        for correct in self.current_answer:
            if self.normalize_text(correct) == normalized:
                total_points = 1

                if self.team_mode:
                    team = self.get_user_team(user_id) or self.assign_to_team(user_id)
                    self.add_team_score(team, total_points)
                else:
                    self.add_score(user_id, display_name, total_points)

                self.previous_question = self.used_riddles[-1]["q"] if self.used_riddles else None
                self.previous_answer = correct
                self.current_question += 1
                self.answered_users.clear()

                if self.current_question >= self.questions_count:
                    result = self.end_game()
                    result["points"] = total_points
                    return result

                return {"message": f"صحيح +{total_points}", "response": self.get_question(), "points": total_points}

        return None
