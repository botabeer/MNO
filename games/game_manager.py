import os
import random
from typing import Optional, Dict, Any, Type

from games.song_game import SongGame
from games.opposite_game import OppositeGame
from games.fast_typing_game import FastTypingGame
from games.chain_words_game import ChainWordsGame
from games.human_animal_plant_game import HumanAnimalPlantGame
from games.letters_words_game import LettersWordsGame
from games.category_letter_game import CategoryLetterGame
from games.compatibility_game import CompatibilityGame
from games.mafia_game import MafiaGame


class GameManager:
    """
    Manages active games for different groups and provides helper utilities.
    Each group can only have ONE active game at a time.
    """

    # Cache loaded text files so they don’t reload every time GameManager is created
    _cached_files: Dict[str, list] = {}

    # Central registry for all games (easier to add new games)
    GAME_CLASSES: Dict[str, Type] = {
        "song": SongGame,
        "opposite": OppositeGame,
        "fast_typing": FastTypingGame,
        "chain": ChainWordsGame,
        "human_animal": HumanAnimalPlantGame,
        "letters": LettersWordsGame,
        "category": CategoryLetterGame,
        "compatibility": CompatibilityGame,
        "mafia": MafiaGame,
    }

    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.active_games: Dict[str, Dict[str, Any]] = {}

        # Load all external text-based content
        self.questions = self._load_file("games/questions.txt")
        self.challenges = self._load_file("games/challenges.txt")
        self.confessions = self._load_file("games/confessions.txt")
        self.mentions = self._load_file("games/mentions.txt")

    # --------------------------------------------------------------
    # Helper: Load text file with caching
    # --------------------------------------------------------------
    def _load_file(self, filepath: str) -> list:
        """
        Load lines from a text file and cache them so subsequent
        GameManager instances do not reload from disk.
        """
        if filepath in self._cached_files:
            return self._cached_files[filepath]

        try:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip()]
                    self._cached_files[filepath] = lines
                    return lines
        except Exception as e:
            print(f"Error loading {filepath}: {e}")

        self._cached_files[filepath] = []
        return []

    # --------------------------------------------------------------
    # Game control
    # --------------------------------------------------------------
    def start_game(self, game_type: str, group_id: str) -> Optional[Any]:
        """
        Start a game for a group. If a game was already active,
        it gets replaced with the new one.
        """
        game_type = game_type.lower()

        if game_type not in self.GAME_CLASSES:
            return None

        game_class = self.GAME_CLASSES[game_type]
        game_instance = game_class(self.line_bot_api)

        self.active_games[group_id] = {
            "type": game_type,
            "game": game_instance,
        }

        return game_instance.start_game()

    def get_game(self, group_id: str) -> Optional[Any]:
        """
        Return the active game instance for a group.
        """
        game_data = self.active_games.get(group_id)
        return game_data["game"] if game_data else None

    def check_answer(self, group_id: str, answer: str, user_id: str, display_name: str) -> Optional[Any]:
        """
        Send the user's answer to the active game.
        """
        game = self.get_game(group_id)
        if not game:
            return None
        return game.check_answer(answer, user_id, display_name)

    def next_question(self, group_id: str) -> Optional[Any]:
        """
        Request the next question/task from the active game.
        """
        game = self.get_game(group_id)
        return game.next_question() if game else None

    def stop_game(self, group_id: str) -> bool:
        """
        Stop and remove the active game for the group.
        """
        if group_id in self.active_games:
            del self.active_games[group_id]
            return True
        return False

    # --------------------------------------------------------------
    # Random selections
    # --------------------------------------------------------------
    def get_random_question(self) -> str:
        return random.choice(self.questions) if self.questions else "لا توجد أسئلة متاحة"

    def get_random_challenge(self) -> str:
        return random.choice(self.challenges) if self.challenges else "لا توجد تحديات متاحة"

    def get_random_confession(self) -> str:
        return random.choice(self.confessions) if self.confessions else "لا توجد اعترافات متاحة"

    def get_random_mention(self) -> str:
        return random.choice(self.mentions) if self.mentions else "لا توجد منشنات متاحة"
