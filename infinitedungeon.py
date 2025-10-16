import random
import time
import json
import sys
import os
import debug # Import debug module
import copy
from datetime import datetime
from sound import Sound

# --- History Log ---
HISTORY_LOG_FILE = "history_log.txt"

def log_event(message):
    """Appends a message to the history log file with a timestamp."""
    try:
        with open(HISTORY_LOG_FILE, 'a') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except IOError as e:
        print(f"Error writing to history log: {e}")

# Enable debug (THIS IS THE MASTER SWITCH FOR DEBUGGING)
DEBUG = False # Set to True to enable debug prints and file logging, False to disable


# --- Sound Manager ---
sound_manager = Sound(sound_enabled=True)

# --- Game Data ---
# Function to get the path to resource files, whether running as script or as PyInstaller bundle
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # If not running as a PyInstaller bundle, use the current directory
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Load all game data from a JSON file
GAME_DATA = {}
try:
    game_data_file_path = resource_path('game_data.json')
    with open(game_data_file_path, 'r') as f:
        GAME_DATA = json.load(f)

    # --- Initial Game Data Load Checks using debug.py ---
    if DEBUG: # Wrapped debug calls
        debug.debug_game_data_full_output(GAME_DATA) # Output all game data
        debug.debug_game_data_load_check(GAME_DATA) # Output key summary
    # --- END Initial Game Data Load Checks ---

except FileNotFoundError:
    print(f"Error: {game_data_file_path} not found. Ensure 'game_data.json' is included with the executable.")
    if DEBUG: # Wrapped debug calls
        debug.debug_print("Critical Error: game_data.json not found. Exiting.")
    # No need for debug.close_debug_log() here, as the finally block handles it.
    exit()

ADJECTIVES = GAME_DATA.get('adjectives', [])
if DEBUG: # Wrapped debug calls
    debug.debug_print(f"Loaded {len(ADJECTIVES)} adjectives.")
ROOM_TYPES = GAME_DATA.get('room_types', [])
if DEBUG: # Wrapped debug calls
    debug.debug_print(f"Loaded {len(ROOM_TYPES)} room types.")
DETAILS = GAME_DATA.get('details', [])
if DEBUG: # Wrapped debug calls
    debug.debug_print(f"Loaded {len(DETAILS)} details.")
ALL_ITEMS = GAME_DATA.get('items', [])
if DEBUG: # Wrapped debug calls
    debug.debug_print(f"Loaded {len(ALL_ITEMS)} items.")
WINNING_ITEMS = [item['name'] for item in ALL_ITEMS if item.get('type') == 'winning_item']
if DEBUG: # Wrapped debug calls
    debug.debug_print(f"Identified {len(WINNING_ITEMS)} winning items.")
NPCs = GAME_DATA.get('npcs', [])
if DEBUG: # Wrapped debug calls
    debug.debug_print(f"Loaded {len(NPCs)} NPCs.")
HAZARDS = GAME_DATA.get('hazards', [])
if DEBUG: # Wrapped debug calls
    debug.debug_print(f"Loaded {len(HAZARDS)} hazards.")
MONSTERS = GAME_DATA.get('monsters', [])
if DEBUG: # Wrapped debug calls
    debug.debug_print(f"Loaded {len(MONSTERS)} monsters.")
PUZZLES = GAME_DATA.get('puzzles', [])
if DEBUG: # Wrapped debug calls
    debug.debug_print(f"Loaded {len(PUZZLES)} puzzles.")
QUESTS = GAME_DATA.get('quests', [])
if DEBUG: # Wrapped debug calls
    debug.debug_print(f"Loaded {len(QUESTS)} quests.")
SHRINES = GAME_DATA.get('shrines', [])
if DEBUG: # Wrapped debug calls
    debug.debug_print(f"Loaded {len(SHRINES)} shrines.")
HORDES = GAME_DATA.get('hordes', [])
if DEBUG: # Wrapped debug calls
    debug.debug_print(f"Loaded {len(HORDES)} hordes.")

COMBINATION_RECIPES = GAME_DATA.get('combination_recipes', [])
if DEBUG: # Wrapped debug calls
    debug.debug_print(f"Loaded {len(COMBINATION_RECIPES)} combination recipes.")

# Specific debug for item_spawn_weights to confirm it's loaded
ITEM_SPAWN_WEIGHTS = GAME_DATA.get('item_spawn_weights', {})
if DEBUG: # Wrapped debug calls
    if ITEM_SPAWN_WEIGHTS:
        debug.debug_print(f"Loaded item spawn weights: {json.dumps(ITEM_SPAWN_WEIGHTS)}")
    else:
        debug.debug_print("Item spawn weights not found in game_data.json or empty.")


# --- MAIN SCREEN TEXT ---
MAIN_SCREEN_TEXT = """
=======================================
=       THE INFINITE DUNGEON          =
=======================================
=       1. Start New Game             =
=       2. Load Game                  =
=       3. Daily Challenge            =
=       4. Seeded Run                 =
=       5. Adventurer's Guild         =
=       6. Credits                    =
=       7. Quit                       =
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

# --- GLOBAL GAME CONSTANTS ---
# These define default/base values and are accessible everywhere
BASE_PLAYER_ATTACK_POWER = 8
BASE_PLAYER_ATTACK_VARIANCE = 2
BASE_PLAYER_CRIT_CHANCE = 0.1
BASE_PLAYER_CRIT_MULTIPLIER = 1.5

# --- LEVELING CONSTANTS ---
BASE_XP_TO_LEVEL_UP = 100
XP_SCALE_FACTOR = 1.5
HP_GAIN_PER_LEVEL = 15
ATTACK_GAIN_PER_LEVEL = 3
CRIT_CHANCE_GAIN_PER_LEVEL = 0.015 # Changed to 0.015 (1.5%)

# --- MONSTER SPAWN CONSTANTS ---
MONSTER_SPAWN_LEVEL_MIN_OFFSET = -1
MONSTER_SPAWN_LEVEL_MAX_OFFSET = 2
MONSTER_LEVEL_WEIGHTS = {
    -1: 0.2,
    0: 0.5,
    1: 0.2,
    2: 0.1
}

# --- WINNING ITEM SPAWN CHANCE ---
WINNING_ITEM_SPAWN_CHANCE = 0.01
WINNING_ITEM_MIN_PLAYER_LEVEL = 5

# --- DEDICATED VENDOR SPAWN CHANCE ---
VENDOR_SPAWN_CHANCE = 0.05

# --- INN SPAWN CHANCE ---
INN_SPAWN_CHANCE = 0.04

# --- SPECIAL EVENT TRACKER ---
special_event_after_unlock = None

# --- PUZZLE ROOM CONSTANTS ---
PUZZLE_SPAWN_CHANCE = 0.10

# --- SHRINE SPAWN CHANCE ---
SHRINE_SPAWN_CHANCE = 0.08

# --- HORDE ROOM CONSTANTS ---
HORDE_SPAWN_CHANCE = 0.05

# --- CRAFTING STATION CONSTANTS ---
CRAFTING_STATION_SPAWN_CHANCE = 0.05

# --- QUEST GIVER SPAWN CHANCE ---
QUEST_GIVER_SPAWN_CHANCE = 0.15

# --- SHOP CONSTANTS ---
SELL_PRICE_MULTIPLIER = 0.5

# --- Helper Functions ---

def apply_and_tick_effects(player_effects):
    """
    Applies active effects (buffs/curses) to player stats for the current turn
    and ticks down their duration. Removes expired effects.
    Returns a dictionary of total modifiers for the current turn.
    """
    stat_modifiers = {
        'attack_power': 0,
        'defense': 0,
        'crit_chance': 0.0
    }

    # Iterate over a copy, as we may modify the list
    for effect in list(player_effects):
        stat = effect.get('stat')
        modifier = effect.get('modifier')

        if stat in stat_modifiers and modifier is not None:
            stat_modifiers[stat] += modifier

        effect['duration'] -= 1

        if effect['duration'] <= 0:
            # Check for message key before trying to access it
            if 'message' in effect and effect['message']:
                print(f"The effect of '{effect['message'].split('!')[0]}' has worn off.")
            player_effects.remove(effect)

    return stat_modifiers

def apply_and_tick_status_effects(effects, character_hp):
    """
    Applies active status effects to a character for the current turn, ticks down their duration, and removes expired effects.
    Returns updated character_hp and a boolean indicating if the character is stunned.
    """
    is_stunned = False
    for effect in list(effects):
        if effect['type'] == 'dot':
            damage = effect['damage']
            character_hp -= damage
            print(effect['message_tick'].format(damage=damage))
        elif effect['type'] == 'control' and effect['name'] == 'Stun':
            is_stunned = True
        elif effect['type'] == 'persistent_debuff':
            pass
        effect['duration'] -= 1
        if effect['duration'] == 0:
            print(effect['message_wear_off'])
            effects.remove(effect)
    return character_hp, is_stunned

def add_article(word):
    """Adds 'a' or 'an' prefix to a word based on its starting letter."""
    if not word:
        return ""
    if word.lower().startswith(('a', 'e', 'i', 'o', 'u')):
        return f"an {word}"
    return f"a {word}"

def get_item_by_name(item_name_lower):
    """Utility to find an item dictionary by its lowercase name."""
    for item in ALL_ITEMS:
        if item['name'].lower() == item_name_lower:
            return item
    return None

# Quest Helper Functions
def get_quest_by_id(quest_id):
    """Retrieves a quest dictionary by its ID."""
    for quest in QUESTS:
        if quest['id'] == quest_id:
            return quest
    return None

def get_player_quest_status(player_quests, quest_id):
    """
    Determines the status of a quest for the player.
    Returns 'not_started', 'active', 'complete_ready', or 'completed'.
    """
    if quest_id not in player_quests:
        return 'not_started'

    quest_data = player_quests[quest_id]
    if quest_data['status'] == 'completed':
        return 'completed'

    quest_def = get_quest_by_id(quest_id)
    if quest_def:
        if quest_def['type'] in ['fetch_item', 'defeat_any_monster', 'defeat_monster']:
            if quest_data['current_count'] >= quest_def['target_count']:
                return 'complete_ready'
        elif quest_def['type'] == 'find_npc':
            if quest_data.get('found_npc'):
                return 'complete_ready'

    return 'active'

def has_player_enough_items(player_inventory, item_name, count):
    """Checks if the player's inventory contains the required number of an item."""
    current_count = sum(1 for item in player_inventory if item['name'].lower() == item_name.lower())
    return current_count >= count

def remove_items_from_inventory(player_inventory, item_name, count):
    """Removes a specified number of items from the player's inventory."""
    removed_count = 0
    items_to_keep = []
    for item in player_inventory:
        if item['name'].lower() == item_name.lower() and removed_count < count:
            removed_count += 1
        else:
            items_to_keep.append(item)
    player_inventory[:] = items_to_keep
    return removed_count == count


def update_reputation(player_reputation, faction_id, amount):
    """Updates the player's reputation with a specific faction."""
    if faction_id not in player_reputation:
        player_reputation[faction_id] = 0
    player_reputation[faction_id] += amount
    print(f"Your reputation with {faction_id} has changed by {amount}.")


def calculate_xp_for_next_level(current_level):
    """Calculates the XP required for the next level."""
    return int(BASE_XP_TO_LEVEL_UP * (XP_SCALE_FACTOR ** (current_level - 1)))

def level_up_player(player_hp, max_hp, player_level, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points):
    """Applies level-up bonuses to player stats."""
    player_level += 1
    skill_point_gained = False
    if player_level % 3 == 0 and player_level <= 15:
        player_skill_points += 1
        skill_point_gained = True

    old_max_hp = max_hp
    max_hp += HP_GAIN_PER_LEVEL
    player_hp = max_hp

    player_attack_power += ATTACK_GAIN_PER_LEVEL

    # Corrected critical hit chance increase on level-up
    player_crit_chance = min(1.0, player_crit_chance + CRIT_CHANCE_GAIN_PER_LEVEL)
    # The multiplier is a constant, so it's not increased by level-up
    # player_crit_multiplier = BASE_PLAYER_CRIT_MULTIPLIER # This should stay constant or be based on items

    print("\n" + "#" * 50)
    print(f"      CONGRATULATIONS! YOU REACHED LEVEL {player_level}!              ")
    print("#" * 50)
    print(f"Your Max HP increased from {old_max_hp} to {max_hp}!")
    print(f"Your Attack Power increased to {player_attack_power}!")
    print(f"Your Critical Chance increased to {player_crit_chance*100:.0f}%!")
    if skill_point_gained:
        print(f"You have gained a skill point! You now have {player_skill_points} skill point(s).")
    print(f"You feel fully revitalized!")
    print("#" * 50)

    return player_hp, max_hp, player_level, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points

def check_for_level_up(player_xp, player_level, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points):
    """Checks if the player has enough XP to level up and calls level_up_player."""
    while player_xp >= xp_to_next_level:
        player_xp -= xp_to_next_level

        player_hp, max_hp, player_level, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points = \
            level_up_player(player_hp, max_hp, player_level, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points)

        xp_to_next_level = calculate_xp_for_next_level(player_level)

    return player_xp, player_level, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points


def handle_skill_tree(player_class, player_level, player_skill_points, player_unlocked_skills):
    """Displays the skill tree and allows the player to unlock skills."""
    character_classes = GAME_DATA.get('character_classes', {})
    class_data = character_classes.get(player_class)
    if not class_data:
        print("Invalid class. Cannot display skill tree.")
        return player_skill_points, player_unlocked_skills

    skill_tree = class_data['skill_tree']
    ascii_tree = class_data['ascii_tree']
    skill_map = {skill['id']: skill for skill in skill_tree}

    while True:
        print(f"\n--- {player_class} Skill Tree ---")
        print(f"You have {player_skill_points} skill point(s).")

        # Display ASCII skill tree with status
        for line in ascii_tree:
            for skill_id, skill_data in skill_map.items():
                placeholder = f"({skill_id})"
                if placeholder in line:
                    skill_name = skill_data['name']
                    status = ""
                    if skill_name in player_unlocked_skills:
                        status = "[Unlocked]"
                    elif player_level >= skill_data['level_unlocked']:
                        is_unlockable = True
                        if 'dependencies' in skill_data:
                            for dep_id in skill_data['dependencies']:
                                if skill_map.get(dep_id) and skill_map[dep_id]['name'] not in player_unlocked_skills:
                                    is_unlockable = False
                                    break
                        if is_unlockable:
                            status = "[Available]"
                        else:
                            status = "[Locked]"
                    else:
                        status = "[Locked]"

                    line = line.replace(placeholder, f"({skill_id}) {skill_name} {status}")
            print(line)

        print("\nCommands: unlock <skill_id>, view <skill_id>, back")
        choice = input("Enter your command: ").strip().lower()

        if choice == 'back':
            break

        parts = choice.split()
        if len(parts) != 2:
            print("Invalid command format.")
            continue

        command, skill_id_str = parts
        if not skill_id_str.isdigit():
            print("Invalid skill ID.")
            continue

        skill_id = int(skill_id_str)
        skill_to_act = skill_map.get(skill_id)

        if not skill_to_act:
            print("Skill ID not found.")
            continue

        if command == 'view':
            print(f"\n--- {skill_to_act['name']} ---")
            print(f"Description: {skill_to_act['description']}")
            print(f"Required Level: {skill_to_act['level_unlocked']}")
            if 'dependencies' in skill_to_act and skill_to_act['dependencies']:
                dep_names = [skill_map[dep_id]['name'] for dep_id in skill_to_act['dependencies'] if skill_map.get(dep_id)]
                if dep_names:
                    print(f"Requires: {', '.join(dep_names)}")
            input("Press Enter to continue...")

        elif command == 'unlock':
            if player_skill_points <= 0:
                print("You have no skill points to spend.")
                continue

            if skill_to_act['name'] in player_unlocked_skills:
                print("You have already unlocked this skill.")
                continue

            if player_level < skill_to_act['level_unlocked']:
                print(f"You need to be level {skill_to_act['level_unlocked']} to unlock this skill.")
                continue

            can_unlock = True
            if 'dependencies' in skill_to_act:
                for dep_id in skill_to_act['dependencies']:
                    if skill_map.get(dep_id) and skill_map[dep_id]['name'] not in player_unlocked_skills:
                        print(f"You must unlock '{skill_map[dep_id]['name']}' first.")
                        can_unlock = False
                        break

            if can_unlock:
                player_skill_points -= 1
                player_unlocked_skills.append(skill_to_act['name'])
                print(f"You have unlocked '{skill_to_act['name']}'!")
        else:
            print("Invalid command.")

    return player_skill_points, player_unlocked_skills


