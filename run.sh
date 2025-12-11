#!/usr/bin/env bash

echo "🚀 Starting VoiceBlend-TUI..."

# Detect python
if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    echo "❌ Python 3.10–3.13 is required but not found."
    exit 1
fi

# Check Python version
VERSION=$($PY -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
case "$VERSION" in
  3.10|3.11|3.12|3.13)
    ;;
  *)
    echo "❌ Python version $VERSION detected."
    echo "   VoiceBlend-TUI requires Python 3.10–3.13 (3.12 recommended)."
    exit 1
    ;;
esac

# Create venv if missing
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $PY -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies if needed
if [ ! -d "venv/lib" ] || [ -z "$(pip freeze | grep textual)" ]; then
    echo "📚 Installing dependencies..."
    pip install -r requirements.txt
    pip install -e .
fi

echo "🎉 Launching VoiceBlend-TUI..."
python main.py
