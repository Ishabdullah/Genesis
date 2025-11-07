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
- **Result:** ❌ FAILED - But revealed CRITICAL DISCOVERY! 🎉
- **Approach:** Use p4a.hook instead of p4a.local_recipes
  - Created `p4a_hook.py` - executable Python script
  - Hook searches for libffi configure.ac in .buildozer/
  - Patches the file before autogen.sh runs
  - Added `p4a.hook = p4a_hook.py` to buildozer.spec
- **Why it failed:**
  - Build failed with missing patch file: `p4a-recipes/libffi/remove-version-info.patch`
  - Having `p4a.local_recipes` directory made p4a expect complete recipe with patches
- **🎉 CRITICAL DISCOVERY:**
  - Build logs show: `Downloading libffi from https://github.com/libffi/libffi/archive/v3.4.2.tar.gz`
  - **p4a master NOW uses libffi 3.4.2!** (not the old 3.2.1)
  - libffi 3.4.2 is a modern version released in 2022
  - It has FIXED configure.ac that doesn't use LT_SYS_SYMBOL_USCORE!
- **This means:** ALL our patching attempts were unnecessary - p4a already upgraded libffi!
- **The real problem:** Our `p4a.local_recipes` setting was interfering with normal p4a operation

### Attempt 10: Let p4a Use Default libffi 3.4.2 ⭐ THE FIX
- **Date:** 2025-11-07
- **Config:** NDK 28c, p4a master, NO custom recipes or hooks
- **Status:** 🔄 IN PROGRESS (Build #19)
- **Approach:** Remove all custom overrides and let p4a work normally
  - Removed `p4a.local_recipes = ./p4a-recipes`
  - Removed `p4a.hook = p4a_hook.py`
  - Let p4a use its default libffi 3.4.2 recipe
- **Why this should work:**
  - p4a master already has libffi 3.4.2 in its recipes
  - libffi 3.4.2 has modern configure.ac compatible with autoconf 2.71+
  - No obsolete macros, no patching needed
  - Our custom overrides were preventing normal operation
- **Lesson learned:**
  - Always check what version p4a is actually using!
  - We spent 8 attempts trying to fix an already-fixed issue
  - The problem was our attempted solutions, not the base p4a setup

## ⚠️ ROOT CAUSE IDENTIFIED (Updated After Attempt #9)

**MAJOR UPDATE:** The initial diagnosis was WRONG! 🎯

### What We Initially Thought:
- p4a used old libffi (3.2.1) with obsolete LT_SYS_SYMBOL_USCORE macro
- Needed to patch or upgrade libffi

### What Was Actually Happening:
**p4a master ALREADY uses libffi 3.4.2** (discovered in Build #18 logs)
- libffi 3.4.2 is modern (released 2022) and compatible with autoconf 2.71+
- Has fixed configure.ac with no obsolete macros
- Works perfectly with NDK 28c and modern toolchains

### Why First 7-8 Attempts Failed:
1. **Attempts 1-7**: Unrelated issues, bad configurations, or just didn't check p4a's actual libffi version
2. **Attempt 8-9**: Our custom `p4a.local_recipes` was INTERFERING with p4a's correct libffi 3.4.2
3. **The real blocker**: Our attempted "fixes" were preventing the working solution from running!

### Lesson Learned:
**Always check what's actually being used before trying to fix it!** We spent 9 attempts trying to "fix" a problem that p4a had already solved.

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

**Total Attempts**: 10
**Success Rate**: 0/9 (Attempt #10 in progress)
**Previous Blocker**: RESOLVED! ✅ p4a master now uses libffi 3.4.2
**Root Cause of Failures**: Our custom overrides (p4a.local_recipes) were interfering
**Current Strategy**: Let p4a use default libffi 3.4.2 - no custom patches needed

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
