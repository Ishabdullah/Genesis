"""
Custom libffi recipe that patches configure.ac BEFORE autoreconf runs
ONLY patches the CRITICAL blocker - LT_SYS_SYMBOL_USCORE USAGE (not the macro call!)
"""

import os
from pythonforandroid.recipes.libffi import LibffiRecipe


class LibffiRecipePatched(LibffiRecipe):
    """
    Custom libffi recipe that patches ONLY the critical blocker in configure.ac

    Build #23 lesson: We patched the macro CALL, not the USAGE!
    - Line 223 has: LT_SYS_SYMBOL_USCORE (macro call - WRONG to patch!)
    - Need to find: if test "x$LT_SYS_SYMBOL_USCORE" = xyes; then (USAGE - patch this!)

    The $ is critical - it means variable reference, not macro call.
    """

    # Use latest stable libffi
    url = 'https://github.com/libffi/libffi/releases/download/v3.4.4/libffi-3.4.4.tar.gz'

    # Override patches - we do our own patching in build_arch()
    patches = []

    def build_arch(self, arch):
        """
        Patch ONLY the LT_SYS_SYMBOL_USCORE USAGE (with $) in configure.ac
        """
        # Get build directory where libffi source was extracted
        build_dir = self.get_build_dir(arch.arch)
        configure_ac_path = os.path.join(build_dir, 'configure.ac')

        print("=" * 70)
        print("🔧 PATCHING LIBFFI - USAGE LINE ONLY (not macro call!)")
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
            print("🔍 Searching for LT_SYS_SYMBOL_USCORE USAGE (with $)...")

            # MUST have $ to be a variable reference (usage), not macro call
            patterns_to_try = [
                ('exact_if_test', 'if test "x$LT_SYS_SYMBOL_USCORE" = xyes; then'),
                ('quoted_if_test', 'if test "x$LT_SYS_SYMBOL_USCORE" = "xyes"; then'),
                ('any_dollar_ref', '$LT_SYS_SYMBOL_USCORE'),  # At minimum, must have $
            ]

            found_pattern = None
            found_line_num = None

            for pattern_name, pattern in patterns_to_try:
                if pattern in content:
                    print(f"  ✅ Found {pattern_name} pattern: '{pattern}'")
                    # Find line number and show context
                    for i, line in enumerate(lines, 1):
                        if pattern in line:
                            found_line_num = i
                            found_pattern = pattern
                            print(f"  📍 At line {i}: {line.strip()}")

                            # Show context (5 lines before and after)
                            print(f"  📄 Context:")
                            start = max(0, i - 6)  # -6 because enumerate starts at 1
                            end = min(len(lines), i + 4)
                            for j in range(start, end):
                                marker = "→→→" if j == i - 1 else "   "
                                print(f"    {marker} Line {j+1}: {lines[j]}")
                            break
                    break

            if not found_pattern:
                print("  ❌ LT_SYS_SYMBOL_USCORE USAGE not found!")
                print("  🔎 Searching for ALL lines containing 'LT_SYS_SYMBOL_USCORE':")
                for i, line in enumerate(lines, 1):
                    if 'LT_SYS_SYMBOL_USCORE' in line:
                        has_dollar = '$' in line
                        symbol = "💲" if has_dollar else "🔤"
                        print(f"    {symbol} Line {i}: {line.strip()}")
                print("  📝 Legend: 💲 = has $ (usage), 🔤 = no $ (macro call)")
                print("  ⚠️  Cannot patch - proceeding anyway (will likely fail)")
            else:
                # PATCH IT!
                print(f"  🔧 Patching line {found_line_num}...")

                # For safety, only replace if it's an if-test pattern
                if 'if test' in found_pattern:
                    # Replace the entire if-test line
                    patched_content = content.replace(
                        found_pattern,
                        '# PATCHED BY GENESIS: LT_SYS_SYMBOL_USCORE is obsolete\n'
                        '# Original: ' + found_pattern + '\n'
                        '# Fixed: Default to "no" (modern systems have no underscore prefix)\n'
                        'if test "xno" = xyes; then'
                    )
                else:
                    # Just comment out the line if it's not an if-test
                    patched_content = content.replace(
                        found_pattern,
                        '# PATCHED BY GENESIS: ' + found_pattern
                    )

                # Verify patch worked
                if 'PATCHED BY GENESIS' in patched_content:
                    # Write patched file
                    with open(configure_ac_path, 'w') as f:
                        f.write(patched_content)
                    print("  ✅ Patch applied successfully!")
                    print(f"  📝 Replaced '{found_pattern[:50]}...'")
                else:
                    print("  ❌ Patch failed to apply!")

        print("=" * 70)
        print("📞 Calling parent build_arch (will run autoreconf on patched file)")
        print("=" * 70)

        # Now call parent which will run autoreconf on PATCHED configure.ac
        super().build_arch(arch)


recipe = LibffiRecipePatched()
