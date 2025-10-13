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
    player_skill_points += 1

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

    print(f"\n--- {player_class} Skill Tree ---")
    print(f"You have {player_skill_points} skill point(s).")

    skill_tree = class_data['skill_tree']
    for skill in skill_tree:
        status = "Unlocked" if skill['name'] in player_unlocked_skills else "Locked"
        print(f"  - {skill['name']} (Level {skill['level_unlocked']}) - {skill['description']} [{status}]")

    if player_skill_points > 0:
        unlock_choice = input("\nEnter the name of the skill you want to unlock, or 'back': ").strip()
        if unlock_choice.lower() == 'back':
            return player_skill_points, player_unlocked_skills

        skill_to_unlock = None
        for skill in skill_tree:
            if skill['name'].lower() == unlock_choice.lower():
                skill_to_unlock = skill
                break

        if skill_to_unlock:
            if skill_to_unlock['name'] in player_unlocked_skills:
                print("You have already unlocked this skill.")
            elif player_level >= skill_to_unlock['level_unlocked']:
                player_skill_points -= 1
                player_unlocked_skills.append(skill_to_unlock['name'])
                print(f"You have unlocked '{skill_to_unlock['name']}'!")
            else:
                print(f"You need to be level {skill_to_unlock['level_unlocked']} to unlock this skill.")
        else:
            print("Invalid skill name.")
    else:
        input("Press Enter to continue...")

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

def display_room_content_summary(current_room, rooms_travelled, direction_history=None, seed=None):
    """
    Displays the room description and then any relevant hints or status information.
    """
    status_text = f" Room: {rooms_travelled} "
    if seed:
        status_text += f"| Seed: {seed} "
    separator_length = (40 - len(status_text)) // 2
    print("=" * separator_length + status_text + "=" * (40 - separator_length - len(status_text)))

    current_room.show_description(direction_history)

    if current_room.npc and not current_room.npc.get('talked_to', False):
        print("    Hint: Try typing 'talk'")
    if current_room.puzzle and not current_room.puzzle.get('solved', True):
        puzzle_type = current_room.puzzle['type']
        if puzzle_type == 'riddle':
            print("    Hint: Answering the riddle might reveal the way. Try 'answer [your guess]'")
        elif puzzle_type == 'mechanism':
            print("    Hint: You might need to 'pull' a lever here. Try 'pull [lever color/material]'")
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
def handle_combat(player_hp, max_hp, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, monster_data, player_shield_value, equipped_armor_value, equipped_cloak, player_inventory, current_max_inventory_slots, player_gold, equipped_weapon, player_xp, player_level, xp_to_next_level, player_quests, player_keychain, current_room, equipped_misc_items, player_effects, sound_manager, current_defense_bonus, current_crit_chance_bonus, equipped_helmet, player_class, player_unlocked_skills):
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

    # Defense values are now from the equipped item dictionaries
    # MODIFIED: Include equipped_cloak in total_player_defense calculation
    total_player_defense = calculate_total_defense(player_shield_value, equipped_armor_value, equipped_cloak, equipped_helmet) + current_defense_bonus

    for item in [equipped_armor_value, equipped_cloak, equipped_helmet, player_shield_value]:
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
    print(f"Your HP: {player_hp}/{max_hp} | {monster_name} HP: {monster_current_hp}") # FIXED: Used max_hp here
    if total_player_defense > 0:
        print(f"Your Total Defense: {total_player_defense}")

    while player_hp > 0 and monster_current_hp > 0:
        player_hp, is_player_stunned = apply_and_tick_status_effects(player_status_effects, player_hp)
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
            if equipped_weapon and equipped_weapon.get('cursed') and equipped_weapon.get('curse_effect', {}).get('hp_drain'):
                drain_amount = equipped_weapon['curse_effect']['hp_drain']
                player_hp -= drain_amount
                print(f"Your {equipped_weapon['name']} drains {drain_amount} HP from you!")
                if player_hp <= 0:
                    print("You have been drained of your life force!")
                    break
            base_damage = random.randint(player_attack_power - player_attack_variance, player_attack_power + player_attack_variance)

            is_crit = False
            accuracy = 1.0
            for effect in player_status_effects:
                if effect['name'] == 'Blindness':
                    accuracy += effect['effect']['modifier']

            if random.random() > accuracy:
                print("You miss!")
                damage_dealt = 0
            elif random.random() < (player_crit_chance + current_crit_chance_bonus):
                damage_dealt = int(base_damage * player_crit_multiplier)
                is_crit = True
            else:
                damage_dealt = base_damage

            damage_dealt = max(0, damage_dealt - monster_defense)
            monster_current_hp -= damage_dealt
            if is_crit:
                print(f"You deliver a **CRITICAL HIT** to the {monster_name} for {damage_dealt} damage!")
            else:
                print(f"You strike the {monster_name} for {damage_dealt} damage!")

            if equipped_weapon and 'status_effects' in equipped_weapon:
                for effect in equipped_weapon['status_effects']:
                    if random.random() < effect['chance']:
                        monster_status_effects.append(copy.deepcopy(effect))
                        print(f"The {monster_name} is now {effect['name']}!")

            if equipped_weapon and equipped_weapon.get('enchantment'):
                enchantment_name = equipped_weapon['enchantment']
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
                monster_data = None
                break
        elif verb == "skill":
            if not player_unlocked_skills:
                print("You have not unlocked any skills yet.")
                continue

            print("\nAvailable skills:")
            for skill_name in player_unlocked_skills:
                print(f"  - {skill_name}")

            skill_choice = input("Enter the name of the skill you want to use, or 'back': ").strip()
            if skill_choice.lower() == 'back':
                continue

            chosen_skill = None
            for skill_name in player_unlocked_skills:
                if skill_name.lower() == skill_choice.lower():
                    character_classes = GAME_DATA.get('character_classes', {})
                    class_data = character_classes.get(player_class)
                    for skill_data in class_data['skill_tree']:
                        if skill_data['name'] == skill_name:
                            chosen_skill = skill_data
                            break
                    break

            if chosen_skill:
                effect = chosen_skill['effect']
                if effect['type'] == 'damage_boost':
                    base_damage = random.randint(player_attack_power - player_attack_variance, player_attack_power + player_attack_variance)
                    damage_dealt = int(base_damage * effect['value'])
                    damage_dealt = max(0, damage_dealt - monster_defense)
                    monster_current_hp -= damage_dealt
                    print(f"You use {chosen_skill['name']} and deal {damage_dealt} damage!")
                elif effect['type'] == 'guaranteed_crit':
                    base_damage = random.randint(player_attack_power - player_attack_variance, player_attack_power + player_attack_variance)
                    damage_dealt = int(base_damage * player_crit_multiplier)
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
                    player_hp = min(max_hp, player_hp + healing_amount)
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
                    player_effects.append({"stat": effect['stat'], "modifier": effect['value'], "duration": effect['duration'] + 1, "message": f"You feel the power of {chosen_skill['name']}!"})
                    print(f"You use {chosen_skill['name']} and feel stronger!")
                elif effect['type'] == 'damage_modifier':
                    undead_monsters = ["skeletal warrior", "feral ghoul", "vampire spawn", "lich's apprentice", "ghostly apparition", "specter of despair", "minotaur skeleton"]
                    base_damage = random.randint(player_attack_power - player_attack_variance, player_attack_power + player_attack_variance)
                    damage_dealt = base_damage
                    if monster_name.lower() in [m.lower() for m in undead_monsters]:
                        damage_dealt = int(base_damage * effect['multiplier'])
                        print("Your divine power smites the undead creature!")
                    damage_dealt = max(0, damage_dealt - monster_defense)
                    monster_current_hp -= damage_dealt
                    print(f"You use {chosen_skill['name']} and deal {damage_dealt} damage!")
                elif effect['type'] == 'shield':
                    player_effects.append({"stat": "defense", "modifier": effect['value'], "duration": 1, "message": "An arcane shield surrounds you."})
                    print(f"You summon an Arcane Shield that will absorb up to {effect['value']} damage.")
                elif effect['type'] == 'dodge_buff':
                    player_effects.append({"stat": "dodge_chance", "modifier": effect['value'], "duration": effect['duration'] + 1, "message": "You feel nimble and evasive."})
                    print(f"You use {chosen_skill['name']} and feel much harder to hit.")
                action_taken = True
            else:
                print("Invalid skill name.")
                continue

            if monster_current_hp <= 0:
                print(f"The {monster_name} collapses, defeated!")
                gold_gained = random.randint(gold_drop_range[0], gold_drop_range[1])
                if equipped_helmet and equipped_helmet.get('cursed') and equipped_helmet.get('curse_effect', {}).get('gold_find'):
                    gold_gained = int(gold_gained * equipped_helmet['curse_effect']['gold_find'])
                    print(f"Your {equipped_helmet['name']} doubles the gold dropped!")
                print(f"You gained {gold_gained} gold from defeating the {monster_name}!")

                player_xp += monster_xp_reward
                print(f"You gained {monster_xp_reward} experience points!")

                item_drop_name = monster_data.get('item_drop')
                if item_drop_name:
                    item_def = get_item_by_name(item_drop_name)
                    if item_def:
                        if len(player_inventory) < current_max_inventory_slots:
                            scaled_item = scale_item_for_player_level(item_def, player_level)
                            player_inventory.append(scaled_item)
                            print(f"The monster dropped {add_article(scaled_item['name'])}! It has been added to your inventory.")
                            # NEW: Quick equip prompt
                            if scaled_item.get('type') in ['weapon', 'shield', 'armor', 'equipment']:
                                quick_equip_choice = input(f"Do you want to quick equip the {scaled_item['name']}? (yes/no): ").lower().strip()
                                if quick_equip_choice in ['yes', 'y']:
                                    player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items = \
                                        handle_equip_item(player_inventory[-1], player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items, player_level)
                                    player_attack_power = recalculate_attack_power(player_level, equipped_weapon, equipped_misc_items, player_attack_bonus)
                                    print(f"Your attack power is now {player_attack_power}.")
                        elif current_room.item is None:
                            scaled_item = scale_item_for_player_level(item_def, player_level)
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
                        if len(player_inventory) < current_max_inventory_slots:
                            player_inventory.append(copy.deepcopy(material_to_drop))
                            print(f"The monster dropped a {material_to_drop['name']}!")
                        else:
                            print(f"The monster dropped a {material_to_drop['name']}, but your inventory is full!")

                for q_id, q_data in player_quests.items():
                    quest_def = get_quest_by_id(q_id)
                    if quest_def and q_data['status'] == 'active':
                        if (quest_def['type'] == 'defeat_any_monster') or \
                           (quest_def['type'] == 'defeat_monster' and quest_def['target_monster'].lower() == monster_name.lower()):
                            if q_data['current_count'] < quest_def['target_count']:
                                q_data['current_count'] += 1
                                print(f"Quest Update: Defeated a monster! ({q_data['current_count']}/{quest_def['target_count']}) for '{quest_def['name']}'")
                                if q_data['current_count'] >= quest_def['target_count']:
                                    print(f"QUEST COMPLETE: '{quest_def['name']}'! Return to {quest_def['giver_npc_name']} to claim your reward!")

                player_xp, player_level, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points = \
                    check_for_level_up(player_xp, player_level, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points)

                monster_data = None
                break

        elif verb == "heal":
            # Find the best healing item in the inventory
            best_healing_item = None
            max_heal = 0
            for item in player_inventory:
                if item.get('type') == 'consumable' and item.get('effect_type') == 'heal':
                    heal_amount = item.get('effect_value', 0)
                    if heal_amount > max_heal:
                        max_heal = heal_amount
                        best_healing_item = item

            if best_healing_item:
                original_player_hp = player_hp
                player_hp, max_hp, current_max_inventory_slots, consumed_turn, _ = process_item_use(best_healing_item, player_hp, max_hp, player_inventory, current_max_inventory_slots, in_combat=True)
                action_taken = consumed_turn

                if player_hp <= 0:
                    print(f"You succumb to the effects of {add_article(best_healing_item['name'])}...")
                    break

                if consumed_turn and player_hp != original_player_hp:
                    print(f"Your health is now {player_hp}/{max_hp} HP.")

            else:
                print("You don't have any healing items.")
                continue
        elif verb == "run":
            run_chance = random.random()
            if run_chance > 0.5:
                print("You manage to escape the fight!")
                monster_data = None
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
            for item_dict in player_inventory:
                if item_dict['name'].lower() == item_to_use_name_input:
                    item_found_in_inventory = item_dict
                    break

            if item_found_in_inventory:
                original_player_hp = player_hp
                player_hp, max_hp, current_max_inventory_slots, consumed_turn, stat_changes = process_item_use(item_found_in_inventory, player_hp, max_hp, player_inventory, current_max_inventory_slots, in_combat=True)
                action_taken = consumed_turn
                if 'remove_effect' in stat_changes:
                    effect_to_remove = stat_changes['remove_effect']
                    player_status_effects = [effect for effect in player_status_effects if effect['name'] != effect_to_remove]
                    print(f"The {effect_to_remove} has been cured.")
                if 'add_effect_to_monster' in stat_changes:
                    effect_to_add = stat_changes['add_effect_to_monster']
                    monster_status_effects.append(effect_to_add)
                    print(f"The {monster_name} is now {effect_to_add['name']}!")

                if player_hp <= 0:
                    print(f"You succumb to the effects of {add_article(item_found_in_inventory['name'])}...")
                    break

                if consumed_turn and player_hp != original_player_hp:
                    print(f"Your health is now {player_hp}/{max_hp} HP.")

            else:
                print(f"You don't have {item_to_use_name_input} in your inventory.")

        elif verb.startswith("inv"): # Changed to use .startswith
            # Use debug function for inventory data, but keep regular print for user-facing output
            if DEBUG: # Wrapped debug calls
                debug.debug_player_data(player_inventory, player_keychain, current_max_inventory_slots, player_gold, "Inventory Check")

            if not player_inventory and not player_keychain: # Check keychain too
                print("Your inventory is empty.")
            else:
                print(f"Your Health: {player_hp}/{max_hp} HP.")
                print(f"Your Level: {player_level} (XP: {player_xp}/{xp_to_next_level})")

                # Display regular inventory
                print(f"You are carrying ({len(player_inventory)}/{current_max_inventory_slots}):")
                if player_inventory:
                    for item_dict in player_inventory:
                        display_str = f"    - {add_article(item_dict['name'])}"
                        item_type = item_dict.get('type')
                        if item_type == 'consumable':
                            effect_type = item_dict.get('effect_type')
                            effect_value = item_dict.get('effect_value')
                            if effect_type == 'heal' and isinstance(effect_value, int):
                                display_str += f" (Heals {effect_value} HP)"
                            elif effect_type == 'harm' and isinstance(effect_value, int):
                                display_str += f" (Harms {effect_value} HP)"
                            elif effect_type == 'wake_up':
                                display_str += " (Stimulant)"
                            elif effect_type == 'flavor':
                                display_str += " (Consumable)"
                            elif effect_type == 'cure':
                                display_str += f" (Cures {item_dict.get('effect_value')})"
                            elif effect_type == 'inflict':
                                display_str += f" (Inflicts {item_dict.get('effect_value')})"
                        elif item_type == 'weapon':
                            display_str += f" (Damage: {item_dict.get('damage', '?')})"
                            if equipped_weapon and equipped_weapon['name'].lower() == item_dict['name'].lower():
                                display_str += " (EQUIPPED)"
                        elif item_type == 'armor':
                            # MODIFIED: Check if it's armor or cloak
                            item_subtype = item_dict.get('subtype')
                            if item_subtype == 'body_armor':
                                display_str += f" (Defense: {item_dict.get('defense', '?')})"
                                if equipped_armor_value and equipped_armor_value['name'].lower() == item_dict['name'].lower():
                                    display_str += " (EQUIPPED)"
                            elif item_subtype == 'cloak':
                                display_str += f" (Defense: {item_dict.get('defense', '?')})"
                                if equipped_cloak and equipped_cloak['name'].lower() == item_dict['name'].lower():
                                    display_str += " (EQUIPPED)"
                            else: # fallback for generic 'armor' type without subtype
                                display_str += f" (Defense: {item_dict.get('defense', '?')})"
                                if equipped_armor_value and equipped_armor_value['name'].lower() == item_dict['name'].lower():
                                    display_str += " (EQUIPPED)"
                        elif item_type == 'backpack':
                            display_str += f" (+{item_dict.get('effect_value', '?')} Slots)"
                        elif item_type == 'shield':
                            display_str += f" (Defense: {item_dict.get('defense', '?')})"
                            # FIXED: Compare by name for equipped status
                            if player_shield_value and player_shield_value['name'].lower() == item_dict['name'].lower():
                                display_str += " (EQUIPPED)"
                        elif item_type == 'winning_item':
                            display_str += " (Legendary Artifact!)"
                        elif item_type == 'equipment':
                            display_str += f" (Effect: {item_dict.get('effect_type', 'unknown')})"
                            if item_dict in equipped_misc_items:
                                display_str += " (EQUIPPED)"
                        elif item_dict.get('description'):
                            display_str += f" ({item_dict['description']})"
                        print(display_str)
                else:
                    print("    (Empty)")

                # Display keychain
                print("Your Keychain:")
                if player_keychain:
                    for item_dict in player_keychain:
                        print(f"    - {add_article(item_dict['name'])} (Type: {item_dict.get('key_type', '?')} key)")
                else:
                    print("    (Empty)")

                print(f"Your Gold: {player_gold}")
                print(f"Current Shield Defense: {player_shield_value.get('defense', 0) if player_shield_value else 0}") # Display value from item dict
                print(f"Current Armor Defense: {equipped_armor_value.get('defense', 0) if equipped_armor_value else 0}") # Display value from item dict
                # MODIFIED: Display cloak defense
                print(f"Current Cloak Defense: {equipped_cloak.get('defense', 0) if equipped_cloak else 0}")
                # MODIFIED: Update total defense calculation in display
                print(f"Total Defense: {calculate_total_defense(player_shield_value, equipped_armor_value, equipped_cloak, equipped_helmet)}")
                print(f"Attack Power: {player_attack_power} (+/-{player_attack_variance})")
                print(f"Critical Chance: {player_crit_chance*100:.0f}% (x{player_crit_multiplier:.1f} Damage)")
                if equipped_weapon:
                    print(f"Equipped Weapon: {equipped_weapon['name']} (Damage: {equipped_weapon.get('damage', '?')})")
                else:
                    print("Equipped Weapon: Fists (Damage: 5)")
                continue

        elif verb == "help":
            print("\nAvailable commands:")
            print("    (Press Enter) or attack - Strike the monster.") # Updated help text
            print("    run                   - Attempt to escape the fight (may fail).")
            print("    heal                  - Use the best healing item in your inventory.")
            print("    use [item]            - Use any consumable from your inventory (e.g., 'use healing potion').")
            print("    inventory             - View your current inventory (does not cost a turn).")
            # NEW: Add 'equipped' to combat help
            print("    equipped              - View your currently equipped items (does not cost a turn).")
            print("    help                  - Show this list of combat commands.")
            print("-" * 50)
            continue

        # NEW: Add 'equipped' command to combat
        elif verb == "equipped":
            print("\n--- Currently Equipped Items ---")
            print(f"Weapon: {equipped_weapon['name']} (Damage: {equipped_weapon.get('damage', '?')})" if equipped_weapon else "Weapon: Fists (Damage: 5)")
            print(f"Shield: {player_shield_value['name']} (Defense: {player_shield_value.get('defense', '?')})" if player_shield_value else "Shield: None")
            print(f"Body Armor: {equipped_armor_value['name']} (Defense: {equipped_armor_value.get('defense', '?')})" if equipped_armor_value else "Body Armor: None")
            print(f"Cloak: {equipped_cloak['name']} (Defense: {equipped_cloak.get('defense', '?')})" if equipped_cloak else "Cloak: None")
            print(f"Total Defense: {(player_shield_value.get('defense', 0) if player_shield_value else 0) + (equipped_armor_value.get('defense', 0) if equipped_armor_value else 0) + (equipped_cloak.get('defense', 0) if equipped_cloak else 0)}")
            print("----------------------------------")
            continue


        else:
            print("Invalid combat action. Type 'help' for options.")
            continue

        if action_taken and player_hp > 0 and monster_current_hp > 0:
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

            damage_after_defense = max(0, monster_actual_damage - total_player_defense)
            player_hp -= damage_after_defense

            if monster_is_crit:
                print(f"The {monster_name} lands a **CRITICAL HIT** on you for {monster_actual_damage} damage! Your defense absorbed {monster_actual_damage - damage_after_defense} damage.")
            else:
                print(f"The {monster_name} retaliates, hitting you for {monster_actual_damage} damage! Your defense absorbed {monster_actual_damage - damage_after_defense} damage.")

            if 'status_effects' in monster_data:
                for effect in monster_data['status_effects']:
                    if random.random() < effect['chance']:
                        player_status_effects.append(copy.deepcopy(effect))
                        print(f"You are now {effect['name']}!")

            if player_hp <= 0:
                print(f"The {monster_name} delivers a fatal blow...")
                break

        if player_hp > 0 and monster_current_hp > 0:
            print(f"Your HP: {player_hp}/{max_hp} | {monster_name} HP: {monster_current_hp}")
            if player_status_effects:
                print(f"Your status: {', '.join([effect['name'] for effect in player_status_effects])}")
            if monster_status_effects:
                print(f"{monster_name}'s status: {', '.join([effect['name'] for effect in monster_status_effects])}")

    sound_manager.stop_music()
    sound_manager.play_music('ambient_music')
    # MODIFIED: Added equipped_cloak, equipped_misc_items, and player_attack_bonus to returned values
    return player_hp, max_hp, monster_data, gold_gained, player_xp, player_level, xp_to_next_level, player_quests, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items

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
        player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items = \
            handle_combat(player_hp, max_hp, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, \
                          monster_data, player_shield_value, equipped_armor_value, equipped_cloak, player_inventory, current_max_inventory_slots, \
                          player_gold, equipped_weapon, player_xp, player_level, xp_to_next_level, player_quests, player_keychain, current_room, equipped_misc_items, player_effects, sound_manager, 0, 0, equipped_helmet, player_class, player_unlocked_skills)

        if player_hp <= 0:
            return 'lose', player_hp, max_hp, player_gold, player_xp, player_level, xp_to_next_level, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items, monsters_defeated_in_horde

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
def handle_shop(player_gold, player_inventory, current_max_inventory_slots, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, vendor_data, player_keychain, player_level, sound_manager, equipped_misc_items):
    """
    Manages the shop interaction with a vendor NPC.
    Returns updated player_gold, player_inventory, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, and equipped_misc_items.
    """
    vendor_name = vendor_data['name']
    shop_stock_names = vendor_data.get('shop_stock', [])
    shop_dialogues = vendor_data.get('dialogues', ["What're ya buyin'?", "Come back anytime!"])

    shop_items = []
    for item_name in shop_stock_names:
        item_def = get_item_by_name(item_name.lower())
        if item_def and item_def.get('shop_price') is not None:
            scaled_item = scale_item_for_player_level(item_def, player_level)
            shop_items.append(scaled_item)

    sound_manager.stop_music()
    sound_manager.play_music('vendor_music')
    print(f"\n--- {vendor_name}'s Shop ---")
    print(random.choice(shop_dialogues))

    while True:
        print(f"\nYour Gold: {player_gold}")
        print(f"Your Inventory: ({len(player_inventory)}/{current_max_inventory_slots})")
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
                    elif player_gold >= item_price:
                        if item_to_buy.get('type') == 'key':
                            player_keychain.append(copy.deepcopy(item_to_buy))
                            player_gold -= item_price
                            print(f"You bought {add_article(item_to_buy['name'])} for {item_price} gold! It's added to your keychain.")
                            print(random.choice(shop_dialogues))
                            # --- NEW DEBUG AFTER KEY BUY ---
                            if DEBUG: # Wrapped debug calls
                                debug.debug_key_acquisition(player_keychain[-1], "shop buy")
                            # --- END NEW DEBUG ---
                        elif len(player_inventory) < current_max_inventory_slots:
                            player_gold -= item_price
                            player_inventory.append(copy.deepcopy(item_to_buy))
                            print(f"You bought {add_article(item_to_buy['name'])} for {item_price} gold!")
                            print(random.choice(shop_dialogues))
                        else:
                            print("Your inventory is full! You need to drop an item first.")
                    else:
                        print(f"You don't have enough gold for {add_article(item_to_buy['name'])}.")
                        print(random.choice(shop_dialogues))
                else:
                    print("Invalid item number.")
            else:
                print("Invalid buy command.")

        elif verb == "sell":
            sellable_items_main_inv = []
            sellable_items_keychain = []

            for item_dict in player_inventory:
                # MODIFIED: Ensure winning items cannot be sold
                if item_dict.get('shop_price') is not None and item_dict.get('type') != 'winning_item':
                    sellable_items_main_inv.append(item_dict)

            # --- Populating Sellable Keychain using debug.py ---
            # This function just logs; the actual append logic is below within the 'if' condition
            if DEBUG: # Wrapped debug calls
                debug.debug_keychain_populate(player_keychain, sellable_items_keychain) # Pass player_keychain

            for item_dict in player_keychain: # This loop performs the actual append
                if item_dict.get('shop_price') is not None and item_dict.get('type') != 'winning_item':
                    sellable_items_keychain.append(item_dict)
            # --- END Populating Sellable Keychain ---

            print("\nYour Items to Sell:")
            if not sellable_items_main_inv and not sellable_items_keychain:
                print("    (You have no items that can be sold.)")
            else:
                print("--- From Inventory ---")
                for i, item_dict in enumerate(sellable_items_main_inv):
                    sell_price = int(item_dict['shop_price'] * SELL_PRICE_MULTIPLIER)
                    display_str = f"    {i+1}. {add_article(item_dict['name'])}"
                    if equipped_weapon is item_dict:
                        display_str += " (EQUIPPED)"
                    elif equipped_armor_value is item_dict:
                        display_str += " (EQUIPPED BODY ARMOR)" # MODIFIED: clarify equipped type
                    elif equipped_cloak is item_dict: # NEW: Check for equipped cloak
                        display_str += " (EQUIPPED CLOAK)"
                    elif player_shield_value is item_dict:
                        display_str += " (EQUIPPED SHIELD)" # MODIFIED: clarify equipped type
                    elif item_dict in equipped_misc_items:
                        display_str += " (EQUIPPED)"
                    elif item_dict.get('type') == 'misc' and item_dict.get('shop_price') is not None:
                        display_str += f" ({item_dict.get('description', '')})"
                    print(f"{display_str} - Sells for {sell_price} Gold")

                print("--- From Keychain ---")
                keychain_start_index = len(sellable_items_main_inv)
                for i, item_dict in enumerate(sellable_items_keychain):
                    sell_price = int(item_dict['shop_price'] * SELL_PRICE_MULTIPLIER)
                    display_str = f"    {keychain_start_index + i + 1}. {add_article(item_dict['name'])}"
                    display_str += f" (Type: {item_dict.get('key_type', '?')} key)"
                    print(f"{display_str} - Sells for {sell_price} Gold")


            sell_choice = input("Enter item number to sell, or 'back': ").lower().strip()
            if sell_choice == 'back':
                continue

            if sell_choice.isdigit():
                item_num = int(sell_choice) - 1
                item_to_sell = None

                if 0 <= item_num < len(sellable_items_main_inv):
                    item_to_sell = sellable_items_main_inv[item_num]

                    if equipped_weapon is item_to_sell:
                        equipped_weapon = None
                        print(f"You unequip your {item_to_sell['name']}.")
                    elif equipped_armor_value is item_to_sell:
                        equipped_armor_value = None
                        print(f"You unequip your {item_to_sell['name']}.")
                    elif equipped_cloak is item_to_sell: # NEW: Unequip cloak if selling
                        equipped_cloak = None
                        print(f"You unequip your {item_to_sell['name']}.")
                    elif player_shield_value is item_to_sell:
                        player_shield_value = None
                        print(f"You unequip your {item_to_sell['name']}.")
                    elif item_to_sell in equipped_misc_items:
                        equipped_misc_items.remove(item_to_sell)
                        print(f"You unequip your {item_to_sell['name']}.")

                    player_inventory.remove(item_to_sell)

                elif keychain_start_index <= item_num < (keychain_start_index + len(sellable_items_keychain)):
                    item_to_sell = sellable_items_keychain[item_num - keychain_start_index]
                    player_keychain.remove(item_to_sell)
                else:
                    print("Invalid item number.")
                    continue

                if item_to_sell:
                    sell_price = int(item_to_sell['shop_price'] * SELL_PRICE_MULTIPLIER)
                    player_gold += sell_price
                    print(f"You sold {add_article(item_to_sell['name'])} for {sell_price} gold!")

            else:
                print("Invalid sell command.")

        elif verb == "exit":
            print(random.choice(shop_dialogues))
            sound_manager.stop_music()
            sound_manager.play_music('ambient_music')
            # MODIFIED: Added equipped_cloak and equipped_misc_items to returned values
            return player_gold, player_inventory, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, player_keychain, equipped_misc_items
        else:
            print("Invalid shop command. Type 'buy', 'sell', or 'exit'.")