def process_item_use(item_to_use, player_hp, max_hp, player_inventory, current_max_inventory_slots, in_combat=False):
    """
    Processes the effect of using a consumable item.
    Returns updated player_hp, updated max_hp (if changed by item), updated current_max_inventory_slots, a boolean indicating if a turn was consumed, and a dictionary of stat changes.
    """
    action_consumed_turn = False
    stat_changes = {}

    item_type = item_to_use.get('type')

    if item_type == 'consumable':
        effect_type = item_to_use.get('effect_type')
        effect_value = item_to_use.get('effect_value')

        if effect_type == 'heal' and isinstance(effect_value, int):
            healing_amount = effect_value
            player_hp_before_heal = player_hp
            player_hp = min(max_hp, player_hp + healing_amount)
            print(f"You use {add_article(item_to_use['name'])} and restore {player_hp - player_hp_before_heal} HP.")
            player_inventory.remove(item_to_use)
            action_consumed_turn = True
        elif effect_type == 'harm' and isinstance(effect_value, int):
            player_hp -= effect_value
            print(f"You use {add_article(item_to_use['name'])} and feel terrible! You take {effect_value} damage.")
            player_inventory.remove(item_to_use)
            action_consumed_turn = True
        elif effect_type == 'wake_up':
            print(f"You sniff {add_article(item_to_use['name'])} and feel invigorated! (This takes your turn.)")
            player_inventory.remove(item_to_use)
            action_consumed_turn = True
        elif effect_type == 'flavor':
            print(f"You consume {add_article(item_to_use['name'])}. It tastes... unique. (This takes your turn.)")
            player_inventory.remove(item_to_use)
            action_consumed_turn = True
        elif effect_type == 'perception_boost':
            if not in_combat:
                stat_changes['perception_boost'] = True
                print(f"You drink the {item_to_use['name']} and feel your senses sharpen.")
                player_inventory.remove(item_to_use)
                action_consumed_turn = True
            else:
                print("You can't drink this in the heat of combat.")
        elif effect_type == 'stat_boost':
            if not in_combat:
                stat_to_boost = effect_value.get('stat')
                amount = effect_value.get('amount')
                if stat_to_boost and isinstance(amount, int):
                    stat_changes[stat_to_boost] = stat_changes.get(stat_to_boost, 0) + amount
                    print(f"You consume the {item_to_use['name']} and feel permanently stronger!")
                    player_inventory.remove(item_to_use)
                    action_consumed_turn = True
                else:
                    print("This item seems to have no effect.")
            else:
                print("You can't use this powerful item in the heat of combat.")
        elif effect_type == 'cure':
            effect_to_cure = item_to_use.get('effect_value')
            if effect_to_cure:
                stat_changes['remove_effect'] = effect_to_cure
                print(f"You use the {item_to_use['name']}.")
                player_inventory.remove(item_to_use)
                action_consumed_turn = True
        elif effect_type == 'inflict':
            if in_combat:
                effect_to_inflict_name = item_to_use.get('effect_value')
                status_effects_data = GAME_DATA.get('status_effects', [])
                effect_def = next((e for e in status_effects_data if e['name'] == effect_to_inflict_name), None)
                if effect_def:
                    stat_changes['add_effect_to_monster'] = copy.deepcopy(effect_def)
                    print(f"You use the {item_to_use['name']}!")
                    player_inventory.remove(item_to_use)
                    action_consumed_turn = True
            else:
                print("You can only use this item in combat.")
        else:
            print(f"You can't use {add_article(item_to_use['name'])} in that way right now.")
    elif item_type == 'backpack':
        if in_combat:
            print(f"You can't use {add_article(item_to_use['name'])} in combat.")
        else:
            slots_added = item_to_use.get('effect_value', 0)
            if slots_added > 0:
                current_max_inventory_slots += slots_added
                print(f"You use {add_article(item_to_use['name'])} and gain {slots_added} additional inventory slots!")
                player_inventory.remove(item_to_use)
                action_consumed_turn = True
            else:
                print(f"You can't seem to use {add_article(item_to_use['name'])} to expand your inventory.")

    elif in_combat and item_type in ['weapon', 'armor', 'shield', 'key', 'winning_item']:
        print(f"You can't 'use' {add_article(item_to_use['name'])} during combat. Try 'equip' for gear, or 'unlock' for keys.")
    elif not in_combat and item_type in ['key', 'weapon', 'armor', 'shield', 'winning_item']:
        print(f"You can't 'use' {add_article(item_to_use['name'])} directly. Try 'equip' for gear, or 'unlock' for keys.")
    else:
        print(f"You can't use {add_article(item_to_use['name'])} in that way.")

    return player_hp, max_hp, current_max_inventory_slots, action_consumed_turn, stat_changes


def handle_item_effects(effect_type, player_hp, damage, monster_hp, equipped_items):
    """
    Handles unique item effects during combat.
    """
    for item in equipped_items:
        if item and "effects" in item:
            effects = item["effects"]
            if effect_type == "on_deal_damage":
                if "lifesteal_percentage" in effects:
                    lifesteal = int(damage * effects["lifesteal_percentage"])
                    player_hp += lifesteal
                    print(f"Your {item['name']} drains {lifesteal} HP from the enemy!")
                if "chain_lightning_chance" in effects and random.random() < effects["chain_lightning_chance"]:
                    monster_hp -= effects["chain_lightning_damage"]
                    print(f"A lightning bolt from your {item['name']} strikes the enemy for an extra {effects['chain_lightning_damage']} damage!")
            elif effect_type == "on_take_damage":
                if "evade_chance" in effects and random.random() < effects["evade_chance"]:
                    damage = 0
                    print(f"You dodge the attack thanks to your {item['name']}!")
                if "reflect_damage_chance" in effects and random.random() < effects["reflect_damage_chance"]:
                    reflect_damage = int(damage * effects["reflect_damage_percentage"])
                    monster_hp -= reflect_damage
                    print(f"Your {item['name']} reflects {reflect_damage} damage back at the enemy!")
    return player_hp, damage, monster_hp
def display_room_content_summary(current_room, rooms_travelled, direction_history=None, seed=None):
    """
    Displays the room description and then any relevant hints or status information.
    """
    status_text = f" Room: {rooms_travelled} "
    if seed:
        status_text += f"| Seed: {seed} "
    separator_length = (40 - len(status_text)) // 2
    print("=" * separator_length + status_text + "=" * (40 - separator_length - len(status_text)))

    current_room.show_description()

    if current_room.npc and not current_room.npc.get('talked_to', False):
        print("    Hint: Try typing 'talk'")
    if current_room.puzzle and not current_room.puzzle.get('solved', True):
        puzzle_type = current_room.puzzle['type']
        if puzzle_type == 'riddle':
            print("    Hint: Answering the riddle might reveal the way. Try 'answer [your guess]'")
        elif puzzle_type == 'mechanism':
            print("    Hint: You might need to 'pull' a lever here. Try 'pull [lever color/material]'")
        elif puzzle_type == 'pressure_plate':
            print("    Hint: A pressure plate on the floor looks like it needs something pressed on it. Try 'press'")
        elif puzzle_type == 'item_delivery':
            print("    Hint: Look for a way to 'give' something to the object. Try 'give [item] to [object]'")

    print("=" * 40)


def recalculate_attack_power(player_level, equipped_weapon, equipped_misc_items, player_attack_bonus):
    """Recalculates the player's attack power based on their level, equipment, and permanent bonuses."""
    current_base_attack = BASE_PLAYER_ATTACK_POWER + ((player_level - 1) * ATTACK_GAIN_PER_LEVEL) + player_attack_bonus
    if equipped_weapon:
        player_attack_power = current_base_attack + equipped_weapon.get('damage', 0)
    else:
        player_attack_power = current_base_attack

    for item in equipped_misc_items:
        if item.get('effect_type') == 'strength_boost':
            player_attack_power += item.get('effect_value', 0)
        if item.get('effects', {}).get('crit_chance_boost'):
            player_crit_chance += item.get('effects', {}).get('crit_chance_boost', 0)

    return player_attack_power


def calculate_total_defense(player_shield_value, equipped_armor_value, equipped_cloak, equipped_helmet):
    """Calculates total defense, including penalties from cursed items."""
    total_defense = 0

    # List of all equipped armor items
    equipped_gear = [player_shield_value, equipped_armor_value, equipped_cloak, equipped_helmet]

    for item in equipped_gear:
        if item:
            # Add base defense
            total_defense += item.get('defense', 0)
            # Apply curse effect if present
            if item.get('cursed'):
                curse_effect = item.get('curse_effect', {})
                if 'defense' in curse_effect:
                    total_defense += curse_effect['defense']

    return max(0, total_defense) # Defense cannot be negative


def scale_item_for_player_level(item, player_level):
    """
    Scales an item's stats and name based on the player's level.
    Returns a new, scaled item dictionary or the original item if not scalable.
    """
    if not item or item.get('type') not in ['weapon', 'shield', 'armor']:
        return item

    bonus = 0
    if 5 <= player_level <= 7:
        bonus = 1
    elif 8 <= player_level <= 10:
        bonus = 2
    elif 11 <= player_level <= 13:
        bonus = 3
    elif 14 <= player_level <= 16:
        bonus = 4
    elif player_level >= 17:
        bonus = 5

    if bonus > 0:
        # Create a deep copy to avoid modifying the original item in ALL_ITEMS
        scaled_item = copy.deepcopy(item)
        scaled_item['name'] = f"{scaled_item['name']}+{bonus}"

        if 'damage' in scaled_item:
            scaled_item['damage'] += bonus

        if 'defense' in scaled_item:
            scaled_item['defense'] += bonus

        if 'shop_price' in scaled_item:
            price_increase = 1.0 + (bonus * 0.33)
            scaled_item['shop_price'] = int(scaled_item['shop_price'] * price_increase)

        return scaled_item

    return item


# NEW: Dedicated function for equipping items
def handle_equip_item(item_to_equip, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items, player_level, equipped_helmet):
    """
    Handles the logic of equipping an item and returns the updated equipment state.
    """
    item_type = item_to_equip.get('type')

    if item_type == 'shield':
        if player_shield_value and player_shield_value.get('cursed'):
            print(f"Your {player_shield_value['name']} is cursed! You cannot unequip it.")
            return player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items, equipped_helmet
        item_defense = item_to_equip.get('defense', 0)
        current_shield_defense = player_shield_value.get('defense', 0) if player_shield_value else 0
        if item_to_equip is player_shield_value:
            print(f"You already have {add_article(item_to_equip['name'])} equipped.")
        elif item_defense >= current_shield_defense:
            player_shield_value = item_to_equip
            print(f"You equip {add_article(item_to_equip['name'])}. Your **shield defense** is now {player_shield_value.get('defense',0)}.")
        else:
            print(f"You already have a shield ({player_shield_value['name']}) providing {current_shield_defense} defense, which is better than {add_article(item_to_equip['name'])}'s {item_defense} defense.")

    elif item_type == 'armor':
        item_subtype = item_to_equip.get('subtype')
        if not item_subtype:
            item_subtype = 'body_armor'

        if item_subtype == 'body_armor':
            if equipped_armor_value and equipped_armor_value.get('cursed'):
                print(f"Your {equipped_armor_value['name']} is cursed! You cannot unequip it.")
                return player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items, equipped_helmet
            item_defense = item_to_equip.get('defense', 0)
            current_armor_defense = equipped_armor_value.get('defense', 0) if equipped_armor_value else 0
            if item_to_equip is equipped_armor_value:
                print(f"You already have {add_article(item_to_equip['name'])} equipped as body armor.")
            elif item_defense >= current_armor_defense:
                equipped_armor_value = item_to_equip
                print(f"You equip {add_article(item_to_equip['name'])}. Your **body armor defense** is now {equipped_armor_value.get('defense',0)}.")
            else:
                print(f"You already have body armor ({equipped_armor_value['name']}) providing {current_armor_defense} defense, which is better than {add_article(item_to_equip['name'])}'s {item_defense} defense.")
        elif item_subtype == 'cloak':
            if equipped_cloak and equipped_cloak.get('cursed'):
                print(f"Your {equipped_cloak['name']} is cursed! You cannot unequip it.")
                return player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items, equipped_helmet
            item_defense = item_to_equip.get('defense', 0)
            current_cloak_defense = equipped_cloak.get('defense', 0) if equipped_cloak else 0
            if item_to_equip is equipped_cloak:
                print(f"You already have {add_article(item_to_equip['name'])} equipped as a cloak.")
            elif item_defense >= current_cloak_defense:
                equipped_cloak = item_to_equip
                print(f"You equip {add_article(item_to_equip['name'])}. Your **cloak defense** is now {equipped_cloak.get('defense',0)}.")
            else:
                print(f"You already have a cloak ({equipped_cloak['name']}) providing {current_cloak_defense} defense, which is better than {add_article(item_to_equip['name'])}'s {item_defense} defense.")
        elif item_subtype == 'helmet':
            if equipped_helmet and equipped_helmet.get('cursed'):
                print(f"Your {equipped_helmet['name']} is cursed! You cannot unequip it.")
                return player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items, equipped_helmet
            item_defense = item_to_equip.get('defense', 0)
            current_helmet_defense = equipped_helmet.get('defense', 0) if equipped_helmet else 0
            if item_to_equip is equipped_helmet:
                print(f"You already have {add_article(item_to_equip['name'])} equipped as a helmet.")
            elif item_defense >= current_helmet_defense:
                equipped_helmet = item_to_equip
                print(f"You equip {add_article(item_to_equip['name'])}. Your **helmet defense** is now {equipped_helmet.get('defense',0)}.")
            else:
                print(f"You already have a helmet ({equipped_helmet['name']}) providing {current_helmet_defense} defense, which is better than {add_article(item_to_equip['name'])}'s {item_defense} defense.")
        else:
            print(f"You can't equip {add_article(item_to_equip['name'])} as an armor of unknown subtype.")

    elif item_type == 'weapon':
        if equipped_weapon and equipped_weapon.get('cursed'):
            print(f"Your {equipped_weapon['name']} is cursed! You cannot unequip it.")
            return player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items, equipped_helmet
        new_weapon_damage = item_to_equip.get('damage', 0)
        current_weapon_damage = equipped_weapon.get('damage', 0) if equipped_weapon else 0

        if item_to_equip is equipped_weapon:
            print(f"You already have {add_article(item_to_equip['name'])} equipped.")
        elif new_weapon_damage >= current_weapon_damage:
            equipped_weapon = item_to_equip
            print(f"You equip {add_article(item_to_equip['name'])}.")
        else:
            current_weapon_name = equipped_weapon['name'] if equipped_weapon else "your fists"
            print(f"You already have {add_article(current_weapon_name)} (Damage: {current_weapon_damage}), which is better than {add_article(item_to_equip['name'])}'s {new_weapon_damage} damage.")

    elif item_type == 'equipment':
        if item_to_equip in equipped_misc_items:
            print(f"You already have {add_article(item_to_equip['name'])} equipped.")
        else:
            equipped_misc_items.append(item_to_equip)
            print(f"You equip {add_article(item_to_equip['name'])}.")

    return player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items, equipped_helmet


