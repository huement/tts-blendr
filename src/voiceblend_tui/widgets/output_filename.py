"""Output filename widget with validation."""

from pathlib import Path
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Static, Input
from textual.message import Message


class OutputFilenameChanged(Message):
    """Message sent when output filename changes."""
    
    def __init__(self, filename: str, is_valid: bool):
        super().__init__()
        self.filename = filename
        self.is_valid = is_valid


class OutputFilenameWidget(Widget):
    """Widget for entering output filename."""
    
    def __init__(self, default_output_dir: Path = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_output_dir = default_output_dir or Path("data")
        self.current_filename: str = "output"
        self.is_valid: bool = True
    
    def compose(self):
        """Create child widgets."""
        with Vertical():
            yield Static("💾 Output Filename", classes="section-title")
            yield Static("(without .wav extension)", classes="hint")
            yield Input(
                value="output",
                placeholder="output",
                id="output-filename-input",
            )
            yield Static("", id="output-filename-status", classes="status-text")
    
    def on_mount(self):
        """Called when widget is mounted."""
        self.add_class("output-filename-section")
        self.update_status()
    
    def on_input_changed(self, event: Input.Changed):
        """Handle filename input change."""
        if event.input.id == "output-filename-input":
            filename = event.value.strip()
            if not filename:
                filename = "output"
            
            # Remove .wav extension if user added it
            if filename.endswith(".wav"):
                filename = filename[:-4]
                event.input.value = filename
            
            self.current_filename = filename
            self.validate_filename()
            self.update_status()
            self.notify_filename_changed()
    
    def validate_filename(self):
        """Validate the filename."""
        if not self.current_filename:
            self.is_valid = False
            return
        
        # Check for invalid characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in self.current_filename for char in invalid_chars):
            self.is_valid = False
            return
        
        # Check if file exists
        output_path = self.default_output_dir / f"{self.current_filename}.wav"
        self.is_valid = True
    
    def update_status(self):
        """Update status text."""
        status_widget = self.query_one("#output-filename-status", Static)
        output_path = self.default_output_dir / f"{self.current_filename}.wav"
        
        if not self.is_valid:
            status_widget.update("❌ Invalid filename")
            status_widget.set_classes("status-text error")
        elif output_path.exists():
            status_widget.update(
                f"⚠️  File exists: {output_path.name} (will be overwritten)"
            )
            status_widget.set_classes("status-text warning")
        else:
            status_widget.update(
                f"✅ Will save to: {output_path.name}"
            )
            status_widget.set_classes("status-text success")
    
    def notify_filename_changed(self):
        """Notify parent of filename change."""
        self.post_message(
            OutputFilenameChanged(self.current_filename, self.is_valid)
        )
    
    def get_filename(self) -> str:
        """Get current filename."""
        return self.current_filename
    
    def get_full_path(self) -> Path:
        """Get full output path."""
        return self.default_output_dir / f"{self.current_filename}.wav"
    
    def check_overwrite(self) -> bool:
        """Check if output file exists (for overwrite confirmation)."""
        return self.get_full_path().exists()

