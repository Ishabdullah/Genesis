# Build #27 Analysis - Shell Variables Don't Work in configure.ac

## SYSTEMATIC 4-STEP APPROACH

---

## STEP 1: List ALL Problems

### ✅ What Worked:
```
✅ PATCH #1 applied successfully! (line 223 commented)
✅ PATCH #2 applied successfully! (inserted at line 222)
✅ autoreconf completed
✅ configure ran
✅ Most files compiled
```

### ❌ CRITICAL PROBLEM:

**Patch #2 was applied but HAD NO EFFECT!**

```
✅ Inserted trampoline disable code at line 222
📝 Added: enable_exec_trampoline=no
📝 Added: ac_cv_func_mmap_exec=no
✅ PATCH #2 applied successfully!

BUT:
src/tramp.c:262:22: error: call to undeclared function 'open_temp_exec_file'
make: *** [Makefile:1319: src/tramp.lo] Error 1
```

**Root Cause Analysis:**

We inserted these lines into configure.ac:
```bash
enable_exec_trampoline=no
ac_cv_func_mmap_exec=no
```

**BUT:** These are SHELL VARIABLES, not autoconf M4 macros!

**How autoconf works:**
1. configure.ac contains M4 macros like `AC_DEFINE`, `AC_ARG_ENABLE`, etc.
2. autoreconf processes M4 macros to GENERATE configure script
3. Shell variables in configure.ac are NOT processed by autoreconf
4. They're just treated as literal text (or ignored)

**What we actually did:**
- Inserted shell variable assignments into M4 source code
- autoreconf ignored them (not M4 macros)
- Generated configure script didn't have trampolines disabled
- Makefile still includes src/tramp.c
- Compilation fails

**Evidence:**
- Patch says "applied successfully" ✅
- But src/tramp.lo is STILL being compiled
- Same error at line 262
- This proves the patch had NO EFFECT on build

---

## STEP 2: Compare to Previous Fixes (Builds 1-26)

| Build | Strategy | Patch Applied? | Trampolines Disabled? | Result |
|-------|----------|----------------|-----------------------|--------|
| 25 | Line 223 only | ✅ | ❌ | tramp.c error |
| 26 | configured_args | ❌ (not used) | ❌ | tramp.c error |
| 27 | Shell variables in configure.ac | ✅ (but wrong!) | ❌ | tramp.c error |

