# Voice Blender TUI - Implementation Guide

## 📋 Overview

This document provides a complete guide to the Voice Blender TUI implementation, including architecture, component structure, and extension points.

## 🏗️ Architecture

### Component Hierarchy

```
VoiceBlendApp (app.py)
├── Header
├── Main Container
│   ├── Controls Column (Vertical)
│   │   ├── FileInputWidget
│   │   ├── VoiceSelectionWidget
│   │   ├── BlendRatioWidget (conditionally visible)
│   │   ├── OutputFilenameWidget
│   │   └── Generate Button
│   └── Log Column (Vertical)
│       └── MessageLogWidget
└── Footer
```

### Data Flow

1. **User Input** → Widgets capture user selections
2. **Message Events** → Widgets post messages to parent (App)
3. **State Management** → App maintains state variables
4. **Validation** → Services validate inputs before generation
5. **Async Generation** → Worker thread calls AudioService
6. **UI Updates** → Messages logged, footer updated, UI re-enabled

## 📦 Component Details

### 1. FileInputWidget (`widgets/file_input.py`)

**Purpose**: Load text files for audio generation

**Features**:
- File path input field
- Browse button (placeholder for future file picker)
- File validation
- Status messages
- Posts `FileLoaded` message when file is loaded

**Usage**:
```python
file_input = FileInputWidget()
# Listen for FileLoaded message
```

### 2. VoiceSelectionWidget (`widgets/voice_selection.py`)

**Purpose**: Select voice mode (1 or 2 voices) and choose voices

**Features**:
- RadioSet for mode selection (1 Voice / 2 Voices)
- Voice 1 dropdown (always visible)
- Voice 2 dropdown (only visible when mode = 2)
- Dynamic show/hide of voice 2 selector
- Voice validation
- Posts `VoiceSelectionChanged` message

**Usage**:
```python
voice_widget = VoiceSelectionWidget(blender=blender)
# Listen for VoiceSelectionChanged message
mode, voice1, voice2 = voice_widget.get_selection()
```

### 3. BlendRatioWidget (`widgets/blend_ratio.py`)

**Purpose**: Select blend ratio for 2-voice mode

**Features**:
- Select dropdown with predefined ratios (50/50, 60/40, etc.)
- Only visible when 2 voices are selected
- Shows percentage breakdown
- Posts `BlendRatioChanged` message

**Usage**:
```python
blend_widget = BlendRatioWidget()
blend_widget.show()  # or hide()
ratio = blend_widget.get_ratio()  # 0.0 to 1.0
```

### 4. OutputFilenameWidget (`widgets/output_filename.py`)

**Purpose**: Enter output filename with validation

**Features**:
- Filename input (without .wav extension)
- Automatic .wav extension handling
- Invalid character validation
- File existence checking
- Posts `OutputFilenameChanged` message

**Usage**:
```python
output_widget = OutputFilenameWidget(default_output_dir=Path("data"))
filename = output_widget.get_filename()
full_path = output_widget.get_full_path()
```

### 5. MessageLogWidget (`widgets/message_log.py`)

**Purpose**: Display scrollable operation messages

**Features**:
- TextLog widget for scrollable messages
- Timestamped messages
- Color-coded by level (info, success, warning, error)
- Markup support for rich text

**Usage**:
```python
log_widget = MessageLogWidget()
log_widget.log("Operation started", "info")
log_widget.log("Success!", "success")
log_widget.log("Warning message", "warning")
log_widget.log("Error occurred", "error")
```

## 🔧 Services

### AudioService (`services/audio_service.py`)

**Purpose**: Orchestrate audio generation

**Methods**:
- `generate_audio()`: Main method for generating audio
  - Handles both 1-voice and 2-voice modes
  - For 1-voice: uses voice1 with 100% weight
  - For 2-voice: blends voice1 and voice2 with specified ratio

**Usage**:
```python
audio_service = AudioService(blender)
result = audio_service.generate_audio(
    text="Hello world",
    voice_mode=2,
    voice1="am_adam",
    voice2="af_bella",
    ratio=0.5,
    output_path="output.wav"
)
```

### FileService (`services/file_service.py`)

**Purpose**: File operations and validation

**Methods**:
- `validate_text_file()`: Validate text file exists and is readable
- `read_text_file()`: Read text file contents
- `ensure_output_path()`: Ensure output directory exists
- `check_file_exists()`: Check if file exists
- `get_output_path()`: Get full output path for filename

