import json
import sys
import os
import debug

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class GameData:
    def __init__(self, debug_enabled=False):
        self.DEBUG = debug_enabled
        self.GAME_DATA = self._load_game_data()
        self.ADJECTIVES = self.GAME_DATA.get('adjectives', [])
        self.ROOM_TYPES = self.GAME_DATA.get('room_types', [])
        self.DETAILS = self.GAME_DATA.get('details', [])
        self.ALL_ITEMS = self.GAME_DATA.get('items', [])
        self.WINNING_ITEMS = [item['name'] for item in self.ALL_ITEMS if item.get('type') == 'winning_item']
        self.NPCs = self.GAME_DATA.get('npcs', [])
        self.HAZARDS = self.GAME_DATA.get('hazards', [])
        self.MONSTERS = self.GAME_DATA.get('monsters', [])
        self.PUZZLES = self.GAME_DATA.get('puzzles', [])
        self.QUESTS = self.GAME_DATA.get('quests', [])
        self.SHRINES = self.GAME_DATA.get('shrines', [])
        self.HORDES = self.GAME_DATA.get('hordes', [])
        self.ITEM_SPAWN_WEIGHTS = self.GAME_DATA.get('item_spawn_weights', {})

        if self.DEBUG:
            self._print_debug_info()

    def _load_game_data(self):
        try:
            game_data_file_path = resource_path('game_data.json')
            with open(game_data_file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {game_data_file_path} not found. Ensure 'game_data.json' is included with the executable.")
            if self.DEBUG:
                debug.debug_print("Critical Error: game_data.json not found. Exiting.")
            exit()

    def _print_debug_info(self):
        debug.debug_game_data_full_output(self.GAME_DATA)
        debug.debug_game_data_load_check(self.GAME_DATA)
        debug.debug_print(f"Loaded {len(self.ADJECTIVES)} adjectives.")
        debug.debug_print(f"Loaded {len(self.ROOM_TYPES)} room types.")
        debug.debug_print(f"Loaded {len(self.DETAILS)} details.")
        debug.debug_print(f"Loaded {len(self.ALL_ITEMS)} items.")
        debug.debug_print(f"Identified {len(self.WINNING_ITEMS)} winning items.")
        debug.debug_print(f"Loaded {len(self.NPCs)} NPCs.")
        debug.debug_print(f"Loaded {len(self.HAZARDS)} hazards.")
        debug.debug_print(f"Loaded {len(self.MONSTERS)} monsters.")
        debug.debug_print(f"Loaded {len(self.PUZZLES)} puzzles.")
        debug.debug_print(f"Loaded {len(self.QUESTS)} quests.")
        debug.debug_print(f"Loaded {len(self.SHRINES)} shrines.")
        debug.debug_print(f"Loaded {len(self.HORDES)} hordes.")
        if self.ITEM_SPAWN_WEIGHTS:
            debug.debug_print(f"Loaded item spawn weights: {json.dumps(self.ITEM_SPAWN_WEIGHTS)}")
        else:
            debug.debug_print("Item spawn weights not found in game_data.json or empty.")

    def get_item_by_name(self, item_name_lower):
        for item in self.ALL_ITEMS:
            if item['name'].lower() == item_name_lower:
                return item
        return None
