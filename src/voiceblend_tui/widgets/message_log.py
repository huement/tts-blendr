"""Message log widget for displaying operation messages."""

from datetime import datetime
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Static, RichLog


class MessageLogWidget(Widget):
    """Widget for displaying scrollable operation messages."""
    
    def compose(self):
        """Create child widgets."""
        with Vertical():
            yield Static("📋 Messages", classes="section-title")
            yield RichLog(id="message-log", wrap=True, markup=True)
    
    def on_mount(self):
        """Called when widget is mounted."""
        self.add_class("message-log-section")
        self.log("Application started. Ready to generate audio.")
    
    def log(self, message: str, level: str = "info"):
        """Add a message to the log.
        
        Args:
            message: Message text
            level: Message level (info, success, warning, error)
        """
        log_widget = self.query_one("#message-log", RichLog)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding based on level
        if level == "success":
            prefix = f"[green]✓[/green]"
        elif level == "warning":
            prefix = f"[yellow]⚠[/yellow]"
        elif level == "error":
            prefix = f"[red]✗[/red]"
        else:
            prefix = f"[blue]ℹ[/blue]"
        
        log_widget.write(f"[{timestamp}] {prefix} {message}")
    
    def clear(self):
        """Clear the message log."""
        log_widget = self.query_one("#message-log", RichLog)
        log_widget.clear()
        self.log("Log cleared.")

