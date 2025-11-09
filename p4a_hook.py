#!/usr/bin/env python3
"""
p4a pre-build hook to patch libffi configure.ac before building
This patches the obsolete LT_SYS_SYMBOL_USCORE macro
"""
import os
import sys
from pathlib import Path

def find_libffi_source():
    """Find libffi source directory in p4a build"""
    # p4a downloads libffi to build/other_builds/libffi/
    current = Path.cwd()

    # Search for libffi configure.ac in buildozer directory
    buildozer_dir = current / '.buildozer'
    if buildozer_dir.exists():
        for configure_ac in buildozer_dir.rglob('configure.ac'):
            # Check if this is libffi by looking for the problematic macro
            try:
                content = configure_ac.read_text()
                if 'LT_SYS_SYMBOL_USCORE' in content and 'libffi' in str(configure_ac):
                    return configure_ac
            except:
                continue

    return None

def patch_libffi_configure(configure_ac_path):
    """Patch configure.ac to remove obsolete macro"""
    print("=" * 70)
    print("🔧 P4A HOOK: PATCHING LIBFFI FOR MODERN AUTOTOOLS")
    print("=" * 70)
    print(f"📁 Found configure.ac at: {configure_ac_path}")

    # Read the file
    content = configure_ac_path.read_text()

    # Check if already patched
    if 'PATCHED: Removed obsolete LT_SYS_SYMBOL_USCORE' in content:
        print("✓ Already patched, skipping")
        print("=" * 70)
        return True

    # Patch 1: Replace the line that uses LT_SYS_SYMBOL_USCORE
    original = 'if test "x$LT_SYS_SYMBOL_USCORE" = xyes; then'
    if original in content:
        replacement = (
            '# PATCHED: Removed obsolete LT_SYS_SYMBOL_USCORE macro\n'
            '# Defaulting to no underscore prefix (modern systems)\n'
            'if test "xno" = xyes; then'
        )
        content = content.replace(original, replacement)
        print("✓ Patched LT_SYS_SYMBOL_USCORE usage")
    else:
        print("⚠️  Warning: LT_SYS_SYMBOL_USCORE usage not found in expected format")

    # Patch 2: Comment out SYMBOL_UNDERSCORE AC_DEFINE
    original_define = 'AC_DEFINE(SYMBOL_UNDERSCORE,1,[Define if symbols are underscored.])'
    if original_define in content:
        content = content.replace(
            original_define,
            '# PATCHED: Removed SYMBOL_UNDERSCORE definition'
        )
        print("✓ Patched SYMBOL_UNDERSCORE AC_DEFINE")

    # Patch 3: Remove the LT_SYS_SYMBOL_USCORE macro call itself
    original_macro = 'LT_SYS_SYMBOL_USCORE'
    # Only patch it if it appears on its own line (not in comments we added)
    lines = content.split('\n')
    patched_lines = []
    for line in lines:
        if original_macro in line and not line.strip().startswith('#'):
            patched_lines.append('# PATCHED: ' + line)
            print(f"✓ Commented out line: {line.strip()}")
        else:
            patched_lines.append(line)
    content = '\n'.join(patched_lines)

    # Write the patched file
    configure_ac_path.write_text(content)
    print("✓ Wrote patched configure.ac")
    print("=" * 70)
    return True

def main():
    """Main hook entry point"""
    print("\n" + "=" * 70)
    print("🎯 P4A HOOK STARTED - Searching for libffi...")
    print("=" * 70)

    # Try to find and patch libffi
    configure_ac = find_libffi_source()

    if configure_ac:
        patch_libffi_configure(configure_ac)
        print("✅ Hook completed successfully")
        return 0
    else:
        print("ℹ️  libffi configure.ac not found yet (will patch during build)")
        print("=" * 70)
        # Don't fail - libffi might not be downloaded yet
        return 0

if __name__ == '__main__':
    sys.exit(main())
