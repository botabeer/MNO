from linebot.models import TextSendMessage, FlexSendMessage
import random
import re
from constants import COLORS

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

def normalize_text(text):
    if not text:
        return ""
    text = text.strip().lower()
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    text = text.replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '')
    text = text.replace('ة', 'ه').replace('ى', 'ي')
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'\s+', '', text)
    return text

class SongGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.songs = SONGS
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.answered_users = set()
        self.hints_used = {}

    def start_game(self):
        self.questions = random.sample(self.songs, min(self.total_questions, len(self.songs)))
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        self.hints_used = {}
        return self._show_question()

    def _show_question(self):
        song = self.questions[self.current_question]
        progress = f"{self.current_question + 1}/{self.total_questions}"
        
        return FlexSendMessage(
            alt_text="لعبه الاغنيه",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "لعبة الأغنية", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                        {"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": "السؤال", "size": "xs", "color": COLORS['text_light'], "flex": 0}, {"type": "text", "text": progress, "size": "xs", "color": COLORS['primary'], "weight": "bold", "align": "end"}], "margin": "lg"},
                        {"type": "separator", "margin": "md", "color": COLORS['border']},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": song['lyrics'], "size": "lg", "color": COLORS['text_dark'], "wrap": True, "weight": "bold", "align": "center"}, {"type": "text", "text": "من المغني؟", "size": "md", "color": COLORS['primary'], "margin": "md", "align": "center"}], "margin": "lg", "spacing": "sm"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "box", "layout": "horizontal", "contents": [{"type": "button", "action": {"type": "message", "label": "لمح", "text": "لمح"}, "style": "secondary", "height": "sm", "flex": 1}, {"type": "button", "action": {"type": "message", "label": "جاوب", "text": "جاوب"}, "style": "secondary", "height": "sm", "flex": 1}], "spacing": "sm", "margin": "lg"},
                        {"type": "box", "layout": "horizontal", "contents": [{"type": "button", "action": {"type": "message", "label": "إيقاف", "text": "إيقاف"}, "style": "secondary", "height": "sm", "flex": 1}, {"type": "button", "action": {"type": "message", "label": "تسجيل", "text": "تسجيل"}, "style": "secondary", "height": "sm", "flex": 1}], "spacing": "sm", "margin": "sm"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.answered_users = set()
            self.hints_used = {}
            return self._show_question()
        return None

    def check_answer(self, answer, user_id, display_name):
        if user_id in self.answered_users:
            return None

        song = self.questions[self.current_question]

        if answer in ['لمح', 'تلميح']:
            if user_id not in self.hints_used:
                self.hints_used[user_id] = True
                return {'response': TextSendMessage(text=f"يبدأ بحرف: {song['singer'][0]}\nعدد الحروف: {len(song['singer'])}"), 'points': 0, 'correct': False}
            return {'response': TextSendMessage(text="استخدمت التلميح مسبقاً"), 'points': 0, 'correct': False}

        if answer in ['جاوب', 'الجواب']:
            self.answered_users.add(user_id)
            if self.current_question + 1 < self.total_questions:
                return {'response': TextSendMessage(text=f"الإجابة: {song['singer']}"), 'points': 0, 'correct': False, 'next_question': True}
            return self._end_game()

        if normalize_text(answer) == normalize_text(song['singer']):
            points = 1
            self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})
            self.player_scores[user_id]['score'] += points
            self.answered_users.add(user_id)

            if self.current_question + 1 < self.total_questions:
                return {'response': TextSendMessage(text=f"إجابة صحيحة {display_name}\n+{points} نقطة"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
            return self._end_game()

        return None

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextSendMessage(text="انتهت اللعبة"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}

        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        
        players_contents = []
        
        for i, p in enumerate(sorted_players[:5]):
            rank = f"{i+1}."
            players_contents.append({"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": rank, "size": "sm", "flex": 0}, {"type": "text", "text": p[1]['name'], "size": "sm", "color": COLORS['text_dark'], "flex": 3, "margin": "sm"}, {"type": "text", "text": f"{p[1]['score']} نقطة", "size": "sm", "color": COLORS['primary'], "weight": "bold", "align": "end", "flex": 2}], "margin": "md" if i > 0 else "sm"})

        winner_card = FlexSendMessage(
            alt_text="نتائج اللعبة",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "انتهت اللعبة", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "الفائز", "size": "sm", "color": COLORS['text_light'], "align": "center"}, {"type": "text", "text": winner['name'], "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center", "margin": "xs"}, {"type": "text", "text": f"{winner['score']} نقطة", "size": "lg", "color": COLORS['success'], "align": "center", "margin": "xs"}], "margin": "lg"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "النتائج", "size": "md", "color": COLORS['text_dark'], "weight": "bold"}, *players_contents], "margin": "lg"},
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {"type": "button", "action": {"type": "message", "label": "إعادة اللعب", "text": "اغنيه"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "lg"}
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

        return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
