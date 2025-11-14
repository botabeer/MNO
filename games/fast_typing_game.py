from linebot.models import TextSendMessage
import random
import time
import re

def normalize_text(text):
    if not text:
        return ""
    text = text.strip().lower()
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    text = text.replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '')
    text = text.replace('ة', 'ه').replace('ى', 'ي')
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text

class FastTypingGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.all_sentences = [
            "اللهم استرني",
            "يا رب رحمتك",
            "الحمد لله دائمًا",
            "سبحان الله وبحمده",
            "اللهم اغفر لي",
            "يا رب لطفك",
            "حسبي الله ونعم الوكيل",
            "توكلت على الله",
            "اللهم فرجًا قريبًا",
            "يا رب ارزقني",
            "اللهم تمم بخير",
            "يا رب سددني",
            "اللهم اكتب لي الخير",
            "يا رب أعني",
            "اللهم هون علي",
            "اللهم ارفع همي",
            "يا رب كن معي",
            "اللهم اشف مرضانا",
            "يا رب رحمة",
            "اللهم اجبر قلبي",
            "ذكر الله راحة",
            "الصبر مفتاح الفرج",
            "العلم نور",
            "الوقت كالسيف",
            "الصدق منجاة",
            "الأمل حياة",
            "الرفق جميل",
            "التسامح راحة",
            "الغفران قوة",
            "العطاء بركة",
            "السكوت حكمة",
            "الابتسامة صدقة",
            "القناعة كنز",
            "الأخلاق أساس",
            "التواضع رفعة",
            "الهدوء نعمة",
            "النية الطيبة بركة",
            "الحياة تجارب",
            "الخير باقٍ",
            "الدنيا فانية",
            "الصمت راحة",
            "لا تيأس أبدًا",
            "توكل تكفي",
            "الله معنا",
            "اصبر تؤجر",
            "احسن الظن",
            "ابتسم وامضِ",
            "عامل بلطف",
            "سامح ترتاح",
            "الحب نقاء",
            "الوفاء جميل",
            "النية تصنع",
            "القلب أبيض",
            "الكلمة الطيبة نور",
            "الدعاء سلاح",
            "البساطة جمال",
            "العقل زينة",
            "الرحمة خلق",
            "الخير عادة",
            "الإيمان قوة",
            "الرضا جنة",
            "راحة بال",
            "يا رب يسر",
            "اللهم كفايتي",
            "ربي حسبي",
            "اللهم اهدني",
            "يا رب وفقني",
            "اللهم بارك لي",
            "رب اجعلني شاكرًا",
            "اللهم نور دربي",
            "يا رب حققها",
            "اللهم استجب",
            "يا رب اجعلها خيرة",
            "اللهم رحمتك بي",
            "يا رب سكينة",
            "اللهم يسر أمري",
            "اللهم اكتب أجري",
            "يا رب اقبض حزني",
            "اللهم اخلفني خيرًا",
            "يا رب احفظني",
            "اللهم كما أحب",
            "يا رب هداية",
            "اللهم بلطفك",
            "يا رب وفقنا",
            "اللهم سخر لي",
            "آمنت بالله",
            "اللهم تقبل مني",
            "ربي زدني",
            "استغفر الله العظيم",
            "سبحان الله",
            "الحمد لله",
            "لا إله إلا الله",
            "الله أكبر",
            "اللهم اجعلها بركة",
            "اللهم لا تخيبني",
            "رب وفقني",
            "ربي ارحمني",
            "اللهم يارب"
        ]
        
        self.questions = []
        self.current_sentence = None
        self.start_time = None
        self.question_number = 0
        self.total_questions = 5
        self.player_scores = {}
    
    def start_game(self):
        self.questions = random.sample(self.all_sentences, self.total_questions)
        self.question_number = 0
        self.player_scores = {}
        return self._next_question()
    
    def _next_question(self):
        self.question_number += 1
        self.current_sentence = self.questions[self.question_number - 1]
        self.start_time = time.time()
        return TextSendMessage(
            text=f"▪️ لعبة السرعة\n\nسؤال {self.question_number} من {self.total_questions}\n\nاكتب هذه الجملة بأسرع وقت:\n\n{self.current_sentence}\n\n⏱️ الوقت بدأ الآن"
        )
    
    def next_question(self):
        if self.question_number < self.total_questions:
            return self._next_question()
        return None
    
    def check_answer(self, answer, user_id, display_name):
        if not self.current_sentence or not self.start_time:
            return None
        
        elapsed_time = time.time() - self.start_time
        
        if normalize_text(answer) == normalize_text(self.current_sentence):
            if elapsed_time < 5:
                points = 30
            elif elapsed_time < 10:
                points = 25
            elif elapsed_time < 15:
                points = 20
            elif elapsed_time < 20:
                points = 15
            else:
                points = 10
            
            if user_id not in self.player_scores:
                self.player_scores[user_id] = {'name': display_name, 'score': 0}
            self.player_scores[user_id]['score'] += points
            
            if self.question_number < self.total_questions:
                response_text = f"▪️ صحيح {display_name}\n\n⏱️ الوقت: {elapsed_time:.2f} ثانية\n▫️ النقاط: {points}"
                return {
                    'response': TextSendMessage(text=response_text),
                    'points': points,
                    'correct': True,
                    'won': True,
                    'game_over': False,
                    'next_question': True
                }
            else:
                return self._end_game()
        
        return None
    
    def _end_game(self):
        if self.player_scores:
            sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
            winner = sorted_players[0][1]
            all_scores = [(data['name'], data['score']) for uid, data in sorted_players]
            
            from app import get_winner_card
            winner_card = get_winner_card(winner['name'], winner['score'], all_scores)
            
            return {
                'points': 0,
                'correct': False,
                'won': True,
                'game_over': True,
                'winner_card': winner_card
            }
        else:
            return {
                'response': TextSendMessage(text="انتهت اللعبة"),
                'points': 0,
                'correct': False,
                'won': False,
                'game_over': True
            }
