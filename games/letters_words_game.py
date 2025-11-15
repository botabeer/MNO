from linebot.models import TextSendMessage, FlexSendMessage
import random
import os
import logging

logger = logging.getLogger("game-bot")

class LettersWordsGame:
    def __init__(self, line_bot_api, use_ai=False, ask_ai=None):
        self.line_bot_api = line_bot_api
        self.use_ai = use_ai
        self.ask_ai = ask_ai
        self.letters = []
        self.target_words = []
        self.found_words = []
        self.words_file = self.load_words()
        self.player_scores = {}
        self.max_words = 3
        
    def load_words(self):
        """تحميل قائمة الكلمات من الملف"""
        try:
            filepath = os.path.join('games', 'words_list.txt')
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    words = [line.strip() for line in f if line.strip() and len(line.strip()) >= 3]
                logger.info(f"✅ تم تحميل {len(words)} كلمة لعبة التكوين")
                return words
            else:
                logger.warning(f"⚠️ ملف words_list.txt غير موجود")
                return self.get_default_words()
        except Exception as e:
            logger.error(f"❌ خطأ في تحميل ملف الكلمات: {e}")
            return self.get_default_words()
    
    def get_default_words(self):
        """كلمات افتراضية إذا لم يوجد الملف"""
        return [
            'كتاب', 'قلم', 'باب', 'ماء', 'شمس', 'قمر', 'نجم', 'بحر',
            'جبل', 'شجر', 'زهر', 'ورد', 'طير', 'سمك', 'حصان', 'كلب',
            'قطة', 'بيت', 'سيارة', 'طائرة', 'سفينة', 'قطار', 'مدرسة',
            'مستشفى', 'مكتب', 'كرسي', 'طاولة', 'نافذة', 'باب', 'جدار',
            'سقف', 'أرض', 'سماء', 'أرض', 'مطر', 'رعد', 'برق', 'ثلج',
            'ريح', 'عاصفة', 'صحراء', 'غابة', 'نهر', 'بحيرة', 'جزيرة'
        ]
    
    def normalize_text(self, text):
        """تطبيع النص للمقارنة"""
        if not text:
            return ""
        text = text.strip().lower()
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ؤ', 'و').replace('ئ', 'ي').replace('ء', '')
        text = text.replace('ة', 'ه').replace('ى', 'ي')
        import re
        text = re.sub(r'[\u064B-\u065F]', '', text)
        text = re.sub(r'\s+', '', text)
        return text
    
    def generate_letters_and_words(self):
        """توليد 6 حروف و3 كلمات يمكن تكوينها"""
        max_attempts = 50
        
        for attempt in range(max_attempts):
            # اختيار 3 كلمات عشوائية
            selected_words = random.sample(self.words_file, min(5, len(self.words_file)))
            
            # جمع كل الحروف من هذه الكلمات
            all_chars = []
            for word in selected_words:
                all_chars.extend(list(word))
            
            # إزالة التكرار والحصول على 6 حروف فريدة
            unique_chars = list(set(all_chars))
            
            if len(unique_chars) >= 6:
                # اختيار 6 حروف عشوائية
                chosen_letters = random.sample(unique_chars, 6)
                
                # البحث عن كلمات يمكن تكوينها من هذه الحروف
                possible_words = []
                for word in self.words_file:
                    if self.can_form_word(word, chosen_letters):
                        possible_words.append(word)
                
                # إذا وجدنا على الأقل 3 كلمات، نستخدم هذه المجموعة
                if len(possible_words) >= 3:
                    self.letters = chosen_letters
                    self.target_words = random.sample(possible_words, min(10, len(possible_words)))
                    logger.info(f"✅ تم توليد حروف: {self.letters}")
                    logger.info(f"✅ كلمات متاحة: {len(self.target_words)}")
                    return True
        
        # إذا فشلت جميع المحاولات، نستخدم مجموعة افتراضية
        logger.warning("⚠️ لم يتم توليد حروف، استخدام مجموعة افتراضية")
        self.letters = ['ك', 'ت', 'ا', 'ب', 'ر', 'م']
        self.target_words = ['كتاب', 'مكتب', 'كرم', 'بكر', 'ركب', 'كمر']
        return True
    
    def can_form_word(self, word, available_letters):
        """التحقق من إمكانية تكوين الكلمة من الحروف المتاحة"""
        # يمكن استخدام كل حرف أكثر من مرة
        word_normalized = self.normalize_text(word)
        available_normalized = [self.normalize_text(c) for c in available_letters]
        
        for char in word_normalized:
            if char not in available_normalized:
                return False
        return True
    
    def start_game(self):
        """بدء اللعبة"""
        self.found_words = []
        self.player_scores = {}
        self.generate_letters_and_words()
        
        letters_display = ' '.join(self.letters)
        
        card = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🔤 لعبة التكوين",
                                "size": "xl",
                                "weight": "bold",
                                "color": "#FFFFFF",
                                "align": "center"
                            }
                        ],
                        "backgroundColor": "#000000",
                        "cornerRadius": "12px",
                        "paddingAll": "20px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "الحروف المتاحة",
                                "size": "sm",
                                "color": "#666666",
                                "align": "center",
                                "margin": "lg"
                            },
                            {
                                "type": "text",
                                "text": letters_display,
                                "size": "xxl",
                                "weight": "bold",
                                "color": "#000000",
                                "align": "center",
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "lg",
                                "color": "#E5E5E5"
                            },
                            {
                                "type": "text",
                                "text": f"كوّن {self.max_words} كلمات صحيحة",
                                "size": "sm",
                                "color": "#333333",
                                "align": "center",
                                "margin": "lg",
                                "wrap": True
                            },
                            {
                                "type": "text",
                                "text": "• يمكن تكرار استخدام الحرف\n• كل كلمة رسالة منفصلة\n• كلمات من 3 حروف فأكثر",
                                "size": "xs",
                                "color": "#999999",
                                "align": "center",
                                "margin": "md",
                                "wrap": True
                            }
                        ],
                        "margin": "lg"
                    }
                ],
                "backgroundColor": "#FFFFFF",
                "paddingAll": "20px"
            }
        }
        
        return FlexSendMessage(alt_text="لعبة التكوين", contents=card)
    
    def verify_word_with_ai(self, word):
        """التحقق من صحة الكلمة باستخدام AI"""
        if not self.use_ai or not self.ask_ai:
            return False
        
        try:
            prompt = f"""هل الكلمة "{word}" كلمة عربية صحيحة موجودة في القاموس؟
أجب فقط بـ "نعم" أو "لا" بدون أي تفسير."""
            
            response = self.ask_ai(prompt)
            if response:
                answer = response.strip().lower()
                return 'نعم' in answer or 'yes' in answer
        except Exception as e:
            logger.error(f"❌ خطأ في التحقق بـ AI: {e}")
        
        return False
    
    def check_answer(self, text, user_id, display_name):
        """التحقق من الإجابة"""
        text_normalized = self.normalize_text(text)
        
        # التحقق من الأوامر الخاصة
        if text in ['لمح', 'تلميح', 'hint']:
            if len(self.target_words) > len(self.found_words):
                # إعطاء تلميح لكلمة لم تُكتشف بعد
                remaining = [w for w in self.target_words if self.normalize_text(w) not in self.found_words]
                hint_word = random.choice(remaining)
                hint = hint_word[0] + ' _ ' * (len(hint_word) - 1)
                return {
                    'correct': False,
                    'response': TextSendMessage(text=f"💡 تلميح: {hint}")
                }
            else:
                return {
                    'correct': False,
                    'response': TextSendMessage(text="▫️ لقد وجدت كل الكلمات المتاحة!")
                }
        
        if text in ['جاوب', 'الحل', 'الإجابة']:
            remaining = [w for w in self.target_words if self.normalize_text(w) not in self.found_words]
            if remaining:
                answers_text = '\n'.join([f"▫️ {w}" for w in remaining[:5]])
                return {
                    'correct': False,
                    'response': TextSendMessage(text=f"📝 بعض الكلمات الممكنة:\n\n{answers_text}")
                }
            else:
                return {
                    'correct': False,
                    'response': TextSendMessage(text="✅ لقد وجدت كل الكلمات!")
                }
        
        # التحقق من طول الكلمة
        if len(text_normalized) < 3:
            return {
                'correct': False,
                'response': TextSendMessage(text="▫️ الكلمة يجب أن تكون 3 حروف فأكثر")
            }
        
        # التحقق من أن الكلمة لم تُكتب من قبل
        if text_normalized in self.found_words:
            return {
                'correct': False,
                'response': TextSendMessage(text="▫️ هذه الكلمة تم كتابتها من قبل")
            }
        
        # التحقق من إمكانية تكوين الكلمة
        if not self.can_form_word(text, self.letters):
            return {
                'correct': False,
                'response': TextSendMessage(text="❌ لا يمكن تكوين هذه الكلمة من الحروف المتاحة")
            }
        
        # التحقق من صحة الكلمة
        is_valid = False
        
        # أولاً: التحقق من قائمة الكلمات المعروفة
        if text_normalized in [self.normalize_text(w) for w in self.target_words]:
            is_valid = True
            logger.info(f"✅ كلمة صحيحة من القائمة: {text}")
        
        # ثانياً: إذا فعّل AI، نتحقق منه
        elif self.use_ai and self.ask_ai:
            is_valid = self.verify_word_with_ai(text)
            if is_valid:
                logger.info(f"✅ كلمة صحيحة بواسطة AI: {text}")
        
        if not is_valid:
            return {
                'correct': False,
                'response': TextSendMessage(text="❌ كلمة غير صحيحة، حاول مرة أخرى")
            }
        
        # كلمة صحيحة!
        self.found_words.append(text_normalized)
        
        if user_id not in self.player_scores:
            self.player_scores[user_id] = {'name': display_name, 'score': 0}
        
        points = 3  # 3 نقاط لكل كلمة
        self.player_scores[user_id]['score'] += points
        
        remaining = self.max_words - len(self.found_words)
        
        if remaining > 0:
            return {
                'correct': True,
                'points': points,
                'response': TextSendMessage(text=f"✅ إجابة صحيحة!\n\n▪️ {text}\n▪️ +{points} نقطة\n\n⏳ باقي {remaining} {'كلمة' if remaining == 1 else 'كلمات'}")
            }
        else:
            # اللعبة انتهت
            return self.end_game()
    
    def end_game(self):
        """إنهاء اللعبة وإظهار النتائج"""
        if not self.player_scores:
            return {
                'game_over': True,
                'response': TextSendMessage(text="▫️ لم يشارك أحد في اللعبة")
            }
        
        # ترتيب اللاعبين
        sorted_players = sorted(
            self.player_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        winner_id, winner_data = sorted_players[0]
        winner_name = winner_data['name']
        winner_score = winner_data['score']
        
        # تجهيز قائمة النتائج
        all_scores = [(p[1]['name'], p[1]['score']) for p in sorted_players]
        
        # إنشاء بطاقة الفائز
        score_items = []
        for i, (name, score) in enumerate(all_scores, 1):
            if i == 1:
                rank_icon = "👑"
                bg_color = "#000000"
                text_color = "#FFFFFF"
            elif i == 2:
                rank_icon = "🥈"
                bg_color = "#333333"
                text_color = "#FFFFFF"
            elif i == 3:
                rank_icon = "🥉"
                bg_color = "#666666"
                text_color = "#FFFFFF"
            else:
                rank_icon = "▫️"
                bg_color = "#F5F5F5"
                text_color = "#000000"
            
            score_items.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {"type": "text", "text": f"{rank_icon} {name}", "size": "sm", "color": text_color, "flex": 3, "wrap": True},
                    {"type": "text", "text": str(score), "size": "md", "weight": "bold", "color": text_color, "flex": 1, "align": "end"}
                ],
                "backgroundColor": bg_color,
                "cornerRadius": "8px",
                "paddingAll": "12px",
                "margin": "sm" if i > 1 else "md"
            })
        
        winner_card = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🎉 انتهت لعبة التكوين",
                                "size": "xl",
                                "weight": "bold",
                                "color": "#FFFFFF",
                                "align": "center"
                            }
                        ],
                        "backgroundColor": "#000000",
                        "cornerRadius": "12px",
                        "paddingAll": "20px"
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": "#E5E5E5"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "الفائز",
                                "size": "sm",
                                "color": "#999999",
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": winner_name,
                                "size": "xxl",
                                "weight": "bold",
                                "color": "#000000",
                                "align": "center",
                                "margin": "sm",
                                "wrap": True
                            },
                            {
                                "type": "text",
                                "text": f"{winner_score} نقطة",
                                "size": "md",
                                "color": "#666666",
                                "align": "center",
                                "margin": "xs"
                            }
                        ],
                        "margin": "xl"
                    },
                    {
                        "type": "separator",
                        "margin": "xl",
                        "color": "#E5E5E5"
                    },
                    {
                        "type": "text",
                        "text": "النتائج النهائية",
                        "size": "md",
                        "weight": "bold",
                        "color": "#000000",
                        "margin": "xl"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": score_items,
                        "margin": "md"
                    }
                ],
                "backgroundColor": "#FFFFFF",
                "paddingAll": "20px"
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "لعب مرة أخرى", "text": "تكوين"},
                        "style": "primary",
                        "color": "#000000",
                        "height": "sm"
                    }
                ],
                "backgroundColor": "#F5F5F5",
                "paddingAll": "12px"
            }
        }
        
        return {
            'game_over': True,
            'won': True,
            'winner_card': winner_card,
            'points': winner_score
        }
    
    def next_question(self):
        """لا يوجد سؤال تالي في هذه اللعبة"""
        return None
