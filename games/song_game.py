from linebot.models import TextSendMessage
import random
import re

class SongGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.current_song = None
        self.correct_answer = None
        self.current_question = 0
        self.max_questions = 5
        self.hint_used = False

        # كل الأغاني مدموجة في قائمة واحدة
        self.songs = [
            {"lyrics": "احبك ليه؟ انا مدري ليه اهواك؟\nانا مدري لو مرت علي ذكراك\nيفز النبض في صدري", "answer": "عبدالمجيد عبدالله", "song_name": "احبك ليه"},
            {"lyrics": "سود العيون كبار والشامه حلوه\nشايل جمال الكون وباليني بلوه", "answer": "راشد الماجد", "song_name": "العيون السود"},
            {"lyrics": "لا تخاف من الزمان\nالزمان ماله امان\nخف من اللي كل املك\nفي يديه وتامنه", "answer": "اصالة نصري", "song_name": "لا تخاف"},
            {"lyrics": "وين انت ماهي مثلي\nوين انت دايم\nوين انت هالمرة على الفين\nوين انت", "answer": "رابح صقر", "song_name": "وين انت"},
            {"lyrics": "جننت قلبي بحب يلوي ذراعي\nلاهو بتايب ولا عبر تجاريبه\nامر الله اقوى احبك والعقل واعي", "answer": "ماجد المهندس", "song_name": "جننت قلبي"},
            {"lyrics": "سألوني الليل ليش ساهر\nقلت لهم القمر ساهر", "answer": "حسين الجسمي", "song_name": "سألوني الليل"},
            {"lyrics": "يا طير يا طاير يا رايح بلاد الخير\nسلم على الغالي وقل له انا كثير", "answer": "عبدالمجيد عبدالله", "song_name": "يا طير"},
            {"lyrics": "تعبت وانا انادي على النوم\nوالنوم ماله خبر يجيني", "answer": "راشد الماجد", "song_name": "تعبت"},
            {"lyrics": "قولي وداعا للجميع وتعالي\nقولي وداعا واتركي اللي راح", "answer": "عبدالمجيد عبدالله", "song_name": "قولي وداعا"},
            {"lyrics": "اه يا دنيا اه يا ناس\nجاني الحب يسأل عنك", "answer": "محمد عبده", "song_name": "اه يا دنيا"},
            {"lyrics": "حبيبي يا نور العين\nيا ساكن خيالي", "answer": "عمرو دياب", "song_name": "نور العين"},
            {"lyrics": "انا عايش يا ناس معاه في الجنة\nوحياتي كلها فرحة وسعادة", "answer": "محمد منير", "song_name": "انا عايش"},
            {"lyrics": "بكيت يوم فارقتني وبكيت\nدموعي سالت على خدي", "answer": "كاظم الساهر", "song_name": "بكيت"},
            {"lyrics": "احبك موت موت\nواموت فيك حبيبي", "answer": "ماجد المهندس", "song_name": "احبك موت"},
            {"lyrics": "على مودك انا جيت\nوعلى غلاك انا جيت", "answer": "طلال مداح", "song_name": "على مودك"},
            {"lyrics": "سلملي عليها لو تشوفها يا ريح\nقلها حبيبها دايم يذكرها", "answer": "ماجد المهندس", "song_name": "سلملي عليها"},
            {"lyrics": "عيونه سود وحواجبه سود\nوشعره اسود اسود", "answer": "اصالة نصري", "song_name": "عيونه سود"},
            {"lyrics": "يا غالي على قلبي\nيا اغلى من روحي", "answer": "عبدالمجيد عبدالله", "song_name": "يا غالي"},
            {"lyrics": "تملي معاك يا جميل\nوالله تملي معاك", "answer": "عمرو دياب", "song_name": "تملي معاك"},
            {"lyrics": "بحبك يا صاحبي يا اللي معايا\nيا سندي في الدنيا", "answer": "تامر حسني", "song_name": "بحبك يا صاحبي"},
            {"lyrics": "رجعت لي أيام الماضي معاك", "answer": "أم كلثوم", "song_name": "إنت عمري"},
            {"lyrics": "جلست والخوف بعينيها تتأمل فنجاني", "answer": "عبد الحليم حافظ", "song_name": "قارئة الفنجان"},
            {"lyrics": "أنا لحبيبي وحبيبي إلي", "answer": "فيروز", "song_name": "أنا لحبيبي"},
            {"lyrics": "عندك بحرية يا ريس", "answer": "وديع الصافي", "song_name": "عندك بحرية"},
            {"lyrics": "تملي معاك ولو حتى بعيد عني", "answer": "عمرو دياب", "song_name": "تملي معاك"},
            {"lyrics": "حبيبي يا كل الحياة اوعدني تبقى معايا", "answer": "تامر حسني", "song_name": "حبيبي يا كل الحياة"},
            {"lyrics": "مشاعر.. مشاعر جوايا من زمان", "answer": "شيرين عبد الوهاب", "song_name": "مشاعر"},
            {"lyrics": "قلبي بيسألني عنك دخلك طمني وينك", "answer": "وائل كفوري", "song_name": "البنت القوية"},
            {"lyrics": "يا بنات يا بنات", "answer": "نانسي عجرم", "song_name": "يا بنات"},
            {"lyrics": "قولي أحبك كي تزيد وسامتي", "answer": "كاظم الساهر", "song_name": "قولي أحبك"},
            {"lyrics": "قول عني ما تقول", "answer": "أحلام", "song_name": "قول عني ما تقول"},
            {"lyrics": "خذني إليك", "answer": "فضل شاكر", "song_name": "إليّ"},
            {"lyrics": "أنا قلبي عليك مش منك خايف أنا خوفي عليك", "answer": "زياد برجي", "song_name": "أنا قلبي عليك"},
            {"lyrics": "كيف أبيّن لك شعوري دون ما أحكي\nخابرك لمّاح لكن مالمحته\nلاتغرّك كثرة مزوحي وضحكي\nوالله إن قلبي لغيرك ما فتحته", "answer": "عايض", "song_name": "لماح"},
            {"lyrics": "اسخر لك غلا وتشوفني مقصر\nمعاك الحق ..\nوش الي يملي عيونك\nأنا ما عيش من دونك\nأحد ربي يجيبه لك حبيب\nويقدر يخونك", "answer": "عايض", "song_name": "إجرح"}
        ]

    def normalize_text(self, text):
        if not text:
            return ""
        text = text.strip().lower()
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ة', 'ه').replace('ى', 'ي')
        text = re.sub(r'[\u064B-\u065F]', '', text)
        text = re.sub(r'[^\w\s\u0600-\u06FF]', '', text)
        text = re.sub(r'\bال', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def start_game(self):
        self.current_question = 0
        self.hint_used = False
        take = min(self.max_questions, len(self.songs))
        self.remaining_songs = random.sample(self.songs, take)
        return self.next_question()

    def next_question(self):
        if not self.remaining_songs:
            self.current_song = None
            return TextSendMessage(text="انتهت الاسئلة 🎵")
        song_data = self.remaining_songs.pop(0)
        self.current_song = song_data
        self.correct_answer = song_data["answer"]
        self.hint_used = False
        self.current_question += 1
        return TextSendMessage(
            text=f"🎶 السؤال {self.current_question}/{self.max_questions}\n\n"
                 f"{song_data['lyrics']}\n\n"
                 f"خمن اسم الفنان 🎤\n"
                 f"▫️ اكتب 'لمح' أو 'تلميح' للتلميح 🔍\n"
                 f"▫️ اكتب 'جاوب' لعرض الإجابة 🎵"
        )

    def _make_hint(self):
        name = self.correct_answer.strip()
        if not name:
            return "🎵 تلميح: الاسم غير متاح حالياً."
        length_no_spaces = len(name.replace(" ", ""))
        first_letter = name.replace(" ", "")[0]
        word_count = len(name.split())
        if word_count == 1:
            words_text = "مكون من كلمة واحدة"
        elif word_count == 2:
            words_text = "مكون من كلمتين"
        else:
            words_text = f"مكون من {word_count} كلمات"
        return f"🎵 تلميح:\nيبدأ بحرف: {first_letter}\nعدد الحروف: {length_no_spaces}\n{words_text}"

    def check_answer(self, answer, user_id=None, display_name="لاعب"):
        if not self.current_song:
            return {'points': 0, 'won': False, 'response': TextSendMessage(text="🎮 لا يوجد سؤال حالياً")}

        ans = answer.strip().lower()
        if ans in ['لمح', 'تلميح']:
            if self.hint_used:
                return {'points': 0, 'won': False, 'response': TextSendMessage(text="🔍 تم استخدام التلميح مسبقاً")}
            self.hint_used = True
            return {'points': 0, 'won': False, 'response': TextSendMessage(text=self._make_hint())}

        if ans == 'جاوب':
            msg = f"🎤 الإجابة الصحيحة: {self.correct_answer}\n🎵 الأغنية: {self.current_song['song_name']}"
            next_q = self.next_question()
            return {'points': 0, 'won': False, 'response': TextSendMessage(text=f"{msg}\n\n{next_q.text}")}

        user_ans = self.normalize_text(answer)
        correct = self.normalize_text(self.correct_answer)
        if user_ans in correct or correct in user_ans:
            points = 10 if not self.hint_used else 5
            msg = f"👏 ممتاز {display_name}!\n+{points} نقاط 🎉"
            next_q = self.next_question()
            return {'points': points, 'won': True, 'response': TextSendMessage(text=f"{msg}\n\n{next_q.text}")}
        return {'points': 0, 'won': False, 'response': TextSendMessage(text="❌ خطأ! حاول مرة أخرى 🎶")}
