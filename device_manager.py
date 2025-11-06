#!/usr/bin/env python3
"""
Genesis Device Manager
Provides access to Android device capabilities via Termux API
"""

import json
import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple, Any


class DeviceManager:
    """Manages Android device capabilities through Termux API"""

    def __init__(self, media_dir: str = "data/media"):
        """
        Initialize device manager

        Args:
            media_dir: Directory for storing media files (photos, videos, audio)
        """
        self.media_dir = Path(media_dir)
        self.media_dir.mkdir(parents=True, exist_ok=True)

        # Check if termux-api is available
        self.api_available = self._check_termux_api()

        # Supported actions
        self.actions = {
            "get_location": self.get_location,
            "get_date_time": self.get_date_time,
            "get_weather": self.get_weather,
            "take_photo": self.take_photo,
            "record_video": self.record_video,
            "record_audio": self.record_audio,
            "toggle_flashlight": self.toggle_flashlight,
            "adjust_brightness": self.adjust_brightness,
            "adjust_volume": self.adjust_volume,
        }

        # Flashlight state
        self.flashlight_on = False

    def _check_termux_api(self) -> bool:
        """Check if termux-api is available"""
        try:
            result = subprocess.run(
                ["which", "termux-location"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception:
            return False

    def _run_termux_command(self, command: list, timeout: int = 30) -> Tuple[bool, str]:
        """
        Run a termux-api command

        Args:
            command: Command list to execute
            timeout: Command timeout in seconds

        Returns:
            (success, output) tuple
        """
        if not self.api_available:
            return False, "Termux API not available. Install with: pkg install termux-api"

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def execute_action(self, action: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute a device action

        Args:
            action: Action name
            parameters: Action parameters

        Returns:
            Result dictionary with success status and data
        """
        if action not in self.actions:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "available_actions": list(self.actions.keys())
            }

        try:
            params = parameters or {}
            result = self.actions[action](**params)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Action execution failed: {str(e)}"
            }

    def get_location(self) -> Dict[str, Any]:
        """
        Get device GPS location

        Returns:
            Location data with latitude, longitude, and address
        """
        success, output = self._run_termux_command(["termux-location", "-p", "gps"])

        if not success:
            return {
                "success": False,
                "error": output
            }

        try:
            location_data = json.loads(output)
            return {
                "success": True,
                "latitude": location_data.get("latitude"),
                "longitude": location_data.get("longitude"),
                "altitude": location_data.get("altitude"),
                "accuracy": location_data.get("accuracy"),
                "provider": location_data.get("provider", "gps")
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Failed to parse location data"
            }

    def get_date_time(self) -> Dict[str, Any]:
        """
        Get current device date and time

        Returns:
            Current date/time information
        """
        now = datetime.now()

        return {
            "success": True,
            "datetime": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "day_of_week": now.strftime("%A"),
            "timezone": now.astimezone().tzname(),
            "timestamp": int(now.timestamp())
        }

    def get_weather(self, location: Optional[str] = None, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get weather information

        Args:
            location: Location string (lat,lon or city name)
            date: Date string (YYYY-MM-DD) for forecast

        Returns:
            Weather data (NOTE: This requires external API integration)
        """
        # This is a placeholder - actual weather requires API integration
        # You would integrate with OpenWeatherMap, wttr.in, or similar service

        return {
            "success": False,
            "error": "Weather API not yet integrated",
            "note": "To integrate weather: Use wttr.in, OpenWeatherMap, or WeatherAPI",
            "location": location,
            "date": date
        }

    def take_photo(self, camera: str = "back", filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Take a photo with device camera

        Args:
            camera: Camera to use ("back" or "front")
            filename: Optional filename (auto-generated if not provided)

        Returns:
            Photo capture result with file path
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"photo_{timestamp}.jpg"

        filepath = self.media_dir / filename
        camera_id = "0" if camera == "back" else "1"

        success, output = self._run_termux_command([
            "termux-camera-photo",
            "-c", camera_id,
            str(filepath)
        ])

        if success and filepath.exists():
            return {
                "success": True,
                "filepath": str(filepath),
                "filename": filename,
                "camera": camera,
                "size_bytes": filepath.stat().st_size
            }
        else:
            return {
                "success": False,
                "error": output or "Photo capture failed"
            }

    def record_video(self, duration: int = 10, camera: str = "back", filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Record video with device camera

        Args:
            duration: Recording duration in seconds
            camera: Camera to use ("back" or "front")
            filename: Optional filename

        Returns:
            Video recording result with file path
        """
        # Note: termux-camera-video might not be available in all termux-api versions
        # This is a placeholder implementation

        return {
            "success": False,
            "error": "Video recording not yet fully implemented",
            "note": "termux-camera-video may not be available in all Termux API versions",
            "duration": duration,
            "camera": camera
        }

    def record_audio(self, duration: int = 10, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Record audio from device microphone

        Args:
            duration: Recording duration in seconds
            filename: Optional filename

        Returns:
            Audio recording result with file path
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audio_{timestamp}.m4a"

        filepath = self.media_dir / filename

        success, output = self._run_termux_command([
            "termux-microphone-record",
            "-f", str(filepath),
            "-l", str(duration)
        ], timeout=duration + 5)

        if success and filepath.exists():
            return {
                "success": True,
                "filepath": str(filepath),
                "filename": filename,
                "duration_seconds": duration,
                "size_bytes": filepath.stat().st_size
            }
        else:
            return {
                "success": False,
                "error": output or "Audio recording failed"
            }

    def toggle_flashlight(self, state: Optional[bool] = None) -> Dict[str, Any]:
        """
        Toggle device flashlight on/off

        Args:
            state: Explicit state (True=on, False=off, None=toggle)

        Returns:
            Flashlight state result
        """
        if state is None:
            # Toggle
            new_state = not self.flashlight_on
        else:
            new_state = state

        command = ["termux-torch", "on" if new_state else "off"]
        success, output = self._run_termux_command(command, timeout=5)

        if success:
            self.flashlight_on = new_state
            return {
                "success": True,
                "state": "on" if new_state else "off",
                "flashlight_on": new_state
            }
        else:
            return {
                "success": False,
                "error": output
            }

    def adjust_brightness(self, brightness: int) -> Dict[str, Any]:
        """
        Adjust screen brightness

        Args:
            brightness: Brightness level (0-255)

        Returns:
            Brightness adjustment result
        """
        # Clamp to valid range
        brightness = max(0, min(255, brightness))

        success, output = self._run_termux_command([
            "termux-brightness",
            str(brightness)
        ], timeout=5)

        if success:
            return {
                "success": True,
                "brightness": brightness,
                "brightness_percent": int((brightness / 255) * 100)
            }
        else:
            return {
                "success": False,
                "error": output
            }

    def adjust_volume(self, stream: str = "music", volume: Optional[int] = None, change: Optional[int] = None) -> Dict[str, Any]:
        """
        Adjust device volume

        Args:
            stream: Audio stream ("music", "ring", "alarm", "notification", "system")
            volume: Absolute volume level (0-15)
            change: Relative volume change (+/- value)

        Returns:
            Volume adjustment result
        """
        if volume is not None:
            # Set absolute volume
            volume = max(0, min(15, volume))
            command = ["termux-volume", stream, str(volume)]
        elif change is not None:
            # Relative change - need to get current volume first
            success, output = self._run_termux_command(["termux-volume"], timeout=5)
            if not success:
                return {"success": False, "error": "Failed to get current volume"}

            try:
                volumes = json.loads(output)
                current = volumes.get(stream, 7)
                new_volume = max(0, min(15, current + change))
                command = ["termux-volume", stream, str(new_volume)]
            except Exception as e:
                return {"success": False, "error": f"Failed to parse volume: {str(e)}"}
        else:
            # Get current volume
            success, output = self._run_termux_command(["termux-volume"], timeout=5)
            if success:
                try:
                    volumes = json.loads(output)
                    return {
                        "success": True,
                        "volumes": volumes,
                        "stream": stream,
                        "current_volume": volumes.get(stream)
                    }
                except Exception as e:
                    return {"success": False, "error": f"Failed to parse volume: {str(e)}"}
            else:
                return {"success": False, "error": output}

        success, output = self._run_termux_command(command, timeout=5)

        if success:
            return {
                "success": True,
                "stream": stream,
                "volume": volume if volume is not None else current + change
            }
        else:
            return {
                "success": False,
                "error": output
            }


# Global instance
_device_manager_instance = None


def get_device_manager() -> DeviceManager:
    """Get or create global DeviceManager instance"""
    global _device_manager_instance
    if _device_manager_instance is None:
        _device_manager_instance = DeviceManager()
    return _device_manager_instance


if __name__ == "__main__":
    # Test the device manager
    dm = DeviceManager()

    print("Device Manager Test\n" + "=" * 50)
    print(f"Termux API Available: {dm.api_available}\n")

    # Test date/time
    print("Testing get_date_time:")
    result = dm.get_date_time()
    print(json.dumps(result, indent=2))
    print()

    # Test available actions
    print("Available Actions:")
    for action in dm.actions.keys():
        print(f"  - {action}")
