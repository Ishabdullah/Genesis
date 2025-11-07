"""
Custom libffi recipe that patches configure.ac BEFORE autoreconf runs
This fixes the LT_SYS_SYMBOL_USCORE obsolete macro issue with modern autoconf
"""

import os
from pythonforandroid.recipes.libffi import LibffiRecipe
from pythonforandroid.logger import shprint


class LibffiRecipePatched(LibffiRecipe):
    """
    Custom libffi recipe that patches configure.ac before parent runs autoreconf

    The issue: p4a's LibffiRecipe always runs autoreconf, which fails with modern
    autoconf 2.71 because LT_SYS_SYMBOL_USCORE macro was removed from libtool.

    The fix: Patch configure.ac to replace the obsolete macro before autoreconf runs.
    """

    # Use latest stable libffi
    url = 'https://github.com/libffi/libffi/releases/download/v3.4.4/libffi-3.4.4.tar.gz'

    def build_arch(self, arch):
        """
        Patch configure.ac BEFORE parent runs autoreconf
        """
        # Get build directory where libffi source was extracted
        build_dir = self.get_build_dir(arch.arch)
        configure_ac_path = os.path.join(build_dir, 'configure.ac')

        print("=" * 70)
        print("🔧 PATCHING LIBFFI CONFIGURE.AC FOR MODERN AUTOCONF")
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

        # Check if already patched
        if 'PATCHED: LT_SYS_SYMBOL_USCORE' in content:
            print("✅ Already patched, skipping")
        else:
            # Patch 1: Replace the LT_SYS_SYMBOL_USCORE usage
            original_line = 'if test "x$LT_SYS_SYMBOL_USCORE" = xyes; then'
            if original_line in content:
                patched_content = content.replace(
                    original_line,
                    '# PATCHED: LT_SYS_SYMBOL_USCORE is obsolete in modern libtool\n'
                    '# Defaulting to "no" (modern systems don\'t use underscore prefix)\n'
                    'if test "xno" = xyes; then'
                )

                # Write patched file
                with open(configure_ac_path, 'w') as f:
                    f.write(patched_content)

                print("✅ Patched LT_SYS_SYMBOL_USCORE successfully!")
                print("   Replaced with safe default value")
            else:
                print(f"⚠️  WARNING: Could not find expected line in configure.ac")
                print(f"   Looking for: {original_line}")
                print("   Continuing anyway...")

        print("=" * 70)
        print("📞 Calling parent build_arch (will run autoreconf on patched file)")
        print("=" * 70)

        # Now call parent which will run autoreconf on PATCHED configure.ac
        super().build_arch(arch)


recipe = LibffiRecipePatched()
