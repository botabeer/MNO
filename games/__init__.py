# __init__.py
# حزمة الألعاب - واجهة بسيطة للاستيراد
from .game_manager import GameManager
from .game_helpers import *
from .constants import *
from .category_letter_game import CategoryLetterGame
from .chain_words_game import ChainWordsGame
from .compatibility_game import CompatibilityGame
from .fast_typing_game import FastTypingGame
from .human_animal_plant_game import HumanAnimalPlantGame
from .letters_words_game import LettersWordsGame
from .mafia_game import MafiaGame
from .opposite_game import OppositeGame
from .song_game import SongGame

__all__ = [
    "GameManager",
    "normalize_text", "create_game_header", "create_progress_box",
    "create_separator", "create_action_buttons", "create_winner_card",
    "create_hint_text",
    "COLORS", "MAFIA_CONFIG",
    "CategoryLetterGame", "ChainWordsGame", "CompatibilityGame",
    "FastTypingGame", "HumanAnimalPlantGame", "LettersWordsGame",
    "MafiaGame", "OppositeGame", "SongGame"
]
