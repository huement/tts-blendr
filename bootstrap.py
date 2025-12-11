"""Bootstrap module for setting up Python path."""

import sys
from pathlib import Path


def setup_path():
    """Add src directory to Python path for development."""
    src_path = Path(__file__).parent / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


# Automatically setup path when module is imported
setup_path()

