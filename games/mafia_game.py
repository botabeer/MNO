# games/mafia_game.py - لعبة المافيا الكاملة والمحسنة

from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer, PushMessageRequest
import random
from typing import Dict, Any, Optional
from datetime import datetime

class MafiaGame:
    """
    لعبة المافيا - لعبة جماعية استراتيجية
    
    المميزات:
    - الدكتور يحمي كل اسم مرة واحدة فقط (بما فيهم نفسه)
    - المقتولون/المطرودون يُقصَون من اللعبة ولا يظهرون في نوافذ الاختيار
    - اللعبة تستمر حتى النهاية حتى لو تغيب بعض اللاعبين
    - ألوان هادئة ومريحة ومتناسقة
    - جميع الأزرار بلون واحد #6B9BD1
    """
    
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.game_name = "مافيا"
        self.game_active = False
        self.game_start_time = None
        
        # إعدادات اللعبة
        self.min_players = 4
        self.max_players = 15
        
        # اللاعبون
        self.players = {}  # {user_id: display_name}
        self.roles = {}  # {user_id: role}
        self.alive_players = set()  # اللاعبون الأحياء
        self.dead_players = set()  # اللاعبون الموتى
        self.excluded_players = set()  # المُقصَون (لا يظهرون في النوافذ)
        
        # الأدوار
        self.mafia_members = set()
        self.citizens = set()
        self.doctor = None
        self.detective = None
        
        # قيود الدكتور
        self.doctor_protected = set()  # من تم حمايتهم سابقاً
        self.doctor_self_protected = False  # هل حمى نفسه
        
        # مراحل اللعبة
        self.game_phase = "waiting"  # waiting, joining, night, day, ended
        self.current_round = 0
        
        # التصويت
        self.night_votes = {}  # تصويت المافيا
        self.day_votes = {}  # تصويت النهار
        self.doctor_save = None  # من حماه الدكتور هذه الليلة
        self.detective_check = None  # من تحقق منه المحقق
        self.voted_users = set()  # من صوّت
        self.night_actions_done = set()  # من نفّذ فعله في الليل
        
        # ألوان هادئة ومريحة ومتناسقة - جميع الأزرار #6B9BD1
        self.colors = {
            'primary': '#6B9BD1',      # اللون الأساسي للبوت وجميع الأزرار
            'success': '#7BC8A4',      # أخضر هادئ
            'error': '#E19B9B',        # أحمر هادئ وردي
            'warning': '#F4C47C',      # برتقالي هادئ
            'mafia': '#C77A7A',        # وردي هادئ للمافيا
            'doctor': '#7CBFCA',       # أزرق فاتح للدكتور
            'detective': '#E8C97F',    # ذهبي فاتح للمحقق
            'citizen': '#8BC9A4',      # أخضر نعناعي للمواطن
            'text': '#4A5568',         # رمادي داكن للنص
            'text_light': '#A0AEC0',   # رمادي فاتح للنص الثانوي
            'border': '#E2E8F0',       # رمادي فاتح جداً للحدود
            'bg': '#F7FAFC',           # خلفية بيضاء مزرقة
            'card': '#FFFFFF',         # أبيض نقي للبطاقات
            'excluded': '#CBD5E0'      # رمادي للمُقصَين
        }
    
    def start_game(self):
        """بدء اللعبة - مرحلة الانضمام"""
        self.game_active = True
        self.game_phase = "joining"
        self.game_start_time = datetime.now()
        self.current_round = 0
        return self._get_joining_screen()
    
    def _get_joining_screen(self):
        """شاشة الانضمام مع أزرار"""
        joined_count = len(self.players)
        joined_names = ", ".join(list(self.players.values())[:8])
        
        contents = [
            # العنوان
            {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": "لعبة المافيا",
                    "weight": "bold",
                    "size": "xxl",
                    "color": "#FFFFFF",
                    "align": "center"
                }],
                "paddingAll": "18px",
                "backgroundColor": self.colors['primary'],
                "cornerRadius": "12px"
            },
            {"type": "separator", "margin": "lg", "color": self.colors['border']},
            
            # الوصف
            {
                "type": "text",
                "text": "لعبة جماعية تنقسم فيها الأدوار بين مافيا ومواطنين",
                "size": "xs",
                "color": self.colors['text_light'],
                "wrap": True,
                "align": "center",
                "margin": "md"
            },
            {"type": "separator", "margin": "md", "color": self.colors['border']},
            
            # عداد اللاعبين
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"المنضمون: {joined_count}/{self.max_players}",
                        "size": "md",
                        "weight": "bold",
                        "color": self.colors['primary'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": joined_names + ("..." if joined_count > 8 else "") if joined_names else "لا يوجد لاعبون بعد",
                        "size": "xs",
                        "color": self.colors['text_light'],
                        "wrap": True,
                        "align": "center",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": "#EDF2F7",
                "cornerRadius": "12px",
                "paddingAll": "12px",
                "margin": "md"
            },
            {"type": "separator", "margin": "md", "color": self.colors['border']},
            
            # ملاحظة مهمة
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "ملاحظة مهمة",
                        "size": "sm",
                        "weight": "bold",
                        "color": self.colors['error']
                    },
                    {
                        "type": "text",
                        "text": "يجب إضافة البوت كصديق ليصلك دورك بالخاص",
                        "size": "xs",
                        "color": self.colors['text_light'],
                        "wrap": True,
                        "margin": "xs"
                    }
                ],
                "backgroundColor": "#FFF5F5",
                "cornerRadius": "8px",
                "paddingAll": "10px",
                "margin": "md"
            },
            
            # الأزرار - كلها بنفس اللون #6B9BD1
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "انضم للعبة",
                            "text": "انضم"
                        },
                        "style": "primary",
                        "color": "#6B9BD1",
                        "height": "sm"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": f"ابدأ اللعبة ({joined_count}/{self.min_players})",
                            "text": "ابدأ"
                        },
                        "style": "primary",
                        "color": "#6B9BD1",
                        "height": "sm",
                        "margin": "sm"
                    }
                ],
                "margin": "lg"
            }
        ]
        
        return FlexMessage(
            alt_text="لعبة المافيا",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "size": "mega",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": contents,
                    "paddingAll": "24px",
                    "backgroundColor": self.colors['bg']
                }
            })
        )
    
    def _assign_roles(self):
        """توزيع الأدوار عشوائياً"""
        player_list = list(self.players.keys())
        random.shuffle(player_list)
        
        num_players = len(player_list)
        num_mafia = max(1, num_players // 4)  # 25% مافيا
        
        # تعيين المافيا
        self.mafia_members = set(player_list[:num_mafia])
        remaining = player_list[num_mafia:]
        
        # تعيين الدكتور والمحقق
        if len(remaining) >= 2:
            self.doctor = remaining[0]
            self.detective = remaining[1]
            self.citizens = set(remaining[2:])
        else:
            self.citizens = set(remaining)
        
        # حفظ الأدوار
        for player_id in self.mafia_members:
            self.roles[player_id] = "مافيا"
        if self.doctor:
            self.roles[self.doctor] = "دكتور"
        if self.detective:
            self.roles[self.detective] = "محقق"
        for player_id in self.citizens:
            self.roles[player_id] = "مواطن"
        
        # جميع اللاعبين أحياء في البداية
        self.alive_players = set(player_list)
    
    def _get_player_selection_card(self, title, description, for_user_id):
        """بطاقة اختيار لاعب - في الخاص"""
        
        available_players = []
        
        # قائمة اللاعبين الأحياء (غير المُقصَين)
        for pid in self.alive_players:
            if pid in self.excluded_players:
                continue  # لا يظهر المُقصَون
            
            if pid == for_user_id:
                continue  # لا يظهر نفسه (سيُضاف لاحقاً للدكتور فقط)
            
            player_name = self.players[pid]
            
            # للدكتور: إظهار من تم حمايتهم سابقاً
            if self.roles.get(for_user_id) == "دكتور":
                if pid in self.doctor_protected:
                    continue  # لا يمكن حمايته مرة أخرى
            
            available_players.append((pid, player_name))
        
        # إضافة خيار حماية النفس للدكتور (مرة واحدة فقط)
        if self.roles.get(for_user_id) == "دكتور" and not self.doctor_self_protected:
            available_players.insert(0, (for_user_id, f"{self.players[for_user_id]} (أنت)"))
        
        contents = [
            {
                "type": "text",
                "text": title,
                "size": "xl",
                "weight": "bold",
                "color": self.colors['primary'],
                "align": "center"
            },
            {"type": "separator", "margin": "md", "color": self.colors['border']},
            {
                "type": "text",
                "text": description,
                "size": "sm",
                "color": self.colors['text_light'],
                "align": "center",
                "wrap": True,
                "margin": "md"
            },
            {"type": "separator", "margin": "md", "color": self.colors['border']},
            {
                "type": "text",
                "text": "اختر لاعب:",
                "size": "sm",
                "weight": "bold",
                "color": self.colors['text'],
                "margin": "md"
            }
        ]
        
        # إضافة أزرار اللاعبين - كلها بنفس اللون #6B9BD1
        for player_id, player_name in available_players[:12]:
            contents.append({
                "type": "button",
                "action": {
                    "type": "message",
                    "label": player_name,
                    "text": f"اختار:{player_name}"
                },
                "style": "primary",
                "color": "#6B9BD1",
                "height": "sm",
                "margin": "sm"
            })
        
        return FlexMessage(
            alt_text=title,
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "size": "mega",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": contents,
                    "paddingAll": "20px",
                    "backgroundColor": self.colors['bg']
                }
            })
        )
    
    def _send_role_message(self, user_id, role):
        """إرسال رسالة خاصة بالدور + نافذة اختيار"""
        try:
            # إرسال نافذة الاختيار للأدوار النشطة فقط
            if role in ["مافيا", "دكتور", "محقق"]:
                if role == "مافيا":
                    card = self._get_player_selection_card(
                        "اختر الضحية",
                        "اختر من تريد قتله الليلة",
                        user_id
                    )
                elif role == "دكتور":
                    card = self._get_player_selection_card(
                        "اختر من تحمي",
                        "كل اسم مرة واحدة فقط (بما فيهم أنت)",
                        user_id
                    )
                else:  # محقق
                    card = self._get_player_selection_card(
                        "اختر من تحقق منه",
                        "اختر اللاعب للتحقق من دوره",
                        user_id
                    )
                
                self.line_bot_api.push_message(
                    PushMessageRequest(to=user_id, messages=[card])
                )
        except Exception as e:
            print(f"Failed to send role message: {e}")
    
    def _get_night_phase(self):
        """مرحلة الليل مع زر لإنهاء الليل"""
        
        # إرسال نوافذ الاختيار للاعبين الأحياء فقط
        for player_id in self.alive_players:
            if player_id not in self.excluded_players:
                self._send_role_message(player_id, self.roles[player_id])
        
        self.night_actions_done.clear()
        
        contents = [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": f"الليلة رقم {self.current_round}",
                    "size": "xxl",
                    "weight": "bold",
                    "color": "#FFFFFF",
                    "align": "center"
                }],
                "paddingAll": "18px",
                "backgroundColor": self.colors['primary'],
                "cornerRadius": "12px"
            },
            {"type": "separator", "margin": "lg", "color": self.colors['border']},
            {
                "type": "text",
                "text": "حان وقت الليل - تحقق من رسائلك الخاصة",
                "size": "md",
                "color": self.colors['text'],
                "align": "center",
                "wrap": True,
                "margin": "md"
            },
            {
                "type": "button",
                "action": {
                    "type": "message",
                    "label": "إنهاء الليل وبدء التصويت",
                    "text": "انهي الليل"
                },
                "style": "primary",
                "color": "#6B9BD1",
                "height": "sm",
                "margin": "lg"
            }
        ]
        
        return FlexMessage(
            alt_text="مرحلة الليل",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "size": "mega",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": contents,
                    "paddingAll": "24px",
                    "backgroundColor": self.colors['bg']
                }
            })
        )
    
    def _process_night_result(self):
        """معالجة نتيجة الليل"""
        # اختيار المافيا (الأكثر تصويتاً)
        mafia_target = max(self.night_votes, key=self.night_votes.get) if self.night_votes else None
        
        killed = None
        # التحقق من الإنقاذ
        if mafia_target and mafia_target != self.doctor_save:
            killed = mafia_target
            self.alive_players.discard(killed)
            self.dead_players.add(killed)
            self.excluded_players.add(killed)  # إقصاءه من اللعبة
        
        # مسح أصوات الليل
        self.night_votes.clear()
        self.doctor_save = None
        
        return killed
    
    def _get_day_voting_card(self, night_result=None):
        """نافذة التصويت النهاري - في القروب"""
        
        # اللاعبون الأحياء غير المُقصَين فقط
        alive_list = [
            (pid, self.players[pid]) 
            for pid in self.alive_players 
            if pid not in self.excluded_players
        ]
        
        contents = [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": f"النهار رقم {self.current_round}",
                    "size": "xxl",
                    "weight": "bold",
                    "color": "#FFFFFF",
                    "align": "center"
                }],
                "paddingAll": "18px",
                "backgroundColor": self.colors['primary'],
                "cornerRadius": "12px"
            },
            {"type": "separator", "margin": "lg", "color": self.colors['border']}
        ]
        
        # نتيجة الليل
        if night_result:
            contents.append({
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"تم قتل: {self.players[night_result]}",
                        "size": "md",
                        "weight": "bold",
                        "color": self.colors['error'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "تم إقصاؤه من اللعبة ولا يستطيع المشاركة",
                        "size": "xs",
                        "color": self.colors['text_light'],
                        "align": "center",
                        "margin": "xs"
                    }
                ],
                "backgroundColor": "#FFF5F5",
                "cornerRadius": "8px",
                "paddingAll": "12px",
                "margin": "md"
            })
        else:
            contents.append({
                "type": "text",
                "text": "لم يتم قتل أحد الليلة",
                "size": "sm",
                "color": self.colors['success'],
                "align": "center",
                "margin": "md"
            })
        
        contents.extend([
            {"type": "separator", "margin": "md", "color": self.colors['border']},
            {
                "type": "text",
                "text": "وقت التصويت - اختر من تريد طرده:",
                "size": "sm",
                "weight": "bold",
                "color": self.colors['text'],
                "margin": "md",
                "align": "center"
            }
        ])
        
        # أزرار اللاعبين - كلها بنفس اللون #6B9BD1
        for player_id, player_name in alive_list[:12]:
            contents.append({
                "type": "button",
                "action": {
                    "type": "message",
                    "label": player_name,
                    "text": f"صوت:{player_name}"
                },
                "style": "primary",
                "color": "#6B9BD1",
                "height": "sm",
                "margin": "sm"
            })
        
        # زر إنهاء التصويت
        contents.append({
            "type": "button",
            "action": {
                "type": "message",
                "label": "إنهاء التصويت",
                "text": "انهي التصويت"
            },
            "style": "primary",
            "color": "#6B9BD1",
            "height": "sm",
            "margin": "lg"
        })
        
        # مسح الأصوات السابقة
        self.voted_users.clear()
        self.day_votes.clear()
        
        return FlexMessage(
            alt_text="التصويت النهاري",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "size": "mega",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": contents,
                    "paddingAll": "20px",
                    "backgroundColor": self.colors['bg']
                }
            })
        )
    
    def _process_day_result(self):
        """معالجة نتيجة التصويت النهاري"""
        executed = max(self.day_votes, key=self.day_votes.get) if self.day_votes else None
        
        if executed:
            self.alive_players.discard(executed)
            self.dead_players.add(executed)
            self.excluded_players.add(executed)  # إقصاءه من اللعبة
        
        self.day_votes.clear()
        return executed
    
    def _check_win_condition(self):
        """التحقق من شرط الفوز"""
        alive_mafia = len(self.mafia_members & self.alive_players)
        alive_citizens = len(self.alive_players) - alive_mafia
        
        if alive_mafia == 0:
            return "المواطنون"
        elif alive_mafia >= alive_citizens:
            return "المافيا"
        
        return None
    
    def _get_winner_card(self, winner_team):
        """بطاقة الفوز مع كشف جميع الأدوار"""
        
        role_groups = {
            "مافيا": [],
            "دكتور": [],
            "محقق": [],
            "مواطن": []
        }
        
        # تجميع اللاعبين حسب الأدوار
        for player_id, role in self.roles.items():
            player_name = self.players[player_id]
            status = "حي" if player_id in self.alive_players else "ميت"
            role_groups[role].append(f"{player_name} ({status})")
        
        contents = [
            # العنوان
            {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": "انتهت اللعبة",
                    "weight": "bold",
                    "size": "xxl",
                    "color": "#FFFFFF",
                    "align": "center"
                }],
                "backgroundColor": self.colors['primary'],
                "paddingAll": "18px",
                "cornerRadius": "12px"
            },
            {"type": "separator", "margin": "lg", "color": self.colors['border']},
            
            # الفائز
            {
                "type": "text",
                "text": f"الفائز: {winner_team}",
                "size": "xl",
                "weight": "bold",
                "color": self.colors['success'],
                "align": "center",
                "margin": "md"
            },
            {"type": "separator", "margin": "lg", "color": self.colors['border']},
            
            # عنوان كشف الأدوار
            {
                "type": "text",
                "text": "كشف الأدوار",
                "size": "md",
                "weight": "bold",
                "color": self.colors['text'],
                "align": "center",
                "margin": "md"
            }
        ]
        
        # عرض كل دور مع لونه
        for role, color_key in [("مافيا", "mafia"), ("دكتور", "doctor"), ("محقق", "detective"), ("مواطن", "citizen")]:
            if role_groups[role]:
                contents.append({
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [{"type": "filler"}],
                            "width": "4px",
                            "backgroundColor": self.colors[color_key]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": role,
                                    "size": "sm",
                                    "weight": "bold",
                                    "color": self.colors[color_key]
                                },
                                {
                                    "type": "text",
                                    "text": "\n".join(role_groups[role]),
                                    "size": "xs",
                                    "color": self.colors['text'],
                                    "wrap": True,
                                    "margin": "xs"
                                }
                            ],
                            "margin": "sm"
                        }
                    ],
                    "backgroundColor": self.colors['card'],
                    "cornerRadius": "8px",
                    "paddingAll": "12px",
                    "margin": "sm"
                })
        
        # الإحصائيات
        contents.extend([
            {"type": "separator", "margin": "lg", "color": self.colors['border']},
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "إحصائيات اللعبة",
                        "size": "sm",
                        "weight": "bold",
                        "color": self.colors['text']
                    },
                    {
                        "type": "text",
                        "text": f"عدد الجولات: {self.current_round}\nعدد اللاعبين: {len(self.players)}\nالأحياء: {len(self.alive_players)}\nالموتى: {len(self.dead_players)}",
                        "size": "xs",
                        "color": self.colors['text_light'],
                        "wrap": True,
                        "margin": "sm"
                    }
                ],
                "backgroundColor": "#EDF2F7",
                "cornerRadius": "8px",
                "paddingAll": "12px",
                "margin": "md"
            }
        ])
        
        return FlexMessage(
            alt_text="نتائج اللعبة",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "size": "mega",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": contents,
                    "paddingAll": "24px",
                    "backgroundColor": self.colors['bg']
                }
            })
        )
    
    def check_answer(self, user_answer: str, user_id: str, display_name: str) -> Optional[Dict[str, Any]]:
        """معالجة الإجابات والأوامر"""
        
        if not self.game_active:
            return None
        
        text = user_answer.strip()
        text_lower = text.lower()
        
        # مرحلة الانضمام
        if self.game_phase == "joining":
            if text_lower in ['انضم', 'join']:
                if user_id not in self.players and len(self.players) < self.max_players:
                    self.players[user_id] = display_name
                    return {'response': self._get_joining_screen(), 'points': 0}
            
            elif text_lower in ['ابدأ', 'start', 'بدأ']:
                if len(self.players) >= self.min_players:
                    self._assign_roles()
                    self.game_phase = "night"
                    self.current_round = 1
                    return {'response': self._get_night_phase(), 'points': 0}
                else:
                    return {
                        'response': TextMessage(text=f"يحتاج {self.min_players - len(self.players)} لاعبين إضافيين"),
                        'points': 0
                    }
        
        # مرحلة الليل - الاختيارات
        elif self.game_phase == "night":
            if text.startswith("اختار:"):
                selected_name = text.replace("اختار:", "").strip().replace(" (أنت)", "")
                
                # البحث عن اللاعب
                selected_id = None
                for pid, pname in self.players.items():
                    if pname == selected_name and pid in self.alive_players:
                        selected_id = pid
                        break
                
                if selected_id:
                    # تسجيل الاختيار حسب الدور
                    if self.roles.get(user_id) == "مافيا":
                        self.night_votes[selected_id] = self.night_votes.get(selected_id, 0) + 1
                        self.night_actions_done.add(user_id)
                        return {'response': TextMessage(text=f"تم اختيار {selected_name}"), 'points': 0}
                    
                    elif self.roles.get(user_id) == "دكتور":
                        # التحقق من القيود
                        if selected_id in self.doctor_protected:
                            return {
                                'response': TextMessage(text="هذا اللاعب تم حمايته سابقاً، اختر لاعب آخر"),
                                'points': 0
                            }
                        if selected_id == user_id and self.doctor_self_protected:
                            return {
                                'response': TextMessage(text="لقد حميت نفسك سابقاً، اختر لاعب آخر"),
                                'points': 0
                            }
                        
                        self.doctor_save = selected_id
                        self.doctor_protected.add(selected_id)
                        if selected_id == user_id:
                            self.doctor_self_protected = True
                        self.night_actions_done.add(user_id)
                        return {'response': TextMessage(text=f"تم الحماية"), 'points': 0}
                    
                    elif self.roles.get(user_id) == "محقق":
                        self.detective_check = selected_id
                        self.night_actions_done.add(user_id)
                        is_mafia = selected_id in self.mafia_members
                        result = "مافيا" if is_mafia else "مواطن"
                        return {'response': TextMessage(text=f"{selected_name} هو {result}"), 'points': 0}
            
            elif text_lower in ['انهي الليل', 'انهاء الليل']:
                # الانتقال لمرحلة النهار
                self.game_phase = "day"
                killed = self._process_night_result()
                
                # التحقق من الفوز
                winner = self._check_win_condition()
                if winner:
                    return self.end_game()
                
                return {'response': self._get_day_voting_card(killed), 'points': 0}
        
        # مرحلة النهار - التصويت
        elif self.game_phase == "day":
            if text.startswith("صوت:"):
                # التحقق من أن اللاعب حي وغير مُقصى
                if user_id not in self.alive_players or user_id in self.excluded_players:
                    return None
                
                # التحقق من أنه لم يصوت بعد
                if user_id in self.voted_users:
                    return {'response': TextMessage(text="لقد صوّت بالفعل"), 'points': 0}
                
                voted_name = text.replace("صوت:", "").strip()
                
                # البحث عن اللاعب المصوت عليه
                voted_id = None
                for pid, pname in self.players.items():
                    if pname == voted_name and pid in self.alive_players:
                        voted_id = pid
                        break
                
                if voted_id:
                    self.day_votes[voted_id] = self.day_votes.get(voted_id, 0) + 1
                    self.voted_users.add(user_id)
                    return {'response': TextMessage(text=f"تم التصويت"), 'points': 0}
            
            elif text_lower in ['انهي التصويت', 'انهاء التصويت']:
                # معالجة نتيجة التصويت
                executed = self._process_day_result()
                
                # التحقق من الفوز
                winner = self._check_win_condition()
                if winner:
                    return self.end_game()
                
                # العودة لليل
                self.game_phase = "night"
                self.current_round += 1
                
                result_text = f"تم طرد {self.players[executed]} - تم إقصاؤه من اللعبة" if executed else "لم يتم طرد أحد"
                
                return {
                    'response': [
                        TextMessage(text=result_text),
                        self._get_night_phase()
                    ],
                    'points': 0
                }
        
        return None
    
    def end_game(self):
        """إنهاء اللعبة"""
        winner = self._check_win_condition() or "لا أحد"
        self.game_active = False
        self.game_phase = "ended"
        
        return {
            'game_over': True,
            'points': 1,
            'response': self._get_winner_card(winner)
        }
