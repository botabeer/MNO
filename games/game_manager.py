import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GameManager:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.active_games = {}
        self.withdrawn_users = {}
        self.waiting_for_name = set()
        
    def set_waiting_for_name(self, user_id, waiting):
        if waiting:
            self.waiting_for_name.add(user_id)
        else:
            self.waiting_for_name.discard(user_id)
    
    def is_waiting_for_name(self, user_id):
        return user_id in self.waiting_for_name
    
    def stop_game(self, group_id):
        if group_id in self.active_games:
            del self.active_games[group_id]
            return True
        return False
    
    def add_withdrawn_user(self, group_id, user_id):
        if group_id not in self.withdrawn_users:
            self.withdrawn_users[group_id] = set()
        self.withdrawn_users[group_id].add(user_id)
    
    def cleanup_inactive_games(self, timeout_minutes=30):
        try:
            now = datetime.now()
            inactive = []
            
            for group_id, game in self.active_games.items():
                if hasattr(game, 'game_start_time') and game.game_start_time:
                    elapsed = (now - game.game_start_time).total_seconds() / 60
                    if elapsed > timeout_minutes:
                        inactive.append(group_id)
            
            for group_id in inactive:
                del self.active_games[group_id]
                logger.info(f"Cleaned up inactive game: {group_id}")
            
            return len(inactive)
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return 0
    
    def process_message(self, text, user_id, group_id, display_name, is_registered):
        from games import (
            SongGame, OppositeGame, ChainWordsGame, 
            FastTypingGame, HumanAnimalPlantGame,
            LettersWordsGame, CategoryLetterGame, CompatibilityGame
        )
        
        text_normalized = text.lower().strip()
        
        game_map = {
            "اغنيه": ("اغنيه", SongGame, True),
            "ضد": ("ضد", OppositeGame, True),
            "سلسله": ("سلسله", ChainWordsGame, True),
            "اسرع": ("اسرع", FastTypingGame, True),
            "لعبه": ("لعبه", HumanAnimalPlantGame, True),
            "تكوين": ("تكوين", LettersWordsGame, True),
            "فئه": ("فئه", CategoryLetterGame, True),
            "توافق": ("توافق", CompatibilityGame, False),
        }
        
        if text_normalized in game_map:
            game_key, GameClass, requires_registration = game_map[text_normalized]
            
            if requires_registration and not is_registered:
                from linebot.models import TextSendMessage
                return TextSendMessage(text="يجب التسجيل أولاً. اكتب: تسجيل")
            
            game = GameClass(self.line_bot_api)
            self.active_games[group_id] = game
            
            try:
                response = game.start_game()
                return response
            except Exception as e:
                logger.error(f"Error starting game {game_key}: {e}")
                from linebot.models import TextSendMessage
                return TextSendMessage(text="حدث خطأ في بدء اللعبة")
        
        if group_id in self.active_games:
            game = self.active_games[group_id]
            
            try:
                result = game.check_answer(text, user_id, display_name)
                
                if result:
                    responses = []
                    
                    if result.get('message'):
                        from linebot.models import TextSendMessage
                        responses.append(TextSendMessage(text=result['message']))
                    
                    if result.get('response'):
                        responses.append(result['response'])
                    
                    if result.get('next_question'):
                        next_q = game.get_question()
                        if next_q:
                            responses.append(next_q)
                    
                    if result.get('game_over'):
                        del self.active_games[group_id]
                        
                        if is_registered and result.get('points', 0) > 0:
                            from database import Database
                            Database.update_user_points(
                                user_id, 
                                result['points'], 
                                result.get('won', True),
                                game.game_name
                            )
                    
                    return responses if len(responses) > 1 else (responses[0] if responses else None)
                
            except Exception as e:
                logger.error(f"Error processing game answer: {e}")
        
        return None