## 🎨 UI Layout

The app uses Textual's container system:

- **Header**: Standard Textual Header with app title
- **Main Container**: Contains two columns
  - **Left Column**: All input controls stacked vertically
  - **Right Column**: Message log
- **Footer**: Dynamic status messages

### Layout Structure

```python
Header
└── Main Container
    ├── Horizontal (top-section)
    │   ├── Vertical (controls-column)
    │   │   ├── FileInputWidget
    │   │   ├── VoiceSelectionWidget
    │   │   ├── BlendRatioWidget
    │   │   ├── OutputFilenameWidget
    │   │   └── Generate Button
    │   └── Vertical (log-column)
    │       └── MessageLogWidget
    └── Footer
```

## 🔄 Event Flow

### File Loading
1. User enters file path → `FileInputWidget.on_input_submitted()`
2. Widget loads file → `FileInputWidget.load_file()`
3. Widget posts `FileLoaded` message
4. App receives message → `VoiceBlendApp.on_file_input_file_loaded()`
5. App updates `self.selected_text`

### Voice Selection
1. User changes mode/voice → `VoiceSelectionWidget` handlers
2. Widget posts `VoiceSelectionChanged` message
3. App receives message → `VoiceBlendApp.on_voice_selection_voice_selection_changed()`
4. App shows/hides `BlendRatioWidget` based on mode
5. App updates state variables

### Generation
1. User clicks Generate → `VoiceBlendApp.on_button_pressed()`
2. App validates inputs → `VoiceBlendApp.handle_generate()`
3. App disables UI components
4. App runs worker → `VoiceBlendApp._generate_worker()`
5. Worker calls `AudioService.generate_audio()`
6. Worker completes → `VoiceBlendApp.on_worker_state_changed()`
7. App re-enables UI and shows result

## 🚀 Extension Points

### Adding a File Picker Dialog

Replace the Browse button with a proper file picker:

```python
# In FileInputWidget
async def on_button_pressed(self, event: Button.Pressed):
    if event.button.id == "browse-btn":
        # Use Textual's file picker
        path = await self.app.get_file_path()
        if path:
            input_widget = self.query_one("#file-path-input", Input)
            input_widget.value = str(path)
            await self.load_file()
```

### Adding Overwrite Confirmation

Add a confirmation dialog before overwriting:

```python
# In VoiceBlendApp.handle_generate()
if output_path.exists():
    confirmed = await self.app.push_screen_wait(ConfirmScreen(
        f"Overwrite {output_path.name}?"
    ))
    if not confirmed:
        return
```

### Adding Custom CSS Styling

Create a CSS file and link it:

```python
# In VoiceBlendApp
CSS_PATH = "styles.css"
```

### Adding More Voice Modes

Extend `VoiceSelectionWidget` to support 3+ voices:

1. Add more radio options
2. Create dynamic voice selectors
3. Update `BlendRatioWidget` to handle multiple ratios
4. Update `AudioService` to blend multiple voices

## 🐛 Troubleshooting

### Widgets Not Showing

- Check that widgets are properly mounted in `compose()`
- Verify widget IDs are unique
- Check for CSS display issues

### Messages Not Received

- Ensure message class names match pattern: `on_<widget_id>_<message_class_name>`
- Check that `post_message_to_parent()` is called
- Verify widget hierarchy (parent-child relationship)

### Generation Fails

- Check that kokoro-onnx models are downloaded
- Verify voice names are valid
- Check file permissions for output directory
- Review error messages in MessageLogWidget

## 📝 Best Practices

1. **State Management**: Keep state in App class, not in widgets
2. **Message Passing**: Use messages for widget-to-app communication
3. **Async Operations**: Always use workers for long-running tasks
4. **Error Handling**: Catch exceptions and log to MessageLogWidget
5. **UI Responsiveness**: Disable inputs during generation
6. **Validation**: Validate inputs before starting generation

## 🔗 Integration with kokoro-onnx

The app integrates with kokoro-onnx through:

1. **VoiceBlender** (`core/blender.py`): Low-level kokoro-onnx wrapper
2. **AudioService** (`services/audio_service.py`): High-level orchestration
3. **VoiceSelectionWidget**: Loads available voices from blender

To extend:
- Add voice filtering/grouping
- Add voice preview functionality
- Add custom voice parameters (speed, pitch, etc.)

