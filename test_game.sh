#!/bin/bash

export SDL_AUDIODRIVER=dummy

# Test Case 1: Start a new game as a Reaver and check initial stats
echo -e "1\nTestReaver\n1\nleave\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nsave\nquit\n7\n" | python3 infinitedungeon.py > test_output_1.txt

if grep -q "You have chosen the path of the Reaver" test_output_1.txt; then
    echo "Test Case 1 Passed: Reaver class chosen successfully."
else
    echo "Test Case 1 Failed: Reaver class not chosen."
fi

# Test Case 2: Start a new game as a Whisper and check initial stats
echo -e "1\nTestWhisper\n2\nleave\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nsave\nquit\n7\n" | python3 infinitedungeon.py > test_output_2.txt

if grep -q "You have chosen the path of the Whisper" test_output_2.txt; then
    echo "Test Case 2 Passed: Whisper class chosen successfully."
else
    echo "Test Case 2 Failed: Whisper class not chosen."
fi

# Test Case 3: Start a new game as a Prodigy and check initial stats
echo -e "1\nTestProdigy\n3\nleave\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nsave\nquit\n7\n" | python3 infinitedungeon.py > test_output_3.txt

if grep -q "You have chosen the path of the Prodigy" test_output_3.txt; then
    echo "Test Case 3 Passed: Prodigy class chosen successfully."
else
    echo "Test Case 3 Failed: Prodigy class not chosen."
fi

# Test Case 4: Start a new game as a Oracle and check initial stats
echo -e "1\nTestOracle\n4\nleave\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nsave\nquit\n7\n" | python3 infinitedungeon.py > test_output_4.txt

if grep -q "You have chosen the path of the Oracle" test_output_4.txt; then
    echo "Test Case 4 Passed: Oracle class chosen successfully."
else
    echo "Test Case 4 Failed: Oracle class not chosen."
fi

# Clean up
rm test_output_*.txt

# Test Case 5: Buy Hideout Key and enter hideout
echo -e "1\nTestHider\n1\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nohinn\ntalk Key Vendor\nbuy\n1\nexit\nenter hideout\nleave\nleave\nquit\n7\n" | python3 infinitedungeon.py > test_output_5.txt

if grep -q "You have chosen the path of the Reaver" test_output_5.txt && grep -q "You bought a Hideout Key" test_output_5.txt && grep -q "A quiet, personal space." test_output_5.txt; then
    echo "Test Case 5 Passed: Hideout functionality verified."
else
    echo "Test Case 5 Failed: Hideout functionality not verified."
fi

# Test Case 6: Pressure plate puzzle
echo -e "4\n42\nTestPress\n1\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\nattack\ndrop battle-worn axe\npress\nget battle-worn axe\nequip battle-worn axe\npress\nnorth\nquit\n7\n" | python3 infinitedungeon.py > test_output_6.txt

if grep -q "You try to press the plate, but nothing happens." test_output_6.txt && grep -q "You press the battle-worn axe onto the pressure plate." test_output_6.txt && grep -q "A new path to the north has opened!" test_output_6.txt; then
    echo "Test Case 6 Passed: Pressure plate puzzle solved successfully."
else
    echo "Test Case 6 Failed: Pressure plate puzzle not solved."
fi
