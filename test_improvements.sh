#!/bin/bash
# Genesis Improvements Test Suite
# Tests all 6 improvement areas

echo "🧬 Genesis Improvements Test Suite"
echo "===================================="
echo ""

# Test 1: Identity
echo "Test 1: Identity Check"
echo "-----------------------"
echo -e "Genesis, identify yourself.\n#exit" | timeout 10 python genesis.py 2>/dev/null | grep -A 2 "Genesis:"
echo ""

# Test 2: Math
echo "Test 2: Simple Math (should answer 62)"
echo "---------------------------------------"
echo -e "What is 8 × 7 + 6?\n#exit" | timeout 10 python genesis.py 2>/dev/null | grep -A 2 "Genesis:"
echo ""

# Test 3: String Reversal
echo "Test 3: String Reversal (should be 'siseneG')"
echo "----------------------------------------------"
echo -e "Reverse this string: Genesis\n#exit" | timeout 10 python genesis.py 2>/dev/null | grep -A 2 "Genesis:"
echo ""

# Test 4: Code Execution with Function Persistence
echo "Test 4: Code Persistence (function should work across blocks)"
echo "--------------------------------------------------------------"
cat > /tmp/test_genesis_code.txt << 'EOF'
Write a Python function that adds two numbers, then call it with 3 and 5.
#exit
EOF
timeout 35 python genesis.py < /tmp/test_genesis_code.txt 2>/dev/null | tail -20
echo ""

# Test 5: Memory Recall
echo "Test 5: Memory Storage and Recall"
echo "----------------------------------"
echo "First, storing preference..."
cat > /tmp/test_genesis_memory.txt << 'EOF'
Remember that my favorite programming language is Python.
#exit
EOF
timeout 35 python genesis.py < /tmp/test_genesis_memory.txt 2>/dev/null | grep -A 3 "Genesis:"
echo ""
echo "Now testing recall (checking learning memory)..."
python -c "
from learning_memory import LearningMemory
memory = LearningMemory()
convs = memory.get_relevant_context('favorite programming language', max_results=1)
if convs:
    print('✓ Memory contains conversation about favorite language')
    print(f'  User said: {convs[0].get(\"user_input\", \"\")[:60]}...')
else:
    print('✗ No relevant memory found')
"
echo ""

# Test 6: Debugging Ability (intentional error)
echo "Test 6: Debug Broken Code"
echo "--------------------------"
cat > /tmp/test_genesis_debug.txt << 'EOF'
Fix this code: def add_numbers(a,b): return a +
#exit
EOF
timeout 35 python genesis.py < /tmp/test_genesis_debug.txt 2>/dev/null | grep -A 10 "Genesis:"
echo ""

echo "===================================="
echo "Test Suite Complete"
echo ""
echo "Expected Results:"
echo "1. Identity: Should show Genesis identity instantly"
echo "2. Math: Should answer 62 (8×7+6 = 56+6 = 62)"
echo "3. String: Should reverse to 'siseneG'"
echo "4. Code: Function should persist and execute successfully"
echo "5. Memory: Should store and find conversation"
echo "6. Debug: Should identify syntax error and suggest fix"
echo ""
