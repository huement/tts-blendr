"""Custom header widget."""

from textual.widgets import Header as TextualHeader


class CustomHeader(TextualHeader):
    """Custom header widget for the application."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_clock = True

