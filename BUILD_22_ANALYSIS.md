# Build #22 Error Analysis - Systematic Approach

## 📋 STEP 1: List ALL Problems in Build #22

### 🔴 CRITICAL ERRORS

#### Error 1: M4 syntax error - "end of file in string"
**Line:** `/usr/bin/m4:configure.ac:92: ERROR: end of file in string`
**Severity:** CRITICAL - Build-blocking
**When:** During `aclocal --force -I m4` (before autoreconf)
**Context:** This happens AFTER our patching, BEFORE autoreconf runs

#### Error 2: autom4te failed
**Line:** `autom4te: error: /usr/bin/m4 failed with exit status: 1`
**Severity:** CRITICAL - Cascading from Error 1
**Chain:** m4 fails → autom4te fails → aclocal fails → autoreconf fails

### ⚠️ WARNING OBSERVATIONS

#### Observation 1: Our patch couldn't find LT_SYS_SYMBOL_USCORE
**Log shows:** `⚠️  Could not find LT_SYS_SYMBOL_USCORE`
**Meaning:** The critical line we're looking for doesn't exist in expected format
**Impact:** We didn't patch the main issue!

#### Observation 2: We DID patch STDC_HEADERS
**Log shows:** `✅ Patched STDC_HEADERS preprocessor checks`
**Meaning:** Our STDC_HEADERS patching executed
**Suspicion:** This might have CAUSED Error 1!

### 🔍 KEY INSIGHT

**Timeline:**
1. Our recipe loads ✅
2. We read configure.ac ✅
3. Can't find `LT_SYS_SYMBOL_USCORE` line ⚠️
4. We patch `STDC_HEADERS` lines ✅
5. We write patched file ✅
6. Call super() → autoreconf
7. **m4 reports line 92 has "end of file in string"** 🔴
8. Build fails

**Hypothesis:** Our STDC_HEADERS patching BROKE configure.ac syntax at line 92!

---

## 📊 STEP 2: Compare to Previous Fixes

| Attempt | What We Fixed | Result | Why It Failed |
|---------|---------------|--------|---------------|
| 1-7 | NDK, configs | ❌ | Didn't address libffi issue |
| 8 | Custom recipe patching | ❌ | Recipe didn't execute |
| 9 | p4a hook | ❌ | Hook ran at wrong time |
| 10 | No overrides | ❌ | libffi still has obsolete macros |
| 11 | Official release URL | ❌ | p4a runs autoreconf anyway |
| 12 | Patch before autoreconf | ❌ | Missing patches file |
| 21 | Override patches list | ❌ | Missing patch file fixed, but... |
| **22** | **Patch ALL obsolete code** | **❌ BROKE configure.ac!** |

### Pattern Analysis:

**Attempts 1-20:** Couldn't get to the patching stage
**Attempt 21:** Got to patching, but missing patch file
**Attempt 22:** Patching executed, BUT broke configure.ac syntax!

**The Problem:** We're trying to patch TOO MUCH!
- Patching STDC_HEADERS broke m4 syntax
- We never even found the critical LT_SYS_SYMBOL_USCORE line

---

## 🎯 STEP 3: New Fixes to Try

### Root Cause of Build #22 Failure:

**Our STDC_HEADERS patching is too aggressive:**
```python
if 'STDC_HEADERS' in line and not line.strip().startswith('#'):
    lines[i] = '# PATCHED BY GENESIS BUILD: ' + line
```

This comments out EVERY line containing "STDC_HEADERS", which might include:
- Variable assignments
- String literals
- M4 macro arguments

**At line 92, we probably broke something like:**
```m4
AC_DEFINE([HAVE_STDC_HEADERS], [1], [Define to 1 if you have the ANSI C header files.])
```

By turning it into:
```m4
# PATCHED BY GENESIS BUILD: AC_DEFINE([HAVE_STDC_HEADERS], [1], [Define to 1 if you have the ANSI C header files.])
```

This breaks m4 syntax - the `])` is now inside a comment, leaving an unclosed string!

### Fix Options (Ranked by Priority):

#### Option A: ONLY Patch LT_SYS_SYMBOL_USCORE ⭐⭐⭐ BEST
**Why:**
- That's the ONLY critical blocker
- Warnings don't stop the build
- Less risk of breaking syntax

**How:**
1. Remove AC_HEADER_STDC patching
2. Remove STDC_HEADERS patching
3. ONLY patch the one critical line
4. But first - FIX why we can't find it!

**Investigation needed:** Why is `⚠️ Could not find LT_SYS_SYMBOL_USCORE`?
- Check the actual line format in libffi 3.4.4 configure.ac
- It might be at a different line number (not 215/223)
- The format might be slightly different

#### Option B: Fix the search pattern for LT_SYS_SYMBOL_USCORE ⭐⭐ GOOD
**Why:** We need to find it first!

**Investigation:**
1. Check what line number it's actually at
2. Check exact format (spacing, quotes, etc.)
3. Update our search pattern

#### Option C: Patch more carefully with context ⭐ RISKY
**Why:** Too complex, high risk of more syntax errors

**Not recommended:** Let's go simpler first

---

## ✅ STEP 4: Execute Fixes

### Fix Strategy for Build #23:

1. **Remove ALL warning patches** (AC_HEADER_STDC, STDC_HEADERS, AC_TRY_COMPILE)
2. **Focus ONLY on LT_SYS_SYMBOL_USCORE** (the critical blocker)
3. **Fix the search pattern** to actually find it
4. **Add debugging** to see what line we're actually looking for

### Implementation Plan:

```python
def build_arch(self, arch):
    build_dir = self.get_build_dir(arch.arch)
    configure_ac_path = os.path.join(build_dir, 'configure.ac')

    print("=" * 70)
    print("🔧 PATCHING LIBFFI - CRITICAL BLOCKER ONLY")
    print("=" * 70)

    with open(configure_ac_path, 'r') as f:
        content = f.read()

    # DEBUG: Show what we're searching for
    print("🔍 Searching for LT_SYS_SYMBOL_USCORE...")

    # Try multiple patterns
    patterns = [
        'if test "x$LT_SYS_SYMBOL_USCORE" = xyes; then',
        'if test "x$LT_SYS_SYMBOL_USCORE" = "xyes"; then',
        'LT_SYS_SYMBOL_USCORE',
    ]

    found = False
    for pattern in patterns:
        if pattern in content:
            print(f"  ✅ Found pattern: {pattern}")
            # Show context around it
            idx = content.find(pattern)
            start = max(0, idx - 100)
            end = min(len(content), idx + 100)
            print(f"  Context: ...{content[start:end]}...")
            found = True
            break

    if not found:
        print("  ❌ LT_SYS_SYMBOL_USCORE not found!")
        print("  Showing lines containing 'SYMBOL':")
        for i, line in enumerate(content.split('\n'), 1):
            if 'SYMBOL' in line:
                print(f"    Line {i}: {line}")

    # Only patch if we find it
    if found:
        # Patch it...

    super().build_arch(arch)
```

---

## 📝 Summary

**Build #22 broke because:**
- We patched too aggressively
- STDC_HEADERS patching broke m4 syntax at line 92
- We never even found the critical LT_SYS_SYMBOL_USCORE line

**Build #23 will:**
- Remove ALL warning patches
- Focus ONLY on critical LT_SYS_SYMBOL_USCORE
- Add debugging to find the actual line
- Patch ONLY that one thing

**Expected outcome:**
- Find the right pattern
- Patch only critical blocker
- Clean build with warnings (acceptable)
