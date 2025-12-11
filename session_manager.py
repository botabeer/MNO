from database import Database
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        self.registered_users = {}
        self.withdrawn_users = {}
        self.waiting_for_name = {}
    
    def is_user_registered(self, group_id, user_id):
        return group_id in self.registered_users and user_id in self.registered_users[group_id]
    
    def is_user_withdrawn(self, group_id, user_id):
        return group_id in self.withdrawn_users and user_id in self.withdrawn_users[group_id]
    
    def register_user(self, group_id, user_id, display_name):
        if group_id not in self.registered_users:
            self.registered_users[group_id] = {}
        self.registered_users[group_id][user_id] = display_name
        
        if group_id in self.withdrawn_users and user_id in self.withdrawn_users[group_id]:
            del self.withdrawn_users[group_id][user_id]
        
        Database.register_or_update_user(user_id, display_name)
        logger.info(f"User registered: {user_id} as {display_name}")
    
    def withdraw_user(self, group_id, user_id):
        if group_id in self.registered_users and user_id in self.registered_users[group_id]:
            del self.registered_users[group_id][user_id]
        
        if group_id not in self.withdrawn_users:
            self.withdrawn_users[group_id] = {}
        self.withdrawn_users[group_id][user_id] = True
        
        logger.info(f"User withdrawn: {user_id}")
        return True
    
    def get_user_display_name(self, group_id, user_id):
        if self.is_user_registered(group_id, user_id):
            return self.registered_users[group_id][user_id]
        
        stats = Database.get_user_stats(user_id)
        if stats and stats.get('display_name'):
            return stats['display_name']
        
        return None
    
    def is_waiting_for_name(self, user_id):
        return self.waiting_for_name.get(user_id, False)
    
    def set_waiting_for_name(self, user_id, waiting):
        if waiting:
            self.waiting_for_name[user_id] = True
        elif user_id in self.waiting_for_name:
            del self.waiting_for_name[user_id]
