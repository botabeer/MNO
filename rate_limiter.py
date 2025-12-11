from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_requests=50, time_window=3600):
        self.user_requests = defaultdict(list)
        self.max_requests = max_requests
        self.time_window = time_window
    
    def is_allowed(self, user_id):
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.time_window)
        
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id]
            if req_time > cutoff
        ]
        
        if len(self.user_requests[user_id]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for user: {user_id}")
            return False
        
        self.user_requests[user_id].append(now)
        return True
    
    def reset_user(self, user_id):
        if user_id in self.user_requests:
            del self.user_requests[user_id]
