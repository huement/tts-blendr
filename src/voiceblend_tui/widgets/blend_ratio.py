"""Blend ratio widget for controlling voice blend percentages."""

from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Static, Select, Input
from textual.message import Message


class BlendRatioChanged(Message):
    """Message sent when blend ratio changes."""
    
    def __init__(self, ratio: float):
        super().__init__()
        self.ratio = ratio  # 0.0 to 1.0


class BlendRatioWidget(Widget):
    """Widget for selecting blend ratio (only shown for 2 voices)."""
    
    # Predefined ratio options
    RATIO_OPTIONS = [
        ("50/50 (Equal)", 0.5),
        ("60/40", 0.4),
        ("70/30", 0.3),
        ("80/20", 0.2),
        ("90/10", 0.1),
        ("40/60", 0.6),
        ("30/70", 0.7),
        ("20/80", 0.8),
        ("10/90", 0.9),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_ratio: float = 0.5
        self.visible: bool = False
    
    def compose(self):
        """Create child widgets."""
        with Vertical():
            yield Static("⚖️  Blend Ratio", classes="section-title")
            yield Static("Voice 1 / Voice 2", classes="hint")
            yield Select(
                [(label, value) for label, value in self.RATIO_OPTIONS],
                id="blend-ratio-select",
                prompt="Select ratio"
            )
            yield Static("", id="blend-ratio-status", classes="status-text")
    
    def on_mount(self):
        """Called when widget is mounted."""
        self.add_class("blend-ratio-section")
        self.display = False  # Hidden by default
        # Set default value
        ratio_select = self.query_one("#blend-ratio-select", Select)
        ratio_select.value = 0.5
        self.current_ratio = 0.5
    
    def show(self):
        """Show the blend ratio widget."""
        self.display = True
        self.visible = True
    
    def hide(self):
        """Hide the blend ratio widget."""
        self.display = False
        self.visible = False
    
    def on_select_changed(self, event: Select.Changed):
        """Handle ratio selection change."""
        if event.select.id == "blend-ratio-select":
            self.current_ratio = float(event.value)
            self.update_status()
            self.notify_ratio_changed()
    
    def update_status(self):
        """Update status text with current ratio."""
        status_widget = self.query_one("#blend-ratio-status", Static)
        voice1_pct = int((1.0 - self.current_ratio) * 100)
        voice2_pct = int(self.current_ratio * 100)
        status_widget.update(
            f"✅ Ratio: {voice1_pct}% / {voice2_pct}%"
        )
        status_widget.set_classes("status-text success")
    
    def notify_ratio_changed(self):
        """Notify parent of ratio change."""
        self.post_message(BlendRatioChanged(self.current_ratio))
    
    def get_ratio(self) -> float:
        """Get current blend ratio."""
        return self.current_ratio
    
    def set_default(self):
        """Set default ratio (50/50)."""
        ratio_select = self.query_one("#blend-ratio-select", Select)
        ratio_select.value = 0.5
        self.current_ratio = 0.5
        self.update_status()

