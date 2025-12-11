# Voice Blender TUI - Quick Start Guide

## 🚀 Running the Application

```bash
python main.py
```

## 📋 What's New

The app has been completely redesigned with a modern, modular architecture:

### ✅ Features Implemented

1. **File Input Section**
   - Text file path input
   - File validation
   - Status messages

2. **Voice Selection**
   - Choose between 1 or 2 voices
   - Voice dropdown selectors
   - Dynamic UI (Voice 2 only shows when needed)

3. **Blend Ratio** (for 2 voices)
   - Predefined ratio options (50/50, 60/40, etc.)
   - Only visible when 2 voices selected

4. **Output Filename**
   - Filename input (without extension)
   - Automatic validation
   - Overwrite warnings

5. **Message Log**
   - Scrollable message area
   - Color-coded messages (info, success, warning, error)
   - Timestamped entries

6. **Generate Button**
   - Disables UI during generation
   - Shows progress in footer
   - Async audio generation

## 🎯 How to Use

1. **Load a Text File**
   - Enter the path to a text file in the "Input File" section
   - Press Enter or click "Browse" (placeholder)
   - File will be validated and loaded

2. **Select Voice Mode**
   - Choose "1 Voice" or "2 Voices" using the radio buttons
   - Select Voice 1 from the dropdown
   - If using 2 voices, select Voice 2 (appears automatically)

3. **Set Blend Ratio** (2 voices only)
   - Choose a ratio from the dropdown
   - Options show percentage split (e.g., "50/50" = equal blend)

4. **Enter Output Filename**
   - Type filename without .wav extension
   - App will show if file exists (will be overwritten)

5. **Generate Audio**
   - Click "🎵 Generate Audio" button
   - UI will disable during generation
   - Progress shown in footer and message log
   - Audio saved to `data/` directory

## 📁 File Structure

```
src/voiceblend_tui/
├── app.py                    # Main application
├── widgets/                  # UI Components
│   ├── file_input.py        # File loading widget
│   ├── voice_selection.py   # Voice selection widget
│   ├── blend_ratio.py       # Blend ratio widget
│   ├── output_filename.py   # Output filename widget
│   └── message_log.py       # Message log widget
├── services/                 # Business Logic
│   ├── audio_service.py     # Audio generation service
│   └── file_service.py      # File operations service
└── core/                     # Core Utilities
    ├── blender.py           # kokoro-onnx integration
    ├── config.py            # Configuration
    └── file_utils.py        # File utilities
```

## 🔧 Architecture Highlights

- **Modular Widgets**: Each UI section is a separate, reusable widget
- **Service Layer**: Business logic separated from UI
- **Message-Based Communication**: Widgets communicate via Textual messages
- **Async Operations**: Audio generation runs in worker threads
- **State Management**: App class coordinates widget state

## 📖 Documentation

- **ARCHITECTURE.md**: Detailed architecture and design decisions
- **IMPLEMENTATION_GUIDE.md**: Complete implementation guide with examples

## 🐛 Troubleshooting

### No voices available
- Models will download automatically on first use
- Check internet connection
- Models download to `voices/` directory

### Generation fails
- Check that text file is loaded
- Verify voice selections are valid
- Check output directory permissions
- Review error messages in message log

### UI not responsive
- Generation runs in background thread
- UI should remain responsive
- Check message log for progress updates

## 🎨 Customization

### Adding CSS Styling

Create a `styles.css` file and update `app.py`:

```python
CSS_PATH = "styles.css"
```

### Adding File Picker

Replace Browse button with Textual's file picker (see IMPLEMENTATION_GUIDE.md)

### Adding Overwrite Confirmation

Add confirmation dialog before overwriting files (see IMPLEMENTATION_GUIDE.md)

## 📝 Next Steps

1. Test the application with various text files
2. Try different voice combinations
3. Experiment with blend ratios
4. Review ARCHITECTURE.md for extension points
5. Check IMPLEMENTATION_GUIDE.md for advanced features

