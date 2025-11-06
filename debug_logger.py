#!/usr/bin/env python3
"""
Genesis Debug Logger
Logs execution errors, misrouted commands, and debugging information
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from threading import Lock

class DebugLogger:
    """Handles debug logging for Genesis"""

    def __init__(self, log_file: str = "debug_log.json"):
        """
        Initialize debug logger

        Args:
            log_file: Path to debug log file
        """
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

        # Load existing log
        self.log_data = self._load_log()

    def _load_log(self) -> Dict[str, Any]:
        """Load debug log from file"""
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠ Could not load debug log: {e}")

        # Initialize empty log
        return {
            "session_start": datetime.now().isoformat(),
            "entries": []
        }

    def _save_log(self):
        """Save debug log to file"""
        try:
            with self._lock:
                with open(self.log_file, 'w') as f:
                    json.dump(self.log_data, f, indent=2)
        except Exception as e:
            print(f"⚠ Could not save debug log: {e}")

    def log_error(self, error_type: str, message: str, context: Optional[Dict] = None):
        """
        Log an error with context

        Args:
            error_type: Type of error (e.g., "llm_error", "fallback_failed")
            message: Error message
            context: Optional context dictionary
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "error",
            "error_type": error_type,
            "message": message,
            "context": context or {}
        }

        with self._lock:
            self.log_data["entries"].append(entry)

            # Keep only last 500 entries
            if len(self.log_data["entries"]) > 500:
                self.log_data["entries"] = self.log_data["entries"][-500:]

        self._save_log()

    def log_misrouted_execution(self, command: str, intended_target: str,
                                actual_target: str, context: Optional[Dict] = None):
        """
        Log a misrouted command execution

        Args:
            command: The command that was misrouted
            intended_target: Where it should have gone
            actual_target: Where it was sent
            context: Optional context
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "misrouted_execution",
            "command": command,
            "intended_target": intended_target,
            "actual_target": actual_target,
            "context": context or {}
        }

        with self._lock:
            self.log_data["entries"].append(entry)

            # Keep only last 500 entries
            if len(self.log_data["entries"]) > 500:
                self.log_data["entries"] = self.log_data["entries"][-500:]

        self._save_log()

    def log_fallback_attempt(self, query: str, local_confidence: float,
                            source: str, success: bool, error_msg: Optional[str] = None):
        """
        Log a fallback consultation attempt

        Args:
            query: User query
            local_confidence: Local confidence score
            source: External source (perplexity/claude)
            success: Whether the attempt succeeded
            error_msg: Error message if failed
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "fallback_attempt",
            "query": query[:200],
            "local_confidence": local_confidence,
            "source": source,
            "success": success,
            "error": error_msg
        }

        with self._lock:
            self.log_data["entries"].append(entry)

            # Keep only last 500 entries
            if len(self.log_data["entries"]) > 500:
                self.log_data["entries"] = self.log_data["entries"][-500:]

        self._save_log()

    def log_reasoning_issue(self, query: str, problem_type: str,
                           issue_description: str, context: Optional[Dict] = None):
        """
        Log a reasoning-related issue

        Args:
            query: User query
            problem_type: Detected problem type
            issue_description: Description of the issue
            context: Optional context
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "reasoning_issue",
            "query": query[:200],
            "problem_type": problem_type,
            "issue": issue_description,
            "context": context or {}
        }

        with self._lock:
            self.log_data["entries"].append(entry)

            # Keep only last 500 entries
            if len(self.log_data["entries"]) > 500:
                self.log_data["entries"] = self.log_data["entries"][-500:]

        self._save_log()

    def get_recent_entries(self, count: int = 20, entry_type: Optional[str] = None) -> list:
        """
        Get recent debug log entries

        Args:
            count: Number of entries to return
            entry_type: Optional filter by entry type

        Returns:
            List of recent entries
        """
        with self._lock:
            entries = self.log_data["entries"]

            if entry_type:
                entries = [e for e in entries if e.get("type") == entry_type]

            return entries[-count:]

    def get_error_summary(self) -> Dict[str, int]:
        """
        Get summary of errors by type

        Returns:
            Dictionary of error types and counts
        """
        with self._lock:
            error_counts = {}
            for entry in self.log_data["entries"]:
                if entry.get("type") == "error":
                    error_type = entry.get("error_type", "unknown")
                    error_counts[error_type] = error_counts.get(error_type, 0) + 1

            return error_counts

    def clear_old_entries(self, days: int = 7):
        """
        Clear entries older than specified days

        Args:
            days: Number of days to keep
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)

        with self._lock:
            self.log_data["entries"] = [
                e for e in self.log_data["entries"]
                if datetime.fromisoformat(e["timestamp"]) > cutoff
            ]

        self._save_log()
