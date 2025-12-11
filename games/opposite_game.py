"""
لعبة ضد - Bot Mesh v20.1 FINAL
Created by: Abeer Aldosari © 2025
✅ نقطة واحدة لكل إجابة | ثيمات | سؤال سابق | أزرار | بدون وقت
"""

from games.base_game import BaseGame
import random
from typing import Dict, Any, Optional


class OppositeGame(BaseGame):
    """لعبة ضد"""

    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "ضد"
        self.supports_hint = True
        self.supports_reveal = True

        self.opposites = {
            "كبير": ["صغير", "قصير", "ضئيل", "محدود"],
            "طويل": ["قصير", "قزم"],
            "سريع": ["بطيء", "متمهل"],
            "ساخن": ["بارد", "مثلج"],
            "نظيف": ["وسخ", "قذر", "متسخ"],
            "جديد": ["قديم", "عتيق"],
            "صعب": ["سهل", "بسيط", "ميسر"],
            "قوي": ["ضعيف", "واهن"],
            "غني": ["فقير", "معدم"],
            "سعيد": ["حزين", "تعيس", "كئيب"],
            "جميل": ["قبيح", "دميم"],
            "ثقيل": ["خفيف", "طائر"],
            "عالي": ["منخفض", "واطي"],
            "واسع": ["ضيق", "محدود"],
            "قريب": ["بعيد", "نائي"],
            "مفتوح": ["مغلق", "مقفل"],
            "نهار": ["ليل", "مساء"],
            "شمس": ["قمر", "نجم"],
            "شتاء": ["صيف", "حر"],
            "شرق": ["غرب", "مغرب"],
            "شمال": ["جنوب", "قبلة"],
            "أبيض": ["أسود", "معتم"],
            "حلو": ["مر", "حامض", "مالح"],
            "حار": ["بارد", "ثلجي"],
            "جاف": ["رطب", "مبلل"],
            "مالح": ["حلو", "عذب"],
            "صحيح": ["خطأ", "خاطئ", "غلط"],
            "حي": ["ميت", "متوفي"],
            "نور": ["ظلام", "ظلمة", "عتمة"],
            "فوق": ["تحت", "أسفل"],
            "يمين": ["يسار", "شمال"],
            "أمام": ["خلف", "وراء", "دبر"],
            "داخل": ["خارج", "برا"],
            "صباح": ["مساء", "عصر", "ليل"],
            "أول": ["آخر", "نهاية"],
            "كثير": ["قليل", "نادر"],
            "عميق": ["سطحي", "ضحل"],
            "ممتلئ": ["فارغ", "خالي"],
            "ناعم": ["خشن", "قاسي"],
            "لين": ["صلب", "قاسي"],
            "حاد": ["كليل", "غير حاد"],
            "واضح": ["غامض", "مبهم"],
            "نشيط": ["كسول", "خامل"],
            "صامت": ["صاخب", "مزعج"],
            "هادئ": ["صاخب", "عالي"],
            "مبلل": ["جاف", "ناشف"],
            "مضيء": ["مظلم", "معتم"],
            "رخيص": ["غالي", "ثمين"],
            "بسيط": ["معقد", "صعب"],
            "عريض": ["ضيق", "نحيف"]
        }

        self.questions_list = list(self.opposites.items())
        random.shuffle(self.questions_list)

    def start_game(self):
        self.current_question = 0
        self.game_active = True
        self.previous_question = None
        self.previous_answer = None
        self.answered_users.clear()
        return self.get_question()

    def get_question(self):
        word, opposites = self.questions_list[self.current_question % len(self.questions_list)]
        self.current_answer = opposites

        return self.build_question_flex(
            question_text=f"ما هو عكس كلمة\n\n{word}",
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
            if len(answer) <= 2:
                hint = f"الكلمة قصيرة {answer[0]}"
            else:
                hint = f"{answer[0]}{answer[1]}" + "_" * (len(answer) - 2)
                hint = f"تلميح {hint}"
            return {"message": hint, "response": self._create_text_message(hint), "points": 0}

        if self.can_reveal_answer() and normalized == "جاوب":
            answers_text = " او ".join(self.current_answer)
            word, _ = self.questions_list[self.current_question % len(self.questions_list)]
            self.previous_question = f"عكس {word}"
            self.previous_answer = answers_text
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["message"] = f"الإجابة {answers_text}\n\n{result.get('message','')}"
                return result

            return {"message": f"الإجابة {answers_text}", "response": self.get_question(), "points": 0}

        if self.team_mode and normalized in ["لمح", "جاوب"]:
            return None

        for correct_answer in self.current_answer:
            if self.normalize_text(correct_answer) == normalized:
                total_points = 1
                
                if self.team_mode:
                    team = self.get_user_team(user_id) or self.assign_to_team(user_id)
                    self.add_team_score(team, total_points)
                else:
                    self.add_score(user_id, display_name, total_points)

                word, _ = self.questions_list[self.current_question % len(self.questions_list)]
                self.previous_question = f"عكس {word}"
                self.previous_answer = correct_answer
                self.current_question += 1
                self.answered_users.clear()

                if self.current_question >= self.questions_count:
                    result = self.end_game()
                    result["points"] = total_points
                    return result

                return {"message": f"صحيح +{total_points}", "response": self.get_question(), "points": total_points}

        return None
