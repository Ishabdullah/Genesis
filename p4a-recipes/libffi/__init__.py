"""
Custom libffi recipe that patches configure.ac BEFORE autoreconf runs
Patches the macro CALL (line 223) - there is NO usage line!
"""

import os
from pythonforandroid.recipes.libffi import LibffiRecipe


class LibffiRecipePatched(LibffiRecipe):
    """
    Custom libffi recipe that patches the LT_SYS_SYMBOL_USCORE macro CALL

    Build #24 discovery: There is ONLY line 223 with LT_SYS_SYMBOL_USCORE!
    - No $ usage line exists in libffi 3.4.4
    - Just the macro call: LT_SYS_SYMBOL_USCORE
    - This macro is undefined in modern autoconf
    - Solution: Comment it out entirely
    """

    # Use latest stable libffi
    url = 'https://github.com/libffi/libffi/releases/download/v3.4.4/libffi-3.4.4.tar.gz'

    # Override patches - we do our own patching in build_arch()
    patches = []

    def build_arch(self, arch):
        """
        Comment out the LT_SYS_SYMBOL_USCORE macro call at line 223
        """
        # Get build directory where libffi source was extracted
        build_dir = self.get_build_dir(arch.arch)
        configure_ac_path = os.path.join(build_dir, 'configure.ac')

        print("=" * 70)
        print("🔧 PATCHING LIBFFI - Comment out macro CALL (line 223)")
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
        print("📞 Calling parent build_arch (will run autoreconf on patched file)")
        print("=" * 70)

        # Now call parent which will run autoreconf on PATCHED configure.ac
        super().build_arch(arch)


recipe = LibffiRecipePatched()
