# voiceblend-tui

A Textual-based TUI application for voice blending.

## Setup

**Note:** This project requires Python 3.10-3.13 (Python 3.12 recommended) due to kokoro-onnx dependencies.

1. Create a virtual environment with Python 3.12:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies and package:
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install package in editable mode
   ```
   
   Or use the install script:
   ```bash
   ./scripts/install.sh
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Project Structure

- `src/voiceblend_tui/` - Main application package
- `voices/` - ONNX model storage
- `data/` - Sample input files
- `scripts/` - Installer scripts

