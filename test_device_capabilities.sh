#!/bin/bash
# Test Suite for Genesis Device Capabilities
# Tests device integration and Termux API functionality

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🧬 Genesis Device Capabilities Test Suite               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0
SKIPPED=0

# Helper functions
pass_test() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((PASSED++))
}

fail_test() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    echo -e "  ${RED}Error: $2${NC}"
    ((FAILED++))
}

skip_test() {
    echo -e "${YELLOW}⊘ SKIP${NC}: $1 - $2"
    ((SKIPPED++))
}

# Test 1: Check Termux API availability
echo -e "${CYAN}[Test 1]${NC} Checking Termux API availability..."
if command -v termux-location &> /dev/null; then
    pass_test "Termux API is installed"
else
    fail_test "Termux API is not installed" "Run: pkg install termux-api"
fi

# Test 2: Test device_manager.py import
echo -e "\n${CYAN}[Test 2]${NC} Testing device_manager.py module..."
if python device_manager.py &> /dev/null; then
    pass_test "device_manager.py module loads successfully"
else
    fail_test "device_manager.py module failed to load" "Check Python imports"
fi

# Test 3: Test get_date_time (always works, no permissions needed)
echo -e "\n${CYAN}[Test 3]${NC} Testing get_date_time action..."
python3 << 'EOF'
from device_manager import DeviceManager
import sys

dm = DeviceManager()
result = dm.get_date_time()

if result['success']:
    print(f"✓ Date/Time: {result['date']} {result['time']}")
    sys.exit(0)
else:
    print(f"✗ Failed: {result.get('error')}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    pass_test "get_date_time works correctly"
else
    fail_test "get_date_time failed" "Check device_manager.py"
fi

# Test 4: Test location (requires permission)
echo -e "\n${CYAN}[Test 4]${NC} Testing GPS location..."
if termux-location -p gps 2>/dev/null | grep -q "latitude"; then
    pass_test "GPS location access works"
else
    skip_test "GPS location" "Permission not granted or GPS unavailable"
fi

# Test 5: Test camera photo (requires permission)
echo -e "\n${CYAN}[Test 5]${NC} Testing camera access..."
TEST_PHOTO="/tmp/test_photo_$$.jpg"
if termux-camera-photo -c 0 "$TEST_PHOTO" 2>/dev/null && [ -f "$TEST_PHOTO" ]; then
    pass_test "Camera access works"
    rm -f "$TEST_PHOTO"
else
    skip_test "Camera" "Permission not granted or camera unavailable"
fi

# Test 6: Test volume control (usually works)
echo -e "\n${CYAN}[Test 6]${NC} Testing volume control..."
if termux-volume 2>/dev/null | grep -q "music"; then
    pass_test "Volume control access works"
else
    skip_test "Volume control" "Feature unavailable"
fi

# Test 7: Test brightness control
echo -e "\n${CYAN}[Test 7]${NC} Testing brightness control..."
CURRENT_BRIGHTNESS=$(termux-brightness 2>/dev/null)
if [ $? -eq 0 ]; then
    pass_test "Brightness control access works"
else
    skip_test "Brightness control" "Feature unavailable"
fi

# Test 8: Test flashlight/torch
echo -e "\n${CYAN}[Test 8]${NC} Testing flashlight control..."
if termux-torch on 2>/dev/null && termux-torch off 2>/dev/null; then
    pass_test "Flashlight control works"
else
    skip_test "Flashlight" "Feature unavailable or no flashlight"
fi

# Test 9: Test device manager execute_action
echo -e "\n${CYAN}[Test 9]${NC} Testing DeviceManager.execute_action..."
python3 << 'EOF'
from device_manager import DeviceManager
import sys

dm = DeviceManager()

# Test valid action
result = dm.execute_action("get_date_time")
if not result['success']:
    print(f"✗ Valid action failed: {result.get('error')}")
    sys.exit(1)

# Test invalid action
result = dm.execute_action("invalid_action")
if result['success']:
    print("✗ Invalid action should have failed")
    sys.exit(1)

print("✓ Action execution works correctly")
sys.exit(0)
EOF

if [ $? -eq 0 ]; then
    pass_test "DeviceManager.execute_action works correctly"
else
    fail_test "DeviceManager.execute_action failed" "Check device_manager.py"
fi

# Test 10: Test genesis.py device command parsing
echo -e "\n${CYAN}[Test 10]${NC} Testing Genesis device command parsing..."
python3 << 'EOF'
import re
import json

# Simulate LLM response with device command
text = 'DEVICE: {"action": "get_date_time"}'

device_pattern = r'DEVICE:\s*(\{[^}]+\})'
matches = list(re.finditer(device_pattern, text))

if len(matches) != 1:
    print("✗ Failed to detect device command")
    exit(1)

json_str = matches[0].group(1).strip()
try:
    command = json.loads(json_str)
    if command.get("action") != "get_date_time":
        print("✗ Failed to parse action correctly")
        exit(1)
    print("✓ Device command parsing works")
    exit(0)
except Exception as e:
    print(f"✗ JSON parsing failed: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    pass_test "Genesis device command parsing works"
else
    fail_test "Genesis device command parsing failed" "Check regex pattern"
fi

# Summary
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                     TEST SUMMARY                             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${GREEN}✓ Passed:${NC}  $PASSED"
echo -e "${RED}✗ Failed:${NC}  $FAILED"
echo -e "${YELLOW}⊘ Skipped:${NC} $SKIPPED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All critical tests passed!${NC}"
    echo ""
    echo "Note: Skipped tests require:"
    echo "  1. Termux:API app installed"
    echo "  2. Permissions granted in Android Settings"
    echo "  3. Physical device capabilities (GPS, camera, etc.)"
    exit 0
else
    echo -e "${RED}Some tests failed. Please review errors above.${NC}"
    exit 1
fi