def handle_hideout(stash, player_inventory, current_max_inventory_slots):
    """
    Manages the player's personal hideout.
    Returns the updated stash and player_inventory.
    """
    print("\n--- Your Personal Hideout ---")
    print("A quiet, personal space. You can stash items here.")

    while True:
        print("\nHideout commands: stash / unstash / leave")
        hideout_command_input = input("Hideout Action> ").lower().strip()
        parts = hideout_command_input.split()

        if not parts:
            continue

        verb = parts[0]

        if verb == "stash":
            item_to_stash_name = " ".join(parts[1:])
            item_to_stash = None
            for item in player_inventory:
                if item['name'].lower() == item_to_stash_name.lower():
                    item_to_stash = item
                    break

            if item_to_stash:
                player_inventory.remove(item_to_stash)
                stash.append(item_to_stash)
                print(f"You stashed the {item_to_stash['name']}.")
            else:
                print("You don't have that item.")
        elif verb == "unstash":
            item_to_unstash_name = " ".join(parts[1:])
            item_to_unstash = None
            for item in stash:
                if item['name'].lower() == item_to_unstash_name.lower():
                    item_to_unstash = item
                    break

            if item_to_unstash:
                if len(player_inventory) < current_max_inventory_slots:
                    stash.remove(item_to_unstash)
                    player_inventory.append(item_to_unstash)
                    print(f"You unstashed the {item_to_unstash['name']}.")
                else:
                    print("Your inventory is full.")
            else:
                print("You don't have that item in your stash.")
        elif verb == "leave":
            print("You leave your hideout.")
            return stash, player_inventory
        else:
            print("Invalid hideout command.")

def handle_inn(player_hp, max_hp, player_quests, player_level, player_inventory, current_max_inventory_slots, player_gold, player_xp, xp_to_next_level, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_keychain, sound_manager, stash, has_hideout_key, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon):
    """
    Manages the inn interaction, allowing the player to rest and talk to quest givers.
    Returns updated player state.
    """
    sound_manager.stop_music()
    sound_manager.play_music('inn_music')
    print("\n--- The Hearth and Home Inn ---")
    print("You find yourself in a cozy, bustling inn. A warm fire crackles in the hearth.")

    while True:
        print(f"\nYour HP: {player_hp}/{max_hp}")
        if has_hideout_key:
            print("Inn commands: rest / talk / enter hideout / leave")
        else:
            print("Inn commands: rest / talk / leave")
        inn_command_input = input("Inn Action> ").lower().strip()
        parts = inn_command_input.split()

        if not parts:
            continue

        verb = parts[0]

        if verb == "rest":
            if player_hp < max_hp:
                player_hp = max_hp
                print("\nYou rest by the fire, feeling your wounds mend and your spirit lift. You are fully healed.")
            else:
                print("\nYou are already at full health and feeling great.")

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
                    player_gold, player_inventory, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, player_keychain, equipped_misc_items = \
                        handle_shop(player_gold, player_inventory, current_max_inventory_slots, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, chosen_npc, player_keychain, player_level, sound_manager, [])
                    if any(item.get('key_type') == 'hideout' for item in player_keychain):
                        has_hideout_key = True
                elif chosen_npc:
                    player_quests, player_reputation, player_inventory, player_gold, player_xp, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_level = \
                        interact_with_quest_giver(chosen_npc, player_quests, player_reputation, player_level, player_inventory, current_max_inventory_slots, player_gold, player_xp, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_keychain, sound_manager)
                else:
                    print(f"You don't see anyone named '{npc_name_to_talk}' here.")

        elif verb == "enter" and "hideout" in parts:
            if has_hideout_key:
                stash, player_inventory = handle_hideout(stash, player_inventory, current_max_inventory_slots)
            else:
                print("You don't have a key to a hideout.")

        elif verb == "leave":
            print("You step out of the inn, back into the dungeon's gloom.")
            sound_manager.stop_music()
            sound_manager.play_music('ambient_music')
            return player_hp, max_hp, player_quests, player_inventory, player_gold, player_xp, xp_to_next_level, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_level, player_keychain, stash, has_hideout_key

        else:
            print("Invalid inn command. Type 'rest', 'talk', or 'leave'.")

    sound_manager.stop_music()
    sound_manager.play_music('ambient_music')
    return player_hp, max_hp, player_quests, player_inventory, player_gold, player_xp, xp_to_next_level, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_level, player_keychain, stash, has_hideout_key


def interact_with_quest_giver(npc, player_quests, player_reputation, player_level, player_inventory, current_max_inventory_slots, player_gold, player_xp, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_keychain, sound_manager):
    """Handles all interaction logic with a quest-giving NPC."""
    print(f"\nYou approach {npc['name']}.")

    # Reputation-based dialogue
    faction_id = npc.get('faction')
    if faction_id and faction_id in player_reputation:
        reputation_level = player_reputation[faction_id]
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
        return player_quests, player_reputation, player_inventory, player_gold, player_xp, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_keychain, player_level

    quest_status = get_player_quest_status(player_quests, npc_quest_id)
    quest_def = get_quest_by_id(npc_quest_id)

    if quest_status == 'not_started' and quest_def:
        if player_level >= quest_def.get('required_level', 1) and (not quest_def.get('prerequisite_quest') or get_player_quest_status(player_quests, quest_def.get('prerequisite_quest')) == 'completed'):
            dialogue = quest_def.get('dialogue_offer', "I have a task for you.").format(target_count=quest_def.get('target_count', 0))
            print(f"{npc['name']}: '{dialogue}'")
            accept = input("Accept quest? (yes/no): ").lower().strip()
            if accept in ['yes', 'y']:
                if quest_def['type'] == 'find_npc':
                    player_quests[npc_quest_id] = {'status': 'active', 'found_npc': False}
                else:
                    player_quests[npc_quest_id] = {'status': 'active', 'current_count': 0}
                print(f"You accept the quest: '{quest_def['name']}'!")
        else:
            print(f"{npc['name']}: '{quest_def.get('dialogue_unavailable', 'I have no task for you.')}'")
    elif quest_status == 'active' and quest_def:
        if quest_def['type'] in ['defeat_any_monster', 'defeat_monster', 'fetch_item']:
            dialogue = quest_def.get('dialogue_active', "How goes the quest?").format(
                current_count=player_quests[npc_quest_id].get('current_count', 0),
                target_count=quest_def.get('target_count', 0)
            )
        else:
            dialogue = quest_def.get('dialogue_active', "How goes the quest?")
        print(f"{npc['name']}: '{dialogue}'")
    elif quest_status == 'complete_ready' and quest_def:
        if quest_def['type'] in ['defeat_any_monster', 'defeat_monster', 'fetch_item']:
            dialogue = quest_def.get('dialogue_complete_ready', "You've done it!").format(
                current_count=player_quests[npc_quest_id].get('current_count', 0),
                target_count=quest_def.get('target_count', 0)
            )
        else:
            dialogue = quest_def.get('dialogue_complete_ready', "You've done it!")
        print(f"{npc['name']}: '{dialogue}'")
        turn_in = input("Turn in quest? (yes/no): ").lower().strip()
        if turn_in in ['yes', 'y']:
            if quest_def['type'] == 'fetch_item' and not has_player_enough_items(player_inventory, quest_def['target_item'], quest_def['target_count']):
                print("You don't have the required items!")
            else:
                if quest_def['type'] == 'fetch_item':
                    remove_items_from_inventory(player_inventory, quest_def['target_item'], quest_def['target_count'])
                    print(f"You hand over {quest_def['target_count']} {quest_def['target_item']}(s).")

                player_gold += quest_def.get('reward_gold', 0)
                player_xp += quest_def.get('reward_xp', 0)
                print(f"Quest complete! You receive {quest_def.get('reward_gold', 0)} gold and {quest_def.get('reward_xp', 0)} XP.")

                reward_item_name = quest_def.get('reward_item')
                if reward_item_name:
                    item_def = get_item_by_name(reward_item_name)
                    if item_def:
                        if len(player_inventory) < current_max_inventory_slots:
                            player_inventory.append(copy.deepcopy(item_def))
                            print(f"You also receive {add_article(item_def['name'])}!")
                        else:
                            print(f"You would have received an item, but your inventory is full!")

                player_quests[npc_quest_id]['status'] = 'completed'

                # Update reputation
                if 'rewards' in quest_def:
                    if 'reputation_gain' in quest_def['rewards']:
                        faction_id = quest_def['rewards']['reputation_gain']['faction']
                        amount = quest_def['rewards']['reputation_gain']['amount']
                        update_reputation(player_reputation, faction_id, amount)
                    if 'reputation_loss' in quest_def['rewards']:
                        faction_id = quest_def['rewards']['reputation_loss']['faction']
                        amount = quest_def['rewards']['reputation_loss']['amount']
                        update_reputation(player_reputation, faction_id, -amount)

                player_xp, player_level, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points = \
                    check_for_level_up(player_xp, player_level, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points)
    elif quest_status == 'completed' and quest_def:
        print(f"{npc['name']}: '{quest_def.get('dialogue_complete_turn_in', 'Thank you for your help.')}'")

    return player_quests, player_reputation, player_inventory, player_gold, player_xp, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_level

