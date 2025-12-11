"""Custom footer widget."""

from textual.widgets import Footer as TextualFooter


class CustomFooter(TextualFooter):
    """Custom footer widget for the application."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

