"""Voice selection widget with mode toggle (1 or 2 voices)."""

from textual.containers import Vertical, Horizontal
from textual.widget import Widget
from textual.widgets import Static, Select, RadioSet
from textual.message import Message

from voiceblend_tui.core.blender import VoiceBlender


class VoiceSelectionChanged(Message):
    """Message sent when voice selection changes."""
    
    def __init__(self, mode: int, voice1: str | None, voice2: str | None):
        super().__init__()
        self.mode = mode  # 1 or 2
        self.voice1 = voice1
        self.voice2 = voice2


class VoiceSelectionWidget(Widget):
    """Widget for selecting voice mode and voices."""
    
    def __init__(self, blender: VoiceBlender = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blender = blender or VoiceBlender()
        self.available_voices: list[str] = []
        self.mode: int = 2  # Default to 2 voices (can't blend one voice!)
        self.selected_voice1: str | None = None
        self.selected_voice2: str | None = None
    
    def compose(self):
        """Create child widgets."""
        with Vertical():
            yield Static("🎤 Voice Selection", classes="section-title")
            with Horizontal():
                yield Static("Mode:", classes="label")
                yield RadioSet(
                    "1 Voice",
                    "2 Voices",
                    id="voice-mode"
                )
            yield Static("Voice 1:", classes="label")
            yield Select([], id="voice-1-select", prompt="Select Voice 1")
            yield Static("", id="voice-status", classes="status-text")
    
    def on_mount(self):
        """Called when widget is mounted."""
        self.add_class("voice-selection-section")
        # Set initial value for RadioSet (default to 2 voices)
        radio_set = self.query_one("#voice-mode", RadioSet)
        radio_set.pressed = "2 Voices"  # Default to 2 voices
        self.mode = 2  # Ensure mode is set to 2
        self.load_voices()
        # Update visibility after a brief delay to ensure voices are loaded
        self.call_after_refresh(self.update_voice2_visibility)
    
    def load_voices(self):
        """Load available voice models."""
        try:
            self.available_voices = self.blender.list_models()
            
            if not self.available_voices:
                self.app.notify(
                    "No voice models found. Models will download on first use.",
                    severity="information"
                )
                # Use fallback list
                self.available_voices = [
                    "af_bella",
                    "af_sarah",
                    "am_adam",
                    "am_eric",
                    "am_michael",
                    "am_onyx",
                    "bm_george",
                ]
            
            # Create options for Select widgets
            options = [(voice, voice) for voice in self.available_voices]
            
            voice1_select = self.query_one("#voice-1-select", Select)
            voice1_select.set_options(options)
            
            # Update voice2 select if it already exists
            try:
                voice2_select = self.query_one("#voice-2-select", Select)
                voice2_select.set_options(options)
            except:
                pass  # Voice2 select doesn't exist yet, will be created later
            
        except Exception as e:
            self.app.notify(f"Error loading voices: {e}", severity="warning")
            self.available_voices = [
                "af_bella",
                "af_sarah",
                "am_adam",
                "am_eric",
                "am_michael",
                "am_onyx",
                "bm_george",
            ]
            options = [(voice, voice) for voice in self.available_voices]
            try:
                voice1_select = self.query_one("#voice-1-select", Select)
                voice1_select.set_options(options)
                # Update voice2 select if it exists
                try:
                    voice2_select = self.query_one("#voice-2-select", Select)
                    voice2_select.set_options(options)
                except:
                    pass
            except:
                pass
    
    def on_radio_set_changed(self, event: RadioSet.Changed):
        """Handle voice mode change."""
        if event.radio_set.id == "voice-mode":
            # Map label to mode value
            pressed_label = event.radio_set.pressed
            if pressed_label == "1 Voice":
                self.mode = 1
            elif pressed_label == "2 Voices":
                self.mode = 2
            else:
                self.mode = 1  # Default
            self.update_voice2_visibility()
            self.notify_selection_changed()
    
    def on_select_changed(self, event: Select.Changed):
        """Handle voice selection change."""
        if event.select.id == "voice-1-select":
            self.selected_voice1 = str(event.value) if event.value != Select.BLANK else None
        elif event.select.id == "voice-2-select":
            self.selected_voice2 = str(event.value) if event.value != Select.BLANK else None
        
        self.update_status()
        self.notify_selection_changed()
    
    def update_voice2_visibility(self):
        """Show or hide voice 2 selector based on mode."""
        # Try to find voice2_section
        try:
            voice2_section = self.query_one("#voice-2-section")
        except:
            voice2_section = None
        
        if self.mode == 2:
            # Show voice 2 selector
            if voice2_section is None:
                # Ensure we have voices loaded
                if not self.available_voices:
                    # Use fallback if voices aren't loaded yet
                    self.available_voices = [
                        "af_bella", "af_sarah", "am_adam", "am_eric",
                        "am_michael", "am_onyx", "bm_george",
                    ]
                
                try:
                    # Create voice 2 section with proper composition
                    from textual.containers import Vertical as VContainer
                    voice2_section = VContainer(id="voice-2-section")
                    
                    # Mount the container first
                    voice1_select = self.query_one("#voice-1-select", Select)
                    self.mount(voice2_section, after=voice1_select)
                    
                    # Add children directly (not using yield in a function)
                    voice2_label = Static("Voice 2:", classes="label")
                    options = [(voice, voice) for voice in self.available_voices]
                    voice2_select = Select(options, id="voice-2-select", prompt="Select Voice 2")
                    
                    voice2_section.mount(voice2_label)
                    voice2_section.mount(voice2_select)
                    
                    # Log that we created it (if app has message_log available)
                    try:
                        message_log = self.app.query_one("#message-log")
                        message_log.log("   ✅ Voice 2 selector widget created and mounted", "success")
                    except:
                        pass  # Message log not available yet
                except Exception as e:
                    try:
                        message_log = self.app.query_one("#message-log")
                        message_log.log(f"   ❌ Error creating voice 2 selector: {e}", "error")
                    except:
                        pass
            else:
                voice2_section.display = True
        else:
            # Hide voice 2 selector
            if voice2_section:
                voice2_section.display = False
                self.selected_voice2 = None
    
    def update_status(self):
        """Update status text."""
        status_widget = self.query_one("#voice-status", Static)
        if self.mode == 1:
            if self.selected_voice1:
                status_widget.update(f"✅ Selected: {self.selected_voice1}")
                status_widget.set_classes("status-text success")
            else:
                status_widget.update("⚠️  Please select Voice 1")
                status_widget.set_classes("status-text warning")
        else:
            if self.selected_voice1 and self.selected_voice2:
                status_widget.update(
                    f"✅ Selected: {self.selected_voice1} + {self.selected_voice2}"
                )
                status_widget.set_classes("status-text success")
            else:
                missing = []
                if not self.selected_voice1:
                    missing.append("Voice 1")
                if not self.selected_voice2:
                    missing.append("Voice 2")
                status_widget.update(f"⚠️  Please select: {', '.join(missing)}")
                status_widget.set_classes("status-text warning")
    
    def notify_selection_changed(self):
        """Notify parent of selection change."""
        self.post_message(
            VoiceSelectionChanged(self.mode, self.selected_voice1, self.selected_voice2)
        )
    
    def get_selection(self) -> tuple[int, str | None, str | None]:
        """Get current voice selection."""
        return (self.mode, self.selected_voice1, self.selected_voice2)
    
    def validate_selection(self) -> tuple[bool, str]:
        """Validate that required voices are selected."""
        if not self.selected_voice1:
            return False, "Please select Voice 1"
        if self.mode == 2 and not self.selected_voice2:
            return False, "Please select Voice 2"
        return True, ""

