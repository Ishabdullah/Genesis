#!/bin/bash
# Genesis Reasoning Test Suite
# Tests multi-step reasoning, pseudocode, and thinking traces

echo "🧬 Genesis Reasoning System Test Suite"
echo "======================================="
echo ""

# Test 1: Multi-Step Math Word Problem
echo "Test 1: Multi-Step Reasoning (Cats & Mice Problem)"
echo "---------------------------------------------------"
cat > /tmp/test_reasoning_1.txt << 'EOF'
If 3 cats catch 3 mice in 3 minutes, how many cats do you need to catch 100 mice in 100 minutes?
#exit
EOF
echo "Running test..."
timeout 45 python genesis.py < /tmp/test_reasoning_1.txt 2>/dev/null | grep -A 80 "Thinking"
echo ""
echo ""

# Test 2: Logic Problem
echo "Test 2: Logical Reasoning (Transitivity)"
echo "-----------------------------------------"
cat > /tmp/test_reasoning_2.txt << 'EOF'
If A implies B and B implies C, does A imply C? Explain why.
#exit
EOF
echo "Running test..."
timeout 45 python genesis.py < /tmp/test_reasoning_2.txt 2>/dev/null | grep -A 80 "Thinking"
echo ""
echo ""

# Test 3: Programming with Pseudocode
echo "Test 3: Programming Problem (Pseudocode Expected)"
echo "--------------------------------------------------"
cat > /tmp/test_reasoning_3.txt << 'EOF'
Write a Python function that returns the sum of even numbers in a list.
#exit
EOF
echo "Running test..."
timeout 45 python genesis.py < /tmp/test_reasoning_3.txt 2>/dev/null | grep -A 100 "Thinking"
echo ""
echo ""

# Test 4: Design Problem
echo "Test 4: System Design Reasoning"
echo "--------------------------------"
cat > /tmp/test_reasoning_4.txt << 'EOF'
Explain how you'd design a memory system for an AI assistant like yourself.
#exit
EOF
echo "Running test..."
timeout 45 python genesis.py < /tmp/test_reasoning_4.txt 2>/dev/null | grep -A 80 "Thinking"
echo ""
echo ""

# Test 5: Algorithm Problem
echo "Test 5: Algorithm Design with Pseudocode"
echo "-----------------------------------------"
cat > /tmp/test_reasoning_5.txt << 'EOF'
Design an algorithm to find the longest palindrome in a string.
#exit
EOF
echo "Running test..."
timeout 45 python genesis.py < /tmp/test_reasoning_5.txt 2>/dev/null | grep -A 80 "Thinking"
echo ""
echo ""

echo "======================================="
echo "Reasoning Test Suite Complete"
echo ""
echo "Expected Behaviors:"
echo "1. ✓ [Thinking...] section appears before answer"
echo "2. ✓ Multi-step reasoning displayed (Step 1, 2, 3...)"
echo "3. ✓ Pseudocode shown for programming problems"
echo "4. ✓ Final Answer clearly separated"
echo "5. ✓ Confidence score displayed"
echo "6. ✓ Validation warnings if needed"
echo ""
echo "Check Output Above:"
echo "- Does reasoning appear step-by-step?"
echo "- Is pseudocode formatted correctly?"
echo "- Is Final Answer section visible?"
echo "- Are steps logical and helpful?"
echo ""