# MODIFIED: Added equipped_cloak and equipped_misc_items to parameters
def handle_combat(player, monster_data, current_room, sound_manager):
    player_status_effects = []
    monster_status_effects = []
    """
    Handles a simple turn-based combat encounter.
    Returns the updated player_hp, max_hp, monster_data (None if defeated), gold_gained,
    player_xp, player_level, xp_to_next_level, player_quests, and equipped items.
    """
    print("=" * 40)
    monster_name = monster_data['name']
    monster_current_hp = monster_data['health']
    monster_base_damage = monster_data['damage']
    monster_damage_variance = monster_data.get('damage_variance', 0)
    monster_crit_chance = monster_data.get('crit_chance', 0.0)
    monster_crit_multiplier = monster_data.get('crit_multiplier', 1.0)
    monster_xp_reward = monster_data.get('xp_reward', 10)

    gold_drop_range = monster_data.get('gold_drop', [0, 0])
    gold_gained = 0

    effect_modifiers = apply_and_tick_effects(player.effects)
    current_attack_power = player.attack_power + effect_modifiers.get('attack_power', 0)
    current_defense_bonus = effect_modifiers.get('defense', 0)
    current_crit_chance_bonus = effect_modifiers.get('crit_chance', 0.0)

    # Defense values are now from the equipped item dictionaries
    total_player_defense = calculate_total_defense(player.equipped_shield, player.equipped_armor, player.equipped_cloak, player.equipped_helmet) + current_defense_bonus

    for item in [player.equipped_armor, player.equipped_cloak, player.equipped_helmet, player.equipped_shield]:
        if item and item.get('enchantment'):
            enchantment_name = item['enchantment']
            enchantment = next((e for e in GAME_DATA.get('enchantments', []) if e['name'] == enchantment_name), None)
            if enchantment and 'defense_boost' in enchantment['effect']:
                total_player_defense += enchantment['effect']['defense_boost']

    for effect in player_status_effects:
        if effect['name'] == 'Curse':
            total_player_defense += effect['effect']['modifier']

    monster_defense = monster_data.get('defense', 0)
    for effect in monster_status_effects:
        if effect['name'] == 'Curse':
            monster_defense += effect['effect']['modifier']

    sound_manager.stop_music()
    sound_manager.play_music('combat_music')
    print(f"\n--- Combat with {monster_name} ---")
    print(f"Your HP: {player.hp}/{player.max_hp} | {monster_name} HP: {monster_current_hp}")
    if total_player_defense > 0:
        print(f"Your Total Defense: {total_player_defense}")

    first_strike = False
    for item in player.equipped_misc_items:
        if item.get('effects', {}).get('first_strike'):
            first_strike = True
            break

    if first_strike:
        print("Thanks to your Amulet of Swiftness, you get the first strike!")
        # This is a simplified version of the player's turn for the first strike
        base_damage = random.randint(player.attack_power - player.attack_variance, player.attack_power + player.attack_variance)
        damage_dealt = max(0, base_damage - monster_defense)
        monster_current_hp -= damage_dealt
        print(f"You strike the {monster_name} for {damage_dealt} damage!")
        if monster_current_hp <= 0:
            print(f"You defeated the {monster_name} before it could even act!")
            current_room.monster = None

    while player.hp > 0 and monster_current_hp > 0:
        player.hp, is_player_stunned = apply_and_tick_status_effects(player_status_effects, player.hp)
        if is_player_stunned:
            print("You are stunned and cannot act!")
            action_taken = True
        else:
            print("\nWhat do you do? (attack / skill / heal / run / use [item name] / inventory / help)")
            combat_command_input = input("Combat Action> ").lower().strip()
            parts = combat_command_input.split()

            verb = "" # Initialize verb to an empty string

            # NEW: If input is empty, default to 'attack'
            if not parts:
                verb = "attack"
            else:
                verb = parts[0]

            action_taken = False

            if verb == "attack":
                if player.equipped_weapon and player.equipped_weapon.get('cursed') and player.equipped_weapon.get('curse_effect', {}).get('hp_drain'):
                    drain_amount = player.equipped_weapon['curse_effect']['hp_drain']
                    player.hp -= drain_amount
                    print(f"Your {player.equipped_weapon['name']} drains {drain_amount} HP from you!")
                    if player.hp <= 0:
                        print("You have been drained of your life force!")
                        break
                base_damage = random.randint(current_attack_power - player.attack_variance, current_attack_power + player.attack_variance)

                is_crit = False
                accuracy = 1.0
                for effect in player_status_effects:
                    if effect['name'] == 'Blindness':
                        accuracy += effect['effect']['modifier']

                if random.random() > accuracy:
                    print("You miss!")
                    damage_dealt = 0
                elif random.random() < (player.crit_chance + current_crit_chance_bonus):
                    damage_dealt = int(base_damage * player.crit_multiplier)
                    is_crit = True
                else:
                    damage_dealt = base_damage

                damage_dealt = max(0, damage_dealt - monster_defense)
                monster_current_hp -= damage_dealt
                if is_crit:
                    print(f"You deliver a **CRITICAL HIT** to the {monster_name} for {damage_dealt} damage!")
                else:
                    print(f"You strike the {monster_name} for {damage_dealt} damage!")

                if player.equipped_weapon and 'status_effects' in player.equipped_weapon:
                    for effect in player.equipped_weapon['status_effects']:
                        if random.random() < effect['chance']:
                            monster_status_effects.append(copy.deepcopy(effect))
                            print(f"The {monster_name} is now {effect['name']}!")

                if player.equipped_weapon and player.equipped_weapon.get('enchantment'):
                    enchantment_name = player.equipped_weapon['enchantment']
                    enchantment = next((e for e in GAME_DATA.get('enchantments', []) if e['name'] == enchantment_name), None)
                    if enchantment:
                        if 'damage_boost' in enchantment['effect']:
                            damage_dealt += enchantment['effect']['damage_boost']['value']
                            print(f"Your weapon's {enchantment_name} enchantment deals an extra {enchantment['effect']['damage_boost']['value']} damage!")
                        if 'status_effect' in enchantment['effect']:
                            if random.random() < enchantment['effect']['status_effect']['chance']:
                                monster_status_effects.append(copy.deepcopy(enchantment['effect']['status_effect']))
                                print(f"The {monster_name} is now {enchantment['effect']['status_effect']['name']}!")

                action_taken = True

                if monster_current_hp <= 0:
                    print(f"The {monster_name} collapses, defeated!")
                    gold_gained = random.randint(gold_drop_range[0], gold_drop_range[1])
                    if player.equipped_helmet and player.equipped_helmet.get('cursed') and player.equipped_helmet.get('curse_effect', {}).get('gold_find'):
                        gold_gained = int(gold_gained * player.equipped_helmet['curse_effect']['gold_find'])
                        print(f"Your {player.equipped_helmet['name']} doubles the gold dropped!")
                    print(f"You gained {gold_gained} gold from defeating the {monster_name}!")
                    player.gold += gold_gained

                    player.xp += monster_xp_reward
                    print(f"You gained {monster_xp_reward} experience points!")

                    item_drop_name = monster_data.get('item_drop')
                    if item_drop_name:
                        item_def = get_item_by_name(item_drop_name)
                        if item_def:
                            if len(player.inventory) < player.current_max_inventory_slots:
                                scaled_item = scale_item_for_player_level(item_def, player.level)
                                player.inventory.append(scaled_item)
                                print(f"The monster dropped {add_article(scaled_item['name'])}! It has been added to your inventory.")
                                # NEW: Quick equip prompt
                                if scaled_item.get('type') in ['weapon', 'shield', 'armor', 'equipment']:
                                    quick_equip_choice = input(f"Do you want to quick equip the {scaled_item['name']}? (yes/no): ").lower().strip()
                                    if quick_equip_choice in ['yes', 'y']:
                                        player.equipped_shield, player.equipped_armor, player.equipped_cloak, player.equipped_weapon, player.equipped_misc_items, player.equipped_helmet = \
                                            handle_equip_item(player.inventory[-1], player.equipped_shield, player.equipped_armor, player.equipped_cloak, player.equipped_weapon, player.equipped_misc_items, player.level, player.equipped_helmet)
                                        player.attack_power = recalculate_attack_power(player.level, player.equipped_weapon, player.equipped_misc_items, player.attack_bonus)
                                        print(f"Your attack power is now {player.attack_power}.")
                            elif current_room.item is None:
                                scaled_item = scale_item_for_player_level(item_def, player.level)
                                current_room.item = scaled_item
                                print(f"The monster dropped {add_article(scaled_item['name'])}, but your inventory is full! It has been placed on the floor.")
                            else:
                                print(f"The monster dropped {add_article(item_def['name'])}, but your inventory is full and there's already an item on the floor! The dropped item is lost.")
                        else:
                            if DEBUG:
                                debug.debug_print(f"Monster drop item '{item_drop_name}' not found in game data.")

                    if random.random() < 0.1:
                        crafting_materials = [item for item in ALL_ITEMS if item.get('type') == 'crafting_material']
                        if crafting_materials:
                            material_to_drop = random.choice(crafting_materials)
                            if len(player.inventory) < player.current_max_inventory_slots:
                                player.inventory.append(copy.deepcopy(material_to_drop))
                                print(f"The monster dropped a {material_to_drop['name']}!")
                            else:
                                print(f"The monster dropped a {material_to_drop['name']}, but your inventory is full!")

                    for q_id, q_data in player.quests.items():
                        quest_def = get_quest_by_id(q_id)
                        if quest_def and q_data['status'] == 'active':
                            if (quest_def['type'] == 'defeat_any_monster') or \
                               (quest_def['type'] == 'defeat_monster' and quest_def['target_monster'].lower() == monster_name.lower()):
                                if q_data['current_count'] < quest_def['target_count']:
                                    q_data['current_count'] += 1
                                    print(f"Quest Update: Defeated a monster! ({q_data['current_count']}/{quest_def['target_count']}) for '{quest_def['name']}'")
                                    if q_data['current_count'] >= quest_def['target_count']:
                                        print(f"QUEST COMPLETE: '{quest_def['name']}'! Return to {quest_def['giver_npc_name']} to claim your reward!")

                    player.xp, player.level, player.xp_to_next_level, player.hp, player.max_hp, player.attack_power, player.attack_variance, player.crit_chance, player.crit_multiplier, player.skill_points = \
                        check_for_level_up(player.xp, player.level, player.xp_to_next_level, player.hp, player.max_hp, player.attack_power, player.attack_variance, player.crit_chance, player.crit_multiplier, player.skill_points)

                    current_room.monster = None
                    break
            elif verb == "skill":
                if not player.unlocked_skills:
                    print("You have not unlocked any skills yet.")
                    continue

                print("\nAvailable skills:")
                for skill_name in player.unlocked_skills:
                    print(f"  - {skill_name}")

                skill_choice = input("Enter the name of the skill you want to use, or 'back': ").strip()
                if skill_choice.lower() == 'back':
                    continue

                chosen_skill = None
                for skill_name in player.unlocked_skills:
                    if skill_name.lower() == skill_choice.lower():
                        character_classes = GAME_DATA.get('character_classes', {})
                        class_data = character_classes.get(player.character_class)
                        for skill_data in class_data['skill_tree']:
                            if skill_data['name'] == skill_name:
                                chosen_skill = skill_data
                                break
                        break

                if chosen_skill:
                    effect = chosen_skill['effect']
                    if effect['type'] == 'damage_boost':
                        base_damage = random.randint(player.attack_power - player.attack_variance, player.attack_power + player.attack_variance)
                        damage_dealt = int(base_damage * effect['value'])
                        damage_dealt = max(0, damage_dealt - monster_defense)
                        monster_current_hp -= damage_dealt
                        print(f"You use {chosen_skill['name']} and deal {damage_dealt} damage!")
                    elif effect['type'] == 'guaranteed_crit':
                        base_damage = random.randint(player.attack_power - player.attack_variance, player.attack_power + player.attack_variance)
                        damage_dealt = int(base_damage * player.crit_multiplier)
                        damage_dealt = max(0, damage_dealt - monster_defense)
                        monster_current_hp -= damage_dealt
                        print(f"You use {chosen_skill['name']} for a guaranteed critical hit, dealing {damage_dealt} damage!")
                    elif effect['type'] == 'aoe_damage':
                        damage_dealt = effect['damage']
                        damage_dealt = max(0, damage_dealt - monster_defense)
                        monster_current_hp -= damage_dealt
                        print(f"You use {chosen_skill['name']} and deal {damage_dealt} damage to all enemies!")
                    elif effect['type'] == 'heal':
                        healing_amount = effect['value']
                        player.hp = min(player.max_hp, player.hp + healing_amount)
                        print(f"You use {chosen_skill['name']} and heal for {healing_amount} HP.")
                    elif effect['type'] == 'stun':
                        if random.random() < effect['chance']:
                            monster_status_effects.append({"name": "Stun", "type": "control", "duration": 2}) # 2 turns because it ticks down once immediately
                            print(f"You use {chosen_skill['name']} and stun the {monster_name}!")
                        else:
                            print(f"You use {chosen_skill['name']}, but it fails to stun the {monster_name}.")
                    elif effect['type'] == 'poison':
                        monster_status_effects.append({"name": "Poison", "type": "dot", "damage": effect['damage'], "duration": effect['duration'] + 1, "message_tick": "The monster takes {damage} from poison.", "message_wear_off": "The monster is no longer poisoned."})
                        print(f"You use {chosen_skill['name']} and poison the {monster_name}!")
                    elif effect['type'] == 'freeze':
                        if random.random() < effect['chance']:
                            monster_status_effects.append({"name": "Stun", "type": "control", "duration": 2})
                            print(f"You use {chosen_skill['name']} and freeze the {monster_name} in place!")
                        else:
                            print(f"You use {chosen_skill['name']}, but the {monster_name} resists the freeze.")
                    elif effect['type'] == 'stat_buff':
                        player.effects.append({"stat": effect['stat'], "modifier": effect['value'], "duration": effect['duration'] + 1, "message": f"You feel the power of {chosen_skill['name']}!"})
                        print(f"You use {chosen_skill['name']} and feel stronger!")
                    elif effect['type'] == 'damage_modifier':
                        undead_monsters = ["skeletal warrior", "feral ghoul", "vampire spawn", "lich's apprentice", "ghostly apparition", "specter of despair", "minotaur skeleton"]
                        base_damage = random.randint(player.attack_power - player.attack_variance, player.attack_power + player.attack_variance)
                        damage_dealt = base_damage
                        if monster_name.lower() in [m.lower() for m in undead_monsters]:
                            damage_dealt = int(base_damage * effect['multiplier'])
                            print("Your divine power smites the undead creature!")
                        damage_dealt = max(0, damage_dealt - monster_defense)
                        monster_current_hp -= damage_dealt
                        print(f"You use {chosen_skill['name']} and deal {damage_dealt} damage!")
                    elif effect['type'] == 'shield':
                        player.effects.append({"stat": "defense", "modifier": effect['value'], "duration": 1, "message": "An arcane shield surrounds you."})
                        print(f"You summon an Arcane Shield that will absorb up to {effect['value']} damage.")
                    elif effect['type'] == 'dodge_buff':
                        player.effects.append({"stat": "dodge_chance", "modifier": effect['value'], "duration": effect['duration'] + 1, "message": "You feel nimble and evasive."})
                        print(f"You use {chosen_skill['name']} and feel much harder to hit.")
                    action_taken = True
                else:
                    print("Invalid skill name.")
                    continue

                if monster_current_hp <= 0:
                    print(f"The {monster_name} collapses, defeated!")
                    gold_gained = random.randint(gold_drop_range[0], gold_drop_range[1])
                    if player.equipped_helmet and player.equipped_helmet.get('cursed') and player.equipped_helmet.get('curse_effect', {}).get('gold_find'):
                        gold_gained = int(gold_gained * player.equipped_helmet['curse_effect']['gold_find'])
                        print(f"Your {player.equipped_helmet['name']} doubles the gold dropped!")
                    print(f"You gained {gold_gained} gold from defeating the {monster_name}!")
                    player.gold += gold_gained

                    player.xp += monster_xp_reward
                    print(f"You gained {monster_xp_reward} experience points!")

                    item_drop_name = monster_data.get('item_drop')
                    if item_drop_name:
                        item_def = get_item_by_name(item_drop_name)
                        if item_def:
                            if len(player.inventory) < player.current_max_inventory_slots:
                                scaled_item = scale_item_for_player_level(item_def, player.level)
                                player.inventory.append(scaled_item)
                                print(f"The monster dropped {add_article(scaled_item['name'])}! It has been added to your inventory.")
                                # NEW: Quick equip prompt
                                if scaled_item.get('type') in ['weapon', 'shield', 'armor', 'equipment']:
                                    quick_equip_choice = input(f"Do you want to quick equip the {scaled_item['name']}? (yes/no): ").lower().strip()
                                    if quick_equip_choice in ['yes', 'y']:
                                        player.equipped_shield, player.equipped_armor, player.equipped_cloak, player.equipped_weapon, player.equipped_misc_items, player.equipped_helmet = \
                                            handle_equip_item(player.inventory[-1], player.equipped_shield, player.equipped_armor, player.equipped_cloak, player.equipped_weapon, player.equipped_misc_items, player.level, player.equipped_helmet)
                                        player.attack_power = recalculate_attack_power(player.level, player.equipped_weapon, player.equipped_misc_items, player.attack_bonus)
                                        print(f"Your attack power is now {player.attack_power}.")
                            elif current_room.item is None:
                                scaled_item = scale_item_for_player_level(item_def, player.level)
                                current_room.item = scaled_item
                                print(f"The monster dropped {add_article(scaled_item['name'])}, but your inventory is full! It has been placed on the floor.")
                            else:
                                print(f"The monster dropped {add_article(item_def['name'])}, but your inventory is full and there's already an item on the floor! The dropped item is lost.")
                        else:
                            if DEBUG:
                                debug.debug_print(f"Monster drop item '{item_drop_name}' not found in game data.")

                    if random.random() < 0.1:
                        crafting_materials = [item for item in ALL_ITEMS if item.get('type') == 'crafting_material']
                        if crafting_materials:
                            material_to_drop = random.choice(crafting_materials)
                            if len(player.inventory) < player.current_max_inventory_slots:
                                player.inventory.append(copy.deepcopy(material_to_drop))
                                print(f"The monster dropped a {material_to_drop['name']}!")
                            else:
                                print(f"The monster dropped a {material_to_drop['name']}, but your inventory is full!")

                    for q_id, q_data in player.quests.items():
                        quest_def = get_quest_by_id(q_id)
                        if quest_def and q_data['status'] == 'active':
                            if (quest_def['type'] == 'defeat_any_monster') or \
                               (quest_def['type'] == 'defeat_monster' and quest_def['target_monster'].lower() == monster_name.lower()):
                                if q_data['current_count'] < quest_def['target_count']:
                                    q_data['current_count'] += 1
                                    print(f"Quest Update: Defeated a monster! ({q_data['current_count']}/{quest_def['target_count']}) for '{quest_def['name']}'")
                                    if q_data['current_count'] >= quest_def['target_count']:
                                        print(f"QUEST COMPLETE: '{quest_def['name']}'! Return to {quest_def['giver_npc_name']} to claim your reward!")

                    player.xp, player.level, player.xp_to_next_level, player.hp, player.max_hp, player.attack_power, player.attack_variance, player.crit_chance, player.crit_multiplier, player.skill_points = \
                        check_for_level_up(player.xp, player.level, player.xp_to_next_level, player.hp, player.max_hp, player.attack_power, player.attack_variance, player.crit_chance, player.crit_multiplier, player.skill_points)

                    current_room.monster = None
                    break

            elif verb == "heal":
                # Find the best healing item in the inventory
                best_healing_item = None
                max_heal = 0
                for item in player.inventory:
                    if item.get('type') == 'consumable' and item.get('effect_type') == 'heal':
                        heal_amount = item.get('effect_value', 0)
                        if heal_amount > max_heal:
                            max_heal = heal_amount
                            best_healing_item = item

                if best_healing_item:
                    original_player_hp = player.hp
                    player.hp, player.max_hp, player.current_max_inventory_slots, consumed_turn, _ = process_item_use(best_healing_item, player.hp, player.max_hp, player.inventory, player.current_max_inventory_slots, in_combat=True)
                    action_taken = consumed_turn

                    if player.hp <= 0:
                        print(f"You succumb to the effects of {add_article(best_healing_item['name'])}...")
                        break

                    if consumed_turn and player.hp != original_player_hp:
                        print(f"Your health is now {player.hp}/{player.max_hp} HP.")

                else:
                    print("You don't have any healing items.")
                    continue
            elif verb == "run":
                run_chance = random.random()
                if run_chance > 0.5:
                    print("You manage to escape the fight!")
                    current_room.monster = None
                    break
                else:
                    print("You try to run, but the monster blocks your path!")
                    action_taken = True

            elif verb == "use":
                if len(parts) < 2:
                    print("What do you want to use? (e.g., 'use healing potion')")
                    continue

                item_to_use_name_input = " ".join(parts[1:])
                item_found_in_inventory = None
                for item_dict in player.inventory:
                    if item_dict['name'].lower() == item_to_use_name_input:
                        item_found_in_inventory = item_dict
                        break

                if item_found_in_inventory:
                    original_player_hp = player.hp
                    player.hp, player.max_hp, player.current_max_inventory_slots, consumed_turn, stat_changes = process_item_use(item_found_in_inventory, player.hp, player.max_hp, player.inventory, player.current_max_inventory_slots, in_combat=True)
                    action_taken = consumed_turn
                    if 'remove_effect' in stat_changes:
                        effect_to_remove = stat_changes['remove_effect']
                        player_status_effects = [effect for effect in player_status_effects if effect['name'] != effect_to_remove]
                        print(f"The {effect_to_remove} has been cured.")
                    if 'add_effect_to_monster' in stat_changes:
                        effect_to_add = stat_changes['add_effect_to_monster']
                        monster_status_effects.append(effect_to_add)
                        print(f"The {monster_name} is now {effect_to_add['name']}!")

                    if player.hp <= 0:
                        print(f"You succumb to the effects of {add_article(item_found_in_inventory['name'])}...")
                        break

                    if consumed_turn and player.hp != original_player_hp:
                        print(f"Your health is now {player.hp}/{player.max_hp} HP.")

                else:
                    print(f"You don't have {item_to_use_name_input} in your inventory.")

            elif verb.startswith("inv"): # Changed to use .startswith
                display_inventory_and_stats(player)
                continue

        # Monster's turn
        if monster_current_hp > 0:
            if action_taken:
                monster_current_hp, is_monster_stunned = apply_and_tick_status_effects(monster_status_effects, monster_current_hp)
                if is_monster_stunned:
                    print(f"The {monster_name} is stunned and cannot act!")
                else:
                    monster_actual_damage = random.randint(monster_base_damage - monster_damage_variance, monster_base_damage + monster_damage_variance)
                    monster_is_crit = False
                    accuracy = 1.0
                    for effect in monster_status_effects:
                        if effect['name'] == 'Blindness':
                            accuracy += effect['effect']['modifier']

                    if random.random() > accuracy:
                        print(f"The {monster_name} misses!")
                        monster_actual_damage = 0
                    elif random.random() < monster_crit_chance:
                        monster_actual_damage = int(monster_actual_damage * monster_crit_multiplier)
                        monster_is_crit = True

                    player.hp, monster_actual_damage, monster_current_hp = handle_item_effects("on_take_damage", player.hp, monster_actual_damage, monster_current_hp, [player.equipped_weapon, player.equipped_armor, player.equipped_cloak, player.equipped_helmet] + player.equipped_misc_items)

                    damage_after_defense = max(0, monster_actual_damage - total_player_defense)
                    player.hp -= damage_after_defense

                    if monster_is_crit:
                        print(f"The {monster_name} lands a **CRITICAL HIT** on you for {monster_actual_damage} damage! Your defense absorbed {monster_actual_damage - damage_after_defense} damage.")
                    else:
                        print(f"The {monster_name} retaliates, hitting you for {monster_actual_damage} damage! Your defense absorbed {monster_actual_damage - damage_after_defense} damage.")

                    if 'status_effects' in monster_data:
                        for effect in monster_data['status_effects']:
                            if random.random() < effect['chance']:
                                player_status_effects.append(copy.deepcopy(effect))
                                print(f"You are now {effect['name']}!")

                    if player.hp <= 0:
                        print(f"The {monster_name} delivers a fatal blow...")
                        break
            else:
                # This else block handles cases where the player command didn't consume a turn (e.g., 'inv' or 'help')
                # We simply continue to the next player input without the monster taking a turn.
                continue

        if player.hp > 0 and monster_current_hp > 0:
            print(f"Your HP: {player.hp}/{player.max_hp} | {monster_name} HP: {monster_current_hp}")
            if player_status_effects:
                print(f"Your status: {', '.join([effect['name'] for effect in player_status_effects])}")
            if monster_status_effects:
                print(f"{monster_name}'s status: {', '.join([effect['name'] for effect in monster_status_effects])}")

    sound_manager.stop_music()
    sound_manager.play_music('ambient_music')

    if player.hp <= 0:
        return 'lose'
    return 'win'

