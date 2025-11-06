#!/usr/bin/env python3
"""
Genesis Time Sync Module
Provides real-time device time synchronization and temporal awareness
"""

import datetime
import time
import threading
import json
from pathlib import Path
from typing import Dict, Optional


class TimeSync:
    """Manages device time synchronization for temporal awareness"""

    def __init__(self, sync_interval: int = 60):
        """
        Initialize time synchronization

        Args:
            sync_interval: Time sync interval in seconds (default: 60)
        """
        self.sync_interval = sync_interval
        self.current_datetime = None
        self.current_date = None
        self.timezone = "local"
        self.last_sync = None
        self.is_running = False
        self.sync_thread = None
        self.state_file = Path("data/memory/system_state.json")
        self.knowledge_cutoff = datetime.date(2023, 12, 31)  # CodeLlama-7B cutoff

        # Initialize
        self._update_time()
        self._save_state()

    def _update_time(self):
        """Update current time from device"""
        now = datetime.datetime.now()
        self.current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
        self.current_date = now.date()
        self.last_sync = self.current_datetime

    def _save_state(self):
        """Save time state to disk"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)

            state = {
                "last_sync": self.last_sync,
                "timezone": self.timezone,
                "current_datetime": self.current_datetime,
                "knowledge_cutoff": self.knowledge_cutoff.isoformat()
            }

            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)

        except Exception as e:
            print(f"⚠️ Warning: Could not save time state: {e}")

    def _sync_loop(self):
        """Background thread for continuous time sync"""
        while self.is_running:
            time.sleep(self.sync_interval)
            self._update_time()
            self._save_state()

    def start_sync(self):
        """Start background time synchronization"""
        if not self.is_running:
            self.is_running = True
            self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
            self.sync_thread.start()
            print("Genesis> [Clock Synced 🕒]")

    def stop_sync(self):
        """Stop background time synchronization"""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=2)

    def get_device_time(self) -> str:
        """
        Get current device time

        Returns:
            Formatted datetime string (YYYY-MM-DD HH:MM:SS)
        """
        self._update_time()
        return self.current_datetime

    def get_device_date(self) -> str:
        """
        Get current device date

        Returns:
            ISO format date string (YYYY-MM-DD)
        """
        self._update_time()
        return self.current_date.isoformat()

    def get_current_datetime_obj(self) -> datetime.datetime:
        """
        Get current datetime object

        Returns:
            datetime object
        """
        return datetime.datetime.now()

    def is_after_knowledge_cutoff(self, date_str: Optional[str] = None) -> bool:
        """
        Check if a date (or current date) is after the knowledge cutoff

        Args:
            date_str: Optional date string to check (YYYY-MM-DD). If None, uses current date.

        Returns:
            True if date is after knowledge cutoff
        """
        try:
            if date_str:
                check_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                check_date = self.current_date

            return check_date > self.knowledge_cutoff
        except:
            return True  # Assume temporal if parsing fails

    def get_time_context_header(self) -> str:
        """
        Get time context header for display

        Returns:
            Formatted time context string
        """
        self._update_time()
        return f"Current system date/time: {self.current_datetime}"

    def get_temporal_metadata(self) -> Dict:
        """
        Get complete temporal metadata

        Returns:
            Dictionary with temporal information
        """
        self._update_time()
        return {
            "current_datetime": self.current_datetime,
            "current_date": self.current_date.isoformat(),
            "timezone": self.timezone,
            "last_sync": self.last_sync,
            "knowledge_cutoff": self.knowledge_cutoff.isoformat(),
            "is_post_cutoff": self.is_after_knowledge_cutoff()
        }

    def format_timestamp(self, dt: Optional[datetime.datetime] = None) -> str:
        """
        Format a timestamp in ISO format

        Args:
            dt: datetime object (uses current time if None)

        Returns:
            ISO formatted timestamp with timezone
        """
        if dt is None:
            dt = datetime.datetime.now()
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def get_time_difference(self, past_timestamp: str) -> Dict:
        """
        Calculate time difference from a past timestamp to now

        Args:
            past_timestamp: ISO format timestamp

        Returns:
            Dictionary with time difference details
        """
        try:
            past = datetime.datetime.fromisoformat(past_timestamp.replace('Z', '+00:00'))
            now = datetime.datetime.now()
            diff = now - past

            return {
                "seconds": diff.total_seconds(),
                "minutes": diff.total_seconds() / 60,
                "hours": diff.total_seconds() / 3600,
                "days": diff.days,
                "is_stale": diff.total_seconds() > 3600  # >1 hour is stale
            }
        except Exception as e:
            return {"error": str(e), "is_stale": True}


# Global instance
_time_sync_instance = None


def get_time_sync(sync_interval: int = 60) -> TimeSync:
    """
    Get or create global TimeSync instance

    Args:
        sync_interval: Time sync interval in seconds

    Returns:
        Global TimeSync instance
    """
    global _time_sync_instance
    if _time_sync_instance is None:
        _time_sync_instance = TimeSync(sync_interval)
    return _time_sync_instance


def get_device_time() -> str:
    """Convenience function to get device time"""
    return get_time_sync().get_device_time()


def get_device_date() -> str:
    """Convenience function to get device date"""
    return get_time_sync().get_device_date()


if __name__ == "__main__":
    # Test the time sync module
    sync = TimeSync()
    print(f"Current time: {sync.get_device_time()}")
    print(f"Current date: {sync.get_device_date()}")
    print(f"After cutoff: {sync.is_after_knowledge_cutoff()}")
    print(f"\nTemporal metadata: {json.dumps(sync.get_temporal_metadata(), indent=2)}")
