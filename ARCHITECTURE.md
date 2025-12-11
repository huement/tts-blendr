# Voice Blender TUI - Architecture Plan

## 🏗️ High-Level Architecture

### Component Structure
```
voiceblend_tui/
├── app.py                 # Main Textual App class
├── widgets/               # UI Widget Components
│   ├── file_input.py     # Text file input section
│   ├── voice_selection.py # Voice 1/2 selection with mode toggle
│   ├── blend_ratio.py    # Blend ratio controls
│   ├── output_filename.py # Output filename input
│   ├── message_log.py    # Scrollable message/log area
│   └── header.py         # Custom header (optional)
├── services/              # Business Logic Services
│   ├── audio_service.py  # Audio generation orchestration
│   └── file_service.py   # File operations and validation
├── core/                  # Core Utilities
│   ├── blender.py        # kokoro-onnx integration
│   ├── config.py         # Configuration management
│   └── file_utils.py     # File utility functions
└── ui/                    # UI Layout Helpers (optional)
    └── layout.py         # Layout constants and helpers
```

## 📐 UI Layout Structure

```
┌─────────────────────────────────────────┐
│ Header: "Voice Blender"                 │
├─────────────────────────────────────────┤
│ ┌─────────────────┬───────────────────┐ │
│ │ Input File      │ Voice Selection   │ │
│ │ [file path]     │ Mode: ○ 1 ○ 2     │ │
│ │ [Browse]        │ Voice 1: [Select] │ │
│ │                 │ Voice 2: [Select] │ │
│ │                 │ (hidden if 1)     │ │
│ ├─────────────────┴───────────────────┤ │
│ │ Blend Ratio (if 2 voices)           │ │
│ │ [50/50 ▼] or [Input: 50]            │ │
│ ├─────────────────────────────────────┤ │
│ │ Output Filename                     │ │
│ │ [output]                            │ │
│ ├─────────────────────────────────────┤ │
│ │ Generate Audio [Button]             │ │
│ └─────────────────────────────────────┘ │
│ ┌─────────────────────────────────────┐ │
│ │ Message Log                         │ │
│ │ [scrollable messages]               │ │
│ └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│ Footer: Status messages                 │
└─────────────────────────────────────────┘
```

## 🔄 Data Flow

1. **User Input** → Widgets capture user selections
2. **State Management** → App class maintains state
3. **Validation** → Services validate inputs
4. **Audio Generation** → Async worker calls blender service
5. **UI Updates** → Messages logged, footer updated
6. **Completion** → UI re-enabled, success message shown

## 🎯 Key Design Decisions

1. **Modular Widgets**: Each UI section is a separate widget for reusability
2. **Service Layer**: Business logic separated from UI
3. **Async Operations**: All audio generation runs in workers
4. **State Management**: App class coordinates widget state
5. **Message Bus**: Events/messages for widget communication

## 📦 Component Responsibilities

### Widgets
- **FileInputWidget**: File path input, validation, file loading
- **VoiceSelectionWidget**: Voice mode (1/2), voice dropdowns
- **BlendRatioWidget**: Ratio selection (only visible for 2 voices)
- **OutputFilenameWidget**: Filename input, overwrite checking
- **MessageLogWidget**: Scrollable log of operations
- **GenerateButton**: Triggers generation, manages button state

### Services
- **AudioService**: Orchestrates audio generation, handles async operations
- **FileService**: File validation, path operations, overwrite checks

### Core
- **Blender**: Low-level kokoro-onnx integration
- **Config**: Application configuration
- **FileUtils**: Utility functions

## 🚀 Implementation Phases

1. **Phase 1**: Create widget structure and basic UI layout
2. **Phase 2**: Implement service layer and async operations
3. **Phase 3**: Integrate with kokoro-onnx blender
4. **Phase 4**: Add validation, error handling, polish

