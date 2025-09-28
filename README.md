# The Infinite Dungeon ⚔️

Welcome to The Infinite Dungeon, a feature-rich, command-line rogue-like RPG. Dive into a procedurally generated world where every playthrough is unique. Battle a vast bestiary of monsters, solve clever puzzles, interact with NPCs, complete quests, manage your equipment, and seek legendary artifacts to conquer the dungeon's greatest challenges.

## 🎮 How to Play

Your goal is to become a legend by exploring the dungeon, growing stronger, and ultimately finding a legendary Winning Item. Acquiring such an artifact will summon a powerful guardian you must defeat to truly master the dungeon.

## Core Gameplay

### 🧭 Exploring
The dungeon is an endless series of randomly generated rooms. Each room can contain monsters, items, hazards, NPCs, or puzzles. Pay attention to the descriptions!

### ⚔️ Combat
When you encounter a monster, combat is turn-based. You can attack, use items, or attempt to run. Defeating monsters grants you Gold and Experience Points (XP).

### 🔼 Leveling Up
Gaining enough XP will increase your Level, raising your Max HP, Attack Power, and Critical Hit Chance, and fully restoring your health.

### 🧩 Puzzles
Some rooms contain puzzles like riddles or mechanisms. Solving them can yield valuable rewards or open new paths.

### 📜 Quests
You'll find Quest Givers in special Inn rooms or wandering the dungeon. Completing their tasks provides significant rewards in Gold, XP, and unique items.

### 🤝 NPCs
Talk to characters you meet. Some are vendors who will buy and sell goods, while others may offer quests or useful information.

### 🎒 Equipment
Manage your inventory, equip better weapons, armor, shields, and cloaks to improve your attack and defense. Some items provide permanent stat boosts!

### 💾 Saving
You can save your progress at any time and load it from the main menu.

## Key Commands

The game is controlled by typing commands. Most can be shortened (e.g., `inv` for inventory).

### Movement & Interaction
- `go [direction]` or just `[direction]` - Move north, south, east, or west.
- `look` - Re-displays the description of the current room.
- `get [item name]` or `get item` - Pick up an item from the floor.
- `drop [item name]` - Drop an item from your inventory.
- `talk` or `talk [npc name]` - Interact with a character in the room.
- `unlock [direction] with [key name]` - Use a key to open a locked door.

### Inventory & Character
- `inventory` or `i` - View your stats, gold, inventory, and equipped items.
- `equip [item name]` - Equip a weapon, shield, armor, or cloak from your inventory.
- `unequip [item name]` - Unequip an item, returning it to your inventory.
- `equipped` - Shows a summary of only your equipped gear.
- `use [item name]` - Use a consumable item like a healing potion or a backpack to increase inventory space.
- `combine [item name]` - Combine two smaller items (like healing potions) into a larger one.
- `quests` - View the status of your active quests.

### Combat
- `attack` or `a` (or just press Enter) - Attack the monster in the room.
- `run` - Attempt to flee from combat (may fail).
- `use [item name]` - Use a consumable during your turn in combat.

### Puzzle Commands
- `answer [your guess]` - Submit an answer to a riddle.
- `pull [lever name]` - Pull a lever in a mechanism puzzle.
- `give [item name] to [target]` - Give an item to an object or NPC to solve a puzzle.

### Game Management
- `save` - Saves your current progress to savegame.json.
- `help` - Shows a list of available commands.
- `quit` - Exits the game.

## 🚀 Getting Started

You can run this game on your local machine with Python.

### Prerequisites
- You must have Python 3 installed. If you don't have it, download it from [python.org](https://python.org).
- You will need Git to clone the repository. If you don't have it, you can download it from [git-scm.com](https://git-scm.com).

### Running the Game

#### Quick Start
- **On Windows**: Double-click `build.bat` to run the game.
- **On macOS/Linux**: Open your terminal, make the script executable with `chmod +x build.sh`, then run `./build.sh`.

#### Manual Start
1. **Open Terminal**: Open your terminal or command prompt (e.g., cmd, PowerShell, Terminal).
   
2. **Clone the Repository**: Use git to download all the necessary game files (infinitedungeon.py, gamedata.json, etc.).
   ```bash
   git clone https://github.com/junglistloydee/infinitedungeon.git
   ```
3. **Navigate to the Directory**:
   ```bash
   cd infinitedungeon
   ```
4. **Run the Game**:
   ```bash
   python3 infinitedungeon.py
   ```
