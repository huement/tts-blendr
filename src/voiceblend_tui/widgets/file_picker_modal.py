"""File picker modal screen with DirectoryTree."""

from pathlib import Path
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Button, Static


class FileSelectionModal(ModalScreen[Path | None]):
    """Modal screen for file selection using DirectoryTree.
    
    Returns Path if a file is selected, None if cancelled.
    """
    
    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]
    
    def __init__(self, initial_path: Path = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_path = initial_path or Path.cwd()
        self.selected_file: Path | None = None
    
    def compose(self):
        """Create child widgets."""
        with Vertical():
            yield Static("Select File", classes="modal-title")
            yield DirectoryTree(str(self.initial_path), id="file-tree")
            with Horizontal():
                yield Button("Cancel", id="cancel-btn", variant="default")
                yield Button("Select", id="select-btn", variant="primary")
    
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection in directory tree."""
        self.selected_file = Path(event.path)
        # Auto-select when Enter is pressed on a file
        if self.selected_file and self.selected_file.is_file():
            self.dismiss(self.selected_file)
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "cancel-btn":
            self.dismiss(None)
        elif event.button.id == "select-btn":
            self.action_select()
    
    def action_select(self) -> None:
        """Select the currently highlighted file."""
        if self.selected_file and self.selected_file.is_file():
            self.dismiss(self.selected_file)
        else:
            # Try to get the cursor node
            tree = self.query_one("#file-tree", DirectoryTree)
            try:
                if hasattr(tree, 'cursor_node') and tree.cursor_node:
                    path_str = tree.cursor_node.data.get("path", "") if hasattr(tree.cursor_node, 'data') else ""
                    if path_str:
                        path = Path(path_str)
                        if path.is_file():
                            self.dismiss(path)
                            return
            except:
                pass
            self.app.notify("Please select a file", severity="warning")
    
    def action_cancel(self) -> None:
        """Cancel file selection."""
        self.dismiss(None)