def handle_gambler(player_gold, gambler_data):
    """
    Manages the gambling interaction with a Gambler NPC.
    Returns updated player_gold.
    """
    gambler_name = gambler_data.get('name', 'the Gambler')
    print(f"\n--- {gambler_name}'s Game of Chance ---")
    print(f"'{random.choice(gambler_data.get('dialogues', ['Care to try your luck?']))}'")

    while True:
        print(f"\nYour Gold: {player_gold}")
        print("Gambling commands: bet [amount] / leave")

        command_input = input("Gambler Action> ").lower().strip()
        parts = command_input.split()

        if not parts:
            continue

        verb = parts[0]

        if verb == "leave":
            print(f"'{random.choice(['Come back when you feel lucky!', 'May fortune favor you.'])}'")
            break

        elif verb == "bet":
            if len(parts) < 2 or not parts[1].isdigit():
                print("Invalid bet. Please enter a number. (e.g., 'bet 50')")
                continue

            bet_amount = int(parts[1])

            if bet_amount <= 0:
                print("You must bet a positive amount of gold.")
                continue

            if bet_amount > player_gold:
                print("You don't have enough gold for that bet.")
                continue

            print(f"You bet {bet_amount} gold.")
            player_gold -= bet_amount

            # Simulate dice rolls
            player_roll = random.randint(1, 6) + random.randint(1, 6)
            gambler_roll = random.randint(1, 6) + random.randint(1, 6)

            print("The dice are rolling...")
            time.sleep(1)
            print(f"You rolled a {player_roll}.")
            time.sleep(0.5)
            print(f"The Gambler rolled a {gambler_roll}.")

            if player_roll > gambler_roll:
                winnings = bet_amount * 2
                player_gold += winnings
                print(f"You win! You receive {winnings} gold.")
            elif gambler_roll > player_roll:
                print("You lose! The Gambler takes your bet.")
            else:
                player_gold += bet_amount
                print("It's a draw! Your bet is returned.")

        else:
            print("Invalid command. Type 'bet [amount]' or 'leave'.")

    return player_gold

def handle_horde_combat(player_hp, max_hp, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, player_shield_value, equipped_armor_value, equipped_cloak, player_inventory, current_max_inventory_slots, player_gold, equipped_weapon, player_xp, player_level, xp_to_next_level, player_quests, player_keychain, current_room, equipped_misc_items, player_effects, sound_manager, equipped_helmet, player_class, player_unlocked_skills, player_skill_points):
    horde_data = current_room.horde_data
    horde_name = horde_data['name']
    horde_monsters = horde_data['monsters']
    horde_size = random.randint(horde_data['size'][0], horde_data['size'][1])
    monsters_defeated_in_horde = 0

    print(f"\nA horde of {horde_size} monsters appears! It's a {horde_name}!")

    total_gold_gained = 0
    total_xp_gained = 0

    for i in range(horde_size):
        monster_name = random.choice(horde_monsters)
        monster_def = next((m for m in MONSTERS if m['name'] == monster_name), None)
        if not monster_def:
            continue

        monster_data = dict(monster_def)
        print(f"\n--- Horde Battle ({i+1}/{horde_size}) ---")

        player_hp, max_hp, monster_data, gold_gained, player_xp, player_level, xp_to_next_level, player_quests, \
        player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items, player_skill_points = \
            handle_combat(player_hp, max_hp, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, \
                          monster_data, player_shield_value, equipped_armor_value, equipped_cloak, player_inventory, current_max_inventory_slots, \
                          player_gold, equipped_weapon, player_xp, player_level, xp_to_next_level, player_quests, player_keychain, current_room, equipped_misc_items, player_effects, sound_manager, 0, 0, equipped_helmet, player_class, player_unlocked_skills, player_skill_points)

        if player_hp <= 0:
            return 'lose', player_hp, max_hp, player_gold, player_xp, player_level, xp_to_next_level, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items, monsters_defeated_in_horde, player_skill_points

        if monster_data is None:
            monsters_defeated_in_horde += 1
        total_gold_gained += gold_gained
        total_xp_gained += monster_def.get('xp_reward', 0)

    print(f"\n--- Horde Defeated! ---")
    print(f"You defeated the {horde_name}!")
    print(f"Total Gold Gained: {total_gold_gained}")
    print(f"Total XP Gained: {total_xp_gained}")

    player_gold += total_gold_gained
    player_xp += total_xp_gained

    player_xp, player_level, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points = \
        check_for_level_up(player_xp, player_level, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points)

    # Special reward for defeating the horde
    if random.random() < 0.5: # 50% chance of a special item
        item_def = get_item_by_name(random.choice([item['name'] for item in ALL_ITEMS if item.get('type') not in ['winning_item', 'key']]))
        if item_def:
            if len(player_inventory) < current_max_inventory_slots:
                scaled_item = scale_item_for_player_level(item_def, player_level)
                player_inventory.append(scaled_item)
                print(f"You found a special item: {add_article(scaled_item['name'])}!")
            else:
                print("You would have received a special item, but your inventory is full!")

    return 'continue', player_hp, max_hp, player_gold, player_xp, player_level, xp_to_next_level, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items, monsters_defeated_in_horde, player_skill_points

