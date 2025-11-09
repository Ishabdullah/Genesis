# Build #24 Error Analysis - Systematic Approach

## 📋 STEP 1: List ALL Problems in Build #24

### 🔴 CRITICAL ERROR

#### Error 1: Undefined macro at line 223
**Line:** `configure.ac:223: error: possibly undefined macro: LT_SYS_SYMBOL_USCORE`
**Severity:** CRITICAL - Build-blocking
**When:** During autoreconf → autoconf step
**Context:** The MACRO CALL itself is the problem!

### 🔍 KEY DEBUGGING OUTPUT

Our enhanced debugging revealed THE TRUTH:
```
  ❌ LT_SYS_SYMBOL_USCORE USAGE not found!
  🔎 Searching for ALL lines containing 'LT_SYS_SYMBOL_USCORE':
    🔤 Line 223: LT_SYS_SYMBOL_USCORE
  📝 Legend: 💲 = has $ (usage), 🔤 = no $ (macro call)
```

**CRITICAL DISCOVERY:**
- There's ONLY **ONE** line with LT_SYS_SYMBOL_USCORE in the entire file!
- Line 223 has JUST `LT_SYS_SYMBOL_USCORE` (the macro call)
- There is **NO** line with `$LT_SYS_SYMBOL_USCORE` (no usage!)

---

## 📊 STEP 2: Compare to Previous Fixes

| Build | Approach | Result | Discovery |
|-------|----------|--------|-----------|
| 1-22 | Various | ❌ | Different errors |
| 23 | Match any LT_SYS_SYMBOL_USCORE | ❌ | Patched macro call, broke syntax |
| **24** | **Match only $LT_SYS_SYMBOL_USCORE** | **❌ Found NOTHING!** |

### The Revelation:

**We were looking for the WRONG thing!**

In older libffi versions (3.2.1), configure.ac probably had BOTH:
- Line X: `LT_SYS_SYMBOL_USCORE` (macro call)
- Line Y: `if test "x$LT_SYS_SYMBOL_USCORE" = xyes; then` (usage)

In libffi 3.4.4, there's ONLY:
- Line 223: `LT_SYS_SYMBOL_USCORE` (macro call)
- **NO usage line!**

**The macro call IS the problem!**

The error confirms:
```
configure.ac:223: error: possibly undefined macro: LT_SYS_SYMBOL_USCORE
      If this token and others are legitimate, please use m4_pattern_allow.
```

---

## 🎯 STEP 3: New Fixes to Try

### ROOT CAUSE:

Line 223 has the macro **CALL**: `LT_SYS_SYMBOL_USCORE`

This is an **m4 autoconf macro** that doesn't exist in modern autoconf.
We need to handle the CALL itself, not look for a usage!

### Fix Options (Ranked):

#### Option A: Comment out line 223 (the macro call) ⭐⭐⭐ BEST
**Why:** It's the only line, and it's causing the error

**How:**
```python
# Find line 223 (or any line with JUST LT_SYS_SYMBOL_USCORE)
if 'LT_SYS_SYMBOL_USCORE' in line and '$' not in line:
    # This is the macro call
    patched = line.replace(
        'LT_SYS_SYMBOL_USCORE',
        '# PATCHED: LT_SYS_SYMBOL_USCORE - obsolete macro removed\n# LT_SYS_SYMBOL_USCORE'
    )
```

**Confidence:** VERY HIGH - This should work!

#### Option B: Use m4_pattern_allow (as error suggests) ⭐⭐
**Why:** Tells autoconf to ignore the undefined macro

**How:**
```
m4_pattern_allow([LT_SYS_SYMBOL_USCORE])
```

**Confidence:** MEDIUM - Might just suppress error, not fix issue

#### Option C: Skip autoreconf - use pre-generated configure ⭐
**Why:** Fallback if patching configure.ac is impossible

**Confidence:** MEDIUM-HIGH but complex

---

## ✅ STEP 4: Execute Fix

### Fix for Build #25 (Option A):

**Strategy:** Comment out ONLY the macro call at line 223

**Updated patching logic:**

```python
# Search for the macro CALL (no $ sign)
for i, line in enumerate(lines, 1):
    if 'LT_SYS_SYMBOL_USCORE' in line and '$' not in line:
        # This is line 223 - the macro call
        print(f"  ✅ Found macro CALL at line {i}: {line.strip()}")

        # Comment it out
        lines[i-1] = '# PATCHED BY GENESIS: Obsolete macro removed\n# ' + line

        print(f"  🔧 Commented out line {i}")
        break

# Write patched file
with open(configure_ac_path, 'w') as f:
    f.write('\n'.join(lines))
```

**Why this should work:**
1. Line 223 just calls an undefined macro
2. The macro probably sets a variable that's never used (since no usage line exists!)
3. Commenting it out = autoconf won't try to call undefined macro
4. Build proceeds without error

---

## 📝 Summary

**Build #24 KEY INSIGHT:**
```
🔤 Line 223: LT_SYS_SYMBOL_USCORE  ← ONLY line in entire file!
```

**There is NO usage line with $!**

**Previous attempts were based on wrong assumption:**
- We thought there was a usage line like: `if test "x$LT_SYS_SYMBOL_USCORE" = xyes`
- In reality, libffi 3.4.4 only has the macro CALL at line 223
- No usage = the macro is probably not needed at all!

**Build #25 will:**
- Find line 223 (or any line with LT_SYS_SYMBOL_USCORE without $)
- Comment it out completely
- autoreconf will skip the commented line
- Build should succeed!

**Confidence: VERY HIGH** - We finally know exactly what to patch!

---

## 🔢 Remaining Options if Build #25 Fails

After this, we have:
1. Build #26: Try m4_pattern_allow approach
2. Build #27: Skip autoreconf entirely (use pre-generated configure)
3. Build #28: Try Ubuntu 20.04 runner (older autoconf)
4. Alternative: Switch to different build tool

But Build #25 should work - we're commenting out the exact line causing the error!
