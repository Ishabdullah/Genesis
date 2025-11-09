# Genesis Debug Features Documentation

## Overview

Genesis includes comprehensive developer debugging features that display directly on the app screen **only in debug APK builds**. These features help developers monitor performance, troubleshoot issues, and understand app behavior.

---

## 🔧 Debug Panel (Visual Display)

### Location
Appears at the top of the app, just below the header, in a dark panel with yellow "DEBUG MODE" label.

### Information Displayed
The debug panel updates **every 2 seconds** and shows:

```
🔧 DEBUG MODE
Time: HH:MM:SS
Memory: XX.X MB | CPU: X.X%
Platform: Linux 5.15.0
Core: ✓ Initialized (or ⚠ Not Ready)
Accel: NPU (or GPU/CPU)
Modules: genesis, device, accel
Threads: X active
```

### Features
- **Real-time updates**: Auto-refreshes every 2 seconds
- **Memory monitoring**: Shows RSS memory usage in MB
- **CPU tracking**: Current CPU usage percentage
- **Module status**: Shows which Genesis modules are loaded
- **Acceleration mode**: Current hardware acceleration (NPU/GPU/CPU)
- **Thread count**: Number of active Python threads
- **Platform info**: Operating system and version

---

## 💬 Debug Commands (Chat Interface)

Type these commands in the chat to get detailed debugging information:

### `#debug help`
Shows list of all available debug commands.

**Example:**
```
You: #debug help
Genesis: Debug Commands:
         #debug logs - Show recent debug logs
         #debug status - Show detailed status
         #debug memory - Show memory usage
         #debug help - Show this help
```

### `#debug logs`
Shows the last 20 debug log entries with timestamps.

**Example:**
```
You: #debug logs
Genesis: Recent Debug Logs:
         [15:23:45] Debug mode enabled
         [15:23:46] Starting Genesis initialization
         [15:23:47] Initializing acceleration manager
         [15:23:48] Running acceleration detection and benchmark
         [15:23:50] Acceleration mode: NPU
         ...
```

### `#debug status`
Shows comprehensive system status including:
- Python version
- Platform details
- Kivy version
- Genesis module status
- Acceleration status
- Active thread count
- Memory usage

**Example:**
```
You: #debug status
Genesis: System Status:
         Python: 3.11.6
         Platform: Linux 5.15.0
         Kivy: 2.2.1
         Genesis Core: ✓ Loaded
         Acceleration: ✓ NPU
         Active Threads: 5
         Memory: 125.3 MB
```

### `#debug memory`
Shows detailed memory usage information (requires psutil):
- RSS (Resident Set Size)
- VMS (Virtual Memory Size)
- Memory percentage

**Example:**
```
You: #debug memory
Genesis: Memory Usage:
         RSS: 125.3 MB
         VMS: 450.8 MB
         Percent: 8.5%
```

---

## 📝 Debug Logging

### Automatic Logging
All major events are automatically logged in debug mode:

**Initialization:**
```
[15:23:45] Debug mode enabled
[15:23:46] Starting Genesis initialization
[15:23:47] Initializing acceleration manager
[15:23:48] Running acceleration detection and benchmark
[15:23:50] Acceleration mode: NPU
[15:23:51] Initializing Genesis core
[15:23:52] Genesis core initialized successfully
```

**Message Processing:**
```
[15:24:10] Processing: What is 2 + 2?...
[15:24:12] Response generated in 2.15s
```

**Quick Actions:**
```
[15:25:00] Quick action: Location
[15:25:05] Quick action: Camera
```

**Errors:**
```
[15:26:30] ERROR: Failed to initialize camera
[15:26:31] ERROR in send_message: Camera permission denied
```

### Log Storage
- Logs stored in memory (last 100 entries)
- Accessible via `#debug logs` command
- Also printed to console/logcat for external monitoring

### External Access
View logs via adb logcat:
```bash
adb logcat | grep -i "DEBUG"
```

---

## 🎯 Debug Mode Control

### Environment Variable
Debug mode is controlled by the `GENESIS_DEBUG` environment variable:

```python
# In main.py
DEBUG_MODE = os.environ.get('GENESIS_DEBUG', '1') == '1'
```

### Buildozer Configuration
In `buildozer.spec`:

```ini
# For DEBUG builds (default)
android.meta_data = GENESIS_DEBUG=1

# For RELEASE builds (disable debug panel)
android.meta_data = GENESIS_DEBUG=0
```

### Build Commands

**Debug APK (with debug features):**
```bash
buildozer android debug
```

**Release APK (without debug features):**
```bash
# First, edit buildozer.spec:
# Change: android.meta_data = GENESIS_DEBUG=0
buildozer android release
```

### Manual Override
You can manually set the environment variable before running:

```bash
# Enable debug mode
export GENESIS_DEBUG=1
python main.py

# Disable debug mode
export GENESIS_DEBUG=0
python main.py
```

---

## 🛠️ What Gets Logged

### Automatic Event Logging

**App Lifecycle:**
- ✓ App launch
- ✓ Debug mode enabled/disabled
- ✓ Genesis initialization start/complete
- ✓ Module loading
- ✓ Acceleration manager initialization
- ✓ Acceleration mode detection

**User Interactions:**
- ✓ Messages sent (first 50 chars)
- ✓ Quick action button presses
- ✓ Response generation time

**Errors:**
- ✓ Initialization failures
- ✓ Message processing errors
- ✓ Device feature errors
- ✓ Any exception caught

### Performance Metrics
Tracked automatically:
- **Message processing time**: How long to generate responses
- **Memory usage**: Current RAM usage
- **CPU usage**: Current CPU percentage
- **Thread count**: Active background threads

