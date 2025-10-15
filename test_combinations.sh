#!/bin/bash

export SDL_AUDIODRIVER=dummy

# This script will:
# 1. Start a new game as a Reaver.
# 2. Defeat any monster that might be in the starting room.
# 3. Use 'ohvendor' to summon the vendor.
# 4. Buy the components for the Shadow-Woven Aegis.
# 5. Combine the item.
# 6. Equip the item.
# 7. Move to a new room to find a monster.
# 8. Fight the monster to trigger and verify the evasion effect.
# 9. Quit the game.

echo -e "1\nTestCrafter\n1\nattack\nattack\nattack\nattack\nattack\nattack\nohvendor\nbuy\n10\nbuy\n11\nexit\ncombine Shadow-Woven Aegis\nequip Shadow-Woven Aegis\neast\neast\neast\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nquit\n7\n" | python3 infinitedungeon.py > test_output_combinations.txt

# --- Verification ---

# Check for successful crafting
if grep -q "You successfully combined the items to create a Shadow-Woven Aegis" test_output_combinations.txt; then
    echo "Test Case Combinations Passed: Shadow-Woven Aegis crafted successfully."
else
    echo "Test Case Combinations Failed: Shadow-Woven Aegis not crafted."
fi

# Check for item effects
echo "--- Verifying Item Effects ---"
if grep -q "dodge" test_output_combinations.txt; then
    echo "Evasion effect verified."
else
    echo "Evasion effect NOT verified."
fi
