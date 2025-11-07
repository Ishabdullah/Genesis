# Genesis Android Build - Issues Checklist

Based on analysis of build logs and error patterns across 8 attempts.

## ✅ What's Working (No Fix Needed)

1. **Hostpython3 compilation** - Successfully builds with system libffi
2. **Python _ctypes module** - Compiles on host using `-lffi`
3. **NDK/SDK setup** - NDK 28c and SDK 33 install correctly
4. **Build environment** - All system dependencies present
5. **GitHub Actions workflow** - Pipeline configuration is correct

## 🔴 Critical Issues (MUST FIX)

### Issue #1: libffi autoconf macro error (ROOT CAUSE)
**Error:** `configure.ac:215: error: possibly undefined macro: LT_SYS_SYMBOL_USCORE`

**Where it fails:**
- When p4a builds libffi for Android targets (arm64-v8a, armeabi-v7a)
- During `autogen.sh` execution in libffi source

**Root cause:**
- p4a's libffi recipe uses old libffi version (3.2.1 or similar)
- Old configure.ac references obsolete `LT_SYS_SYMBOL_USCORE` macro
- Modern autotools (autoconf 2.71+) removed this macro
- Ubuntu 24.04 runners have autoconf 2.71, incompatible with old libffi

**Fix attempts so far:**
- ❌ Change NDK versions (r21e, 25c, 28c) - same error
- ❌ Install autoconf-archive - macro doesn't exist there
- ❌ Export ACLOCAL_PATH - can't find what doesn't exist
- ❌ Switch p4a branches - both use same old libffi
- ❌ Remove pyjnius - Python ctypes still needs libffi
- ❌ Custom p4a recipe - didn't load properly

**Next fixes to try:**
1. ✅ **p4a hook to patch libffi** (JUST CREATED - p4a_hook.py)
2. Fork p4a and update libffi recipe to version 3.4.4
3. Use p4a patch system to modify libffi source
4. Try building in older Ubuntu 20.04 Docker container
5. Switch to alternative build tool (BeeWare, Chaquopy)

### Issue #2: Custom recipe not loading
**Problem:** Created `p4a-recipes/libffi/__init__.py` but it never executed

**Evidence:** No patch messages in build logs

**Possible causes:**
- Recipe directory structure wrong
- Recipe needs `recipe.sh` not just `__init__.py`
- p4a.local_recipes path incorrect
- Recipe class name doesn't match p4a expectations
- Missing recipe metadata (__version__, depends, etc.)

**Fix:** Switched to p4a hook approach (more reliable)

## ⚠️ Minor Issues (NON-CRITICAL)

### Issue #3: Missing optional Python modules
**Modules not built:** _dbm, _gdbm, _tkinter, nis

**Impact:** Low - Genesis doesn't use these modules

**Fix if needed:**
```bash
sudo apt-get install libgdbm-dev tk-dev
```

### Issue #4: stty warning
**Warning:** `stty: 'standard input': Inappropriate ioctl for device`

**Impact:** None - harmless warning in non-TTY environment (GitHub Actions)

**Fix:** Can be ignored, or suppress with `2>/dev/null`

## 📋 Build Process Stages (What Happens When)

1. **Stage 1: Environment Setup** ✅ WORKING
   - Install system dependencies
   - Set up Python, Java
   - Install buildozer

2. **Stage 2: SDK/NDK Download** ✅ WORKING
   - Download Android SDK 33
   - Download Android NDK 28c
   - Accept licenses

3. **Stage 3: p4a Clone** ✅ WORKING
   - Clone python-for-android (master branch)
   - Load recipes

4. **Stage 4: Hostpython3 Build** ✅ WORKING
   - Build Python for host machine
   - Uses system libffi (works fine)
   - Build _ctypes and other modules

5. **Stage 5: Target Dependencies** 🔴 **FAILS HERE**
   - Build libffi for Android (arm64-v8a, armeabi-v7a)
   - **THIS IS WHERE IT FAILS** ❌
   - autogen.sh fails with LT_SYS_SYMBOL_USCORE error

6. **Stage 6: Target Python Build** ⏸️ NEVER REACHED
   - Would build Python for Android
   - Can't reach this due to libffi failure

7. **Stage 7: APK Assembly** ⏸️ NEVER REACHED
   - Would package everything into APK
   - Can't reach this due to libffi failure

## 🎯 Priority Fix Order

### Immediate (Next Build #18):
1. **Enable p4a hook** - Add `p4a.hook = p4a_hook.py` to buildozer.spec
2. **Make hook executable** - Ensure proper permissions
3. **Test hook execution** - Verify it runs before libffi build

### If Hook Fails (Build #19):
4. **Try different hook timing** - Use p4a pre-build vs post-download hooks
5. **Direct configure.ac patching** - Patch in workflow before buildozer runs

### If All Hooks Fail (Build #20+):
6. **Fork python-for-android** - Create custom p4a fork with updated libffi
7. **Docker workaround** - Build in Ubuntu 20.04 container
8. **Alternative tool** - Switch to BeeWare Briefcase

## 📊 Error Pattern Analysis

All 8 failed builds show **IDENTICAL error at IDENTICAL stage:**

```
[DEBUG]: Building libffi for arm64-v8a
[DEBUG]: -> directory context /path/to/libffi
[DEBUG]: -> running autogen.sh
[DEBUG]: configure.ac:215: error: possibly undefined macro: LT_SYS_SYMBOL_USCORE
[DEBUG]: autoreconf: error: /usr/bin/autoconf failed with exit status: 1
[ERROR]: Build failed: Subprocess command failed
```

**Conclusion:** This is 100% reproducible, configuration-independent, and requires source code patching.

## 🔧 Technical Details for Hook Approach

**Why hooks might work better than recipes:**
- Recipes override build logic (complex, must match p4a API)
- Hooks run shell scripts (simple, just patch files)
- Hooks execute at guaranteed times in build process
- Less likely to break with p4a version changes

**Hook strategy:**
1. p4a downloads libffi source
2. **Hook runs AFTER download, BEFORE autogen.sh**
3. Hook searches for configure.ac in .buildozer/
4. Hook patches configure.ac to remove LT_SYS_SYMBOL_USCORE
5. p4a continues with patched source
6. autogen.sh runs successfully

**Hook implementation:** Created `p4a_hook.py` with:
- Search for libffi configure.ac in buildozer directory
- Patch the problematic macro usage
- Replace with safe default value (no underscore prefix)
- Don't fail if not found yet (might run early)

## 📝 Files Modified/Created

### New Files:
- `p4a_hook.py` - Pre-build hook to patch libffi
- `BUILD_ISSUES_CHECKLIST.md` - This file

### Need to Modify:
- `buildozer.spec` - Add `p4a.hook = p4a_hook.py`

### Already Modified (Previous Attempts):
- `buildozer.spec` - NDK version, requirements, local_recipes
- `.github/workflows/build-apk.yml` - Added autoconf packages
- `BUILD_FIXES_LOG.md` - Comprehensive attempt log
- `ANDROID_BUILD_STATUS.md` - Status report
- `p4a-recipes/libffi/__init__.py` - Custom recipe (didn't work)

## 🎬 Next Action

**Update buildozer.spec to enable the hook:**
```ini
p4a.hook = p4a_hook.py
```

Then commit and push for Build #18.
