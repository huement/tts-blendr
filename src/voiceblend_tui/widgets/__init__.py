"""Widget components for the TUI."""

# New widgets
from .file_input import FileInputWidget, FileLoaded
from .file_picker_modal import FileSelectionModal as FilePickerModal
from .voice_selection import VoiceSelectionWidget, VoiceSelectionChanged
from .blend_ratio import BlendRatioWidget, BlendRatioChanged
from .output_filename import OutputFilenameWidget, OutputFilenameChanged
from .message_log import MessageLogWidget

# Legacy widgets (kept for compatibility)
from .header import CustomHeader
from .footer import CustomFooter
from .file_picker import FilePicker
from .blend_controls import BlendControls

__all__ = [
    # New widgets
    "FileInputWidget",
    "FileLoaded",
    "FilePickerModal",
    "VoiceSelectionWidget",
    "VoiceSelectionChanged",
    "BlendRatioWidget",
    "BlendRatioChanged",
    "OutputFilenameWidget",
    "OutputFilenameChanged",
    "MessageLogWidget",
    # Legacy widgets
    "CustomHeader",
    "CustomFooter",
    "FilePicker",
    "BlendControls",
]

