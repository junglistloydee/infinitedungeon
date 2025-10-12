import random
import copy
from modules.game_data import GameData
from modules.utils import add_article

class Room:
    """Represents a single, randomly generated room in the dungeon."""
    def __init__(self, game_data: GameData, player_current_level, player_quests, load_from_save=False, entry_direction=None):
        self.game_data = game_data
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
        self.crafting_station = None

        if not load_from_save:
            self._generate_new_room(player_current_level, player_quests, entry_direction)

    def _generate_new_room(self, player_current_level, player_quests, entry_direction):
        if random.random() < self.game_data.GAME_DATA.get('inn_spawn_chance', 0.04):
            self.is_inn = True
            self.description = "You find yourself in a cozy, bustling inn. A warm fire crackles in the hearth."
            self.exits = {"south": True}
            return

        adj = random.choice(self.game_data.ADJECTIVES)
        room_type = random.choice(self.game_data.ROOM_TYPES)
        detail = random.choice(self.game_data.DETAILS)
        self.description = f"You are in a {adj} {room_type}. You notice {detail}."

        self._generate_exits(entry_direction)
        self._populate_room_content(player_current_level, player_quests)

    def _generate_exits(self, entry_direction):
        all_possible_directions = ["north", "south", "east", "west"]
        opposites = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
        available_directions = all_possible_directions[:]

        if entry_direction:
            back_direction = opposites[entry_direction]
            self.exits[back_direction] = True
            if back_direction in available_directions:
                available_directions.remove(back_direction)

        if not self.exits:
            guaranteed_exit = random.choice(available_directions)
            self.exits[guaranteed_exit] = True
            available_directions.remove(guaranteed_exit)

        for direction in available_directions:
            if random.random() < 0.3:
                self.exits[direction] = True

    def _populate_room_content(self, player_level, player_quests):
        content_roll = random.random()

        if content_roll < 0.25:
            eligible_monsters = [m for m in self.game_data.MONSTERS if abs(m.get('level', 1) - player_level) <= 2]
            if eligible_monsters:
                self.monster = dict(random.choice(eligible_monsters))
        elif content_roll < 0.5:
            self.item = self._get_random_item(player_level)
        elif content_roll < 0.6 and self.game_data.NPCs:
            self.npc = dict(random.choice(self.game_data.NPCs))
            self.npc['talked_to'] = False

    def _get_random_item(self, player_level):
        eligible_items = [i for i in self.game_data.ALL_ITEMS if i.get('type') != 'winning_item']
        if eligible_items:
            chosen_item = random.choice(eligible_items)
            return self._scale_item_for_player_level(chosen_item, player_level)
        return None

    def _scale_item_for_player_level(self, item, player_level):
        if not item or item.get('type') not in ['weapon', 'shield', 'armor']:
            return item
        bonus = player_level // 3
        if bonus > 0:
            scaled_item = copy.deepcopy(item)
            scaled_item['name'] = f"{scaled_item['name']}+{bonus}"
            if 'damage' in scaled_item:
                scaled_item['damage'] = scaled_item.get('damage', 0) + bonus
            if 'defense' in scaled_item:
                scaled_item['defense'] = scaled_item.get('defense', 0) + bonus
            return scaled_item
        return item

    def show_description(self, direction_history=None):
        print(self.description)
        if self.item:
            print(f"You see {add_article(self.item['name'])} on the floor.")
        if self.monster:
            print(f"A {self.monster['name']} {self.monster.get('description', '')}")
        if self.npc:
            print(f"You spot {self.npc['name']}: {self.npc.get('description', '')}")

        exits_str = ", ".join(self.exits.keys())
        print(f"Exits: {exits_str}")
