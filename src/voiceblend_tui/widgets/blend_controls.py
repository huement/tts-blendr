"""Blend controls widget."""

from textual.containers import Vertical
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, Button, Input, Select
from textual import events

from voiceblend_tui.core.blender import VoiceBlender


class GenerateRequested(events.Message):
    """Message sent when generate button is pressed."""
    
    def __init__(self, model_a: str, model_b: str, ratio: float, output_file: str):
        super().__init__()
        self.model_a = model_a
        self.model_b = model_b
        self.ratio = ratio
        self.output_file = output_file


class BlendControls(Widget):
    """Widget for controlling voice blending parameters."""

    def __init__(self, blender: VoiceBlender = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blender = blender or VoiceBlender()
        self.available_models: list[str] = []

    def compose(self) -> ComposeResult:
        """Create child widgets for blend controls."""
        with Vertical():
            yield Static("Blend Controls", classes="section-title")
            yield Static("(Tab to navigate, Enter to select)", classes="hint")
            yield Static("")  # Spacing
            
            yield Static("Voice Model A:", classes="label")
            yield Select([], id="model-a-select", prompt="Select Voice A (Enter to open)")
            yield Static("")  # Spacing
            
            yield Static("Voice Model B:", classes="label")
            yield Select([], id="model-b-select", prompt="Select Voice B (Enter to open)")
            yield Static("")  # Spacing
            
            yield Static("Blend Ratio (0-100):", classes="label")
            yield Static("0 = all Voice A, 100 = all Voice B", classes="hint")
            yield Input(
                value="50",
                placeholder="Enter 0-100",
                id="blend-ratio",
            )
            yield Static("Current: 50%", id="blend-ratio-value", classes="value-display")
            yield Static("")  # Spacing
            
            yield Static("Output Filename:", classes="label")
            yield Input(
                value="output.wav",
                placeholder="output.wav",
                id="output-filename",
            )
            yield Static("")  # Spacing
            
            yield Button("🎵 Generate Audio", id="generate-btn", variant="success")

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        self.add_class("blend-controls-panel")
        # Load available models
        self.load_models()

    def load_models(self) -> None:
        """Load available voice models."""
        try:
            self.available_models = self.blender.list_models()
            
            if not self.available_models:
                # If no models, show a message
                self.app.notify(
                    "No voice models found. Models will download on first use.",
                    severity="information"
                )
                # Use default list for now
                self.available_models = [
                    "af_bella",
                    "af_sarah", 
                    "am_adam",
                    "am_eric",
                    "am_michael",
                    "am_onyx",
                    "bm_george",
                ]
            
            # Create options for Select widgets
            options = [(model, model) for model in self.available_models]
            
            model_a_select = self.query_one("#model-a-select", Select)
            model_b_select = self.query_one("#model-b-select", Select)
            
            model_a_select.set_options(options)
            model_b_select.set_options(options)
            
            self.app.notify(f"Loaded {len(self.available_models)} voice models", severity="information")
        except Exception as e:
            self.app.notify(f"Error loading models: {e}", severity="warning")
            # Use fallback list
            self.available_models = [
                "af_bella",
                "af_sarah",
                "am_adam", 
                "am_eric",
                "am_michael",
                "am_onyx",
                "bm_george",
            ]
            options = [(model, model) for model in self.available_models]
            try:
                model_a_select = self.query_one("#model-a-select", Select)
                model_b_select = self.query_one("#model-b-select", Select)
                model_a_select.set_options(options)
                model_b_select.set_options(options)
            except:
                pass

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input value changes."""
        if event.input.id == "blend-ratio":
            try:
                value = int(event.value) if event.value else 0
                # Clamp value between 0 and 100
                value = max(0, min(100, value))
                self.query_one("#blend-ratio-value", Static).update(f"{value}%")
            except ValueError:
                # Invalid input, keep previous value
                pass

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "generate-btn":
            await self.handle_generate()

    async def handle_generate(self) -> None:
        """Handle generate button press."""
        # Get values from inputs
        model_a_select = self.query_one("#model-a-select", Select)
        model_b_select = self.query_one("#model-b-select", Select)
        ratio_input = self.query_one("#blend-ratio", Input)
        output_input = self.query_one("#output-filename", Input)
        
        # Validate inputs
        if model_a_select.value is Select.BLANK:
            self.app.notify("Please select Model A", severity="warning")
            return
        
        if model_b_select.value is Select.BLANK:
            self.app.notify("Please select Model B", severity="warning")
            return
        
        try:
            ratio = int(ratio_input.value) if ratio_input.value else 50
            ratio = max(0, min(100, ratio))
            ratio_float = ratio / 100.0  # Convert to 0.0-1.0 range
        except ValueError:
            self.app.notify("Invalid blend ratio", severity="error")
            return
        
        output_file = output_input.value.strip() or "output.wav"
        
        model_a = str(model_a_select.value)
        model_b = str(model_b_select.value)
        
        # Send message to app to handle generation
        self.post_message(GenerateRequested(model_a, model_b, ratio_float, output_file))

