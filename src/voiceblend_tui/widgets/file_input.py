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
                yield Button("🔄 Reload", id="reload-btn", variant="default")
                yield Button("✖ Clear", id="clear-btn", variant="default")
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
        # Initially hide reload and clear buttons
        self.update_button_visibility()
    
    def update_button_visibility(self):
        """Update visibility of reload and clear buttons based on file state."""
        try:
            reload_btn = self.query_one("#reload-btn", Button)
            clear_btn = self.query_one("#clear-btn", Button)
            has_file = self.selected_file is not None and bool(self.file_content)
            reload_btn.display = has_file
            clear_btn.display = has_file
        except:
            pass  # Buttons might not be mounted yet
    
    def on_button_pressed(self, event: Button.Pressed):
        """Handle button press."""
        # Check if widget is disabled
        if self.disabled:
            try:
                message_log = self.app.query_one("#message-log")
                message_log.log("File input is disabled (generation in progress)", "warning")
            except:
                pass
            return
        
        if event.button.id == "browse-btn":
            # Log that button was pressed
            try:
                message_log = self.app.query_one("#message-log")
                message_log.log("Browse button pressed, opening file picker...", "info")
            except:
                pass
            self.run_worker(self.open_file_picker(), exclusive=False)
        elif event.button.id == "reload-btn":
            if self.selected_file:
                try:
                    message_log = self.app.query_one("#message-log")
                    message_log.log("Reload button pressed...", "info")
                except:
                    pass
                self.run_worker(self.reload_current_file(), exclusive=False)
            else:
                try:
                    message_log = self.app.query_one("#message-log")
                    message_log.log("No file to reload", "warning")
                except:
                    pass
        elif event.button.id == "clear-btn":
            try:
                message_log = self.app.query_one("#message-log")
                message_log.log("Clear button pressed...", "info")
            except:
                pass
            self.clear_file()
    
    async def reload_current_file(self):
        """Reload the currently selected file."""
        if self.selected_file:
            await self.load_file_from_path(self.selected_file)
    
    async def open_file_picker(self):
        """Open the file picker modal."""
        try:
            # Log that we're opening the picker
            try:
                message_log = self.app.query_one("#message-log")
                message_log.log("Opening file picker...", "info")
            except:
                pass
            
            # Determine initial path - use current file's directory if available, else current working directory
            initial_path = Path.cwd()
            if self.selected_file and self.selected_file.exists():
                initial_path = self.selected_file.parent
            
            try:
                message_log = self.app.query_one("#message-log")
                message_log.log(f"File picker starting at: {initial_path}", "info")
            except:
                pass
            
            # Create and show the modal
            modal = FileSelectionModal(initial_path=initial_path)
            
            # Open modal and wait for result
            result = await self.app.push_screen_wait(modal)
            
            try:
                message_log = self.app.query_one("#message-log")
                if result:
                    message_log.log(f"File selected: {result}", "success")
                else:
                    message_log.log("File selection cancelled", "info")
            except:
                pass
            
            if result:
                # Load the file automatically
                await self.load_file_from_path(result)
                # Update button visibility after loading
                self.update_button_visibility()
        except Exception as e:
            # Log error if modal fails
            try:
                message_log = self.app.query_one("#message-log")
                message_log.log(f"Error opening file picker: {e}", "error")
                import traceback
                message_log.log(f"Traceback: {traceback.format_exc()}", "error")
            except:
                pass
    
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
            
            # Update UI - wrap long file paths to fit multiple lines
            file_path_str = str(file_path)
            # Estimate width - use textwrap to intelligently wrap at word/path boundaries
            # Account for padding and border - roughly 60-70 chars per line
            max_width = 60
            if len(file_path_str) > max_width:
                # Use textwrap to break the path intelligently
                # First try to break at path separators, then at max width
                wrapped_lines = []
                remaining = file_path_str
                lines_needed = 0
                max_lines = 6  # Don't wrap more than 6 lines
                
                while len(remaining) > max_width and lines_needed < max_lines - 1:
                    # Try to break at a path separator first
                    break_point = remaining.rfind('/', 0, max_width)
                    if break_point == -1:
                        break_point = remaining.rfind('\\', 0, max_width)
                    if break_point == -1:
                        # Just break at max_width if no separator found
                        break_point = max_width
                    wrapped_lines.append(remaining[:break_point + 1])
                    remaining = remaining[break_point + 1:].lstrip('/\\')
                    lines_needed += 1
                
                if remaining:
                    wrapped_lines.append(remaining)
                
                file_path_str = '\n'.join(wrapped_lines)
            
            display_widget.update(file_path_str)
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
            
            # Update button visibility
            self.update_button_visibility()
            
        except Exception as e:
            status_widget.update(f"❌ Error: {str(e)}")
            status_widget.set_classes("status-text error")
            display_widget.update("No file selected")
            self.selected_file = None
            self.file_content = ""
            self.post_message(FileLoaded(Path(""), ""))
            self.update_button_visibility()
    
    def clear_file(self):
        """Clear the selected file and reset the UI."""
        self.selected_file = None
        self.file_content = ""
        
        try:
            # Update UI
            display_widget = self.query_one("#file-display", Static)
            status_widget = self.query_one("#file-status", Static)
            preview_widget = self.query_one("#file-content-preview", TextArea)
            
            display_widget.update("No file selected")
            status_widget.update("")
            status_widget.set_classes("status-text")
            preview_widget.text = ""
            
            # Update button visibility
            self.update_button_visibility()
            
            # Notify parent with empty path and content
            self.post_message(FileLoaded(Path(""), ""))
        except Exception as e:
            # If widgets aren't ready, just clear the state
            # The UI will update on next refresh
            pass
    
    def get_file_content(self) -> str:
        """Get the loaded file content."""
        return self.file_content
    
    def has_file_loaded(self) -> bool:
        """Check if a file is loaded."""
        return self.selected_file is not None and bool(self.file_content)

