"""File picker widget."""

from pathlib import Path
from textual.containers import Vertical
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, Button, Input
from textual import events

from voiceblend_tui.core.file_utils import FileUtils


class FileSelected(events.Message):
    """Message sent when a file is selected."""
    
    def __init__(self, file_path: Path, content: str):
        super().__init__()
        self.file_path = file_path
        self.content = content


class FilePicker(Widget):
    """Widget for selecting text files."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_file: Path | None = None
        self.file_content: str = ""

    def compose(self) -> ComposeResult:
        """Create child widgets for the file picker."""
        with Vertical():
            yield Static("Text File Picker", classes="section-title")
            yield Static("Enter text file path:", classes="label")
            yield Input(
                placeholder="Enter path to text file...",
                id="file-path-input",
            )
            yield Button("Load File", id="load-btn", variant="primary")
            yield Static("", id="selected-file-path", classes="file-path")
            yield Static("File content preview:", classes="label")
            yield Static("No file loaded", id="file-preview", classes="file-preview")

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        self.add_class("file-picker-panel")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "load-btn":
            await self.load_file()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key)."""
        if event.input.id == "file-path-input":
            await self.load_file()

    async def load_file(self) -> None:
        """Load the file from the input path."""
        input_widget = self.query_one("#file-path-input", Input)
        file_path_str = input_widget.value.strip()
        
        if not file_path_str:
            self.app.notify("Please enter a file path", severity="warning")
            return
        
        try:
            file_path = Path(file_path_str)
            if not file_path.exists():
                self.app.notify(f"File not found: {file_path}", severity="error")
                return
            
            if not file_path.is_file():
                self.app.notify(f"Path is not a file: {file_path}", severity="error")
                return
            
            # Read the file
            self.selected_file = file_path
            self.file_content = FileUtils.read_text_file(file_path)
            
            # Update UI
            self.query_one("#selected-file-path", Static).update(
                f"✓ Loaded: {file_path.name}"
            )
            
            # Show preview (first 300 chars)
            preview = self.file_content[:300].replace("\n", " ")
            if len(self.file_content) > 300:
                preview += "..."
            self.query_one("#file-preview", Static).update(preview)
            
            # Notify parent that file was selected
            self.post_message(FileSelected(self.selected_file, self.file_content))
            
            self.app.notify(f"File loaded: {file_path.name}", severity="information")
            
        except Exception as e:
            self.app.notify(f"Error reading file: {e}", severity="error")
            self.query_one("#selected-file-path", Static).update(f"✗ Error: {str(e)}")

    def get_selected_text(self) -> str:
        """Get the text content from the selected file."""
        return self.file_content

