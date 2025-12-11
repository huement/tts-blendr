"""Settings management with .env file persistence."""

import os
from pathlib import Path
from typing import Optional


class Settings:
    """Manages application settings with .env file persistence."""
    
    def __init__(self, env_file: Path = None):
        """Initialize settings manager.
        
        Args:
            env_file: Path to .env file (defaults to .env in project root)
        """
        if env_file is None:
            # Find project root (where .env should be)
            env_file = Path(__file__).parent.parent.parent.parent / ".env"
        self.env_file = env_file
        self._settings: dict[str, str] = {}
        self.load()
    
    def load(self) -> None:
        """Load settings from .env file."""
        if not self.env_file.exists():
            return
        
        try:
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        self._settings[key] = value
        except Exception as e:
            print(f"Warning: Could not load .env file: {e}")
    
    def save(self) -> None:
        """Save current settings to .env file."""
        try:
            # Ensure directory exists
            self.env_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.env_file, 'w') as f:
                f.write("# Voice Blender TUI Settings\n")
                f.write("# Auto-generated - do not edit manually\n\n")
                for key, value in sorted(self._settings.items()):
                    # Escape quotes in values
                    if '"' in value or ' ' in value:
                        value = f'"{value}"'
                    f.write(f"{key}={value}\n")
        except Exception as e:
            print(f"Warning: Could not save .env file: {e}")
    
    def get(self, key: str, default: str = "") -> str:
        """Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        return self._settings.get(key, default)
    
    def set(self, key: str, value: str) -> None:
        """Set a setting value and save to .env.
        
        Args:
            key: Setting key
            value: Setting value
        """
        self._settings[key] = str(value)
        self.save()
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get a setting as integer."""
        try:
            return int(self.get(key, str(default)))
        except ValueError:
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get a setting as float."""
        try:
            return float(self.get(key, str(default)))
        except ValueError:
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a setting as boolean."""
        value = self.get(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')

