import sys
from sound import Sound
import debug

# Import the new, fully-featured modules
from modules.game_data import GameData
from modules.character import Player, Monster
from modules.room import Room
from modules.combat import handle_combat
from modules.interaction import handle_shop, handle_quest_giver, handle_inn, handle_gambler
from modules.persistence import save_game, load_game
from modules.utils import add_article

# --- MAIN SCREEN TEXT ---
MAIN_SCREEN_TEXT = """
=======================================
=       THE INFINITE DUNGEON          =
=======================================
=       1. Start New Game             =
=       2. Load Game                  =
=       3. Adventurer's Guild (TBD)   =
=       4. Credits                    =
=       5. Quit                       =
=======================================
"""

# --- CREDITS TEXT ---
CREDITS_TEXT = """
=======================================
=       THE INFINITE DUNGEON          =
=         Development Team            =
=======================================
= Lead Developer and Designer:        =
= Lloyd                               =
= Lead Tester:                        =
= Liam                                =
= Assistant to the Lead Tester:       =
= Stefan                              =
=======================================
"""

def game_loop(player: Player, current_room: Room, game_data: GameData, sound_manager):
    """Main game loop for active gameplay."""
    rooms_travelled = 1
    room_history = []
    direction_history = []

    while True:
        current_room.show_description(direction_history)

        if current_room.monster:
            monster = Monster(current_room.monster)
            win = handle_combat(player, monster, game_data, sound_manager, current_room)
            if win:
                current_room.monster = None
            else:
                print("\nGAME OVER")
                return

        command_input = input("> ").lower().strip()
        parts = command_input.split()
        verb = parts[0] if parts else ""

        if verb in ["north", "south", "east", "west"]:
            if verb in current_room.exits:
                room_history.append(current_room)
                direction_history.append(verb)
                current_room = Room(game_data, player.level, player.quests, entry_direction=verb)
                rooms_travelled += 1
            else:
                print("You can't go that way.")
        elif verb == "talk":
            if current_room.npc:
                npc_type = current_room.npc.get('type')
                if npc_type == 'vendor':
                    handle_shop(player, current_room.npc, game_data, sound_manager)
                elif npc_type == 'quest_giver':
                    handle_quest_giver(player, current_room.npc, game_data)
                elif npc_type == 'gambler':
                    handle_gambler(player, current_room.npc)
                else:
                    print(f"You have a pleasant chat with {current_room.npc['name']}.")
            else:
                print("There is no one to talk to.")
        elif verb == "save":
            save_game(player, current_room, rooms_travelled, room_history, direction_history)
        elif verb == "quit":
            print("Thanks for playing!")
            return
        # ... Other commands like get, drop, use, etc. would be added here
        else:
            print("Unknown command.")

def main():
    """The main function to run the game."""
    DEBUG = True
    if DEBUG:
        debug.initialize_debug_log(DEBUG)

    sound_manager = Sound(sound_enabled=True)
    game_data = GameData(debug_enabled=DEBUG)

    while True:
        print(MAIN_SCREEN_TEXT)
        main_menu_choice = input("Enter your choice: ").strip()

        if main_menu_choice == '1':
            player_name = input("Enter your adventurer's name: ").strip() or "Adventurer"

            class_choices = list(game_data.GAME_DATA.get('character_classes', {}).keys())
            print("\nChoose your class:")
            for i, class_name in enumerate(class_choices):
                print(f"{i+1}. {class_name}")

            class_choice_index = -1
            while class_choice_index not in range(len(class_choices)):
                try:
                    class_choice_input = input(f"Enter class (1-{len(class_choices)}): ")
                    class_choice_index = int(class_choice_input) - 1
                except ValueError:
                    print("Invalid input.")

            player_class = class_choices[class_choice_index]
            print(f"You have chosen the path of the {player_class}.")

            player = Player(player_name, player_class, game_data)
            current_room = Room(game_data, player.level, player.quests)

            if current_room.is_inn:
                handle_inn(player, game_data, sound_manager)
                current_room = Room(game_data, player.level, player.quests)

            sound_manager.stop_music()
            sound_manager.play_music('ambient_music')
            game_loop(player, current_room, game_data, sound_manager)

        elif main_menu_choice == '2':
            player, current_room, rooms_travelled, room_history, direction_history = load_game(game_data)
            if player and current_room:
                sound_manager.stop_music()
                sound_manager.play_music('ambient_music')
                game_loop(player, current_room, game_data, sound_manager)

        elif main_menu_choice == '4':
            print(CREDITS_TEXT)
            input("Press Enter to continue...")
        elif main_menu_choice == '5':
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    try:
        main()
    finally:
        if 'DEBUG' in locals() and DEBUG:
            debug.close_debug_log()