# MODIFIED: Added equipped_cloak and equipped_misc_items to parameters
def handle_shop(player, vendor_data, sound_manager):
    """
    Manages the shop interaction with a vendor NPC.
    Modifies the player object directly.
    """
    vendor_name = vendor_data['name']
    shop_stock_names = vendor_data.get('shop_stock', [])
    shop_dialogues = vendor_data.get('dialogues', ["What're ya buyin'?", "Come back anytime!"])

    shop_items = []
    for item_name in shop_stock_names:
        item_def = get_item_by_name(item_name.lower())
        if item_def and item_def.get('shop_price') is not None:
            scaled_item = scale_item_for_player_level(item_def, player.level)
            shop_items.append(scaled_item)

    sound_manager.stop_music()
    sound_manager.play_music('vendor_music')
    print(f"\n--- {vendor_name}'s Shop ---")
    print(random.choice(shop_dialogues))

    while True:
        print(f"\nYour Gold: {player.gold}")
        print(f"Your Inventory: ({len(player.inventory)}/{player.current_max_inventory_slots})")
        print("Shop commands: buy / sell / exit")

        shop_command_input = input("Shop Action> ").lower().strip()
        parts = shop_command_input.split()

        if not parts:
            continue

        verb = parts[0]

        if verb == "buy":
            print("\nItems for Sale:")
            if not shop_items:
                print("    (Empty - looks like he's out of stock!)")
            else:
                for i, item_dict in enumerate(shop_items):
                    price = item_dict.get('shop_price', 'N/A')
                    display_name = add_article(item_dict['name'])
                    print(f"    {i+1}. {display_name.capitalize()} ({item_dict.get('description', '')}) - {price} Gold")

            buy_choice = input("Enter item number to buy, or 'back': ").lower().strip()
            if buy_choice == 'back':
                continue

            if buy_choice.isdigit():
                item_num = int(buy_choice) - 1
                if 0 <= item_num < len(shop_items):
                    item_to_buy = shop_items[item_num]
                    item_price = item_to_buy.get('shop_price')

                    if item_price is None:
                        print(f"That item ({item_to_buy['name']}) is not for sale.")
                    elif player.gold >= item_price:
                        if item_to_buy.get('type') == 'key':
                            player.keychain.append(copy.deepcopy(item_to_buy))
                            player.gold -= item_price
                            print(f"You bought {add_article(item_to_buy['name'])} for {item_price} gold! It's added to your keychain.")
                        elif len(player.inventory) < player.current_max_inventory_slots:
                            player.gold -= item_price
                            player.inventory.append(copy.deepcopy(item_to_buy))
                            print(f"You bought {add_article(item_to_buy['name'])} for {item_price} gold!")
                        else:
                            print("Your inventory is full! You need to drop an item first.")
                    else:
                        print(f"You don't have enough gold for {add_article(item_to_buy['name'])}.")
                else:
                    print("Invalid item number.")
            else:
                print("Invalid buy command.")

        elif verb == "sell":
            sellable_items = [item for item in player.inventory if item.get('shop_price') is not None and item.get('type') != 'winning_item']

            print("\nYour Items to Sell:")
            if not sellable_items:
                print("    (You have no items that can be sold.)")
            else:
                for i, item_dict in enumerate(sellable_items):
                    sell_price = int(item_dict['shop_price'] * SELL_PRICE_MULTIPLIER)
                    display_str = f"    {i+1}. {add_article(item_dict['name'])}"
                    # Check if the item is equipped
                    if item_dict is player.equipped_weapon or item_dict is player.equipped_shield or item_dict is player.equipped_armor or item_dict is player.equipped_cloak or item_dict in player.equipped_misc_items:
                        display_str += " (EQUIPPED)"
                    print(f"{display_str} - Sells for {sell_price} Gold")

            sell_choice = input("Enter item number to sell, or 'back': ").lower().strip()
            if sell_choice == 'back':
                continue

            if sell_choice.isdigit():
                item_num = int(sell_choice) - 1
                if 0 <= item_num < len(sellable_items):
                    item_to_sell = sellable_items[item_num]

                    # Unequip if necessary
                    if item_to_sell is player.equipped_weapon: player.equipped_weapon = None
                    if item_to_sell is player.equipped_shield: player.equipped_shield = None
                    if item_to_sell is player.equipped_armor: player.equipped_armor = None
                    if item_to_sell is player.equipped_cloak: player.equipped_cloak = None
                    if item_to_sell in player.equipped_misc_items: player.equipped_misc_items.remove(item_to_sell)

                    sell_price = int(item_to_sell['shop_price'] * SELL_PRICE_MULTIPLIER)
                    player.gold += sell_price
                    player.inventory.remove(item_to_sell)
                    print(f"You sold {add_article(item_to_sell['name'])} for {sell_price} gold!")
                else:
                    print("Invalid item number.")
            else:
                print("Invalid sell command.")

        elif verb == "exit":
            print(random.choice(shop_dialogues))
            sound_manager.stop_music()
            sound_manager.play_music('ambient_music')
            return
        else:
            print("Invalid shop command. Type 'buy', 'sell', or 'exit'.")

def display_inventory_and_stats(player):
    if not player.inventory and not player.keychain:
        print("Your inventory is empty.")
    else:
        print(f"Your Health: {player.hp}/{player.max_hp} HP.")
        print(f"Your Level: {player.level} (XP: {player.xp}/{player.xp_to_next_level})")
        print(f"You are carrying ({len(player.inventory)}/{player.current_max_inventory_slots}):")
        if player.inventory:
            for item_dict in player.inventory:
                display_str = f"    - {add_article(item_dict['name'])}"
                item_type = item_dict.get('type')
                if item_type == 'consumable':
                    effect_type = item_dict.get('effect_type')
                    effect_value = item_dict.get('effect_value')
                    if effect_type == 'heal' and isinstance(effect_value, int):
                        display_str += f" (Heals {effect_value} HP)"
                elif item_type == 'weapon':
                    display_str += f" (Damage: {item_dict.get('damage', '?')})"
                    if player.equipped_weapon and player.equipped_weapon['name'].lower() == item_dict['name'].lower():
                        display_str += " (EQUIPPED)"
                elif item_type == 'armor':
                    item_subtype = item_dict.get('subtype')
                    if item_subtype == 'body_armor':
                        display_str += f" (Defense: {item_dict.get('defense', '?')})"
                        if player.equipped_armor and player.equipped_armor['name'].lower() == item_dict['name'].lower():
                            display_str += " (EQUIPPED)"
                    elif item_subtype == 'cloak':
                        display_str += f" (Defense: {item_dict.get('defense', '?')})"
                        if player.equipped_cloak and player.equipped_cloak['name'].lower() == item_dict['name'].lower():
                            display_str += " (EQUIPPED)"
                elif item_type == 'backpack':
                    display_str += f" (+{item_dict.get('effect_value', '?')} Slots)"
                elif item_type == 'shield':
                    display_str += f" (Defense: {item_dict.get('defense', '?')})"
                    if player.equipped_shield and player.equipped_shield['name'].lower() == item_dict['name'].lower():
                        display_str += " (EQUIPPED)"
                elif item_type == 'equipment':
                    display_str += f" (Effect: {item_dict.get('effect_type', 'unknown')})"
                    if item_dict in player.equipped_misc_items:
                        display_str += " (EQUIPPED)"
                print(display_str)
        else:
            print("    (Empty)")

        print("Your Keychain:")
        if player.keychain:
            for item_dict in player.keychain:
                print(f"    - {add_article(item_dict['name'])} (Type: {item_dict.get('key_type', '?')} key)")
        else:
            print("    (Empty)")

        print(f"Your Gold: {player.gold}")
        print(f"Total Defense: {calculate_total_defense(player.equipped_shield, player.equipped_armor, player.equipped_cloak, player.equipped_helmet)}")
        print(f"Attack Power: {player.attack_power} (+/-{player.attack_variance})")
        print(f"Critical Chance: {player.crit_chance*100:.0f}% (x{player.crit_multiplier:.1f} Damage)")
        if player.equipped_weapon:
            print(f"Equipped Weapon: {player.equipped_weapon['name']} (Damage: {player.equipped_weapon.get('damage', '?')})")
        else:
            print("Equipped Weapon: Fists (Damage: 5)")
        if player.effects:
            print("\n--- Active Effects ---")
            for effect in player.effects:
                print(f"  - {effect['message'].split('!')[0]} ({effect['duration']} turns remaining)")
            print("----------------------")

def handle_hideout(player):
    """
    Manages the player's personal hideout.
    Modifies the player object directly.
    """
    print("\n--- Your Personal Hideout ---")
    print("A quiet, personal space. You can stash items here.")

    while True:
        print("\nHideout commands: stash / unstash / view / inv / leave")
        hideout_command_input = input("Hideout Action> ").lower().strip()
        parts = hideout_command_input.split()

        if not parts:
            continue

        verb = parts[0]

        if verb.startswith("inv"):
            display_inventory_and_stats(player)
        elif verb == "stash":
            item_to_stash_name = " ".join(parts[1:])
            item_to_stash = None
            for item in player.inventory:
                if item['name'].lower() == item_to_stash_name.lower():
                    item_to_stash = item
                    break

            if item_to_stash:
                player.inventory.remove(item_to_stash)
                player.stash.append(item_to_stash)
                print(f"You stashed the {item_to_stash['name']}.")
            else:
                print("You don't have that item.")
        elif verb == "unstash":
            item_to_unstash_name = " ".join(parts[1:])
            item_to_unstash = None
            for item in player.stash:
                if item['name'].lower() == item_to_unstash_name.lower():
                    item_to_unstash = item
                    break

            if item_to_unstash:
                if len(player.inventory) < player.current_max_inventory_slots:
                    player.stash.remove(item_to_unstash)
                    player.inventory.append(item_to_unstash)
                    print(f"You unstashed the {item_to_unstash['name']}.")
                else:
                    print("Your inventory is full.")
            else:
                print("You don't have that item in your stash.")
        elif verb == "view":
            if not player.stash:
                print("Your stash is empty.")
            else:
                print("\n--- Your Stash ---")
                for item_dict in player.stash:
                    display_str = f"    - {add_article(item_dict['name'])}"
                    print(display_str)
                print("--------------------")
        elif verb == "leave":
            print("You leave your hideout.")
            return
        else:
            print("Invalid hideout command.")

def handle_inn(player, sound_manager):
    """
    Manages the inn interaction, allowing the player to rest and talk to quest givers.
    Modifies the player object directly.
    """
    sound_manager.stop_music()
    sound_manager.play_music('inn_music')
    print("\n--- The Hearth and Home Inn ---")
    print("You find yourself in a cozy, bustling inn. A warm fire crackles in the hearth.")

    while True:
        print(f"\nYour HP: {player.hp}/{player.max_hp}")
        if player.has_hideout_key:
            print("Inn commands: rest / talk / enter hideout / inv / leave")
        else:
            print("Inn commands: rest / talk / inv / leave")
        inn_command_input = input("Inn Action> ").lower().strip()
        parts = inn_command_input.split()

        if not parts:
            continue

        verb = parts[0]

        if verb == "rest":
            if player.hp < player.max_hp:
                player.hp = player.max_hp
                print("\nYou rest by the fire, feeling your wounds mend and your spirit lift. You are fully healed.")
            else:
                print("\nYou are already at full health and feeling great.")

        elif verb.startswith("inv"):
            display_inventory_and_stats(player)
        elif verb == "talk":
            quest_givers = [n for n in NPCs if n.get('type') == 'quest_giver' or n.get('name') == 'Key Vendor']
            if not quest_givers:
                print("The inn is quiet today; no one seems to have any quests.")
                continue

            if len(parts) == 1:
                print("\nPeople in the inn:")
                for npc in quest_givers:
                    print(f"  - {npc['name']}")
                print("\n(To talk to someone, type 'talk [name]')")
            else:
                npc_name_to_talk = " ".join(parts[1:])
                chosen_npc = next((n for n in quest_givers if n['name'].lower() == npc_name_to_talk.lower()), None)

                if chosen_npc and chosen_npc['name'] == 'Key Vendor':
                    handle_shop(player, chosen_npc, sound_manager)
                    if any(item.get('key_type') == 'hideout' for item in player.keychain):
                        player.has_hideout_key = True
                elif chosen_npc:
                    interact_with_quest_giver(chosen_npc, player, sound_manager)
                else:
                    print(f"You don't see anyone named '{npc_name_to_talk}' here.")

        elif verb == "enter" and "hideout" in parts:
            if player.has_hideout_key:
                handle_hideout(player)
            else:
                print("You don't have a key to a hideout.")

        elif verb == "leave":
            print("You step out of the inn, back into the dungeon's gloom.")
            sound_manager.stop_music()
            sound_manager.play_music('ambient_music')
            return
        else:
            print("Invalid inn command. Type 'rest', 'talk', or 'leave'.")


def interact_with_quest_giver(npc, player, sound_manager):
    """Handles all interaction logic with a quest-giving NPC."""
    print(f"\nYou approach {npc['name']}.")

    # Reputation-based dialogue
    faction_id = npc.get('faction')
    if faction_id and faction_id in player.reputation:
        reputation_level = player.reputation[faction_id]
        if reputation_level > 50:
            for dialogue in npc.get('dialogue_reputation', []):
                if dialogue['reputation_level'] == 'friendly':
                    print(f"'{dialogue['dialogue']}'")
                    break
        elif reputation_level < -50:
            for dialogue in npc.get('dialogue_reputation', []):
                if dialogue['reputation_level'] == 'hostile':
                    print(f"'{dialogue['dialogue']}'")
                    break
        else:
            for dialogue in npc.get('dialogue_reputation', []):
                if dialogue['reputation_level'] == 'neutral':
                    print(f"'{dialogue['dialogue']}'")
                    break
    else:
        print(f"'{npc.get('dialogues', ['...'])[0]}'")

    npc_quest_id = npc.get('current_quest_id')
    if not npc_quest_id:
        return

    quest_status = get_player_quest_status(player.quests, npc_quest_id)
    quest_def = get_quest_by_id(npc_quest_id)

    if quest_status == 'not_started' and quest_def:
        if player.level >= quest_def.get('required_level', 1) and (not quest_def.get('prerequisite_quest') or get_player_quest_status(player.quests, quest_def.get('prerequisite_quest')) == 'completed'):
            dialogue = quest_def.get('dialogue_offer', "I have a task for you.").format(target_count=quest_def.get('target_count', 0))
            print(f"{npc['name']}: '{dialogue}'")
            accept = input("Accept quest? (yes/no): ").lower().strip()
            if accept in ['yes', 'y']:
                if quest_def['type'] == 'find_npc':
                    player.quests[npc_quest_id] = {'status': 'active', 'found_npc': False}
                else:
                    player.quests[npc_quest_id] = {'status': 'active', 'current_count': 0}
                print(f"You accept the quest: '{quest_def['name']}'!")
        else:
            print(f"{npc['name']}: '{quest_def.get('dialogue_unavailable', 'I have no task for you.')}'")
    elif quest_status == 'active' and quest_def:
        if quest_def['type'] in ['defeat_any_monster', 'defeat_monster', 'fetch_item']:
            dialogue = quest_def.get('dialogue_active', "How goes the quest?").format(
                current_count=player.quests[npc_quest_id].get('current_count', 0),
                target_count=quest_def.get('target_count', 0)
            )
        else:
            dialogue = quest_def.get('dialogue_active', "How goes the quest?")
        print(f"{npc['name']}: '{dialogue}'")
    elif quest_status == 'complete_ready' and quest_def:
        if quest_def['type'] in ['defeat_any_monster', 'defeat_monster', 'fetch_item']:
            dialogue = quest_def.get('dialogue_complete_ready', "You've done it!").format(
                current_count=player.quests[npc_quest_id].get('current_count', 0),
                target_count=quest_def.get('target_count', 0)
            )
        else:
            dialogue = quest_def.get('dialogue_complete_ready', "You've done it!")
        print(f"{npc['name']}: '{dialogue}'")
        turn_in = input("Turn in quest? (yes/no): ").lower().strip()
        if turn_in in ['yes', 'y']:
            if quest_def['type'] == 'fetch_item' and not has_player_enough_items(player.inventory, quest_def['target_item'], quest_def['target_count']):
                print("You don't have the required items!")
            else:
                if quest_def['type'] == 'fetch_item':
                    remove_items_from_inventory(player.inventory, quest_def['target_item'], quest_def['target_count'])
                    print(f"You hand over {quest_def['target_count']} {quest_def['target_item']}(s).")

                player.gold += quest_def.get('reward_gold', 0)
                player.xp += quest_def.get('reward_xp', 0)
                print(f"Quest complete! You receive {quest_def.get('reward_gold', 0)} gold and {quest_def.get('reward_xp', 0)} XP.")

                reward_item_name = quest_def.get('reward_item')
                if reward_item_name:
                    item_def = get_item_by_name(reward_item_name)
                    if item_def:
                        if len(player.inventory) < player.current_max_inventory_slots:
                            player.inventory.append(copy.deepcopy(item_def))
                            print(f"You also receive {add_article(item_def['name'])}!")
                        else:
                            print(f"You would have received an item, but your inventory is full!")

                player.quests[npc_quest_id]['status'] = 'completed'

                # Update reputation
                if 'rewards' in quest_def:
                    if 'reputation_gain' in quest_def['rewards']:
                        faction_id = quest_def['rewards']['reputation_gain']['faction']
                        amount = quest_def['rewards']['reputation_gain']['amount']
                        update_reputation(player.reputation, faction_id, amount)
                    if 'reputation_loss' in quest_def['rewards']:
                        faction_id = quest_def['rewards']['reputation_loss']['faction']
                        amount = quest_def['rewards']['reputation_loss']['amount']
                        update_reputation(player.reputation, faction_id, -amount)

                player.xp, player.level, player.xp_to_next_level, player.hp, player.max_hp, player.attack_power, player.attack_variance, player.crit_chance, player.crit_multiplier, player.skill_points = \
                    check_for_level_up(player.xp, player.level, player.xp_to_next_level, player.hp, player.max_hp, player.attack_power, player.attack_variance, player.crit_chance, player.crit_multiplier, player.skill_points)
    elif quest_status == 'completed' and quest_def:
        print(f"{npc['name']}: '{quest_def.get('dialogue_complete_turn_in', 'Thank you for your help.')}'")

    return

