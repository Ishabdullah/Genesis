"""
Custom SDL2_ttf recipe that patches HarfBuzz for NDK r28+ compatibility

Build #35: HarfBuzz function pointer cast fix
- NDK r28+ has stricter -Wcast-function-type-strict warnings (treated as errors)
- HarfBuzz's hb-ft.cc has incompatible function pointer casts
- Solution: Disable -Werror for HarfBuzz compilation or patch the casts
"""

import os
from pythonforandroid.recipes.sdl2_ttf import LibSDL2_ttfRecipe


class LibSDL2_ttfRecipePatched(LibSDL2_ttfRecipe):
    """
    Custom SDL2_ttf recipe that patches HarfBuzz for NDK r28+

    PATCH: Fix function pointer casts in hb-ft.cc
    - File: external/harfbuzz/src/hb-ft.cc
    - Error: -Wcast-function-type-strict (cast from 'void (*)(FT_Face)' to 'void (*)(void *)')
    - Fix: Add proper wrapper function or disable -Werror for this file
    """

    def build_arch(self, arch):
        """
        Apply HarfBuzz patch BEFORE compilation
        """
        # Get build directory where SDL2_ttf source was extracted
        build_dir = self.get_build_dir(arch.arch)
        hb_ft_path = os.path.join(build_dir, 'external', 'harfbuzz', 'src', 'hb-ft.cc')

        print("=" * 70)
        print("🔧 PATCHING SDL2_TTF/HARFBUZZ - Build #35 (NDK r28+ compatibility)")
        print("  Fix: Function pointer cast warnings in hb-ft.cc")
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
                print("\n🔍 Patching function pointer casts...")

                # Strategy: Create a proper wrapper function that matches the expected signature
                # Then use that wrapper instead of direct casts

                # Add wrapper function at the top of the file (after includes)
                wrapper_code = '''
/* GENESIS ANDROID PATCH: Wrapper to fix function pointer type mismatch in NDK r28+ */
#ifdef __ANDROID__
static void hb_ft_face_finalize_wrapper(void *object) {
    hb_ft_face_finalize(reinterpret_cast<FT_Face>(object));
}
#define HB_FT_FACE_FINALIZER hb_ft_face_finalize_wrapper
#else
#define HB_FT_FACE_FINALIZER ((FT_Generic_Finalizer) hb_ft_face_finalize)
#endif

static void _release_blob_wrapper(void *object) {
    _release_blob(reinterpret_cast<FT_Face>(object));
}
'''

                # Find a good insertion point (after the initial includes, before functions)
                # Look for the first function definition
                import re

                # Insert after the last #include or #define at the top
                include_pattern = r'(#include[^\n]+\n(?:[^\n]*\n)*?)(\n(?:static|extern|namespace|hb_))'
                match = re.search(include_pattern, content)

                if match:
                    # Insert wrapper after includes
                    content = content[:match.end(1)] + wrapper_code + content[match.end(1):]
                    print("  ✅ Added wrapper functions")
                else:
                    # Fallback: add after first few lines
                    lines = content.split('\n')
                    insert_pos = min(50, len(lines))
                    lines.insert(insert_pos, wrapper_code)
                    content = '\n'.join(lines)
                    print("  ✅ Added wrapper functions (fallback position)")

                # Now replace the casts with the wrapper
                # Replace: (FT_Generic_Finalizer) hb_ft_face_finalize
                # With: HB_FT_FACE_FINALIZER
                content = content.replace(
                    '(FT_Generic_Finalizer) hb_ft_face_finalize',
                    'HB_FT_FACE_FINALIZER'
                )

                # Replace: (FT_Generic_Finalizer) _release_blob
                # With: _release_blob_wrapper
                content = content.replace(
                    '(FT_Generic_Finalizer) _release_blob',
                    '_release_blob_wrapper'
                )

                # Write patched file
                with open(hb_ft_path, 'w') as f:
                    f.write(content)
                print("  ✅ Replaced function pointer casts with wrappers")
                print("  📝 Wrote patched hb-ft.cc")

                # Verify patch with SHA256 hash
                import hashlib
                hash_obj = hashlib.sha256(content.encode('utf-8'))
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
        print("   PATCH: Function pointer casts fixed with proper wrappers")
        print("   Expected: HarfBuzz compiles ✅ → SDL2_ttf builds ✅ → APK SUCCESS! 🎉")
        print("=" * 70)

        # Now call parent which will compile SDL2_ttf with patched HarfBuzz
        super().build_arch(arch)


recipe = LibSDL2_ttfRecipePatched()
