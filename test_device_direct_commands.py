#!/usr/bin/env python3
"""
Quick test for device direct commands
"""

# Test the pattern matching logic
test_commands = [
    "turn on my flashlight",
    "turn on the flashlight",
    "flashlight on",
    "turn off flashlight",
    "where am i",
    "what's my location",
    "what time is it",
    "what's the date",
    "take a photo",
    "take a selfie",
    "set volume to 10",
    "increase volume",
    "set brightness to 150",
    "record 5 seconds of audio"
]

# Simulate the trigger matching
flashlight_on_triggers = ["turn on flashlight", "turn on torch", "turn on the flashlight",
                           "turn on the torch", "flashlight on", "torch on", "enable flashlight",
                           "turn flashlight on", "turn torch on"]
flashlight_off_triggers = ["turn off flashlight", "turn off torch", "turn off the flashlight",
                            "turn off the torch", "flashlight off", "torch off", "disable flashlight",
                            "turn flashlight off", "turn torch off"]
location_triggers = ["where am i", "what is my location", "what's my location",
                   "my location", "current location", "gps location", "my coordinates"]
time_triggers = ["what time is it", "what's the time", "current time", "tell me the time"]
date_triggers = ["what is the date", "what's the date", "today's date", "current date",
                "what day is it", "what day is today"]
photo_triggers = ["take a photo", "take photo", "take a picture", "take picture",
                 "capture photo", "capture image"]
selfie_triggers = ["take a selfie", "take selfie", "selfie"]

print("Testing device command pattern matching:\n")

for cmd in test_commands:
    input_lower = cmd.lower().strip()
    matched = False

    if any(trigger in input_lower for trigger in flashlight_on_triggers):
        print(f"✓ '{cmd}' → Flashlight ON")
        matched = True
    elif any(trigger in input_lower for trigger in flashlight_off_triggers):
        print(f"✓ '{cmd}' → Flashlight OFF")
        matched = True
    elif any(trigger in input_lower for trigger in location_triggers):
        print(f"✓ '{cmd}' → Get Location")
        matched = True
    elif any(trigger in input_lower for trigger in time_triggers):
        print(f"✓ '{cmd}' → Get Time")
        matched = True
    elif any(trigger in input_lower for trigger in date_triggers):
        print(f"✓ '{cmd}' → Get Date")
        matched = True
    elif any(trigger in input_lower for trigger in selfie_triggers):
        print(f"✓ '{cmd}' → Take Selfie")
        matched = True
    elif any(trigger in input_lower for trigger in photo_triggers):
        print(f"✓ '{cmd}' → Take Photo")
        matched = True
    elif "volume" in input_lower:
        print(f"✓ '{cmd}' → Volume Control")
        matched = True
    elif "brightness" in input_lower:
        print(f"✓ '{cmd}' → Brightness Control")
        matched = True
    elif "record" in input_lower and ("audio" in input_lower or "sound" in input_lower):
        print(f"✓ '{cmd}' → Record Audio")
        matched = True

    if not matched:
        print(f"✗ '{cmd}' → NOT MATCHED")

print("\n✅ All test commands should be matched!")
