# Build #26 Analysis - Configure Flag Not Applied

## SYSTEMATIC 4-STEP APPROACH

---

## STEP 1: List ALL Problems

### ✅ Still Working:
```
✅ Patch applied successfully! (line 223 commented)
✅ autoreconf completed
✅ configure ran
✅ Most files compiled
```

### ❌ PROBLEMS:

**Problem #1: Configure flag NOT applied**
```
📞 Calling parent build_arch (will run autoreconf + configure + make)
   Configure args: ['--without-exec-trampoline']   ← SET
   Expected: autoreconf ✅ → configure ✅ → make ✅

BUT:
src/tramp.c:262:22: error: call to undeclared function 'open_temp_exec_file'
make: *** [Makefile:1319: src/tramp.lo] Error 1
```

**Analysis:**
- We SET `configured_args = ['--without-exec-trampoline']`
- Our print shows it's set correctly
- BUT configure didn't actually use it!
- src/tramp.c is STILL being compiled (shouldn't be!)

**Root Cause:**
- The attribute name `configured_args` is WRONG
- Parent LibffiRecipe doesn't read this attribute
- Standard p4a recipes use `configure_args` (without 'd')
- OR we need to override a different method

**Evidence:**
- If flag was applied, configure would output:
  `checking for exec trampoline support... no`
- Makefile wouldn't include src/tramp.lo
- But we see `make: *** [Makefile:1319: src/tramp.lo]`
- This means trampoline code IS enabled!

---

## STEP 2: Compare to Previous Fixes (Builds 1-25)

### Build #25:
- ❌ Same error: `open_temp_exec_file` undefined
- No configure flag attempted

### Build #26:
- ✅ Added `configured_args` attribute
- ❌ Same error: `open_temp_exec_file` undefined
- ❌ Flag not actually applied

### What we learned:
- Setting attribute alone doesn't work
- Parent LibffiRecipe doesn't use `configured_args`
- Need to actually PASS the flag to configure command

### What we haven't tried yet:
- Correct attribute name: `configure_args`
- Override get_recipe_env() to set CFLAGS
- Patch configure.ac to disable trampolines in source
- Override the actual configure call

---

## STEP 3: Ranked List of New Fixes

### Option A: Fix attribute name to `configure_args` (Quick test)
**Confidence: MEDIUM**
**Why:**
- Might be simple typo: `configured_args` → `configure_args`
- Standard p4a recipes use various names
- Quick to test

**Implementation:**
- Change line 35: `configure_args = ['--without-exec-trampoline']`
- Try again

**Pros:**
- One character change
- Might be the issue

**Cons:**
- Might still not work if LibffiRecipe doesn't use this attribute
- Not guaranteed

---

### Option B: Patch configure.ac to disable trampolines in source (BEST)
**Confidence: VERY HIGH**
**Why:**
- Directly modify configure.ac BEFORE autoreconf
- Set FFI_EXEC_TRAMPOLINE_TABLE=0 in source
- Bypasses need for configure flags entirely
- We already successfully patch line 223

**Implementation:**
```python
# After line 223 patch, also patch trampoline settings
# Find line with FFI_EXEC_TRAMPOLINE_TABLE and force to 0
# Or add before autoreconf:
#   AC_DEFINE(FFI_EXEC_TRAMPOLINE_TABLE, 0, [Trampolines disabled for Android])
```

**Pros:**
- Guaranteed to work (source-level change)
- We already successfully patch configure.ac
- No dependency on recipe attributes
- Direct control

**Cons:**
- More complex than flag
- Need to find right place in configure.ac

---

### Option C: Override build_arch completely (Complex)
**Confidence: HIGH**
**Why:**
- Take full control of configure command
- Call configure manually with our flags
- Guaranteed flag application

**Implementation:**
```python
def build_arch(self, arch):
    # Patch configure.ac
    # Run autoreconf manually
    # Run configure manually with --without-exec-trampoline
    # Run make manually
```

**Pros:**
- Full control
- Guaranteed flags applied

**Cons:**
- Complex - need to reimplement build logic
- Duplicate parent code
- More maintenance

---

### Option D: Patch Makefile.am to exclude tramp.c (Source patch)
**Confidence: MEDIUM**
**Why:**
- Directly edit source build files
- Remove src/tramp.c from SOURCES list

**Implementation:**
- Patch Makefile.am after extraction
- Remove tramp references
- Run autoreconf

**Pros:**
- Source-level control

**Cons:**
- Complex - multiple files to patch
- autoreconf might override
- Need to understand libffi build

---

## STEP 4: Execute Fix - Option B (Patch configure.ac)

**Selected: Option B - Patch configure.ac to disable trampolines**

**Rationale:**
1. We already successfully patch configure.ac (line 223)
2. Source-level change = guaranteed to work
3. No dependency on p4a recipe attributes
4. Clean, maintainable solution
5. Proven approach (we know our patching works!)

**Implementation Plan:**
1. After patching line 223, add second patch
2. Find line ~228: `FFI_EXEC_TRAMPOLINE_TABLE=0`
3. Force this to remain 0 (disable all trampoline logic)
4. OR: Comment out the trampoline enable code
5. autoreconf will use our patched configure.ac
6. Makefile will exclude trampoline code

**Code approach:**
```python
# After line 223 patch:
# Find FFI_EXEC_TRAMPOLINE_TABLE assignments
# Force to 0 or comment out enable logic
# This disables trampolines at source level
```

**Expected Result:**
- autoreconf: ✅ (already working)
- configure: ✅ (will have trampolines disabled in generated script)
- make: ✅ (will not compile src/tramp.c)
- libffi builds successfully!

---

## Alternative: Option A first (quick test)

Since Option A is a one-character change, try that FIRST, then fall back to Option B if it doesn't work.

**Try:**
1. Change `configured_args` → `configure_args`
2. Push Build #27
3. If fails → Implement Option B for Build #28

---

## Summary

**Build #26 Issue:**
- Configure flag was SET but not APPLIED
- Attribute name might be wrong OR parent doesn't use it
- src/tramp.c still being compiled

**Next Steps:**
1. **Build #27:** Try `configure_args` (quick test)
2. **Build #28 (if needed):** Patch configure.ac to force FFI_EXEC_TRAMPOLINE_TABLE=0

**Best approach:** Option B (patch source) - guaranteed to work!
