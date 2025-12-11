"""Configuration management."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppConfig:
    """Application configuration dataclass."""

    voices_path: Path = Path("voices")
    default_ratio: float = 0.5
    save_path: Path = Path("data")

    def __post_init__(self):
        """Ensure paths are Path objects."""
        if isinstance(self.voices_path, str):
            self.voices_path = Path(self.voices_path)
        if isinstance(self.save_path, str):
            self.save_path = Path(self.save_path)


class Config:
    """Configuration manager."""

    def __init__(self):
        """Initialize configuration with defaults."""
        self._config = AppConfig()

    def load(self) -> AppConfig:
        """Load configuration (placeholder - returns defaults for now)."""
        return self._config

    def save(self) -> None:
        """Save configuration (placeholder)."""
        # TODO: Implement configuration persistence
        pass

    @property
    def config(self) -> AppConfig:
        """Get current configuration."""
        return self._config

