"""
Genesis Android Build - Kivy Recipe (Build #46 - Revised)

Patches Kivy's setup.py to prevent host system header inclusion during Android cross-compilation.

Issue: Kivy's setup.py calls pkg-config which returns host system paths, bypassing environment filtering.

Root Cause: setup.py runs subprocess calls to pkg-config on host, gets x86_64 paths, adds them to include_dirs.

Solution: Patch setup.py before build to disable pkg-config calls during Android cross-compilation.
"""

from pythonforandroid.recipes.kivy import KivyRecipe
from pythonforandroid.logger import info, warning
from pythonforandroid.util import current_directory
import os


class KivyRecipeBuild46(KivyRecipe):
    """
    Custom Kivy recipe for Genesis Android build.

    Fixes cross-compilation header conflicts by patching setup.py to skip
    host system pkg-config calls during Android builds.
    """

    def build_arch(self, arch):
        """
        Override build_arch to patch setup.py before building.

        Patches Kivy's setup.py to prevent pkg-config from adding host system
        include paths during Android cross-compilation.
        """
        info("=" * 70)
        info("🔧 PATCHING KIVY SETUP.PY - Build #46 (NDK r28+ cross-compilation)")
        info("  Fix: Disable host pkg-config during Android build")
        info("  Issue: setup.py calls pkg-config, gets host x86_64 paths")
        info(f"📁 Build dir: {self.get_build_dir(arch.arch)}")
        info("=" * 70)

        with current_directory(self.get_build_dir(arch.arch)):
            setup_py_path = 'setup.py'
            info(f"📖 Reading {setup_py_path}...")

            try:
                with open(setup_py_path, 'r') as f:
                    setup_content = f.read()

                # Create patch to disable pkg-config for Android builds
                # Insert this early in the file, after imports
                patch_code = '''
# GENESIS ANDROID PATCH: Disable host pkg-config during cross-compilation (Build #46)
import os as _patch_os
import subprocess as _patch_subprocess

if _patch_os.environ.get('ANDROID_NDK') or _patch_os.environ.get('ANDROIDNDK'):
    print("[GENESIS PATCH] Android cross-compilation detected - disabling pkg-config")

    # Save original subprocess functions
    _original_check_output = _patch_subprocess.check_output
    _original_run = _patch_subprocess.run
    _original_Popen = _patch_subprocess.Popen

    def _patched_check_output(cmd, *args, **kwargs):
        """Block pkg-config calls during Android builds"""
        if isinstance(cmd, (list, tuple)) and len(cmd) > 0:
            if 'pkg-config' in str(cmd[0]) or any('pkg-config' in str(arg) for arg in cmd):
                print(f"[GENESIS PATCH] Blocking pkg-config call: {cmd}")
                # Return empty output to prevent host paths
                return b''
        return _original_check_output(cmd, *args, **kwargs)

    def _patched_run(cmd, *args, **kwargs):
        """Block pkg-config calls during Android builds"""
        if isinstance(cmd, (list, tuple)) and len(cmd) > 0:
            if 'pkg-config' in str(cmd[0]) or any('pkg-config' in str(arg) for arg in cmd):
                print(f"[GENESIS PATCH] Blocking pkg-config call: {cmd}")
                # Return empty result
                class EmptyResult:
                    stdout = b''
                    stderr = b''
                    returncode = 0
                return EmptyResult()
        return _original_run(cmd, *args, **kwargs)

    def _patched_Popen(cmd, *args, **kwargs):
        """Block pkg-config calls during Android builds"""
        if isinstance(cmd, (list, tuple)) and len(cmd) > 0:
            if 'pkg-config' in str(cmd[0]) or any('pkg-config' in str(arg) for arg in cmd):
                print(f"[GENESIS PATCH] Blocking pkg-config call: {cmd}")
                # Return a process that outputs nothing
                return _original_Popen(['echo', ''], *args, **kwargs)
        return _original_Popen(cmd, *args, **kwargs)

    # Monkey-patch subprocess module
    _patch_subprocess.check_output = _patched_check_output
    _patch_subprocess.run = _patched_run
    _patch_subprocess.Popen = _patched_Popen

    print("[GENESIS PATCH] pkg-config blocking active for Android build")

# END GENESIS ANDROID PATCH
'''

                # Find where to insert the patch - after imports, before setup() or build_ext
                lines = setup_content.split('\n')

                # Look for the last import or from statement
                last_import_idx = -1
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith('import ') or stripped.startswith('from '):
                        last_import_idx = i

                if last_import_idx >= 0:
                    info(f"🔍 Inserting patch after line {last_import_idx + 1}...")
                    lines.insert(last_import_idx + 1, patch_code)
                    patched_content = '\n'.join(lines)

                    with open(setup_py_path, 'w') as f:
                        f.write(patched_content)

                    info("✅ setup.py PATCHED successfully!")
                    info("   pkg-config calls will be blocked during Android build")
                else:
                    warning("⚠️  Could not find import statements in setup.py")
                    warning("   Trying alternative patch location...")

                    # Fallback: insert at the very beginning after shebang/docstring
                    if lines[0].startswith('#!'):
                        lines.insert(1, patch_code)
                    elif lines[0].startswith('"""') or lines[0].startswith("'''"):
                        # Find end of docstring
                        quote = lines[0][:3]
                        for i in range(1, len(lines)):
                            if quote in lines[i]:
                                lines.insert(i + 1, patch_code)
                                break
                    else:
                        lines.insert(0, patch_code)

                    patched_content = '\n'.join(lines)
                    with open(setup_py_path, 'w') as f:
                        f.write(patched_content)

                    info("✅ setup.py patched at alternative location")

            except Exception as e:
                warning(f"⚠️  Setup.py patch failed: {e}")
                warning("   Continuing with unpatched build (may fail)...")
                import traceback
                warning(traceback.format_exc())

        info("=" * 70)
        info("📞 Calling parent build_arch (will build Kivy with patched setup.py)")
        info("   Expected: No pkg-config → No host paths → Kivy builds ✅")
        info("=" * 70)

        # Call parent build_arch
        super().build_arch(arch)


recipe = KivyRecipeBuild46()
