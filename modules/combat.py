import random
import time
import copy
from modules.character import Player, Monster
from modules.game_data import GameData
from sound import Sound
from modules.utils import add_article

def handle_combat(player: Player, monster: Monster, game_data: GameData, sound_manager: Sound, current_room):
    """
    Handles a full-featured, turn-based combat encounter.
    Modifies the player and monster objects directly.
    Returns True if the player wins or escapes, False if the player dies.
    """
    print("=" * 40)
    print(f"\n--- Combat with {monster.name} ---")

    sound_manager.stop_music()
    sound_manager.play_music('combat_music')

    while player.is_alive() and monster.is_alive():
        player.recalculate_stats()
        print(f"Your HP: {player.hp}/{player.max_hp} | {monster.name} HP: {monster.hp}/{monster.max_hp}")

        is_player_stunned = player.apply_and_tick_status_effects()
        if is_player_stunned:
            print("You are stunned and cannot act!")
            action_taken = True
        else:
            combat_command_input = input("Combat Action (attack/skill/heal/run/use/inv)> ").lower().strip()
            parts = combat_command_input.split()
            verb = parts[0] if parts else "attack"
            action_taken = False

            if verb == "attack":
                damage_dealt = max(0, random.randint(player.attack_power - player.attack_variance, player.attack_power + player.attack_variance) - monster.defense)
                monster.hp -= damage_dealt
                print(f"You strike the {monster.name} for {damage_dealt} damage!")
                action_taken = True

            elif verb == "run":
                if random.random() > 0.5:
                    print("You manage to escape the fight!")
                    sound_manager.stop_music()
                    sound_manager.play_music('ambient_music')
                    return True
                else:
                    print("You try to run, but the monster blocks your path!")
                    action_taken = True

            elif verb == "heal":
                best_heal = None
                for item in player.inventory:
                    if item.get('effect_type') == 'heal':
                        if best_heal is None or item.get('effect_value', 0) > best_heal.get('effect_value', 0):
                            best_heal = item
                if best_heal:
                    player.use_item(best_heal, in_combat=True)
                    action_taken = True
                else:
                    print("You have no healing items.")
            else:
                print("Invalid command in combat.")

        if not monster.is_alive():
            print(f"The {monster.name} collapses, defeated!")
            player.add_xp(monster.xp_reward)
            gold_gained = monster.get_gold_dropped()
            player.gold += gold_gained
            print(f"You found {gold_gained} gold.")

            if monster.item_drop:
                item_def = game_data.get_item_by_name(monster.item_drop)
                if item_def:
                    if len(player.inventory) < player.max_inventory_slots:
                        player.inventory.append(copy.deepcopy(item_def))
                        print(f"The monster dropped {add_article(item_def['name'])}!")
                    else:
                        print(f"The monster dropped an item, but your inventory is full!")

            sound_manager.stop_music()
            sound_manager.play_music('ambient_music')
            return True

        if action_taken:
            is_monster_stunned = monster.apply_and_tick_status_effects()
            if not is_monster_stunned:
                damage_taken = max(0, random.randint(monster.attack_power - monster.attack_variance, monster.attack_power + monster.attack_variance) - player.defense)
                player.hp -= damage_taken
                print(f"The {monster.name} retaliates, hitting you for {damage_taken} damage!")

        if not player.is_alive():
            print(f"The {monster.name} delivers a fatal blow...")
            sound_manager.stop_music()
            sound_manager.play_music('ambient_music')
            return False

    return player.is_alive()

def handle_horde_combat(player: Player, horde_data: dict, game_data: GameData, sound_manager: Sound, current_room):
    horde_name = horde_data['name']
    horde_monsters_names = horde_data['monsters']
    horde_size = random.randint(horde_data['size'][0], horde_data['size'][1])

    print(f"\nA horde of {horde_size} monsters appears! It's a {horde_name}!")

    for i in range(horde_size):
        monster_name = random.choice(horde_monsters_names)
        monster_def = next((m for m in game_data.MONSTERS if m['name'] == monster_name), None)
        if not monster_def:
            continue

        monster = Monster(monster_def)
        print(f"\n--- Horde Battle ({i+1}/{horde_size}): A {monster.name} appears! ---")

        player_survived = handle_combat(player, monster, game_data, sound_manager, current_room)

        if not player_survived:
            return 'lose'

    print(f"\n--- Horde Defeated! ---")
    print(f"You defeated the {horde_name}!")
    return 'win'
