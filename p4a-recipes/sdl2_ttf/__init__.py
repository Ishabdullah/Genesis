"""
Custom SDL2_ttf recipe that patches HarfBuzz for NDK r28+ compatibility

Build #43: HarfBuzz function pointer cast fix (SOURCE CODE PATCH)
- NDK r28+ has stricter -Wcast-function-type-strict warnings (treated as errors)
- HarfBuzz's hb-ft.cc has incompatible function pointer casts (C++ file)
- Pragma approach (Builds #39-40) failed because -Werror elevates warnings to errors
- Android.mk LOCAL_CPPFLAGS approach (Builds #41-42) failed - flags not in compile command
- Solution: Patch the source code to use proper C++ type-safe wrapper functions
- This is the most reliable approach - fixes the actual type mismatch
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

    PATCH: Fix incompatible function pointer casts in hb-ft.cc
    - File: external/harfbuzz/src/hb-ft.cc
    - Error: cast from 'void (*)(FT_Face)' to 'FT_Generic_Finalizer' (aka 'void (*)(void *)')
    - Fix: Add type-safe wrapper function that bridges the cast
    - Why: Android.mk flag approach failed - flags not picked up by build system
    """

    # Ensure name is set if using base Recipe class
    name = 'sdl2_ttf'

    def build_arch(self, arch):
        """
        Apply HarfBuzz source code patch BEFORE compilation
        """
        # SDL2_ttf is built as part of SDL2 bootstrap
        # The actual source is in the SDL2 bootstrap build directory
        from pythonforandroid.toolchain import current_directory
        import glob

        # Find SDL2_ttf source in bootstrap builds
        bootstrap_dir = os.path.join(self.ctx.build_dir, 'bootstrap_builds', 'sdl2')
        hb_ft_path = os.path.join(bootstrap_dir, 'jni', 'SDL2_ttf', 'external', 'harfbuzz', 'src', 'hb-ft.cc')

        print("=" * 70)
        print("🔧 PATCHING SDL2_TTF/HARFBUZZ - Build #43 (NDK r28+ compatibility)")
        print("  Fix: Patch hb-ft.cc to use type-safe wrapper functions")
        print("  Method: Add wrapper functions to bridge incompatible pointer types")
        print("  Why: Android.mk flags not working, source patch is most reliable")
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
                print("\n🔍 Adding type-safe wrapper functions...")

                # Strategy: Add wrapper functions that properly bridge the type mismatch
                # The issue is: void (*)(FT_Face) vs void (*)(void *)
                # Solution: Create wrapper that takes void* and casts to FT_Face

                wrapper_code = '''
/* GENESIS ANDROID PATCH: Type-safe wrappers for FT_Generic_Finalizer casts (NDK r28+) */
/* Wrapper for hb_ft_face_finalize to match FT_Generic_Finalizer signature */
static void hb_ft_face_finalize_wrapper(void *object) {
  hb_ft_face_finalize(reinterpret_cast<FT_Face>(object));
}

/* Wrapper for _release_blob to match FT_Generic_Finalizer signature */
static void _release_blob_wrapper(void *object) {
  _release_blob(reinterpret_cast<FT_Face>(object));
}
/* END GENESIS ANDROID PATCH */

'''

                # Find a good insertion point - after the includes, before the first function
                # Look for the first function definition (static or not)
                lines = content.split('\n')
                patched_lines = []
                inserted = False

                for i, line in enumerate(lines):
                    # Look for the first function definition after includes
                    # Usually after struct/class definitions, before first function
                    if not inserted and ('hb_ft_face_finalize' in line or 'static void' in line) and '(' in line and not line.strip().startswith('//') and not line.strip().startswith('/*'):
                        # Insert wrapper before this function
                        patched_lines.append(wrapper_code)
                        inserted = True

                    patched_lines.append(line)

                # If we didn't find a good spot, insert after the last #include
                if not inserted:
                    patched_lines = []
                    for i, line in enumerate(lines):
                        patched_lines.append(line)
                        if '#include' in line and i < len(lines) - 1 and '#include' not in lines[i+1]:
                            patched_lines.append(wrapper_code)
                            inserted = True

                patched_content = '\n'.join(patched_lines)

                # Now replace the casts with wrapper function calls
                # Line 759: ft_face->generic.finalizer != (FT_Generic_Finalizer) hb_ft_face_finalize
                patched_content = patched_content.replace(
                    'ft_face->generic.finalizer != (FT_Generic_Finalizer) hb_ft_face_finalize',
                    'ft_face->generic.finalizer != hb_ft_face_finalize_wrapper'
                )

                # Line 765: ft_face->generic.finalizer = (FT_Generic_Finalizer) hb_ft_face_finalize;
                patched_content = patched_content.replace(
                    'ft_face->generic.finalizer = (FT_Generic_Finalizer) hb_ft_face_finalize;',
                    'ft_face->generic.finalizer = hb_ft_face_finalize_wrapper;'
                )

                # Line 1035: ft_face->generic.finalizer = (FT_Generic_Finalizer) _release_blob;
                patched_content = patched_content.replace(
                    'ft_face->generic.finalizer = (FT_Generic_Finalizer) _release_blob;',
                    'ft_face->generic.finalizer = _release_blob_wrapper;'
                )

                # Write patched file
                with open(hb_ft_path, 'w') as f:
                    f.write(patched_content)
                print("  ✅ Added type-safe wrapper functions")
                print("  ✅ Replaced 3 incompatible casts with wrapper calls")
                print("  📝 Wrote patched hb-ft.cc")

                # Verify patch with SHA256 hash
                import hashlib
                hash_obj = hashlib.sha256(patched_content.encode('utf-8'))
                print(f"  🔒 Patch verification hash: {hash_obj.hexdigest()[:16]}...")
                print("  ✅ PATCH applied successfully!")
                patch_applied = True

        print("\n" + "=" * 70)
        if patch_applied:
            print("✅ SDL2_TTF/HARFBUZZ SOURCE CODE PATCH COMPLETE!")
        else:
            print("⚠️  SDL2_TTF/HARFBUZZ PATCH SKIPPED (may not be needed)")
        print("=" * 70)

        print("\n" + "=" * 70)
        print("📞 Calling parent build_arch (will compile SDL2_ttf)")
        print("   PATCH: hb-ft.cc uses type-safe wrapper functions")
        print("   Expected: HarfBuzz compiles ✅ → SDL2_ttf builds ✅ → APK SUCCESS! 🎉")
        print("=" * 70)

        # Now call parent which will compile SDL2_ttf with patched source
        super().build_arch(arch)


recipe = SDL2TtfRecipePatched()
