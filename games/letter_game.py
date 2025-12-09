from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from constants import THEMES
from games.game_helpers import normalize_text, create_game_header, create_progress_box, create_separator, create_winner_card
from database import Database

class LetterGame:
    """لعبة حروف - من متجر ديجيز"""
    
    def __init__(self, line_bot_api, total_questions=5):
        self.line_bot_api = line_bot_api
        self.total_questions = total_questions
        self.questions = []
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        self.registered = set()
        
        self.all_letters = {
            'ا': ['ادم', 'اثينا', 'الجزائر', 'اسمرة', 'ابوبكر', 'اسيا', 'اسد'],
            'ب': ['بغداد', 'بكين', 'بيروت', 'برلين', 'باريس', 'بقرة', 'ببغاء'],
            'ت': ['تونس', 'تايبيه', 'تبليسي', 'تيرانا', 'تالين', 'تمساح'],
            'ث': ['ثعلب', 'ثوم', 'ثعبان', 'ثريد', 'ثور'],
            'ج': ['جيبوتي', 'جدة', 'جمل', 'جربوع', 'جراد'],
            'ح': ['حلب', 'حماة', 'حائل', 'حمص', 'حج', 'حوت'],
            'خ': ['خرطوم', 'خبر', 'خميس مشيط', 'خندق', 'خنساء'],
            'د': ['دبلن', 'دمشق', 'دبي', 'دوحة', 'دكار', 'دب'],
            'ذ': ['ذئب', 'ذهب', 'ذرة', 'ذباب', 'ذقن'],
            'ر': ['روما', 'روسيا', 'ريكيافيك', 'رز', 'راكون'],
            'ز': ['زغرب', 'زيمبابوي', 'زنجبار', 'زحل', 'زرافة'],
            'س': ['سلحفاة', 'سنجاب', 'سلطنة عمان', 'سمك', 'ستوكهولم'],
            'ش': ['شرم الشيخ', 'شيتا', 'شارقة', 'شنغهاي', 'شمبانزي'],
            'ص': ['صنعاء', 'صقر', 'صبار', 'صيف', 'صحراء'],
            'ض': ['ضفدع', 'ضابط', 'ضرس العقل', 'ضحى', 'ضبع'],
            'ط': ['طاجيكستان', 'طهر عربي', 'طاجين', 'طاووس', 'طلح'],
            'ظ': ['ظلم', 'ظهر', 'ظبي', 'ظمأ', 'ظفر'],
            'ع': ['عسل', 'عين', 'عمان', 'عقل', 'عنب'],
            'غ': ['غور الاردن', 'غزال', 'غينيا', 'غراب', 'غرناطة'],
            'ف': ['فنلندا', 'فرنسا', 'فيل', 'فهد', 'فارس'],
            'ق': ['قطر', 'قاهرة', 'قسنطينة', 'قنفذ', 'قمح'],
            'ك': ['كوالالمبور', 'كابول', 'كييف', 'كمباال', 'كنغر'],
            'ل': ['ليرة لبنانية', 'ليمون', 'لحاء', 'لوحة', 'ليثيوم'],
            'م': ['مخ', 'مرسيدس', 'معدة', 'ميكروفون', 'مانجو'],
            'ن': ['نيل', 'نسر', 'نمر', 'نور', 'نقود'],
            'ه': ['هوليوود', 'هاني شاكر', 'هيرميس', 'هرم'],
            'و': ['ويندسر', 'وداع للامة', 'ويتني هيوستن', 'ورد'],
            'ي': ['يوم', 'يد', 'يقين', 'يسار', 'يمين']
        }
    
    def register_player(self, uid, name):
        self.registered.add(uid)
        return True
    
    def start_game(self):
        available_letters = list(self.all_letters.keys())
        selected_letters = random.sample(available_letters, min(self.total_questions, len(available_letters)))
        self.questions = [{'letter': letter, 'answers': self.all_letters[letter]} for letter in selected_letters]
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        return self._show_question()
    
    def _show_question(self, theme="light"):
        colors = THEMES.get(theme, THEMES["light"])
        question = self.questions[self.current_question]
        letter = question['letter']
        
        contents = [
            create_game_header("لعبة حروف", "اذكر كلمة تبدا بالحرف", theme=theme),
            create_progress_box(self.current_question + 1, self.total_questions, theme=theme),
            create_separator(theme=theme),
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": letter,
                        "size": "5xl",
                        "color": colors['primary'],
                        "align": "center",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "اكتب اي كلمة تبدا بهذا الحرف",
                        "size": "sm",
                        "color": colors['text_dark'],
                        "align": "center",
                        "wrap": True,
                        "margin": "md"
                    }
                ],
                "margin": "lg"
            },
            create_separator(theme=theme),
            {
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "لمح", "text": "لمح"},
                        "style": "secondary",
                        "height": "sm"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "جاوب", "text": "جاوب"},
                        "style": "secondary",
                        "height": "sm",
                        "color": colors['warning']
                    }
                ]
            }
        ]
        
        return FlexMessage(
            alt_text="لعبة حروف",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": contents,
                    "backgroundColor": colors['card_bg'],
                    "paddingAll": "18px"
                }
            })
        )
    
    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.answered_users = set()
            return self._show_question()
        return None
    
    def check_answer(self, text, user_id, display_name):
        if user_id not in self.registered:
            return None
        if user_id in self.answered_users:
            return None
        
        question = self.questions[self.current_question]
        letter = question['letter']
        answers = question['answers']
        
        txt = text.strip().lower()
        theme = Database.get_user_theme(user_id)
        
        if txt in ['لمح', 'تلميح']:
            sample = answers[0] if answers else "كلمة"
            return {
                'response': TextMessage(text=f"تلميح: {sample}"),
                'points': 0,
                'correct': False
            }
        
        if txt in ['جاوب', 'الجواب', 'الحل']:
            self.answered_users.add(user_id)
            examples = ' - '.join(answers[:3])
            if self.current_question + 1 < self.total_questions:
                return {
                    'response': TextMessage(text=f"بعض الاجابات:\n{examples}"),
                    'points': 0,
                    'correct': False,
                    'next_question': True
                }
            return self._end_game(user_id)
        
        normalized = normalize_text(text)
        
        if normalized.startswith(normalize_text(letter)):
            self.answered_users.add(user_id)
            self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})
            self.player_scores[user_id]['score'] += 1
            
            if self.current_question + 1 < self.total_questions:
                return {
                    'response': TextMessage(text=f"اجابة صحيحة {display_name}\n+1 نقطة"),
                    'points': 1,
                    'correct': True,
                    'next_question': True
                }
            return self._end_game(user_id)
        
        return None
    
    def _end_game(self, user_id):
        theme = Database.get_user_theme(user_id)
        
        if not self.player_scores:
            return {
                'response': TextMessage(text="انتهت اللعبة"),
                'points': 0,
                'correct': False,
                'game_over': True
            }
        
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        
        return {
            'response': FlexMessage(
                alt_text="نتائج اللعبة",
                contents=FlexContainer.from_dict(create_winner_card(winner, sorted_players, "لعبة حروف", theme=theme))
            ),
            'points': winner['score'],
            'correct': True,
            'won': True,
            'game_over': True
        }
