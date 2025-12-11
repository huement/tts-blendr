"""File utility functions."""

from pathlib import Path


class FileUtils:
    """Utility functions for file operations."""

    @staticmethod
    def read_text_file(path: str | Path) -> str:
        """
        Read a text file and return its contents.

        Args:
            path: Path to the text file

        Returns:
            File contents as string

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not path.is_file():
            raise IOError(f"Path is not a file: {path}")
        return path.read_text(encoding="utf-8")

    @staticmethod
    def ensure_output_path(path: str | Path) -> Path:
        """
        Ensure the output directory exists, creating it if necessary.

        Args:
            path: Output file path

        Returns:
            Path object for the output file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def check_overwrite(path: str | Path) -> bool:
        """
        Check if a file exists and should be overwritten.

        Args:
            path: Path to check

        Returns:
            True if file doesn't exist or can be overwritten, False otherwise
        """
        path = Path(path)
        return not path.exists()

    @staticmethod
    def validate_file(path: str | Path) -> bool:
        """
        Validate a file path exists and is readable.

        Args:
            path: Path to validate

        Returns:
            True if file is valid, False otherwise
        """
        try:
            path = Path(path)
            return path.exists() and path.is_file() and path.stat().st_size > 0
        except (OSError, ValueError):
            return False

