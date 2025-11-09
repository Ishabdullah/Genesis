"""
Genesis Android Build - Kivy Recipe (Build #46 - Revised v2)

Blocks pkg-config during Kivy cross-compilation by overriding PKG_CONFIG environment variable.

Issue: Kivy's setup.py calls pkg-config which returns host system paths.

Previous approaches failed:
1. Environment filtering - setup.py bypasses it
2. setup.py monkey-patching - recipe build_arch() not called by p4a

Solution: Override PKG_CONFIG env var to point to /bin/true (outputs nothing).
"""

from pythonforandroid.recipes.kivy import KivyRecipe
from pythonforandroid.logger import info
import os


class KivyRecipeBuild46(KivyRecipe):
    """
    Custom Kivy recipe for Genesis Android build.

    Fixes cross-compilation header conflicts by disabling pkg-config
    via environment variable override.
    """

    def get_recipe_env(self, arch, **kwargs):
        """
        Override environment to disable pkg-config during Android builds.

        Sets PKG_CONFIG to /bin/true which outputs nothing, preventing
        setup.py from getting host system include paths.
        """
        # Get parent environment
        env = super().get_recipe_env(arch, **kwargs)

        info("=" * 70)
        info("🔧 KIVY RECIPE - Build #46 v2 (Disable pkg-config via env)")
        info("  Fix: Override PKG_CONFIG environment variable")
        info("  Issue: setup.py calls pkg-config, gets host paths")
        info("=" * 70)

        # Override PKG_CONFIG to point to /bin/true
        # This makes all pkg-config calls return success but with empty output
        env['PKG_CONFIG'] = '/bin/true'
        env['PKG_CONFIG_PATH'] = ''
        env['PKG_CONFIG_LIBDIR'] = ''

        info("✅ PKG_CONFIG=/bin/true (will return empty output)")
        info("✅ PKG_CONFIG_PATH='' (no search paths)")
        info("✅ PKG_CONFIG_LIBDIR='' (no library dirs)")
        info("   setup.py will not find host SDL2/harfbuzz packages")
        info("=" * 70)

        return env


recipe = KivyRecipeBuild46()