---

## 📊 Debug Panel Updates

### Update Frequency
- **Debug panel**: Updates every 2 seconds
- **Debug logs**: Instant (as events occur)
- **Performance stats**: Real-time

### What Triggers Updates

**Panel Auto-Updates:**
- Time (every 2 seconds)
- Memory usage
- CPU usage
- Module status
- Thread count

**Log Updates:**
- User sends message
- Quick action triggered
- Genesis initializes
- Error occurs
- Response generated

---

## 🎨 Visual Design

### Debug Panel Styling
```
Background: Dark blue/gray (0.1, 0.1, 0.2, 0.95)
Border: Rounded corners (5dp radius)
Font: 9sp monospace
Colors:
  - Yellow (#ffff00): DEBUG MODE header
  - Cyan (#00ffff): Timestamps
  - Green (#00ff00): Success/Ready status
  - Orange (#ffaa00): Warning status
  - Red (#ff0000): Error status
  - Magenta (#ff00ff): Platform info
  - Light blue (#00ffff): Acceleration info
```

### Welcome Message
In debug mode, a welcome message appears on app start:

```
🔧 DEBUG MODE ACTIVE
Developer features enabled:
• Real-time performance monitoring
• Memory usage tracking
• Module status display
• Error logging

This panel only appears in debug APK builds.
```

---

## 🧪 Testing Debug Features

### Test Debug Panel
1. Build debug APK
2. Install on device
3. Launch app
4. Verify debug panel appears at top
5. Check that it updates every 2 seconds

### Test Debug Commands
```
Type: #debug help
Expected: List of commands

Type: #debug status
Expected: System information

Type: #debug logs
Expected: Recent log entries

Type: #debug memory
Expected: Memory usage details
```

### Test Debug Logging
1. Send a message
2. Type `#debug logs`
3. Verify message processing was logged
4. Check timestamp and content

### Test Release Build
1. Edit buildozer.spec: `android.meta_data = GENESIS_DEBUG=0`
2. Build release APK
3. Install on device
4. Verify debug panel does NOT appear
5. Verify debug commands do NOT work

---

## 🔍 Troubleshooting

### Debug Panel Not Showing
**Problem:** Debug panel doesn't appear in debug build

**Solutions:**
1. Check `buildozer.spec`: Ensure `android.meta_data = GENESIS_DEBUG=1`
2. Rebuild APK completely: `buildozer android clean && buildozer android debug`
3. Verify in logcat: `adb logcat | grep "DEBUG MODE"`

### Debug Commands Not Working
**Problem:** Typing `#debug` commands shows as regular messages

**Solutions:**
1. Ensure you're using a debug build
2. Check that `DEBUG_MODE = True` in the app
3. Type exact command: `#debug help` (no extra spaces)

### Memory Info Not Showing
**Problem:** Debug panel shows no memory/CPU info

**Solution:**
- psutil not available in this build
- Memory info requires psutil package
- Add to requirements.txt and rebuild

### Logs Not Appearing
**Problem:** `#debug logs` shows "No debug logs yet"

**Solutions:**
1. Use the app first (send messages, click buttons)
2. Logs are created as events occur
3. Check console/logcat for print statements

---

## 📱 Performance Impact

### Debug Mode Overhead
- **Memory**: +5-10 MB for logging and monitoring
- **CPU**: ~0.5% for panel updates
- **Battery**: Negligible impact
- **Storage**: Minimal (logs kept in memory)

### Recommendation
- Use debug builds for **development and testing**
- Use release builds (DEBUG_MODE=0) for **production**
- Debug features have minimal impact but should be disabled for end users

---

## 🚀 Advanced Usage

### Custom Debug Logging
Add custom debug logs in your code:

```python
# In any method of GenesisApp
self.log_debug("Custom message here")

# Example
def my_custom_function(self):
    self.log_debug("Starting custom function")
    # ... your code ...
    self.log_debug(f"Processed {count} items")
```

### Accessing Debug Info Programmatically
```python
# Get debug status
status = app.get_debug_status()

# Access logs
recent_logs = app.debug_logs[-10:]  # Last 10 logs

# Check debug mode
if DEBUG_MODE:
    # Debug-only code here
    pass
```

### External Monitoring
Monitor debug logs from computer:

```bash
# Watch all debug logs in real-time
adb logcat | grep "\[DEBUG\]"

# Save logs to file
adb logcat | grep "\[DEBUG\]" > genesis_debug.log

# Filter for errors only
adb logcat | grep "\[DEBUG\]" | grep "ERROR"
```

---

## 📚 Related Documentation

- **IMPLEMENTATION_PLAN.md**: Development roadmap
- **PROJECT_HANDOFF.md**: Complete project documentation
- **BUILD_COMPLETE_SUMMARY.md**: Build status and instructions

---

## ✅ Debug Feature Checklist

### For Developers
- [ ] Debug panel visible in debug builds
- [ ] Panel updates every 2 seconds
- [ ] Memory/CPU info displays correctly
- [ ] Module status shows correctly
- [ ] Acceleration mode displays
- [ ] Debug commands work (#debug help/status/logs/memory)
- [ ] Logs capture all events
- [ ] Timestamps are accurate
- [ ] Release builds hide all debug features

### For Testing
- [ ] Build debug APK with debug enabled
- [ ] Build release APK with debug disabled
- [ ] Test all debug commands
- [ ] Verify performance impact is minimal
- [ ] Check logs via adb logcat
- [ ] Test on multiple devices
- [ ] Verify no debug info leaks in release

---

**Debug features complete! Use them to build the best Genesis app possible! 🚀**