### What we learned:
- Patching configure.ac works (Patch #1 proves it)
- BUT we need to use AUTOCONF MACROS, not shell variables
- M4 macros: `AC_DEFINE`, `AC_ARG_ENABLE`, `AC_SUBST`, etc.
- Shell variables are for RUNTIME (configure execution), not source

### What we haven't tried yet:
- Modify AC_ARG_ENABLE logic to force disable
- Use AC_DEFINE to set FFI_EXEC_TRAMPOLINE_TABLE=0
- Patch Makefile.am to exclude tramp.c from SOURCES
- Override configure command execution (set env vars at runtime)
- Patch tramp.c to add missing function

---

## STEP 3: Ranked List of New Fixes

### Option A: Patch AC_ARG_ENABLE to force disable (HIGH confidence)
**Confidence: HIGH**
**Why:**
- Modify the actual M4 macro that controls trampolines
- Find `AC_ARG_ENABLE([pax-emutramp` section
- Force the result to always be 'no'
- This is M4 code that autoreconf WILL process

**Implementation:**
```m4
# Find section around line 200-230:
AC_ARG_ENABLE([pax-emutramp],
  [AS_HELP_STRING([--enable-pax-emutramp], [...])],
  [if test "$enableval" = "yes"; then
    ...
  elif test "$enableval" = "experimental"; then
    ...
  fi)

# PATCH: Add after this section:
# PATCHED BY GENESIS: Force disable trampolines for Android
enable_pax_emutramp=no
enable_exec_trampoline=no
```

**Pros:**
- Uses autoconf's own variable system
- Will be processed during configure generation
- Clean integration with existing logic

**Cons:**
- Still might not work if logic is downstream
- Need to find exact variable names

---

### Option B: Patch Makefile.am to exclude tramp.c (BEST - Direct)
**Confidence: VERY HIGH**
**Why:**
- Most direct approach
- Remove src/tramp.c from SOURCES list in Makefile.am
- When autoreconf runs, generated Makefile won't include tramp.c
- No trampoline code = no compilation error

**Implementation:**
```python
# Read Makefile.am
# Find libffi_la_SOURCES or similar
# Remove references to src/tramp.lo or src/tramp.c
# Save file
# autoreconf will use patched Makefile.am
```

**Pros:**
- GUARANTEED to work (directly controls what gets compiled)
- Simple text replacement
- No dependency on configure logic
- We already successfully patch files

**Cons:**
- Need to find correct Makefile.am
- Might be multiple Makefiles

---

### Option C: Use AC_DEFINE to force FFI_EXEC_TRAMPOLINE_TABLE=0 (Medium)
**Confidence: MEDIUM**
**Why:**
- Add AC_DEFINE after AC_ARG_ENABLE section
- Forces C preprocessor definition
- Might bypass trampoline compilation

**Implementation:**
```m4
# After pax-emutramp section, insert:
AC_DEFINE([FFI_EXEC_TRAMPOLINE_TABLE], [0], [Trampolines disabled for Android])
```

**Pros:**
- Clean M4 macro
- Autoconf standard approach

**Cons:**
- Might be overridden by later logic
- FFI_EXEC_TRAMPOLINE_TABLE might not control everything

---

### Option D: Override get_recipe_env() to set runtime vars (Complex)
**Confidence: MEDIUM**
**Why:**
- Set shell variables when configure RUNS (not in source)
- Override parent's get_recipe_env()
- Add to environment: enable_exec_trampoline=no

**Implementation:**
```python
def get_recipe_env(self, arch):
    env = super().get_recipe_env(arch)
    env['enable_exec_trampoline'] = 'no'
    env['ac_cv_func_mmap_exec'] = 'no'
    return env
```

**Pros:**
- Variables set at correct time (configure execution)
- Standard autoconf approach

**Cons:**
- Complex - need to understand p4a recipe API
- Variable names might be wrong
- Might not override internal logic

---

### Option E: Patch tramp.c to add open_temp_exec_file() (Last resort)
**Confidence: LOW**
**Why:**
- Define the missing function for Android
- Complex - need to understand Android APIs
- Might have other dependencies

**Cons:**
- Very complex
- Might break on different Android versions
- Not actually needed (trampolines not required)

---

## STEP 4: Execute Fix - Option B (Patch Makefile.am)

**Selected: Option B - Patch Makefile.am to exclude tramp.c**

**Rationale:**
1. Most DIRECT solution - controls what gets compiled
2. GUARANTEED to work - no tramp.c in build = no error
3. We already successfully patch files (Patch #1 works!)
4. Simple text replacement, no M4 knowledge needed
5. Trampolines not needed for Android anyway

**Implementation Plan:**
1. After patching configure.ac, also patch Makefile.am
2. Find `libffi_la_SOURCES` or `_SOURCES` variable
3. Remove lines with `tramp.c` or `tramp.lo`
4. OR comment out those lines
5. autoreconf will generate Makefile without tramp.c
6. Compilation succeeds!

**Code strategy:**
```python
# Read Makefile.am
makefile_am_path = os.path.join(build_dir, 'Makefile.am')
with open(makefile_am_path, 'r') as f:
    lines = f.readlines()

# Find and comment out lines with tramp
new_lines = []
for line in lines:
    if 'tramp.c' in line or 'tramp.lo' in line:
        new_lines.append('# GENESIS PATCH: ' + line)
    else:
        new_lines.append(line)

# Write back
with open(makefile_am_path, 'w') as f:
    f.writelines(new_lines)
```

**Expected Result:**
- autoreconf: ✅ (Patch #1 working)
- configure: ✅ (will be generated from patched Makefile.am)
- make: ✅ (Makefile won't include src/tramp.lo)
- libffi builds successfully!

---

## Summary

**Build #27 Failure:**
- Patches were APPLIED but had NO EFFECT
- Shell variables don't work in configure.ac M4 source
- Need to patch at a different level

**Root Cause:**
- Mixed up "configure source" vs "configure execution"
- configure.ac needs M4 macros, not shell variables
- Shell variables are for runtime environment

**Next Step - Build #28:**
- Patch Makefile.am to exclude src/tramp.c from build
- Direct, simple, guaranteed to work!

**Confidence: VERY HIGH** - Directly removes problematic file from build!
