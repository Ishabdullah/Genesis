# Android Build Fixes Log

This file tracks all attempted fixes for the Genesis Android APK build issues.

## Problem: libffi autoconf error
**Error Message:** `configure.ac:215: error: possibly undefined macro: LT_SYS_SYMBOL_USCORE`

### Attempt 1: NDK r21e
- **Date:** 2025-11-07
- **Config:** NDK r21e, p4a develop branch
- **Result:** ❌ FAILED - NDK too old, p4a requires minimum NDK 25
- **Error:** "The minimum supported NDK version is 25"

### Attempt 2: NDK 25c
- **Date:** 2025-11-07
- **Config:** NDK 25c, p4a master branch
- **Result:** ❌ FAILED - libffi autoconf error (LT_SYS_SYMBOL_USCORE undefined)
- **Error:** Same autoconf macro error

### Attempt 3: NDK 28c (recommended by p4a)
- **Date:** 2025-11-07
- **Config:** NDK 28c, p4a master branch
- **Result:** ❌ FAILED - libffi autoconf error (LT_SYS_SYMBOL_USCORE undefined)
- **Error:** Same autoconf macro error
- **Note:** This is the officially recommended NDK version by p4a

### Attempt 4: Added autoconf-archive package
- **Date:** 2025-11-07
- **Config:** NDK 28c, p4a master branch, autoconf-archive installed
- **Result:** ❌ FAILED - libffi autoconf error (LT_SYS_SYMBOL_USCORE undefined)
- **Error:** Same error - macros not found by aclocal during p4a build
- **Reason:** autoconf-archive installed on runner but not accessible in p4a build environment

### Attempt 5: Export ACLOCAL_PATH environment variables
- **Date:** 2025-11-07
- **Config:** NDK 28c, p4a master branch, autoconf-archive + ACLOCAL_PATH export
- **Result:** ❌ FAILED - libffi autoconf error (LT_SYS_SYMBOL_USCORE undefined)
- **Changes:**
  - Added `export ACLOCAL_PATH="/usr/share/aclocal:${ACLOCAL_PATH}"`
  - Added `export ACLOCAL="aclocal -I /usr/share/aclocal"`
- **Reason:** Environment variables were set correctly but macros still not found by autogen.sh
- **Note:** ACLOCAL_PATH was confirmed in environment but didn't help

### Attempt 6: Use p4a develop branch with NDK 28c
- **Date:** 2025-11-07
- **Config:** NDK 28c, p4a develop branch, autoconf-archive + ACLOCAL_PATH export
- **Result:** ❌ FAILED - libffi autoconf error (LT_SYS_SYMBOL_USCORE undefined)
- **Reason:** develop branch uses Python 3.14 but has same libffi version with same autoconf issues
- **Note:** develop branch is too bleeding edge, same libffi problem persists

### Attempt 7: Remove pyjnius dependency
- **Date:** 2025-11-07
- **Config:** NDK 28c, p4a master branch, requirements WITHOUT pyjnius
- **Result:** ❌ FAILED - libffi autoconf error (LT_SYS_SYMBOL_USCORE undefined)
- **Changes:** Removed pyjnius from requirements (kept python3, kivy, android, plyer)
- **Trade-off:** Lost Java bridge functionality
- **Reason:** Python3's ctypes module still requires libffi - p4a builds it from source with same error
- **Conclusion:** Removing pyjnius doesn't help; Python itself needs libffi

### Attempt 8: Custom p4a Recipe with On-the-Fly Patching 🎯 CREATIVE SOLUTION
- **Date:** 2025-11-07
- **Config:** NDK 28c, p4a master, custom local recipe that patches libffi source
- **Result:** ❌ FAILED - Recipe never loaded/executed
- **Approach:** **Think Outside the Box!**
  - Created custom libffi recipe: `p4a-recipes/libffi/__init__.py`
  - Recipe patches configure.ac BEFORE autogen.sh runs
  - Removes/replaces the problematic `LT_SYS_SYMBOL_USCORE` macro
  - Defaults to modern system behavior (no underscore prefix)
- **How it works:**
  1. p4a loads our custom recipe (via `p4a.local_recipes`)
  2. Before building, recipe reads configure.ac
  3. Patches out the obsolete macro usage
  4. Continues with normal build process
- **Why it failed:** Build logs show no patch messages - recipe didn't execute
- **Reason:** p4a local recipes have specific structure requirements that our recipe didn't meet
- **Lesson:** p4a recipes need exact API compatibility, hooks are more reliable

