#!/usr/bin/env python3
"""
Genesis Code Executor
Safely executes Python code in a sandboxed subprocess
"""

import os
import subprocess
import tempfile
import re
from typing import Tuple, Optional

class CodeExecutor:
    """Handles safe execution of Python code snippets"""

    def __init__(self, runtime_dir: str = "runtime"):
        """
        Initialize code executor

        Args:
            runtime_dir: Directory for temporary execution files
        """
        self.runtime_dir = runtime_dir
        os.makedirs(runtime_dir, exist_ok=True)
        self.temp_file = os.path.join(runtime_dir, "temp_exec.py")

    def extract_code_blocks(self, text: str) -> list:
        """
        Extract Python code blocks from markdown-style triple backticks

        Args:
            text: Text containing code blocks

        Returns:
            List of extracted code blocks
        """
        # Match ```python or ``` followed by code
        pattern = r'```(?:python)?\s*\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches

    def execute_code(self, code: str, timeout: int = 30) -> Tuple[bool, str]:
        """
        Execute Python code in a subprocess

        Args:
            code: Python code to execute
            timeout: Maximum execution time in seconds

        Returns:
            Tuple of (success: bool, output: str)
        """
        try:
            # Write code to temporary file
            with open(self.temp_file, 'w', encoding='utf-8') as f:
                f.write(code)

            # Execute in subprocess with timeout
            result = subprocess.run(
                ['python', self.temp_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()  # Execute in current working directory
            )

            # Combine stdout and stderr
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr

            success = result.returncode == 0
            return success, output.strip()

        except subprocess.TimeoutExpired:
            return False, f"⚠ Execution timeout ({timeout}s exceeded)"

        except Exception as e:
            return False, f"⚠ Execution error: {str(e)}"

    def execute_shell_command(self, command: str, timeout: int = 30) -> Tuple[bool, str]:
        """
        Execute a shell command safely

        Args:
            command: Shell command to execute
            timeout: Maximum execution time in seconds

        Returns:
            Tuple of (success: bool, output: str)
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr

            success = result.returncode == 0
            return success, output.strip()

        except subprocess.TimeoutExpired:
            return False, f"⚠ Command timeout ({timeout}s exceeded)"

        except Exception as e:
            return False, f"⚠ Command error: {str(e)}"

    def clean_runtime(self):
        """Remove temporary execution files"""
        try:
            if os.path.exists(self.temp_file):
                os.remove(self.temp_file)
        except Exception as e:
            print(f"⚠ Could not clean runtime: {e}")
