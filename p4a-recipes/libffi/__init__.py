"""
Custom libffi recipe that patches configure.ac BEFORE autoreconf runs
ONLY patches the CRITICAL blocker - LT_SYS_SYMBOL_USCORE
"""

import os
from pythonforandroid.recipes.libffi import LibffiRecipe


class LibffiRecipePatched(LibffiRecipe):
    """
    Custom libffi recipe that patches ONLY the critical blocker in configure.ac

    CRITICAL FIX:
    - LT_SYS_SYMBOL_USCORE (obsolete macro that blocks build)

    WARNINGS IGNORED:
    - AC_HEADER_STDC (warning only, doesn't block)
    - AC_TRY_COMPILE (warning only, doesn't block)
    - STDC_HEADERS (warning only, doesn't block)

    Strategy: Patch the minimum needed to build successfully
    """

    # Use latest stable libffi
    url = 'https://github.com/libffi/libffi/releases/download/v3.4.4/libffi-3.4.4.tar.gz'

    # Override patches - we do our own patching in build_arch()
    patches = []

    def build_arch(self, arch):
        """
        Patch ONLY LT_SYS_SYMBOL_USCORE in configure.ac BEFORE parent runs autoreconf
        """
        # Get build directory where libffi source was extracted
        build_dir = self.get_build_dir(arch.arch)
        configure_ac_path = os.path.join(build_dir, 'configure.ac')

        print("=" * 70)
        print("🔧 PATCHING LIBFFI - CRITICAL BLOCKER ONLY")
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
            print("🔍 Searching for LT_SYS_SYMBOL_USCORE...")

            # Try multiple patterns to find the line
            patterns_to_try = [
                ('exact', 'if test "x$LT_SYS_SYMBOL_USCORE" = xyes; then'),
                ('quoted', 'if test "x$LT_SYS_SYMBOL_USCORE" = "xyes"; then'),
                ('spaced', 'if test "x$LT_SYS_SYMBOL_USCORE"  = xyes; then'),
                ('any_containing', 'LT_SYS_SYMBOL_USCORE'),
            ]

            found_pattern = None
            found_line_num = None

            for pattern_name, pattern in patterns_to_try:
                if pattern in content:
                    print(f"  ✅ Found {pattern_name} pattern: '{pattern}'")
                    # Find line number
                    for i, line in enumerate(lines, 1):
                        if pattern in line:
                            found_line_num = i
                            found_pattern = pattern
                            print(f"  📍 At line {i}: {line.strip()}")
                            break
                    break

            if not found_pattern:
                print("  ❌ LT_SYS_SYMBOL_USCORE not found with any pattern!")
                print("  🔎 Searching for lines containing 'SYMBOL' or 'USCORE':")
                for i, line in enumerate(lines, 1):
                    if 'SYMBOL' in line or 'USCORE' in line:
                        print(f"     Line {i}: {line.strip()}")
                print("  ⚠️  Cannot patch - proceeding anyway (might fail)")
            else:
                # PATCH IT!
                print(f"  🔧 Patching line {found_line_num}...")

                # Replace the found pattern with safe default
                patched_content = content.replace(
                    found_pattern,
                    '# PATCHED BY GENESIS: LT_SYS_SYMBOL_USCORE is obsolete in modern libtool\n'
                    '# Original: ' + found_pattern + '\n'
                    '# Defaulting to "no" (modern systems don\'t use underscore prefix)\n'
                    'if test "xno" = xyes; then'
                )

                # Verify patch worked
                if 'PATCHED BY GENESIS' in patched_content:
                    # Write patched file
                    with open(configure_ac_path, 'w') as f:
                        f.write(patched_content)
                    print("  ✅ Patch applied successfully!")
                else:
                    print("  ❌ Patch failed to apply!")

        print("=" * 70)
        print("📞 Calling parent build_arch (will run autoreconf on patched file)")
        print("=" * 70)

        # Now call parent which will run autoreconf on PATCHED configure.ac
        super().build_arch(arch)


recipe = LibffiRecipePatched()