# MODIFIED: Added equipped_cloak to parameters and save state
def save_game(player_hp, max_hp, player_inventory, current_room, current_max_inventory_slots, player_gold, player_shield_value, equipped_armor_value, equipped_cloak, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, equipped_weapon, player_xp, player_level, xp_to_next_level, player_quests, player_reputation, player_name, rooms_travelled, player_keychain, equipped_misc_items, player_effects, room_history, direction_history, stash, player_class, player_skill_points, player_unlocked_skills, equipped_helmet, has_hideout_key):
    """Saves the current game state to 'savegame.json'."""
    game_state = {
        'player_hp': player_hp,
        'max_hp': max_hp,
        'player_inventory': player_inventory,
        'current_max_inventory_slots': current_max_inventory_slots,
        'player_gold': player_gold,
        'player_shield_value': player_shield_value, # Now stores item dict or None
        'equipped_armor_value': equipped_armor_value, # Now stores item dict or None
        'equipped_cloak': equipped_cloak, # NEW: Save equipped cloak
        'player_attack_power': player_attack_power,
        'player_attack_bonus': player_attack_bonus, # NEW: Save permanent attack bonus
        'player_attack_variance': player_attack_variance,
        'player_crit_chance': player_crit_chance,
        'player_crit_multiplier': player_crit_multiplier,
        'equipped_weapon': equipped_weapon,
        'player_xp': player_xp,
        'player_level': player_level,
        'xp_to_next_level': xp_to_next_level,
        'player_quests': player_quests,
        'player_reputation': player_reputation,
        'player_name': player_name,
        'rooms_travelled': rooms_travelled,
        'player_keychain': player_keychain, # Added to save state
        'equipped_misc_items': equipped_misc_items,
        'stash': stash,
        'player_effects': player_effects,
        'player_class': player_class,
        'player_skill_points': player_skill_points,
        'player_unlocked_skills': player_unlocked_skills,
        'equipped_helmet': equipped_helmet,
        'has_hideout_key': has_hideout_key,
        'special_event_after_unlock': special_event_after_unlock,
        'room_history_data': [
            {
                'description': room.description,
                'exits': list(room.exits.keys()),
                'locked_exits': room.locked_exits,
                'item': room.item,
                'npc': room.npc,
                'hazard': room.hazard,
                'monster': room.monster,
                'puzzle': room.puzzle,
                'shrine': room.shrine,
                'winning_item_just_spawned': room.winning_item_just_spawned,
                'boss_monster_spawned': room.boss_monster_spawned,
                'awaiting_winning_item_pickup': room.awaiting_winning_item_pickup,
                'is_inn': getattr(room, 'is_inn', False)
            } for room in room_history
        ],
        'direction_history': direction_history,
        'current_room': {
            'description': current_room.description,
            'exits': list(current_room.exits.keys()),
            'locked_exits': current_room.locked_exits,
            'item': current_room.item, # Save the item on the floor
            'npc': current_room.npc,
            'hazard': current_room.hazard,
            'monster': current_room.monster,
            'puzzle': current_room.puzzle,
            'shrine': current_room.shrine,
            'winning_item_just_spawned': current_room.winning_item_just_spawned, # Save this flag
            'boss_monster_spawned': current_room.boss_monster_spawned, # Save this flag
            'awaiting_winning_item_pickup': current_room.awaiting_winning_item_pickup, # Save this flag
            'is_inn': getattr(current_room, 'is_inn', False)
        }
    }
    try:
        with open('savegame.json', 'w') as f:
            json.dump(game_state, f, indent=4)
        print("Game saved successfully!")
    except IOError:
        print("Error: Could not save game. Check file permissions.")
    except TypeError as e:
        print(f"Error: Could not save game due to data type issue: {e}")
        print("Ensure all game state data is JSON serializable.")

# MODIFIED: Added equipped_cloak to returned and loaded state
def load_game():
    """Loads the game state from 'savegame.json' and returns it."""
    global special_event_after_unlock
    try:
        with open('savegame.json', 'r') as f:
            game_state = json.load(f)

        special_event_after_unlock = game_state.get('special_event_after_unlock')

        loaded_room = Room(game_state.get('player_level', 1), game_state.get('player_quests', {}), load_from_save=True)
        loaded_room.description = game_state['current_room']['description']
        loaded_room.exits = {direction: True for direction in game_state['current_room']['exits']}
        loaded_room.locked_exits = game_state['current_room']['locked_exits']
        loaded_room.item = game_state['current_room'].get('item') # Load the item on the floor
        loaded_room.npc = game_state['current_room'].get('npc')
        loaded_room.hazard = game_state['current_room'].get('hazard')
        loaded_room.monster = game_state['current_room'].get('monster')
        loaded_room.puzzle = game_state['current_room'].get('puzzle')
        loaded_room.shrine = game_state['current_room'].get('shrine')
        loaded_room.winning_item_just_spawned = game_state['current_room'].get('winning_item_just_spawned', False) # Load flag
        loaded_room.boss_monster_spawned = game_state['current_room'].get('boss_monster_spawned', False) # Load flag
        loaded_room.awaiting_winning_item_pickup = game_state['current_room'].get('awaiting_winning_item_pickup', False) # Load flag
        loaded_room.is_inn = game_state['current_room'].get('is_inn', False)

        room_history_loaded = []
        player_level_for_room_load = game_state.get('player_level', 1)
        for room_data in game_state.get('room_history_data', []):
            room = Room(player_level_for_room_load, player_quests={}, load_from_save=True)
            room.description = room_data['description']
            room.exits = {direction: True for direction in room_data['exits']}
            room.locked_exits = room_data['locked_exits']
            room.item = room_data.get('item')
            room.npc = room_data.get('npc')
            room.hazard = room_data.get('hazard')
            room.monster = room_data.get('monster')
            room.puzzle = room_data.get('puzzle')
            room.shrine = room_data.get('shrine')
            room.winning_item_just_spawned = room_data.get('winning_item_just_spawned', False)
            room.boss_monster_spawned = room_data.get('boss_monster_spawned', False)
            room.awaiting_winning_item_pickup = room_data.get('awaiting_winning_item_pickup', False)
            room.is_inn = room_data.get('is_inn', False)
            room_history_loaded.append(room)

        direction_history_loaded = game_state.get('direction_history', [])


        print("\nGame loaded successfully!")
        # Correctly load equipped items as dictionaries
        player_shield_value_from_save = game_state.get('player_shield_value')
        equipped_armor_value_from_save = game_state.get('equipped_armor_value')
        equipped_cloak_from_save = game_state.get('equipped_cloak') # NEW: Load equipped cloak
        equipped_weapon_from_save = game_state.get('equipped_weapon')

        # Compatibility for older saves where these might have been integers
        # Attempt to re-fetch the full item dictionary if just a value was saved.
        # Otherwise, assume it was saved as the dictionary or None.
        if isinstance(player_shield_value_from_save, int):
            # This handles old saves where only value was stored. It means the item object is lost.
            # Best we can do is represent it as "no shield equipped" or try to find a matching item.
            # For simplicity, setting to None if it's an int from an old save.
            player_shield_value_loaded = None
            print("Notice: Old save format detected for shield, defaulting to no shield equipped.")
        else:
            player_shield_value_loaded = player_shield_value_from_save

        if isinstance(equipped_armor_value_from_save, int):
            equipped_armor_value_loaded = None
            print("Notice: Old save format detected for armor, defaulting to no armor equipped.")
        else:
            equipped_armor_value_loaded = equipped_armor_value_from_save

        # NEW: Handle old save format for equipped_cloak
        if isinstance(equipped_cloak_from_save, int):
            equipped_cloak_loaded = None
            print("Notice: Old save format detected for cloak, defaulting to no cloak equipped.")
        else:
            equipped_cloak_loaded = equipped_cloak_from_save


        # Deepcopy inventory and keychain to prevent reference issues from save file
        player_inventory_loaded = [copy.deepcopy(item) for item in game_state['player_inventory']]
        player_keychain_loaded = [copy.deepcopy(key) for key in game_state.get('player_keychain', [])]


        return game_state['player_hp'], game_state.get('max_hp', 100), player_inventory_loaded, loaded_room, \
               game_state['current_max_inventory_slots'], game_state['player_gold'], \
               player_shield_value_loaded, equipped_armor_value_loaded, equipped_cloak_loaded, \
               game_state.get('player_attack_power', BASE_PLAYER_ATTACK_POWER), \
               game_state.get('player_attack_bonus', 0), \
               game_state.get('player_attack_variance', BASE_PLAYER_ATTACK_VARIANCE), \
               game_state.get('player_crit_chance', BASE_PLAYER_CRIT_CHANCE), \
               game_state.get('player_crit_multiplier', BASE_PLAYER_CRIT_MULTIPLIER), \
               equipped_weapon_from_save, \
               game_state.get('player_xp', 0), \
               game_state.get('player_level', 1), \
               game_state.get('xp_to_next_level', calculate_xp_for_next_level(game_state.get('player_level', 1))), \
               game_state.get('player_quests', {}), \
               game_state.get('player_reputation', {}), \
               game_state.get('player_name', 'Adventurer'), \
               game_state.get('rooms_travelled', 0), \
               player_keychain_loaded, \
               game_state.get('equipped_misc_items', []), \
               game_state.get('player_effects', []), \
               room_history_loaded, direction_history_loaded, \
               game_state.get('stash', []), \
               game_state.get('player_class', None), \
                game_state.get('player_skill_points', 0), \
                game_state.get('player_unlocked_skills', []), \
                game_state.get('equipped_helmet', None), \
                game_state.get('has_hideout_key', False)

    except FileNotFoundError:
        print("\nNo saved game found. Starting a new adventure.")
        # MODIFIED: Added None for equipped_cloak and player_attack_bonus in return tuple
        return None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
    except json.JSONDecodeError:
        print("\nError: Corrupted save file. Starting a new adventure.")
        # MODIFIED: Added None for equipped_cloak and player_attack_bonus in return tuple
        return None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None


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

