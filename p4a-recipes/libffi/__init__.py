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

    PATCH #2: Remove tramp.c from Makefile.am (Build #28 - DIRECT FIX)
    - src/tramp.c uses open_temp_exec_file() not available on Android
    - Build #26 tried configure flag (didn't work - not applied)
    - Build #27 tried shell vars in configure.ac (didn't work - wrong approach)
    - Solution: Patch Makefile.am to exclude tramp.c from SOURCES
    - When autoreconf runs, generated Makefile won't compile tramp.c
    - This is the MOST DIRECT approach - removes problematic file from build
    """

    # Use latest stable libffi
    url = 'https://github.com/libffi/libffi/releases/download/v3.4.4/libffi-3.4.4.tar.gz'

    # Override patches - we do our own patching in build_arch()
    patches = []

    def build_arch(self, arch):
        """
        Apply TWO patches BEFORE autoreconf:
        1. Comment out LT_SYS_SYMBOL_USCORE macro call in configure.ac (line 223)
        2. Remove tramp.c from Makefile.am SOURCES (direct exclusion)
        """
        # Get build directory where libffi source was extracted
        build_dir = self.get_build_dir(arch.arch)
        configure_ac_path = os.path.join(build_dir, 'configure.ac')
        makefile_am_path = os.path.join(build_dir, 'Makefile.am')

        print("=" * 70)
        print("🔧 PATCHING LIBFFI - Build #28 (Direct Makefile.am patch)")
        print("  Fix #1: Comment out LT_SYS_SYMBOL_USCORE macro (configure.ac line 223)")
        print("  Fix #2: Remove tramp.c from Makefile.am SOURCES (direct exclusion)")
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
            print("✅ configure.ac already patched, skipping")
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

            # Write patched configure.ac
            if patch1_applied:
                with open(configure_ac_path, 'w') as f:
                    f.write('\n'.join(lines))
                print("  📝 Wrote patched configure.ac")

        # PATCH #2: Remove tramp.c from Makefile.am
        print("\n🔍 PATCH #2: Patching Makefile.am to exclude tramp.c...")

        if not os.path.exists(makefile_am_path):
            print(f"  ⚠️  WARNING: Makefile.am not found at {makefile_am_path}")
            print("  ⚠️  Skipping Patch #2")
            patch2_applied = False
        else:
            with open(makefile_am_path, 'r') as f:
                makefile_content = f.read()

            if 'GENESIS TRAMP PATCH' in makefile_content:
                print("  ✅ Makefile.am already patched, skipping")
                patch2_applied = True
            else:
                makefile_lines = makefile_content.split('\n')
                patch2_applied = False
                removed_count = 0

                # Find and comment out all lines containing tramp
                new_makefile_lines = []
                for line in makefile_lines:
                    if 'tramp' in line.lower() and ('src/' in line or '.lo' in line or '.c' in line):
                        # This line references tramp source file
                        if not line.strip().startswith('#'):
                            new_makefile_lines.append('# GENESIS TRAMP PATCH: ' + line)
                            removed_count += 1
                            patch2_applied = True
                        else:
                            new_makefile_lines.append(line)
                    else:
                        new_makefile_lines.append(line)

                if patch2_applied:
                    # Write patched Makefile.am
                    with open(makefile_am_path, 'w') as f:
                        f.write('\n'.join(new_makefile_lines))
                    print(f"  ✅ Removed {removed_count} tramp.c references from Makefile.am")
                    print(f"  📝 Wrote patched Makefile.am")
                    print("  ✅ PATCH #2 applied successfully!")
                else:
                    print("  ⚠️  No tramp references found in Makefile.am")
                    print("  ⚠️  This might be OK if trampolines are conditionally included")

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
        print("   PATCH #2: Makefile.am tramp.c removed (fixes compilation)")
        print("   Expected: autoreconf ✅ → configure ✅ → make ✅ (NO tramp.c!)")
        print("=" * 70)

        # Now call parent which will run autoreconf on PATCHED source files
        # Patch #1: Fixes autoreconf (LT_SYS_SYMBOL_USCORE commented)
        # Patch #2: Fixes make (tramp.c excluded from Makefile)
        # This should complete the entire libffi build!
        super().build_arch(arch)


recipe = LibffiRecipePatched()
