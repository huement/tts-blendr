"""File service for file operations and validation."""

from pathlib import Path
from voiceblend_tui.core.file_utils import FileUtils


class FileService:
    """Service for file operations."""
    
    def __init__(self, default_output_dir: Path = None):
        """Initialize file service.
        
        Args:
            default_output_dir: Default directory for output files
        """
        self.default_output_dir = default_output_dir or Path("data")
    
    def validate_text_file(self, file_path: Path | str) -> tuple[bool, str]:
        """
        Validate that a text file exists and is readable.
        
        Args:
            file_path: Path to text file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return False, f"File not found: {path}"
            if not path.is_file():
                return False, f"Path is not a file: {path}"
            if not FileUtils.validate_file(path):
                return False, f"File is empty or unreadable: {path}"
            return True, ""
        except Exception as e:
            return False, f"Error validating file: {e}"
    
    def read_text_file(self, file_path: Path | str) -> str:
        """
        Read text file contents.
        
        Args:
            file_path: Path to text file
            
        Returns:
            File contents as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        return FileUtils.read_text_file(file_path)
    
    def ensure_output_path(self, output_path: Path | str) -> Path:
        """
        Ensure output directory exists.
        
        Args:
            output_path: Output file path
            
        Returns:
            Path object for output file
        """
        path = Path(output_path)
        return FileUtils.ensure_output_path(path)
    
    def check_file_exists(self, file_path: Path | str) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file exists
        """
        return Path(file_path).exists()
    
    def get_output_path(self, filename: str) -> Path:
        """
        Get full output path for a filename.
        
        Args:
            filename: Filename without extension
            
        Returns:
            Full path with .wav extension
        """
        if filename.endswith(".wav"):
            filename = filename[:-4]
        return self.default_output_dir / f"{filename}.wav"

