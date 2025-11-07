"""
Custom libffi recipe that uses official release tarball with pre-generated configure
This avoids running autogen.sh which fails with modern autotools
"""

from pythonforandroid.recipes.libffi import LibffiRecipe
from pythonforandroid.logger import shprint
import sh


class LibffiRecipePatched(LibffiRecipe):
    """
    Custom libffi recipe that uses official release tarball
    Official releases include pre-generated configure scripts, so we can skip autogen.sh
    """

    # Use official release URL instead of GitHub archive
    # Official releases have pre-generated configure, avoiding autogen.sh/autoconf issues
    url = 'https://github.com/libffi/libffi/releases/download/v3.4.4/libffi-3.4.4.tar.gz'

    # Patches from the default recipe
    patches = []  # Empty - official release doesn't need patches

    def build_arch(self, arch):
        """
        Build using the pre-generated configure script from official release
        """
        env = self.get_recipe_env(arch)

        print("=" * 70)
        print("🎯 USING LIBFFI 3.4.4 OFFICIAL RELEASE")
        print("📦 Pre-generated configure script included - NO autogen.sh needed!")
        print("=" * 70)

        # Call parent build but it will use our URL with pre-generated configure
        super().build_arch(arch)


recipe = LibffiRecipePatched()