class Room:
    """Represents a single, randomly generated room in the dungeon."""
    def __init__(self, player_current_level, player_quests, load_from_save=False, entry_direction=None):
        global special_event_after_unlock
        # --- INITIALIZE ALL ATTRIBUTES ---
        self.description = ""
        self.exits = {}
        self.locked_exits = {}
        self.item = None
        self.npc = None
        self.hazard = None
        self.monster = None
        self.puzzle = None
        self.shrine = None
        self.winning_item_just_spawned = False
        self.boss_monster_spawned = False
        self.awaiting_winning_item_pickup = False
        self.is_inn = False
        self.is_horde_room = False
        self.horde_data = None

        if load_from_save:
            return # Stop here for loaded rooms, attributes will be overwritten

        # --- GENERATE NEW ROOM ---
        if special_event_after_unlock:
            monster_name_to_spawn = special_event_after_unlock.get('monster_name')
            found_monster_def = next((m for m in MONSTERS if m['name'] == monster_name_to_spawn), None)

            if found_monster_def:
                self.monster = dict(found_monster_def)
                self.description = f"You enter a chamber that feels strangely significant. A powerful {self.monster['name']} stands guard here."
                self.exits = {"south": True}  # Default exit to go back
                self.locked_exits = {}
                self.item = None
                self.npc = None
                self.hazard = None
                self.puzzle = None
                self.winning_item_just_spawned = False
                self.boss_monster_spawned = False
                self.awaiting_winning_item_pickup = False
                special_event_after_unlock = None
                return
            else:
                if DEBUG:
                    debug.debug_print(f"Special monster '{monster_name_to_spawn}' not found. Generating normal room.")
                special_event_after_unlock = None

        # --- Inn Generation ---
        if random.random() < INN_SPAWN_CHANCE:
            self.is_inn = True
            return # Prevent other content from spawning

        if random.random() < CRAFTING_STATION_SPAWN_CHANCE:
            crafting_station_type = random.choice(["Altar", "Anvil"])
            self.description = f"You enter a room with a mystical {crafting_station_type}."
            self.exits = {"south": True}
            self.crafting_station = crafting_station_type
            return

        if random.random() < HORDE_SPAWN_CHANCE and HORDES:
            self.is_horde_room = True
            self.horde_data = random.choice(HORDES)
            return

        adj = random.choice(ADJECTIVES)
        room_type = random.choice(ROOM_TYPES)
        detail = random.choice(DETAILS)
        self.description = f"You are in a {adj} {room_type}. You notice {detail}."

        self.exits = {}
        self.locked_exits = {}
        all_possible_directions = ["north", "south", "east", "west"]
        opposites = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}

        # All directions are initially available for random generation
        available_directions_for_random = all_possible_directions[:]

        # If entering from a specific direction, guarantee an exit back.
        if entry_direction and entry_direction in opposites:
            back_direction = opposites[entry_direction]
            self.exits[back_direction] = True
            # This direction is now taken, remove it from random generation pool.
            available_directions_for_random.remove(back_direction)

        # We must have at least one exit. If the back-exit wasn't created, create one now.
        if not self.exits and available_directions_for_random:
            guaranteed_unlocked_direction = random.choice(available_directions_for_random)
            self.exits[guaranteed_unlocked_direction] = True
            available_directions_for_random.remove(guaranteed_unlocked_direction)

        # Now, for the remaining available directions, randomly create more exits.
        for direction in available_directions_for_random:
            rand_roll = random.random()
            if rand_roll < 0.25: # Same probability as before
                self.exits[direction] = True
            elif rand_roll < 0.45: # Same probability as before
                key_type = random.choice(["rusty", "silver", "bone"])
                self.locked_exits[direction] = key_type

        self.item = None # Explicitly None by default
        self.npc = None
        self.hazard = None
        self.monster = None
        self.puzzle = None
        self.shrine = None
        self.winning_item_just_spawned = False # Track if winning item just appeared
        self.boss_monster_spawned = False # Track if boss monster has appeared yet
        self.awaiting_winning_item_pickup = False # Track if player needs to pick up winning item

        content_roll = random.random()

        # Content generation priority (higher up = checked first)
        # 1. Dedicated Vendor Spawn Chance
        if random.random() < VENDOR_SPAWN_CHANCE:
            vendor_npc_def = next((n for n in NPCs if n.get('type') == 'vendor'), None)
            if vendor_npc_def:
                self.npc = dict(vendor_npc_def)
                self.npc['talked_to'] = False
            return

        # 1.25. Shrine Spawn Chance
        if SHRINES and random.random() < SHRINE_SPAWN_CHANCE:
            self.shrine = copy.deepcopy(random.choice(SHRINES))
            self.shrine['used'] = False # Mark as not used
            return # A shrine room should not have other major features

        # 1.5. Puzzle Room Spawn Chance
        if PUZZLES and random.random() < PUZZLE_SPAWN_CHANCE:
            # Ensure item_delivery puzzles don't block exits
            eligible_puzzles = [p for p in PUZZLES if not (p.get('type') == 'item_delivery' and p.get('reward_type') == 'exit')]
            if eligible_puzzles:
                self.puzzle = dict(random.choice(eligible_puzzles))
                self.puzzle['solved'] = False
            return

        # 1.75. Quest Giver NPC Spawn Chance
        if NPCs and player_quests is not None and random.random() < 0.15:
            all_quest_givers = [n for n in NPCs if n.get('type') == 'quest_giver']
            available_quest_givers = []
            for npc in all_quest_givers:
                quest_id = npc.get('current_quest_id')
                if not quest_id:
                    continue

                quest_def = get_quest_by_id(quest_id)
                if not quest_def:
                    continue

                # Check if quest is already completed or active
                quest_status = get_player_quest_status(player_quests, quest_id)
                if quest_status == 'completed' or quest_status == 'active':
                    continue

                # Check for level requirement
                if player_current_level < quest_def.get('required_level', 1):
                    continue

                # Check for prerequisite quest
                prereq_quest_id = quest_def.get('prerequisite_quest')
                if prereq_quest_id:
                    prereq_status = get_player_quest_status(player_quests, prereq_quest_id)
                    if prereq_status != 'completed':
                        continue

                # If all checks pass, the quest giver is available
                available_quest_givers.append(npc)

            if available_quest_givers:
                self.npc = dict(random.choice(available_quest_givers))
                self.npc['talked_to'] = False
                return

        # 2. Winning Item Spawn (level-gated) - Item spawns, boss does NOT, boss spawns on 'get'
        if player_current_level >= WINNING_ITEM_MIN_PLAYER_LEVEL and content_roll < WINNING_ITEM_SPAWN_CHANCE:
            winning_item_candidates = [item for item in ALL_ITEMS if item.get('type') == 'winning_item']
            if winning_item_candidates:
                self.item = random.choice(winning_item_candidates)
                self.winning_item_just_spawned = True # Mark that winning item just spawned
                self.awaiting_winning_item_pickup = True # Player must pick it up before anything else
                # Boss monster is NOT set here, it will be set in the 'get' command handler
                print("\n" + "=" * 40)
                print("A powerful aura emanates from something nearby...")
                print(f"You sense a legendary artifact is close! You see {add_article(self.item['name'])} on the floor.")
                print("=" * 40)
                return # Crucial: prevent other content from spawning if winning item is present

        # 3. Other Room Content (if no primary content was generated)
        else:
            secondary_content_roll = random.random()

            item_spawn_threshold = 0.35
            npc_spawn_threshold = item_spawn_threshold + 0.12
            hazard_spawn_threshold = npc_spawn_threshold + 0.15
            monster_spawn_threshold = hazard_spawn_threshold + 0.20

            if secondary_content_roll < item_spawn_threshold:
                item_spawn_weights_from_json = GAME_DATA.get('item_spawn_weights', {})

                possible_items_with_weights = []

                for item_def in ALL_ITEMS:
                    item_type = item_def.get('type')

                    if item_type == 'winning_item':
                        continue

                    weight = 0
                    if item_type == 'backpack':
                        weight = item_spawn_weights_from_json.get('backpack', 0)
                    elif item_type == 'shield':
                        weight = item_spawn_weights_from_json.get('shield', 0)
                    elif item_type == 'armor': # MODIFIED: Check for subtypes within armor
                        item_subtype = item_def.get('subtype')
                        if item_subtype == 'body_armor':
                            weight = item_spawn_weights_from_json.get('armor_body', 0)
                        elif item_subtype == 'cloak':
                            weight = item_spawn_weights_from_json.get('armor_cloak', 0)
                        else: # Fallback for old armor entries without subtype
                            weight = item_spawn_weights_from_json.get('armor', 0)
                    elif item_type == 'weapon':
                        weight = item_spawn_weights_from_json.get('weapon', 0)
                    elif item_type == 'key':
                        weight = item_spawn_weights_from_json.get('key', 0)
                    elif item_type == 'consumable':
                        if item_def.get('effect_type') == 'heal':
                            weight = item_spawn_weights_from_json.get('consumable_healing', 0)
                        else:
                            weight = item_spawn_weights_from_json.get('consumable_other', 0)
                    elif item_type == 'misc' or item_type == 'equipment':
                                                weight = item_spawn_weights_from_json.get('default', 0)

                    if weight > 0:
                        possible_items_with_weights.append((item_def, weight))

                if possible_items_with_weights:
                    items_to_choose_from = [item_tuple[0] for item_tuple in possible_items_with_weights]
                    weights_for_choices = [item_tuple[1] for item_tuple in possible_items_with_weights]

                    chosen_item = random.choices(items_to_choose_from, weights=weights_for_choices, k=1)[0]
                    self.item = scale_item_for_player_level(chosen_item, player_current_level)

            elif secondary_content_roll < npc_spawn_threshold:
                non_quest_npcs = [n for n in NPCs if n.get('type') != 'vendor' and n.get('type') != 'quest_giver']

                # Filter out NPCs that require a quest the player doesn't have
                eligible_npcs = []
                for npc in non_quest_npcs:
                    required_quest = npc.get('requires_quest')
                    if not required_quest or (required_quest and player_quests.get(required_quest, {}).get('status') == 'active'):
                        eligible_npcs.append(npc)

                if eligible_npcs:
                    self.npc = dict(random.choice(eligible_npcs))
                    self.npc['talked_to'] = False
            elif secondary_content_roll < hazard_spawn_threshold:
                if HAZARDS:
                    self.hazard = random.choice(HAZARDS)
                    if self.hazard.get('hidden'):
                        self.hazard['is_currently_hidden'] = True
                    self.hazard['disarmed'] = False
            elif secondary_content_roll < monster_spawn_threshold:
                if MONSTERS:
                    eligible_monsters = []
                    monster_weights = []

                    for monster_def in MONSTERS:
                        monster_level = monster_def.get('level', 1)
                        level_difference = monster_level - player_current_level

                        if MONSTER_SPAWN_LEVEL_MIN_OFFSET <= level_difference <= MONSTER_SPAWN_LEVEL_MAX_OFFSET:
                            weight_multiplier = MONSTER_LEVEL_WEIGHTS.get(level_difference, 0)
                            if weight_multiplier > 0:
                                eligible_monsters.append(monster_def)
                                monster_weights.append(weight_multiplier)

                    if eligible_monsters:
                        self.monster = dict(random.choices(eligible_monsters, weights=monster_weights, k=1)[0])

    def show_description(self, direction_history=None):
        """Prints the full description of the room."""
        print(self.description)

        if self.item:
            # If it's a winning item and boss hasn't spawned yet, mention the aura
            if self.item['name'] in WINNING_ITEMS and not self.boss_monster_spawned:
                print(f"You see {add_article(self.item['name'])} lying here, emanating a powerful aura.")
            elif self.monster and self.item['name'] not in WINNING_ITEMS: # Regular item guarded by monster
                print(f"You see {add_article(self.item['name'])} on the floor, but it's guarded!")
            elif not self.monster and self.item['name'] not in WINNING_ITEMS: # Regular item, no monster
                print(f"You see {add_article(self.item['name'])} on the floor.")

        if self.npc:
            # Safely get NPC description using .get() with a default value
            npc_description = self.npc.get('description', 'stands silently.')
            print(f"You spot {self.npc['name']}: {npc_description}")

        if self.shrine:
            print(f"Here, you find a {self.shrine['name']}. {self.shrine['description']}")
            if not self.shrine.get('used'):
                print(f"    Hint: Try to '{self.shrine['interaction_verb']}'")
            else:
                print("It seems to be dormant now.")

        if self.puzzle and not self.puzzle.get('solved', True):
            print(f"A puzzle here demands your attention: {self.puzzle['description']}")

        if self.hazard and not self.hazard.get('is_currently_hidden', False):
            print(f"Watch out! There's {self.hazard['name']} here!")
        elif self.hazard and self.hazard.get('is_currently_hidden', False):
            print("You feel a sense of danger, but you're not sure from where.")

        # Only display monster if it's not a boss guardian waiting to spawn, or if it IS a boss guardian and has spawned.
        if self.monster and not self.monster.get('is_boss_guardian', False):
            print(f"A {self.monster['name']} {self.monster['description']}")
        elif self.monster and self.monster.get('is_boss_guardian', False) and self.boss_monster_spawned:
            print(f"A fierce {self.monster['name']} stands here!")


        opposites = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
        back_direction = None
        if direction_history:
            last_direction = direction_history[-1]
            back_direction = opposites.get(last_direction)

        exits_available_list = []
        for direction in self.exits.keys():
            if direction == back_direction:
                exits_available_list.append(f"{direction} (Previous Room)")
            else:
                exits_available_list.append(direction)

        locked_exit_descriptions = []
        for direction, key_type in self.locked_exits.items():
            locked_exit_descriptions.append(f"{direction} (locked, requires {key_type} key)")

        if exits_available_list or locked_exit_descriptions:
            all_exits_display = ", ".join(exits_available_list + locked_exit_descriptions)
            print(f"Exits: {all_exits_display}")
        else:
            print("There are no exits from this room. You are trapped!")

