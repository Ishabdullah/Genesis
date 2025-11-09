# Build #20 Error Analysis

## 🔴 CRITICAL ERRORS

### Error 1: LT_SYS_SYMBOL_USCORE undefined macro
**Line:** `configure.ac:223: error: possibly undefined macro: LT_SYS_SYMBOL_USCORE`
**Severity:** CRITICAL - Build-blocking
**When:** During autoreconf execution
**Why:** Modern autoconf 2.71 doesn't have this obsolete libtool macro

---

## ⚠️ WARNINGS (Non-blocking but indicate issues)

### Warning 1: STDC_HEADERS obsolete
**Line:** `configure.ac:92: warning: The preprocessor macro 'STDC_HEADERS' is obsolete`
**Severity:** WARNING - Doesn't block build
**Impact:** Informational only

### Warning 2: AC_TRY_COMPILE obsolete
**Line:** `configure.ac:127: warning: The macro 'AC_TRY_COMPILE' is obsolete`
**Severity:** WARNING - Doesn't block build
**Impact:** Informational only

---

## 🔍 KEY OBSERVATIONS

### Observation 1: Our custom recipe IS loading
**Evidence:** Log shows `🎯 USING LIBFFI 3.4.4 OFFICIAL RELEASE`
**Meaning:** The p4a-recipes/libffi/__init__.py file is being executed

### Observation 2: autoreconf is STILL being called
**Evidence:** `RAN: /usr/bin/autoreconf -vif`
**Traceback shows:**
```
File "/home/runner/work/Genesis/Genesis/p4a-recipes/libffi/__init__.py", line 36, in build_arch
    super().build_arch(arch)
File "...python-for-android/pythonforandroid/recipes/libffi/__init__.py", line 29, in build_arch
    shprint(sh.Command('autoreconf'), '-vif', _env=env)
```
**Meaning:** Parent LibffiRecipe ALWAYS runs autoreconf, even if configure exists!

### Observation 3: Our URL change worked
**Evidence:** Build is using libffi 3.4.4 (we specified that URL)
**But:** p4a's base recipe still regenerates configure

---

## 💡 ROOT CAUSE IDENTIFIED

**The Problem:**
p4a's LibffiRecipe has `autoreconf` hardcoded in its build_arch() method at line 29. It ALWAYS regenerates configure from configure.ac, regardless of whether configure already exists in the tarball.

**Why our Attempt #11 failed:**
We changed the URL to official release (which has configure), but calling `super().build_arch(arch)` executes the parent's code which runs autoreconf anyway!

---

## 📊 COMPARISON TO PREVIOUS FIXES

| Attempt | Approach | Why it failed |
|---------|----------|---------------|
| 1-7 | Config changes, NDK versions | Didn't address autoreconf issue |
| 8 | Custom recipe with patching | Recipe never executed |
| 9 | p4a hook | Hook didn't run at right time |
| 10 | No custom overrides | libffi 3.4.2 still has the macro |
| 11 | Official release URL | Parent recipe runs autoreconf anyway! |

**Pattern:** We keep hitting the autoreconf + LT_SYS_SYMBOL_USCORE issue because p4a ALWAYS runs autoreconf.

---

## 🎯 NEW FIXES TO TRY

### Option A: Patch configure.ac BEFORE calling super() ⭐ BEST
**How:**
1. In our custom recipe's build_arch()
2. Read configure.ac from extracted source
3. Replace LT_SYS_SYMBOL_USCORE line with safe default
4. Write patched configure.ac back
5. THEN call super().build_arch() which will run autoreconf on patched file

**Pros:** Works with p4a's existing logic, clean approach
**Cons:** None
**Priority:** TRY FIRST

### Option B: Override build_arch completely (skip autoreconf)
**How:**
1. Copy entire parent build_arch() code
2. Remove the autoreconf line
3. Run configure directly

**Pros:** Total control
**Cons:** Fragile, breaks if p4a updates recipe, complex to maintain
**Priority:** TRY IF OPTION A FAILS

### Option C: Use ubuntu-20.04 runner (older autoconf)
**How:**
1. Change GitHub Actions to use ubuntu-20.04
2. Ubuntu 20.04 has autoconf 2.69 which might still have the macro

**Pros:** Avoids patching
**Cons:** Uses older system, might have other issues
**Priority:** TRY IF OPTIONS A & B FAIL

### Option D: Use p4a develop branch with fork
**How:**
1. Fork python-for-android
2. Update libffi recipe in fork
3. Use custom fork in buildozer.spec

**Pros:** Clean solution
**Cons:** Requires maintaining fork, slow to implement
**Priority:** LAST RESORT

---

## ✅ RECOMMENDED EXECUTION ORDER

1. **TRY NOW:** Option A - Patch configure.ac in custom recipe before super()
2. If fails: Option B - Override build_arch completely
3. If fails: Option C - Try ubuntu-20.04 runner
4. If fails: Option D - Fork p4a

---

## 📝 DETAILED FIX FOR OPTION A

Update `p4a-recipes/libffi/__init__.py`:

```python
def build_arch(self, arch):
    """
    Patch configure.ac BEFORE parent runs autoreconf
    """
    # Get build directory
    build_dir = self.get_build_dir(arch.arch)
    configure_ac = os.path.join(build_dir, 'configure.ac')

    print("=" * 70)
    print("🔧 PATCHING LIBFFI CONFIGURE.AC BEFORE AUTORECONF")
    print("=" * 70)

    # Read configure.ac
    with open(configure_ac, 'r') as f:
        content = f.read()

    # Patch the LT_SYS_SYMBOL_USCORE line
    patched = content.replace(
        'if test "x$LT_SYS_SYMBOL_USCORE" = xyes; then',
        '# PATCHED: LT_SYS_SYMBOL_USCORE is obsolete\nif test "xno" = xyes; then'
    )

    # Write patched file
    with open(configure_ac, 'w') as f:
        f.write(patched)

    print("✅ Patched configure.ac successfully!")
    print("=" * 70)

    # Now call parent which will run autoreconf on PATCHED file
    super().build_arch(arch)
```

This should work because:
1. Our recipe loads (we see the print)
2. We patch BEFORE autoreconf runs
3. Autoreconf runs on patched file
4. Build succeeds!
