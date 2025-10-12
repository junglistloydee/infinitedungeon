import json
import copy
from modules.character import Player
from modules.room import Room
from modules.game_data import GameData

def save_game(player: Player, current_room: Room, rooms_travelled: int, room_history: list, direction_history: list):
    """Saves the current game state to 'savegame.json'."""
    game_state = {
        'player_data': player.__dict__,
        'dungeon_data': {
            'rooms_travelled': rooms_travelled,
            'current_room': current_room.__dict__,
            'room_history': [room.__dict__ for room in room_history],
            'direction_history': direction_history
        }
    }
    # Player and Room objects contain a reference to GameData, which is not serializable.
    # We need to remove it before saving.
    game_state['player_data'].pop('game_data', None)
    game_state['dungeon_data']['current_room'].pop('game_data', None)
    for room_dict in game_state['dungeon_data']['room_history']:
        room_dict.pop('game_data', None)

    try:
        with open('savegame.json', 'w') as f:
            json.dump(game_state, f, indent=4)
        print("Game saved successfully!")
    except (IOError, TypeError) as e:
        print(f"Error saving game: {e}")

def load_game(game_data: GameData):
    """Loads the game state from 'savegame.json'."""
    try:
        with open('savegame.json', 'r') as f:
            game_state = json.load(f)

        player_data = game_state['player_data']
        dungeon_data = game_state['dungeon_data']

        # Recreate the player object
        player = Player(player_data['name'], player_data['character_class'], game_data)
        for key, value in player_data.items():
            setattr(player, key, value)

        # Recreate the current room object
        room_data = dungeon_data['current_room']
        current_room = Room(game_data, player.level, player.quests, load_from_save=True)
        for key, value in room_data.items():
            setattr(current_room, key, value)

        # Recreate the room history
        room_history = []
        for room_data in dungeon_data['room_history']:
            room = Room(game_data, player.level, player.quests, load_from_save=True)
            for key, value in room_data.items():
                setattr(room, key, value)
            room_history.append(room)

        rooms_travelled = dungeon_data['rooms_travelled']
        direction_history = dungeon_data['direction_history']

        print("\nGame loaded successfully!")
        return player, current_room, rooms_travelled, room_history, direction_history

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"\nCould not load save game ({e}). Starting a new adventure.")
        return None, None, None, None, None
