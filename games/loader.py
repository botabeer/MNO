"""
Game Loader - Bot Mesh v9.0
"""

import importlib
import os
from pathlib import Path

class GameLoader:
    """محمّل الألعاب الديناميكي"""
    
    def __init__(self):
        self.games = {}
        self._load_all_games()
    
    def _load_all_games(self):
        """تحميل جميع الألعاب من المجلد"""
        games_dir = Path(__file__).parent
        
        for file in games_dir.glob("*.py"):
            if file.name in ["__init__.py", "loader.py", "base.py"]:
                continue
            
            module_name = file.stem
            try:
                module = importlib.import_module(f"games.{module_name}")
                
                # البحث عن الكلاس الذي ينتهي بـ Game
                for attr_name in dir(module):
                    if attr_name.endswith("Game") and not attr_name.startswith("_"):
                        game_class = getattr(module, attr_name)
                        if hasattr(game_class, "name"):
                            game_name = game_class.name
                            self.games[game_name] = game_class
            except Exception as e:
                print(f"Error loading game {module_name}: {e}")
    
    def get_game(self, game_name):
        """الحصول على كلاس اللعبة"""
        return self.games.get(game_name)
    
    def get_all_games(self):
        """الحصول على جميع الألعاب"""
        return self.games
    
    def game_exists(self, game_name):
        """التحقق من وجود اللعبة"""
        return game_name in self.games
