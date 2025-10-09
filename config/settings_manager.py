"""Application settings management with persistent storage."""

import json
from pathlib import Path
from typing import Any


class SettingsManager:
    """Manages application settings with JSON persistence."""

    def __init__(self, config_file: str = "md_reader_settings.json") -> None:
        """
        Initialize settings manager.

        Args:
            config_file: Name of the settings file (stored in user's home directory)
        """
        self.config_path = Path.home() / ".config" / "md_reader" / config_file
        self.settings: dict[str, Any] = {}
        self._load_settings()

    def _load_settings(self) -> None:
        """Load settings from disk, or create default settings if file doesn't exist."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    self.settings = json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, start with defaults
                self.settings = self._get_default_settings()
        else:
            self.settings = self._get_default_settings()

    def _get_default_settings(self) -> dict[str, Any]:
        """Get default settings structure."""
        return {
            "window": {"width": 1000, "height": 700, "x": 100, "y": 100, "maximized": False},
            "recent_files": [],
            "max_recent_files": 5,
        }

    def save_settings(self) -> None:
        """Save current settings to disk."""
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.config_path, "w") as f:
                json.dump(self.settings, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.

        Args:
            key: Setting key (can use dot notation for nested keys, e.g. 'window.width')
            default: Default value if key doesn't exist

        Returns:
            Setting value or default
        """
        keys = key.split(".")
        value = self.settings

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a setting value.

        Args:
            key: Setting key (can use dot notation for nested keys, e.g. 'window.width')
            value: Value to set
        """
        keys = key.split(".")
        current = self.settings

        # Navigate to the correct nested dict, creating if necessary
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # Set the final value
        current[keys[-1]] = value

    def get_recent_files(self) -> list[str]:
        """Get list of recently opened files."""
        return self.settings.get("recent_files", [])

    def add_recent_file(self, file_path: str) -> None:
        """
        Add a file to the recent files list.

        Args:
            file_path: Absolute path to the file
        """
        recent = self.get_recent_files()

        # Remove if already in list (to move to top)
        if file_path in recent:
            recent.remove(file_path)

        # Add to beginning of list
        recent.insert(0, file_path)

        # Keep only max_recent_files
        max_files = self.get("max_recent_files", 5)
        recent = recent[:max_files]

        self.settings["recent_files"] = recent
        self.save_settings()
