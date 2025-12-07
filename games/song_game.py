# games/song_game.py - Enhanced Song Game
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from games.game_helpers import (
    normalize_text, create_hint_text, create_winner_card, create_question_card
)


class SongGame:
    """
    لعبة تخمين الأغنية
    - 5 جولات
    - نقطة واحدة لكل إجابة صحيحة
    - أول إجابة فقط
    - تلميح: أول حرف وعدد الحروف
    - جاوب: الإجابة الصحيحة
    """

    SONGS=[
{'lyrics':'رجعت لي أيام الماضي معاك','singer':'أم كلثوم'},
{'lyrics':'جلست والخوف بعينيها تتأمل فنجاني','singer':'عبد الحليم حافظ'},
{'lyrics':'تملي معاك ولو حتى بعيد عني','singer':'عمرو دياب'},
{'lyrics':'يا بنات يا بنات','singer':'نانسي عجرم'},
{'lyrics':'قولي أحبك كي تزيد وسامتي','singer':'كاظم الساهر'},
{'lyrics':'أنا لحبيبي وحبيبي إلي','singer':'فيروز'},
{'lyrics':'حبيبي يا كل الحياة اوعدني تبقى معايا','singer':'تامر حسني'},
{'lyrics':'قلبي بيسألني عنك دخلك طمني وينك','singer':'وائل كفوري'},
{'lyrics':'كيف أبيّن لك شعوري دون ما أحكي','singer':'عايض'},
{'lyrics':'اسخر لك غلا وتشوفني مقصر','singer':'عايض'},
{'lyrics':'رحت عني ما قويت جيت لك لاتردني','singer':'عبدالمجيد عبدالله'},
{'lyrics':'خذني من ليلي لليلك','singer':'عبادي الجوهر'},
{'lyrics':'تدري كثر ماني من البعد مخنوق','singer':'راشد الماجد'},
{'lyrics':'انسى هالعالم ولو هم يزعلون','singer':'عباس ابراهيم'},
{'lyrics':'أنا عندي قلب واحد','singer':'حسين الجسمي'},
{'lyrics':'منوتي ليتك معي','singer':'محمد عبده'},
{'lyrics':'خلنا مني طمني عليك','singer':'نوال الكويتية'},
{'lyrics':'أحبك ليه أنا مدري','singer':'عبدالمجيد عبدالله'},
{'lyrics':'أمر الله أقوى أحبك والعقل واعي','singer':'ماجد المهندس'},
{'lyrics':'الحب يتعب من يدله والله في حبه بلاني','singer':'راشد الماجد'},
{'lyrics':'محد غيرك شغل عقلي شغل بالي','singer':'وليد الشامي'},
{'lyrics':'نكتشف مر الحقيقة بعد ما يفوت الأوان','singer':'أصالة'},
{'lyrics':'يا هي توجع كذبة اخباري تمام','singer':'أميمة طالب'},
{'lyrics':'احس اني لقيتك بس عشان تضيع مني','singer':'عبدالمجيد عبدالله'},
{'lyrics':'بردان أنا تكفى أبي احترق بدفا لعيونك','singer':'محمد عبده'},
{'lyrics':'أشوفك كل يوم وأروح وأقول نظرة ترد الروح','singer':'محمد عبده'},
{'lyrics':'في زحمة الناس صعبة حالتي','singer':'محمد عبده'},
{'lyrics':'اختلفنا مين يحب الثاني أكثر','singer':'محمد عبده'},
{'lyrics':'لبيه يا بو عيون وساع','singer':'محمد عبده'},
{'lyrics':'اسمحيلي يا الغرام العف','singer':'محمد عبده'},
{'lyrics':'سألوني الناس عنك يا حبيبي','singer':'فيروز'},
{'lyrics':'أنا لحبيبي وحبيبي إلي','singer':'فيروز'},
{'lyrics':'أحبك موت كلمة مالها تفسير','singer':'ماجد المهندس'},
{'lyrics':'جننت قلبي بحب يلوي ذراعي','singer':'ماجد المهندس'},
{'lyrics':'بديت أطيب بديت احس بك عادي','singer':'ماجد المهندس'},
{'lyrics':'من أول نظرة شفتك قلت هذا اللي تمنيته','singer':'ماجد المهندس'},
{'lyrics':'أنا بلياك إذا أرمش تنزل ألف دمعة','singer':'ماجد المهندس'},
{'lyrics':'عطشان يا برق السما','singer':'ماجد المهندس'},
{'lyrics':'هيجيلي موجوع دموعه ف عينه','singer':'تامر عاشور'},
{'lyrics':'تيجي نتراهن إن هيجي اليوم','singer':'تامر عاشور'},
{'lyrics':'خليني ف حضنك يا حبيبي','singer':'تامر عاشور'},
{'lyrics':'أريد الله يسامحني لأن أذيت نفسي','singer':'رحمة رياض'},
{'lyrics':'كون نصير أنا وياك نجمة بالسما','singer':'رحمة رياض'},
{'lyrics':'على طاري الزعل والدمعتين','singer':'أصيل هميم'},
{'lyrics':'يشبهك قلبي كنك القلب مخلوق','singer':'أصيل هميم'},
{'lyrics':'أحبه بس مو معناه اسمحله يجرح','singer':'أصيل هميم'},
{'lyrics':'المفروض أعوفك من زمان','singer':'أصيل هميم'},
{'lyrics':'ضعت منك وانهدم جسر التلاقي','singer':'أميمة طالب'},
{'lyrics':'بيان صادر من معاناة المحبة','singer':'أميمة طالب'},
{'lyrics':'أنا ودي إذا ودك نعيد الماضي','singer':'رابح صقر'},
{'lyrics':'مثل ما تحب ياروحي ألبي رغبتك','singer':'رابح صقر'},
{'lyrics':'كل ما بلل مطر وصلك ثيابي','singer':'رابح صقر'},
{'lyrics':'يراودني شعور إني أحبك أكثر من أول','singer':'راشد الماجد'},
{'lyrics':'أنا أكثر شخص بالدنيا يحبك','singer':'راشد الماجد'},
{'lyrics':'ليت العمر لو كان مليون مرة','singer':'راشد الماجد'},
{'lyrics':'تلمست لك عذر','singer':'راشد الماجد'},
{'lyrics':'عظيم إحساسي والشوق فيني','singer':'راشد الماجد'},
{'lyrics':'خذ راحتك ماعاد تفرق معي','singer':'راشد الماجد'},
{'lyrics':'قال الوداع ومقصده يجرح القلب','singer':'راشد الماجد'},
{'lyrics':'اللي لقى احبابه نسى اصحابه','singer':'راشد الماجد'},
{'lyrics':'واسع خيالك اكتبه أنا بكذبك معجبه','singer':'شمة حمدان'},
{'lyrics':'ما دريت إني أحبك ما دريت','singer':'شمة حمدان'},
{'lyrics':'حبيته بيني وبين نفسي','singer':'شيرين'},
{'lyrics':'كلها غيرانة بتحقد','singer':'شيرين'},
{'lyrics':'مشاعر تشاور تودع تسافر','singer':'شيرين'},
{'lyrics':'أنا مش بتاعت الكلام ده','singer':'شيرين'},
{'lyrics':'مقادير يا قلبي العنا مقادير','singer':'طلال مداح'},
{'lyrics':'ظلمتني والله قوي يجازيك','singer':'طلال مداح'},
{'lyrics':'فزيت من نومي أناديلك','singer':'ذكرى'},
{'lyrics':'ابد على حطة يدك','singer':'ذكرى'},
{'lyrics':'أنا لولا الغلا والمحبة','singer':'فؤاد عبدالواحد'},
{'lyrics':'كلمة ولو جبر خاطر','singer':'عبادي الجوهر'},
{'lyrics':'أحبك لو تكون حاضر','singer':'عبادي الجوهر'},
{'lyrics':'إلحق عيني إلحق','singer':'وليد الشامي'},
{'lyrics':'يردون قلت لازم يردون','singer':'وليد الشامي'},
{'lyrics':'ولهان أنا ولهان','singer':'وليد الشامي'},
{'lyrics':'اقولها كبر عن الدنيا حبيبي','singer':'وليد الشامي'},
{'lyrics':'أنا استاهل وداع أفضل وداع','singer':'نوال الكويتية'},
{'lyrics':'لقيت روحي بعد ما لقيتك','singer':'نوال الكويتية'},
{'lyrics':'غريبة الناس غريبة الدنيا','singer':'وائل جسار'},
{'lyrics':'اعذريني يوم زفافك','singer':'وائل جسار'},
{'lyrics':'ماعاد يمديني ولا عاد يمديك','singer':'عبدالمجيد عبدالله'},
{'lyrics':'يا بعدهم كلهم يا سراجي بينهم','singer':'عبدالمجيد عبدالله'},
{'lyrics':'حتى الكره احساس','singer':'عبدالمجيد عبدالله'},
{'lyrics':'استكثرك وقتي علي','singer':'عبدالمجيد عبدالله'},
{'lyrics':'ياما حاولت الفراق وما قويت','singer':'عبدالمجيد عبدالله'}
]


    def __init__(self, line_bot_api, total_questions=5):
        self.line_bot_api = line_bot_api
        self.total_questions = total_questions
        self.questions = []
        self.current_question = 0
        self.player_scores = {}
        self.question_answered = False
        self.registered = set()

    def register_player(self, user_id: str, display_name: str):
        """تسجيل لاعب في اللعبة"""
        self.registered.add(user_id)
        return True

    def start_game(self):
        """بدء اللعبة"""
        # Select random songs
        self.questions = random.sample(
            self.SONGS, 
            min(self.total_questions, len(self.SONGS))
        )
        self.current_question = 0
        self.player_scores = {}
        self.question_answered = False
        
        return self._show_question()

    def _show_question(self):
        """عرض السؤال الحالي"""
        song = self.questions[self.current_question]
        lyrics = song['lyrics']
        
        question_text = f"{lyrics}\n\nمن المغني؟"
        
        return FlexMessage(
            alt_text="لعبة الأغنية",
            contents=FlexContainer.from_dict(
                create_question_card(
                    question_text,
                    self.current_question + 1,
                    self.total_questions,
                    "لعبة الأغنية"
                )
            )
        )

    def next_question(self):
        """الانتقال للسؤال التالي"""
        self.current_question += 1
        
        if self.current_question < self.total_questions:
            self.question_answered = False
            return self._show_question()
        
        return None

    def check_answer(self, answer: str, user_id: str, display_name: str):
        """فحص الإجابة"""
        # Ignore non-registered players
        if user_id not in self.registered:
            return None

        # If question already answered, ignore
        if self.question_answered:
            return None

        song = self.questions[self.current_question]
        answer_lower = answer.strip().lower()

        # Handle hint request
        if answer_lower in ['لمح', 'تلميح']:
            hint = create_hint_text(song['singer'])
            return {
                'response': TextMessage(text=hint),
                'points': 0,
                'correct': False
            }

        # Handle answer reveal
        if answer_lower in ['جاوب', 'الجواب', 'الحل']:
            self.question_answered = True
            
            if self.current_question + 1 < self.total_questions:
                return {
                    'response': TextMessage(text=f"الإجابة: {song['singer']}"),
                    'points': 0,
                    'correct': False,
                    'next_question': True
                }
            else:
                # Last question - end game
                return self._end_game()

        # Check if answer is correct
        if normalize_text(answer) == normalize_text(song['singer']):
            # First correct answer
            self.player_scores.setdefault(user_id, {
                'name': display_name,
                'score': 0
            })
            self.player_scores[user_id]['score'] += 1
            self.question_answered = True

            if self.current_question + 1 < self.total_questions:
                # More questions remaining
                return {
                    'response': TextMessage(
                        text=f"إجابة صحيحة {display_name}\n+1 نقطة"
                    ),
                    'points': 1,
                    'correct': True,
                    'next_question': True
                }
            else:
                # Last question - end game
                return self._end_game()

        return None

    def _end_game(self):
        """إنهاء اللعبة وإعلان الفائز"""
        if not self.player_scores:
            return {
                'response': TextMessage(text="انتهت اللعبة بدون فائز"),
                'points': 0,
                'correct': False,
                'game_over': True
            }

        # Sort players by score
        sorted_players = sorted(
            self.player_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )

        winner = sorted_players[0][1]

        return {
            'response': FlexMessage(
                alt_text="نتائج اللعبة",
                contents=FlexContainer.from_dict(
                    create_winner_card(winner, sorted_players, "الأغنية")
                )
            ),
            'points': winner['score'],
            'correct': True,
            'won': True,
            'game_over': True
        }
