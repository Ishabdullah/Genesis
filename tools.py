#!/usr/bin/env python3
"""
Genesis Tool Functions
File system operations and utility commands
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple

class GenesisTools:
    """Provides file system and utility tools for Genesis"""

    @staticmethod
    def read_file(filepath: str) -> str:
        """
        Read and return file contents

        Args:
            filepath: Path to file

        Returns:
            File contents or error message
        """
        try:
            path = Path(filepath).expanduser()
            if not path.exists():
                return f"⚠ File not found: {filepath}"

            if not path.is_file():
                return f"⚠ Not a file: {filepath}"

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.count('\n') + 1
            size = len(content)
            return f"📄 {filepath} ({lines} lines, {size} bytes)\n\n{content}"

        except Exception as e:
            return f"⚠ Error reading file: {e}"

    @staticmethod
    def write_file(filepath: str, content: str) -> str:
        """
        Write content to file

        Args:
            filepath: Path to file
            content: Content to write

        Returns:
            Success or error message
        """
        try:
            path = Path(filepath).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            size = len(content)
            return f"✓ Written {size} bytes to {filepath}"

        except Exception as e:
            return f"⚠ Error writing file: {e}"

    @staticmethod
    def append_file(filepath: str, content: str) -> str:
        """
        Append content to file

        Args:
            filepath: Path to file
            content: Content to append

        Returns:
            Success or error message
        """
        try:
            path = Path(filepath).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'a', encoding='utf-8') as f:
                f.write(content)

            size = len(content)
            return f"✓ Appended {size} bytes to {filepath}"

        except Exception as e:
            return f"⚠ Error appending to file: {e}"

    @staticmethod
    def list_directory(dirpath: str = ".") -> str:
        """
        List directory contents

        Args:
            dirpath: Path to directory

        Returns:
            Formatted directory listing
        """
        try:
            path = Path(dirpath).expanduser()
            if not path.exists():
                return f"⚠ Directory not found: {dirpath}"

            if not path.is_dir():
                return f"⚠ Not a directory: {dirpath}"

            items = []
            for item in sorted(path.iterdir()):
                if item.is_dir():
                    items.append(f"📁 {item.name}/")
                else:
                    size = item.stat().st_size
                    items.append(f"📄 {item.name} ({size} bytes)")

            result = f"📂 {path.absolute()}\n\n"
            result += "\n".join(items)
            result += f"\n\nTotal: {len(items)} items"

            return result

        except Exception as e:
            return f"⚠ Error listing directory: {e}"

    @staticmethod
    def delete_file(filepath: str) -> str:
        """
        Delete a file

        Args:
            filepath: Path to file

        Returns:
            Success or error message
        """
        try:
            path = Path(filepath).expanduser()
            if not path.exists():
                return f"⚠ File not found: {filepath}"

            if path.is_dir():
                return f"⚠ Cannot delete directory (use delete_directory): {filepath}"

            path.unlink()
            return f"✓ Deleted {filepath}"

        except Exception as e:
            return f"⚠ Error deleting file: {e}"

    @staticmethod
    def delete_directory(dirpath: str) -> str:
        """
        Delete a directory and its contents

        Args:
            dirpath: Path to directory

        Returns:
            Success or error message
        """
        try:
            path = Path(dirpath).expanduser()
            if not path.exists():
                return f"⚠ Directory not found: {dirpath}"

            if not path.is_dir():
                return f"⚠ Not a directory: {dirpath}"

            shutil.rmtree(path)
            return f"✓ Deleted directory {dirpath}"

        except Exception as e:
            return f"⚠ Error deleting directory: {e}"

    @staticmethod
    def create_directory(dirpath: str) -> str:
        """
        Create a directory

        Args:
            dirpath: Path to directory

        Returns:
            Success or error message
        """
        try:
            path = Path(dirpath).expanduser()
            path.mkdir(parents=True, exist_ok=True)
            return f"✓ Created directory {dirpath}"

        except Exception as e:
            return f"⚠ Error creating directory: {e}"

    @staticmethod
    def get_current_directory() -> str:
        """Get current working directory"""
        return f"📂 Current directory: {os.getcwd()}"

    @staticmethod
    def change_directory(dirpath: str) -> str:
        """
        Change current working directory

        Args:
            dirpath: Path to directory

        Returns:
            Success or error message
        """
        try:
            path = Path(dirpath).expanduser()
            if not path.exists():
                return f"⚠ Directory not found: {dirpath}"

            if not path.is_dir():
                return f"⚠ Not a directory: {dirpath}"

            os.chdir(path)
            return f"✓ Changed to {path.absolute()}"

        except Exception as e:
            return f"⚠ Error changing directory: {e}"

    @staticmethod
    def file_info(filepath: str) -> str:
        """
        Get detailed file information

        Args:
            filepath: Path to file

        Returns:
            File information
        """
        try:
            path = Path(filepath).expanduser()
            if not path.exists():
                return f"⚠ Path not found: {filepath}"

            stat = path.stat()
            info = [
                f"📄 {path.absolute()}",
                f"Type: {'Directory' if path.is_dir() else 'File'}",
                f"Size: {stat.st_size} bytes",
                f"Modified: {stat.st_mtime}",
                f"Permissions: {oct(stat.st_mode)[-3:]}"
            ]

            return "\n".join(info)

        except Exception as e:
            return f"⚠ Error getting file info: {e}"

    @staticmethod
    def edit_file(filepath: str, old_text: str, new_text: str) -> str:
        """
        Find and replace text in file

        Args:
            filepath: Path to file
            old_text: Text to find
            new_text: Text to replace with

        Returns:
            Success or error message
        """
        try:
            path = Path(filepath).expanduser()
            if not path.exists():
                return f"⚠ File not found: {filepath}"

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            if old_text not in content:
                return f"⚠ Text not found in {filepath}"

            # Count occurrences
            count = content.count(old_text)
            new_content = content.replace(old_text, new_text)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return f"✓ Edited {filepath} ({count} occurrence{'s' if count > 1 else ''} replaced)"

        except Exception as e:
            return f"⚠ Error editing file: {e}"

    @staticmethod
    def find_files(pattern: str, path: str = ".") -> str:
        """
        Find files matching glob pattern

        Args:
            pattern: Glob pattern (e.g., "*.py", "test_*.txt")
            path: Directory to search in

        Returns:
            List of matching files
        """
        try:
            search_path = Path(path).expanduser()
            if not search_path.exists():
                return f"⚠ Path not found: {path}"

            matches = list(search_path.rglob(pattern))

            if not matches:
                return f"⚠ No files found matching '{pattern}'"

            result = f"🔍 Found {len(matches)} file{'s' if len(matches) > 1 else ''}:\n\n"

            # Show first 100 matches
            for match in matches[:100]:
                size = match.stat().st_size if match.is_file() else 0
                if match.is_dir():
                    result += f"📁 {match}\n"
                else:
                    result += f"📄 {match} ({size} bytes)\n"

            if len(matches) > 100:
                result += f"\n... and {len(matches) - 100} more"

            return result

        except Exception as e:
            return f"⚠ Error searching files: {e}"

    @staticmethod
    def grep_files(pattern: str, filepath: str = None, path: str = ".", file_types: list = None) -> str:
        """
        Search for pattern in files

        Args:
            pattern: Text or regex pattern to search
            filepath: Specific file to search (if None, searches all)
            path: Directory to search in
            file_types: List of extensions to search (e.g., ['.py', '.txt'])

        Returns:
            Matching lines with file:line format
        """
        try:
            import re

            if file_types is None:
                file_types = ['.py', '.txt', '.md', '.js', '.json', '.sh', '.yaml', '.yml']

            matches = []
            search_path = Path(path).expanduser()

            if filepath:
                # Search specific file
                files = [Path(filepath).expanduser()]
            else:
                # Search all files with matching extensions
                files = []
                for ext in file_types:
                    files.extend(search_path.rglob(f"*{ext}"))

            for file in files:
                try:
                    if not file.is_file():
                        continue

                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        for i, line in enumerate(f, 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                matches.append(f"{file}:{i}: {line.strip()}")

                except:
                    continue

            if not matches:
                return f"⚠ Pattern '{pattern}' not found"

            result = f"🔍 Found {len(matches)} match{'es' if len(matches) > 1 else ''}:\n\n"
            result += "\n".join(matches[:100])

            if len(matches) > 100:
                result += f"\n\n... and {len(matches) - 100} more"

            return result

        except Exception as e:
            return f"⚠ Error searching: {e}"

    @staticmethod
    def ask_perplexity(query: str, timeout: int = 30) -> Tuple[bool, str]:
        """
        Consult Perplexity CLI for research queries

        Args:
            query: Question to ask Perplexity
            timeout: Command timeout in seconds

        Returns:
            Tuple of (success: bool, response: str)
        """
        try:
            # Check if perplexity CLI is available
            check = subprocess.run(
                ["which", "perplexity"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if check.returncode != 0:
                return False, "Perplexity CLI not installed"

            # Call Perplexity with the query (standard CLI format)
            result = subprocess.run(
                ["perplexity", query],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, f"Perplexity error: {result.stderr.strip()}"

        except subprocess.TimeoutExpired:
            return False, "Perplexity request timed out"
        except FileNotFoundError:
            return False, "Perplexity CLI not found"
        except Exception as e:
            return False, f"Error calling Perplexity: {str(e)}"
