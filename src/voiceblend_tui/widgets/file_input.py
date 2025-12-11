"""File input widget for selecting text files."""

from pathlib import Path
from textual.containers import Vertical, Horizontal
from textual.widget import Widget
from textual.widgets import Static, Button, TextArea
from textual.message import Message

from voiceblend_tui.core.file_utils import FileUtils
from voiceblend_tui.widgets.file_picker_modal import FileSelectionModal


class FileLoaded(Message):
    """Message sent when a file is successfully loaded."""
    
    def __init__(self, file_path: Path, content: str):
        super().__init__()
        self.file_path = file_path
        self.content = content


class FileInputWidget(Widget):
    """Widget for selecting and loading text files."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_file: Path | None = None
        self.file_content: str = ""
    
    def compose(self):
        """Create child widgets."""
        with Vertical():
            yield Static("📄 Input File", classes="section-title")
            with Horizontal():
                yield Static("No file selected", id="file-display")
                yield Button("📂 Browse...", id="browse-btn", variant="primary")
            yield Static("", id="file-status", classes="status-text")
            yield Static("File Content Preview:", classes="label")
            yield TextArea(
                "",
                id="file-content-preview",
                read_only=True,
                language="text"
            )
    
    def on_mount(self):
        """Called when widget is mounted."""
        self.add_class("file-input-section")
    
    def on_button_pressed(self, event: Button.Pressed):
        """Handle button press."""
        if event.button.id == "browse-btn":
            self.run_worker(self.open_file_picker())
    
    async def open_file_picker(self):
        """Open the file picker modal."""
        # Determine initial path - use current file's directory if available, else current working directory
        initial_path = Path.cwd()
        if self.selected_file:
            initial_path = self.selected_file.parent
        
        # Open modal and wait for result
        result = await self.app.push_screen_wait(FileSelectionModal(initial_path=initial_path))
        
        if result:
            # Load the file automatically
            await self.load_file_from_path(result)
    
    async def load_file_from_path(self, file_path: Path):
        """Load the file from the given path."""
        status_widget = self.query_one("#file-status", Static)
        display_widget = self.query_one("#file-display", Static)
        
        try:
            if not file_path.exists():
                status_widget.update(f"❌ File not found: {file_path}")
                status_widget.set_classes("status-text error")
                display_widget.update("No file selected")
                self.post_message(FileLoaded(Path(""), ""))
                return
            
            if not file_path.is_file():
                status_widget.update(f"❌ Path is not a file: {file_path}")
                status_widget.set_classes("status-text error")
                display_widget.update("No file selected")
                self.post_message(FileLoaded(Path(""), ""))
                return
            
            # Read the file
            self.selected_file = file_path
            self.file_content = FileUtils.read_text_file(file_path)
            
            # Update UI
            display_widget.update(str(file_path))
            status_widget.update(
                f"✅ Loaded: {file_path.name} ({len(self.file_content)} chars)"
            )
            status_widget.set_classes("status-text success")
            
            # Update file content preview
            preview_widget = self.query_one("#file-content-preview", TextArea)
            # Show first 500 characters or full content if shorter
            preview_text = self.file_content[:500]
            if len(self.file_content) > 500:
                preview_text += "\n\n... (truncated, full content will be used for generation)"
            preview_widget.text = preview_text
            
            # Notify parent
            self.post_message(FileLoaded(self.selected_file, self.file_content))
            
        except Exception as e:
            status_widget.update(f"❌ Error: {str(e)}")
            status_widget.set_classes("status-text error")
            display_widget.update("No file selected")
            self.post_message(FileLoaded(Path(""), ""))
    
    def get_file_content(self) -> str:
        """Get the loaded file content."""
        return self.file_content
    
    def has_file_loaded(self) -> bool:
        """Check if a file is loaded."""
        return self.selected_file is not None and bool(self.file_content)

