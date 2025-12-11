"""
لعبة أغنيه - Bot Mesh v20.1 FINAL
Created by: Abeer Aldosari © 2025
✅ نقطة واحدة لكل إجابة | ثيمات | سؤال سابق | أزرار | بدون وقت
"""

from games.base_game import BaseGame
import random
from typing import Dict, Any, Optional


class SongGame(BaseGame):
    """لعبة أغنيه"""

    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "أغنيه"
        self.supports_hint = True
        self.supports_reveal = True

        self.songs = [
            {"lyrics":"رجعت لي أيام الماضي معاك","artist":"أم كلثوم"},
            {"lyrics":"قولي أحبك كي تزيد وسامتي","artist":"كاظم الساهر"},
            {"lyrics":"بردان أنا تكفى أبي احترق بدفا لعيونك","artist":"محمد عبده"},
            {"lyrics":"جلست والخوف بعينيها تتأمل فنجاني","artist":"عبد الحليم حافظ"},
            {"lyrics":"أحبك موت كلمة مالها تفسير","artist":"ماجد المهندس"},
            {"lyrics":"تملي معاك ولو حتى بعيد عني","artist":"عمرو دياب"},
            {"lyrics":"يا بنات يا بنات","artist":"نانسي عجرم"},
            {"lyrics":"رحت عني ما قويت جيت لك لاتردني","artist":"عبدالمجيد عبدالله"},
            {"lyrics":"أنا لحبيبي وحبيبي إلي","artist":"فيروز"},
            {"lyrics":"كيف أبيّن لك شعوري دون ما أحكي","artist":"عايض"},
            {"lyrics":"حبيبي يا كل الحياة اوعدني تبقى معايا","artist":"تامر حسني"},
            {"lyrics":"خذني من ليلي لليلك","artist":"عبادي الجوهر"},
            {"lyrics":"قلبي بيسألني عنك دخلك طمني وينك","artist":"وائل كفوري"},
            {"lyrics":"تدري كثر ماني من البعد مخنوق","artist":"راشد الماجد"},
            {"lyrics":"اسخر لك غلا وتشوفني مقصر","artist":"عايض"},
            {"lyrics":"انسى هالعالم ولو هم يزعلون","artist":"عباس ابراهيم"},
            {"lyrics":"أشوفك كل يوم وأروح وأقول نظرة ترد الروح","artist":"محمد عبده"},
            {"lyrics":"أنا عندي قلب واحد","artist":"حسين الجسمي"},
            {"lyrics":"منوتي ليتك معي","artist":"محمد عبده"},
            {"lyrics":"جننت قلبي بحب يلوي ذراعي","artist":"ماجد المهندس"},
            {"lyrics":"خلنا مني طمني عليك","artist":"نوال الكويتية"},
            {"lyrics":"أحبك ليه أنا مدري","artist":"عبدالمجيد عبدالله"},
            {"lyrics":"أمر الله أقوى أحبك والعقل واعي","artist":"ماجد المهندس"},
            {"lyrics":"في زحمة الناس صعبة حالتي","artist":"محمد عبده"},
            {"lyrics":"الحب يتعب من يدله والله في حبه بلاني","artist":"راشد الماجد"},
            {"lyrics":"محد غيرك شغل عقلي شغل بالي","artist":"وليد الشامي"},
            {"lyrics":"نكتشف مر الحقيقة بعد ما يفوت الأوان","artist":"أصالة"},
            {"lyrics":"بديت أطيب بديت احس بك عادي","artist":"ماجد المهندس"},
            {"lyrics":"يا هي توجع كذبة اخباري تمام","artist":"أميمة طالب"},
            {"lyrics":"احس اني لقيتك بس عشان تضيع مني","artist":"عبدالمجيد عبدالله"},
            {"lyrics":"اختلفنا مين يحب الثاني أكثر","artist":"محمد عبده"},
            {"lyrics":"من أول نظرة شفتك قلت هذا اللي تمنيته","artist":"ماجد المهندس"},
            {"lyrics":"لبيه يا بو عيون وساع","artist":"محمد عبده"},
            {"lyrics":"اسمحيلي يا الغرام العف","artist":"محمد عبده"},
            {"lyrics":"سألوني الناس عنك يا حبيبي","artist":"فيروز"},
            {"lyrics":"أنا بلياك إذا أرمش تنزل ألف دمعة","artist":"ماجد المهندس"},
            {"lyrics":"عطشان يا برق السما","artist":"ماجد المهندس"},
            {"lyrics":"يراودني شعور إني أحبك أكثر من أول","artist":"راشد الماجد"},
            {"lyrics":"هيجيلي موجوع دموعه ف عينه","artist":"تامر عاشور"},
            {"lyrics":"تيجي نتراهن إن هيجي اليوم","artist":"تامر عاشور"},
            {"lyrics":"خليني ف حضنك يا حبيبي","artist":"تامر عاشور"},
            {"lyrics":"أنا أكثر شخص بالدنيا يحبك","artist":"راشد الماجد"},
            {"lyrics":"أريد الله يسامحني لأن أذيت نفسي","artist":"رحمة رياض"},
            {"lyrics":"كون نصير أنا وياك نجمة بالسما","artist":"رحمة رياض"},
            {"lyrics":"على طاري الزعل والدمعتين","artist":"أصيل هميم"},
            {"lyrics":"يشبهك قلبي كنك القلب مخلوق","artist":"أصيل هميم"},
            {"lyrics":"ليت العمر لو كان مليون مرة","artist":"راشد الماجد"},
            {"lyrics":"أحبه بس مو معناه اسمحله يجرح","artist":"أصيل هميم"},
            {"lyrics":"المفروض أعوفك من زمان","artist":"أصيل هميم"},
            {"lyrics":"ضعت منك وانهدم جسر التلاقي","artist":"أميمة طالب"},
            {"lyrics":"تلمست لك عذر","artist":"راشد الماجد"},
            {"lyrics":"بيان صادر من معاناة المحبة","artist":"أميمة طالب"},
            {"lyrics":"أنا ودي إذا ودك نعيد الماضي","artist":"رابح صقر"},
            {"lyrics":"عظيم إحساسي والشوق فيني","artist":"راشد الماجد"},
            {"lyrics":"مثل ما تحب ياروحي ألبي رغبتك","artist":"رابح صقر"},
            {"lyrics":"كل ما بلل مطر وصلك ثيابي","artist":"رابح صقر"},
            {"lyrics":"خذ راحتك ماعاد تفرق معي","artist":"راشد الماجد"},
            {"lyrics":"واسع خيالك اكتبه أنا بكذبك معجبه","artist":"شمة حمدان"},
            {"lyrics":"ما دريت إني أحبك ما دريت","artist":"شمة حمدان"},
            {"lyrics":"قال الوداع ومقصده يجرح القلب","artist":"راشد الماجد"},
            {"lyrics":"حبيته بيني وبين نفسي","artist":"شيرين"},
            {"lyrics":"كلها غيرانة بتحقد","artist":"شيرين"},
            {"lyrics":"اللي لقى احبابه نسى اصحابه","artist":"راشد الماجد"},
            {"lyrics":"مشاعر تشاور تودع تسافر","artist":"شيرين"},
            {"lyrics":"أنا مش بتاعت الكلام ده","artist":"شيرين"},
            {"lyrics":"مقادير يا قلبي العنا مقادير","artist":"طلال مداح"},
            {"lyrics":"ظلمتني والله قوي يجازيك","artist":"طلال مداح"},
            {"lyrics":"كلمة ولو جبر خاطر","artist":"عبادي الجوهر"},
            {"lyrics":"فزيت من نومي أناديلك","artist":"ذكرى"},
            {"lyrics":"ابد على حطة يدك","artist":"ذكرى"},
            {"lyrics":"أنا لولا الغلا والمحبة","artist":"فؤاد عبدالواحد"},
            {"lyrics":"أحبك لو تكون حاضر","artist":"عبادي الجوهر"},
            {"lyrics":"إلحق عيني إلحق","artist":"وليد الشامي"},
            {"lyrics":"يردون قلت لازم يردون","artist":"وليد الشامي"},
            {"lyrics":"ماعاد يمديني ولا عاد يمديك","artist":"عبدالمجيد عبدالله"},
            {"lyrics":"ولهان أنا ولهان","artist":"وليد الشامي"},
            {"lyrics":"اقولها كبر عن الدنيا حبيبي","artist":"وليد الشامي"},
            {"lyrics":"أنا استاهل وداع أفضل وداع","artist":"نوال الكويتية"},
            {"lyrics":"لقيت روحي بعد ما لقيتك","artist":"نوال الكويتية"},
            {"lyrics":"يا بعدهم كلهم يا سراجي بينهم","artist":"عبدالمجيد عبدالله"},
            {"lyrics":"غريبة الناس غريبة الدنيا","artist":"وائل جسار"},
            {"lyrics":"اعذريني يوم زفافك","artist":"وائل جسار"},
            {"lyrics":"حتى الكره احساس","artist":"عبدالمجيد عبدالله"},
            {"lyrics":"استكثرك وقتي علي","artist":"عبدالمجيد عبدالله"},
            {"lyrics":"ياما حاولت الفراق وما قويت","artist":"عبدالمجيد عبدالله"}
        ]

        random.shuffle(self.songs)
        self.used_songs = []

    def start_game(self):
        self.current_question = 0
        self.game_active = True
        self.previous_question = None
        self.previous_answer = None
        self.answered_users.clear()
        self.used_songs = []
        return self.get_question()

    def get_question(self):
        available = [s for s in self.songs if s not in self.used_songs]
        if not available:
            self.used_songs = []
            available = self.songs.copy()

        q_data = random.choice(available)
        self.used_songs.append(q_data)
        self.current_answer = [q_data["artist"]]

        return self.build_question_flex(
            question_text=q_data['lyrics'],
            additional_info="من المغني"
        )

    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        if not self.game_active or user_id in self.answered_users:
            return None

        if self.team_mode and user_id not in self.joined_users:
            return None

        normalized = self.normalize_text(user_answer)

        if self.can_use_hint() and normalized == "لمح":
            artist = self.current_answer[0]
            hint = f"يبدأ بـ {artist[0]}\nعدد الحروف {len(artist)}"
            return {"message": hint, "response": self._create_text_message(hint), "points": 0}

        if self.can_reveal_answer() and normalized == "جاوب":
            reveal = f"المغني {self.current_answer[0]}"
            self.previous_question = self.used_songs[-1]["lyrics"] if self.used_songs else None
            self.previous_answer = self.current_answer[0]
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["message"] = f"{reveal}\n\n{result.get('message', '')}"
                return result

            return {"message": reveal, "response": self.get_question(), "points": 0}

        if self.team_mode and normalized in ["لمح", "جاوب"]:
            return None

        correct_normalized = self.normalize_text(self.current_answer[0])
        
        if normalized == correct_normalized:
            total_points = 1

            if self.team_mode:
                team = self.get_user_team(user_id) or self.assign_to_team(user_id)
                self.add_team_score(team, total_points)
            else:
                self.add_score(user_id, display_name, total_points)

            self.previous_question = self.used_songs[-1]["lyrics"] if self.used_songs else None
            self.previous_answer = self.current_answer[0]
            self.answered_users.add(user_id)
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = total_points
                return result

            return {"message": f"صحيح +{total_points}", "response": self.get_question(), "points": total_points}

        return None
