"""
لعبة الذكاء - IQ Game
أسئلة ذكاء منطقية ورياضية
"""

from linebot.models import TextSendMessage
import random
import logging

logger = logging.getLogger(__name__)


class IQGame:
    """لعبة أسئلة الذكاء"""
    
    def __init__(self, line_bot_api, use_ai=False, get_api_key=None, switch_key=None):
        self.line_bot_api = line_bot_api
        self.current_question = None
        self.hint_used = False
        
        # 50 سؤال ذكاء متنوع
        self.questions = [
            {
                'question': 'ما هو الشيء الذي يمشي بلا رجلين ويبكي بلا عينين؟',
                'answer': ['السحاب', 'سحاب', 'الغيم', 'غيم'],
                'hint': 'موجود في السماء'
            },
            {
                'question': 'له رأس ولا عين له، وهي لها عين ولا رأس لها، ما هما؟',
                'answer': ['الدبوس والابرة', 'دبوس وابرة', 'ابرة ودبوس'],
                'hint': 'أدوات خياطة'
            },
            {
                'question': 'شيء اذا اخذت منه كبر واذا اضفت اليه صغر؟',
                'answer': ['الحفرة', 'حفرة'],
                'hint': 'في الأرض'
            },
            {
                'question': 'ما هو الشيء الذي كلما زاد نقص؟',
                'answer': ['العمر', 'عمر'],
                'hint': 'مرتبط بالزمن'
            },
            {
                'question': 'له اسنان ولا يعض؟',
                'answer': ['المشط', 'مشط'],
                'hint': 'تستخدمه للشعر'
            },
            {
                'question': 'ما هو الشيء الذي يكتب ولا يقرأ؟',
                'answer': ['القلم', 'قلم'],
                'hint': 'أداة كتابة'
            },
            {
                'question': 'شيء له اربع ارجل ولا يستطيع المشي؟',
                'answer': ['الكرسي', 'كرسي', 'الطاولة', 'طاولة'],
                'hint': 'أثاث'
            },
            {
                'question': 'ما هو الشيء الذي يخترق الزجاج ولا يكسره؟',
                'answer': ['الضوء', 'ضوء'],
                'hint': 'يأتي من الشمس'
            },
            {
                'question': 'اذا كان اليوم الثلاثاء، ما هو اليوم بعد غد؟',
                'answer': ['الخميس', 'خميس'],
                'hint': 'اليوم الخامس من الأسبوع'
            },
            {
                'question': '5 + 5 × 5 = ؟',
                'answer': ['30', '٣٠'],
                'hint': 'الضرب قبل الجمع'
            },
            {
                'question': 'كم عدد اصابع اليدين والرجلين معا؟',
                'answer': ['20', '٢٠', 'عشرون'],
                'hint': '10 + 10'
            },
            {
                'question': 'ما هو الشيء الذي تراه في الليل 3 مرات وفي النهار مرة واحدة؟',
                'answer': ['حرف اللام', 'اللام', 'ل'],
                'hint': 'حرف من الحروف'
            },
            {
                'question': 'اخت خالك وليست خالتك من تكون؟',
                'answer': ['امي', 'امك', 'الام', 'ام'],
                'hint': 'أقرب الناس لك'
            },
            {
                'question': 'ما هو الشيء الذي يسمع بلا اذن ويتكلم بلا لسان؟',
                'answer': ['الهاتف', 'هاتف', 'التلفون', 'تلفون'],
                'hint': 'تستخدمه للاتصال'
            },
            {
                'question': 'شيء موجود في السماء اذا اضفت اليه حرفا اصبح في الارض؟',
                'answer': ['نجم ومنجم', 'نجم', 'منجم'],
                'hint': 'أضف حرف الميم'
            },
            {
                'question': 'ما هو الشيء الذي يقرصك ولا تراه؟',
                'answer': ['الجوع', 'جوع'],
                'hint': 'شعور في المعدة'
            },
            {
                'question': 'حيوان يبدأ اسمه بحرف الدال؟',
                'answer': ['دب', 'ديك', 'دجاجة', 'دولفين'],
                'hint': 'حيوان كبير او صغير'
            },
            {
                'question': 'كم عدد ايام السنة الميلادية؟',
                'answer': ['365', '٣٦٥'],
                'hint': 'أكثر من 300'
            },
            {
                'question': 'ما هو اطول نهر في العالم؟',
                'answer': ['النيل', 'نيل', 'نهر النيل'],
                'hint': 'في افريقيا'
            },
            {
                'question': 'كم عدد الوان قوس قزح؟',
                'answer': ['7', '٧', 'سبعة'],
                'hint': 'رقم الحظ'
            },
            {
                'question': 'ما هو الحيوان الذي ينام واحدى عينيه مفتوحة؟',
                'answer': ['الدولفين', 'دولفين'],
                'hint': 'حيوان بحري ذكي'
            },
            {
                'question': 'شيء له عنق وليس له رأس؟',
                'answer': ['الزجاجة', 'زجاجة', 'القارورة'],
                'hint': 'تحفظ فيها السوائل'
            },
            {
                'question': '10 - 5 + 3 = ؟',
                'answer': ['8', '٨', 'ثمانية'],
                'hint': 'بين 7 و 9'
            },
            {
                'question': 'ما هو الشيء الذي اسمه على لونه؟',
                'answer': ['البيضة', 'بيضة', 'البرتقال', 'برتقال'],
                'hint': 'طعام'
            },
            {
                'question': 'كم عدد اشهر السنة الهجرية؟',
                'answer': ['12', '١٢', 'اثنا عشر'],
                'hint': 'دزينة'
            },
            {
                'question': 'ما هي عاصمة السعودية؟',
                'answer': ['الرياض', 'رياض'],
                'hint': 'مدينة كبيرة'
            },
            {
                'question': 'حيوان ملك الغابة؟',
                'answer': ['الاسد', 'اسد'],
                'hint': 'مفترس'
            },
            {
                'question': 'كم عدد الصلوات المفروضة في اليوم؟',
                'answer': ['5', '٥', 'خمس', 'خمسة'],
                'hint': 'اقل من 6'
            },
            {
                'question': '2 × 6 = ؟',
                'answer': ['12', '١٢', 'اثنا عشر'],
                'hint': 'ضعف 6'
            },
            {
                'question': 'ما هو اكبر كوكب في المجموعة الشمسية؟',
                'answer': ['المشتري', 'مشتري'],
                'hint': 'كوكب ضخم'
            },
            {
                'question': 'شيء يحملك وانت تحمله؟',
                'answer': ['الحذاء', 'حذاء'],
                'hint': 'في قدمك'
            },
            {
                'question': 'ما هو الشيء الذي يدور حول البيت دون ان يتحرك؟',
                'answer': ['السور', 'سور', 'الجدار'],
                'hint': 'حول المنزل'
            },
            {
                'question': 'كم عدد قارات العالم؟',
                'answer': ['7', '٧', 'سبع', 'سبعة'],
                'hint': 'اقل من 10'
            },
            {
                'question': 'ما هو اصغر عدد؟',
                'answer': ['صفر', '0', '٠'],
                'hint': 'قبل الواحد'
            },
            {
                'question': 'حيوان يعطينا الحليب؟',
                'answer': ['البقرة', 'بقرة', 'الماعز', 'ماعز'],
                'hint': 'في المزرعة'
            },
            {
                'question': 'ما هو الشيء الذي له قلب ولا يحب؟',
                'answer': ['الشجرة', 'شجرة'],
                'hint': 'نبات'
            },
            {
                'question': '3 × 3 = ؟',
                'answer': ['9', '٩', 'تسعة'],
                'hint': '3 + 3 + 3'
            },
            {
                'question': 'ما هو الحيوان الذي له سنام؟',
                'answer': ['الجمل', 'جمل'],
                'hint': 'سفينة الصحراء'
            },
            {
                'question': 'شيء يمكنك ان تمسكه بيدك اليمنى ولا يمكنك ان تمسكه بيدك اليسرى؟',
                'answer': ['يدك اليمنى', 'اليد اليمنى'],
                'hint': 'جزء من جسمك'
            },
            {
                'question': 'كم عدد فصول السنة؟',
                'answer': ['4', '٤', 'اربعة', 'اربع'],
                'hint': 'ربيع صيف خريف شتاء'
            },
            {
                'question': '20 ÷ 5 = ؟',
                'answer': ['4', '٤', 'اربعة'],
                'hint': 'ربع عشرين'
            },
            {
                'question': 'ما هو الطائر الذي لا يطير؟',
                'answer': ['النعامة', 'نعامة'],
                'hint': 'طائر كبير'
            },
            {
                'question': 'شيء له جناحان ولا يطير؟',
                'answer': ['الطاحونة', 'طاحونة', 'المروحة'],
                'hint': 'يدور'
            },
            {
                'question': 'ما هي اكبر دولة في العالم من حيث المساحة؟',
                'answer': ['روسيا', 'روسيه'],
                'hint': 'دولة كبيرة جدا'
            },
            {
                'question': '1 + 1 = ؟',
                'answer': ['2', '٢', 'اثنان'],
                'hint': 'سهل جدا'
            },
            {
                'question': 'ما هو الشيء الذي يجري ولا يمشي؟',
                'answer': ['الماء', 'ماء', 'النهر'],
                'hint': 'سائل'
            },
            {
                'question': 'حيوان يضرب به المثل في الذكاء؟',
                'answer': ['الثعلب', 'ثعلب'],
                'hint': 'ماكر'
            },
            {
                'question': 'كم عدد اضلاع المربع؟',
                'answer': ['4', '٤', 'اربعة'],
                'hint': 'شكل هندسي'
            },
            {
                'question': 'ما هو اسرع حيوان بري؟',
                'answer': ['الفهد', 'فهد'],
                'hint': ' يبدى بحرف ف'
            },
            {
                'question': 'شيء بينك وبين ايران؟',
                'answer': ['حرف الياء', 'الياء', 'ي'],
                'hint': 'حرف'
            }
        ]
    
    def start_game(self):
        """بدء سؤال جديد"""
        self.current_question = random.choice(self.questions)
        self.hint_used = False
        
        return TextSendMessage(
            text=f"سؤال ذكاء:\n\n{self.current_question['question']}\n\n"
                 f"لمح - للحصول على تلميح\n"
                 f"جاوب - لعرض الاجابة"
        )
    
    def check_answer(self, answer, user_id, display_name):
        """فحص الإجابة"""
        if not self.current_question:
            return None
        
        answer_normalized = answer.strip().lower()
        
        # أوامر خاصة
        if answer_normalized in ['لمح', 'تلميح']:
            self.hint_used = True
            return {
                'points': 0,
                'won': False,
                'response': TextSendMessage(
                    text=f"تلميح: {self.current_question['hint']}"
                )
            }
        
        if answer_normalized in ['جاوب', 'استسلم']:
            correct = self.current_question['answer'][0]
            return {
                'points': 0,
                'won': False,
                'game_over': False,
                'response': TextSendMessage(
                    text=f"الاجابة الصحيحة:\n{correct}"
                )
            }
        
        # فحص الإجابة
        if answer_normalized in [a.lower() for a in self.current_question['answer']]:
            points = 5 if not self.hint_used else 3
            return {
                'points': points,
                'won': True,
                'game_over': False,
                'response': TextSendMessage(
                    text=f"ممتاز {display_name}!\n\nالنقاط: +{points}"
                )
            }
        else:
            return {
                'points': 0,
                'won': False,
                'response': TextSendMessage(text="خطأ! حاول مرة اخرى")
            }