# MODIFIED: Added equipped_cloak to parameters and save state
def save_game(player, world):
    """Saves the current game state to 'savegame.json'."""

    # Convert world dungeons to a serializable format
    serializable_dungeons = {}
    for (x, y), dungeon in world.dungeons.items():
        serializable_rooms = {}
        # It's important to handle the case where dungeon.rooms might be None or not iterable
        if dungeon.rooms:
            for (rx, ry), room in dungeon.rooms.items():
                serializable_rooms[f"{rx},{ry}"] = room.__dict__

        dungeon_data = {
            'width': dungeon.width,
            'height': dungeon.height,
            'player_level': dungeon.player_level,
            'grid': dungeon.grid,
            'rooms': serializable_rooms,
            'start_pos': dungeon.start_pos,
        }
        serializable_dungeons[f"{x},{y}"] = dungeon_data

    game_state = {
        'player': player.__dict__,
        'world': {
            'dungeons': serializable_dungeons,
        }
    }
    try:
        with open('savegame.json', 'w') as f:
            json.dump(game_state, f, indent=4)
        print("Game saved successfully!")
    except (IOError, TypeError) as e:
        print(f"Error: Could not save game: {e}")

def load_game():
    """Loads the game state from 'savegame.json' and returns it."""
    try:
        with open('savegame.json', 'r') as f:
            game_state = json.load(f)

        # Reconstruct Player
        player_data = game_state['player']
        class_data = GAME_DATA['character_classes'][player_data['character_class']]
        player = Player(player_data['name'], player_data['character_class'], class_data)
        player.__dict__.update(player_data)

        # Reconstruct World
        world_data = game_state['world']
        world = World(player, generate_initial_dungeon=False)

        # Reconstruct Dungeons
        for key, dungeon_data in world_data['dungeons'].items():
            x, y = map(int, key.split(','))
            dungeon = Dungeon(dungeon_data['player_level'])
            dungeon.width = dungeon_data['width']
            dungeon.height = dungeon_data['height']
            dungeon.grid = dungeon_data['grid']
            dungeon.start_pos = dungeon_data['start_pos']

            # Reconstruct Rooms
            deserialized_rooms = {}
            if dungeon_data.get('rooms'):
                for r_key, room_data in dungeon_data['rooms'].items():
                    rx, ry = map(int, r_key.split(','))
                    room = Room(rx, ry, room_data['width'], room_data['height'])
                    room.__dict__.update(room_data)
                    deserialized_rooms[(rx, ry)] = room
            dungeon.rooms = deserialized_rooms

            world.dungeons[(x, y)] = dungeon

        world.current_dungeon = world.dungeons.get((player.world_x, player.world_y))

        print("\nGame loaded successfully!")
        return player, world

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"\nCould not load game: {e}")
        return None, None


# --- Meta-Progression Functions ---
def load_meta_progress():
    """Loads the meta-progression data from 'metaprogress.json'."""
    try:
        with open('metaprogress.json', 'r') as f:
            meta_progress = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        meta_progress = {
            "soul_shards": 0,
            "upgrades": {
                "max_hp": 0
            }
        }
    return meta_progress

def save_meta_progress(meta_progress):
    """Saves the meta-progression data to 'metaprogress.json'."""
    try:
        with open('metaprogress.json', 'w') as f:
            json.dump(meta_progress, f, indent=4)
        print("Meta-progression saved.")
    except IOError:
        print("Error: Could not save meta-progression. Check file permissions.")


# --- Classes ---

class Player:
    """Encapsulates all player-related state."""
    def __init__(self, name, class_name, character_class_data):
        self.name = name
        self.character_class = class_name

        # Coordinates
        self.world_x = 0
        self.world_y = 0
        self.x = 0
        self.y = 0

        # Core Stats
        self.hp = character_class_data['starting_stats']['max_hp']
        self.max_hp = character_class_data['starting_stats']['max_hp']
        self.attack_power = character_class_data['starting_stats']['attack_power']
        self.attack_bonus = 0
        self.attack_variance = character_class_data['starting_stats']['attack_variance']
        self.crit_chance = character_class_data['starting_stats']['crit_chance']
        self.crit_multiplier = character_class_data['starting_stats']['crit_multiplier']

        # XP and Leveling
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = calculate_xp_for_next_level(self.level)
        self.skill_points = 0
        self.unlocked_skills = []

        # Inventory and Equipment
        self.inventory = []
        self.current_max_inventory_slots = 5
        self.gold = 500
        self.keychain = []
        self.stash = []
        self.has_hideout_key = False

        # Equipped Items
        self.equipped_weapon = None
        self.equipped_shield = None
        self.equipped_armor = None
        self.equipped_cloak = None
        self.equipped_helmet = None
        self.equipped_misc_items = []

        # Effects and Quests
        self.effects = []
        self.quests = {}
        self.reputation = {}

        # Add starting equipment
        for item_name in character_class_data['starting_equipment']:
            item_def = get_item_by_name(item_name)
            if item_def:
                self.inventory.append(copy.deepcopy(item_def))

class World:
    """Manages the grid of dungeons."""
    def __init__(self, player, generate_initial_dungeon=True):
        self.dungeons = {}
        self.player = player
        self.current_dungeon = None
        if generate_initial_dungeon:
            self.generate_dungeon(0, 0)
            self.current_dungeon = self.dungeons[(0, 0)]

    def generate_dungeon(self, world_x, world_y):
        """Generates a new dungeon at the given world coordinates."""
        if (world_x, world_y) not in self.dungeons:
            new_dungeon = Dungeon(self.player.level)
            new_dungeon.generate()
            self.dungeons[(world_x, world_y)] = new_dungeon
            print(f"A new area has been discovered at ({world_x}, {world_y})!")
        return self.dungeons[(world_x, world_y)]

    def get_dungeon(self, world_x, world_y):
        """Gets the dungeon at the specified coordinates, generating it if it doesn't exist."""
        return self.dungeons.get((world_x, world_y)) or self.generate_dungeon(world_x, world_y)

    def move_player(self, dx, dy):
        """Handles player movement between dungeons."""
        new_world_x = self.player.world_x + dx
        new_world_y = self.player.world_y + dy

        self.current_dungeon = self.get_dungeon(new_world_x, new_world_y)
        self.player.world_x = new_world_x
        self.player.world_y = new_world_y

        # Adjust player's local coordinates for seamless transition
        if dy == -1: # Moved North
            self.player.y = self.current_dungeon.height - 1
        elif dy == 1: # Moved South
            self.player.y = 0
        elif dx == -1: # Moved West
            self.player.x = self.current_dungeon.width - 1
        elif dx == 1: # Moved East
            self.player.x = 0

class Dungeon:
    """Represents a single level of the dungeon, containing a grid of rooms."""
    def __init__(self, player_level, width=80, height=40):
        self.width = width
        self.height = height
        self.player_level = player_level
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.rooms = {} # Stores Room objects by (x, y) tuple
        self.start_pos = None

    class _BSPNode:
        """Helper class for Binary Space Partitioning."""
        def __init__(self, x, y, width, height):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.left = None
            self.right = None
            self.room = None

        def split(self, min_size=10):
            if self.left or self.right:
                return False # Already split

            split_horizontally = random.choice([True, False])
            if self.width > self.height and self.width / self.height >= 1.25:
                split_horizontally = False
            elif self.height > self.width and self.height / self.width >= 1.25:
                split_horizontally = True

            max_size = (self.height if split_horizontally else self.width) - min_size
            if max_size < min_size:
                return False

            split_pos = random.randint(min_size, max_size)

            if split_horizontally:
                self.left = Dungeon._BSPNode(self.x, self.y, self.width, split_pos)
                self.right = Dungeon._BSPNode(self.x, self.y + split_pos, self.width, self.height - split_pos)
            else:
                self.left = Dungeon._BSPNode(self.x, self.y, split_pos, self.height)
                self.right = Dungeon._BSPNode(self.x + split_pos, self.y, self.width - split_pos, self.height)

            return True

    def generate(self, min_room_size=8, bsp_depth=4):
        """Generates the dungeon layout using Binary Space Partitioning."""
        self.grid = [['#' for _ in range(self.width)] for _ in range(self.height)]

        root = self._BSPNode(0, 0, self.width, self.height)
        nodes = [root]

        for _ in range(bsp_depth):
            new_nodes = []
            for node in nodes:
                if node.split(min_size=min_room_size * 2):
                    new_nodes.append(node.left)
                    new_nodes.append(node.right)
                else:
                    new_nodes.append(node)
            nodes = new_nodes

        leaf_nodes = [node for node in nodes if not (node.left or node.right)]

        for node in leaf_nodes:
            w = random.randint(min_room_size, node.width - 2)
            h = random.randint(min_room_size, node.height - 2)
            x = node.x + random.randint(1, node.width - w - 1)
            y = node.y + random.randint(1, node.height - h - 1)

            room = Room(x, y, w, h, "")
            node.room = room

            for i in range(y, y + h):
                for j in range(x, x + w):
                    if 0 <= i < self.height and 0 <= j < self.width:
                        self.grid[i][j] = '.'

            self.rooms[(x, y)] = room

        self._connect_rooms(root)
        self._populate_rooms(leaf_nodes)

    def _populate_rooms(self, leaf_nodes):
        if not leaf_nodes: return

        # 1. Narrative Graph & Placement
        # Find start and end nodes (furthest apart)
        start_node, end_node = leaf_nodes[0], leaf_nodes[-1]
        max_dist = 0
        if len(leaf_nodes) > 1:
            for i in range(len(leaf_nodes)):
                for j in range(i + 1, len(leaf_nodes)):
                    n1, n2 = leaf_nodes[i], leaf_nodes[j]
                    dist = abs(n1.room.x - n2.room.x) + abs(n1.room.y - n2.room.y)
                    if dist > max_dist:
                        max_dist = dist
                        start_node, end_node = n1, n2

        # Find a node roughly in the middle for the mini-boss
        mid_point_x = (start_node.room.x + end_node.room.x) // 2
        mid_point_y = (start_node.room.y + end_node.room.y) // 2

        potential_miniboss_nodes = [n for n in leaf_nodes if n is not start_node and n is not end_node]
        if not potential_miniboss_nodes:
            potential_miniboss_nodes = leaf_nodes # Fallback if only 2-3 rooms

        miniboss_node = min(potential_miniboss_nodes, key=lambda n: abs(n.room.x - mid_point_x) + abs(n.room.y - mid_point_y), default=None)
        if miniboss_node is None: # Handle case with very few rooms
            miniboss_node = end_node

        # Place Start Room
        self.start_pos = (start_node.room.x + 2, start_node.room.y + 2)
        start_node.room.is_start = True
        start_node.room.description = "You find yourself in the starting chamber of a new dungeon level."

        # Place Final Boss
        final_boss_def = next((m for m in MONSTERS if m.get('name') == "Primeval Horror"), None)
        if final_boss_def:
            end_node.room.monster = copy.deepcopy(final_boss_def)
            end_node.room.description = "A room of immense dread. A Primeval Horror blocks the final exit."

        # Place Mini-Boss and Key
        miniboss_def = next((m for m in MONSTERS if m.get('name') == "Crystal Golem"), None)
        boss_key_def = get_item_by_name("crystal key")
        if miniboss_def and boss_key_def and miniboss_node is not end_node:
            miniboss_instance = copy.deepcopy(miniboss_def)
            miniboss_instance['item_drop'] = boss_key_def['name']
            miniboss_node.room.monster = miniboss_instance
            miniboss_node.room.description = "A Crystal Golem guards this chamber fiercely."

        # 2. Populate all other rooms
        narrative_rooms = {start_node.room, end_node.room}
        if miniboss_node:
            narrative_rooms.add(miniboss_node.room)

        for node in leaf_nodes:
            room = node.room
            if room in narrative_rooms:
                continue

            # Generate a base description
            adj = random.choice(ADJECTIVES)
            room_type_desc = random.choice(ROOM_TYPES)
            detail = random.choice(DETAILS)
            room.description = f"You are in a {adj} {room_type_desc}. You notice {detail}."

            # Independent chances for each feature
            if PUZZLES and random.random() < PUZZLE_SPAWN_CHANCE:
                room.puzzle = copy.deepcopy(random.choice(PUZZLES))
                if room.puzzle: room.puzzle['solved'] = False

            if MONSTERS and random.random() < 0.20:
                eligible_monsters, monster_weights = [], []
                for monster_def in MONSTERS:
                    level_diff = monster_def.get('level', 1) - self.player_level
                    if MONSTER_SPAWN_LEVEL_MIN_OFFSET <= level_diff <= MONSTER_SPAWN_LEVEL_MAX_OFFSET:
                        weight = MONSTER_LEVEL_WEIGHTS.get(level_diff, 0)
                        if weight > 0:
                            eligible_monsters.append(monster_def)
                            monster_weights.append(weight)
                if eligible_monsters:
                    room.monster = copy.deepcopy(random.choices(eligible_monsters, weights=monster_weights, k=1)[0])

            if ALL_ITEMS and random.random() < 0.35:
                item_spawn_weights = GAME_DATA.get('item_spawn_weights', {})
                possible_items = [item for item in ALL_ITEMS if item.get('type') not in ['winning_item', 'key']]
                weights = [item_spawn_weights.get(item.get('subtype', item.get('type')), 0.05) for item in possible_items]
                if possible_items and sum(weights) > 0:
                    chosen_item = random.choices(possible_items, weights=weights, k=1)[0]
                    room.item = scale_item_for_player_level(chosen_item, self.player_level)

            if NPCs and random.random() < 0.12:
                eligible_npcs = [n for n in NPCs if n.get('type') not in ['vendor', 'quest_giver']]
                if eligible_npcs: room.npc = copy.deepcopy(random.choice(eligible_npcs))

            if HAZARDS and random.random() < 0.15:
                room.hazard = copy.deepcopy(random.choice(HAZARDS))

            if random.random() < CRAFTING_STATION_SPAWN_CHANCE:
                room.crafting_station = {"name": "Crafting Station"}

    def _connect_rooms(self, node):
        if not node.left or not node.right:
            return

        self._connect_rooms(node.left)
        self._connect_rooms(node.right)

        room1 = self._get_room_from_node(node.left)
        room2 = self._get_room_from_node(node.right)
        if room1 and room2:
            self._create_corridor_between_rooms(room1, room2)

    def _get_room_from_node(self, node):
        if node.room:
            return node.room
        else:
            if node.left and node.right:
                return random.choice([self._get_room_from_node(node.left), self._get_room_from_node(node.right)])
            elif node.left:
                return self._get_room_from_node(node.left)
            elif node.right:
                return self._get_room_from_node(node.right)
            return None

    def _create_corridor_between_rooms(self, room1, room2):
        x1, y1 = room1.x + room1.width // 2, room1.y + room1.height // 2
        x2, y2 = room2.x + room2.width // 2, room2.y + room2.height // 2

        if x2 > x1: room1.exits['east'] = True; room2.exits['west'] = True
        elif x2 < x1: room1.exits['west'] = True; room2.exits['east'] = True
        if y2 > y1: room1.exits['south'] = True; room2.exits['north'] = True
        elif y2 < y1: room1.exits['north'] = True; room2.exits['south'] = True

        self._create_corridor(x1, y1, x2, y2)

    def _create_corridor(self, x1, y1, x2, y2):
        if random.random() > 0.5:
            self._carve_h_corridor(x1, x2, y1)
            self._carve_v_corridor(y1, y2, x2)
        else:
            self._carve_v_corridor(y1, y2, x1)
            self._carve_h_corridor(x1, x2, y2)

    def _carve_h_corridor(self, x1, x2, y):
        if 0 <= y < self.height:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= x < self.width: self.grid[y][x] = '.'

    def _carve_v_corridor(self, y1, y2, x):
        if 0 <= x < self.width:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if 0 <= y < self.height: self.grid[y][x] = '.'

    def add_room(self, x, y, room):
        self.rooms[(x, y)] = room

    def get_room_at(self, x, y):
        for room in self.rooms.values():
            if room.x <= x < room.x + room.width and room.y <= y < room.y + room.height:
                return room
        return None

