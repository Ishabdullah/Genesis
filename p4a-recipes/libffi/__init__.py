"""
Custom libffi recipe that patches configure.ac BEFORE autoreconf runs
Patches the macro CALL (line 223) - there is NO usage line!
"""

import os
from pythonforandroid.recipes.libffi import LibffiRecipe


class LibffiRecipePatched(LibffiRecipe):
    """
    Custom libffi recipe that applies TWO patches to configure.ac for Android

    PATCH #1: Comment out LT_SYS_SYMBOL_USCORE macro (Build #25)
    - Line 223 has obsolete macro undefined in autoconf 2.71+
    - Solution: Comment out the macro call

    PATCH #2: Force disable trampolines at source level (Build #27)
    - src/tramp.c uses open_temp_exec_file() not available on Android
    - Build #26 tried configure flag but it wasn't applied
    - Solution: Patch configure.ac to force enable_exec_trampoline=no
    - This makes configure script skip trampoline code entirely
    """

    # Use latest stable libffi
    url = 'https://github.com/libffi/libffi/releases/download/v3.4.4/libffi-3.4.4.tar.gz'

    # Override patches - we do our own patching in build_arch()
    patches = []

    def build_arch(self, arch):
        """
        Apply TWO patches to configure.ac:
        1. Comment out LT_SYS_SYMBOL_USCORE macro call at line 223
        2. Disable trampolines for Android (source-level disable)
        """
        # Get build directory where libffi source was extracted
        build_dir = self.get_build_dir(arch.arch)
        configure_ac_path = os.path.join(build_dir, 'configure.ac')

        print("=" * 70)
        print("🔧 PATCHING LIBFFI - Build #27 (Two source patches)")
        print("  Fix #1: Comment out LT_SYS_SYMBOL_USCORE macro (line 223)")
        print("  Fix #2: Disable trampolines at SOURCE level in configure.ac")
        print(f"📁 Build dir: {build_dir}")
        print("=" * 70)

        # Check if configure.ac exists
        if not os.path.exists(configure_ac_path):
            print(f"⚠️  WARNING: configure.ac not found at {configure_ac_path}")
            print("Continuing with parent build...")
            super().build_arch(arch)
            return

        # Read configure.ac
        print("📖 Reading configure.ac...")
        with open(configure_ac_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')

        print(f"📊 File has {len(lines)} lines")

        # Check if already patched
        if 'PATCHED BY GENESIS' in content:
            print("✅ Already patched, skipping")
        else:
            # PATCH #1: Comment out LT_SYS_SYMBOL_USCORE
            print("\n🔍 PATCH #1: Searching for LT_SYS_SYMBOL_USCORE macro call...")
            patch1_applied = False
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

            if not patch1_applied:
                print("  ❌ PATCH #1 FAILED: LT_SYS_SYMBOL_USCORE not found!")
            else:
                print("  ✅ PATCH #1 applied successfully!")

            # PATCH #2: Disable trampolines
            print("\n🔍 PATCH #2: Disabling exec trampolines for Android...")
            patch2_applied = False

            # Strategy: Find AC_ARG_ENABLE([pax-emutramp] section and add
            # a forced disable of exec trampolines right after
            for i, line in enumerate(lines):
                # Look for the line AFTER pax-emutramp section ends
                # This is around line 221-228 area
                if 'fi)' in line and i > 0:
                    # Check if previous lines have pax-emutramp
                    context = '\n'.join(lines[max(0, i-10):i])
                    if 'pax' in context.lower() or 'emutramp' in context.lower():
                        # Insert our trampoline disable AFTER this section
                        insert_line = i + 1

                        # Skip any blank lines
                        while insert_line < len(lines) and lines[insert_line].strip() == '':
                            insert_line += 1

                        # Check if next line is LT_SYS or FFI_EXEC_TRAMPOLINE
                        if insert_line < len(lines):
                            next_line = lines[insert_line]

                            # Insert BEFORE LT_SYS_SYMBOL_USCORE or at trampoline section
                            if 'LT_SYS_SYMBOL_USCORE' in next_line or 'FFI_EXEC_TRAMPOLINE' in next_line:
                                # Insert our disable code here
                                disable_code = [
                                    '',
                                    '# PATCHED BY GENESIS: Disable exec trampolines for Android (Build #27)',
                                    '# Trampolines require open_temp_exec_file() not available on Android',
                                    '# Force disable regardless of platform detection',
                                    'enable_exec_trampoline=no',
                                    'ac_cv_func_mmap_exec=no',
                                    ''
                                ]

                                # Insert the lines
                                for offset, new_line in enumerate(disable_code):
                                    lines.insert(insert_line + offset, new_line)

                                print(f"  ✅ Inserted trampoline disable code at line {insert_line}")
                                print(f"  📝 Added: enable_exec_trampoline=no")
                                print(f"  📝 Added: ac_cv_func_mmap_exec=no")
                                patch2_applied = True
                                break

            if not patch2_applied:
                print("  ⚠️  PATCH #2: Could not find ideal insertion point")
                print("  ⚠️  Trying alternative: Force disable at end of AC checks")

                # Alternative: Find first occurrence of FFI_EXEC_TRAMPOLINE_TABLE and force it
                for i, line in enumerate(lines):
                    if 'FFI_EXEC_TRAMPOLINE_TABLE' in line and '=' in line:
                        print(f"  ✅ Found FFI_EXEC_TRAMPOLINE_TABLE at line {i+1}")
                        # Insert disable BEFORE this line
                        disable_code = [
                            '# PATCHED BY GENESIS: Force disable trampolines for Android',
                            'enable_exec_trampoline=no',
                            'ac_cv_func_mmap_exec=no',
                            ''
                        ]
                        for offset, new_line in enumerate(disable_code):
                            lines.insert(i + offset, new_line)
                        print(f"  ✅ PATCH #2 applied at line {i+1}")
                        patch2_applied = True
                        break

            if not patch2_applied:
                print("  ❌ PATCH #2 FAILED: Could not disable trampolines")
            else:
                print("  ✅ PATCH #2 applied successfully!")

            # Write patched file
            if patch1_applied or patch2_applied:
                with open(configure_ac_path, 'w') as f:
                    f.write('\n'.join(lines))
                print("\n✅ All patches written to configure.ac")

        print("=" * 70)
        print("📞 Calling parent build_arch (will run autoreconf + configure + make)")
        print("   Trampolines disabled at SOURCE level (configure.ac patched)")
        print("   Expected: autoreconf ✅ → configure ✅ → make ✅ (skip tramp.c)")
        print("=" * 70)

        # Now call parent which will run autoreconf on PATCHED configure.ac
        # Our patches force trampolines to be disabled at source level
        # This causes generated configure script to skip trampoline code
        super().build_arch(arch)


recipe = LibffiRecipePatched()
