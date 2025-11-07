# 📱 Genesis Device Integration - Quick Start Guide

Get started with Genesis device capabilities in under 5 minutes!

---

## ⚡ Quick Setup (2 minutes)

### Step 1: Install Termux API
```bash
pkg install termux-api
```

### Step 2: Install Termux:API App
Download from:
- F-Droid: https://f-droid.org/packages/com.termux.api/
- GitHub: https://github.com/termux/termux-api/releases

### Step 3: Grant Permissions
```
Android Settings → Apps → Termux:API → Permissions
✓ Location
✓ Camera
✓ Microphone
✓ Storage
```

### Step 4: Test It!
```bash
./genesis.py
```

---

## 🎯 Try These Commands

### 1. Get Current Time
```
Genesis> What time is it?
Genesis> What's today's date?
```

**Expected**: Current date and time from device

---

### 2. Get Your Location
```
Genesis> Where am I?
Genesis> What's my current location?
```

**Expected**: GPS coordinates with accuracy

---

### 3. Take a Photo
```
Genesis> Take a photo
Genesis> Take a selfie
Genesis> Take a picture with the back camera
```

**Expected**: Photo saved to `data/media/photo_YYYYMMDD_HHMMSS.jpg`

---

### 4. Control Flashlight
```
Genesis> Turn on the flashlight
Genesis> Turn off the torch
Genesis> Toggle flashlight
```

**Expected**: Device flashlight turns on/off

---

### 5. Adjust Volume
```
Genesis> Set music volume to 10
Genesis> Increase volume
Genesis> What's the current volume?
```

**Expected**: Music volume changes

---

### 6. Adjust Brightness
```
Genesis> Set brightness to 150
Genesis> Increase brightness
Genesis> Dim the screen
```

**Expected**: Screen brightness changes (0-255)

---

### 7. Record Audio
```
Genesis> Record 5 seconds of audio
Genesis> Record audio for 10 seconds
```

**Expected**: Audio file saved to `data/media/audio_YYYYMMDD_HHMMSS.m4a`

---

## 🧪 Test Device Capabilities

Run the comprehensive test suite:
```bash
./test_device_capabilities.sh
```

Sample output:
```
╔══════════════════════════════════════════════════════════════╗
║     🧬 Genesis Device Capabilities Test Suite               ║
╚══════════════════════════════════════════════════════════════╝

[Test 1] Checking Termux API availability...
✓ PASS: Termux API is installed

[Test 2] Testing device_manager.py module...
✓ PASS: device_manager.py module loads successfully

[Test 3] Testing get_date_time action...
✓ Date/Time: 2025-11-06 15:12:18
✓ PASS: get_date_time works correctly

...

╔══════════════════════════════════════════════════════════════╗
║                     TEST SUMMARY                             ║
╚══════════════════════════════════════════════════════════════╝
✓ Passed:  7
✗ Failed:  0
⊘ Skipped: 3

All critical tests passed!
```

---

## 🔍 Troubleshooting

### Issue: "Termux API not available"
**Solution**:
```bash
pkg install termux-api
# Restart Termux after installation
```

### Issue: "Permission denied" for location/camera
**Solution**:
1. Install Termux:API app
2. Grant permissions in Android Settings
3. Try the command again

### Issue: "Command not found: termux-location"
**Solution**:
```bash
# Update packages
pkg update && pkg upgrade
# Reinstall termux-api
pkg install termux-api
```

### Issue: Photos not saving
**Solution**:
```bash
# Check if directory exists
ls -la data/media/
# Create if missing
mkdir -p data/media/
```

### Issue: Genesis not detecting device commands
**Solution**:
1. Verify `device_manager.py` exists
2. Check Genesis version: Should be v2.2.0+
3. Restart Genesis

---

## 📚 Device Command Reference

### Location
```python
# Natural language
"Where am I?"
"What's my current location?"

# Returns
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "accuracy": 5.0,
  "altitude": 10.0
}
```

### Date/Time
```python
# Natural language
"What time is it?"
"What's the date?"

# Returns
{
  "date": "2025-11-06",
  "time": "15:12:18",
  "day_of_week": "Thursday",
  "timezone": "EST"
}
```

### Camera
```python
# Natural language
"Take a photo"
"Take a selfie" (front camera)
"Take a picture with back camera"

# Returns
{
  "filepath": "data/media/photo_20251106_151218.jpg",
  "camera": "back",
  "size_bytes": 2457600
}
```

### Audio Recording
```python
# Natural language
"Record 10 seconds of audio"
"Record audio for 5 seconds"

# Returns
{
  "filepath": "data/media/audio_20251106_151218.m4a",
  "duration_seconds": 10,
  "size_bytes": 160000
}
```

### Flashlight
```python
# Natural language
"Turn on flashlight"
"Turn off torch"
"Toggle flashlight"

# Returns
{
  "state": "on",
  "flashlight_on": true
}
```

### Brightness
```python
# Natural language
"Set brightness to 150"
"Increase brightness"
"Dim the screen"

# Returns
{
  "brightness": 150,
  "brightness_percent": 59
}
```

### Volume
```python
# Natural language
"Set music volume to 10"
"Increase volume"
"Mute music"

# Returns
{
  "stream": "music",
  "volume": 10
}

# Available streams:
# music, ring, alarm, notification, system
```

---

## 🎓 Advanced Usage

### Direct JSON Commands (Advanced)
If you want Genesis to use specific parameters:

```
Genesis> Use the front camera to take a photo

# Genesis will generate:
DEVICE: {"action": "take_photo", "parameters": {"camera": "front"}}
```

### Combining Device Commands
```
Genesis> What time is it and where am I?

# Genesis will:
1. Get date/time
2. Get location
3. Provide combined response
```

---

## 🔐 Privacy Notes

- ✅ All processing happens **locally** on your device
- ✅ Device data **never leaves** your device
- ✅ **You control** which permissions to grant
- ✅ Commands execute only when **explicitly requested**
- ✅ Full **audit trail** in Genesis logs

---

## 📊 Supported Android Versions

- Android 7.0+ (Nougat): ✅ Full support
- Android 6.0 (Marshmallow): ⚠️ Limited support
- Android 5.0 and below: ❌ Not supported

---

## ✨ Tips

1. **Be specific**: "Take a photo with the back camera" works better than "take photo"
2. **Natural language**: Genesis understands natural requests
3. **Check permissions**: If a command fails, verify Android permissions
4. **Test first**: Run `./test_device_capabilities.sh` to verify setup
5. **Check logs**: Use `#performance` to see device command execution

---

## 🚀 Next Steps

1. ✅ Complete setup steps above
2. ✅ Try the example commands
3. ✅ Run the test suite
4. ✅ Explore device capabilities
5. ✅ Read full documentation in README.md

---

**Need help?** Check:
- Full documentation: `README.md`
- Changelog: `CHANGELOG.md`
- Integration summary: `DEVICE_INTEGRATION_SUMMARY.md`
- Test suite: `./test_device_capabilities.sh`

**Version**: Genesis v2.2.0
**Repository**: https://github.com/Ishabdullah/Genesis
