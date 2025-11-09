"""
Genesis Android Build - Kivy Recipe (Build #47)

Fixes two issues for NDK r28+ cross-compilation:
1. Blocks pkg-config from returning host system paths
2. Suppresses OpenGL function pointer type mismatch errors

Issues:
- Kivy's setup.py calls pkg-config which returns host system paths
- Cython-generated OpenGL code has const qualifier mismatches (NDK r28+ strict checking)

Solutions:
1. Override PKG_CONFIG env var to /bin/true (outputs nothing)
2. Add -Wno-incompatible-function-pointer-types to CFLAGS
"""

from pythonforandroid.recipes.kivy import KivyRecipe
from pythonforandroid.logger import info
import os


class KivyRecipeBuild47(KivyRecipe):
    """
    Custom Kivy recipe for Genesis Android build.

    Fixes two NDK r28+ cross-compilation issues:
    1. Disables pkg-config to prevent host system header conflicts
    2. Suppresses OpenGL function pointer type mismatch errors
    """

    def get_recipe_env(self, arch, **kwargs):
        """
        Override environment for NDK r28+ compatible Kivy builds.

        Changes:
        1. Sets PKG_CONFIG to /bin/true (prevents host system paths)
        2. Adds -Wno-incompatible-function-pointer-types to CFLAGS
           (fixes OpenGL const qualifier mismatches in Cython-generated code)
        """
        # Get parent environment
        env = super().get_recipe_env(arch, **kwargs)

        info("=" * 70)
        info("🔧 KIVY RECIPE - Build #47 (NDK r28+ Compatibility)")
        info("  Fix #1: Override PKG_CONFIG environment variable")
        info("  Fix #2: Suppress function pointer type mismatches")
        info("=" * 70)

        # Fix #1: Override PKG_CONFIG to point to /bin/true
        # This makes all pkg-config calls return success but with empty output
        env['PKG_CONFIG'] = '/bin/true'
        env['PKG_CONFIG_PATH'] = ''
        env['PKG_CONFIG_LIBDIR'] = ''

        info("✅ PKG_CONFIG=/bin/true (will return empty output)")
        info("✅ PKG_CONFIG_PATH='' (no search paths)")
        info("✅ PKG_CONFIG_LIBDIR='' (no library dirs)")
        info("   → Prevents host SDL2/harfbuzz header conflicts")

        # Fix #2: Add compiler flag to suppress OpenGL function pointer type errors
        # NDK r28+ has strict type checking for function pointers
        # Kivy's Cython-generated OpenGL code has const qualifier mismatches:
        #   Expected: const GLchar **
        #   Actual:   const GLchar *const *
        # This is safe to suppress - both are const-correct, just different const positions
        cflags = env.get('CFLAGS', '')
        if '-Wno-incompatible-function-pointer-types' not in cflags:
            env['CFLAGS'] = cflags + ' -Wno-incompatible-function-pointer-types'
            info("✅ Added -Wno-incompatible-function-pointer-types to CFLAGS")
            info("   → Allows OpenGL function pointer assignments in cgl_gl.c")

        info("=" * 70)

        return env


recipe = KivyRecipeBuild47()

