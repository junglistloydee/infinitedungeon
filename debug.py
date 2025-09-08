import datetime
import json
import os

DEBUG_MODE_ENABLED = False  # Keep this as False by default. Your main script will control it.
DEBUG_LOG_FILE = None       # Will store the file object for the log

def initialize_debug_log(enabled_by_main_script=False):
    """Initializes a new debug log file with a timestamp."""
    global DEBUG_MODE_ENABLED, DEBUG_LOG_FILE
    DEBUG_MODE_ENABLED = enabled_by_main_script # Sync with the main script's DEBUG flag

    if DEBUG_MODE_ENABLED and DEBUG_LOG_FILE is None: # Only initialize if enabled and not already open
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"DEBUG_{timestamp}.txt"
        try:
            DEBUG_LOG_FILE = open(log_filename, 'w', encoding='utf-8')
            DEBUG_LOG_FILE.write(f"--- Debug Log Started: {datetime.datetime.now()} ---\n\n")
            DEBUG_LOG_FILE.flush() # Ensure it's written immediately
            debug_print(f"Debug log opened: {log_filename}") # Log to file
        except IOError as e:
            # Keep this console print for critical errors if the log file can't be opened
            print(f"Error: Could not open debug log file {log_filename}: {e}")
            DEBUG_LOG_FILE = None # Disable file logging if it fails
            DEBUG_MODE_ENABLED = False # Also disable debug mode if file can't be opened

def debug_print(message):
    """Writes a debug message to the log file if DEBUG_MODE_ENABLED is True and file is open."""
    if DEBUG_MODE_ENABLED and DEBUG_LOG_FILE:
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        formatted_message = f"{timestamp} {message}"
        DEBUG_LOG_FILE.write(formatted_message + "\n")
        DEBUG_LOG_FILE.flush() # Write to file immediately

def close_debug_log():
    """Closes the debug log file."""
    global DEBUG_LOG_FILE
    if DEBUG_LOG_FILE:
        debug_print("\n--- Debug Log Ended ---") # Log message before closing
        DEBUG_LOG_FILE.close()
        DEBUG_LOG_FILE = None

def debug_game_data_full_output(game_data):
    """Outputs the full GAME_DATA dictionary to the debug log."""
    if DEBUG_MODE_ENABLED and DEBUG_LOG_FILE:
        debug_print("\n--- Debug: Full GAME_DATA Contents ---")
        DEBUG_LOG_FILE.write(json.dumps(game_data, indent=2) + "\n")
        DEBUG_LOG_FILE.flush()
        debug_print("--- End Debug: Full GAME_DATA Contents ---\n")

def debug_game_data_load_check(game_data):
    """Debugs the initial loading of game data, specifically keys (summary)."""
    if DEBUG_MODE_ENABLED:
        debug_print("\n--- Debug: Initial Key Data Load Check (Summary) ---")
        for item in game_data.get('items', []):
            if item.get('type') == 'key':
                debug_print(f"    Loaded Key: {item.get('name')} | shop_price: {item.get('shop_price')}")
        debug_print("--- End Debug: Initial Key Data Load Check ---\n")

def debug_player_data(player_inventory, player_keychain, current_max_inventory_slots, player_gold, context_message="Current Player State"):
    """Outputs current inventory, keychain, and gold."""
    if DEBUG_MODE_ENABLED:
        debug_print(f"\n--- Debug: {context_message} ---")
        debug_print(f"    Gold: {player_gold}")
        debug_print(f"    Inventory ({len(player_inventory)}/{current_max_inventory_slots}):")
        if player_inventory:
            for item in player_inventory:
                debug_print(f"        - {item.get('name', 'Unnamed Item')} (Type: {item.get('type')}, Price: {item.get('shop_price')})")
        else:
            debug_print("        (Empty)")

        debug_print("    Keychain:")
        if player_keychain:
            for key in player_keychain:
                debug_print(f"        - {key.get('name', 'Unnamed Key')} (Type: {key.get('key_type')}, Price: {key.get('shop_price')})")
        else:
            debug_print("        (Empty)")
        debug_print("--- End Debug: Player Data ---\n")


def debug_keychain_populate(player_keychain, sellable_items_keychain_placeholder):
    """Debugs the process of populating sellable_items_keychain from player_keychain."""
    if DEBUG_MODE_ENABLED:
        debug_print("\n--- Debug: Populating Sellable Keychain (Shop Logic) ---")
        for item_dict in player_keychain:
            item_name = item_dict.get('name', 'UNKNOWN ITEM')
            shop_price = item_dict.get('shop_price')
            item_type = item_dict.get('type')

            debug_print(f"    Checking key: {item_name} (Type: {item_type}, Shop Price: {shop_price})")

            if shop_price is not None and item_type != 'winning_item':
                debug_print(f"        -> (Would be) Added '{item_name}' to sellable keychain.")
            else:
                debug_print(f"        -> Skipped '{item_name}': Price is {shop_price} or type is '{item_type}'.")
        debug_print("--- End Debug: Populating Sellable Keychain ---\n")

def debug_key_acquisition(key_object, context_message):
    """Debugs key acquisition by printing the key object."""
    if DEBUG_MODE_ENABLED:
        debug_print(f"--- Debug: Key acquired via {context_message}. Contents: {key_object} ---")