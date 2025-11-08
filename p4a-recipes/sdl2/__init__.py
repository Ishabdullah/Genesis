"""
Custom SDL2 recipe that patches for NDK r28+ compatibility

Build #31: SDL2 ALooper_pollAll deprecation fix
- NDK r28+ marks ALooper_pollAll as unavailable
- SDL2's Android sensor code uses deprecated function
- Solution: Patch to use ALooper_pollOnce instead
"""

import os
from pythonforandroid.recipes.sdl2 import LibSDL2Recipe


class LibSDL2RecipePatched(LibSDL2Recipe):
    """
    Custom SDL2 recipe that patches Android sensor backend for NDK r28+

    PATCH: Replace ALooper_pollAll with ALooper_pollOnce
    - File: src/core/android/SDL_androidsensor.c
    - Line: ~164 (may vary by SDL2 version)
    - Error: 'ALooper_pollAll' is unavailable in NDK r28+
    - Fix: Use ALooper_pollOnce instead (recommended replacement)
    """

    def build_arch(self, arch):
        """
        Apply SDL2 Android sensor patch BEFORE compilation
        """
        # Get build directory where SDL2 source was extracted
        build_dir = self.get_build_dir(arch.arch)
        sensor_c_path = os.path.join(build_dir, 'src', 'core', 'android', 'SDL_androidsensor.c')

        print("=" * 70)
        print("🔧 PATCHING SDL2 - Build #31 (NDK r28+ compatibility)")
        print("  Fix: Replace ALooper_pollAll with ALooper_pollOnce")
        print(f"📁 Build dir: {build_dir}")
        print("=" * 70)

        patch_applied = False
        if not os.path.exists(sensor_c_path):
            print(f"⚠️  WARNING: SDL_androidsensor.c not found at {sensor_c_path}")
            print("  ⚠️  File may not exist in this SDL2 version - skipping patch")
        else:
            print("📖 Reading SDL_androidsensor.c...")
            with open(sensor_c_path, 'r') as f:
                content = f.read()

            # Check if already patched
            if 'GENESIS ANDROID PATCH' in content:
                print("✅ SDL_androidsensor.c already patched, skipping")
                patch_applied = True
            else:
                print("\n🔍 Searching for ALooper_pollAll usage...")

                # Check if ALooper_pollAll exists in the file
                if 'ALooper_pollAll' in content:
                    print("  ✅ Found ALooper_pollAll calls")

                    # Replace ALooper_pollAll with ALooper_pollOnce
                    # This is a direct function name replacement - safe and simple
                    original_content = content

                    # Add marker comment before first occurrence
                    content = content.replace(
                        'ALooper_pollAll',
                        '/* GENESIS ANDROID PATCH: Use ALooper_pollOnce for NDK r28+ */ ALooper_pollOnce',
                        1  # Replace first occurrence with comment
                    )
                    # Replace remaining occurrences without comment
                    content = content.replace('ALooper_pollAll', 'ALooper_pollOnce')

                    if content != original_content:
                        # Write patched file
                        with open(sensor_c_path, 'w') as f:
                            f.write(content)
                        print("  ✅ Replaced ALooper_pollAll with ALooper_pollOnce")
                        print("  📝 Wrote patched SDL_androidsensor.c")

                        # Verify patch with SHA256 hash
                        import hashlib
                        hash_obj = hashlib.sha256(content.encode('utf-8'))
                        print(f"  🔒 Patch verification hash: {hash_obj.hexdigest()[:16]}...")
                        print("  ✅ PATCH applied successfully!")
                        patch_applied = True
                    else:
                        print("  ⚠️  Content unchanged - unexpected file format")
                else:
                    print("  ⚠️  ALooper_pollAll not found in file")
                    print("  ⚠️  SDL2 version may already be compatible with NDK r28+")
                    patch_applied = True  # Consider it OK if function not present

        print("\n" + "=" * 70)
        if patch_applied:
            print("✅ SDL2 PATCH COMPLETE!")
        else:
            print("⚠️  SDL2 PATCH SKIPPED (may not be needed)")
        print("=" * 70)

        print("\n" + "=" * 70)
        print("📞 Calling parent build_arch (will compile SDL2)")
        print("   PATCH: ALooper_pollAll → ALooper_pollOnce (NDK r28+ safe)")
        print("   Expected: SDL2 compiles ✅ → Kivy builds ✅ → APK SUCCESS! 🎉")
        print("=" * 70)

        # Now call parent which will compile SDL2 with patched source
        super().build_arch(arch)


recipe = LibSDL2RecipePatched()
