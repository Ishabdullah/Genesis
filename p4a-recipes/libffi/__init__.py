"""
Custom libffi recipe that patches configure.ac to remove obsolete LT_SYS_SYMBOL_USCORE macro
This is a workaround for modern autotools incompatibility
"""

from pythonforandroid.recipes.libffi import LibffiRecipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint
import sh


class LibffiRecipePatched(LibffiRecipe):
    """
    Custom libffi recipe that patches configure.ac before running autogen.sh
    """

    def build_arch(self, arch):
        """
        Override build_arch to patch configure.ac before building
        """
        env = self.get_recipe_env(arch)

        with current_directory(self.get_build_dir(arch.arch)):
            # Patch configure.ac to remove/replace the problematic macro
            configure_ac_path = 'configure.ac'

            print("=" * 60)
            print("APPLYING LIBFFI PATCH FOR MODERN AUTOTOOLS")
            print("=" * 60)

            # Read configure.ac
            with open(configure_ac_path, 'r') as f:
                configure_content = f.read()

            # Patch 1: Comment out the line that uses LT_SYS_SYMBOL_USCORE
            # The macro is used around line 215 in an if statement
            # We'll replace it with a safe default value
            patched_content = configure_content.replace(
                'if test "x$LT_SYS_SYMBOL_USCORE" = xyes; then',
                '# PATCHED: Removed obsolete LT_SYS_SYMBOL_USCORE macro\n'
                '# Defaulting to no underscore prefix (modern systems)\n'
                'if test "xno" = xyes; then'
            )

            # Patch 2: Also handle the AC_DEFINE that follows
            # This ensures the build continues even if the above doesn't catch everything
            if 'SYMBOL_UNDERSCORE' in patched_content:
                print("Found SYMBOL_UNDERSCORE usage, applying secondary patch...")
                patched_content = patched_content.replace(
                    'AC_DEFINE(SYMBOL_UNDERSCORE,1,[Define if symbols are underscored.])',
                    '# PATCHED: Removed SYMBOL_UNDERSCORE definition'
                )

            # Write patched configure.ac
            with open(configure_ac_path, 'w') as f:
                f.write(patched_content)

            print("✓ Patched configure.ac to remove LT_SYS_SYMBOL_USCORE macro")
            print("=" * 60)

            # Now run the normal build process
            super().build_arch(arch)


recipe = LibffiRecipePatched()
