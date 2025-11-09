"""
Genesis Android Build - Kivy Recipe (Build #46)

Filters host system include paths during Kivy cross-compilation for Android.

Issue: Build environment includes host system headers (/usr/include/x86_64-linux-gnu)
       when compiling Kivy for Android, causing __GNUC_PREREQ macro conflicts.

Root Cause: Kivy's setup.py runs on host system and picks up host SDL2/harfbuzz paths
            via pkg-config, which then get mixed with Android NDK headers.

Solution: Override get_recipe_env to filter CFLAGS/CPPFLAGS, removing host includes.
"""

from pythonforandroid.recipes.kivy import KivyRecipe
from pythonforandroid.logger import info, warning
import os


class KivyRecipeBuild46(KivyRecipe):
    """
    Custom Kivy recipe for Genesis Android build.

    Fixes cross-compilation header conflicts in NDK r28+ by filtering out
    host system include paths from the build environment.
    """

    def get_recipe_env(self, arch, **kwargs):
        """
        Override environment to filter out host system include paths.

        The parent recipe's environment may contain host paths like:
        - /usr/include/SDL2
        - /usr/include/harfbuzz
        - /usr/lib/x86_64-linux-gnu/glib-2.0/include

        These cause conflicts when cross-compiling for Android.
        """
        info("=" * 70)
        info("🔧 PATCHING KIVY ENV - Build #46 (NDK r28+ cross-compilation)")
        info("  Fix: Filter host system include paths from CFLAGS/CPPFLAGS")
        info("  Issue: Host headers conflict with Android NDK headers")
        info("=" * 70)

        # Get parent environment
        env = super().get_recipe_env(arch, **kwargs)

        # Host system paths to filter out
        host_prefixes = (
            '/usr/include',
            '/usr/lib/x86_64-linux-gnu',
            '/usr/lib/aarch64-linux-gnu',
            '/usr/lib64',
            '/lib/x86_64-linux-gnu',
            '/lib/aarch64-linux-gnu',
            '/usr/local/include',
        )

        def filter_flags(flags_str):
            """Remove host system -I and -L flags from a space-separated string."""
            if not flags_str:
                return flags_str

            parts = flags_str.split()
            filtered = []
            skip_next = False

            for i, part in enumerate(parts):
                if skip_next:
                    skip_next = False
                    continue

                # Check for -I/path or -I /path patterns
                if part == '-I' or part == '-L':
                    # Next item is the path
                    if i + 1 < len(parts):
                        path = parts[i + 1]
                        if any(path.startswith(prefix) for prefix in host_prefixes):
                            info(f"  [FILTERED] {part} {path}")
                            skip_next = True
                            continue

                # Check for -Ipath or -Lpath patterns
                if part.startswith('-I') or part.startswith('-L'):
                    path = part[2:]
                    if any(path.startswith(prefix) for prefix in host_prefixes):
                        info(f"  [FILTERED] {part}")
                        continue

                filtered.append(part)

            return ' '.join(filtered)

        # Filter CFLAGS, CXXFLAGS, CPPFLAGS
        for flag_name in ['CFLAGS', 'CXXFLAGS', 'CPPFLAGS']:
            if flag_name in env:
                original = env[flag_name]
                filtered = filter_flags(original)
                if original != filtered:
                    info(f"🔍 Filtered {flag_name}:")
                    env[flag_name] = filtered

        info("✅ Environment filtering complete!")
        info("=" * 70)

        return env


recipe = KivyRecipeBuild46()
