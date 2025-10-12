import random
import copy
from modules.game_data import GameData
from modules.utils import add_article

# --- GLOBAL GAME CONSTANTS ---
BASE_PLAYER_ATTACK_POWER = 8
BASE_PLAYER_ATTACK_VARIANCE = 2
BASE_PLAYER_CRIT_CHANCE = 0.1
BASE_PLAYER_CRIT_MULTIPLIER = 1.5

# --- LEVELING CONSTANTS ---
BASE_XP_TO_LEVEL_UP = 100
XP_SCALE_FACTOR = 1.5
HP_GAIN_PER_LEVEL = 15
ATTACK_GAIN_PER_LEVEL = 3
CRIT_CHANCE_GAIN_PER_LEVEL = 0.015

class Character:
    """Base class for player and monsters."""
    def __init__(self, name, hp, attack_power, attack_variance, crit_chance, crit_multiplier, defense):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack_power = attack_power
        self.attack_variance = attack_variance
        self.crit_chance = crit_chance
        self.crit_multiplier = crit_multiplier
        self.defense = defense
        self.status_effects = []

    def is_alive(self):
        return self.hp > 0

    def apply_and_tick_status_effects(self):
        is_stunned = False
        for effect in list(self.status_effects):
            if effect['type'] == 'dot':
                damage = effect['damage']
                self.hp -= damage
                print(effect['message_tick'].format(damage=damage))
            elif effect['type'] == 'control' and effect['name'] == 'Stun':
                is_stunned = True

            effect['duration'] -= 1
            if effect['duration'] <= 0:
                print(effect.get('message_wear_off', f"The {effect['name']} wears off."))
                self.status_effects.remove(effect)
        return is_stunned

class Player(Character):
    """Represents the player character."""
    def __init__(self, name, character_class, game_data: GameData):
        class_data = game_data.GAME_DATA['character_classes'][character_class]
        stats = class_data['starting_stats']

        super().__init__(
            name=name,
            hp=stats['max_hp'],
            attack_power=stats['attack_power'],
            attack_variance=stats['attack_variance'],
            crit_chance=stats['crit_chance'],
            crit_multiplier=stats['crit_multiplier'],
            defense=0
        )

        self.character_class = character_class
        self.game_data = game_data
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = self._calculate_xp_for_next_level()
        self.gold = 75
        self.inventory = []
        self.keychain = []
        self.stash = []
        self.max_inventory_slots = 5
        self.equipment = {
            "weapon": None, "shield": None, "helmet": None,
            "armor": None, "cloak": None, "misc": []
        }
        self.quests = {}
        self.reputation = {}
        self.skill_points = 0
        self.unlocked_skills = []
        self.effects = []
        self.attack_bonus = 0

        self._initialize_starting_equipment(class_data['starting_equipment'])
        self.recalculate_stats()

    def _initialize_starting_equipment(self, equipment_names):
        for item_name in equipment_names:
            item_def = self.game_data.get_item_by_name(item_name)
            if item_def:
                self.inventory.append(copy.deepcopy(item_def))

    def _calculate_xp_for_next_level(self):
        return int(BASE_XP_TO_LEVEL_UP * (XP_SCALE_FACTOR ** (self.level - 1)))

    def add_xp(self, amount):
        self.xp += amount
        print(f"You gained {amount} experience points!")
        self._check_for_level_up()

    def _check_for_level_up(self):
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self._level_up()
            self.xp_to_next_level = self._calculate_xp_for_next_level()

    def _level_up(self):
        self.level += 1
        self.skill_points += 1
        old_max_hp = self.max_hp
        self.max_hp += HP_GAIN_PER_LEVEL
        self.hp = self.max_hp
        self.attack_power += ATTACK_GAIN_PER_LEVEL
        self.crit_chance = min(1.0, self.crit_chance + CRIT_CHANCE_GAIN_PER_LEVEL)

        print("\n" + "#" * 50)
        print(f"      CONGRATULATIONS! YOU REACHED LEVEL {self.level}!              ")
        print(f"Your Max HP increased from {old_max_hp} to {self.max_hp}!")
        print(f"Your Attack Power increased to {self.attack_power}!")
        print(f"Your Critical Chance increased to {self.crit_chance*100:.0f}%!")
        print(f"You have gained a skill point! You now have {self.skill_points} skill point(s).")
        print(f"You feel fully revitalized!")
        print("#" * 50)

        self.recalculate_stats()

    def recalculate_stats(self):
        # Base stats from level
        self.attack_power = BASE_PLAYER_ATTACK_POWER + ((self.level - 1) * ATTACK_GAIN_PER_LEVEL) + self.attack_bonus

        # Equipment stats
        total_defense = 0
        if self.equipment['weapon']:
            self.attack_power += self.equipment['weapon'].get('damage', 0)

        for slot in ["shield", "helmet", "armor", "cloak"]:
            if self.equipment[slot]:
                total_defense += self.equipment[slot].get('defense', 0)

        for item in self.equipment['misc']:
            total_defense += item.get('defense', 0)
            if item.get('effect_type') == 'strength_boost':
                self.attack_power += item.get('effect_value', 0)

        self.defense = total_defense

    def equip(self, item_to_equip):
        item_type = item_to_equip.get('type')
        if item_type == 'weapon':
            self.equipment['weapon'] = item_to_equip
        elif item_type == 'shield':
            self.equipment['shield'] = item_to_equip
        elif item_type == 'armor':
            subtype = item_to_equip.get('subtype', 'body_armor')
            if subtype == 'body_armor':
                self.equipment['armor'] = item_to_equip
            elif subtype in self.equipment:
                self.equipment[subtype] = item_to_equip
            else:
                 print(f"Cannot equip armor of unknown subtype: {subtype}")
        elif item_type == 'equipment':
            self.equipment['misc'].append(item_to_equip)
        else:
            print(f"Cannot equip item of type: {item_type}")
            return

        print(f"You equip {add_article(item_to_equip['name'])}.")
        self.recalculate_stats()
        print(f"Your attack power is now {self.attack_power}.")
        print(f"Your total defense is now {self.defense}.")

    def use_item(self, item, in_combat=False):
        # Migrating process_item_use logic here
        print(f"You use {add_article(item['name'])}.")
        if item in self.inventory:
            self.inventory.remove(item)

class Monster(Character):
    """Represents a monster."""
    def __init__(self, monster_data):
        super().__init__(
            name=monster_data['name'],
            hp=monster_data['health'],
            attack_power=monster_data['damage'],
            attack_variance=monster_data.get('damage_variance', 0),
            crit_chance=monster_data.get('crit_chance', 0.0),
            crit_multiplier=monster_data.get('crit_multiplier', 1.0),
            defense=monster_data.get('defense', 0)
        )
        self.xp_reward = monster_data.get('xp_reward', 10)
        self.gold_drop = monster_data.get('gold_drop', [0, 0])
        self.item_drop = monster_data.get('item_drop')
        self.description = monster_data.get('description', '')

    def get_gold_dropped(self):
        return random.randint(self.gold_drop[0], self.gold_drop[1])
