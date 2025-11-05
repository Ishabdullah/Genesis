#!/usr/bin/env python3
"""
Genesis Tool Functions
File system operations and utility commands
"""

import os
import shutil
from pathlib import Path
from typing import Optional

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
