from games.base_game import BaseGame, normalize_text
from constants import COLORS
import random

SONGS = [
    {'lyrics': 'رجعت لي أيام الماضي معاك', 'singer': 'أم كلثوم'},
    {'lyrics': 'جلست والخوف بعينيها تتأمل فنجاني', 'singer': 'عبد الحليم حافظ'},
    {'lyrics': 'تملي معاك ولو حتى بعيد عني', 'singer': 'عمرو دياب'},
    {'lyrics': 'يا بنات يا بنات', 'singer': 'نانسي عجرم'},
    {'lyrics': 'قولي أحبك كي تزيد وسامتي', 'singer': 'كاظم الساهر'},
    {'lyrics': 'أنا لحبيبي وحبيبي إلي', 'singer': 'فيروز'},
    {'lyrics': 'حبيبي يا كل الحياة اوعدني تبقى معايا', 'singer': 'تامر حسني'},
    {'lyrics': 'قلبي بيسألني عنك دخلك طمني وينك', 'singer': 'وائل كفوري'},
    {'lyrics': 'كيف أبيّن لك شعوري دون ما أحكي', 'singer': 'عايض'},
    {'lyrics': 'اسخر لك غلا وتشوفني مقصر', 'singer': 'عايض'},
    {'lyrics': 'رحت عني ما قويت جيت لك لاتردني', 'singer': 'عبدالمجيد عبدالله'},
    {'lyrics': 'خذني من ليلي لليلك', 'singer': 'عبادي الجوهر'},
    {'lyrics': 'تدري كثر ماني من البعد مخنوق', 'singer': 'راشد الماجد'},
    {'lyrics': 'انسى هالعالم ولو هم يزعلون', 'singer': 'عباس ابراهيم'},
    {'lyrics': 'أنا عندي قلب واحد', 'singer': 'حسين الجسمي'},
    {'lyrics': 'منوتي ليتك معي', 'singer': 'محمد عبده'},
    {'lyrics': 'خلنا مني طمني عليك', 'singer': 'نوال الكويتية'},
    {'lyrics': 'أحبك ليه أنا مدري', 'singer': 'عبدالمجيد عبدالله'},
    {'lyrics': 'أمر الله أقوى أحبك والعقل واعي', 'singer': 'ماجد المهندس'},
    {'lyrics': 'الحب يتعب من يدله والله في حبه بلاني', 'singer': 'راشد الماجد'},
    {'lyrics': 'محد غيرك شغل عقلي شغل بالي', 'singer': 'وليد الشامي'},
    {'lyrics': 'نكتشف مر الحقيقة بعد ما يفوت الأوان', 'singer': 'أصالة'},
    {'lyrics': 'يا هي توجع كذبة اخباري تمام', 'singer': 'أميمة طالب'},
    {'lyrics': 'احس اني لقيتك بس عشان تضيع مني', 'singer': 'عبدالمجيد عبدالله'},
    {'lyrics': 'بردان أنا تكفى أبي احترق بدفا لعيونك', 'singer': 'محمد عبده'},
    {'lyrics': 'أشوفك كل يوم وأروح وأقول نظرة ترد الروح', 'singer': 'محمد عبده'},
    {'lyrics': 'في زحمة الناس صعبة حالتي', 'singer': 'محمد عبده'},
    {'lyrics': 'اختلفنا مين يحب الثاني أكثر', 'singer': 'محمد عبده'},
    {'lyrics': 'لبيه يا بو عيون وساع', 'singer': 'محمد عبده'},
    {'lyrics': 'اسمحيلي يا الغرام العف', 'singer': 'محمد عبده'}
]

class SongGame(BaseGame):
    """لعبة الأغنية - خمن المغني من كلمات الأغنية"""
    
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, total_questions=5)
        self.songs = SONGS
    
    def _load_questions(self):
        """تحميل أسئلة الأغاني"""
        return random.sample(self.songs, min(self.total_questions, len(self.songs)))
    
    def _get_correct_answer(self, question):
        """الحصول على المغني الصحيح"""
        return question['singer']
    
    def _get_game_name(self):
        """اسم اللعبة"""
        return "لعبة الأغنية"
    
    def _get_restart_command(self):
        """أمر إعادة اللعب"""
        return "اغنيه"
    
    def _build_question_content(self, question):
        """بناء محتوى السؤال مخصص للأغاني"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": question['lyrics'],
                    "size": "lg",
                    "color": COLORS['text_dark'],
                    "wrap": True,
                    "weight": "bold",
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": "من المغني",
                    "size": "md",
                    "color": COLORS['primary'],
                    "margin": "md",
                    "align": "center"
                }
            ],
            "margin": "lg",
            "spacing": "sm"
        }
