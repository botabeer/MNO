"""
Mafia Game - لعبة المافيا
==========================
"""

from linebot.models import TextSendMessage, FlexSendMessage
import random
from datetime import datetime, timedelta
from constants import MAFIA_CONFIG, POINTS, COLORS

class MafiaGame:
    """لعبة المافيا"""
    
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.players = {}  # {user_id: {'name': '', 'role': '', 'alive': True}}
        self.phase = 'registration'  # registration, night, discussion, voting, ended
        self.day_number = 0
        self.votes = {}
        self.night_actions = {}
        self.start_time = None
        self.phase_end_time = None
        
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
                        "type": "text",
                        "text": "التسجيل مفتوح",
                        "size": "md",
                        "weight": "bold",
                        "color": COLORS['text_dark']
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": COLORS['border']
                    },
                    {
                        "type": "text",
                        "text": f"اللاعبون: {len(self.players)}",
                        "size": "sm",
                        "color": COLORS['text_light'],
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": f"الحد الأدنى: {MAFIA_CONFIG['min_players']}",
                        "size": "sm",
                        "color": COLORS['text_light'],
                        "margin": "xs"
                    },
                    {
                        "type": "text",
                        "text": "اكتب 'انضم' للتسجيل",
                        "size": "xs",
                        "color": COLORS['text_light'],
                        "margin": "lg",
                        "wrap": True
                    }
                ],
                "backgroundColor": COLORS['white'],
                "paddingAll": "20px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "بدء اللعبة", "text": "بدء مافيا"},
                        "style": "primary",
                        "color": COLORS['primary'],
                        "height": "sm"
                    }
                ],
                "backgroundColor": COLORS['background'],
                "paddingAll": "12px"
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
            'message': f"{display_name} انضم للعبة - العدد: {len(self.players)}"
        }
    
    def start_roles_assignment(self):
        """توزيع الأدوار"""
        if len(self.players) < MAFIA_CONFIG['min_players']:
            return {
                'success': False,
                'message': f'يجب وجود {MAFIA_CONFIG['min_players']} لاعبين على الأقل'
            }
        
        # الحصول على توزيع الأدوار
        player_count = len(self.players)
        roles_config = MAFIA_CONFIG['roles'].get(player_count)
        
        if not roles_config:
            # استخدام أقرب تكوين
            roles_config = MAFIA_CONFIG['roles'][min(MAFIA_CONFIG['roles'].keys(), 
                                                      key=lambda x: abs(x - player_count))]
        
        # إنشاء قائمة الأدوار
        roles = []
        roles.extend(['mafia'] * roles_config['mafia'])
        roles.extend(['detective'] * roles_config['detective'])
        roles.extend(['citizen'] * roles_config['citizen'])
        
        # توزيع عشوائي
        random.shuffle(roles)
        player_ids = list(self.players.keys())
        
        for i, user_id in enumerate(player_ids):
            if i < len(roles):
                self.players[user_id]['role'] = roles[i]
        
        self.phase = 'night'
        self.day_number = 1
        self.phase_end_time = datetime.now() + timedelta(seconds=MAFIA_CONFIG['night_time'])
        
        return {'success': True, 'phase': 'night'}
    
    def get_role_message(self, user_id):
        """الحصول على رسالة الدور"""
        if user_id not in self.players:
            return None
        
        role = self.players[user_id]['role']
        role_names = {
            'mafia': 'المافيا',
            'detective': 'المحقق',
            'citizen': 'مواطن'
        }
        
        role_descriptions = {
            'mafia': 'أنت من المافيا - اختر ضحية كل ليلة',
            'detective': 'أنت المحقق - اكتشف المافيا',
            'citizen': 'أنت مواطن - ساعد في العثور على المافيا'
        }
        
        return {
            'role': role_names.get(role, 'غير محدد'),
            'description': role_descriptions.get(role, '')
        }
    
    def night_action(self, user_id, target_id):
        """إجراء ليلي"""
        if self.phase != 'night':
            return {'success': False, 'message': 'ليس وقت الليل'}
        
        if user_id not in self.players or not self.players[user_id]['alive']:
            return {'success': False, 'message': 'لست في اللعبة'}
        
        role = self.players[user_id]['role']
        
        if role == 'mafia':
            self.night_actions[user_id] = {'action': 'kill', 'target': target_id}
            return {'success': True, 'message': 'تم تسجيل اختيارك'}
        elif role == 'detective':
            self.night_actions[user_id] = {'action': 'investigate', 'target': target_id}
            target_role = self.players.get(target_id, {}).get('role')
            is_mafia = target_role == 'mafia'
            return {
                'success': True,
                'message': f"التحقيق: {'مافيا' if is_mafia else 'بريء'}"
            }
        
        return {'success': False, 'message': 'لا يمكنك القيام بهذا الإجراء'}
    
    def end_night(self):
        """إنهاء الليل"""
        # جمع أصوات المافيا
        mafia_votes = {}
        for action in self.night_actions.values():
            if action['action'] == 'kill':
                target = action['target']
                mafia_votes[target] = mafia_votes.get(target, 0) + 1
        
        # قتل الهدف الأكثر تصويتاً
        victim = None
        if mafia_votes:
            victim = max(mafia_votes, key=mafia_votes.get)
            if victim in self.players:
                self.players[victim]['alive'] = False
        
        self.phase = 'discussion'
        self.night_actions = {}
        self.phase_end_time = datetime.now() + timedelta(seconds=MAFIA_CONFIG['discussion_time'])
        
        return {'victim': victim, 'victim_name': self.players.get(victim, {}).get('name', 'غير معروف')}
    
    def vote(self, user_id, target_id):
        """التصويت"""
        if self.phase != 'voting':
            return {'success': False, 'message': 'ليس وقت التصويت'}
        
        if user_id not in self.players or not self.players[user_id]['alive']:
            return {'success': False, 'message': 'لست في اللعبة'}
        
        self.votes[user_id] = target_id
        return {'success': True, 'message': 'تم تسجيل تصويتك'}
    
    def end_voting(self):
        """إنهاء التصويت"""
        # جمع الأصوات
        vote_counts = {}
        for target in self.votes.values():
            vote_counts[target] = vote_counts.get(target, 0) + 1
        
        # إعدام الشخص الأكثر تصويتاً
        executed = None
        if vote_counts:
            executed = max(vote_counts, key=vote_counts.get)
            if executed in self.players:
                self.players[executed]['alive'] = False
        
        self.votes = {}
        
        # التحقق من نهاية اللعبة
        game_over = self.check_game_over()
        
        if not game_over:
            self.phase = 'night'
            self.day_number += 1
            self.phase_end_time = datetime.now() + timedelta(seconds=MAFIA_CONFIG['night_time'])
        
        return {
            'executed': executed,
            'executed_name': self.players.get(executed, {}).get('name', 'غير معروف'),
            'executed_role': self.players.get(executed, {}).get('role', 'غير معروف'),
            'game_over': game_over
        }
    
    def check_game_over(self):
        """التحقق من نهاية اللعبة"""
        alive_mafia = sum(1 for p in self.players.values() 
                         if p['alive'] and p['role'] == 'mafia')
        alive_citizens = sum(1 for p in self.players.values() 
                            if p['alive'] and p['role'] in ['citizen', 'detective'])
        
        if alive_mafia == 0:
            self.phase = 'ended'
            return {'winner': 'citizens', 'reason': 'تم القضاء على جميع المافيا'}
        
        if alive_mafia >= alive_citizens:
            self.phase = 'ended'
            return {'winner': 'mafia', 'reason': 'المافيا تسيطر على المدينة'}
        
        return None
    
    def get_game_status(self):
        """الحصول على حالة اللعبة"""
        alive_count = sum(1 for p in self.players.values() if p['alive'])
        
        return {
            'phase': self.phase,
            'day': self.day_number,
            'alive_players': alive_count,
            'total_players': len(self.players)
        }
    
    def check_answer(self, text, user_id, display_name):
        """معالجة إجابات اللاعبين"""
        text = text.strip().lower()
        
        # أوامر خاصة باللعبة
        if text == 'انضم' and self.phase == 'registration':
            result = self.add_player(user_id, display_name)
            return {
                'correct': result['success'],
                'response': TextSendMessage(text=result['message']),
                'game_over': False
            }
        
        if text == 'بدء مافيا' and self.phase == 'registration':
            result = self.start_roles_assignment()
            if result['success']:
                # إرسال الأدوار بشكل خاص لكل لاعب
                return {
                    'correct': True,
                    'response': TextSendMessage(text='تم توزيع الأدوار - تحقق من رسائلك الخاصة'),
                    'game_over': False,
                    'assign_roles': True
                }
            else:
                return {
                    'correct': False,
                    'response': TextSendMessage(text=result['message']),
                    'game_over': False
                }
        
        return None
