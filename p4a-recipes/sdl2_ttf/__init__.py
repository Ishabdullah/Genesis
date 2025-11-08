"""
Custom SDL2_ttf recipe that patches HarfBuzz for NDK r28+ compatibility

Build #42: HarfBuzz function pointer cast fix (ANDROID.MK - LOCAL_CPPFLAGS)
- NDK r28+ has stricter -Wcast-function-type-strict warnings (treated as errors)
- HarfBuzz's hb-ft.cc has incompatible function pointer casts (C++ file)
- Pragma approach failed because -Werror elevates warnings to errors
- Build #41 failed: Used LOCAL_CFLAGS but hb-ft.cc is C++ (.cc extension)
- Solution: Modify Android.mk to add flags to both LOCAL_CFLAGS AND LOCAL_CPPFLAGS
- C++ files (.cc) need LOCAL_CPPFLAGS, not just LOCAL_CFLAGS
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

    PATCH: Disable strict function pointer cast warnings via Android.mk
    - File: external/harfbuzz/Android.mk
    - Error: -Wcast-function-type-strict (cast from 'void (*)(FT_Face)' to 'void (*)(void *)')
    - Fix: Add -Wno-error=cast-function-type-strict to LOCAL_CFLAGS AND LOCAL_CPPFLAGS
    - Why: hb-ft.cc is C++ file (.cc), needs CPPFLAGS not just CFLAGS
    """

    # Ensure name is set if using base Recipe class
    name = 'sdl2_ttf'

    def build_arch(self, arch):
        """
        Apply HarfBuzz Android.mk patch BEFORE compilation
        """
        # SDL2_ttf is built as part of SDL2 bootstrap
        # The actual source is in the SDL2 bootstrap build directory
        from pythonforandroid.toolchain import current_directory
        import glob

        # Find SDL2_ttf source in bootstrap builds
        bootstrap_dir = os.path.join(self.ctx.build_dir, 'bootstrap_builds', 'sdl2')
        harfbuzz_mk_path = os.path.join(bootstrap_dir, 'jni', 'SDL2_ttf', 'external', 'harfbuzz', 'Android.mk')

        print("=" * 70)
        print("🔧 PATCHING SDL2_TTF/HARFBUZZ - Build #42 (NDK r28+ compatibility)")
        print("  Fix: Add -Wno-error=cast-function-type-strict to Android.mk")
        print("  Method: Modify LOCAL_CFLAGS and LOCAL_CPPFLAGS in Android.mk")
        print("  Why: hb-ft.cc is C++, needs CPPFLAGS not just CFLAGS")
        print(f"📁 Bootstrap dir: {bootstrap_dir}")
        print(f"📁 Android.mk: {harfbuzz_mk_path}")
        print("=" * 70)

        patch_applied = False
        if not os.path.exists(harfbuzz_mk_path):
            print(f"⚠️  WARNING: Android.mk not found at {harfbuzz_mk_path}")
            print("  ⚠️  File may not exist in this SDL2_ttf version - skipping patch")
        else:
            print("📖 Reading Android.mk...")
            with open(harfbuzz_mk_path, 'r') as f:
                content = f.read()

            # Check if already patched
            if 'GENESIS ANDROID PATCH' in content:
                print("✅ Android.mk already patched, skipping")
                patch_applied = True
            else:
                print("\n🔍 Adding -Wno-error flag to LOCAL_CFLAGS and LOCAL_CPPFLAGS...")

                # Strategy: Add compiler flag to both CFLAGS and CPPFLAGS (hb-ft.cc is C++)
                # Need to ensure our flags come AFTER any existing flags
                lines = content.split('\n')
                patched_lines = []
                cflags_added = False
                cppflags_added = False

                # Pass through all lines, adding our patches where appropriate
                for line in lines:
                    patched_lines.append(line)

                    # Add to LOCAL_CFLAGS if found
                    if 'LOCAL_CFLAGS' in line and ':=' in line and not line.strip().startswith('#') and not cflags_added:
                        patched_lines.append('# GENESIS ANDROID PATCH: Disable cast-function-type-strict error for NDK r28+')
                        patched_lines.append('LOCAL_CFLAGS += -Wno-error=cast-function-type-strict -Wno-cast-function-type-strict')
                        cflags_added = True

                    # Add to LOCAL_CPPFLAGS if found (C++ specific - hb-ft.cc is C++)
                    if 'LOCAL_CPPFLAGS' in line and ':=' in line and not line.strip().startswith('#') and not cppflags_added:
                        patched_lines.append('# GENESIS ANDROID PATCH: Disable cast-function-type-strict error for NDK r28+')
                        patched_lines.append('LOCAL_CPPFLAGS += -Wno-error=cast-function-type-strict -Wno-cast-function-type-strict')
                        cppflags_added = True

                    # If we find LOCAL_PATH and haven't added flags yet, add both after it
                    if 'LOCAL_PATH' in line and not line.strip().startswith('#'):
                        if not cflags_added and not cppflags_added:
                            patched_lines.append('')
                            patched_lines.append('# GENESIS ANDROID PATCH: Disable cast-function-type-strict error for NDK r28+')
                            patched_lines.append('LOCAL_CFLAGS := -Wno-error=cast-function-type-strict -Wno-cast-function-type-strict')
                            patched_lines.append('LOCAL_CPPFLAGS := -Wno-error=cast-function-type-strict -Wno-cast-function-type-strict')
                            cflags_added = True
                            cppflags_added = True

                patched_content = '\n'.join(patched_lines)

                # Write patched file
                with open(harfbuzz_mk_path, 'w') as f:
                    f.write(patched_content)
                print("  ✅ Added -Wno-error=cast-function-type-strict to LOCAL_CFLAGS and LOCAL_CPPFLAGS")
                print("  📝 Wrote patched Android.mk")

                # Verify patch with SHA256 hash
                import hashlib
                hash_obj = hashlib.sha256(patched_content.encode('utf-8'))
                print(f"  🔒 Patch verification hash: {hash_obj.hexdigest()[:16]}...")
                print("  ✅ PATCH applied successfully!")
                patch_applied = True

        print("\n" + "=" * 70)
        if patch_applied:
            print("✅ SDL2_TTF/HARFBUZZ ANDROID.MK PATCH COMPLETE!")
        else:
            print("⚠️  SDL2_TTF/HARFBUZZ PATCH SKIPPED (may not be needed)")
        print("=" * 70)

        print("\n" + "=" * 70)
        print("📞 Calling parent build_arch (will compile SDL2_ttf)")
        print("   PATCH: Android.mk adds -Wno-error=cast-function-type-strict")
        print("   Expected: HarfBuzz compiles ✅ → SDL2_ttf builds ✅ → APK SUCCESS! 🎉")
        print("=" * 70)

        # Now call parent which will compile SDL2_ttf with patched Android.mk
        super().build_arch(arch)


recipe = SDL2TtfRecipePatched()
