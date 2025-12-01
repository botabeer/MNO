"""
Mafia Game - لعبة المافيا الكاملة
================================
"""

from linebot.models import TextSendMessage, FlexSendMessage
import random
from datetime import datetime, timedelta
from constants import MAFIA_CONFIG, POINTS, COLORS
import logging

logger = logging.getLogger("mafia-bot")

class MafiaGame:
    """لعبة المافيا"""
    
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.players = {}  # {user_id: {'name': '', 'role': '', 'alive': True}}
        self.phase = 'registration'
        self.day_number = 0
        self.votes = {}
        self.night_actions = {}
        self.start_time = None
        self.phase_end_time = None
        self.group_id = None
    
    def start_game(self):
        """بدء التسجيل"""
        self.start_time = datetime.now()
        return FlexSendMessage(
            alt_text="لعبة المافيا",
            contents=self._registration_card()
        )
    
    def _registration_card(self):
        """بطاقة التسجيل"""
        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "لعبة المافيا",
                        "weight": "bold",
                        "size": "xxl",
                        "color": COLORS['white'],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "فتح التسجيل",
                        "size": "sm",
                        "color": COLORS['white'],
                        "align": "center",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": COLORS['primary'],
                "paddingAll": "24px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "اللاعبون",
                                "size": "sm",
                                "color": COLORS['text_light'],
                                "flex": 2
                            },
                            {
                                "type": "text",
                                "text": str(len(self.players)),
                                "size": "xl",
                                "color": COLORS['primary'],
                                "flex": 1,
                                "align": "end",
                                "weight": "bold"
                            }
                        ],
                        "backgroundColor": COLORS['light'],
                        "cornerRadius": "md",
                        "paddingAll": "12px"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": COLORS['border']
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "الحد الأدنى",
                                "size": "xs",
                                "color": COLORS['text_light'],
                                "flex": 2
                            },
                            {
                                "type": "text",
                                "text": str(MAFIA_CONFIG['min_players']),
                                "size": "sm",
                                "color": COLORS['text_dark'],
                                "flex": 1,
                                "align": "end",
                                "weight": "bold"
                            }
                        ],
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "الحد الأقصى",
                                "size": "xs",
                                "color": COLORS['text_light'],
                                "flex": 2
                            },
                            {
                                "type": "text",
                                "text": str(MAFIA_CONFIG['max_players']),
                                "size": "sm",
                                "color": COLORS['text_dark'],
                                "flex": 1,
                                "align": "end",
                                "weight": "bold"
                            }
                        ],
                        "margin": "sm"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": COLORS['border']
                    },
                    {
                        "type": "text",
                        "text": "الأدوار المتاحة",
                        "size": "sm",
                        "weight": "bold",
                        "color": COLORS['text_dark'],
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": "مافيا - محقق - دكتور - مواطن",
                        "size": "xs",
                        "color": COLORS['text_light'],
                        "wrap": True,
                        "margin": "xs"
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "20px",
                "spacing": "none"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "للانضمام اكتب: انضم مافيا",
                        "size": "xs",
                        "color": COLORS['medium'],
                        "align": "center"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "انضم", "text": "انضم مافيا"},
                                "style": "primary",
                                "color": COLORS['primary'],
                                "height": "sm"
                            },
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "بدء", "text": "بدء مافيا"},
                                "style": "secondary",
                                "height": "sm"
                            }
                        ],
                        "spacing": "sm",
                        "margin": "md"
                    }
                ],
                "backgroundColor": COLORS['background'],
                "paddingAll": "16px"
            }
        }
    
    def add_player(self, user_id, display_name):
        """إضافة لاعب"""
        if self.phase != 'registration':
            return {'success': False, 'message': 'اللعبة بدأت بالفعل'}
        
        if len(self.players) >= MAFIA_CONFIG['max_players']:
            return {'success': False, 'message': 'اللعبة ممتلئة'}
        
        if user_id in self.players:
            return {'success': False, 'message': 'أنت مسجل بالفعل'}
        
        self.players[user_id] = {
            'name': display_name,
            'role': None,
            'alive': True
        }
        
        return {
            'success': True,
            'message': f"{display_name} انضم للعبة\nالعدد: {len(self.players)}/{MAFIA_CONFIG['max_players']}"
        }
    
    def start_roles_assignment(self):
        """توزيع الأدوار"""
        if len(self.players) < MAFIA_CONFIG['min_players']:
            return {
                'success': False,
                'message': f'يجب وجود {MAFIA_CONFIG["min_players"]} لاعبين على الأقل'
            }
        
        player_count = len(self.players)
        roles_config = MAFIA_CONFIG['roles'].get(player_count)
        
        if not roles_config:
            roles_config = MAFIA_CONFIG['roles'][min(MAFIA_CONFIG['roles'].keys(), 
                                                      key=lambda x: abs(x - player_count))]
        
        # إنشاء قائمة الأدوار
        roles = []
        roles.extend(['mafia'] * roles_config['mafia'])
        roles.extend(['detective'] * roles_config['detective'])
        roles.extend(['doctor'] * roles_config.get('doctor', 1))
        
        remaining = player_count - len(roles)
        if remaining > 0:
            roles.extend(['citizen'] * remaining)
        
        # توزيع عشوائي
        random.shuffle(roles)
        player_ids = list(self.players.keys())
        
        for i, user_id in enumerate(player_ids):
            if i < len(roles):
                self.players[user_id]['role'] = roles[i]
        
        self.phase = 'night'
        self.day_number = 1
        self.phase_end_time = datetime.now() + timedelta(seconds=MAFIA_CONFIG['night_time'])
        
        return {'success': True, 'phase': 'night', 'roles_assigned': True}
    
    def get_role_message(self, user_id):
        """الحصول على رسالة الدور"""
        if user_id not in self.players:
            return None
        
        role = self.players[user_id]['role']
        name = self.players[user_id]['name']
        
        role_info = {
            'mafia': {
                'name': 'المافيا',
                'description': 'أنت من المافيا\n\nمهمتك: القضاء على المواطنين\n\nكل ليلة اختر ضحية بالأمر:\nقتل @الاسم',
                'color': COLORS['primary']
            },
            'detective': {
                'name': 'المحقق',
                'description': 'أنت المحقق\n\nمهمتك: اكتشاف المافيا\n\nكل ليلة تحقق من شخص بالأمر:\nتحقق @الاسم',
                'color': COLORS['secondary']
            },
            'doctor': {
                'name': 'الدكتور',
                'description': 'أنت الدكتور\n\nمهمتك: حماية المواطنين\n\nكل ليلة احم شخصاً بالأمر:\nاحم @الاسم',
                'color': COLORS['text_dark']
            },
            'citizen': {
                'name': 'مواطن',
                'description': 'أنت مواطن\n\nمهمتك: العثور على المافيا\n\nشارك في النقاش والتصويت',
                'color': COLORS['text_light']
            }
        }
        
        info = role_info.get(role, role_info['citizen'])
        
        return FlexSendMessage(
            alt_text=f"دورك: {info['name']}",
            contents={
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "دورك في اللعبة",
                            "weight": "bold",
                            "size": "xl",
                            "color": COLORS['white'],
                            "align": "center"
                        }
                    ],
                    "backgroundColor": info['color'],
                    "paddingAll": "20px"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": info['name'],
                            "size": "xxl",
                            "weight": "bold",
                            "color": info['color'],
                            "align": "center"
                        },
                        {
                            "type": "separator",
                            "margin": "lg",
                            "color": COLORS['border']
                        },
                        {
                            "type": "text",
                            "text": info['description'],
                            "size": "sm",
                            "color": COLORS['text_dark'],
                            "wrap": True,
                            "margin": "lg"
                        }
                    ],
                    "backgroundColor": COLORS['white'],
                    "paddingAll": "24px"
                }
            }
        )
    
    def night_action(self, user_id, action_type, target_name):
        """إجراء ليلي"""
        if self.phase != 'night':
            return {'success': False, 'message': 'ليس وقت الليل'}
        
        if user_id not in self.players or not self.players[user_id]['alive']:
            return {'success': False, 'message': 'لست في اللعبة'}
        
        role = self.players[user_id]['role']
        
        # البحث عن الهدف
        target_id = None
        for pid, pdata in self.players.items():
            if pdata['name'].lower() == target_name.lower() and pdata['alive']:
                target_id = pid
                break
        
        if not target_id:
            return {'success': False, 'message': 'لم يتم العثور على اللاعب'}
        
        if action_type == 'قتل' and role == 'mafia':
            self.night_actions[user_id] = {'action': 'kill', 'target': target_id}
            return {'success': True, 'message': 'تم تسجيل اختيارك'}
        
        elif action_type == 'تحقق' and role == 'detective':
            target_role = self.players[target_id]['role']
            is_mafia = target_role == 'mafia'
            self.night_actions[user_id] = {'action': 'investigate', 'target': target_id}
            return {
                'success': True,
                'message': f"نتيجة التحقيق عن {target_name}:\n{'مافيا' if is_mafia else 'بريء'}"
            }
        
        elif action_type == 'احم' and role == 'doctor':
            self.night_actions[user_id] = {'action': 'protect', 'target': target_id}
            return {'success': True, 'message': 'تم تسجيل حمايتك'}
        
        return {'success': False, 'message': 'لا يمكنك القيام بهذا الإجراء'}
    
    def end_night(self):
        """إنهاء الليل"""
        # جمع أصوات المافيا
        mafia_votes = {}
        protected = None
        
        for action in self.night_actions.values():
            if action['action'] == 'kill':
                target = action['target']
                mafia_votes[target] = mafia_votes.get(target, 0) + 1
            elif action['action'] == 'protect':
                protected = action['target']
        
        # قتل الهدف الأكثر تصويتاً (إلا إذا كان محمياً)
        victim = None
        victim_name = None
        
        if mafia_votes:
            victim = max(mafia_votes, key=mafia_votes.get)
            
            if victim != protected and victim in self.players:
                self.players[victim]['alive'] = False
                victim_name = self.players[victim]['name']
        
        self.phase = 'discussion'
        self.night_actions = {}
        self.phase_end_time = datetime.now() + timedelta(seconds=MAFIA_CONFIG['discussion_time'])
        
        return {
            'victim': victim,
            'victim_name': victim_name,
            'saved': victim == protected
        }
    
    def vote(self, user_id, target_name):
        """التصويت"""
        if self.phase != 'voting':
            return {'success': False, 'message': 'ليس وقت التصويت'}
        
        if user_id not in self.players or not self.players[user_id]['alive']:
            return {'success': False, 'message': 'لست في اللعبة'}
        
        # البحث عن الهدف
        target_id = None
        for pid, pdata in self.players.items():
            if pdata['name'].lower() == target_name.lower() and pdata['alive']:
                target_id = pid
                break
        
        if not target_id:
            return {'success': False, 'message': 'لم يتم العثور على اللاعب'}
        
        self.votes[user_id] = target_id
        return {'success': True, 'message': 'تم تسجيل تصويتك'}
    
    def end_voting(self):
        """إنهاء التصويت"""
        vote_counts = {}
        for target in self.votes.values():
            vote_counts[target] = vote_counts.get(target, 0) + 1
        
        executed = None
        executed_name = None
        executed_role = None
        
        if vote_counts:
            executed = max(vote_counts, key=vote_counts.get)
            if executed in self.players:
                self.players[executed]['alive'] = False
                executed_name = self.players[executed]['name']
                executed_role = self.players[executed]['role']
        
        self.votes = {}
        
        game_over = self.check_game_over()
        
        if not game_over:
            self.phase = 'night'
            self.day_number += 1
            self.phase_end_time = datetime.now() + timedelta(seconds=MAFIA_CONFIG['night_time'])
        
        return {
            'executed': executed,
            'executed_name': executed_name,
            'executed_role': executed_role,
            'game_over': game_over
        }
    
    def check_game_over(self):
        """التحقق من نهاية اللعبة"""
        alive_mafia = sum(1 for p in self.players.values() 
                         if p['alive'] and p['role'] == 'mafia')
        alive_citizens = sum(1 for p in self.players.values() 
                            if p['alive'] and p['role'] in ['citizen', 'detective', 'doctor'])
        
        if alive_mafia == 0:
            self.phase = 'ended'
            return {'winner': 'citizens', 'reason': 'تم القضاء على جميع المافيا'}
        
        if alive_mafia >= alive_citizens:
            self.phase = 'ended'
            return {'winner': 'mafia', 'reason': 'المافيا تسيطر على المدينة'}
        
        return None
    
    def get_alive_players(self):
        """الحصول على اللاعبين الأحياء"""
        return {uid: data for uid, data in self.players.items() if data['alive']}
    
    def get_game_status(self):
        """الحصول على حالة اللعبة"""
        alive_count = sum(1 for p in self.players.values() if p['alive'])
        
        return FlexSendMessage(
            alt_text="حالة اللعبة",
            contents={
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"اليوم {self.day_number}",
                            "weight": "bold",
                            "size": "xl",
                            "color": COLORS['white'],
                            "align": "center"
                        }
                    ],
                    "backgroundColor": COLORS['primary'],
                    "paddingAll": "20px"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "المرحلة",
                                    "size": "sm",
                                    "color": COLORS['text_light'],
                                    "flex": 2
                                },
                                {
                                    "type": "text",
                                    "text": self.phase,
                                    "size": "md",
                                    "color": COLORS['text_dark'],
                                    "flex": 3,
                                    "align": "end",
                                    "weight": "bold"
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "الأحياء",
                                    "size": "sm",
                                    "color": COLORS['text_light'],
                                    "flex": 2
                                },
                                {
                                    "type": "text",
                                    "text": f"{alive_count}/{len(self.players)}",
                                    "size": "md",
                                    "color": COLORS['text_dark'],
                                    "flex": 3,
                                    "align": "end",
                                    "weight": "bold"
                                }
                            ],
                            "margin": "md"
                        }
                    ],
                    "backgroundColor": COLORS['white'],
                    "paddingAll": "20px"
                }
            }
        )
    
    def check_answer(self, text, user_id, display_name):
        """معالجة إجابات اللاعبين"""
        text = text.strip()
        
        # أوامر خاصة باللعبة
        if text == 'انضم مافيا' and self.phase == 'registration':
            result = self.add_player(user_id, display_name)
            return {
                'correct': result['success'],
                'response': TextSendMessage(text=result['message']),
                'game_over': False
            }
        
        if text == 'بدء مافيا' and self.phase == 'registration':
            result = self.start_roles_assignment()
            if result['success']:
                return {
                    'correct': True,
                    'response': TextSendMessage(text='جاري توزيع الأدوار...'),
                    'game_over': False,
                    'assign_roles': True
                }
            else:
                return {
                    'correct': False,
                    'response': TextSendMessage(text=result['message']),
                    'game_over': False
                }
        
        # أوامر الليل (يجب أن تكون في الخاص)
        if self.phase == 'night':
            if text.startswith('قتل ') or text.startswith('تحقق ') or text.startswith('احم '):
                parts = text.split(maxsplit=1)
                if len(parts) == 2:
                    action_type = parts[0]
                    target_name = parts[1].replace('@', '')
                    result = self.night_action(user_id, action_type, target_name)
                    return {
                        'correct': result['success'],
                        'response': TextSendMessage(text=result['message']),
                        'game_over': False
                    }
        
        # أوامر التصويت
        if self.phase == 'voting' and text.startswith('صوت '):
            target_name = text[5:].replace('@', '')
            result = self.vote(user_id, target_name)
            return {
                'correct': result['success'],
                'response': TextSendMessage(text=result['message']),
                'game_over': False
            }
        
        return None
