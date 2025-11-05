#!/usr/bin/env python3
"""
Genesis Bridge Server
Enables bidirectional communication between Claude Code and Genesis
for collaborative planning and execution
"""

import os
import json
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify

class GenesisBridge:
    """HTTP bridge server for Claude Code ↔ Genesis collaboration"""

    def __init__(self, host='127.0.0.1', port=5050, api_key='localonly'):
        """
        Initialize Genesis Bridge

        Args:
            host: Server host (localhost only for security)
            port: Server port
            api_key: Required API key for requests
        """
        self.host = host
        self.port = port
        self.api_key = api_key
        self.runtime_dir = "runtime"
        self.temp_file = os.path.join(self.runtime_dir, "temp_exec.py")
        self.log_file = "bridge_log.txt"
        self.app = Flask(__name__)
        self.server_thread = None
        self.running = False

        # Ensure runtime directory exists
        os.makedirs(self.runtime_dir, exist_ok=True)

        # Register routes
        self._setup_routes()

    def _setup_routes(self):
        """Configure Flask routes"""

        @self.app.route('/run', methods=['POST'])
        def run_code():
            """Execute Python code and return output"""
            return self._handle_run_request()

        @self.app.route('/status', methods=['GET'])
        def status():
            """Check bridge status"""
            return jsonify({
                'status': 'running',
                'host': self.host,
                'port': self.port,
                'runtime_dir': self.runtime_dir
            })

        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({'healthy': True})

    def _verify_api_key(self) -> bool:
        """
        Verify API key in request headers

        Returns:
            True if valid, False otherwise
        """
        provided_key = request.headers.get('X-Genesis-Key', '')
        return provided_key == self.api_key

    def _verify_localhost(self) -> bool:
        """
        Verify request is from localhost

        Returns:
            True if from localhost, False otherwise
        """
        remote_addr = request.remote_addr
        return remote_addr in ['127.0.0.1', 'localhost', '::1']

    def _sanitize_code(self, code: str) -> tuple:
        """
        Basic code sanitization and safety checks

        Args:
            code: Python code to sanitize

        Returns:
            Tuple of (is_safe: bool, reason: str)
        """
        # Disallow dangerous imports and operations
        dangerous_patterns = [
            'import socket',
            'import requests',
            'import urllib',
            'import http.client',
            'os.system(',
            'subprocess.Popen',
            'eval(',
            'exec(',
            '__import__',
            'open("/etc',
            'open("/sys',
            'open("/proc',
        ]

        for pattern in dangerous_patterns:
            if pattern in code:
                return False, f"Potentially unsafe operation detected: {pattern}"

        return True, "Safe"

    def _log_request(self, code: str, output: str, success: bool):
        """
        Log bridge requests to file

        Args:
            code: Executed code
            output: Execution output
            success: Whether execution succeeded
        """
        try:
            timestamp = datetime.now().isoformat()
            log_entry = {
                'timestamp': timestamp,
                'success': success,
                'code_length': len(code),
                'output_length': len(output),
                'code_preview': code[:100] + ('...' if len(code) > 100 else ''),
                'output_preview': output[:200] + ('...' if len(output) > 200 else '')
            }

            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')

        except Exception as e:
            print(f"⚠ Warning: Could not write to log: {e}")

    def _execute_code(self, code: str, timeout: int = 20) -> dict:
        """
        Execute Python code in sandboxed subprocess

        Args:
            code: Python code to execute
            timeout: Maximum execution time in seconds

        Returns:
            Dictionary with output and success status
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
                cwd=os.path.abspath(self.runtime_dir)  # Execute in runtime dir
            )

            # Combine stdout and stderr
            output = result.stdout
            if result.stderr:
                output += "\nSTDERR:\n" + result.stderr

            success = result.returncode == 0

            return {
                'success': success,
                'output': output.strip(),
                'return_code': result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': f"⚠ Execution timeout ({timeout}s exceeded)",
                'return_code': -1
            }

        except Exception as e:
            return {
                'success': False,
                'output': f"⚠ Execution error: {str(e)}",
                'return_code': -1
            }

    def _handle_run_request(self):
        """
        Handle POST /run endpoint

        Returns:
            JSON response with execution results
        """
        # Security checks
        if not self._verify_localhost():
            return jsonify({
                'error': 'Access denied: requests must come from localhost'
            }), 403

        if not self._verify_api_key():
            return jsonify({
                'error': 'Invalid or missing API key'
            }), 401

        # Parse request
        try:
            data = request.get_json()
            if not data or 'code' not in data:
                return jsonify({
                    'error': 'Missing required field: code'
                }), 400

            code = data['code']

            # Sanitize code
            is_safe, reason = self._sanitize_code(code)
            if not is_safe:
                return jsonify({
                    'error': f'Code rejected: {reason}',
                    'output': ''
                }), 400

            # Execute code
            result = self._execute_code(code)

            # Log request
            self._log_request(code, result['output'], result['success'])

            # Return response
            return jsonify({
                'output': result['output'],
                'success': result['success'],
                'return_code': result['return_code']
            }), 200

        except Exception as e:
            error_msg = f"Bridge error: {str(e)}"
            self._log_request("ERROR", error_msg, False)
            return jsonify({
                'error': error_msg,
                'output': ''
            }), 500

    def start(self):
        """Start the bridge server in a background thread"""
        if self.running:
            print("⚠ Bridge already running")
            return

        def run_server():
            self.app.run(
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False
            )

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.running = True

        print(f"✓ Genesis Bridge started on {self.host}:{self.port}")
        print(f"  API Key: {self.api_key}")
        print(f"  Log file: {self.log_file}")

    def stop(self):
        """Stop the bridge server"""
        if not self.running:
            print("⚠ Bridge not running")
            return

        # Note: Flask development server cannot be gracefully stopped from code
        # In production, use a proper WSGI server like gunicorn
        print("⚠ Bridge server will stop when Genesis exits")
        self.running = False

    def test_connection(self) -> bool:
        """
        Test if bridge is responding

        Returns:
            True if bridge is accessible
        """
        try:
            import requests
            response = requests.get(f'http://{self.host}:{self.port}/health')
            return response.status_code == 200
        except:
            return False


def execute_remote_code(code: str, host='127.0.0.1', port=5050, api_key='localonly') -> dict:
    """
    Client helper function to execute code via Genesis Bridge

    Args:
        code: Python code to execute
        host: Bridge host
        port: Bridge port
        api_key: API key for authentication

    Returns:
        Dictionary with execution results
    """
    try:
        import requests

        url = f'http://{host}:{port}/run'
        headers = {
            'Content-Type': 'application/json',
            'X-Genesis-Key': api_key
        }
        data = {'code': code}

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            return response.json()
        else:
            return {
                'success': False,
                'output': f"Bridge error: HTTP {response.status_code}",
                'error': response.text
            }

    except Exception as e:
        return {
            'success': False,
            'output': f"Connection error: {str(e)}"
        }


# Standalone mode for testing
if __name__ == "__main__":
    print("🧬 Genesis Bridge - Standalone Mode\n")

    bridge = GenesisBridge()
    bridge.start()

    print("\nBridge running. Test with:")
    print(f'curl -X POST -H "Content-Type: application/json" \\')
    print(f'     -H "X-Genesis-Key: localonly" \\')
    print(f'     -d \'{{"code":"print(\\"Hello from Genesis!\\")"}} \' \\')
    print(f'     http://127.0.0.1:5050/run')
    print("\nPress Ctrl+C to stop")

    try:
        # Keep main thread alive
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping bridge...")
        bridge.stop()
