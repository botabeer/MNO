"""
لعبة خمن - Bot Mesh v20.1 FINAL
Created by: Abeer Aldosari © 2025
✅ نقطة واحدة لكل إجابة | ثيمات | سؤال سابق | أزرار | بدون وقت
"""

from games.base_game import BaseGame
import random
from typing import Dict, Any, Optional, List


class GuessGame(BaseGame):
    """لعبة خمن"""

    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "خمن"
        self.supports_hint = True
        self.supports_reveal = True

        self.items = {
            "المطبخ": {
                "ق": ["قدر", "قلاية", "قارورة"],
                "م": ["ملعقة", "مغرفة", "مقلاة", "مبشرة"],
                "س": ["سكين", "صحن", "سلة"],
                "ط": ["طنجرة", "طبق"],
                "ف": ["فرن", "فنجان", "فلتر"],
                "ك": ["كأس", "كوب"],
                "ش": ["شوكة", "شاي"],
                "ت": ["تنور", "ترمس"],
                "ص": ["صينية", "صحن"]
            },
            "غرفة النوم": {
                "س": ["سرير", "ستارة"],
                "و": ["وسادة", "ورد"],
                "م": ["مرآة", "مخدة", "مصباح"],
                "خ": ["خزانة"],
                "ل": ["لحاف", "لمبة"],
                "د": ["دولاب"],
                "ش": ["شرشف"]
            },
            "المدرسة": {
                "ق": ["قلم", "قرطاسية"],
                "د": ["دفتر", "دولاب"],
                "ك": ["كتاب", "كراسة"],
                "م": ["مسطرة", "ممحاة", "معلم", "مدير"],
                "س": ["سبورة", "سلم"],
                "ح": ["حقيبة", "حصة"],
                "ط": ["طالب", "طاولة"],
                "ش": ["شنطة"]
            },
            "الفواكه": {
                "ت": ["تفاح", "تمر", "توت", "تين"],
                "م": ["موز", "مشمش", "منجا"],
                "ع": ["عنب"],
                "ب": ["برتقال", "بطيخ", "برقوق"],
                "ر": ["رمان"],
                "ك": ["كمثرى", "كرز", "كيوي"],
                "ف": ["فراولة"],
                "ن": ["نكتارين"]
            },
            "الحيوانات": {
                "ق": ["قطة", "قرد"],
                "س": ["سنجاب"],
                "ف": ["فيل", "فهد", "فأر"],
                "أ": ["أسد", "أرنب"],
                "ج": ["جمل", "جاموس"],
                "ن": ["نمر", "نعامة"],
                "ح": ["حصان", "حمار"],
                "خ": ["خروف"],
                "ز": ["زرافة"],
                "د": ["ديك", "دجاج"]
            },
            "الخضروات": {
                "ب": ["بطاطس", "بصل", "بقدونس"],
                "ط": ["طماطم"],
                "خ": ["خيار", "خس"],
                "ج": ["جزر"],
                "ف": ["فلفل", "فجل"],
                "ك": ["كوسا"],
                "ث": ["ثوم"]
            },
            "المهن": {
                "ط": ["طبيب", "طيار"],
                "م": ["معلم", "مهندس", "محامي"],
                "ك": ["كاتب"],
                "ص": ["صيدلي"],
                "خ": ["خباز"],
                "ن": ["نجار"],
                "ح": ["حداد"],
                "س": ["سائق"]
            },
            "الرياضة": {
                "ك": ["كرة", "كاراتيه"],
                "س": ["سباحة"],
                "ج": ["جري"],
                "ق": ["قفز"],
                "ر": ["رماية"],
                "م": ["مصارعة"],
                "ت": ["تنس"]
            },
            "الألوان": {
                "أ": ["أحمر", "أزرق", "أخضر", "أصفر"],
                "ب": ["بني", "برتقالي", "بنفسجي"],
                "و": ["وردي"],
                "ر": ["رمادي"]
            },
            "الطقس": {
                "م": ["مطر", "مشمس"],
                "ر": ["رعد", "ريح"],
                "ب": ["برق", "برد"],
                "غ": ["غيم", "غبار"],
                "ث": ["ثلج"],
                "ص": ["صحو"]
            }
        }

        self.questions_list: List[Dict[str, Any]] = []
        for category, letters in self.items.items():
            for letter, words in letters.items():
                self.questions_list.append({
                    "category": category,
                    "letter": letter,
                    "answers": words
                })

        random.shuffle(self.questions_list)

    def start_game(self):
        self.current_question = 0
        self.game_active = True
        self.previous_question = None
        self.previous_answer = None
        self.answered_users.clear()
        self.scores.clear()
        return self.get_question()

    def get_question(self):
        q_data = self.questions_list[self.current_question % len(self.questions_list)]
        self.current_answer = q_data["answers"]

        return self.build_question_flex(
            question_text=f"الفئة {q_data['category']}\nيبدأ بحرف {q_data['letter']}",
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
            q_data = self.questions_list[self.current_question % len(self.questions_list)]
            self.previous_question = f"{q_data['category']} حرف {q_data['letter']}"
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

        for correct_answer in self.current_answer:
            if self.normalize_text(correct_answer) == normalized:
                total_points = 1

                if self.team_mode:
                    team = self.get_user_team(user_id) or self.assign_to_team(user_id)
                    self.add_team_score(team, total_points)
                else:
                    self.add_score(user_id, display_name, total_points)

                q_data = self.questions_list[self.current_question % len(self.questions_list)]
                self.previous_question = f"{q_data['category']} حرف {q_data['letter']}"
                self.previous_answer = correct_answer
                self.current_question += 1
                self.answered_users.clear()

                if self.current_question >= self.questions_count:
                    result = self.end_game()
                    result["points"] = total_points
                    return result

                return {"message": f"صحيح +{total_points}", "response": self.get_question(), "points": total_points}

        return None
