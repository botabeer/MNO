# game_manager.py
# مدير الجلسات - يحتفظ بمثيلات الألعاب لجروب/يوزر
from collections import defaultdict

class GameManager:
    def __init__(self):
        # structure: {group_id: {game_name: game_instance}}
        self.sessions = defaultdict(dict)
        # store activity timestamps for inactivity handling (simplified)
        self.last_active = {}

    def start_game(self, group_id: str, game_name: str, game_instance):
        self.sessions[group_id][game_name] = game_instance
        self.last_active[(group_id, game_name)] = __import__('time').time()
        return game_instance

    def get_game(self, group_id: str, game_name: str):
        return self.sessions[group_id].get(game_name)

    def end_game(self, group_id: str, game_name: str):
        if game_name in self.sessions[group_id]:
            del self.sessions[group_id][game_name]

    def touch(self, group_id: str, game_name: str):
        self.last_active[(group_id, game_name)] = __import__('time').time()

    def cleanup_inactive(self, older_than_seconds=30*24*3600):
        import time
        now = time.time()
        to_remove = []
        for key, t in self.last_active.items():
            if now - t > older_than_seconds:
                group_id, game_name = key
                to_remove.append((group_id, game_name))
        for g, gn in to_remove:
            self.end_game(g, gn)
            del self.last_active[(g, gn)]
