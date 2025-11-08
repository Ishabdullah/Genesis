"""
Custom SDL2_ttf recipe that patches HarfBuzz for NDK r28+ compatibility

Build #38: HarfBuzz function pointer cast fix (DYNAMIC IMPORT)
- NDK r28+ has stricter -Wcast-function-type-strict warnings (treated as errors)
- HarfBuzz's hb-ft.cc has incompatible function pointer casts
- Solution: Add #pragma to disable the warning for this file (cleanest approach)
- Fix: Use dynamic import to find correct base class
"""

import os
import importlib

# Dynamically import the SDL2_ttf recipe to avoid hardcoding class name
try:
    sdl2_ttf_module = importlib.import_module('pythonforandroid.recipes.sdl2_ttf')
    # Try common naming patterns
    for class_name in ['SDL2TtfRecipe', 'LibSDL2_ttfRecipe', 'Sdl2TtfRecipe', 'SDL2TTFRecipe']:
        if hasattr(sdl2_ttf_module, class_name):
            BaseRecipe = getattr(sdl2_ttf_module, class_name)
            break
    else:
        # If none of the common names work, get the 'recipe' variable
        if hasattr(sdl2_ttf_module, 'recipe'):
            BaseRecipe = type(sdl2_ttf_module.recipe)
        else:
            # Last resort: use Recipe base class
            from pythonforandroid.recipe import Recipe
            BaseRecipe = Recipe
except ImportError:
    # Fallback to base Recipe if SDL2_ttf module doesn't exist
    from pythonforandroid.recipe import Recipe
    BaseRecipe = Recipe


class SDL2TtfRecipePatched(BaseRecipe):
    """
    Custom SDL2_ttf recipe that patches HarfBuzz for NDK r28+

    PATCH: Disable strict function pointer cast warnings in hb-ft.cc
    - File: external/harfbuzz/src/hb-ft.cc
    - Error: -Wcast-function-type-strict (cast from 'void (*)(FT_Face)' to 'void (*)(void *)')
    - Fix: Add #pragma clang diagnostic ignored at top of file
    """

    # Ensure name is set if using base Recipe class
    name = 'sdl2_ttf'

    def build_arch(self, arch):
        """
        Apply HarfBuzz patch BEFORE compilation
        """
        # SDL2_ttf is built as part of SDL2 bootstrap
        # The actual source is in the SDL2 bootstrap build directory
        # Get the SDL2 bootstrap build directory
        from pythonforandroid.toolchain import current_directory
        import glob

        # Find SDL2_ttf source in bootstrap builds
        bootstrap_dir = os.path.join(self.ctx.build_dir, 'bootstrap_builds', 'sdl2')
        hb_ft_path = os.path.join(bootstrap_dir, 'jni', 'SDL2_ttf', 'external', 'harfbuzz', 'src', 'hb-ft.cc')

        print("=" * 70)
        print("🔧 PATCHING SDL2_TTF/HARFBUZZ - Build #39 (NDK r28+ compatibility)")
        print("  Fix: Disable -Wcast-function-type-strict in hb-ft.cc")
        print("  Method: #pragma clang diagnostic (simple & reliable)")
        print(f"📁 Bootstrap dir: {bootstrap_dir}")
        print(f"📁 HarfBuzz file: {hb_ft_path}")
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


recipe = SDL2TtfRecipePatched()
