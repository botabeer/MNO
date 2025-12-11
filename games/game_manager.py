import logging
from typing import Dict, Optional
from linebot.v3.messaging import TextMessage
from config import Config
from ui_builder import UIBuilder

logger = logging.getLogger(__name__)

class GameManager:
    def __init__(self, db):
        self.db = db
        self.ui = UIBuilder()
        self.active_games = {}
        self.game_sessions = {}
        self.games = self._load_games()
    
    def _load_games(self):
        games = {}
        try:
            from games.iq_game import IqGame
            from games.roulette_game import RouletteGame
            from games.word_color_game import WordColorGame
            from games.scramble_word_game import ScrambleWordGame
            from games.fast_typing_game import FastTypingGame
            from games.opposite_game import OppositeGame
            from games.letters_words_game import LettersWordsGame
            from games.song_game import SongGame
            from games.human_animal_plant_game import HumanAnimalPlantGame
            from games.chain_words_game import ChainWordsGame
            from games.guess_game import GuessGame
            from games.compatibility_game import CompatibilitySystem
            from games.math_game import MathGame
            
            games = {
                "ذكاء": IqGame,
                "روليت": RouletteGame,
                "لون": WordColorGame,
                "ترتيب": ScrambleWordGame,
                "اسرع": FastTypingGame,
                "ضد": OppositeGame,
                "تكوين": LettersWordsGame,
                "اغنيه": SongGame,
                "لعبة": HumanAnimalPlantGame,
                "سلسلة": ChainWordsGame,
                "خمن": GuessGame,
                "توافق": CompatibilitySystem,
                "رياضيات": MathGame
            }
            logger.info(f"Loaded {len(games)} games")
        except Exception as e:
            logger.error(f"Game loading error: {e}")
        return games
    
    def get_active_count(self) -> int:
        return len(self.active_games)
    
    def get_total_games(self) -> int:
        return len(self.games)
    
    def stop_game(self, context_id: str) -> Optional[str]:
        if context_id in self.active_games:
            game = self.active_games[context_id]
            game_name = game.game_name
            del self.active_games[context_id]
            self.game_sessions.pop(context_id, None)
            return game_name
        return None
    
    def process_message(self, context_id: str, user_id: str, username: str,
                       text: str, is_registered: bool, theme: str, source_type: str) -> Optional[Dict]:
        normalized = Config.normalize(text)
        
        if normalized in self.games:
            game_config = Config.get_game_config(normalized)
            
            if not game_config.get('no_registration') and not is_registered:
                return {'messages': [TextMessage(text="يجب التسجيل اولا")], 'points': 0}
            
            if game_config.get('group_only') and source_type not in ["group", "room"]:
                return {'messages': [TextMessage(text="للمجموعات فقط")], 'points': 0}
            
            GameClass = self.games[normalized]
            game = GameClass(None)
            
            if hasattr(game, 'set_theme'):
                game.set_theme(theme)
            if hasattr(game, 'set_database'):
                game.set_database(self.db)
            
            self.active_games[context_id] = game
            
            if not game_config.get('no_registration'):
                session_id = self.db.create_session(user_id, normalized)
                self.game_sessions[context_id] = {'session_id': session_id, 'user_id': user_id}
            
            question = game.start_game()
            return {'messages': [question], 'points': 0}
        
        if context_id in self.active_games:
            game = self.active_games[context_id]
            result = game.check_answer(text, user_id, username)
            
            if result:
                points = result.get('points', 0)
                messages = []
                
                if result.get('message'):
                    messages.append(TextMessage(text=result['message']))
                
                if result.get('game_over'):
                    if context_id in self.game_sessions:
                        session = self.game_sessions[context_id]
                        self.db.complete_session(session['session_id'], points)
                        del self.game_sessions[context_id]
                    del self.active_games[context_id]
                    if points > 0 and is_registered:
                        self.db.record_game_stat(user_id, game.game_name, points, True)
                elif result.get('response'):
                    messages.append(result['response'])
                
                return {'messages': messages, 'points': points}
        return None
