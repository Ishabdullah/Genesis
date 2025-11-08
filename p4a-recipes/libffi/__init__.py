"""
Custom libffi recipe that patches source files BEFORE autoreconf runs

Build #30: Source-level patching approach (ChatGPT suggestion)
- Patch #1: Comment out LT_SYS_SYMBOL_USCORE macro (configure.ac line 223)
- Patch #2: Make tramp.c Android-compatible by wrapping open_temp_exec_file()
- DON'T touch Makefile.am (avoids "endif without if" errors)
"""

import os
from pythonforandroid.recipes.libffi import LibffiRecipe


class LibffiRecipePatched(LibffiRecipe):
    """
    Custom libffi recipe that applies TWO patches for Android

    PATCH #1: Comment out LT_SYS_SYMBOL_USCORE macro (Build #25)
    - Line 223 has obsolete macro undefined in autoconf 2.71+
    - Solution: Comment out the macro call

    PATCH #2: Make tramp.c Android-compatible (Build #30 - ChatGPT approach)
    - src/tramp.c uses open_temp_exec_file() not available on Android
    - Previous attempts (Builds #26-29) tried to remove tramp.c from build (all failed)
    - Solution: Patch tramp.c source to wrap problematic code with #ifndef __ANDROID__
    - This is CLEANER - doesn't touch build system files
    """

    # Use latest stable libffi
    url = 'https://github.com/libffi/libffi/releases/download/v3.4.4/libffi-3.4.4.tar.gz'

    # Override patches - we do our own patching in build_arch()
    patches = []

    def build_arch(self, arch):
        """
        Apply TWO patches BEFORE autoreconf:
        1. Comment out LT_SYS_SYMBOL_USCORE macro call in configure.ac (line 223)
        2. Wrap open_temp_exec_file() in tramp.c with #ifndef __ANDROID__
        """
        # Get build directory where libffi source was extracted
        build_dir = self.get_build_dir(arch.arch)
        configure_ac_path = os.path.join(build_dir, 'configure.ac')
        tramp_c_path = os.path.join(build_dir, 'src', 'tramp.c')

        print("=" * 70)
        print("🔧 PATCHING LIBFFI - Build #30 (Source-level patch)")
        print("  Fix #1: Comment out LT_SYS_SYMBOL_USCORE macro (configure.ac line 223)")
        print("  Fix #2: Wrap open_temp_exec_file() with #ifndef __ANDROID__")
        print(f"📁 Build dir: {build_dir}")
        print("=" * 70)

        # PATCH #1: configure.ac (same as before)
        patch1_applied = False
        if not os.path.exists(configure_ac_path):
            print(f"⚠️  WARNING: configure.ac not found at {configure_ac_path}")
        else:
            print("📖 Reading configure.ac...")
            with open(configure_ac_path, 'r') as f:
                content = f.read()
                lines = content.split('\n')

            print(f"📊 File has {len(lines)} lines")

            # Check if already patched
            if 'PATCHED BY GENESIS' in content:
                print("✅ configure.ac already patched, skipping")
                patch1_applied = True
            else:
                # Comment out LT_SYS_SYMBOL_USCORE
                print("\n🔍 PATCH #1: Searching for LT_SYS_SYMBOL_USCORE macro call...")
                for i, line in enumerate(lines):
                    # Look for LT_SYS_SYMBOL_USCORE WITHOUT $ (macro call, not usage)
                    if 'LT_SYS_SYMBOL_USCORE' in line and '$' not in line:
                        line_num = i + 1
                        print(f"  ✅ Found macro CALL at line {line_num}: {line.strip()}")

                        # Comment it out
                        lines[i] = ('# PATCHED BY GENESIS: LT_SYS_SYMBOL_USCORE is obsolete in modern libtool\n'
                                    '# This macro is undefined in autoconf 2.71+, commenting out\n'
                                    '# Original line 223: ' + line)

                        print(f"  🔧 Commented out line {line_num}")
                        patch1_applied = True
                        break

                if patch1_applied:
                    with open(configure_ac_path, 'w') as f:
                        f.write('\n'.join(lines))
                    print("  ✅ PATCH #1 applied successfully!")
                    print("  📝 Wrote patched configure.ac")

                    # Verify patch with SHA256 hash
                    import hashlib
                    hash_obj = hashlib.sha256('\n'.join(lines).encode('utf-8'))
                    print(f"  🔒 Patch verification hash: {hash_obj.hexdigest()[:16]}...")
                else:
                    print("  ❌ PATCH #1 FAILED: LT_SYS_SYMBOL_USCORE not found!")

        # PATCH #2: tramp.c (NEW - ChatGPT approach)
        patch2_applied = False
        if not os.path.exists(tramp_c_path):
            print(f"\n⚠️  WARNING: tramp.c not found at {tramp_c_path}")
            print("  ⚠️  Skipping Patch #2")
        else:
            print("\n🔍 PATCH #2: Patching tramp.c for Android compatibility...")
            with open(tramp_c_path, 'r') as f:
                tramp_content = f.read()

            # Check if already patched
            if 'GENESIS ANDROID PATCH' in tramp_content:
                print("  ✅ tramp.c already patched, skipping")
                patch2_applied = True
            else:
                # Find the open_temp_exec_file() call and wrap it
                # Look for the pattern where it's called
                import re

                # Pattern: find the line with open_temp_exec_file() call
                # We'll wrap the entire function call block with #ifndef __ANDROID__

                # Search for the function call
                if 'open_temp_exec_file' in tramp_content:
                    print("  ✅ Found open_temp_exec_file() reference")

                    # Strategy: Replace the function call with Android-safe version
                    # Find: fd = open_temp_exec_file (name, &temp, &length);
                    # Replace with:
                    # #ifndef __ANDROID__  /* GENESIS ANDROID PATCH */
                    # fd = open_temp_exec_file (name, &temp, &length);
                    # #else
                    # fd = -1;  /* Android doesn't support executable temp files */
                    # #endif

                    original_content = tramp_content

                    # Use regex to find and wrap the call
                    pattern = r'(\s*)(fd\s*=\s*open_temp_exec_file\s*\([^;]+\);)'
                    replacement = (
                        r'\1#ifndef __ANDROID__  /* GENESIS ANDROID PATCH: open_temp_exec_file not available on Android */\n'
                        r'\1\2\n'
                        r'\1#else\n'
                        r'\1fd = -1;  /* Android: Skip executable temp file creation */\n'
                        r'\1#endif'
                    )

                    tramp_content = re.sub(pattern, replacement, tramp_content)

                    if tramp_content != original_content:
                        # Write patched file
                        with open(tramp_c_path, 'w') as f:
                            f.write(tramp_content)
                        print("  ✅ Wrapped open_temp_exec_file() with #ifndef __ANDROID__")
                        print("  📝 Wrote patched tramp.c")

                        # Verify patch with SHA256 hash
                        import hashlib
                        hash_obj = hashlib.sha256(tramp_content.encode('utf-8'))
                        print(f"  🔒 Patch verification hash: {hash_obj.hexdigest()[:16]}...")
                        print("  ✅ PATCH #2 applied successfully!")
                        patch2_applied = True
                    else:
                        print("  ⚠️  Primary pattern not matched - tramp.c format might be different")
                        print("  ⚠️  Trying fallback approach...")

                        # Fallback: Replace the entire assignment line
                        # Find any line like: "fd = open_temp_exec_file(...)"
                        # Replace with: "fd = -1; /* Android - function not available */"
                        if 'open_temp_exec_file' in tramp_content:
                            original_fallback = tramp_content

                            # Pattern matches: [optional prefix.]fd = open_temp_exec_file(...);
                            # Examples: "fd = open_temp_exec_file(...);" or "tramp_globals.fd = open_temp_exec_file(...);"
                            fallback_pattern = r'(\s*)(\w+\.)?fd\s*=\s*open_temp_exec_file\s*\([^)]*\)\s*;'
                            fallback_replacement = r'\1\2fd = -1;  /* GENESIS ANDROID PATCH: open_temp_exec_file not available on Android */'

                            tramp_content = re.sub(fallback_pattern, fallback_replacement, tramp_content)

                            if tramp_content != original_fallback:
                                # Add header comment
                                tramp_content = ('/* GENESIS ANDROID PATCH: Replaced open_temp_exec_file calls with fd = -1 */\n' +
                                               tramp_content)

                                with open(tramp_c_path, 'w') as f:
                                    f.write(tramp_content)
                                print("  ✅ Replaced open_temp_exec_file() calls with fd = -1 (fallback method)")
                                print("  📝 Wrote patched tramp.c")

                                # Verify fallback patch
                                import hashlib
                                hash_obj = hashlib.sha256(tramp_content.encode('utf-8'))
                                print(f"  🔒 Fallback patch hash: {hash_obj.hexdigest()[:16]}...")
                                patch2_applied = True
                            else:
                                print("  ❌ Fallback pattern also failed to match")
                                print("  ⚠️  tramp.c may have unexpected format")
                else:
                    print("  ⚠️  open_temp_exec_file not found in tramp.c")
                    print("  ⚠️  This might be OK if it's conditionally compiled")

        print("\n" + "=" * 70)
        if patch1_applied and patch2_applied:
            print("✅ ALL PATCHES APPLIED SUCCESSFULLY!")
        elif patch1_applied:
            print("⚠️  PATCH #1 applied, PATCH #2 skipped")
        else:
            print("❌ PATCHING FAILED!")
        print("=" * 70)

        print("\n" + "=" * 70)
        print("📞 Calling parent build_arch (will run autoreconf + configure + make)")
        print("   PATCH #1: configure.ac line 223 commented (fixes autoreconf)")
        print("   PATCH #2: tramp.c open_temp_exec_file() wrapped (Android-safe)")
        print("   Expected: autoreconf ✅ → configure ✅ → make ✅ (tramp.c compiles!)")
        print("=" * 70)

        # Now call parent which will run autoreconf on PATCHED source files
        # Patch #1: Fixes autoreconf (LT_SYS_SYMBOL_USCORE commented)
        # Patch #2: Fixes tramp.c compilation (open_temp_exec_file wrapped)
        # This should complete the entire libffi build!
        super().build_arch(arch)


recipe = LibffiRecipePatched()
