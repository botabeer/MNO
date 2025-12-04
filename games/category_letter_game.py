from linebot.models import TextSendMessage, FlexSendMessage
import random
import re
from constants import COLORS

def normalize_text(text):
    if not text:
        return ""
    text = text.strip().lower()
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '').replace('ة', 'ه').replace('ى', 'ي')
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'\s+', '', text)
    return text

class CategoryLetterGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.challenges = [
            {"category": "المطبخ", "letter": "ق", "answers": ["قدر", "قلايه", "قهوه", "قنينه", "قباقيب"]},
            {"category": "حيوان", "letter": "ب", "answers": ["بطه", "بقره", "ببغاء", "بومه", "بعير"]},
            {"category": "فاكهه", "letter": "ت", "answers": ["تفاح", "توت", "تمر", "تين", "ترنج"]},
            {"category": "خضار", "letter": "ب", "answers": ["بصل", "بطاطس", "باذنجان", "بقدونس", "بروكلي"]},
            {"category": "بلاد", "letter": "س", "answers": ["سعوديه", "سوريا", "سودان", "سويسرا", "سويد"]},
            {"category": "اسم ولد", "letter": "م", "answers": ["محمد", "مصطفى", "مالك", "ماجد", "معاذ"]},
            {"category": "اسم بنت", "letter": "ر", "answers": ["ريم", "رنا", "رهف", "رغد", "رزان"]},
            {"category": "مهنه", "letter": "ط", "answers": ["طبيب", "طباخ", "طيار", "طالب", "طحان"]},
            {"category": "رياضه", "letter": "ك", "answers": ["كره", "كاراتيه", "كريكت", "كرلنج", "كرة سلة"]},
            {"category": "لون", "letter": "ا", "answers": ["احمر", "ازرق", "اخضر", "اصفر", "ابيض"]},
            {"category": "حيوان", "letter": "ف", "answers": ["فيل", "فار", "فهد", "فراشه", "فقمه"]},
            {"category": "نبات", "letter": "ن", "answers": ["نخل", "نعناع", "نرجس", "نارجيل", "نبق"]},
            {"category": "مدينه", "letter": "ج", "answers": ["جده", "جيزان", "جنيف", "جاكرتا", "جدة"]},
            {"category": "اكل", "letter": "ك", "answers": ["كبسه", "كفته", "كيك", "كريمه", "كشري"]},
            {"category": "شرب", "letter": "ع", "answers": ["عصير", "عرق سوس", "عرن", "عيران", "عسل"]},
            {"category": "اثاث", "letter": "ك", "answers": ["كرسي", "كنبه", "كومدينو", "كابينه", "كشاف"]},
            {"category": "ملابس", "letter": "ق", "answers": ["قميص", "قفطان", "قفازات", "قبعه", "قلنسوه"]},
            {"category": "مركبه", "letter": "س", "answers": ["سياره", "سفينه", "سكوتر", "سايكل", "سبمارين"]},
            {"category": "ادوات", "letter": "م", "answers": ["مطرقه", "مفك", "مقص", "مبرد", "منشار"]},
            {"category": "مجوهرات", "letter": "خ", "answers": ["خاتم", "خلخال", "خرز", "خنجر", "خزامه"]},
            {"category": "جسم", "letter": "ي", "answers": ["يد", "يمين", "يسار", "ياقه", "يافوخ"]},
            {"category": "طيور", "letter": "ح", "answers": ["حمامه", "حجل", "حسون", "حدايه", "حبش"]},
            {"category": "اسماك", "letter": "س", "answers": ["سمك", "سردين", "سلمون", "سبيط", "سمكه"]},
            {"category": "حشرات", "letter": "ن", "answers": ["نمله", "نحله", "نموس", "ناموسه", "نطاط"]},
            {"category": "زهور", "letter": "و", "answers": ["ورد", "ورده", "وهج", "وسمي", "وردية"]},
            {"category": "معادن", "letter": "ذ", "answers": ["ذهب", "ذوب", "ذبابه", "ذره", "ذرع"]},
            {"category": "مشروبات", "letter": "ق", "answers": ["قهوه", "قرفه", "قمر الدين", "قصب", "قشطه"]},
            {"category": "حلويات", "letter": "ك", "answers": ["كيك", "كعك", "كنافه", "كريم كراميل", "كوكيز"]},
            {"category": "اجهزه", "letter": "ت", "answers": ["تلفزيون", "تلفون", "تكييف", "تابلت", "تلسكوب"]},
            {"category": "ادوات مدرسيه", "letter": "ق", "answers": ["قلم", "قرطاسيه", "قاعده", "قياس", "قصاصات"]},
            {"category": "رياضيات", "letter": "ج", "answers": ["جمع", "جذر", "جبر", "جيب", "جداء"]},
            {"category": "علوم", "letter": "ك", "answers": ["كيمياء", "كهرباء", "كوكب", "كتله", "كربون"]},
            {"category": "جغرافيا", "letter": "ج", "answers": ["جبل", "جزيره", "جرف", "جدول", "جليد"]},
            {"category": "تاريخ", "letter": "ح", "answers": ["حرب", "حضاره", "حكم", "حاكم", "حقبه"]},
            {"category": "ادب", "letter": "ش", "answers": ["شعر", "شعراء", "شاعر", "شيخ", "شهره"]},
            {"category": "موسيقى", "letter": "ع", "answers": ["عود", "عزف", "عازف", "عذب", "عتبه"]},
            {"category": "فن", "letter": "ر", "answers": ["رسم", "رسام", "رساله", "رقص", "رواد"]},
            {"category": "سينما", "letter": "ف", "answers": ["فيلم", "فنان", "فناره", "فرقه", "فصل"]},
            {"category": "مسلسلات", "letter": "م", "answers": ["مسلسل", "مشهد", "ممثل", "مخرج", "محور"]},
            {"category": "العاب", "letter": "ش", "answers": ["شطرنج", "شبكه", "شده", "شاشه", "شريط"]},
            {"category": "رياضه مائيه", "letter": "س", "answers": ["سباحه", "سيرف", "سكي", "سبحه", "سواحل"]},
            {"category": "رياضه قتاليه", "letter": "ك", "answers": ["كاراتيه", "كيك بوكسنج", "كونغ فو", "كرة قدم", "كراف ماغا"]},
            {"category": "مصطلحات", "letter": "م", "answers": ["مفهوم", "معنى", "ماده", "منهج", "محتوى"]},
            {"category": "صفات", "letter": "ك", "answers": ["كريم", "كبير", "كاذب", "كسول", "كامل"]},
            {"category": "احوال", "letter": "س", "answers": ["سعيد", "سريع", "سمين", "سليم", "سالم"]},
            {"category": "اعمال", "letter": "ت", "answers": ["تجاره", "تعليم", "تصنيع", "تطوير", "تسويق"]},
            {"category": "مال", "letter": "ر", "answers": ["ريال", "روبيه", "روبل", "رنجت", "راند"]},
            {"category": "اوقات", "letter": "ص", "answers": ["صباح", "صلاه", "صيف", "صهر", "صوم"]},
            {"category": "فصول", "letter": "خ", "answers": ["خريف", "خصب", "خلاء", "خلوه", "خير"]},
            {"category": "اعياد", "letter": "ع", "answers": ["عيد", "عاشوراء", "عرفه", "عشره", "عمره"]}
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.answered_users = set()

    def start_game(self):
        self.questions = random.sample(self.challenges, self.total_questions)
        self.current_question = 0
        self.player_scores = {}
        self.answered_users = set()
        return self._show_question()

    def _show_question(self):
        challenge = self.questions[self.current_question]
        progress = f"{self.current_question + 1}/{self.total_questions}"
        
        return FlexSendMessage(
            alt_text="فئه وحرف",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "فئه وحرف", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "12px"
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {"type": "text", "text": "السؤال", "size": "xs", "color": COLORS['text_light'], "flex": 0},
                                {"type": "text", "text": progress, "size": "xs", "color": COLORS['primary'], "weight": "bold", "align": "end"}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "md", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": f"الفئه: {challenge['category']}", "size": "lg", "color": COLORS['text_dark'], "weight": "bold", "align": "center"},
                                {"type": "text", "text": f"الحرف: {challenge['letter']}", "size": "xxl", "color": COLORS['primary'], "weight": "bold", "margin": "md", "align": "center"}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "button", "action": {"type": "message", "label": "لمح", "text": "لمح"}, "style": "secondary", "height": "sm", "flex": 1},
                                {"type": "button", "action": {"type": "message", "label": "جاوب", "text": "جاوب"}, "style": "secondary", "height": "sm", "flex": 1}
                            ],
                            "spacing": "sm",
                            "margin": "lg"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "button", "action": {"type": "message", "label": "إيقاف", "text": "إيقاف"}, "style": "secondary", "height": "sm", "flex": 1},
                                {"type": "button", "action": {"type": "message", "label": "تسجيل", "text": "تسجيل"}, "style": "secondary", "height": "sm", "flex": 1}
                            ],
                            "spacing": "sm",
                            "margin": "sm"
                        }
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
            return self._show_question()
        return None

    def check_answer(self, text, user_id, display_name):
        if user_id in self.answered_users:
            return None
        
        challenge = self.questions[self.current_question]
        text = text.strip()

        if text.lower() in ['لمح', 'تلميح']:
            sample = challenge['answers'][0]
            return {'response': TextSendMessage(text=f"يبدا بحرف: {sample[0]}\nعدد الحروف: {len(sample)}"), 'points': 0, 'correct': False}

        if text.lower() in ['جاوب', 'الحل']:
            answers = ' - '.join(challenge['answers'][:3])
            self.answered_users.add(user_id)
            if self.current_question + 1 < self.total_questions:
                return {'response': TextSendMessage(text=f"بعض الاجابات:\n{answers}"), 'points': 0, 'correct': False, 'next_question': True}
            return self._end_game()

        normalized = normalize_text(text)
        valid_answers = [normalize_text(ans) for ans in challenge['answers']]

        if normalized in valid_answers:
            points = 1
            self.player_scores.setdefault(user_id, {'name': display_name, 'score': 0})
            self.player_scores[user_id]['score'] += points
            self.answered_users.add(user_id)

            if self.current_question + 1 < self.total_questions:
                return {'response': TextSendMessage(text=f"اجابه صحيحه {display_name}\n+{points} نقطه"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
            return self._end_game()
        
        return None

    def _end_game(self):
        if not self.player_scores:
            return {'response': TextSendMessage(text="انتهت اللعبه"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
        
        sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        winner = sorted_players[0][1]
        
        players_contents = []
        medals = ["🥇", "🥈", "🥉"]
        
        for i, p in enumerate(sorted_players[:5]):
            medal = medals[i] if i < 3 else f"{i+1}."
            players_contents.append({
                "type": "box",
                "layout": "baseline",
                "contents": [
                    {"type": "text", "text": medal, "size": "sm", "flex": 0},
                    {"type": "text", "text": p[1]['name'], "size": "sm", "color": COLORS['text_dark'], "flex": 3, "margin": "sm"},
                    {"type": "text", "text": f"{p[1]['score']} نقطه", "size": "sm", "color": COLORS['primary'], "weight": "bold", "align": "end", "flex": 2}
                ],
                "margin": "md" if i > 0 else "sm"
            })
        
        winner_card = FlexSendMessage(
            alt_text="نتائج اللعبه",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "انتهت اللعبه", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "12px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "الفائز", "size": "sm", "color": COLORS['text_light'], "align": "center"},
                                {"type": "text", "text": winner['name'], "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center", "margin": "xs"},
                                {"type": "text", "text": f"{winner['score']} نقطه", "size": "lg", "color": COLORS['success'], "align": "center", "margin": "xs"}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "النتائج", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                                *players_contents
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "إعادة اللعب", "text": "فئه"},
                            "style": "primary",
                            "color": COLORS['primary'],
                            "height": "sm",
                            "margin": "lg"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )
        return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
