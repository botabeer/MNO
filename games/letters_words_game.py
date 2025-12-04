"""
لعبة تكوين الكلمات - Letters Words Game
كوّن كلمات من الحروف المعطاة
"""

from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
import re
import logging
from constants import COLORS

logger = logging.getLogger(__name__)


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


class LettersWordsGame:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.challenges = [
            {"letters": "ق ل م ع ر ك", "answers": ["قلم", "علم", "عمر", "رقم", "ملك", "قرم", "كرم", "قمر"]},
            {"letters": "ك ت ا ب ر ل", "answers": ["كتاب", "كتب", "باب", "تراب", "بكر", "كبر", "برك", "كار"]},
            {"letters": "م د ر س ه ل", "answers": ["مدرسه", "درس", "سهل", "سهم", "مدر", "رسم", "سمر"]},
            {"letters": "ش ج ر ف ق ه", "answers": ["شجر", "فجر", "قهر", "شرف", "فرش", "رفش", "جرف"]},
            {"letters": "ح د ي ق ه ل", "answers": ["حديقه", "حقل", "دقيق", "حيل", "قيد", "حدي"]},
            {"letters": "ب ي ت ك ر م", "answers": ["بيت", "كبير", "كرم", "بكر", "ترك", "ركب", "تمر"]},
            {"letters": "س م ك ن و ل", "answers": ["سمك", "نوم", "سكن", "كنس", "لون", "سول", "كون"]},
            {"letters": "ط ب خ و ر ي", "answers": ["طبخ", "خبر", "طير", "خور", "بطر", "روح", "طرب"]},
            {"letters": "ن ج م س و ر", "answers": ["نجم", "سور", "جسر", "مرج", "رسم", "نور", "جرس"]},
            {"letters": "ف ص ل ح ي ن", "answers": ["فصل", "صلح", "حين", "فلح", "نصف", "صفن", "لحن"]},
            {"letters": "ع ي د ب ر ك", "answers": ["عيد", "بعد", "كبير", "ركب", "بكر", "عبر", "دير"]},
            {"letters": "ز ه ر و ق ن", "answers": ["زهر", "نور", "قرن", "زرق", "هرق", "نزه", "رزق"]},
            {"letters": "ج م ل ي ع ر", "answers": ["جمل", "جميل", "عمر", "رجل", "علم", "مرج", "جعل"]},
            {"letters": "ص ب ح و ر ي", "answers": ["صبح", "صور", "حور", "بحر", "صير", "روح", "حصي"]},
            {"letters": "ط ر ي ق ف ع", "answers": ["طريق", "فرق", "قرع", "طرف", "فرع", "قطر", "عرق"]},
            {"letters": "ح ل م و ب د", "answers": ["حلم", "حمل", "بحر", "دحل", "لحم", "محل", "حلو"]},
            {"letters": "ن ظ ف ر ي س", "answers": ["نظر", "نظيف", "فرس", "سير", "ظرف", "نفس", "فرن"]},
            {"letters": "ق و ل ب ع د", "answers": ["قول", "قلب", "بعد", "عقل", "قبل", "دول", "عود"]},
            {"letters": "ك ر س ي و م", "answers": ["كرسي", "كرم", "سوم", "ركس", "يوم", "سير", "سوك"]},
            {"letters": "ش م س ع و ر", "answers": ["شمس", "شعر", "عرس", "مشع", "سرع", "عمر", "رشم"]},
            {"letters": "ن و م ب ح ر", "answers": ["نوم", "بحر", "نحر", "محن", "برح", "منح", "حمن"]},
            {"letters": "ح ج ر ب ي ت", "answers": ["حجر", "بيت", "جبر", "حرب", "ترح", "ربح", "جرح"]},
            {"letters": "س ل م ط ع ا", "answers": ["سلم", "طعام", "ملس", "طلع", "علم", "سطل", "عسل"]},
            {"letters": "ف ت ح ل و ي", "answers": ["فتح", "حلو", "فلح", "حول", "فول", "تحف", "يحف"]},
            {"letters": "ر س م ل و ن", "answers": ["رسم", "لون", "سمن", "رمل", "نسل", "منل", "رنم"]},
            {"letters": "ب ع ي د ق ر", "answers": ["بعيد", "قرب", "بعد", "قدر", "ربع", "عقد", "دقر"]},
            {"letters": "ج س م ه ر ي", "answers": ["جسم", "جهر", "مرج", "رجس", "هرم", "سهم", "جمر"]},
            {"letters": "ط ل ب ع و ن", "answers": ["طلب", "بطل", "عون", "طول", "بعل", "نطل", "لبن"]},
            {"letters": "ص د ق ح ي ر", "answers": ["صدق", "حديق", "قدر", "صير", "رحي", "دحر", "صحر"]},
            {"letters": "ع ق ل ص ب و", "answers": ["عقل", "صبو", "عصب", "قصب", "بصل", "عقص", "عصو"]},
            {"letters": "ح ك م ي ل ن", "answers": ["حكم", "حكيم", "نحل", "كمل", "حمل", "نيل", "كلم"]},
            {"letters": "ف ر ح ض و ي", "answers": ["فرح", "فرض", "حور", "ضفر", "روح", "فوح", "حرف"]},
            {"letters": "م ط ر ع س ي", "answers": ["مطر", "عصر", "طرس", "سعر", "مرع", "رسم", "طعم"]},
            {"letters": "ن ع م ت ل ه", "answers": ["نعمه", "علم", "لحم", "نمل", "تمن", "عمل", "نعل"]},
            {"letters": "ب ر د و ق ي", "answers": ["برد", "بريق", "قرد", "دور", "ربي", "قرب", "دبر"]},
            {"letters": "س ف ن ح ي ر", "answers": ["سفن", "سفر", "فرح", "نحر", "فحر", "رسن", "سنح"]},
            {"letters": "خ ب ز ر ي ن", "answers": ["خبز", "خير", "برز", "زين", "خزن", "ربز", "نخز"]},
            {"letters": "و ج ه ل د ي", "answers": ["وجه", "جيد", "يدل", "لوج", "جدل", "هدي", "ودي"]},
            {"letters": "ك و ن ف ر ي", "answers": ["كون", "فرن", "كفر", "ركن", "وفي", "نكر", "فكر"]},
            {"letters": "ش ر ب ح ي ن", "answers": ["شرب", "حرب", "شرح", "برح", "شين", "حبر", "حرش"]},
            {"letters": "ذ ه ب ر و ق", "answers": ["ذهب", "ذرو", "قرب", "برق", "هدر", "بذر", "رهق"]},
            {"letters": "غ ر ف ل ب ه", "answers": ["غرف", "غلب", "فرغ", "لغب", "برغ", "رهف", "غفل"]},
            {"letters": "ت ر ك ع ي و", "answers": ["ترك", "عرك", "كور", "تري", "يرك", "عتر", "روع"]},
            {"letters": "ز ر ع ف ي ن", "answers": ["زرع", "فرن", "عزف", "رزن", "عرف", "زعف", "نزع"]},
            {"letters": "ص خ ر ب ي م", "answers": ["صخر", "صرب", "صرم", "خبر", "رصم", "مرص", "صخب"]},
            {"letters": "ض و ء ف ر ي", "answers": ["ضوء", "فرض", "ضري", "رضي", "فيض", "عرض", "رفض"]},
            {"letters": "ث و ب ر ي ع", "answers": ["ثوب", "ثري", "عرب", "ثبر", "ربع", "بري", "عتر"]},
            {"letters": "ظ ل م ع ي ر", "answers": ["ظلم", "عظم", "ملع", "رعي", "ظعم", "علر", "عرظ"]},
            {"letters": "ا م ل ع د ن", "answers": ["امل", "علم", "عدن", "لعن", "معن", "نعم", "دلع"]},
            {"letters": "ي س ر ف ق د", "answers": ["يسر", "فرد", "سفر", "قدر", "رفد", "سرق", "فدي"]}
        ]
        self.questions = []
        self.current_question = 0
        self.total_questions = 5
        self.player_scores = {}
        self.answered_users = set()
    
    def start_game(self):
        try:
            self.questions = random.sample(self.challenges, min(self.total_questions, len(self.challenges)))
            self.current_question = 0
            self.player_scores = {}
            self.answered_users = set()
            logger.info(f"بدء لعبة تكوين الكلمات - عدد الأسئلة: {self.total_questions}")
            return self._show_question()
        except Exception as e:
            logger.error(f"خطأ في بدء لعبة تكوين الكلمات: {e}")
            return TextMessage(text="حدث خطأ في بدء اللعبة")
    
    def _show_question(self):
        try:
            challenge = self.questions[self.current_question]
            letters = challenge['letters']
            progress = f"{self.current_question + 1}/{self.total_questions}"
            
            return FlexMessage(
                alt_text="تكوين الكلمات",
                contents=FlexContainer.from_dict({
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "contents": [
                            {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "تكوين الكلمات", "weight": "bold", "size": "xl", "color": COLORS['white'], "align": "center"}], "backgroundColor": COLORS['primary'], "paddingAll": "20px", "cornerRadius": "12px"},
                            {"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": "السؤال", "size": "xs", "color": COLORS['text_light'], "flex": 0}, {"type": "text", "text": progress, "size": "xs", "color": COLORS['primary'], "weight": "bold", "align": "end"}], "margin": "lg"},
                            {"type": "separator", "margin": "md", "color": COLORS['border']},
                            {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": letters, "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center"}, {"type": "text", "text": "كون كلمة من هذه الحروف", "size": "sm", "color": COLORS['text_dark'], "margin": "md", "wrap": True, "align": "center"}], "margin": "lg"},
                            {"type": "separator", "margin": "lg", "color": COLORS['border']},
                            {"type": "box", "layout": "horizontal", "contents": [{"type": "button", "action": {"type": "message", "label": "لمح", "text": "لمح"}, "style": "secondary", "height": "sm", "flex": 1}, {"type": "button", "action": {"type": "message", "label": "جاوب", "text": "جاوب"}, "style": "secondary", "height": "sm", "flex": 1}], "spacing": "sm", "margin": "lg"}
                        ],
                        "backgroundColor": COLORS['card_bg'],
                        "paddingAll": "20px"
                    }
                })
            )
        except Exception as e:
            logger.error(f"خطأ في عرض السؤال: {e}")
            return TextMessage(text="حدث خطأ في عرض السؤال")
    
    def next_question(self):
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.answered_users = set()
            return self._show_question()
        return None
    
    def check_answer(self, text, user_id, display_name):
        try:
            if user_id in self.answered_users:
                return None
            
            challenge = self.questions[self.current_question]
            text = text.strip()
            
            if text.lower() in ['لمح', 'تلميح']:
                sample_word = challenge['answers'][0]
                hint_text = f"أول حرف: {sample_word[0]}\nعدد الحروف: {len(sample_word)}"
                return {'response': TextMessage(text=hint_text), 'points': 0, 'correct': False}
            
            if text.lower() in ['جاوب', 'الجواب', 'الحل']:
                self.answered_users.add(user_id)
                some_words = ' - '.join(challenge['answers'][:3])
                if self.current_question + 1 < self.total_questions:
                    return {'response': TextMessage(text=f"بعض الكلمات الصحيحة:\n{some_words}"), 'points': 0, 'correct': False, 'next_question': True}
                else:
                    result = self._end_game()
                    result['response'] = [TextMessage(text=f"بعض الكلمات الصحيحة:\n{some_words}"), result['response']]
                    return result
            
            word_normalized = normalize_text(text)
            valid_answers = [normalize_text(ans) for ans in challenge['answers']]
            
            if word_normalized in valid_answers:
                points = 1
                if user_id not in self.player_scores:
                    self.player_scores[user_id] = {'name': display_name, 'score': 0}
                self.player_scores[user_id]['score'] += points
                self.answered_users.add(user_id)
                
                if self.current_question + 1 < self.total_questions:
                    return {'response': TextMessage(text=f"كلمة صحيحة {display_name}\n+{points} نقطة"), 'points': points, 'correct': True, 'won': True, 'next_question': True}
                else:
                    return self._end_game()
            
            return None
        except Exception as e:
            logger.error(f"خطأ في التحقق من الإجابة: {e}")
            return None
    
    def _end_game(self):
        try:
            if not self.player_scores:
                return {'response': TextMessage(text="انتهت اللعبة"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
            
            sorted_players = sorted(self.player_scores.items(), key=lambda x: x[1]['score'], reverse=True)
            winner = sorted_players[0][1]
            
            players_contents = []
            for i, (uid, player) in enumerate(sorted_players[:5]):
                players_contents.append({"type": "box", "layout": "baseline", "contents": [{"type": "text", "text": f"{i+1}.", "size": "sm", "flex": 0}, {"type": "text", "text": player['name'], "size": "sm", "color": COLORS['text_dark'], "flex": 3, "margin": "sm"}, {"type": "text", "text": f"{player['score']} نقطة", "size": "sm", "color": COLORS['primary'], "weight": "bold", "align": "end", "flex": 2}], "margin": "md" if i > 0 else "sm"})
            
            winner_card = FlexMessage(
                alt_text="نتائج اللعبة",
                contents=FlexContainer.from_dict({
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
                            {"type": "button", "action": {"type": "message", "label": "إعادة اللعب", "text": "تكوين"}, "style": "primary", "color": COLORS['primary'], "height": "sm", "margin": "lg"}
                        ],
                        "backgroundColor": COLORS['card_bg'],
                        "paddingAll": "20px"
                    }
                })
            )
            
            return {'response': winner_card, 'points': winner['score'], 'correct': True, 'won': True, 'game_over': True}
        except Exception as e:
            logger.error(f"خطأ في إنهاء اللعبة: {e}")
            return {'response': TextMessage(text="حدث خطأ في إنهاء اللعبة"), 'points': 0, 'correct': False, 'won': False, 'game_over': True}
