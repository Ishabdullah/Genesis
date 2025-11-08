"""
Custom libffi recipe that patches configure.ac BEFORE autoreconf runs
Patches the macro CALL (line 223) - there is NO usage line!
"""

import os
from pythonforandroid.recipes.libffi import LibffiRecipe


class LibffiRecipePatched(LibffiRecipe):
    """
    Custom libffi recipe that patches the LT_SYS_SYMBOL_USCORE macro CALL
    and disables trampolines for Android compatibility

    Build #24 discovery: There is ONLY line 223 with LT_SYS_SYMBOL_USCORE!
    - No $ usage line exists in libffi 3.4.4
    - Just the macro call: LT_SYS_SYMBOL_USCORE
    - This macro is undefined in modern autoconf
    - Solution: Comment it out entirely

    Build #25 discovery: Trampolines don't compile on Android!
    - src/tramp.c:262: undefined function 'open_temp_exec_file'
    - Trampolines not needed for Python/Kivy/pyjnius on Android
    - Solution: Disable with --without-exec-trampoline
    """

    # Use latest stable libffi
    url = 'https://github.com/libffi/libffi/releases/download/v3.4.4/libffi-3.4.4.tar.gz'

    # Override patches - we do our own patching in build_arch()
    patches = []

    # Disable trampolines for Android (Build #26 fix)
    # Trampolines require executable memory mapping not available on Android
    configured_args = ['--without-exec-trampoline']

    def build_arch(self, arch):
        """
        Comment out the LT_SYS_SYMBOL_USCORE macro call at line 223
        """
        # Get build directory where libffi source was extracted
        build_dir = self.get_build_dir(arch.arch)
        configure_ac_path = os.path.join(build_dir, 'configure.ac')

        print("=" * 70)
        print("🔧 PATCHING LIBFFI - Build #26 (Two fixes)")
        print("  Fix #1: Comment out LT_SYS_SYMBOL_USCORE macro (line 223)")
        print("  Fix #2: Disable trampolines (--without-exec-trampoline)")
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
            print("🔍 Searching for LT_SYS_SYMBOL_USCORE macro call...")

            patched = False
            for i, line in enumerate(lines):
                # Look for LT_SYS_SYMBOL_USCORE WITHOUT $ (macro call, not usage)
                if 'LT_SYS_SYMBOL_USCORE' in line and '$' not in line:
                    line_num = i + 1
                    print(f"  ✅ Found macro CALL at line {line_num}: {line.strip()}")

                    # Show context
                    print(f"  📄 Context (5 lines before and after):")
                    start = max(0, i - 5)
                    end = min(len(lines), i + 6)
                    for j in range(start, end):
                        marker = "→→→" if j == i else "   "
                        print(f"    {marker} Line {j+1}: {lines[j]}")

                    # Comment it out
                    lines[i] = ('# PATCHED BY GENESIS: LT_SYS_SYMBOL_USCORE is obsolete in modern libtool\n'
                                '# This macro is undefined in autoconf 2.71+, commenting out\n'
                                '# Original line 223: ' + line)

                    print(f"  🔧 Commented out line {line_num}")
                    print(f"  📝 Original: {line.strip()}")
                    print(f"  📝 Replaced with comment")
                    patched = True
                    break

            if not patched:
                print("  ❌ LT_SYS_SYMBOL_USCORE not found!")
                print("  ⚠️  This is unexpected - build will likely fail")
            else:
                # Write patched file
                with open(configure_ac_path, 'w') as f:
                    f.write('\n'.join(lines))
                print("  ✅ Patch applied successfully!")

        print("=" * 70)
        print("📞 Calling parent build_arch (will run autoreconf + configure + make)")
        print(f"   Configure args: {self.configured_args}")
        print("   Expected: autoreconf ✅ → configure ✅ → make ✅")
        print("=" * 70)

        # Now call parent which will run autoreconf on PATCHED configure.ac
        # with --without-exec-trampoline flag to skip trampoline compilation
        super().build_arch(arch)


recipe = LibffiRecipePatched()