class Room:
    """Represents a single room in the dungeon."""
    def __init__(self, x, y, width, height, description=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.description = description
        self.exits = {}
        self.locked_exits = {}
        self.item = None
        self.npc = None
        self.hazard = None
        self.monster = None
        self.puzzle = None
        self.shrine = None
        self.crafting_station = None
        self.is_start = False

    def show_description(self):
        """Prints the full description of the room."""
        print(self.description)
        if self.item:
            print(f"You see {add_article(self.item['name'])} on the floor.")
        if self.npc:
            npc_description = self.npc.get('description', 'stands silently.')
            print(f"You spot {self.npc['name']}: {npc_description}")
        if self.shrine:
            print(f"Here, you find a {self.shrine['name']}. {self.shrine['description']}")
        if self.puzzle and not self.puzzle.get('solved', True):
            print(f"A puzzle here demands your attention: {self.puzzle['description']}")
        if self.hazard and not self.hazard.get('disarmed', False):
            print(f"Watch out! There's {self.hazard['name']} here!")
        if self.monster:
            print(f"A {self.monster['name']} {self.monster['description']}")

        exits_available = list(self.exits.keys())
        if exits_available:
            print(f"Exits: {', '.join(exits_available)}")
        else:
            print("There are no apparent exits from this room.")

def display_map(room_history, direction_history, current_room):
    """Generates and displays an ASCII map of the visited rooms."""
    # A mapping of room features to characters for the map
    map_legend = {
        'inn': 'I',
        'vendor': 'V',
        'puzzle': '?',
        'shrine': '!',
        'horde': 'H',
        'crafting': 'C',
        'boss': 'B',
        'start': 'S',
        'default': '·'
    }

    # Determine coordinates of all visited rooms
    coords = {}
    x, y = 0, 0
    # The full room history for map display should include the current room
    full_room_history = room_history + [current_room]
    coords[(x, y)] = full_room_history[0]

    path = [(x, y)]
    for i, direction in enumerate(direction_history):
        if direction == 'north':
            y -= 1
        elif direction == 'south':
            y += 1
        elif direction == 'east':
            x += 1
        elif direction == 'west':
            x -= 1
        if (i + 1) < len(full_room_history):
            coords[(x, y)] = full_room_history[i+1]
            path.append((x, y))

    player_x, player_y = x, y

    if not path:
        min_x, max_x, min_y, max_y = 0, 0, 0, 0
    else:
        min_x = min(p[0] for p in path)
        max_x = max(p[0] for p in path)
        min_y = min(p[1] for p in path)
        max_y = max(p[1] for p in path)

    width = (max_x - min_x + 1) * 2
    height = (max_y - min_y + 1) * 2
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    # Draw connections and rooms
    for i in range(len(path)):
        room_x, room_y = path[i]
        grid_y = (room_y - min_y) * 2
        grid_x = (room_x - min_x) * 2

        room_obj = coords.get((room_x, room_y))
        icon = map_legend['default']
        if room_obj:
            if getattr(room_obj, 'is_inn', False):
                icon = map_legend['inn']
            elif room_obj.npc and room_obj.npc.get('type') == 'vendor':
                icon = map_legend['vendor']
            elif room_obj.puzzle and not room_obj.puzzle.get('solved', True):
                icon = map_legend['puzzle']
            elif room_obj.shrine:
                icon = map_legend['shrine']
            elif room_obj.horde_data:
                icon = map_legend['horde']
            elif hasattr(room_obj, 'crafting_station'):
                icon = map_legend['crafting']
            elif room_obj.monster and room_obj.monster.get('is_boss_guardian', False):
                icon = map_legend['boss']

        if i == 0:
            icon = map_legend['start']

        grid[grid_y][grid_x] = icon

        if i < len(path) - 1:
            next_room_x, next_room_y = path[i+1]
            if next_room_x > room_x:
                grid[grid_y][grid_x + 1] = '-'
            elif next_room_x < room_x:
                grid[grid_y][grid_x - 1] = '-'
            elif next_room_y > room_y:
                grid[grid_y + 1][grid_x] = '|'
            elif next_room_y < room_y:
                grid[grid_y - 1][grid_x] = '|'

    grid_player_y = (player_y - min_y) * 2
    grid_player_x = (player_x - min_x) * 2
    grid[grid_player_y][grid_player_x] = '@'

    print("\n--- Dungeon Map ---")
    for row in grid:
        print("".join(row))
    print("-------------------")
    print("--- Legend ---")
    print("@: You      S: Start")
    print("I: Inn      V: Vendor")
    print("?: Puzzle   !: Shrine")
    print("H: Horde    C: Crafting")
    print("B: Boss     ·: Explored")
    print("--------------\n")


def game_loop(player, world, sound_manager, seed=None):
    """
    This function contains the main game loop logic for active gameplay.
    It returns a string indicating the game outcome and other stats.
    """
    global DEBUG, special_event_after_unlock
    monsters_defeated_this_run = 0
    rooms_travelled = 1
    direction_history = [] # For map drawing

    def process_puzzle_rewards(puzzle, player, current_room):
        rewards_data = puzzle.get('rewards', {})
        if 'xp_gold' in rewards_data:
            xp_reward = rewards_data['xp_gold'].get('xp', 0)
            gold_reward = rewards_data['xp_gold'].get('gold', 0)
            player.xp += xp_reward
            player.gold += gold_reward
            print(f"You gained {xp_reward} XP and {gold_reward} gold!")
            player.xp, player.level, player.xp_to_next_level, player.hp, player.max_hp, player.attack_power, player.attack_variance, player.crit_chance, player.crit_multiplier, player.skill_points = \
                check_for_level_up(player.xp, player.level, player.xp_to_next_level, player.hp, player.max_hp, player.attack_power, player.attack_variance, player.crit_chance, player.crit_multiplier, player.skill_points)
        if 'item' in rewards_data:
            item_def = get_item_by_name(rewards_data['item'])
            if item_def:
                if len(player.inventory) < player.current_max_inventory_slots:
                    player.inventory.append(copy.deepcopy(item_def))
                    print(f"You received {add_article(item_def['name'])}!")
                else:
                    print("You would have received an item, but your inventory is full!")
        if 'unlock_exit' in rewards_data:
            exit_to_unlock = rewards_data['unlock_exit']
            if exit_to_unlock in current_room.locked_exits:
                del current_room.locked_exits[exit_to_unlock]
                current_room.exits[exit_to_unlock] = True
                print(f"A new path to the {exit_to_unlock} has opened!")
        if 'special_event' in rewards_data:
            special_event_after_unlock = rewards_data['special_event']

    while True:
        current_dungeon = world.current_dungeon
        current_room = current_dungeon.get_room_at(player.x, player.y)

        if not current_room:
            print("You are lost in the void... returning to the start of this level.")
            player.x, player.y = current_dungeon.start_pos if current_dungeon.start_pos else (2, 2)
            continue

        display_room_content_summary(current_room, rooms_travelled, direction_history, seed)

        if current_room.hazard and not current_room.hazard.get('disarmed', False):
            hazard = current_room.hazard
            print(f"You encountered a {hazard['name']}!")
            player.hp -= hazard['damage']
            print(f"You take {hazard['damage']} damage.")
            current_room.hazard['disarmed'] = True # One-time damage
            if player.hp <= 0:
                return 'lose', monsters_defeated_this_run, rooms_travelled

        if current_room.monster:
            combat_result = handle_combat(player, current_room.monster, current_room, sound_manager)
            if combat_result == 'lose':
                return 'lose', monsters_defeated_this_run, rooms_travelled
            elif combat_result == 'win':
                monsters_defeated_this_run += 1
                # The monster is set to None inside handle_combat upon defeat
            # 'run' also handled inside handle_combat

        command_input = input("> ").lower().strip()
        parts = command_input.split()
        verb = parts[0] if parts else ""

        # --- System Commands ---
        if verb == "quit":
            return 'quit', monsters_defeated_this_run, rooms_travelled
        elif verb == "save":
            save_game(player, world)
            continue
        elif verb == "help":
            print("\nAvailable commands:")
            print("    go [direction]      - Move (e.g., 'go north').")
            print("    get [item]          - Pick up an item from the floor.")
            print("    drop [item]         - Drop an item from your inventory.")
            print("    inv / inventory     - Display your inventory and stats.")
            print("    look                - Re-examine the room.")
            print("    use [item]          - Use a consumable item.")
            print("    equip [item]        - Equip a weapon, shield, or armor.")
            print("    unequip [item]      - Unequip an item.")
            print("    talk                - Talk to an NPC in the room.")
            print("    answer [guess]      - Answer a riddle.")
            print("    pull [lever]        - Pull a lever.")
            print("    press               - Press a pressure plate.")
            print("    give [item] to [obj]- Give an item to something.")
            print("    skill               - View and use unlocked skills.")
            print("    quests              - View your active quests.")
            print("    map                 - Show the dungeon map.")
            print("    save                - Save your game.")
            print("    quit                - Exit the game.")
            continue
        elif verb == "look":
            continue # The loop will reprint the description automatically
        elif verb.startswith("inv"):
            display_inventory_and_stats(player)
            continue
        elif verb == "map":
            # display_map is not compatible with the new world structure yet.
            # This is a placeholder to avoid crashing.
            print("The map is currently unavailable.")
            continue
        elif verb == "credits":
             print(CREDITS_TEXT)
             continue
        elif verb == "quests":
            if not player.quests:
                print("You have no active quests.")
            else:
                print("\n--- Your Quests ---")
                for q_id, q_data in player.quests.items():
                    quest_def = get_quest_by_id(q_id)
                    if quest_def and q_data['status'] == 'active':
                        progress = ""
                        if quest_def['type'] in ['fetch_item', 'defeat_any_monster', 'defeat_monster']:
                            progress = f" ({q_data.get('current_count', 0)}/{quest_def['target_count']})"
                        print(f"  - {quest_def['name']}: {quest_def['description']}{progress}")
            continue
        elif verb == "skill":
            player.skill_points, player.unlocked_skills = handle_skill_tree(player.character_class, player.level, player.skill_points, player.unlocked_skills)
            continue

        # --- Movement ---
        elif verb in ["go", "north", "south", "east", "west"]:
            direction = verb if verb != "go" else (parts[1] if len(parts) > 1 else "")
            if not direction:
                print("Go where?")
                continue

            if direction in current_room.exits:
                dx, dy = 0, 0
                if direction == 'north': dy = -1
                elif direction == 'south': dy = 1
                elif direction == 'east': dx = 1
                elif direction == 'west': dx = -1

                new_x, new_y = player.x + dx, player.y + dy

                # Check for world boundary transition
                if not (0 <= new_y < current_dungeon.height and 0 <= new_x < current_dungeon.width):
                    print(f"You've reached the edge of this dungeon area and travel {direction}...")
                    world.move_player(dx, dy)
                else:
                    player.x, player.y = new_x, new_y

                rooms_travelled += 1
                direction_history.append(direction) # For map
            elif direction in current_room.locked_exits:
                print(f"The way {direction} is locked. {current_room.locked_exits[direction]}")
            else:
                 print("You can't go that way.")
            continue

        # --- Item Interaction ---
        elif verb == "get":
            if current_room.item:
                if len(player.inventory) < player.current_max_inventory_slots:
                    item_name = current_room.item['name']
                    player.inventory.append(current_room.item)
                    print(f"You pick up {add_article(item_name)}.")
                    current_room.item = None
                else:
                    print("Your inventory is full.")
            else:
                print("There is nothing to get.")
            continue
        elif verb == "drop":
            if len(parts) < 2:
                print("Drop what?")
                continue
            item_to_drop_name = " ".join(parts[1:])
            item_to_drop = next((item for item in player.inventory if item['name'].lower() == item_to_drop_name.lower()), None)
            if item_to_drop:
                if current_room.item is None:
                    player.inventory.remove(item_to_drop)
                    current_room.item = item_to_drop
                    print(f"You drop the {item_to_drop['name']}.")
                else:
                    print("There is already an item on the floor here.")
            else:
                print("You don't have that item.")
            continue
        elif verb == "use":
            if len(parts) < 2:
                print("Use what?")
                continue
            item_to_use_name = " ".join(parts[1:])
            item_to_use = next((item for item in player.inventory if item['name'].lower() == item_to_use_name.lower()), None)
            if item_to_use:
                player.hp, player.max_hp, player.current_max_inventory_slots, _, _ = process_item_use(item_to_use, player.hp, player.max_hp, player.inventory, player.current_max_inventory_slots, in_combat=False)
            else:
                print("You don't have that item.")
            continue
        elif verb == "equip":
            if len(parts) < 2:
                print("Equip what?")
                continue
            item_to_equip_name = " ".join(parts[1:])
            item_to_equip = next((item for item in player.inventory if item['name'].lower() == item_to_equip_name.lower()), None)
            if item_to_equip:
                player.equipped_shield, player.equipped_armor, player.equipped_cloak, player.equipped_weapon, player.equipped_misc_items, player.equipped_helmet = handle_equip_item(item_to_equip, player.equipped_shield, player.equipped_armor, player.equipped_cloak, player.equipped_weapon, player.equipped_misc_items, player.level, player.equipped_helmet)
                player.attack_power = recalculate_attack_power(player.level, player.equipped_weapon, player.equipped_misc_items, player.attack_bonus)
            else:
                print("You don't have that item.")
            continue
        elif verb == "unequip":
            # Basic unequip logic
            print("Unequip command is not fully implemented yet.")
            continue

        # --- NPC and Puzzle Interaction ---
        elif verb == "talk":
            if current_room.npc:
                npc = current_room.npc
                print(f"You talk to {npc['name']}.")
                if npc.get('type') == 'vendor':
                    handle_shop(player, npc, sound_manager)
                elif npc.get('type') == 'quest_giver':
                    interact_with_quest_giver(npc, player, sound_manager)
                elif npc.get('type') == 'gambler':
                    player.gold = handle_gambler(player.gold, npc)
                else: # Generic NPC
                    print(f"'{random.choice(npc.get('dialogues', ['...']))}'")
                npc['talked_to'] = True
            else:
                print("There is no one to talk to.")
            continue
        elif verb == "answer":
            if current_room.puzzle and current_room.puzzle['type'] == 'riddle' and not current_room.puzzle.get('solved', False):
                guess = " ".join(parts[1:])
                if guess.lower() == current_room.puzzle['answer'].lower():
                    print("Correct! The puzzle is solved.")
                    current_room.puzzle['solved'] = True
                    process_puzzle_rewards(current_room.puzzle, player, current_room)
                else:
                    print("That is not the correct answer.")
            else:
                print("There is no riddle to answer here.")
            continue
        elif verb == "pull":
            # Simplified puzzle logic
            if current_room.puzzle and not current_room.puzzle.get('solved', False):
                print("You pull the lever. A grinding noise is heard.")
                current_room.puzzle['solved'] = True
                process_puzzle_rewards(current_room.puzzle, player, current_room)
            else:
                print("There's nothing to pull.")
            continue
        elif verb == "press":
            if current_room.puzzle and current_room.puzzle['type'] == 'pressure_plate' and not current_room.puzzle.get('solved', False):
                if current_room.item:
                    print(f"You press the {current_room.item['name']} onto the pressure plate.")
                    current_room.puzzle['solved'] = True
                    process_puzzle_rewards(current_room.puzzle, player, current_room)
                else:
                    print("You try to press the plate, but nothing happens. It needs weight.")
            else:
                print("There's nothing to press here.")
            continue
        elif verb == "give":
            # Simplified puzzle logic
            if current_room.puzzle and not current_room.puzzle.get('solved', False):
                print("You give the item. The puzzle seems to react.")
                current_room.puzzle['solved'] = True
                process_puzzle_rewards(current_room.puzzle, player, current_room)
            else:
                print("There's nothing to give an item to.")
            continue

        # --- Crafting ---
        elif verb == "craft":
            print("Crafting is not yet implemented in this version.")
            continue

        # --- Easter Egg/Debug Commands ---
        elif verb == "ohgod":
            print("A divine hand reaches down and blesses you.")
            player.hp = player.max_hp
            player.gold += 1000
            continue
        elif verb == "ohno":
            print("A malevolent force curses you.")
            player.hp = 1
            continue
        elif verb == "ohinn":
            print("A magical sign for an inn appears before you.")
            handle_inn(player, sound_manager)
            continue
        elif verb == "ohitems":
            print("A treasure chest materializes out of thin air!")
            for _ in range(3):
                item_def = get_item_by_name(random.choice([item['name'] for item in ALL_ITEMS if item.get('type') not in ['winning_item', 'key']]))
                if item_def:
                    if len(player.inventory) < player.current_max_inventory_slots:
                        player.inventory.append(copy.deepcopy(item_def))
                        print(f"You found {add_article(item_def['name'])}!")
            continue

        else:
            print("I don't understand that command. Type 'help' for a list of commands.")
            continue


# --- Main Game Execution ---
def main():
    """The main function to run the game."""
    global DEBUG
    if "debug" in sys.argv or "/debug" in sys.argv:
        DEBUG = True

    if DEBUG:
        debug.initialize_debug_log(True)

    meta_progress = load_meta_progress()
    while True: # This loop keeps the main menu active
        print(MAIN_SCREEN_TEXT)
        main_menu_choice = input("Enter your choice: ").strip()

        if main_menu_choice == '1':
            start_new_game(meta_progress, seed=time.time())

        elif main_menu_choice == '2':
            player, world = load_game()
            if player and world:
                game_loop(player, world, sound_manager)

        elif main_menu_choice == '3':
            today = datetime.now().strftime('%Y-%m-%d')
            start_new_game(meta_progress, seed=today, is_daily_challenge=True)

        elif main_menu_choice == '4':
            seed = input("Enter the seed for your run: ").strip()
            if not seed:
                print("Seed cannot be empty.")
                continue
            start_new_game(meta_progress, seed=seed)

        elif main_menu_choice == '5':
            handle_adventurers_guild(meta_progress)
            continue

        elif main_menu_choice == '6':
            print(CREDITS_TEXT)
            input("Press Enter to continue...")
            continue

        elif main_menu_choice == '7':
            print("Thanks for playing!")
            if DEBUG: # Wrapped debug calls
                debug.close_debug_log() # Close log before final exit from main menu
            break # Exit the main menu loop, ending the program

def set_seed(seed):
    """Sets the seed for the random number generator."""
    random.seed(seed)

def handle_adventurers_guild(meta_progress):
    """Handles the Adventurer's Guild hub."""
    while True:
        print("\n--- Adventurer's Guild ---")
        print(f"You have {meta_progress['soul_shards']} Soul Shards.")

        # HP Upgrade
        hp_upgrade_level = meta_progress['upgrades'].get('max_hp', 0)
        hp_upgrade_cost = 50 * (hp_upgrade_level + 1)
        print(f"\n1. Upgrade Max HP (+5 HP per level)")
        print(f"   Current Level: {hp_upgrade_level}")
        print(f"   Next Level Cost: {hp_upgrade_cost} Soul Shards")

        print("\nb. Back to main menu")

        choice = input("Enter your choice: ").lower().strip()

        if choice == '1':
            if meta_progress['soul_shards'] >= hp_upgrade_cost:
                meta_progress['soul_shards'] -= hp_upgrade_cost
                meta_progress['upgrades']['max_hp'] += 1
                save_meta_progress(meta_progress)
                print(f"You have successfully upgraded your Max HP. Current level: {meta_progress['upgrades']['max_hp']}")
            else:
                print("You don't have enough Soul Shards for this upgrade.")
            input("Press Enter to continue...")
        elif choice == 'b':
            break
        else:
            print("Invalid choice. Please try again.")

def start_new_game(meta_progress, seed, is_daily_challenge=False):
    """Sets up and runs a new game, handling all pre-game and post-game logic."""
    if is_daily_challenge:
        print(f"Starting Daily Challenge for {seed}...")
        player_name_prompt = "Enter your adventurer's name for the leaderboard: "
    else:
        print("Starting a new adventure...")
        player_name_prompt = "Enter your adventurer's name: "

    set_seed(seed)

    player_name = input(player_name_prompt).strip()
    if not player_name:
        player_name = "Adventurer"

    # Class selection
    character_classes = GAME_DATA.get('character_classes', {})
    class_choices = list(character_classes.keys())
    print("\nChoose your class:")
    for i, class_name in enumerate(class_choices):
        print(f"{i+1}. {class_name} - {character_classes[class_name]['description']}")
    class_choice_index = -1
    while class_choice_index not in range(len(class_choices)):
        try:
            class_choice_input = input(f"Enter the number of your chosen class (1-{len(class_choices)}): ")
            class_choice_index = int(class_choice_input) - 1
            if class_choice_index not in range(len(class_choices)):
                print("Invalid choice. Please select a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    player_class_name = class_choices[class_choice_index]
    class_data = character_classes[player_class_name]
    print(f"You have chosen the path of the {player_class_name}.")

    # Create Player and World objects
    player = Player(player_name, player_class_name, class_data)
    world = World(player)

    # Set initial position from dungeon
    if world.current_dungeon.start_pos:
        player.x, player.y = world.current_dungeon.start_pos
    else:
        # Fallback if start_pos is not set
        player.x, player.y = 2, 2

    # Start the game loop
    game_result, monsters_defeated, rooms_travelled = game_loop(player, world, sound_manager, seed=seed if is_daily_challenge else None)

    # Post-game logic...
    initial_rooms_travelled = 1
    monsters_defeated_this_run = monsters_defeated
    score = (rooms_travelled - initial_rooms_travelled) * 100 + monsters_defeated_this_run * 50
    shards_earned = (rooms_travelled - initial_rooms_travelled) + (monsters_defeated_this_run * 5)
    if shards_earned > 0:
        print(f"\nYou earned {shards_earned} Soul Shards for your efforts.")
        meta_progress['soul_shards'] += shards_earned
        save_meta_progress(meta_progress)

    if is_daily_challenge:
        leaderboard = {}
        try:
            with open('leaderboard.json', 'r') as f:
                leaderboard = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            leaderboard = {}

        today = datetime.now().strftime('%Y-%m-%d')
        if today not in leaderboard:
            leaderboard[today] = []

        leaderboard[today].append({"name": player_name, "score": score})
        leaderboard[today] = sorted(leaderboard[today], key=lambda x: x['score'], reverse=True)

        with open('leaderboard.json', 'w') as f:
            json.dump(leaderboard, f, indent=4)

        print("\n--- Daily Challenge Leaderboard ---")
        for i, entry in enumerate(leaderboard[today]):
            print(f"{i+1}. {entry['name']} - {entry['score']}")
        input("\nPress Enter to continue...")

    return game_result

# --- Main Game Execution ---

def main():
    """The main function to run the game."""
    global DEBUG
    if "debug" in sys.argv or "/debug" in sys.argv:
        DEBUG = True

    if DEBUG:
        debug.initialize_debug_log(True)

    meta_progress = load_meta_progress()
    while True: # This loop keeps the main menu active
        monsters_defeated_this_run = 0
        print(MAIN_SCREEN_TEXT)
        main_menu_choice = input("Enter your choice: ").strip()

        if main_menu_choice == '1':
            start_new_game(meta_progress, seed=time.time())

        elif main_menu_choice == '2':
            # Load Game
            loaded_hp, loaded_max_hp, loaded_inventory, loaded_room, loaded_max_slots, loaded_gold, loaded_shield, loaded_armor, loaded_cloak, \
            loaded_attack_power, loaded_attack_bonus, loaded_attack_variance, loaded_crit_chance, loaded_crit_multiplier, loaded_equipped_weapon, \
            loaded_xp, loaded_level, loaded_xp_to_next_level, loaded_player_quests, loaded_player_reputation, loaded_player_name, loaded_rooms_travelled, loaded_player_keychain, loaded_misc_items, loaded_player_effects, loaded_room_history, loaded_direction_history, loaded_stash, loaded_player_class, loaded_player_skill_points, loaded_player_unlocked_skills, loaded_equipped_helmet, has_hideout_key = load_game()

            print("=" * 40)
            if loaded_hp is not None:
                initial_rooms_travelled = loaded_rooms_travelled
                monsters_defeated_this_run = 0
                # Assign loaded values to game variables
                player_hp = loaded_hp
                max_hp = loaded_max_hp
                player_inventory = loaded_inventory
                current_room = loaded_room
                current_max_inventory_slots = loaded_max_slots
                player_gold = loaded_gold
                player_shield_value = loaded_shield
                equipped_armor_value = loaded_armor
                equipped_cloak = loaded_cloak # NEW: Assign loaded equipped_cloak
                player_attack_power = loaded_attack_power
                player_attack_bonus = loaded_attack_bonus # NEW: Assign loaded attack bonus
                player_attack_variance = loaded_attack_variance
                player_crit_chance = loaded_crit_chance
                player_crit_multiplier = loaded_crit_multiplier
                equipped_weapon = loaded_equipped_weapon
                player_xp = loaded_xp
                player_level = loaded_level
                xp_to_next_level = loaded_xp_to_next_level
                player_quests = loaded_player_quests
                player_name = loaded_player_name
                rooms_travelled = loaded_rooms_travelled
                player_keychain = loaded_player_keychain # Assign loaded keychain
                equipped_misc_items = loaded_misc_items
                player_effects = loaded_player_effects
                room_history = loaded_room_history
                direction_history = loaded_direction_history
                stash = loaded_stash
                player_class = loaded_player_class
                player_skill_points = loaded_player_skill_points
                player_unlocked_skills = loaded_player_unlocked_skills
                player_reputation = loaded_player_reputation
                equipped_helmet = loaded_equipped_helmet

                # After loading, re-evaluate quest counts for 'fetch_item' quests to ensure consistency
                for q_id, q_data in player_quests.items():
                    quest_def = get_quest_by_id(q_id)
                    if quest_def and q_data['status'] == 'active' and quest_def['type'] == 'fetch_item':
                        # Check both inventory and keychain for quest items
                        q_data['current_count'] = sum(1 for item in player_inventory if item['name'].lower() == quest_def['target_item'].lower()) + \
                                                 sum(1 for item in player_keychain if item['name'].lower() == quest_def['target_item'].lower())

                # After loading, recalculate player_attack_power with the correct additive logic
                current_base_attack_after_load = BASE_PLAYER_ATTACK_POWER + (player_level - 1) * ATTACK_GAIN_PER_LEVEL
                if equipped_weapon:
                    player_attack_power = current_base_attack_after_load + equipped_weapon.get('damage', 0)
                else:
                    player_attack_power = current_base_attack_after_load


                print(f"Welcome back, {player_name}!")
                log_event(f"Game loaded for player: {player_name}.")
                print(f"Your current health: {player_hp}/{max_hp} HP.")
                print(f"Your current gold: {player_gold} gold.")
                print(f"Your Level: {player_level} (XP: {player_xp}/{xp_to_next_level})")
                if player_shield_value:
                    print(f"You are currently protected by a {player_shield_value['name']} offering {player_shield_value.get('defense',0)} defense.")
                else:
                    print("You are currently not protected by a shield.")
                if equipped_armor_value:
                    print(f"You are currently wearing {equipped_armor_value['name']} offering {equipped_armor_value.get('defense',0)} defense.")
                else:
                    print("You are currently not wearing body armor.")
                # NEW: Display equipped cloak on load
                if equipped_cloak:
                    print(f"You are currently wearing a {equipped_cloak['name']} offering {equipped_cloak.get('defense',0)} defense.")
                else:
                    print("You are currently not wearing a cloak.")
                if equipped_weapon:
                    print(f"You are currently wielding {equipped_weapon['name']}.")
                else:
                    print("You are fighting with your fists.")

                # This inner loop also applies to loaded games
                while True:
                    sound_manager.stop_music()
                    if getattr(current_room, 'is_inn', False):
                        sound_manager.play_music('inn_music')
                    else:
                        sound_manager.play_music('ambient_music')

                    # --- NEW: Handle if a loaded room is an inn ---
                    while getattr(current_room, 'is_inn', False):
                        print("You load your game and find yourself in a welcoming inn.")
                        player_hp, max_hp, player_quests, player_inventory, player_gold, player_xp, xp_to_next_level, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_level, player_keychain, stash, has_hideout_key = \
                            handle_inn(player_hp, max_hp, player_quests, player_level, player_inventory, current_max_inventory_slots, player_gold, player_xp, xp_to_next_level, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_keychain, sound_manager, stash, has_hideout_key, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, player_reputation)

                        print("You leave the inn to continue your journey.")
                        current_room = Room(player_level, player_quests) # Generate a new room
                    # --- END NEW ---
                    # MODIFIED: Added equipped_cloak to game_loop parameters
                    game_result, monsters_defeated_this_run, rooms_travelled = game_loop(player_hp, max_hp, player_inventory, current_room, current_max_inventory_slots, player_gold, player_shield_value, equipped_armor_value, equipped_cloak, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, equipped_weapon, player_xp, player_level, xp_to_next_level, player_quests, player_reputation, player_name, rooms_travelled, player_keychain, equipped_misc_items, player_effects, room_history, direction_history, sound_manager, equipped_helmet, player_class, player_skill_points, player_unlocked_skills, monsters_defeated_this_run, stash, has_hideout_key, seed=None)

                    rooms_explored_this_run = rooms_travelled - initial_rooms_travelled
                    shards_earned = rooms_explored_this_run + (monsters_defeated_this_run * 5)
                    if shards_earned > 0:
                        print(f"\nYou earned {shards_earned} Soul Shards for your efforts.")
                        meta_progress['soul_shards'] += shards_earned
                        save_meta_progress(meta_progress)

                    if game_result == 'continue_adventure':
                        current_room = Room(player_level, player_quests) # Generate a new room to continue exploring
                        rooms_travelled += 1
                        player_hp = max_hp
                        print("\nYour adventure in the Infinite Dungeon continues!")
                        print("=" * 40)
                        display_room_content_summary(current_room, rooms_travelled, direction_history, seed=None)
                        continue
                    elif game_result == 'return_to_menu':
                        print("\nReturning to the main menu...")
                        break # Break from the inner loop to go back to the main menu loop
                    elif game_result == 'lose':
                        print("\nWhat would you like to do next?")
                        print("1. Try Again (Restart this adventure from the beginning)")
                        print("2. Return to Main Menu")
                        lose_choice = input("> ").strip()
                        if lose_choice == '1':
                            # For loaded games, 'Try Again' still restarts the *current session* from scratch
                            # This means losing the loaded progress. A more complex system would save checkpoint.
                            # For simplicity, we'll just break
                            # to main menu which means they can then Load again.
                            print("\n" + "=" * 40)
                            print(f"You pick yourself up, {player_name}, and bravely begin anew!")
                            print("=" * 40)
                            break # Break from inner loop, effectively returning to main menu
                        else:
                            break # Break from the inner loop to return to the main menu
                    else: # game_result == 'quit'
                        return


            else:
                continue # No save game found, stay in main menu

        elif main_menu_choice == '3':
            today = datetime.now().strftime('%Y-%m-%d')
            start_new_game(meta_progress, seed=today, is_daily_challenge=True)

        elif main_menu_choice == '4':
            seed = input("Enter the seed for your run: ").strip()
            if not seed:
                print("Seed cannot be empty.")
                continue
            start_new_game(meta_progress, seed=seed)

        elif main_menu_choice == '5':
            handle_adventurers_guild(meta_progress)
            continue

        elif main_menu_choice == '6':
            print(CREDITS_TEXT)
            input("Press Enter to continue...")
            continue

        elif main_menu_choice == '7':
            print("Thanks for playing!")
            if DEBUG: # Wrapped debug calls
                debug.close_debug_log() # Close log before final exit from main menu
            break # Exit the main menu loop, ending the program

# --- Start the game ---
if __name__ == "__main__":
    try:
        main()
    finally:
        if DEBUG: # Ensure log is closed even if an unhandled error occurs, only if DEBUG is True
            debug.close_debug_log()