### Attempt 9: p4a Hook to Patch libffi 🪝 ALTERNATIVE APPROACH
- **Date:** 2025-11-07
- **Config:** NDK 28c, p4a master, p4a pre-build hook
- **Status:** 🔄 IN PROGRESS (Build #18)
- **Approach:** Use p4a.hook instead of p4a.local_recipes
  - Created `p4a_hook.py` - executable Python script
  - Hook searches for libffi configure.ac in .buildozer/
  - Patches the file before autogen.sh runs
  - Added `p4a.hook = p4a_hook.py` to buildozer.spec
- **Why hooks are better:**
  - Simpler than custom recipes (just patch files, no p4a API)
  - Execute at guaranteed points in build process
  - Less likely to break with p4a version changes
  - Direct file manipulation, no complex overrides
- **How it works:**
  1. p4a runs hook script at pre-defined stage
  2. Hook searches .buildozer/ for libffi/configure.ac
  3. Reads file and patches LT_SYS_SYMBOL_USCORE usage
  4. Replaces problematic macro with safe default
  5. Writes patched file back
  6. Build continues with patched source
- **Hypothesis:** Hook will execute reliably and patch libffi before autogen.sh runs

## ⚠️ ROOT CAUSE IDENTIFIED

After 7 comprehensive attempts, the root cause is clear:

**python-for-android's libffi recipe uses an outdated libffi version (likely 3.2.1 or similar) that contains obsolete autoconf macros (`LT_SYS_SYMBOL_USCORE`) which are incompatible with modern autoconf/autotools.**

The macro was removed from libtool in newer versions, but libffi's old configure.ac still references it. Even with autoconf-archive installed and ACLOCAL_PATH configured, the macro cannot be found because it simply doesn't exist in modern toolchains.

### Why All Standard Approaches Failed:

1. **NDK versions (r21e, 25c, 28c)**: All use modern autotools
2. **autoconf-archive package**: Doesn't contain this obsolete macro
3. **ACLOCAL_PATH configuration**: Can't find what doesn't exist
4. **p4a branches (master/develop)**: Both use same old libffi
5. **Removing pyjnius**: Python's ctypes still needs libffi

## 🔧 SOLUTION OPTIONS

### Option 1: Patch python-for-android's libffi Recipe ⭐ RECOMMENDED
This requires modifying p4a's libffi recipe to:
- Update to libffi 3.4.x (has fixed configure.ac)
- OR patch the configure.ac to remove LT_SYS_SYMBOL_USCORE macro
- OR use pre-built libffi from NDK

**How to implement:**
1. Fork python-for-android
2. Update `pythonforandroid/recipes/libffi/__init__.py`
3. Point buildozer.spec to your fork: `p4a.fork = yourusername`

### Option 2: Report Upstream & Wait
File an issue at: https://github.com/kivy/python-for-android/issues

Search first - this may already be reported. If it is, add details about NDK 28c incompatibility.

### Option 3: Use Pre-Built APK Solution
Build on a local machine with:
- Older Linux distribution (Ubuntu 20.04 with older autotools)
- Or use Docker with controlled autoconf version

### Option 4: Alternative Build Tools
- **Chaquopy**: Commercial Python-Android tool with better dependency management
- **BeeWare Briefcase**: Free, modern Python mobile framework
- **Termux**: Build directly on Android device

## 📝 RECOMMENDATIONS FOR THIS PROJECT

Given the Genesis app's complexity and need for Android APIs, I recommend:

1. **Short-term**: Report this issue to python-for-android maintainers
2. **Medium-term**: Create a custom p4a recipe fork with updated libffi
3. **Long-term**: Consider migrating to BeeWare/Briefcase for better mobile support

## 📊 CURRENT STATUS

**Total Attempts**: 9
**Success Rate**: 0/8 (Attempt #9 in progress)
**Blocker**: python-for-android libffi recipe incompatibility with modern autotools
**Current Strategy**: Using p4a hook to patch libffi source on-the-fly

## Build Configuration Summary

### Current Settings:
```
Android API: 33
Android NDK: 28c
Python-for-Android: master branch
Requirements: python3, kivy, pyjnius, android, plyer
Architectures: arm64-v8a, armeabi-v7a
```

### Simplified Requirements:
Original requirements included: pillow, requests, certifi, urllib3
These were removed to avoid additional libffi dependencies.

## Next Steps to Try (if current attempt fails):

1. **Try NDK 26b** - Middle ground between 25c and 28c
2. **Use p4a develop branch with NDK 28c** - Latest p4a code may have libffi fixes
3. **Patch libffi recipe** - Create custom p4a recipe to skip problematic macro
4. **Use pre-compiled libffi** - If p4a supports it
5. **Fork p4a and fix libffi** - Last resort, patch the libffi recipe directly

## Root Cause Analysis:

The `LT_SYS_SYMBOL_USCORE` macro is an obsolete libtool macro that was removed in newer autoconf versions. The libffi version used by p4a still references this macro in its configure.ac file, causing autoreconf to fail when building with modern NDK toolchains.

The macro is provided by the autoconf-archive package, but it needs to be in aclocal's search path when libffi's autogen.sh runs during the p4a build process.
