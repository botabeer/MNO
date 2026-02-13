# games/mafia_game.py - لعبة المافيا الكاملة مع نوافذ اختيار

from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer, PushMessageRequest
import random
from typing import Dict, Any, Optional, List
from datetime import datetime

class MafiaGame:
    """لعبة المافيا - لعبة جماعية استراتيجية"""
    
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.game_name = "مافيا"
        self.game_active = False
        self.game_start_time = None
        
        # اعدادات اللعبة
        self.min_players = 4
        self.max_players = 15
        
        # اللاعبون
        self.players = {}  # {user_id: display_name}
        self.roles = {}  # {user_id: role}
        self.alive_players = set()
        self.dead_players = set()
        
        # الادوار
        self.mafia_members = set()
        self.citizens = set()  # المواطنون
        self.doctor = None
        self.detective = None
        
        # مراحل اللعبة
        self.game_phase = "waiting"  # waiting, joining, night, day, ended
        self.current_round = 0
        
        # التصويت
        self.night_votes = {}  # مافيا
        self.day_votes = {}  # تصويت النهار
        self.doctor_save = None
        self.detective_check = None
        self.voted_users = set()  # من صوت
        
        # الالوان
        self.colors = {
            'primary': '#6B9BD1',
            'success': '#52C5B6',
            'error': '#E17B7B',
            'warning': '#F39C6B',
            'mafia': '#8B0000',
            'doctor': '#00CED1',
            'detective': '#FFD700',
            'citizen': '#32CD32',
            'text': '#2C3E50',
            'text_light': '#95A5A6',
            'border': '#E8ECEF',
            'bg': '#F9FAFB',
            'card': '#FFFFFF'
        }
    
    def start_game(self):
        """بدء اللعبة - مرحلة الانضمام"""
        self.game_active = True
        self.game_phase = "joining"
        self.game_start_time = datetime.now()
        self.current_round = 0
        
        return self._get_joining_screen()
    
    def _get_joining_screen(self):
        """شاشة الانضمام"""
        joined_count = len(self.players)
        
        contents = [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": "لعبة المافيا",
                    "weight": "bold",
                    "size": "xxl",
                    "color": self.colors['primary'],
                    "align": "center"
                }],
                "paddingAll": "15px",
                "backgroundColor": self.colors['card'],
                "cornerRadius": "12px"
            },
            {"type": "separator", "margin": "lg", "color": self.colors['border']},
            
            # شرح اللعبة
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "شرح اللعبة",
                        "size": "md",
                        "weight": "bold",
                        "color": self.colors['text'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "لعبة جماعية تنقسم فيها الادوار بين مافيا ومواطنين",
                        "size": "xs",
                        "color": self.colors['text_light'],
                        "wrap": True,
                        "margin": "sm",
                        "align": "center"
                    }
                ],
                "margin": "md"
            },
            
            {"type": "separator", "margin": "md", "color": self.colors['border']},
            
            # الادوار
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "الادوار",
                        "size": "sm",
                        "weight": "bold",
                        "color": self.colors['text'],
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [{"type": "filler"}],
                                        "width": "4px",
                                        "backgroundColor": self.colors['mafia']
                                    },
                                    {
                                        "type": "text",
                                        "text": "المافيا: يحاولون قتل المواطنين ليلا",
                                        "size": "xs",
                                        "color": self.colors['text'],
                                        "wrap": True,
                                        "margin": "sm"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [{"type": "filler"}],
                                        "width": "4px",
                                        "backgroundColor": self.colors['citizen']
                                    },
                                    {
                                        "type": "text",
                                        "text": "المواطنون: يصوتون لطرد المشتبهين نهارا",
                                        "size": "xs",
                                        "color": self.colors['text'],
                                        "wrap": True,
                                        "margin": "sm"
                                    }
                                ],
                                "margin": "xs"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [{"type": "filler"}],
                                        "width": "4px",
                                        "backgroundColor": self.colors['doctor']
                                    },
                                    {
                                        "type": "text",
                                        "text": "الدكتور: ينقذ لاعب واحد كل ليلة",
                                        "size": "xs",
                                        "color": self.colors['text'],
                                        "wrap": True,
                                        "margin": "sm"
                                    }
                                ],
                                "margin": "xs"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [{"type": "filler"}],
                                        "width": "4px",
                                        "backgroundColor": self.colors['detective']
                                    },
                                    {
                                        "type": "text",
                                        "text": "المحقق: يكشف دور لاعب كل ليلة",
                                        "size": "xs",
                                        "color": self.colors['text'],
                                        "wrap": True,
                                        "margin": "sm"
                                    }
                                ],
                                "margin": "xs"
                            }
                        ],
                        "margin": "sm"
                    }
                ],
                "backgroundColor": self.colors['card'],
                "cornerRadius": "12px",
                "paddingAll": "12px",
                "margin": "md"
            },
            
            # عداد اللاعبين
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "اللاعبون المنضمون",
                                "size": "sm",
                                "weight": "bold",
                                "color": self.colors['text'],
                                "flex": 1
                            },
                            {
                                "type": "text",
                                "text": f"{joined_count}/{self.max_players}",
                                "size": "lg",
                                "weight": "bold",
                                "color": self.colors['primary'],
                                "flex": 0
                            }
                        ]
                    },
                    {
                        "type": "text",
                        "text": f"الحد الادنى: {self.min_players} لاعبين",
                        "size": "xs",
                        "color": self.colors['text_light'],
                        "margin": "sm"
                    }
                ],
                "backgroundColor": "#EBF5FB",
                "cornerRadius": "12px",
                "paddingAll": "12px",
                "margin": "lg"
            },
            
            # التعليمات
            {
                "type": "text",
                "text": "اكتب 'انضم' للانضمام\nاكتب 'ابدأ' لبدء اللعبة (بعد وصول الحد الادنى)",
                "size": "sm",
                "color": self.colors['text_light'],
                "align": "center",
                "wrap": True,
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
        """توزيع الادوار عشوائيا"""
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
        
        # حفظ الادوار
        for player_id in self.mafia_members:
            self.roles[player_id] = "مافيا"
        
        if self.doctor:
            self.roles[self.doctor] = "دكتور"
        
        if self.detective:
            self.roles[self.detective] = "محقق"
        
        for player_id in self.citizens:
            self.roles[player_id] = "مواطن"
        
        # جميع اللاعبين احياء
        self.alive_players = set(player_list)
    
    def _get_player_selection_card(self, title, description, for_user_id):
        """بطاقة اختيار لاعب - في الخاص"""
        
        # قائمة اللاعبين الاحياء (غير نفسه)
        available_players = [
            (pid, self.players[pid]) 
            for pid in self.alive_players 
            if pid != for_user_id
        ]
        
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
        
        # اضافة ازرار اللاعبين
        for player_id, player_name in available_players[:10]:  # اول 10 لاعبين
            contents.append({
                "type": "button",
                "action": {
                    "type": "message",
                    "label": player_name,
                    "text": f"اختار:{player_name}"
                },
                "style": "secondary",
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
        """ارسال رسالة خاصة بالدور + نافذة اختيار"""
        role_colors = {
            "مافيا": self.colors['mafia'],
            "دكتور": self.colors['doctor'],
            "محقق": self.colors['detective'],
            "مواطن": self.colors['citizen']
        }
        
        role_descriptions = {
            "مافيا": {
                "title": "انت من المافيا",
                "desc": "مهمتك: القضاء على المواطنين\n\nفي الليل: اختر ضحية من القائمة\n\n",
                "extra": f"اعضاء المافيا الاخرون:\n" + "\n".join([
                    self.players[p] for p in self.mafia_members if p != user_id
                ]) if len(self.mafia_members) > 1 else "انت المافيا الوحيد"
            },
            "دكتور": {
                "title": "انت الدكتور",
                "desc": "مهمتك: حماية المواطنين\n\nفي الليل: اختر لاعب لحمايته من القائمة\n\nملاحظة: يمكنك حماية نفسك",
                "extra": ""
            },
            "محقق": {
                "title": "انت المحقق",
                "desc": "مهمتك: كشف المافيا\n\nفي الليل: اختر لاعب للتحقق من دوره من القائمة\n\nستعرف اذا كان مافيا ام لا",
                "extra": ""
            },
            "مواطن": {
                "title": "انت مواطن",
                "desc": "مهمتك: البقاء على قيد الحياة\n\nفي النهار: صوت لطرد المشتبه به من القائمة\n\nاعتمد على المحقق والدكتور",
                "extra": ""
            }
        }
        
        info = role_descriptions.get(role, role_descriptions["مواطن"])
        role_color = role_colors.get(role, self.colors['citizen'])
        
        contents = [
            {
                "type": "text",
                "text": "دورك في اللعبة",
                "size": "xl",
                "weight": "bold",
                "color": self.colors['primary'],
                "align": "center"
            },
            {"type": "separator", "margin": "lg", "color": self.colors['border']},
            
            # الدور
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": role,
                        "size": "xxl",
                        "weight": "bold",
                        "color": role_color,
                        "align": "center"
                    }
                ],
                "backgroundColor": self.colors['card'],
                "cornerRadius": "20px",
                "paddingAll": "20px",
                "borderWidth": "2px",
                "borderColor": role_color,
                "margin": "lg"
            },
            
            # العنوان
            {
                "type": "text",
                "text": info['title'],
                "size": "md",
                "weight": "bold",
                "color": self.colors['text'],
                "wrap": True,
                "margin": "lg",
                "align": "center"
            },
            
            # الوصف
            {
                "type": "text",
                "text": info['desc'],
                "size": "sm",
                "color": self.colors['text'],
                "wrap": True,
                "margin": "md"
            },
            
            {"type": "separator", "margin": "lg", "color": self.colors['border']},
            
            # معلومات اضافية
            {
                "type": "text",
                "text": info['extra'] if info['extra'] else "سيتم ارسال قائمة الاختيار في كل جولة",
                "size": "xs",
                "color": self.colors['text_light'],
                "align": "center",
                "wrap": True,
                "margin": "md"
            }
        ]
        
        message = FlexMessage(
            alt_text=f"دورك: {role}",
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
        
        try:
            # ارسال رسالة الدور
            self.line_bot_api.push_message(
                PushMessageRequest(to=user_id, messages=[message])
            )
            
            # ارسال نافذة الاختيار حسب الدور
            if role == "مافيا":
                selection_card = self._get_player_selection_card(
                    "اختر الضحية",
                    "اختر من تريد قتله الليلة",
                    user_id
                )
                self.line_bot_api.push_message(
                    PushMessageRequest(to=user_id, messages=[selection_card])
                )
            elif role == "دكتور":
                selection_card = self._get_player_selection_card(
                    "اختر من تحمي",
                    "اختر اللاعب الذي تريد حمايته الليلة",
                    user_id
                )
                self.line_bot_api.push_message(
                    PushMessageRequest(to=user_id, messages=[selection_card])
                )
            elif role == "محقق":
                selection_card = self._get_player_selection_card(
                    "اختر من تحقق منه",
                    "اختر اللاعب الذي تريد التحقق من دوره",
                    user_id
                )
                self.line_bot_api.push_message(
                    PushMessageRequest(to=user_id, messages=[selection_card])
                )
                
        except Exception as e:
            print(f"Failed to send role message: {e}")
    
    def _get_night_phase(self):
        """مرحلة الليل"""
        contents = [
            {
                "type": "text",
                "text": f"الليلة رقم {self.current_round}",
                "size": "xxl",
                "weight": "bold",
                "color": self.colors['primary'],
                "align": "center"
            },
            {"type": "separator", "margin": "lg", "color": self.colors['border']},
            
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "حان وقت الليل",
                        "size": "lg",
                        "weight": "bold",
                        "color": self.colors['text'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "الجميع ينام الان\n\nتحقق من رسائلك الخاصة\nستجد قائمة لاختيار اللاعب",
                        "size": "sm",
                        "color": self.colors['text_light'],
                        "align": "center",
                        "wrap": True,
                        "margin": "md"
                    }
                ],
                "backgroundColor": self.colors['card'],
                "cornerRadius": "12px",
                "paddingAll": "16px",
                "margin": "md"
            },
            
            # التعليمات
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "المافيا: اختاروا ضحية من القائمة",
                        "size": "xs",
                        "color": self.colors['mafia'],
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": "الدكتور: اختر من تحمي من القائمة",
                        "size": "xs",
                        "color": self.colors['doctor'],
                        "wrap": True,
                        "margin": "xs"
                    },
                    {
                        "type": "text",
                        "text": "المحقق: اختر من تتحقق منه من القائمة",
                        "size": "xs",
                        "color": self.colors['detective'],
                        "wrap": True,
                        "margin": "xs"
                    }
                ],
                "backgroundColor": "#EBF5FB",
                "cornerRadius": "12px",
                "paddingAll": "12px",
                "margin": "lg"
            }
        ]
        
        # ارسال الادوار للاعبين مع نوافذ الاختيار
        for player_id in self.alive_players:
            self._send_role_message(player_id, self.roles[player_id])
        
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
    
    def _get_day_voting_card(self):
        """نافذة التصويت النهاري - في القروب"""
        alive_list = [(pid, self.players[pid]) for pid in self.alive_players]
        
        contents = [
            {
                "type": "text",
                "text": f"النهار رقم {self.current_round}",
                "size": "xxl",
                "weight": "bold",
                "color": self.colors['warning'],
                "align": "center"
            },
            {"type": "separator", "margin": "lg", "color": self.colors['border']},
            
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "وقت التصويت",
                        "size": "lg",
                        "weight": "bold",
                        "color": self.colors['text'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "صوت لطرد المشتبه به\nاختر من القائمة",
                        "size": "sm",
                        "color": self.colors['text_light'],
                        "align": "center",
                        "wrap": True,
                        "margin": "sm"
                    }
                ],
                "backgroundColor": self.colors['card'],
                "cornerRadius": "12px",
                "paddingAll": "16px",
                "margin": "md"
            },
            
            {"type": "separator", "margin": "md", "color": self.colors['border']},
            
            {
                "type": "text",
                "text": "اختر من تريد طرده:",
                "size": "sm",
                "weight": "bold",
                "color": self.colors['text'],
                "margin": "md"
            }
        ]
        
        # اضافة ازرار اللاعبين
        for player_id, player_name in alive_list[:10]:
            contents.append({
                "type": "button",
                "action": {
                    "type": "message",
                    "label": player_name,
                    "text": f"صوت:{player_name}"
                },
                "style": "primary",
                "color": self.colors['error'],
                "height": "sm",
                "margin": "sm"
            })
        
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
    
    def _check_win_condition(self) -> Optional[str]:
        """التحقق من شرط الفوز"""
        alive_mafia = len(self.mafia_members & self.alive_players)
        alive_citizens = len(self.alive_players) - alive_mafia
        
        if alive_mafia == 0:
            return "المواطنون"
        elif alive_mafia >= alive_citizens:
            return "المافيا"
        
        return None
    
    def _get_winner_card(self, winner_team):
        """بطاقة الفوز مع كشف جميع الادوار"""
        
        # تجميع اللاعبين حسب الادوار
        role_groups = {
            "مافيا": [],
            "دكتور": [],
            "محقق": [],
            "مواطن": []
        }
        
        for player_id, role in self.roles.items():
            player_name = self.players[player_id]
            is_alive = player_id in self.alive_players
            status = "حي" if is_alive else "ميت"
            role_groups[role].append(f"{player_name} ({status})")
        
        contents = [
            # العنوان الرئيسي
            {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": "انتهت اللعبة",
                    "weight": "bold",
                    "size": "xxl",
                    "color": self.colors['white'],
                    "align": "center"
                }],
                "backgroundColor": self.colors['primary'],
                "paddingAll": "15px",
                "cornerRadius": "12px"
            },
            
            {"type": "separator", "margin": "lg", "color": self.colors['border']},
            
            # الفائز
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"الفائز: {winner_team}",
                        "size": "xl",
                        "weight": "bold",
                        "color": self.colors['success'],
                        "align": "center"
                    }
                ],
                "backgroundColor": self.colors['card'],
                "cornerRadius": "12px",
                "paddingAll": "16px",
                "margin": "md"
            },
            
            {"type": "separator", "margin": "lg", "color": self.colors['border']},
            
            # عنوان الادوار
            {
                "type": "text",
                "text": "كشف الادوار",
                "size": "md",
                "weight": "bold",
                "color": self.colors['text'],
                "align": "center",
                "margin": "md"
            }
        ]
        
        # اضافة كل دور
        for role, color_key in [("مافيا", "mafia"), ("دكتور", "doctor"), ("محقق", "detective"), ("مواطن", "citizen")]:
            if role_groups[role]:
                contents.extend([
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
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
                                ]
                            }
                        ],
                        "backgroundColor": self.colors['card'],
                        "cornerRadius": "8px",
                        "paddingAll": "12px",
                        "margin": "sm"
                    }
                ])
        
        # احصائيات اللعبة
        contents.extend([
            {"type": "separator", "margin": "lg", "color": self.colors['border']},
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "احصائيات اللعبة",
                        "size": "sm",
                        "weight": "bold",
                        "color": self.colors['text']
                    },
                    {
                        "type": "text",
                        "text": f"عدد الجولات: {self.current_round}\nعدد اللاعبين: {len(self.players)}\nالاحياء: {len(self.alive_players)}\nالموتى: {len(self.dead_players)}",
                        "size": "xs",
                        "color": self.colors['text_light'],
                        "wrap": True,
                        "margin": "sm"
                    }
                ],
                "backgroundColor": "#EBF5FB",
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
        """معالجة الاجابات والاوامر"""
        
        if not self.game_active:
            return None
        
        text = user_answer.strip()
        text_lower = text.lower()
        
        # مرحلة الانضمام
        if self.game_phase == "joining":
            if text_lower in ['انضم', 'join']:
                if user_id not in self.players and len(self.players) < self.max_players:
                    self.players[user_id] = display_name
                    return {
                        'response': TextMessage(text=f"{display_name} انضم - العدد: {len(self.players)}"),
                        'points': 0
                    }
            
            elif text_lower in ['ابدأ', 'start', 'بدأ']:
                if len(self.players) >= self.min_players:
                    self._assign_roles()
                    self.game_phase = "night"
                    self.current_round = 1
                    return {
                        'response': self._get_night_phase(),
                        'points': 0
                    }
                else:
                    return {
                        'response': TextMessage(text=f"يحتاج {self.min_players - len(self.players)} لاعبين اضافيين"),
                        'points': 0
                    }
        
        # مرحلة النهار - التصويت
        elif self.game_phase == "day":
            if text.startswith("صوت:"):
                voted_name = text.replace("صوت:", "").strip()
                
                # التحقق من ان اللاعب حي
                if user_id not in self.alive_players:
                    return None
                
                # التحقق من انه لم يصوت بعد
                if user_id in self.voted_users:
                    return {
                        'response': TextMessage(text="لقد صوت بالفعل"),
                        'points': 0
                    }
                
                # البحث عن اللاعب المصوت عليه
                voted_id = None
                for pid, pname in self.players.items():
                    if pname == voted_name and pid in self.alive_players:
                        voted_id = pid
                        break
                
                if voted_id:
                    self.day_votes[voted_id] = self.day_votes.get(voted_id, 0) + 1
                    self.voted_users.add(user_id)
                    return {
                        'response': TextMessage(text=f"تم تسجيل صوتك ضد {voted_name}"),
                        'points': 0
                    }
        
        return None
    
    def end_game(self) -> Dict[str, Any]:
        """انهاء اللعبة"""
        winner = self._check_win_condition()
        self.game_active = False
        
        if not winner:
            winner = "لا احد"
        
        return {
            'game_over': True,
            'points': 1,
            'response': self._get_winner_card(winner)
        }
