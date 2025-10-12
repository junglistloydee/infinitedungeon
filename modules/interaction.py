import random
import time
import copy
from modules.character import Player
from modules.game_data import GameData
from sound import Sound
from modules.utils import add_article

SELL_PRICE_MULTIPLIER = 0.5

def get_quest_by_id(game_data: GameData, quest_id):
    for quest in game_data.QUESTS:
        if quest['id'] == quest_id:
            return quest
    return None

def get_player_quest_status(player: Player, game_data: GameData, quest_id):
    if quest_id not in player.quests:
        return 'not_started'
    quest_data = player.quests[quest_id]
    if quest_data['status'] == 'completed':
        return 'completed'
    quest_def = get_quest_by_id(game_data, quest_id)
    if quest_def:
        if quest_def['type'] in ['fetch_item', 'defeat_any_monster', 'defeat_monster']:
            if quest_data.get('current_count', 0) >= quest_def.get('target_count', 1):
                return 'complete_ready'
        elif quest_def['type'] == 'find_npc':
            if quest_data.get('found_npc'):
                return 'complete_ready'
    return 'active'

def has_player_enough_items(player: Player, item_name, count):
    current_count = sum(1 for item in player.inventory if item['name'].lower() == item_name.lower())
    return current_count >= count

def remove_items_from_inventory(player: Player, item_name, count):
    removed_count = 0
    items_to_keep = []
    for item in player.inventory:
        if item['name'].lower() == item_name.lower() and removed_count < count:
            removed_count += 1
        else:
            items_to_keep.append(item)
    player.inventory[:] = items_to_keep
    return removed_count == count

def update_reputation(player: Player, faction_id, amount):
    if faction_id not in player.reputation:
        player.reputation[faction_id] = 0
    player.reputation[faction_id] += amount
    print(f"Your reputation with {faction_id} has changed by {amount}.")

def handle_shop(player: Player, vendor_data: dict, game_data: GameData, sound_manager: Sound):
    vendor_name = vendor_data['name']
    shop_stock_names = vendor_data.get('shop_stock', [])
    shop_dialogues = vendor_data.get('dialogues', ["What're ya buyin'?", "Come back anytime!"])
    shop_items = [game_data.get_item_by_name(name.lower()) for name in shop_stock_names]
    shop_items = [item for item in shop_items if item and item.get('shop_price') is not None]

    sound_manager.stop_music()
    sound_manager.play_music('vendor_music')
    print(f"\n--- {vendor_name}'s Shop ---")
    print(random.choice(shop_dialogues))

    while True:
        print(f"\nYour Gold: {player.gold}")
        print(f"Your Inventory: ({len(player.inventory)}/{player.max_inventory_slots})")
        print("Shop commands: buy / sell / exit")
        shop_command_input = input("Shop Action> ").lower().strip()
        parts = shop_command_input.split()
        if not parts: continue
        verb = parts[0]
        if verb == "buy":
            # ... (full buy logic from original) ...
            pass
        elif verb == "sell":
            # ... (full sell logic from original) ...
            pass
        elif verb == "exit":
            print(random.choice(shop_dialogues))
            sound_manager.stop_music()
            sound_manager.play_music('ambient_music')
            return
        else:
            print("Invalid shop command.")

def handle_inn(player: Player, game_data: GameData, sound_manager: Sound):
    sound_manager.stop_music()
    sound_manager.play_music('inn_music')
    print("\n--- The Hearth and Home Inn ---")
    while True:
        print(f"\nYour HP: {player.hp}/{player.max_hp}")
        print("Inn commands: rest / talk / stash / unstash / leave")
        inn_command_input = input("Inn Action> ").lower().strip()
        parts = inn_command_input.split()
        if not parts: continue
        verb = parts[0]
        if verb == "rest":
            player.hp = player.max_hp
            print("You are fully healed.")
        elif verb == "leave":
            print("You step out of the inn.")
            sound_manager.stop_music()
            sound_manager.play_music('ambient_music')
            return
        else:
            print("Invalid inn command.")

def handle_quest_giver(player: Player, npc: dict, game_data: GameData):
    print(f"\nYou approach {npc['name']}.")

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

    quest_status = get_player_quest_status(player, game_data, npc_quest_id)
    quest_def = get_quest_by_id(game_data, npc_quest_id)

    if quest_status == 'not_started' and quest_def:
        if player.level >= quest_def.get('required_level', 1) and (not quest_def.get('prerequisite_quest') or get_player_quest_status(player, game_data, quest_def.get('prerequisite_quest')) == 'completed'):
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
            if quest_def['type'] == 'fetch_item' and not has_player_enough_items(player, quest_def['target_item'], quest_def['target_count']):
                print("You don't have the required items!")
            else:
                if quest_def['type'] == 'fetch_item':
                    remove_items_from_inventory(player, quest_def['target_item'], quest_def['target_count'])
                    print(f"You hand over {quest_def['target_count']} {quest_def['target_item']}(s).")

                player.gold += quest_def.get('reward_gold', 0)
                player.add_xp(quest_def.get('reward_xp', 0))
                print(f"Quest complete! You receive {quest_def.get('reward_gold', 0)} gold.")

                reward_item_name = quest_def.get('reward_item')
                if reward_item_name:
                    item_def = game_data.get_item_by_name(reward_item_name)
                    if item_def:
                        if len(player.inventory) < player.max_inventory_slots:
                            player.inventory.append(copy.deepcopy(item_def))
                            print(f"You also receive {add_article(item_def['name'])}!")
                        else:
                            print(f"You would have received an item, but your inventory is full!")

                player.quests[npc_quest_id]['status'] = 'completed'

                if 'rewards' in quest_def:
                    if 'reputation_gain' in quest_def['rewards']:
                        faction_id = quest_def['rewards']['reputation_gain']['faction']
                        amount = quest_def['rewards']['reputation_gain']['amount']
                        update_reputation(player, faction_id, amount)
                    if 'reputation_loss' in quest_def['rewards']:
                        faction_id = quest_def['rewards']['reputation_loss']['faction']
                        amount = quest_def['rewards']['reputation_loss']['amount']
                        update_reputation(player, faction_id, -amount)
    elif quest_status == 'completed' and quest_def:
        print(f"{npc['name']}: '{quest_def.get('dialogue_complete_turn_in', 'Thank you for your help.')}'")

def handle_gambler(player: Player, gambler_data: dict):
    gambler_name = gambler_data.get('name', 'the Gambler')
    print(f"\n--- {gambler_name}'s Game of Chance ---")
    print(f"'{random.choice(gambler_data.get('dialogues', ['Care to try your luck?']))}'")

    while True:
        print(f"\nYour Gold: {player.gold}")
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
            elif bet_amount > player.gold:
                print("You don't have enough gold for that bet.")
            else:
                player.gold -= bet_amount
                player_roll = random.randint(1, 6) + random.randint(1, 6)
                gambler_roll = random.randint(1, 6) + random.randint(1, 6)
                print("The dice are rolling...")
                time.sleep(1)
                print(f"You rolled a {player_roll}.")
                time.sleep(0.5)
                print(f"The Gambler rolled a {gambler_roll}.")

                if player_roll > gambler_roll:
                    winnings = bet_amount * 2
                    player.gold += winnings
                    print(f"You win! You receive {winnings} gold.")
                elif gambler_roll > player_roll:
                    print("You lose! The Gambler takes your bet.")
                else:
                    player.gold += bet_amount
                    print("It's a draw! Your bet is returned.")
        else:
            print("Invalid command.")
