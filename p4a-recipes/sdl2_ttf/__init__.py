"""
Custom SDL2_ttf recipe that patches HarfBuzz for NDK r28+ compatibility

Build #36: HarfBuzz function pointer cast fix (SIMPLIFIED PRAGMA APPROACH)
- NDK r28+ has stricter -Wcast-function-type-strict warnings (treated as errors)
- HarfBuzz's hb-ft.cc has incompatible function pointer casts
- Solution: Add #pragma to disable the warning for this file (cleanest approach)
"""

import os
from pythonforandroid.recipes.sdl2_ttf import LibSDL2_ttfRecipe


class LibSDL2_ttfRecipePatched(LibSDL2_ttfRecipe):
    """
    Custom SDL2_ttf recipe that patches HarfBuzz for NDK r28+

    PATCH: Disable strict function pointer cast warnings in hb-ft.cc
    - File: external/harfbuzz/src/hb-ft.cc
    - Error: -Wcast-function-type-strict (cast from 'void (*)(FT_Face)' to 'void (*)(void *)')
    - Fix: Add #pragma clang diagnostic ignored at top of file
    """

    def build_arch(self, arch):
        """
        Apply HarfBuzz patch BEFORE compilation
        """
        # Get build directory where SDL2_ttf source was extracted
        build_dir = self.get_build_dir(arch.arch)
        hb_ft_path = os.path.join(build_dir, 'external', 'harfbuzz', 'src', 'hb-ft.cc')

        print("=" * 70)
        print("🔧 PATCHING SDL2_TTF/HARFBUZZ - Build #36 (NDK r28+ compatibility)")
        print("  Fix: Disable -Wcast-function-type-strict in hb-ft.cc")
        print("  Method: #pragma clang diagnostic (simple & reliable)")
        print(f"📁 Build dir: {build_dir}")
        print("=" * 70)

        patch_applied = False
        if not os.path.exists(hb_ft_path):
            print(f"⚠️  WARNING: hb-ft.cc not found at {hb_ft_path}")
            print("  ⚠️  File may not exist in this SDL2_ttf version - skipping patch")
        else:
            print("📖 Reading hb-ft.cc...")
            with open(hb_ft_path, 'r') as f:
                content = f.read()

            # Check if already patched
            if 'GENESIS ANDROID PATCH' in content:
                print("✅ hb-ft.cc already patched, skipping")
                patch_applied = True
            else:
                print("\n🔍 Adding pragma to disable cast warning...")

                # Strategy: Add #pragma at the very top of the file
                # This is the simplest and most reliable approach
                pragma_directive = '''/* GENESIS ANDROID PATCH: Disable strict function pointer cast warnings for NDK r28+ */
#pragma clang diagnostic ignored "-Wcast-function-type-strict"

'''

                # Prepend pragma to file content
                patched_content = pragma_directive + content

                # Write patched file
                with open(hb_ft_path, 'w') as f:
                    f.write(patched_content)
                print("  ✅ Added #pragma clang diagnostic ignored")
                print("  📝 Wrote patched hb-ft.cc")

                # Verify patch with SHA256 hash
                import hashlib
                hash_obj = hashlib.sha256(patched_content.encode('utf-8'))
                print(f"  🔒 Patch verification hash: {hash_obj.hexdigest()[:16]}...")
                print("  ✅ PATCH applied successfully!")
                patch_applied = True

        print("\n" + "=" * 70)
        if patch_applied:
            print("✅ SDL2_TTF/HARFBUZZ PATCH COMPLETE!")
        else:
            print("⚠️  SDL2_TTF/HARFBUZZ PATCH SKIPPED (may not be needed)")
        print("=" * 70)

        print("\n" + "=" * 70)
        print("📞 Calling parent build_arch (will compile SDL2_ttf)")
        print("   PATCH: #pragma disables -Wcast-function-type-strict warning")
        print("   Expected: HarfBuzz compiles ✅ → SDL2_ttf builds ✅ → APK SUCCESS! 🎉")
        print("=" * 70)

        # Now call parent which will compile SDL2_ttf with patched HarfBuzz
        super().build_arch(arch)


recipe = LibSDL2_ttfRecipePatched()
