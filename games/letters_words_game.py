"""
لعبة تكوين - Bot Mesh v20.1 FINAL
Created by: Abeer Aldosari © 2025
✅ نقطة واحدة لكل كلمة | ثيمات | سؤال سابق | أزرار | بدون وقت
"""

from games.base_game import BaseGame
import random
from typing import Dict, Any, Optional


class LettersWordsGame(BaseGame):
    """لعبة تكوين"""

    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "تكوين"
        self.supports_hint = True
        self.supports_reveal = True

        self.letter_sets = [
            {"letters": ["ق","ل","م","ع","ر","ب"], "words": ["قلم","عمل","علم","قلب","رقم","عقل","قبل","بقر","قرب","عرب"]},
            {"letters": ["س","ا","ر","ة","ي","م"], "words": ["سيارة","سير","مسار","سارية","رأس","أسر","يسار","مارس","سام","رمي"]},
            {"letters": ["ك","ت","ا","ب","م","ل"], "words": ["كتاب","كتب","مكتب","ملك","بكم","كلم","تلك","كمل"]},
            {"letters": ["د","ر","س","ة","م","ا"], "words": ["مدرسة","درس","مدرس","سدر","رسم","سرد","مسد","رمد","سمر"]},
            {"letters": ["ح","د","ي","ق","ة","ر"], "words": ["حديقة","حديد","قرد","دقيق","حرق","قدر","رحيق","حقد"]},
            {"letters": ["ب","ح","ر","ي","ة","س"], "words": ["بحيرة","بحر","سير","حرب","سحر","بحري","سبر","حبر"]},
            {"letters": ["ش","ج","ر","ة","م","ن"], "words": ["شجرة","شجر","نجم","رجم","شرج","نمر","جمر","نشر"]},
            {"letters": ["غ","ا","ب","ة","ر","ي"], "words": ["غابة","غراب","غرب","بغي","بير","ريب","بري"]},
            {"letters": ["ن","خ","ل","ة","ي","م"], "words": ["نخلة","نخل","خلي","نمل","خيل","نيل","خمل"]},
            {"letters": ["أ","س","د","ر","ن","ي"], "words": ["أسد","سرد","درس","سند","نرد","أسر","دنس","سير"]},
            {"letters": ["ف","ي","ل","ط","ر","ن"], "words": ["فيل","طير","طفل","نفط","رفل","طرف","فرن","طين"]},
            {"letters": ["ق","ط","ة","ر","ب","ي"], "words": ["قطة","قطر","بقر","طرب","رقبة","قرب","طيب","قبر"]},
            {"letters": ["ح","م","ا","م","ة","ل"], "words": ["حمامة","حمام","محل","حمل","ملح","حلم","أمل"]},
            {"letters": ["غ","ز","ا","ل","ر","ي"], "words": ["غزال","غزل","زرع","زال","لغز","رزق","زير"]},
            {"letters": ["ت","م","ر","ي","ن","س"], "words": ["تمر","تمرين","ترس","سمر","نمر","رتم","نير"]},
            {"letters": ["ل","ب","ن","ح","ة","ي"], "words": ["لبن","حلب","نبل","نحل","لحن","بني","حين"]},
            {"letters": ["خ","ب","ز","ر","ن","م"], "words": ["خبز","خزن","برز","زمن","نزر","زرن","خمر"]},
            {"letters": ["ع","س","ل","ج","ر","ن"], "words": ["عسل","جرس","عجل","رجل","سجل","عجن","سرج"]},
            {"letters": ["م","ا","ء","ي","ر","ن"], "words": ["ماء","مرء","نار","راء","أمر","مير","رين"]},
            {"letters": ["ب","ي","ت","ك","م","ن"], "words": ["بيت","كتب","نبت","بنت","نكت","كمن","بكم"]}
        ]

        random.shuffle(self.letter_sets)
        self.current_set = None
        self.found_words = set()
        self.required_words = 3

    def start_game(self):
        self.current_question = 0
        self.game_active = True
        self.previous_question = None
        self.previous_answer = None
        self.answered_users.clear()
        self.found_words.clear()
        return self.get_question()

    def get_question(self):
        q_data = self.letter_sets[self.current_question % len(self.letter_sets)]
        self.current_set = q_data
        self.current_answer = q_data["words"]
        self.found_words.clear()

        letters_display = " ".join(q_data["letters"])

        return self.build_question_flex(
            question_text=f"كون كلمات من\n{letters_display}",
            additional_info=f"مطلوب {self.required_words} كلمات"
        )

    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        if not self.game_active:
            return None

        if self.team_mode and user_id not in self.joined_users:
            return None

        normalized = self.normalize_text(user_answer)

        if self.can_use_hint() and normalized == "لمح":
            remaining = [w for w in self.current_answer if self.normalize_text(w) not in self.found_words]
            if remaining:
                word = remaining[0]
                hint = f"تبدأ بـ {word[0]}\nعدد الحروف {len(word)}"
            else:
                hint = "لا توجد تلميحات"
            return {"message": hint, "response": self._create_text_message(hint), "points": 0}

        if self.can_reveal_answer() and normalized == "جاوب":
            words = " ".join(self.current_answer[:5])
            msg = f"كلمات ممكنة {words}"
            self.current_question += 1
            self.answered_users.clear()
            self.found_words.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["message"] = f"{msg}\n\n{result.get('message', '')}"
                return result

            return {"message": msg, "response": self.get_question(), "points": 0}

        if self.team_mode and normalized in ["لمح", "جاوب"]:
            return None

        valid_words = [self.normalize_text(w) for w in self.current_answer]

        if normalized not in valid_words or normalized in self.found_words:
            return None

        self.found_words.add(normalized)
        points = 1

        if self.team_mode:
            team = self.get_user_team(user_id) or self.assign_to_team(user_id)
            self.add_team_score(team, points)
        else:
            self.add_score(user_id, display_name, points)

        if len(self.found_words) >= self.required_words:
            self.current_question += 1
            self.answered_users.clear()
            self.found_words.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = points
                return result

            return {"message": f"تم +{points}", "response": self.get_question(), "points": points}

        remaining = self.required_words - len(self.found_words)
        return {"message": f"صحيح تبقى {remaining}\n+{points}", "response": self._create_text_message(f"صحيح تبقى {remaining}\n+{points}"), "points": points}