# --- Game Loop Function ---
# MODIFIED: Added equipped_cloak to parameters
def game_loop(player_hp, max_hp, player_inventory, current_room, current_max_inventory_slots, player_gold, player_shield_value, equipped_armor_value, equipped_cloak, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, equipped_weapon, player_xp, player_level, xp_to_next_level, player_quests, player_reputation, player_name, rooms_travelled, player_keychain, equipped_misc_items, player_effects, room_history,direction_history, sound_manager, equipped_helmet, player_class, player_skill_points, player_unlocked_skills, monsters_defeated_this_run, stash, has_hideout_key, seed=None):
    """
    This function contains the main game loop logic for active gameplay.
    It returns a string indicating the game outcome: 'continue_adventure', 'lose', 'quit', or 'return_to_menu'.
    """
    global DEBUG, special_event_after_unlock
    current_defense_bonus = 0
    current_crit_chance_bonus = 0.0
    # Helper function to process puzzle rewards
    def process_puzzle_rewards(puzzle, player_inventory, current_max_inventory_slots, player_keychain, player_xp, player_gold, player_level, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points):
        rewards_data = puzzle.get('rewards', {})
        reward_given = False

        # Handle XP and Gold Rewards
        if 'xp_gold' in rewards_data:
            reward_given = True
            xp_reward = rewards_data['xp_gold'].get('xp', 0)
            gold_reward = rewards_data['xp_gold'].get('gold', 0)
            player_xp += xp_reward
            player_gold += gold_reward
            print(f"You gained {xp_reward} XP and {gold_reward} gold!")
            player_xp, player_level, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points =                 check_for_level_up(player_xp, player_level, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points)

        # Handle Item Rewards
        if 'items' in rewards_data:
            for item_reward in rewards_data['items']:
                item_name = item_reward['name']
                chance = item_reward.get('chance', 100) # Default to 100% chance if not specified
                if random.randint(1, 100) <= chance:
                    item_def = get_item_by_name(item_name)
                    if item_def:
                        reward_given = True
                        if item_def.get('type') == 'key':
                            player_keychain.append(copy.deepcopy(item_def))
                            print(f"A hidden mechanism whirs, and {add_article(item_def['name'])} appears, added to your keychain!")
                        elif len(player_inventory) < current_max_inventory_slots:
                            scaled_item = scale_item_for_player_level(item_def, player_level)
                            player_inventory.append(scaled_item)
                            print(f"A hidden compartment opens, revealing {add_article(scaled_item['name'])}!")
                        else:
                            scaled_item = scale_item_for_player_level(item_def, player_level)
                            print(f"A hidden compartment opens, revealing {add_article(scaled_item['name'])}, but your inventory is full! It remains here.")
                            current_room.item = scaled_item
                    else:
                        print(f"Warning: Reward item '{item_name}' not found in game data.")

        # Handle Old Reward Format
        elif 'reward_type' in puzzle and 'reward_data' in puzzle:
            reward_type = puzzle['reward_type']
            reward_data = puzzle['reward_data']
            if reward_type == 'item':
                reward_given = True
                item_def = get_item_by_name(reward_data)
                if item_def:
                    if item_def.get('type') == 'key':
                        player_keychain.append(copy.deepcopy(item_def))
                        print(f"A hidden mechanism whirs, and {add_article(item_def['name'])} appears, added to your keychain!")
                    elif len(player_inventory) < current_max_inventory_slots:
                        scaled_item = scale_item_for_player_level(item_def, player_level)
                        player_inventory.append(scaled_item)
                        print(f"A hidden compartment opens, revealing {add_article(scaled_item['name'])}!")
                    else:
                        scaled_item = scale_item_for_player_level(item_def, player_level)
                        print(f"A hidden compartment opens, revealing {add_article(scaled_item['name'])}, but your inventory is full! It remains here.")
                        current_room.item = scaled_item
                else:
                    print(f"Warning: Reward item '{reward_data}' not found in game data.")
        
        # Handle Exit Reward as a special case if no other rewards were given
        if not reward_given and 'exit' in rewards_data:
            direction_to_open = rewards_data['exit'].get('direction')
            if direction_to_open and direction_to_open not in current_room.exits:
                current_room.exits[direction_to_open] = True
                if direction_to_open in current_room.locked_exits:
                    del current_room.locked_exits[direction_to_open]
                    print(f"The previously locked {direction_to_open} exit is now open!")
                else:
                    print(f"A new path to the {direction_to_open} has opened!")
            else:
                print(f"The path to the {direction_to_open} was already open.")

        return player_inventory, current_max_inventory_slots, player_keychain, player_xp, player_gold, player_level, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points

    display_room_content_summary(current_room, rooms_travelled, direction_history, seed)

    if hasattr(current_room, 'crafting_station'):
        print(f"You are in a room with a {current_room.crafting_station}.")
        print("You can use the 'craft' or 'enchant' commands here.")

    # --- Initial player state dump for the session ---
    if DEBUG: # Wrapped debug calls
        debug.debug_player_data(player_inventory, player_keychain, current_max_inventory_slots, player_gold, "Player State at Room Entry")
    # --- End initial player state dump ---


    if current_room.is_horde_room:
        game_result, player_hp, max_hp, player_gold, player_xp, player_level, xp_to_next_level, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items, monsters_defeated_in_horde, player_skill_points = \
            handle_horde_combat(player_hp, max_hp, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, player_shield_value, equipped_armor_value, equipped_cloak, player_inventory, current_max_inventory_slots, player_gold, equipped_weapon, player_xp, player_level, xp_to_next_level, player_quests, player_keychain, current_room, equipped_misc_items, player_effects, sound_manager, equipped_helmet, player_class, player_unlocked_skills, player_skill_points)
        monsters_defeated_this_run += monsters_defeated_in_horde
        if game_result == 'lose':
            return 'lose', monsters_defeated_this_run, rooms_travelled
    # Handle immediate hazard upon entering room
    if current_room.hazard and not current_room.hazard.get('is_currently_hidden', False):
        print(current_room.hazard['effect_message'].format(damage=current_room.hazard['damage']))
        # MODIFIED: Include equipped_cloak in total defense calculation for hazards
        total_initial_defense = (player_shield_value.get('defense', 0) if player_shield_value else 0) + \
                               (equipped_armor_value.get('defense', 0) if equipped_armor_value else 0) + \
                               (equipped_cloak.get('defense', 0) if equipped_cloak else 0)
        actual_hazard_damage = max(0, current_room.hazard['damage'] - total_initial_defense)
        player_hp -= actual_hazard_damage
        print(f"Your health is now {player_hp}/{max_hp} HP.")
        if total_initial_defense > 0:
            print(f"Your total defense absorbed {current_room.hazard['damage'] - actual_hazard_damage} damage.")
        if player_hp <= 0:
            print("\n" + "=" * 40)
            print("Your health has fallen to zero! You collapse.")
            print("        G A M E    O V E R            ")
            print("=" * 40)
            if DEBUG: # Wrapped debug calls
                debug.close_debug_log() # Close log on game over
            return 'lose', monsters_defeated_this_run, rooms_travelled # Game over, return 'lose'

    # Winning item pre-combat interaction
    # If a winning item spawned AND the boss hasn't spawned yet, prompt player to pick it up.
    if current_room.item and current_room.item['name'] in WINNING_ITEMS and not current_room.boss_monster_spawned:
        print(f"\nBefore you can act, you feel an immense power radiating from the {current_room.item['name']}!")
        if len(player_inventory) >= current_max_inventory_slots:
            print(f"Your inventory is full! You cannot pick up the {current_room.item['name']}.")
            print("You must drop an item to make space. The guardian's presence is unsettling...")
        else:
            print("You must pick it up to proceed. (Type 'get item')")
        # Set awaiting_winning_item_pickup flag to indicate this state
        current_room.awaiting_winning_item_pickup = True
    else:
        current_room.awaiting_winning_item_pickup = False # Reset flag if not in this state

    # Handle regular monster combat (if present and not a winning item guardian)
    if current_room.monster and not current_room.monster.get('is_boss_guardian', False): # For regular monsters
        monster_was_defeated = current_room.monster is not None
        player_hp, max_hp, current_room.monster, gold_gained, player_xp, player_level, xp_to_next_level, player_quests, \
                player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items = \
            handle_combat(player_hp, max_hp, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, \
                          current_room.monster, player_shield_value, equipped_armor_value, equipped_cloak, player_inventory, current_max_inventory_slots, \
                                  player_gold, equipped_weapon, player_xp, player_level, xp_to_next_level, player_quests, player_keychain, current_room, equipped_misc_items, player_effects, sound_manager, current_defense_bonus, current_crit_chance_bonus, equipped_helmet, player_class, player_unlocked_skills)
        player_gold += gold_gained
        if player_hp <= 0:
            print("\n" + "=" * 40)
            print("Your health has fallen to zero! You collapse.")
            print("        G A M E    O V E R            ")
            print("=" * 40)
            if DEBUG: # Wrapped debug calls
                debug.close_debug_log() # Close log on game over
            return 'lose', monsters_defeated_this_run, rooms_travelled
        if monster_was_defeated and current_room.monster is None:
            current_room.monster = None
            monsters_defeated_this_run += 1
            print(f"\nThe monster is defeated. The room is now safe.")
            display_room_content_summary(current_room, rooms_travelled)


    while True:
        # --- BUFF AND CURSE SYSTEM ---
        # A turn passes each time the player enters a command.
        # Apply effects and get modifiers for this turn.
        effect_modifiers = apply_and_tick_effects(player_effects)

        # Recalculate base stats + permanent bonuses
        base_attack_power = recalculate_attack_power(player_level, equipped_weapon, equipped_misc_items, player_attack_bonus)

        # Apply temporary modifiers from effects to get final stats for this turn
        current_attack_power = base_attack_power + effect_modifiers.get('attack_power', 0)
        current_defense_bonus = effect_modifiers.get('defense', 0)
        current_crit_chance_bonus = effect_modifiers.get('crit_chance', 0.0)

        # Update the player's power for this turn (used for display and combat)
        player_attack_power = current_attack_power

        command_input = input("> ").lower().strip()
        parts = command_input.split()

        verb = ""
        direction = None # Initialize direction variable

        # Determine the verb and potential direction
        if not parts:
            pass # Empty input, will be caught by the "else" for invalid command.
                     # If we wanted to add a default like "look" for empty general input, it would go here.
        elif parts[0] in ["north", "south", "east", "west"]: # NEW: Allow just direction
            verb = parts[0] # Direction IS the verb
            direction = parts[0]
        else:
            verb = parts[0] # Regular command
            if len(parts) > 1 and parts[0] == "go" and parts[1] in ["north", "south", "east", "west"]:
                direction = parts[1] # "go [direction]"
            elif verb in ["go"] and len(parts) == 1:
                print("Where do you want to go? (e.g., 'go north' or just 'north')")
                continue

        # --- Process Commands ---

        if verb == "/debug":
            DEBUG = not DEBUG
            if DEBUG:
                debug.initialize_debug_log(True)
                print("Debug mode ON.")
            else:
                debug.close_debug_log()
                print("Debug mode OFF.")
            continue

        if verb == "quit":
            print("Thanks for playing!")
            if DEBUG: # Wrapped debug calls
                debug.close_debug_log() # Close log before quitting
            return 'quit', monsters_defeated_this_run, rooms_travelled

        elif verb == "help":
            print("\nAvailable commands:")
            print("    go [north, south, east, west] - Move to a new room.")
            print("    [north, south, east, west]    - Move directly (e.g., 'north').") # NEW: Updated help text
            print("    get [item name OR 'item']     - Pick up an item (e.g., 'get rusty key' or 'get item').")
            print("    drop [item name]              - Drop an item from your inventory or keychain.")
            print("    use [item name]               - Use any consumable from your inventory (e.g., 'use healing potion').")
            print("    equip/quip [item name]        - Equip a weapon, shield, or armor.")
            print("    unequip [item name]           - Unequip an item.")
            # NEW: Add 'equipped' to general help
            print("    equipped                      - View your currently equipped items.")
            print("    misc                          - View your currently equipped miscellaneous items.")
            print("    attack                        - Attack a monster in the room.")
            print("    skill                         - Open the skill tree to view and unlock skills.")
            print("    combine                       - Combine items (e.g., 'combine healing potion').")
            print("    talk [person]                 - Attempt to talk to an NPC. In an inn, lists people to talk to.")
            print("    rest                          - Rest at an inn to restore health.")
            print("    quests                        - View your active quests.")
            print("    answer [your guess]           - Answer a riddle in a puzzle room.")
            print("    pull [lever name/color]       - Interact with a lever in a puzzle room.")
            print("    give [item] to [target]       - Give an item to a statue/NPC in a puzzle room.")
            print("    unlock [direction] with [key name] - Unlock a locked exit.")
            print("    look                          - See the room description again.")
            print("    search                        - Search the room for hidden traps.")
            print("    disarm [trap name]            - Attempt to disarm a detected trap.")
            print("    inventory                     - Check your items and inventory space.")
            print("    save                          - Save your current game progress.")
            print("    ohinn                         - Teleport to a mystical inn.")
            print("    credits                       - Show game credits.")
            print("    quit                          - Exit the game.")
            print("-" * 50)

        elif verb == "skill":
            player_skill_points, player_unlocked_skills = handle_skill_tree(player_class, player_level, player_skill_points, player_unlocked_skills)

        elif verb == "craft":
            if hasattr(current_room, 'crafting_station'):
                crafting_recipes = GAME_DATA.get('crafting_recipes', [])
                if not crafting_recipes:
                    print("There are no crafting recipes available.")
                else:
                    print("Available crafting recipes:")
                    for i, recipe in enumerate(crafting_recipes):
                        print(f"  {i+1}. {recipe['name']}")

                    choice = input("Enter the number of the item you want to craft, or 'back': ").strip()
                    if choice.lower() == 'back':
                        continue

                    try:
                        recipe_index = int(choice) - 1
                        if 0 <= recipe_index < len(crafting_recipes):
                            selected_recipe = crafting_recipes[recipe_index]
                            can_craft = True
                            for ingredient in selected_recipe['ingredients']:
                                if not has_player_enough_items(player_inventory, ingredient['name'], ingredient['quantity']):
                                    can_craft = False
                                    print(f"You don't have enough {ingredient['name']}.")
                                    break

                            if can_craft:
                                for ingredient in selected_recipe['ingredients']:
                                    remove_items_from_inventory(player_inventory, ingredient['name'], ingredient['quantity'])

                                result_item = get_item_by_name(selected_recipe['result'])
                                if result_item:
                                    player_inventory.append(copy.deepcopy(result_item))
                                    print(f"You successfully crafted a {result_item['name']}!")
                                else:
                                    print("Crafting failed: result item not found.")
                        else:
                            print("Invalid recipe number.")
                    except ValueError:
                        print("Invalid input.")
            else:
                print("You can't craft items here.")

        elif verb == "enchant":
            if hasattr(current_room, 'crafting_station'):
                enchantments = GAME_DATA.get('enchantments', [])
                if not enchantments:
                    print("There are no enchantments available.")
                else:
                    print("Available enchantments:")
                    for i, enchantment in enumerate(enchantments):
                        print(f"  {i+1}. {enchantment['name']}")

                    choice = input("Enter the number of the enchantment you want to apply, or 'back': ").strip()
                    if choice.lower() == 'back':
                        continue

                    try:
                        enchantment_index = int(choice) - 1
                        if 0 <= enchantment_index < len(enchantments):
                            selected_enchantment = enchantments[enchantment_index]

                            item_to_enchant_name = input("Enter the name of the item to enchant: ").strip()
                            item_to_enchant = None
                            for item in player_inventory:
                                if item['name'].lower() == item_to_enchant_name.lower():
                                    item_to_enchant = item
                                    break

                            if item_to_enchant:
                                if item_to_enchant.get('type') == selected_enchantment.get('type'):
                                    item_to_enchant['enchantment'] = selected_enchantment['name']
                                    print(f"You successfully enchanted the {item_to_enchant['name']} with {selected_enchantment['name']}!")
                                else:
                                    print(f"You can't apply this enchantment to a {item_to_enchant.get('type')}.")
                            else:
                                print("You don't have that item.")
                        else:
                            print("Invalid enchantment number.")
                    except ValueError:
                        print("Invalid input.")
            else:
                print("You can't enchant items here.")

        elif verb == "look":
            display_room_content_summary(current_room, rooms_travelled, direction_history, seed)
            # You might want to add debug.debug_player_data() here too for context

        elif verb.startswith("inv"): # Changed to use .startswith
            # Use debug function for inventory data, but keep regular print for user-facing output
            if DEBUG: # Wrapped debug calls
                debug.debug_player_data(player_inventory, player_keychain, current_max_inventory_slots, player_gold, "Inventory Check")

            if not player_inventory and not player_keychain: # Check keychain too
                print("Your inventory is empty.")
            else:
                print(f"Your Health: {player_hp}/{max_hp} HP.")
                print(f"Your Level: {player_level} (XP: {player_xp}/{xp_to_next_level})")

                # Display regular inventory
                print(f"You are carrying ({len(player_inventory)}/{current_max_inventory_slots}):")
                if player_inventory:
                    for item_dict in player_inventory:
                        display_str = f"    - {add_article(item_dict['name'])}"
                        item_type = item_dict.get('type')
                        if item_type == 'consumable':
                            effect_type = item_dict.get('effect_type')
                            effect_value = item_dict.get('effect_value')
                            if effect_type == 'heal' and isinstance(effect_value, int):
                                display_str += f" (Heals {effect_value} HP)"
                            elif effect_type == 'harm' and isinstance(effect_value, int):
                                display_str += f" (Harms {effect_value} HP)"
                            elif effect_type == 'wake_up':
                                display_str += " (Stimulant)"
                            elif effect_type == 'flavor':
                                display_str += " (Consumable)"
                            elif effect_type == 'cure':
                                display_str += f" (Cures {item_dict.get('effect_value')})"
                            elif effect_type == 'inflict':
                                display_str += f" (Inflicts {item_dict.get('effect_value')})"
                        elif item_type == 'weapon':
                            display_str += f" (Damage: {item_dict.get('damage', '?')})"
                            if equipped_weapon and equipped_weapon['name'].lower() == item_dict['name'].lower():
                                display_str += " (EQUIPPED)"
                        elif item_type == 'armor':
                            # MODIFIED: Check if it's armor or cloak
                            item_subtype = item_dict.get('subtype')
                            if item_subtype == 'body_armor':
                                display_str += f" (Defense: {item_dict.get('defense', '?')})"
                                if equipped_armor_value and equipped_armor_value['name'].lower() == item_dict['name'].lower():
                                    display_str += " (EQUIPPED)"
                            elif item_subtype == 'cloak':
                                display_str += f" (Defense: {item_dict.get('defense', '?')})"
                                if equipped_cloak and equipped_cloak['name'].lower() == item_dict['name'].lower():
                                    display_str += " (EQUIPPED)"
                            else: # fallback for generic 'armor' type without subtype
                                display_str += f" (Defense: {item_dict.get('defense', '?')})"
                                if equipped_armor_value and equipped_armor_value['name'].lower() == item_dict['name'].lower():
                                    display_str += " (EQUIPPED)"
                        elif item_type == 'backpack':
                            display_str += f" (+{item_dict.get('effect_value', '?')} Slots)"
                        elif item_type == 'shield':
                            display_str += f" (Defense: {item_dict.get('defense', '?')})"
                            # FIXED: Compare by name for equipped status
                            if player_shield_value and player_shield_value['name'].lower() == item_dict['name'].lower():
                                display_str += " (EQUIPPED)"
                        elif item_type == 'winning_item':
                            display_str += " (Legendary Artifact!)"
                        elif item_type == 'equipment':
                            display_str += f" (Effect: {item_dict.get('effect_type', 'unknown')})"
                            if item_dict in equipped_misc_items:
                                display_str += " (EQUIPPED)"
                        elif item_dict.get('description'):
                            display_str += f" ({item_dict['description']})"
                        print(display_str)
                else:
                    print("    (Empty)")

                # Display keychain
                print("Your Keychain:")
                if player_keychain:
                    for item_dict in player_keychain:
                        print(f"    - {add_article(item_dict['name'])} (Type: {item_dict.get('key_type', '?')} key)")
                else:
                    print("    (Empty)")

                print(f"Your Gold: {player_gold}")
                print(f"Current Shield Defense: {player_shield_value.get('defense', 0) if player_shield_value else 0}") # Display value from item dict
                print(f"Current Armor Defense: {equipped_armor_value.get('defense', 0) if equipped_armor_value else 0}") # Display value from item dict
                # MODIFIED: Display cloak defense
                print(f"Current Cloak Defense: {equipped_cloak.get('defense', 0) if equipped_cloak else 0}")
                # MODIFIED: Update total defense calculation in display
                print(f"Total Defense: {(player_shield_value.get('defense', 0) if player_shield_value else 0) + (equipped_armor_value.get('defense', 0) if equipped_armor_value else 0) + (equipped_cloak.get('defense', 0) if equipped_cloak else 0)}")
                print(f"Attack Power: {player_attack_power} (+/-{player_attack_variance})")
                print(f"Critical Chance: {player_crit_chance*100:.0f}% (x{player_crit_multiplier:.1f} Damage)")
                if equipped_weapon:
                    print(f"Equipped Weapon: {equipped_weapon['name']} (Damage: {equipped_weapon.get('damage', '?')})")
                else:
                    print("Equipped Weapon: Fists (Damage: 5)")

                if player_effects:
                    print("\n--- Active Effects ---")
                    for effect in player_effects:
                        print(f"  - {effect['message'].split('!')[0]} ({effect['duration']} turns remaining)")
                    print("----------------------")
                continue

        # NEW COMMAND: 'equipped'
        elif verb == "equipped":
            print("\n--- Currently Equipped Items ---")
            print(f"Weapon: {equipped_weapon['name']} (Damage: {equipped_weapon.get('damage', '?')})" if equipped_weapon else "Weapon: Fists (Damage: 5)")
            print(f"Shield: {player_shield_value['name']} (Defense: {player_shield_value.get('defense', '?')})" if player_shield_value else "Shield: None")
            print(f"Body Armor: {equipped_armor_value['name']} (Defense: {equipped_armor_value.get('defense', '?')})" if equipped_armor_value else "Body Armor: None")
            print(f"Cloak: {equipped_cloak['name']} (Defense: {equipped_cloak.get('defense', '?')})" if equipped_cloak else "Cloak: None")
            if equipped_misc_items:
                print("Miscellaneous:")
                for item in equipped_misc_items:
                    print(f"  - {item['name']}")
            print(f"Total Defense: {(player_shield_value.get('defense', 0) if player_shield_value else 0) + (equipped_armor_value.get('defense', 0) if equipped_armor_value else 0) + (equipped_cloak.get('defense', 0) if equipped_cloak else 0)}")
            print("----------------------------------")
            continue

        elif verb == "misc":
            if not equipped_misc_items:
                print("You have no miscellaneous items equipped.")
            else:
                print("\n--- Equipped Miscellaneous Items ---")
                for item in equipped_misc_items:
                    print(f"  - {item['name']} (Effect: {item.get('effect_type', 'unknown')})")
                print("------------------------------------")
            continue

        # NEW/MODIFIED: Consolidated 'go' and direct directional commands
        elif verb in ["go", "north", "south", "east", "west"]:
            if current_room.hazard and current_room.hazard.get('is_currently_hidden') and not current_room.hazard.get('disarmed'):
                print(f"You stumble into a hidden {current_room.hazard['name']}!")
                current_room.hazard['is_currently_hidden'] = False
                # Trigger the trap
                player_hp -= current_room.hazard['damage']
                print(current_room.hazard['effect_message'].format(damage=current_room.hazard['damage']))
                print(f"Your health is now {player_hp}/{max_hp} HP.")
                if player_hp <= 0:
                    return 'lose'
                continue

            if current_room.monster:
                if current_room.monster.get('is_boss_guardian', False) and current_room.boss_monster_spawned:
                    print(f"You can't leave! The powerful {current_room.monster['name']} blocks your escape!")
                else:
                    print(f"You can't leave while the {current_room.monster['name']} is still here!")
                continue

            if current_room.awaiting_winning_item_pickup:
                print(f"You must first pick up {add_article(current_room.item['name'])}!")
                continue

            if current_room.puzzle and not current_room.puzzle.get('solved', True):
                if current_room.puzzle.get('rewards', {}).get('exit', {}).get('direction') not in current_room.exits:
                    print(f"The way is blocked by the puzzle! You must solve it first.")
                    continue

            # Determine the actual direction from input
            if verb in ["north", "south", "east", "west"]:
                direction = verb # Player typed just the direction
            elif verb == "go" and len(parts) >= 2:
                direction = parts[1] # Player typed "go [direction]"
            else:
                # This case should ideally not be hit with the prior checks,
                # but as a fallback, if "go" was typed without a direction.
                print("Where do you want to go? (e.g., 'go north' or just 'north')")
                continue

            opposites = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
            is_back_move = False
            if direction_history and direction == opposites.get(direction_history[-1]):
                is_back_move = True

            if is_back_move:
                print(f"You travel back {direction}...")
                time.sleep(1)
                current_room = room_history.pop()
                direction_history.pop()
                rooms_travelled -= 1
                sound_manager.stop_music()
                if getattr(current_room, 'is_inn', False):
                    sound_manager.play_music('inn_music')
                else:
                    sound_manager.play_music('ambient_music')
                log_event(f"Player {player_name} returned to Room #{rooms_travelled}.")
                display_room_content_summary(current_room, rooms_travelled, direction_history, seed)
                continue

            elif direction in current_room.exits:
                print(f"You travel {direction}...")
                time.sleep(1)

                room_history.append(current_room)
                direction_history.append(direction)

                sound_manager.stop_music()
                current_room = Room(player_level, player_quests, entry_direction=direction)
                # --- NEW: Handle if the new room is an inn ---
                while getattr(current_room, 'is_inn', False):
                    player_hp, max_hp, player_quests, player_inventory, player_gold, player_xp, xp_to_next_level, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_level, player_keychain, stash, has_hideout_key = \
                        handle_inn(player_hp, max_hp, player_quests, player_level, player_inventory, current_max_inventory_slots, player_gold, player_xp, xp_to_next_level, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_keychain, sound_manager, stash, has_hideout_key, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon)

                    print("You leave the inn to continue your journey.")
                    current_room = Room(player_level, player_quests) # Generate a new room
                # --- END NEW ---
                sound_manager.play_music('ambient_music') # Always play ambient after moving, as inn handles its own music.
                rooms_travelled += 1
                log_event(f"Player {player_name} entered Room #{rooms_travelled} travelling {direction}. Description: {current_room.description}")

                display_room_content_summary(current_room, rooms_travelled, direction_history, seed)

                # Handle immediate hazard upon entering new room
                if current_room.hazard:
                    print(current_room.hazard['effect_message'].format(damage=current_room.hazard['damage']))
                    # MODIFIED: Include equipped_cloak in total defense for hazards in new room
                    total_room_defense = (player_shield_value.get('defense', 0) if player_shield_value else 0) + \
                                         (equipped_armor_value.get('defense', 0) if equipped_armor_value else 0) + \
                                         (equipped_cloak.get('defense', 0) if equipped_cloak else 0)
                    actual_hazard_damage = max(0, current_room.hazard['damage'] - total_room_defense)
                    player_hp -= actual_hazard_damage
                    print(f"Your health is now {player_hp}/{max_hp} HP.")
                    if total_room_defense > 0:
                        print(f"Your total defense absorbed {current_room.hazard['damage'] - actual_hazard_damage} damage.")
                    if player_hp <= 0:
                        print("\n" + "=" * 40)
                        print("Your health has fallen to zero! You collapse.")
                        print("        G A M E    O V E R            ")
                        print("=" * 40)
                        if DEBUG: # Wrapped debug calls
                            debug.close_debug_log() # Close log on game over
                        return 'lose' # Game over, return 'lose'

                # If winning item just spawned, set flag for pickup
                if current_room.item and current_room.item['name'] in WINNING_ITEMS and current_room.winning_item_just_spawned:
                    print(f"\nAn intense aura fills the room, emanating from {add_article(current_room.item['name'])}!")
                    if len(player_inventory) >= current_max_inventory_slots:
                        print(f"Your inventory is full! You cannot pick up the {current_room.item['name']}.")
                        print("You must drop an item to make space. The guardian's presence is unsettling...")
                    else:
                        print("You must pick it up to proceed. (Type 'get item')")
                    current_room.awaiting_winning_item_pickup = True
                # Handle regular monsters that just spawned (not winning item guardians)
                elif current_room.monster and not current_room.monster.get('is_boss_guardian', False):
                    player_hp, max_hp, current_room.monster, gold_gained, player_xp, player_level, xp_to_next_level, player_quests, \
                    player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items = \
                        handle_combat(player_hp, max_hp, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, \
                                      current_room.monster, player_shield_value, equipped_armor_value, equipped_cloak, player_inventory, current_max_inventory_slots, \
                                      player_gold, equipped_weapon, player_xp, player_level, xp_to_next_level, player_quests, player_keychain, current_room, equipped_misc_items, player_effects, sound_manager, current_defense_bonus, current_crit_chance_bonus, equipped_helmet, player_class, player_unlocked_skills)
                    player_gold += gold_gained
                    if player_hp <= 0:
                        print("\n" + "=" * 40)
                        print("Your health has fallen to zero! You collapse.")
                        print("        G A M E    O V E R            ")
                        print("=" * 40)
                        if DEBUG: # Wrapped debug calls
                            debug.close_debug_log() # Close log on game over
                        return 'lose' # Game over, return 'lose'
                    if current_room.monster is None:
                        print(f"\nThe monster is defeated. The room is now safe.")
                        display_room_content_summary(current_room, rooms_travelled, direction_history, seed)


            elif direction in current_room.locked_exits:
                print(f"The {direction} exit is locked. You need to unlock it first.")
            else:
                print("You can't go that way.")

        elif verb == "get":
            item_to_get_name_input = None
            # If command is just "get" or "get item", try to get the current room's item
            if len(parts) == 1 or (len(parts) == 2 and parts[1] == "item"):
                if current_room.item:
                    item_to_get_name_input = current_room.item['name'].lower()
                else:
                    print("There's no item here to pick up.")
                    continue
            elif len(parts) >= 2:
                item_to_get_name_input = " ".join(parts[1:])
            else:
                print("What do you want to get? (e.g., 'get rusty key' or 'get item')")
                continue

            # Check if the item they're trying to get is actually on the floor
            if current_room.item and item_to_get_name_input == current_room.item['name'].lower():
                # Prevent picking up item if there's a non-boss monster (regular items)
                if current_room.monster and not current_room.monster.get('is_boss_guardian', False):
                    print(f"You can't just pick up {add_article(current_room.item['name'])}! It's guarded by the {current_room.monster['name']}!")
                    continue

                # Handle winning item pickup FIRST, then spawn the boss
                if current_room.item['name'] in WINNING_ITEMS:
                    if len(player_inventory) >= current_max_inventory_slots:
                        print(f"Your inventory is full! You can't carry {add_article(current_room.item['name'])}. Drop something first.")
                        continue
                    if current_room.boss_monster_spawned: # If boss already spawned, it means player ran away
                        print(f"The {current_room.monster['name']} is blocking your way to the {current_room.item['name']}!")
                        continue

                    # Player picks up the winning item
                    print(f"You reach out and grasp {add_article(current_room.item['name'])}! A surge of raw power courses through you.")
                    player_inventory.append(copy.deepcopy(current_room.item))
                    current_room.item = None # Item is picked up
                    current_room.winning_item_just_spawned = False # No longer just spawned
                    current_room.awaiting_winning_item_pickup = False # No longer awaiting pickup

                    print("\n" + "=" * 40)
                    print(f"You acquired the {player_inventory[-1]['name']}!")
                    print("But the dungeon trembles! Its true guardian senses its loss and appears!")
                    print("=" * 40)

                    # Now, spawn the boss monster dynamically
                    potential_boss_monsters = []
                    max_eligible_level = 0
                    for monster_def in MONSTERS:
                        monster_level = monster_def.get('level', 1)
                        level_difference = monster_level - player_level
                        if level_difference >= 0 and level_difference <= MONSTER_SPAWN_LEVEL_MAX_OFFSET:
                            potential_boss_monsters.append(monster_def)
                            if monster_level > max_eligible_level:
                                max_eligible_level = monster_level

                    hardest_monsters = [m for m in potential_boss_monsters if m.get('level', 1) == max_eligible_level]

                    if hardest_monsters:
                        current_room.monster = dict(random.choice(hardest_monsters))
                        current_room.monster['is_boss_guardian'] = True
                        current_room.boss_monster_spawned = True # Mark that boss has now officially spawned
                        print(f"A fierce {current_room.monster['name']} manifests, enraged by your theft!")
                        # Immediately initiate combat with the boss
                        player_hp, max_hp, current_room.monster, gold_gained, player_xp, player_level, xp_to_next_level, player_quests, \
                        player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items = \
                            handle_combat(player_hp, max_hp, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, \
                                          current_room.monster, player_shield_value, equipped_armor_value, equipped_cloak, player_inventory, current_max_inventory_slots, \
                                      player_gold, equipped_weapon, player_xp, player_level, xp_to_next_level, player_quests, player_keychain, current_room, equipped_misc_items, player_effects, sound_manager, current_defense_bonus, current_crit_chance_bonus, equipped_helmet, player_class, player_unlocked_skills)
                        player_gold += gold_gained
                        if player_hp <= 0:
                            print("\n" + "=" * 40)
                            print("Your health has fallen to zero! You collapse.")
                            print("        G A M E    O V E R            ")
                            print("=" * 40)
                            if DEBUG: # Wrapped debug calls
                                debug.close_debug_log() # Close log on game over
                            return 'lose' # End the game here
                        if current_room.monster is None: # Boss defeated
                            print(f"\nHaving defeated the guardian, you feel a sense of profound achievement!")
                            print("\n" + "=" * 40)
                            print(f"You have conquered this dungeon's greatest challenge! The dungeon continues, but you are now a true legend.")
                            print("Press ENTER to continue your adventure, or type 'exit' to return to the main menu.")
                            print("=" * 40)
                            # Remove the winning item from the room so it doesn't try to spawn another boss later
                            current_room.item = None
                            # Reset flags for winning item spawn for future rooms
                            current_room.winning_item_just_spawned = False
                            current_room.boss_monster_spawned = False

                            # NEW: Prompt for choice after winning
                            choice = input("> ").lower().strip()
                            if choice == 'exit':
                                return 'return_to_menu' # New return type to signal going back to main menu
                            else:
                                return 'continue_adventure' # Default for pressing Enter or anything else
                        else: # Player ran from boss
                            print(f"\nThe {current_room.monster['name']} still stalks this room, guarding your escape route.")
                    else:
                        print("You claimed the item, but no guardian appeared. (This is unexpected!)")
                        print("\n" + "=" * 40)
                        print(f"You found {player_inventory[-1]['name']}! You are truly lucky!")
                        print("The dungeon feels calmer, but still stretches endlessly before you.")
                        print("=" * 40)
                        current_room.item = None
                        current_room.winning_item_just_spawned = False
                        current_room.boss_monster_spawned = False
                        # NEW: Prompt for choice even if no boss for winning item (shouldn't happen with correct spawn logic)
                        print("Press ENTER to continue your adventure, or type 'exit' to return to the main menu.")
                        choice = input("> ").lower().strip()
                        if choice == 'exit':
                            return 'return_to_menu'
                        else:
                            return 'continue_adventure'

                # --- Keychain Integration: Keys go to keychain, others to inventory ---
                elif current_room.item.get('type') == 'key':
                    key_just_picked_up = current_room.item # Store a reference to the item
                    print(f"You pick up {add_article(key_just_picked_up['name'])} and attach it to your keychain.")
                    player_keychain.append(copy.deepcopy(key_just_picked_up)) # Add key to keychain
                    current_room.item = None # Item is picked up from the room
                    # --- NEW DEBUG AFTER KEY PICKUP ---
                    if DEBUG: # Wrapped debug calls
                        debug.debug_key_acquisition(player_keychain[-1], "room pickup")
                    # --- END NEW DEBUG ---
                # Regular item pickup logic (if not a winning item or key)
                else:
                    if len(player_inventory) >= current_max_inventory_slots:
                        print(f"Your inventory is full! You can't carry {add_article(current_room.item['name'])}.")
                        print(f"You must drop an item before picking up another. (Current: {len(player_inventory)}/{current_max_inventory_slots})")
                        continue

                    print(f"You pick up {add_article(current_room.item['name'])}.")
                    player_inventory.append(copy.deepcopy(current_room.item))

                    for q_id, q_data in player_quests.items():
                        quest_def = get_quest_by_id(q_id)
                        if quest_def and q_data['status'] == 'active' and quest_def['type'] == 'fetch_item' and quest_def['target_item'].lower() == item_to_get_name_input.lower():
                            if q_data['current_count'] < quest_def['target_count']:
                                q_data['current_count'] += 1
                                print(f"Quest Update: Picked up a {item_to_get_name_input}! ({q_data['current_count']}/{quest_def['target_count']})")
                                if q_data['current_count'] >= quest_def['target_count']:
                                    print(f"QUEST COMPLETE: '{quest_def['name']}'! Return to {quest_def['giver_npc_name']} to claim your reward!")

                    current_room.item = None # Item is picked up from the room
            else:
                print("That item is not here.")


        elif verb == "drop":
            if len(parts) < 2:
                print("What do you want to drop? (e.g., 'drop rusty key')")
                continue

            item_to_drop_name_input = " ".join(parts[1:])
            item_found_in_inventory = None
            item_found_in_keychain = None # For keychain

            # First, check player's main inventory
            for item_dict in player_inventory:
                if item_dict['name'].lower() == item_to_drop_name_input:
                    item_found_in_inventory = item_dict
                    break

            # If not in main inventory, check keychain
            if not item_found_in_inventory:
                for item_dict in player_keychain:
                    if item_dict['name'].lower() == item_to_drop_name_input:
                        item_found_in_keychain = item_dict
                        break

            if item_found_in_inventory:
                if item_found_in_inventory['name'] in WINNING_ITEMS:
                    print("You cannot drop a legendary artifact! It's too important.")
                    continue

                if current_room.item is not None:
                    print(f"You can't drop {add_article(item_found_in_inventory['name'])}. There's already {add_article(current_room.item['name'])} on the floor.")
                    continue

                is_quest_item = False
                for q_id, q_data in player_quests.items():
                    quest_def = get_quest_by_id(q_id)
                    if quest_def and q_data['status'] == 'active' and quest_def['type'] == 'fetch_item' and quest_def['target_item'].lower() == item_to_drop_name_input.lower():
                        if q_data['current_count'] > 0:
                            print(f"Warning: You are dropping a '{item_to_drop_name_input}' which is a quest item for '{quest_def['name']}'. Your quest progress will decrease.")
                            q_data['current_count'] -= 1
                            if q_data['current_count'] < quest_def['target_count']:
                                print(f"Quest Update: Your progress for '{quest_def['name']}' is now {q_data['current_count']}/{quest_def['target_count']}.")
                            is_quest_item = True
                            break

                # Unequip the specific item if it's currently equipped by object identity
                if equipped_weapon is item_found_in_inventory:
                    equipped_weapon = None
                    print(f"You unequip and drop {add_article(item_found_in_inventory['name'])}. You are now wielding your fists.")
                elif equipped_armor_value is item_found_in_inventory:
                    equipped_armor_value = None
                    print(f"You unequip and drop {add_article(item_found_in_inventory['name'])}. Your body armor defense is now 0.") # MODIFIED: clarify
                elif equipped_cloak is item_found_in_inventory: # NEW: Unequip cloak if dropping
                    equipped_cloak = None
                    print(f"You unequip and drop {add_article(item_found_in_inventory['name'])}. Your cloak defense is now 0.")
                elif item_found_in_inventory in equipped_misc_items:
                    equipped_misc_items.remove(item_found_in_inventory)
                    print(f"You unequip and drop {add_article(item_found_in_inventory['name'])}.")
                elif player_shield_value is item_found_in_inventory:
                    player_shield_value = None
                    print(f"You unequip and drop {add_article(item_found_in_inventory['name'])}. Your shield defense is now 0.")
                else:
                    if not is_quest_item: # Avoid double message if already warned about quest item
                        print(f"You drop {add_article(item_found_in_inventory['name'])}.")

                player_inventory.remove(item_found_in_inventory)
                current_room.item = item_found_in_inventory # Item returns to the room floor
                display_room_content_summary(current_room, rooms_travelled, direction_history, seed)
            elif item_found_in_keychain: # Item is in keychain
                if current_room.item is not None:
                    print(f"You can't drop {add_article(item_found_in_keychain['name'])}. There's already {add_article(current_room.item['name'])} on the floor.")
                    continue

                print(f"You drop {add_article(item_found_in_keychain['name'])} from your keychain.")
                player_keychain.remove(item_found_in_keychain)
                current_room.item = item_found_in_keychain # Key returns to the room floor
                display_room_content_summary(current_room, rooms_travelled, direction_history, seed)
            else:
                print(f"You don't have {item_to_drop_name_input} in your inventory or keychain.")


        elif verb == "use":
            if len(parts) < 2:
                print("What do you want to use? (e.g., 'use healing potion')")
                continue

            item_to_use_name_input = " ".join(parts[1:])
            item_found_in_inventory = None
            for item_dict in player_inventory:
                if item_dict['name'].lower() == item_to_use_name_input:
                    item_found_in_inventory = item_dict
                    break

            if item_found_in_inventory:
                original_player_hp = player_hp
                player_hp, max_hp, current_max_inventory_slots, consumed_turn, stat_changes = process_item_use(item_found_in_inventory, player_hp, max_hp, player_inventory, current_max_inventory_slots, in_combat=False)

                if stat_changes:
                    if 'attack_power' in stat_changes:
                        player_attack_bonus += stat_changes['attack_power']
                        print(f"Your base attack power has permanently increased by {stat_changes['attack_power']}!")
                    elif 'max_hp' in stat_changes:
                        hp_increase = stat_changes['max_hp']
                        max_hp += hp_increase
                        player_hp += hp_increase
                        print(f"Your maximum HP has permanently increased by {hp_increase}!")

                if player_hp <= 0:
                    print("\n" + "=" * 40)
                    print("Your health has fallen to zero! You collapse.")
                    print("        G A M E    O V E R            ")
                    print("=" * 40)
                    if DEBUG: # Wrapped debug calls
                        debug.close_debug_log() # Close log on game over
                    return 'lose' # Game over, return 'lose'

                if player_hp != original_player_hp:
                    print(f"Your health is now {player_hp}/{max_hp} HP.")
            else:
                print(f"You don't have {item_to_use_name_input} in your inventory.")

        elif verb in ["equip", "quip"]:
            if len(parts) < 2:
                print("What do you want to equip? (e.g., 'equip wooden sword' or 'quip chainmail')")
                continue

            item_to_equip_name_input = " ".join(parts[1:])
            item_found_in_inventory = None
            # Find the *specific instance* of the item to equip
            for item_dict in player_inventory:
                if item_dict['name'].lower() == item_to_equip_name_input and \
                   item_dict.get('type') in ['shield', 'armor', 'weapon', 'equipment']:
                    item_found_in_inventory = item_dict
                    break

            if item_found_in_inventory:
                player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items, equipped_helmet = \
                    handle_equip_item(item_found_in_inventory, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items, player_level, equipped_helmet)
                player_attack_power = recalculate_attack_power(player_level, equipped_weapon, equipped_misc_items, player_attack_bonus)
                print(f"Your attack power is now {player_attack_power}.")
            else:
                print(f"You don't have {item_to_equip_name_input} in your inventory, or it's not an equipable item (weapon, shield, or armor).")


        elif verb == "unequip":
            if len(parts) < 2:
                print("What do you want to unequip? (e.g., 'unequip wooden sword')")
                continue

            item_to_unequip_name_input = " ".join(parts[1:])

            item_unequipped = False

            # Check weapon
            if equipped_weapon and equipped_weapon['name'].lower() == item_to_unequip_name_input:
                if equipped_weapon.get('cursed'):
                    print(f"Your {equipped_weapon['name']} is cursed! You cannot unequip it.")
                else:
                    print(f"You unequip your {equipped_weapon['name']}.")
                    equipped_weapon = None
                item_unequipped = True

            # Check shield
            elif player_shield_value and player_shield_value['name'].lower() == item_to_unequip_name_input:
                if player_shield_value.get('cursed'):
                    print(f"Your {player_shield_value['name']} is cursed! You cannot unequip it.")
                else:
                    print(f"You unequip your {player_shield_value['name']}.")
                    player_shield_value = None
                item_unequipped = True

            # Check body armor
            elif equipped_armor_value and equipped_armor_value['name'].lower() == item_to_unequip_name_input:
                if equipped_armor_value.get('cursed'):
                    print(f"Your {equipped_armor_value['name']} is cursed! You cannot unequip it.")
                else:
                    print(f"You unequip your {equipped_armor_value['name']}.")
                    equipped_armor_value = None
                item_unequipped = True

            # Check cloak
            elif equipped_cloak and equipped_cloak['name'].lower() == item_to_unequip_name_input:
                if equipped_cloak.get('cursed'):
                    print(f"Your {equipped_cloak['name']} is cursed! You cannot unequip it.")
                else:
                    print(f"You unequip your {equipped_cloak['name']}.")
                    equipped_cloak = None
                item_unequipped = True

            # Check helmet
            elif equipped_helmet and equipped_helmet['name'].lower() == item_to_unequip_name_input:
                if equipped_helmet.get('cursed'):
                    print(f"Your {equipped_helmet['name']} is cursed! You cannot unequip it.")
                else:
                    print(f"You unequip your {equipped_helmet['name']}.")
                    equipped_helmet = None
                item_unequipped = True

            else:
                for item in equipped_misc_items:
                    if item['name'].lower() == item_to_unequip_name_input:
                        if item.get('cursed'):
                            print(f"Your {item['name']} is cursed! You cannot unequip it.")
                        else:
                            print(f"You unequip your {item['name']}.")
                            equipped_misc_items.remove(item)
                        item_unequipped = True
                        break

            if not item_unequipped:
                print(f"You don't have '{item_to_unequip_name_input}' equipped.")

        elif verb == "attack":
            # If a winning item just spawned and hasn't been picked up, prevent attacking a non-existent boss
            if current_room.awaiting_winning_item_pickup:
                print(f"You must first pick up {add_article(current_room.item['name'])}!")
                continue

            if current_room.monster:
                player_hp, max_hp, current_room.monster, gold_gained, player_xp, player_level, xp_to_next_level, player_quests, \
                player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items = \
                    handle_combat(player_hp, max_hp, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, \
                                  current_room.monster, player_shield_value, equipped_armor_value, equipped_cloak, player_inventory, current_max_inventory_slots, \
                                  player_gold, equipped_weapon, player_xp, player_level, xp_to_next_level, player_quests, player_keychain, current_room, equipped_misc_items, player_effects, sound_manager, current_defense_bonus, current_crit_chance_bonus, equipped_helmet, player_class, player_unlocked_skills)
                player_gold += gold_gained
                if player_hp <= 0:
                    print("\n" + "=" * 40)
                    print("Your health has fallen to zero! You collapse.")
                    print("        G A M E    O V E R            ")
                    print("=" * 40)
                    if DEBUG: # Wrapped debug calls
                        debug.close_debug_log() # Close log on game over
                    return 'lose' # Game over, return 'lose'
                if current_room.monster is None:
                    # If the monster was a boss guardian, the game is won, but continues
                    if current_room.boss_monster_spawned and any(item['name'] in WINNING_ITEMS for item in player_inventory):
                        print(f"\nHaving defeated the guardian, you feel a sense of profound achievement!")
                        print("\n" + "=" * 40)
                        print(f"You have conquered this dungeon's greatest challenge! The dungeon continues, but you are now a true legend.")
                        print("Press ENTER to continue your adventure, or type 'exit' to return to the main menu.")
                        print("=" * 40)
                        # Remove the winning item from the room so it doesn't try to spawn another boss later
                        current_room.item = None
                        # Reset flags for winning item spawn for future rooms
                        current_room.winning_item_just_spawned = False
                        current_room.boss_monster_spawned = False

                        # NEW: Prompt for choice after winning
                        choice = input("> ").lower().strip()
                        if choice == 'exit':
                            return 'return_to_menu' # New return type to signal going back to main menu
                        else:
                            return 'continue_adventure' # Default for pressing Enter or anything else
                    else:
                        print(f"\nThe monster is defeated. The room is now safe.")
                        display_room_content_summary(current_room, rooms_travelled, direction_history, seed)
            else:
                print("There's nothing to attack here.")

        elif verb == "combine":
            if len(parts) < 2:
                print("Combine what? Usage: 'combine [item name]' (e.g., 'combine healing potion')")
                continue

            item_to_combine_name_input = " ".join(parts[1:])

            if current_room.monster:
                print(f"You can't combine items while the {current_room.monster['name']} is still here!")
                continue

            if item_to_combine_name_input == "healing potion":
                healing_potion_count = 0
                healing_potions_in_inv = []
                # Collect actual item objects for removal
                for item_obj in player_inventory:
                    if item_obj.get('name', '').lower() == "healing potion" and \
                       item_obj.get('type') == 'consumable' and \
                       item_obj.get('effect_type') == 'heal':
                        healing_potion_count += 1
                        healing_potions_in_inv.append(item_obj)

                if healing_potion_count >= 2:
                    large_healing_potion_def = get_item_by_name('large healing potion')

                    if large_healing_potion_def:
                        # Check inventory space AFTER removing 2 and adding 1 (net change -1)
                        if len(player_inventory) - 2 + 1 > current_max_inventory_slots:
                                     print("Your inventory is too full to combine items! You need at least one free slot after combining.")
                        else:
                            # Remove the first two healing potion objects found
                            player_inventory.remove(healing_potions_in_inv[0])
                            player_inventory.remove(healing_potions_in_inv[1])

                            player_inventory.append(copy.deepcopy(large_healing_potion_def))
                            print(f"You carefully combine two healing potions to create {add_article(large_healing_potion_def['name'])}!")
                            print(f"Your inventory now has {len(player_inventory)}/{current_max_inventory_slots} items.")
                    else:
                        print("Could not find 'large healing potion' definition in game data. Combination failed.")
                else:
                    print("You need at least two 'healing potions' to combine them into a large one.")

            # NEW LOGIC FOR SUPER HEALING POTION
            elif item_to_combine_name_input == "large healing potion":
                large_healing_potion_count = 0
                large_healing_potions_in_inv = []
                # Collect actual item objects for removal
                for item_obj in player_inventory:
                    if item_obj.get('name', '').lower() == "large healing potion" and \
                       item_obj.get('type') == 'consumable' and \
                       item_obj.get('effect_type') == 'heal':
                        large_healing_potion_count += 1
                        large_healing_potions_in_inv.append(item_obj)

                if large_healing_potion_count >= 2:
                    super_healing_potion_def = get_item_by_name('super healing potion')

                    if super_healing_potion_def:
                        # Check inventory space (same net change: -1 item)
                        if len(player_inventory) - 2 + 1 > current_max_inventory_slots:
                            print("Your inventory is too full to combine items! You need at least one free slot after combining.")
                        else:
                            # Remove the first two large healing potion objects found
                            player_inventory.remove(large_healing_potions_in_inv[0])
                            player_inventory.remove(large_healing_potions_in_inv[1])

                            player_inventory.append(copy.deepcopy(super_healing_potion_def))
                            print(f"With meticulous care, you combine two large healing potions to create {add_article(super_healing_potion_def['name'])}!")
                            print(f"Your inventory now has {len(player_inventory)}/{current_max_inventory_slots} items.")
                    else:
                        print("Could not find 'super healing potion' definition in game data. Combination failed.")
                else:
                    print("You need at least two 'large healing potions' to combine them into a super one.")
            # END NEW LOGIC

            else: # This 'else' now catches all other non-recognized combine attempts
                print(f"You don't know how to combine {add_article(item_to_combine_name_input)}.")

        elif verb == "unlock":
            if len(parts) < 4 or parts[2] != "with":
                print("Unlock what? Usage: 'unlock [direction] with [key name]'")
                continue

            if current_room.monster:
                print(f"You can't do that while the {current_room.monster['name']} is still here!")
                continue

            direction_to_unlock = parts[1]
            key_name_input = " ".join(parts[3:])

            if direction_to_unlock not in current_room.locked_exits:
                print(f"The {direction_to_unlock} exit is not locked, or it doesn't exist.")
                continue

            required_key_type = current_room.locked_exits[direction_to_unlock]

            has_correct_key = False
            found_key_item = None # Can be from keychain or inventory

            for inv_item_dict in player_keychain: # Check keychain first
                if (inv_item_dict.get('type') == 'key' and
                    inv_item_dict.get('key_type') == required_key_type and
                    inv_item_dict['name'].lower() == key_name_input):
                    has_correct_key = True
                    found_key_item = inv_item_dict
                    break

            # If not found in keychain, check main inventory for keys (legacy or dropped)
            if not has_correct_key:
                for inv_item_dict in player_inventory:
                    if (inv_item_dict.get('type') == 'key' and
                        inv_item_dict.get('key_type') == required_key_type and
                        inv_item_dict['name'].lower() == key_name_input):
                        has_correct_key = True
                        found_key_item = inv_item_dict
                        break
                    elif inv_item_dict['name'].lower() == key_name_input and inv_item_dict.get('type') == 'key':
                        print(f"You have '{add_article(inv_item_dict['name'])}', but it's not the correct type for this lock. It requires a '{required_key_type}' key.")
                        break # Found a wrong key, stop searching

            if has_correct_key and found_key_item:
                print(f"You use {add_article(found_key_item['name'])} to unlock the {direction_to_unlock} exit.")
                # Remove from appropriate location
                if found_key_item in player_keychain:
                    player_keychain.remove(found_key_item) # Keys are typically consumed
                elif found_key_item in player_inventory: # For keys still in main inventory
                    player_inventory.remove(found_key_item)

                key_type_used = found_key_item.get('key_type')
                key_unlock_events = GAME_DATA.get('key_unlock_events', {})
                if key_type_used and key_type_used in key_unlock_events:
                    special_event_after_unlock = key_unlock_events[key_type_used]
                    print("You feel a strange presence shift behind the newly unlocked door...")

                current_room.exits[direction_to_unlock] = True
                del current_room.locked_exits[direction_to_unlock]
                display_room_content_summary(current_room, rooms_travelled, direction_history, seed)
            else:
                if not has_correct_key and not found_key_item:
                    print(f"You don't have '{key_name_input}' in your inventory or keychain.")

        # --- UPDATED `talk` COMMAND BLOCK ---
        elif verb == "talk":
            if current_room.monster:
                print(f"You can't talk while the {current_room.monster['name']} is still here!")
                continue

            if hasattr(current_room, 'is_inn') and current_room.is_inn:
                quest_givers = [n for n in NPCs if n.get('type') == 'quest_giver']
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
                    if chosen_npc:
                        player_quests, player_inventory, player_gold, player_xp, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_level = \
                            interact_with_quest_giver(chosen_npc, player_quests, player_level, player_inventory, current_max_inventory_slots, player_gold, player_xp, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_keychain, sound_manager)
                    else:
                        print(f"You don't see anyone named '{npc_name_to_talk}' here.")
                continue

            if current_room.npc:
                if current_room.npc.get('type') == 'quest_giver':
                    player_quests, player_reputation, player_inventory, player_gold, player_xp, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_level = \
                        interact_with_quest_giver(current_room.npc, player_quests, player_reputation, player_level, player_inventory, current_max_inventory_slots, player_gold, player_xp, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_keychain, sound_manager)
                else:
                    # Existing non-quest-giver talk logic
                    print(f"You approach {current_room.npc['name']}.")
                    if current_room.npc.get('dialogues'):
                        print(f"{current_room.npc['name']}: '{random.choice(current_room.npc['dialogues'])}'")
                    else:
                        print(f"{current_room.npc['name']} stares blankly.")
                    current_room.npc['talked_to'] = True
                    # Check if this NPC is a target for a 'find_npc' quest
                    for q_id, q_data in player_quests.items():
                        quest_def = get_quest_by_id(q_id)
                        if quest_def and q_data['status'] == 'active' and quest_def['type'] == 'find_npc':
                            if quest_def['target_npc_name'].lower() == current_room.npc['name'].lower():
                                player_quests[q_id]['found_npc'] = True
                                print(f"Quest Update: You have found {current_room.npc['name']} for the quest '{quest_def['name']}'!")
                                print(f"Return to {quest_def['giver_npc_name']} to complete the quest.")
                    if current_room.npc.get('type') == 'vendor':
                        player_gold, player_inventory, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, player_keychain, equipped_misc_items = \
                            handle_shop(player_gold, player_inventory, current_max_inventory_slots, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, current_room.npc, player_keychain, player_level, sound_manager, equipped_misc_items)
                    elif current_room.npc.get('type') == 'gambler':
                        player_gold = handle_gambler(player_gold, current_room.npc)
            else:
                print("There's no one here to talk to.")

        elif verb == "rest":
            if hasattr(current_room, 'is_inn') and current_room.is_inn:
                if player_hp < max_hp:
                    player_hp = max_hp
                    print("\nYou rest by the fire, feeling your wounds mend and your spirit lift. You are fully healed.")
                else:
                    print("\nYou are already at full health and feeling great.")
            else:
                print("You can only rest at an inn.")

        elif verb == "quests":
            if not player_quests:
                print("You currently have no active quests.")
            else:
                print("\n------------------------------------")
                print("\n-------- Your Active Quests --------")
                print("\n------------------------------------")
                has_active_quest = False
                for q_id, q_data in player_quests.items():
                    quest_def = get_quest_by_id(q_id)
                    if not quest_def or q_data['status'] == 'completed':
                        continue

                    has_active_quest = True
                    status = get_player_quest_status(player_quests, q_id)

                    progress_info = ""
                    if quest_def['type'] in ['defeat_any_monster', 'defeat_monster', 'fetch_item']:
                        # Check if progress tracking is possible
                        if 'current_count' in q_data and 'target_count' in quest_def:
                            if quest_def['type'] == 'fetch_item':
                                progress_info = f" (Collected: {q_data['current_count']}/{quest_def['target_count']} {quest_def.get('target_item','')}s)"
                            else:
                                progress_info = f" (Defeated: {q_data['current_count']}/{quest_def['target_count']} enemies)"

                    print(f"- {quest_def['name']} [{status.upper()}]{progress_info}")
                    print(f"  Description: {quest_def.get('description', 'No description provided.')}")

                    if status == 'active':
                        # Check if the quest dialogue can be formatted with counts
                        if 'current_count' in q_data and 'target_count' in quest_def:
                            dialogue_line = quest_def.get('dialogue_active', 'Continue quest').format(current_count=q_data['current_count'], target_count=quest_def['target_count'])
                        else:
                            # Fallback for quests without countable progress (e.g., find_npc)
                            dialogue_line = quest_def.get('dialogue_active', 'Continue quest')
                        print(f"  Goal: {dialogue_line}")
                    elif status == 'complete_ready':
                        print(f"  Goal: Return to {quest_def['giver_npc_name']} to turn in!")

                if not has_active_quest:
                    print("You currently have no active quests.")
                print("------------------------------------")

        elif verb == "answer":
            if current_room.monster:
                print(f"You can't concentrate on riddles while the {current_room.monster['name']} is still here!")
                continue
            if not current_room.puzzle or current_room.puzzle.get('solved', True) or current_room.puzzle['type'] != 'riddle':
                print("There's no riddle here to answer.")
                continue

            if len(parts) < 2:
                print("What is your answer?")
                continue

            player_answer = " ".join(parts[1:]).lower().strip()
            correct_answer = current_room.puzzle['solution'].lower().strip()

            if player_answer == correct_answer:
                print(f"'{player_answer.capitalize()}!' A resonant voice echoes, 'Correct!'")
                print(f"The ancient guardian rumbles and slowly recedes into the wall, opening the way.")
                current_room.puzzle['solved'] = True
                
                # NEW: Call the new reward handler function
                player_inventory, current_max_inventory_slots, player_keychain, player_xp, player_gold, player_level, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points = process_puzzle_rewards(
                    current_room.puzzle, player_inventory, current_max_inventory_slots, player_keychain, player_xp, player_gold, player_level, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points
                )

                display_room_content_summary(current_room, rooms_travelled, direction_history, seed)
            else:
                print(f"'{player_answer.capitalize()}!' The voice sighs, 'Incorrect.'")
                fail_penalty = current_room.puzzle.get('fail_penalty')
                if fail_penalty:
                    if fail_penalty['type'] == 'damage':
                        damage_taken = fail_penalty['value']
                        # MODIFIED: Include equipped_cloak in total defense calculation for puzzle damage
                        total_defense = (player_shield_value.get('defense', 0) if player_shield_value else 0) + \
                                        (equipped_armor_value.get('defense', 0) if equipped_armor_value else 0) + \
                                        (equipped_cloak.get('defense', 0) if equipped_cloak else 0)
                        actual_damage = max(0, damage_taken - total_defense)
                        player_hp -= actual_damage
                        print(fail_penalty['message'].format(value=damage_taken, actual_damage=actual_damage))
                        if total_defense > 0:
                            print(f"Your total defense absorbed {damage_taken - actual_damage} damage.")
                        print(f"Your health is now {player_hp}/{max_hp} HP.")
                        if player_hp <= 0:
                            print("\n" + "=" * 50)
                            print("Your health has fallen to zero! You collapse.")
                            print("        G A M E    O V E R            ")
                            print("=" * 50)
                            if DEBUG: # Wrapped debug calls
                                debug.close_debug_log() # Close log on game over
                            return 'lose' # Game over, return 'lose'
                    elif fail_penalty['type'] == 'monster_spawn':
                        # Make sure to strip and lower the monster name from JSON for with lookup
                        monster_name_from_penalty = fail_penalty['monster_name'].lower().strip()
                        monster_def = next((m for m in MONSTERS if m['name'].lower().strip() == monster_name_from_penalty), None)
                        if monster_def:
                            current_room.monster = dict(monster_def)
                            print(fail_penalty['message'])
                            player_hp, max_hp, current_room.monster, gold_gained, player_xp, player_level, xp_to_next_level, player_quests, \
                            player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items = \
                                handle_combat(player_hp, max_hp, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, \
                                              current_room.monster, player_shield_value, equipped_armor_value, equipped_cloak, player_inventory, current_max_inventory_slots, \
                                              player_gold, equipped_weapon, player_xp, player_level, xp_to_next_level, player_quests, player_keychain, current_room, equipped_misc_items, player_effects, sound_manager, 0, 0, equipped_helmet, player_class, player_unlocked_skills)
                            player_gold += gold_gained
                            if player_hp <= 0:
                                print("\n" + "=" * 40)
                                print("Your health has fallen to zero! You collapse.")
                                print("        G A M E    O V E R            ")
                                print("=" * 40)
                                if DEBUG: # Wrapped debug calls
                                    debug.close_debug_log() # Close log on game over
                                return 'lose' # Game over, return 'lose'
                            if current_room.monster is None:
                                display_room_content_summary(current_room, rooms_travelled, direction_history)
                        else:
                            print(f"A monster was supposed to spawn ('{fail_penalty['monster_name']}'), but its definition was not found. Please check game_data.json.") # More specific message
                    elif fail_penalty['type'] == 'flavor':
                        print(fail_penalty['message'])
                else:
                    print("Nothing seems to happen.")

        elif verb == "pull":
            if current_room.monster:
                print(f"You can't mess with levers while the {current_room.monster['name']} is still here!")
                continue
            if not current_room.puzzle or current_room.puzzle.get('solved', True) or current_room.puzzle['type'] != 'mechanism':
                print("There's no lever here to pull.")
                continue

            if len(parts) < 2:
                print("Which lever do you want to pull? (e.g., 'pull gold')")
                continue

            lever_choice = " ".join(parts[1:]).lower().strip()
            correct_lever = current_room.puzzle['solution'].lower().strip()

            if lever_choice == correct_lever:
                print(f"You pull the {lever_choice} lever. With a grinding sound, something happens!")
                current_room.puzzle['solved'] = True

                # NEW: Call the new reward handler function
                player_inventory, current_max_inventory_slots, player_keychain, player_xp, player_gold, player_level, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points = process_puzzle_rewards(
                    current_room.puzzle, player_inventory, current_max_inventory_slots, player_keychain, player_xp, player_gold, player_level, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points
                )

                display_room_content_summary(current_room, rooms_travelled, direction_history)
            else:
                print(f"You pull the {lever_choice} lever. A loud clank echoes, but nothing else happens.")
                fail_penalty = current_room.puzzle.get('fail_penalty')
                if fail_penalty:
                    if fail_penalty['type'] == 'damage':
                        damage_taken = fail_penalty['value']
                        # MODIFIED: Include equipped_cloak in total defense for puzzle damage
                        total_defense = (player_shield_value.get('defense', 0) if player_shield_value else 0) + \
                                        (equipped_armor_value.get('defense', 0) if equipped_armor_value else 0) + \
                                        (equipped_cloak.get('defense', 0) if equipped_cloak else 0)
                        actual_damage = max(0, damage_taken - total_defense)
                        player_hp -= actual_damage
                        print(fail_penalty['message'].format(value=damage_taken, actual_damage=actual_damage))
                        if total_defense > 0:
                            print(f"Your total defense absorbed {damage_taken - actual_damage} damage.")
                        print(f"Your health is now {player_hp}/{max_hp} HP.")
                        if player_hp <= 0:
                            print("\n" + "=" * 50)
                            print("Your health has fallen to zero! You collapse.")
                            print("        G A M E    O V E R            ")
                            print("=" * 50)
                            if DEBUG: # Wrapped debug calls
                                debug.close_debug_log() # Close log on game over
                            return 'lose' # Game over, return 'lose'
                    elif fail_penalty['type'] == 'monster_spawn':
                        # Make sure to strip and lower the monster name from JSON for robust lookup
                        monster_name_from_penalty = fail_penalty['monster_name'].lower().strip()
                        monster_def = next((m for m in MONSTERS if m['name'].lower().strip() == monster_name_from_penalty), None)
                        if monster_def:
                            current_room.monster = dict(monster_def)
                            print(fail_penalty['message'])
                            player_hp, max_hp, current_room.monster, gold_gained, player_xp, player_level, xp_to_next_level, player_quests, \
                            player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items = \
                                handle_combat(player_hp, max_hp, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, \
                                              current_room.monster, player_shield_value, equipped_armor_value, equipped_cloak, player_inventory, current_max_inventory_slots, \
                                              player_gold, equipped_weapon, player_xp, player_level, xp_to_next_level, player_quests, player_keychain, current_room, equipped_misc_items, player_effects, sound_manager, 0, 0, equipped_helmet, player_class, player_unlocked_skills)
                            player_gold += gold_gained
                            if player_hp <= 0:
                                print("\n" + "=" * 40)
                                print("Your health has fallen to zero! You collapse.")
                                print("        G A M E    O V E R            ")
                                print("=" * 40)
                                if DEBUG: # Wrapped debug calls
                                    debug.close_debug_log() # Close log on game over
                                return 'lose' # Game over, return 'lose'
                            if current_room.monster is None:
                                display_room_content_summary(current_room, rooms_travelled, direction_history)
                        else:
                            print(f"A monster was supposed to spawn ('{fail_penalty['monster_name']}'), but its definition was not found. Please check game_data.json.") # More specific message
                    elif fail_penalty['type'] == 'flavor':
                        print(fail_penalty['message'])
                else:
                    print("Nothing seems to happen.")

        elif verb == "give":
            if current_room.monster:
                print(f"You can't give items while the {current_room.monster['name']} is still here!")
                continue
            if not current_room.puzzle or current_room.puzzle.get('solved', True) or current_room.puzzle['type'] != 'item_delivery':
                print("There's nothing here that wants an item.")
                continue

            # NEW: Robust parsing for multi-word item and target names
            try:
                to_index = parts.index('to')
            except ValueError:
                print("Give what to whom? Usage: 'give [item name] to [target name]'")
                continue

            if to_index < 2: # 'give [item] to [target]' means 'to' should be at least at index 2
                print("Give what to whom? Usage: 'give [item name] to [target name]'")
                continue

            item_to_give_name_input = " ".join(parts[1:to_index]).lower().strip()
            target_name_input = " ".join(parts[to_index+1:]).lower().strip()

            if not item_to_give_name_input or not target_name_input:
                print("Give what to whom? Usage: 'give [item name] to [target name]'")
                continue
            # END NEW PARSING

            required_item_name = current_room.puzzle['required_item'].lower().strip()
            puzzle_target_name = current_room.puzzle.get('target_name', 'statue').lower()

            # FIX: Corrected variable name from target_name_name_input to target_name_input
            if target_name_input != puzzle_target_name:
                print(f"That target doesn't seem to be {puzzle_target_name} here or doesn't want your item.")
                continue

            item_found_in_inventory = None
            item_found_in_keychain = None # Check keychain too

            # First, check main inventory
            for item_dict in player_inventory:
                if item_dict['name'].lower() == item_to_give_name_input:
                    item_found_in_inventory = item_dict
                    break

            # If not in main inventory, check keychain
            if not item_found_in_inventory:
                for item_dict in player_keychain:
                    if item_dict['name'].lower() == item_to_give_name_input:
                        item_found_in_keychain = item_dict
                        break

            if not item_found_in_inventory and not item_found_in_keychain:
                print(f"You don't have {add_article(item_to_give_name_input)} in your inventory or keychain.")
                continue

            # Determine which item was found
            found_item = item_found_in_inventory if item_found_in_inventory else item_found_in_keychain

            # Check if the required item is a generic 'healing item' and the given item is a specific healing potion
            is_healing_item_puzzle = required_item_name == 'healing item'
            is_given_item_healing_potion = (found_item.get('type') == 'consumable' and
                                            found_item.get('effect_type') == 'heal')

            if item_to_give_name_input == required_item_name or (is_healing_item_puzzle and is_given_item_healing_potion):
                print(f"You give {add_article(found_item['name'])} to the {puzzle_target_name}. It glows faintly!")
                if found_item in player_inventory: # Remove from where it was found
                    player_inventory.remove(found_item)
                elif found_item in player_keychain:
                    player_keychain.remove(found_item)
                current_room.puzzle['solved'] = True

                # NEW: Call the new reward handler function
                player_inventory, current_max_inventory_slots, player_keychain, player_xp, player_gold, player_level, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points = process_puzzle_rewards(
                    current_room.puzzle, player_inventory, current_max_inventory_slots, player_keychain, player_xp, player_gold, player_level, xp_to_next_level, player_hp, max_hp, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_skill_points
                )

                display_room_content_summary(current_room, rooms_travelled, direction_history)
            else:
                print(f"The {puzzle_target_name} rejects {add_article(found_item['name'])}. It seems to desire something else.")
                fail_penalty = current_room.puzzle.get('fail_penalty')
                if fail_penalty:
                    print(fail_penalty['message'])
                else:
                    print("Nothing seems to happen.")

        elif verb == "save":
            # MODIFIED: Added equipped_cloak and player_attack_bonus to save_game parameters
            save_game(player_hp, max_hp, player_inventory, current_room, current_max_inventory_slots, player_gold, player_shield_value, equipped_armor_value, equipped_cloak, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, equipped_weapon, player_xp, player_level, xp_to_next_level, player_quests, player_reputation, player_name, rooms_travelled, player_keychain, equipped_misc_items, player_effects, room_history, direction_history, stash, player_class, player_skill_points, player_unlocked_skills, equipped_helmet, has_hideout_key) # Pass keychain and bonus

        elif verb == "ohvendor":
            guvna_npc_def = next((n for n in NPCs if n.get('name') == 'Stranger' and n.get('type') == 'vendor'), None)
            if guvna_npc_def:
                temp_vendor_npc = dict(guvna_npc_def)
                temp_vendor_npc['talked_to'] = True
                print("\n" + "=" * 30)
                print("\nA mysterious figure shimmers into existence from the shadows...")
                print("You hear a gruff voice say: 'Heh heh heh... What're ya buyin'?'")
                # MODIFIED: Added equipped_cloak and equipped_misc_items to handle_shop parameters
                player_gold, player_inventory, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, player_keychain, equipped_misc_items = \
                    handle_shop(player_gold, player_inventory, current_max_inventory_slots, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, temp_vendor_npc, player_keychain, player_level, sound_manager, equipped_misc_items) # Pass keychain and misc items
                print("\n" + "=" * 30)
                # After returning from handle_shop, display room summary
                display_room_content_summary(current_room, rooms_travelled, direction_history, seed)
            else:
                print("You try to summon the vendor, but he doesn't seem to respond. Perhaps he's not in this realm?")

        elif verb == "ohinn":
            player_hp, max_hp, player_quests, player_inventory, player_gold, player_xp, xp_to_next_level, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_level, player_keychain, stash, has_hideout_key = \
                handle_inn(player_hp, max_hp, player_quests, player_level, player_inventory, current_max_inventory_slots, player_gold, player_xp, xp_to_next_level, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_keychain, sound_manager, stash, has_hideout_key, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon)
            display_room_content_summary(current_room, rooms_travelled, direction_history, seed)

        elif verb == "search":
            if current_room.hazard and current_room.hazard.get('is_currently_hidden'):
                print("You search the room carefully...")
                time.sleep(1)
                perception_chance = 0.5
                if any(item.get('effect_type') == 'perception_boost' for item in player_effects):
                    perception_chance = 0.9
                if random.random() < perception_chance:
                    current_room.hazard['is_currently_hidden'] = False
                    print(f"You found a {current_room.hazard['name']}!")
                else:
                    print("You don't find anything unusual.")
            else:
                print("You search the room, but find nothing of interest.")

        elif verb == "disarm":
            if current_room.hazard and not current_room.hazard.get('is_currently_hidden'):
                if current_room.hazard.get('disarmable'):
                    if not current_room.hazard.get('disarmed'):
                        print(f"You attempt to disarm the {current_room.hazard['name']}...")
                        time.sleep(1)
                        disarm_chance = 0.5
                        if any(item['name'] == 'Trap Disarming Kit' for item in player_inventory):
                            disarm_chance = 0.9
                        if random.random() < disarm_chance:
                            current_room.hazard['disarmed'] = True
                            print(f"You successfully disarmed the {current_room.hazard['name']}.")
                        else:
                            print(f"You failed to disarm the {current_room.hazard['name']} and triggered it!")
                            # Trigger the trap
                            player_hp -= current_room.hazard['damage']
                            print(current_room.hazard['effect_message'].format(damage=current_room.hazard['damage']))
                            print(f"Your health is now {player_hp}/{max_hp} HP.")
                            if player_hp <= 0:
                                return 'lose'
                    else:
                        print("The trap is already disarmed.")
                else:
                    print("This hazard cannot be disarmed.")
            else:
                print("There is no visible trap to disarm.")

        elif verb == "credits":
            print(CREDITS_TEXT)
            input("Press Enter to continue...")
            display_room_content_summary(current_room, rooms_travelled, direction_history, seed)

        elif verb in ["pray", "drink"]:
            if current_room.shrine:
                if current_room.shrine.get('used'):
                    print(f"The {current_room.shrine['name']} is dormant. Nothing happens.")
                elif verb == current_room.shrine.get('interaction_verb'):
                    print(f"You {verb} at the {current_room.shrine['name']}...")
                    time.sleep(1)

                    # Choose a random effect based on weights
                    effects = current_room.shrine['effects']
                    total_weight = sum(e['weight'] for e in effects)
                    chosen_effect_list = random.choices(effects, weights=[e['weight'] for e in effects], k=1)
                    if not chosen_effect_list:
                         print("A strange feeling washes over you, but nothing seems to happen.")
                         continue

                    chosen_effect = chosen_effect_list[0]

                    print(chosen_effect['message'])
                    effect_type = chosen_effect['type']
                    details = chosen_effect['details']

                    if effect_type in ['buff', 'curse']:
                        # Create a new, flattened dictionary for the active effect
                        active_effect = {
                            'stat': details.get('stat'),
                            'modifier': details.get('modifier'),
                            'duration': details.get('duration'),
                            'message': chosen_effect.get('message')
                        }
                        player_effects.append(active_effect)
                    elif effect_type == 'heal':
                        if details['amount'] == 'full':
                            player_hp = max_hp
                        else:
                            player_hp = min(max_hp, player_hp + details['amount'])
                        print(f"Your health is now {player_hp}/{max_hp} HP.")
                    elif effect_type == 'gold':
                        player_gold += details['amount']
                        print(f"You now have {player_gold} gold.")
                    elif effect_type == 'damage':
                        player_hp -= details['amount']
                        print(f"Your health is now {player_hp}/{max_hp} HP.")
                        if player_hp <= 0:
                            print("\n" + "=" * 40)
                            print("The shrine delivers a fatal blow! You collapse.")
                            print("        G A M E    O V E R            ")
                            print("=" * 40)
                            if DEBUG: debug.close_debug_log()
                            return 'lose'
                    elif effect_type == 'spawn_monster':
                        monster_def = next((m for m in MONSTERS if m['name'] == details['monster_name']), None)
                        if monster_def:
                            current_room.monster = dict(monster_def)
                            # Initiate combat immediately
                            player_hp, max_hp, current_room.monster, gold_gained, player_xp, player_level, xp_to_next_level, player_quests, \
                            player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon, equipped_misc_items = \
                                handle_combat(player_hp, max_hp, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, \
                                            current_room.monster, player_shield_value, equipped_armor_value, equipped_cloak, player_inventory, current_max_inventory_slots, \
                                              player_gold, equipped_weapon, player_xp, player_level, xp_to_next_level, player_quests, player_keychain, current_room, equipped_misc_items, player_effects, sound_manager, 0, 0, equipped_helmet, player_class, player_unlocked_skills)
                            player_gold += gold_gained
                            if player_hp <= 0:
                                print("\n" + "=" * 40)
                                print("Your health has fallen to zero! You collapse.")
                                print("        G A M E    O V E R            ")
                                print("=" * 40)
                                if DEBUG: debug.close_debug_log()
                                return 'lose'

                    current_room.shrine['used'] = True
                else:
                    print(f"You can't '{verb}' at the {current_room.shrine['name']}. Try '{current_room.shrine['interaction_verb']}'.")
            else:
                print("There is nothing here to interact with in that way.")

        else:
            print("I don't understand that command. Type 'help' for a list of commands.")

    return 'continue_adventure' # Default return if the loop somehow exits without explicit win/lose/quit

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
                            handle_inn(player_hp, max_hp, player_quests, player_level, player_inventory, current_max_inventory_slots, player_gold, player_xp, xp_to_next_level, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_keychain, sound_manager, stash, has_hideout_key, player_shield_value, equipped_armor_value, equipped_cloak, equipped_weapon)

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
                        display_room_content_summary(current_room, rooms_travelled)
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
    monsters_defeated_this_run = 0
    if is_daily_challenge:
        print(f"Starting Daily Challenge for {seed}...")
        player_name_prompt = "Enter your adventurer's name for the leaderboard: "
    else:
        print("Starting a new adventure...")
        player_name_prompt = "Enter your adventurer's name: "

    set_seed(seed)

    hp_upgrade_level = meta_progress['upgrades'].get('max_hp', 0)
    hp_bonus = hp_upgrade_level * 5
    player_hp = 100 + hp_bonus
    max_hp = 100 + hp_bonus
    player_attack_power = BASE_PLAYER_ATTACK_POWER
    player_attack_bonus = 0
    player_attack_variance = BASE_PLAYER_ATTACK_VARIANCE
    player_crit_chance = BASE_PLAYER_CRIT_CHANCE
    player_crit_multiplier = BASE_PLAYER_CRIT_MULTIPLIER
    current_max_inventory_slots = 5
    player_gold = 500
    player_shield_value = None
    equipped_armor_value = None
    equipped_cloak = None
    equipped_helmet = None
    equipped_weapon = None
    player_xp = 0
    player_level = 1
    xp_to_next_level = calculate_xp_for_next_level(player_level)
    player_inventory = []
    player_keychain = []
    player_quests = {}
    player_reputation = {}
    equipped_misc_items = []
    player_effects = []
    room_history = []
    direction_history = []
    stash = []
    has_hideout_key = False

    player_name = input(player_name_prompt).strip()
    if not player_name:
        player_name = "Adventurer"

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
    player_class = class_choices[class_choice_index]
    print(f"You have chosen the path of the {player_class}.")
    class_data = character_classes[player_class]
    max_hp = class_data['starting_stats']['max_hp']
    player_hp = max_hp
    player_attack_power = class_data['starting_stats']['attack_power']
    player_attack_variance = class_data['starting_stats']['attack_variance']
    player_crit_chance = class_data['starting_stats']['crit_chance']
    player_crit_multiplier = class_data['starting_stats']['crit_multiplier']
    for item_name in class_data['starting_equipment']:
        item_def = get_item_by_name(item_name)
        if item_def:
            player_inventory.append(copy.deepcopy(item_def))
    player_skill_points = 0
    player_unlocked_skills = []

    current_room = Room(player_level, player_quests)
    rooms_travelled = 1
    initial_rooms_travelled = 1
    game_result, monsters_defeated_this_run, rooms_travelled = game_loop(player_hp, max_hp, player_inventory, current_room, current_max_inventory_slots, player_gold, player_shield_value, equipped_armor_value, equipped_cloak, player_attack_power, player_attack_bonus, player_attack_variance, player_crit_chance, player_crit_multiplier, equipped_weapon, player_xp, player_level, xp_to_next_level, player_quests, player_reputation, player_name, rooms_travelled, player_keychain, equipped_misc_items, player_effects, room_history, direction_history, sound_manager, equipped_helmet, player_class, player_skill_points, player_unlocked_skills, monsters_defeated_this_run, stash, has_hideout_key, seed=seed if is_daily_challenge else None)

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
                        player_hp, max_hp, player_quests, player_inventory, player_gold, player_xp, xp_to_next_level, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_level, player_keychain, stash = \
                            handle_inn(player_hp, max_hp, player_quests, player_level, player_inventory, current_max_inventory_slots, player_gold, player_xp, xp_to_next_level, player_attack_power, player_attack_variance, player_crit_chance, player_crit_multiplier, player_keychain, sound_manager, stash)

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