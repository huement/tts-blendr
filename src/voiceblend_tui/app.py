"""Main Textual application entry point."""

from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Header, Footer, Button, Select, RadioSet, Input, Static, TextArea

from voiceblend_tui.widgets.file_input import FileInputWidget, FileLoaded
from voiceblend_tui.widgets.voice_selection import VoiceSelectionWidget, VoiceSelectionChanged
from voiceblend_tui.widgets.blend_ratio import BlendRatioWidget, BlendRatioChanged
from voiceblend_tui.widgets.output_filename import OutputFilenameWidget, OutputFilenameChanged
from voiceblend_tui.widgets.message_log import MessageLogWidget

from voiceblend_tui.core.blender import VoiceBlender
from voiceblend_tui.core.config import Config
from voiceblend_tui.core.settings import Settings
from voiceblend_tui.services.audio_service import AudioService
from voiceblend_tui.services.file_service import FileService


class VoiceBlendApp(App):
    """Main application class for Voice Blender TUI."""

    TITLE = "Voice Blender"
    CSS_PATH = None
    
    # CSS for layout sizing
    CSS = """
    /* 1. Ensure the main container fills the space between Header and Footer */
    #main-container {
        height: 1fr;
    }

    /* 2. Tell the horizontal container to fill that height */
    #top-section {
        height: 100%;
        width: 100%;
    }

    /* 3. Give more space to controls, less to log (3:1 ratio) */
    #controls-column {
        width: 3fr;
        height: 100%;
        padding: 1; /* Add some spacing so widgets aren't touching the edge */
        overflow-y: auto; /* Enable vertical scrolling */
    }
    
    /* 3a. Allow widgets in controls column to expand naturally */
    #controls-column > * {
        width: 100%;
    }

    #log-column {
        width: 1fr;
        height: 100%;
        border-left: solid $primary; /* Optional: Adds a nice divider line */
        padding: 1;
    }

    /* 4. Ensure your message log fills its column */
    MessageLogWidget {
        height: 1fr;
    }

    /* 5. Dashboard-style compact form layout - tight stacking */
    FileInputWidget, VoiceSelectionWidget, BlendRatioWidget, OutputFilenameWidget {
        height: auto;
        margin: 0 0 1 0;
        padding: 1;
        width: 100%;
        border: none !important;
    }
    
    /* 8a. Compact section titles */
    .section-title {
        margin: 0 0 1 0;
        padding: 0;
        text-style: bold;
    }
    
    /* 8b. Compact labels */
    .label {
        margin: 0 0 0 0;
        padding: 0;
    }
    
    /* 8c. File content preview - compact */
    #file-content-preview {
        height: 8;
        min-height: 8;
        margin: 1 0 0 0;
        padding: 0;
    }
    
    /* 8d. Compact Static widgets */
    Static {
        margin: 0;
        padding: 0;
    }
    
    /* 8e. Compact Select and Input widgets - ensure text is visible */
    Select {
        margin: 0;
        padding: 0 1;
        height: 3;
        min-height: 3;
    }
    
    Input {
        margin: 0;
        padding: 0 1;
        height: 3;
    }

    /* 8f. Compact RadioSet */
    RadioSet {
        margin: 0;
        padding: 0;
        height: 3;
    }
    
    /* Status text styling */
    .status-text {
        margin: 1 0 0 0;
        padding: 0;
        height: auto;
        min-height: 1;
    }
    
    /* Voice 2 section - ensure it's visible */
    #voice-2-section {
        margin: 1 0 0 0;
        padding: 0;
        height: auto;
        display: block;
    }
    
    /* 8g. Compact Horizontal containers */
    Horizontal {
        margin: 0;
        padding: 0;
        height: auto;
    }
    
    /* Vertical containers in widgets - allow natural expansion */
    VoiceSelectionWidget > Vertical,
    FileInputWidget > Vertical,
    BlendRatioWidget > Vertical,
    OutputFilenameWidget > Vertical {
        height: auto;
        margin: 0;
        padding: 0;
    }
    
    /* 8h. File display (read-only) */
    #file-display, .file-display {
        margin: 0;
        padding: 0;
        height: auto;
        min-height: 6;
        max-height: 8;
        border: solid $primary;
        background: $panel;
        text-style: none;
        overflow: hidden;
        content-align: left top;
        width: 1fr;
    }

    /* 9. Compact buttons */
    Button {
        height: 3;
        margin: 0;
        padding: 0 1;
    }
    
    /* 10. File picker modal styling */
    FilePickerModal {
        align: center middle;
    }
    
    .modal-title {
        text-style: bold;
        margin: 0 0 1 0;
    }
    
    #file-tree {
        height: 20;
        border: solid $primary;
        margin: 1 0;
    }
    """
    
    # App state
    selected_text: str = ""
    selected_file_path = None
    voice_mode: int = 2  # Default to 2 voices (can't blend one voice!)
    voice1: str | None = None
    voice2: str | None = None
    blend_ratio: float = 0.5
    output_filename: str = "output"
    is_generating: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = Config()
        self.settings = Settings()
        self.blender = VoiceBlender(self.config.config.voices_path)
        self.audio_service = AudioService(self.blender)
        self.file_service = FileService(self.config.config.save_path)
        
        # Load saved settings
        self.voice_mode = self.settings.get_int("voice_mode", 2)
        self.voice1 = self.settings.get("voice1") or None
        self.voice2 = self.settings.get("voice2") or None
        self.blend_ratio = self.settings.get_float("blend_ratio", 0.5)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        
        with Container(id="main-container"):
            with Horizontal(id="top-section"):
                # Left column: Input controls
                with Vertical(id="controls-column"):
                    yield FileInputWidget(id="file-input")
                    yield VoiceSelectionWidget(blender=self.blender, id="voice-selection")
                    yield BlendRatioWidget(id="blend-ratio")
                    yield OutputFilenameWidget(
                        default_output_dir=self.config.config.save_path,
                        id="output-filename"
                    )
                    yield Button("🎵 Generate Audio", id="generate-btn", variant="success")
                
                # Right column: Message log
                with Vertical(id="log-column"):
                    yield MessageLogWidget(id="message-log")
        
        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts."""
        self.update_footer("Ready")
        self.message_log = self.query_one("#message-log", MessageLogWidget)
        self.message_log.log("Application initialized. Load a text file to begin.")
        
        # Log loaded settings
        self.message_log.log("📋 Loading saved settings from .env...", "info")
        self.message_log.log(f"   Voice mode: {self.voice_mode}", "info")
        self.message_log.log(f"   Voice 1: {self.voice1 or 'None'}", "info")
        self.message_log.log(f"   Voice 2: {self.voice2 or 'None'}", "info")
        self.message_log.log(f"   Blend ratio: {self.blend_ratio}", "info")
        
        # Apply saved settings to widgets - wait for widgets to be ready
        self.call_after_refresh(self._apply_saved_settings)

    def update_footer(self, message: str):
        """Update footer status message."""
        self.sub_title = message

    # File input handlers
    def on_file_loaded(self, event: FileLoaded) -> None:
        """Handle file loaded event."""
        if event.file_path and event.content:
            self.selected_text = event.content
            self.selected_file_path = event.file_path
            self.message_log.log(f"Loaded text file: {event.file_path.name}", "success")
            self.message_log.log(f"Text length: {len(event.content)} characters", "info")
            # Update output filename based on input file
            self._update_smart_output_filename()
        else:
            # File was cleared or loading failed
            self.selected_text = ""
            self.selected_file_path = None
            if not event.file_path:
                self.message_log.log("File selection cleared", "info")
            else:
                self.message_log.log("File loading failed", "error")

    # Voice selection handlers
    def on_voice_selection_changed(self, event: VoiceSelectionChanged) -> None:
        """Handle voice selection change."""
        self.voice_mode = event.mode
        self.voice1 = event.voice1
        self.voice2 = event.voice2
        
        # Save to settings
        self.settings.set("voice_mode", str(self.voice_mode))
        if self.voice1:
            self.settings.set("voice1", self.voice1)
        if self.voice2:
            self.settings.set("voice2", self.voice2)
        
        # Show/hide blend ratio widget
        blend_ratio_widget = self.query_one("#blend-ratio", BlendRatioWidget)
        if event.mode == 2:
            blend_ratio_widget.show()
            if self.voice1 and self.voice2:
                self.message_log.log(
                    f"Selected voices: {self.voice1} + {self.voice2}",
                    "success"
                )
        else:
            blend_ratio_widget.hide()
            if self.voice1:
                self.message_log.log(f"Selected voice: {self.voice1}", "success")
        
        # Update output filename based on voices
        self._update_smart_output_filename()

    # Blend ratio handlers
    def on_blend_ratio_changed(self, event: BlendRatioChanged) -> None:
        """Handle blend ratio change."""
        self.blend_ratio = event.ratio
        self.settings.set("blend_ratio", str(self.blend_ratio))
        voice1_pct = int((1.0 - event.ratio) * 100)
        voice2_pct = int(event.ratio * 100)
        self.message_log.log(
            f"Blend ratio set: {voice1_pct}% / {voice2_pct}%",
            "info"
        )
        # Update output filename
        self._update_smart_output_filename()

    # Output filename handlers
    def on_output_filename_changed(self, event: OutputFilenameChanged) -> None:
        """Handle output filename change."""
        self.output_filename = event.filename
        if event.is_valid:
            output_path = self.file_service.get_output_path(event.filename)
            if output_path.exists():
                self.message_log.log(
                    f"Output file exists: {output_path.name} (will be overwritten)",
                    "warning"
                )
            else:
                self.message_log.log(f"Output file: {output_path.name}", "info")
    
    def _update_smart_output_filename(self) -> None:
        """Generate smart output filename based on input file and voices."""
        if not hasattr(self, 'selected_file_path') or not self.selected_file_path:
            return
        
        # Get base name from input file (without extension)
        base_name = self.selected_file_path.stem
        
        # Build filename with voices
        if self.voice_mode == 2 and self.voice1 and self.voice2:
            # Format: inputfile_voice1_voice2_ratio.wav
            ratio_pct = int(self.blend_ratio * 100)
            filename = f"{base_name}_{self.voice1}_{self.voice2}_{ratio_pct}"
        elif self.voice1:
            # Format: inputfile_voice1.wav
            filename = f"{base_name}_{self.voice1}"
        else:
            # Fallback
            filename = base_name
        
        # Update output filename widget
        try:
            output_widget = self.query_one("#output-filename", OutputFilenameWidget)
            try:
                input_widget = output_widget.query_one("#output-filename-input")
                input_widget.value = filename
                # Manually trigger update by calling the handler directly
                output_widget.current_filename = filename
                output_widget.validate_filename()
                output_widget.update_status()
                output_widget.notify_filename_changed()
            except:
                pass  # Widget not ready yet
        except:
            pass  # Widget not found
    
    def _apply_saved_settings(self) -> None:
        """Apply saved settings to widgets after mount."""
        self.message_log.log("🔧 Applying saved settings to widgets...", "info")
        
        # Store original voice2 value to prevent it from being overwritten
        original_voice2 = self.voice2
        
        # Apply voice selection settings
        try:
            voice_widget = self.query_one("#voice-selection", VoiceSelectionWidget)
            self.message_log.log("   ✅ Voice selection widget found", "info")
        except Exception as e:
            self.message_log.log(f"   ❌ Error finding voice widget: {e}", "error")
            return
        
        # Wait for voices to be loaded first
        if not voice_widget.available_voices:
            self.message_log.log("   ⏳ Waiting for voices to load...", "info")
            self.call_after_refresh(self._apply_saved_settings)
            return
        
        self.message_log.log(f"   ✅ Voices loaded ({len(voice_widget.available_voices)} available)", "info")
        
        # Set voice mode
        if self.voice_mode == 2:
            self.message_log.log("   Setting voice mode to 2 voices...", "info")
            try:
                radio_set = voice_widget.query_one("#voice-mode", RadioSet)
                radio_set.pressed = "2 Voices"
                voice_widget.mode = 2
                self.message_log.log("   ✅ Voice mode set to 2", "success")
                
                # Show blend ratio widget since mode is 2
                try:
                    blend_ratio_widget = self.query_one("#blend-ratio", BlendRatioWidget)
                    blend_ratio_widget.show()
                    # Force a refresh to ensure widget is visible
                    self.call_after_refresh(lambda: None)
                    self.message_log.log("   ✅ Blend ratio widget shown", "info")
                except Exception as e:
                    self.message_log.log(f"   ⚠️  Could not show blend ratio widget: {e}", "warning")
                
                # Update voice2 visibility - this creates the widget
                self.message_log.log("   Creating voice 2 selector...", "info")
                voice_widget.update_voice2_visibility()
                self.message_log.log("   ✅ Voice 2 visibility updated", "success")
            except Exception as e:
                self.message_log.log(f"   ❌ Error setting voice mode: {e}", "error")
        
        # Set voice1 - but don't trigger notification yet to avoid overwriting voice2
        if self.voice1:
            self.message_log.log(f"   Setting voice 1 to: {self.voice1}", "info")
            try:
                voice1_select = voice_widget.query_one("#voice-1-select", Select)
                voice1_select.value = self.voice1
                voice_widget.selected_voice1 = self.voice1
                voice_widget.update_status()
                self.message_log.log(f"   ✅ Voice 1 set to: {self.voice1}", "success")
                # Don't trigger notification here - wait until voice2 is also set
            except Exception as e:
                self.message_log.log(f"   ❌ Error setting voice 1: {e}", "error")
        
        # Set voice2 - wait for widget to be fully ready
        if original_voice2 and self.voice_mode == 2:
            self.message_log.log(f"   Scheduling voice 2 setting to: {original_voice2}", "info")
            # Restore voice2 value in case it was overwritten
            self.voice2 = original_voice2
            # Give it multiple refresh cycles to ensure widget is ready
            self.call_after_refresh(lambda: self._set_voice2_value(original_voice2, attempt=1))
        elif original_voice2:
            self.message_log.log(f"   ⚠️  Voice 2 value loaded ({original_voice2}) but mode is not 2", "warning")
        
        # Apply blend ratio - wait for widget to be ready if mode is 2
        if self.voice_mode == 2:
            # Always try to set blend ratio if mode is 2 (even if it's 0.5, to ensure it's set)
            self.message_log.log(f"   Scheduling blend ratio setting to: {self.blend_ratio}", "info")
            # Wait for blend ratio widget to be visible and ready - give it extra time
            self.call_after_refresh(lambda: self.call_after_refresh(lambda: self._set_blend_ratio_value(self.blend_ratio, attempt=1)))
        elif self.blend_ratio != 0.5:
            self.message_log.log(f"   ⚠️  Blend ratio loaded ({self.blend_ratio}) but mode is not 2", "warning")
    
    def _set_blend_ratio_value(self, ratio_value: float, attempt: int = 1, max_attempts: int = 10) -> None:
        """Set blend ratio value after widget is ready."""
        if attempt > max_attempts:
            self.message_log.log(f"   ❌ Failed to set blend ratio after {max_attempts} attempts", "error")
            return
        
        self.message_log.log(f"   Attempt {attempt}/{max_attempts}: Trying to set blend ratio to: {ratio_value}", "info")
        
        try:
            blend_widget = self.query_one("#blend-ratio", BlendRatioWidget)
            
            # Check if widget is visible
            if not blend_widget.visible or not blend_widget.display:
                self.message_log.log(f"   ⚠️  Blend ratio widget not visible, retrying...", "warning")
                self.call_after_refresh(lambda: self._set_blend_ratio_value(ratio_value, attempt=attempt + 1))
                return
            
            # Check if widget is attached
            if not blend_widget.is_attached:
                self.message_log.log(f"   ⚠️  Blend ratio widget not attached, retrying...", "warning")
                self.call_after_refresh(lambda: self._set_blend_ratio_value(ratio_value, attempt=attempt + 1))
                return
            
            try:
                ratio_select = blend_widget.query_one("#blend-ratio-select", Select)
                
                if not ratio_select.is_attached:
                    self.message_log.log(f"   ⚠️  Blend ratio select not attached, retrying...", "warning")
                    self.call_after_refresh(lambda: self._set_blend_ratio_value(ratio_value, attempt=attempt + 1))
                    return
                
                self.message_log.log(f"   ✅ Blend ratio select widget found and ready", "info")
                
                # Find the closest matching option (Select widget only accepts predefined values)
                # Round to nearest 0.1 to match available options
                rounded_ratio = round(ratio_value, 1)
                # Clamp to valid range [0.1, 0.9]
                rounded_ratio = max(0.1, min(0.9, rounded_ratio))
                
                # Check if this value exists in the options
                available_values = [value for _, value in BlendRatioWidget.RATIO_OPTIONS]
                if rounded_ratio not in available_values:
                    # Find closest available value
                    rounded_ratio = min(available_values, key=lambda x: abs(x - ratio_value))
                    self.message_log.log(f"   ⚠️  Ratio {ratio_value} rounded to nearest option: {rounded_ratio}", "warning")
                
                self.message_log.log(f"   Setting ratio_select.value to: {rounded_ratio}", "info")
                
                # Set the value - Select widget accepts the value directly (the second element of the tuple)
                # Try multiple methods to ensure it works
                success = False
                try:
                    # Method 1: Set the value directly (float)
                    ratio_select.value = rounded_ratio
                    # Verify it was set
                    if ratio_select.value == rounded_ratio:
                        success = True
                        self.message_log.log(f"   ✅ ratio_select.value set successfully to {rounded_ratio}", "info")
                    else:
                        self.message_log.log(f"   ⚠️  Value set but doesn't match: got {ratio_select.value}, expected {rounded_ratio}", "warning")
                except Exception as e:
                    self.message_log.log(f"   ⚠️  Method 1 failed: {e}, trying alternative...", "warning")
                
                if not success:
                    # Method 2: Find the option tuple and set it
                    try:
                        for label, value in BlendRatioWidget.RATIO_OPTIONS:
                            if value == rounded_ratio:
                                # Try setting with the tuple
                                ratio_select.value = (label, rounded_ratio)
                                if ratio_select.value == rounded_ratio:
                                    success = True
                                    self.message_log.log(f"   ✅ Set ratio via tuple: ({label}, {rounded_ratio})", "info")
                                    break
                    except Exception as e2:
                        self.message_log.log(f"   ⚠️  Method 2 failed: {e2}, trying index...", "warning")
                
                if not success:
                    # Method 3: Set by finding the index
                    try:
                        for idx, (label, value) in enumerate(BlendRatioWidget.RATIO_OPTIONS):
                            if value == rounded_ratio:
                                # Get options from the select widget
                                options = list(ratio_select.options) if hasattr(ratio_select, 'options') else []
                                if options and idx < len(options):
                                    ratio_select.value = options[idx][1]  # Set by value from options
                                    if ratio_select.value == rounded_ratio:
                                        success = True
                                        self.message_log.log(f"   ✅ Set ratio via option index {idx}", "info")
                                        break
                    except Exception as e3:
                        self.message_log.log(f"   ⚠️  Method 3 failed: {e3}", "error")
                
                if not success:
                    # Last resort: just update the widget state manually and trigger change
                    self.message_log.log(f"   ⚠️  All methods failed, setting state manually to {rounded_ratio}", "warning")
                    blend_widget.current_ratio = rounded_ratio
                    self.blend_ratio = rounded_ratio
                    blend_widget.update_status()
                    # Try to trigger the change event manually
                    try:
                        blend_widget.notify_ratio_changed()
                    except:
                        pass
                    return
                
                blend_widget.current_ratio = rounded_ratio
                # Update app state
                self.blend_ratio = rounded_ratio
                blend_widget.update_status()
                self.message_log.log(f"   ✅ Blend ratio successfully set to: {rounded_ratio}", "success")
                
                # Trigger notification to update app state
                blend_widget.notify_ratio_changed()
                self.message_log.log("   ✅ Blend ratio change notification sent", "success")
                
            except Exception as e:
                self.message_log.log(f"   ❌ Error accessing/setting blend ratio select: {e}, retrying...", "error")
                self.call_after_refresh(lambda: self._set_blend_ratio_value(ratio_value, attempt=attempt + 1))
                
        except Exception as e:
            self.message_log.log(f"   ❌ Unexpected error in _set_blend_ratio_value: {e}, retrying...", "error")
            self.call_after_refresh(lambda: self._set_blend_ratio_value(ratio_value, attempt=attempt + 1))
    
    def _set_voice2_value(self, voice2_value: str, attempt: int = 1, max_attempts: int = 10) -> None:
        """Set voice 2 value after widget is created."""
        if not voice2_value:
            self.message_log.log("   ⚠️  No voice2 value to set", "warning")
            return
        
        if attempt > max_attempts:
            self.message_log.log(f"   ❌ Failed to set voice 2 after {max_attempts} attempts", "error")
            return
        
        self.message_log.log(f"   Attempt {attempt}/{max_attempts}: Trying to set voice 2 to: {voice2_value}", "info")
        
        # Ensure voice2 is set in app state
        self.voice2 = voice2_value
        
        try:
            voice_widget = self.query_one("#voice-selection", VoiceSelectionWidget)
            
            # Check if voice2 section exists
            try:
                voice2_section = voice_widget.query_one("#voice-2-section")
                self.message_log.log(f"   ✅ Voice 2 section found", "info")
            except Exception as e:
                self.message_log.log(f"   ⚠️  Voice 2 section not found: {e}, retrying...", "warning")
                self.call_after_refresh(lambda: self._set_voice2_value(voice2_value, attempt=attempt + 1))
                return
            
            # Check if voice2_select exists and is ready
            try:
                voice2_select = voice_widget.query_one("#voice-2-select", Select)
                # Check if widget is mounted and ready
                if not voice2_select.is_attached:
                    self.message_log.log(f"   ⚠️  Voice 2 select not attached, retrying...", "warning")
                    self.call_after_refresh(lambda: self._set_voice2_value(voice2_value, attempt=attempt + 1))
                    return
                
                self.message_log.log(f"   ✅ Voice 2 select widget found and attached", "info")
                
                # Ensure options are loaded by checking if we can access the widget
                # If options aren't loaded yet, ensure they get set
                if not voice_widget.available_voices:
                    self.message_log.log(f"   ⚠️  Voices not loaded yet, retrying...", "warning")
                    self.call_after_refresh(lambda: self._set_voice2_value(voice2_value, attempt=attempt + 1))
                    return
                
                # Make sure options are set on the select widget
                try:
                    # Try to set options if they might not be set
                    options = [(voice, voice) for voice in voice_widget.available_voices]
                    voice2_select.set_options(options)
                except:
                    pass  # Options might already be set
                
                self.message_log.log(f"   ✅ Voice 2 select widget ready, setting value to: {voice2_value}", "info")
                
                # Try to set the value - this might fail if the widget isn't fully initialized
                voice2_select.value = voice2_value
                voice_widget.selected_voice2 = voice2_value
                voice_widget.update_status()
                self.message_log.log(f"   ✅ Voice 2 successfully set to: {voice2_value}", "success")
                
                # Manually trigger notification to update app state (this will update both voice1 and voice2)
                voice_widget.notify_selection_changed()
                self.message_log.log("   ✅ Voice selection change notification sent", "success")
                
            except Exception as e:
                self.message_log.log(f"   ❌ Error accessing/setting voice 2 select: {e}, retrying...", "error")
                self.call_after_refresh(lambda: self._set_voice2_value(voice2_value, attempt=attempt + 1))
                
        except Exception as e:
            self.message_log.log(f"   ❌ Unexpected error in _set_voice2_value: {e}, retrying...", "error")
            self.call_after_refresh(lambda: self._set_voice2_value(voice2_value, attempt=attempt + 1))

    # Generate button handler
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "generate-btn":
            await self.handle_generate()

    async def handle_generate(self) -> None:
        """Handle generate button press."""
        # Validate inputs
        if not self.selected_text:
            self.app.notify("Please load a text file first", severity="warning")
            self.message_log.log("Generation failed: No text file loaded", "error")
            return
        
        voice_selection = self.query_one("#voice-selection", VoiceSelectionWidget)
        is_valid, error_msg = voice_selection.validate_selection()
        if not is_valid:
            self.app.notify(error_msg, severity="warning")
            self.message_log.log(f"Generation failed: {error_msg}", "error")
            return
        
        output_widget = self.query_one("#output-filename", OutputFilenameWidget)
        if not output_widget.is_valid:
            self.app.notify("Invalid output filename", severity="warning")
            self.message_log.log("Generation failed: Invalid output filename", "error")
            return
        
        # Check for overwrite
        output_path = output_widget.get_full_path()
        if output_path.exists():
            # For now, just log a warning. Full confirmation dialog can be added later.
            self.message_log.log(
                f"Warning: {output_path.name} exists and will be overwritten",
                "warning"
            )
        
        # Disable only the generate button - let users change settings during generation
        # This avoids complex re-enabling logic
        self.is_generating = True
        self.update_footer("Generating audio... Please wait.")
        try:
            generate_btn = self.query_one("#generate-btn", Button)
            generate_btn.disabled = True
        except:
            pass
        
        # Build detailed notification message
        output_filename = output_path.name
        if self.voice_mode == 2 and self.voice1 and self.voice2:
            voice1_pct = int((1.0 - self.blend_ratio) * 100)
            voice2_pct = int(self.blend_ratio * 100)
            details = (
                f"🎵 Generating: {output_filename}\n"
                f"Voices: {self.voice1} ({voice1_pct}%) + {self.voice2} ({voice2_pct}%)\n"
                f"Text: {len(self.selected_text)} chars"
            )
        elif self.voice1:
            details = (
                f"🎵 Generating: {output_filename}\n"
                f"Voice: {self.voice1}\n"
                f"Text: {len(self.selected_text)} chars"
            )
        else:
            details = f"🎵 Generating: {output_filename}"
        
        # Show flash notification with details
        self.notify(
            details,
            severity="information",
            timeout=8.0,
        )
        
        self.message_log.log("Starting audio generation...", "info")
        self.message_log.log(f"Output: {output_filename}", "info")
        if self.voice_mode == 2 and self.voice1 and self.voice2:
            voice1_pct = int((1.0 - self.blend_ratio) * 100)
            voice2_pct = int(self.blend_ratio * 100)
            self.message_log.log(
                f"Voices: {self.voice1} ({voice1_pct}%) + {self.voice2} ({voice2_pct}%)",
                "info"
            )
        elif self.voice1:
            self.message_log.log(f"Voice: {self.voice1}", "info")
        
        # Run generation in worker thread
        # Capture arguments in a lambda since run_worker doesn't accept kwargs
        self.run_worker(
            lambda: self._generate_worker(
                self.selected_text,
                self.voice_mode,
                self.voice1,
                self.voice2,
                self.blend_ratio,
                str(output_path),
            ),
            thread=True,
            name="audio_generator",
        )

    def _generate_worker(
        self,
        text: str,
        voice_mode: int,
        voice1: str,
        voice2: str | None,
        ratio: float,
        output_path: str,
    ) -> str:
        """
        Worker function to run audio generation in background thread.
        
        This runs in a separate thread to keep the TUI responsive.
        """
        try:
            result = self.audio_service.generate_audio(
                text=text,
                voice_mode=voice_mode,
                voice1=voice1,
                output_path=output_path,
                voice2=voice2,
                ratio=ratio,
            )
            return result
        except Exception as e:
            raise RuntimeError(f"Generation failed: {e}") from e

    def on_worker_state_changed(self, event) -> None:
        """Handle worker state changes."""
        # Log worker state changes for debugging
        try:
            worker_name = getattr(event.worker, 'name', 'unknown')
            worker_state = getattr(event.worker, 'state', 'unknown')
            self.message_log.log(f"Worker state changed: {worker_name} -> {worker_state}", "info")
        except Exception as e:
            try:
                self.message_log.log(f"Error logging worker state: {e}", "error")
            except:
                pass
        
        worker_name = getattr(event.worker, 'name', None)
        if worker_name == "audio_generator":
            worker_state = getattr(event.worker, 'state', None)
            if worker_state == "success":
                self.message_log.log("Generation worker completed successfully, re-enabling UI...", "info")
                result = getattr(event.worker, 'result', None)
                output_path = Path(result) if result else None
                
                # Update footer immediately
                if output_path and output_path.exists():
                    self.update_footer(f"✅ Complete! Saved: {output_path.name}")
                    completion_msg = (
                        f"✅ Generation Complete!\n"
                        f"File: {output_path.name}\n"
                        f"Location: {output_path.parent}"
                    )
                else:
                    self.update_footer("✅ Generation Complete!")
                    completion_msg = "✅ Audio generation complete!"
                
                self.message_log.log("Audio generation completed successfully!", "success")
                if result:
                    self.message_log.log(f"Output: {result}", "info")
                
                # Show flash notification
                self.notify(
                    completion_msg,
                    severity="success",
                    timeout=8.0,
                )
                
                # Reset UI state (but keep voices/ratio) - use call_after_refresh to ensure it happens
                self.call_after_refresh(lambda: self._reset_ui_after_generation())
                # Also force enable as backup
                self.call_after_refresh(lambda: self._force_enable_ui())
                self.message_log.log("UI re-enable scheduled", "info")
                
            elif worker_state == "error":
                error = getattr(event.worker, 'error', None)
                error_msg = str(error) if error else "Unknown error"
                self.message_log.log(f"Generation failed: {error_msg}", "error")
                self.message_log.log("Re-enabling UI after error...", "info")
                self.update_footer("Ready - Generation failed")
                self.notify(
                    f"❌ Generation Failed\n{error_msg}",
                    severity="error",
                    timeout=8.0,
                )
                
                # Re-enable UI on error - use call_after_refresh
                self.is_generating = False
                self.call_after_refresh(lambda: self._force_enable_ui())
                self.message_log.log("UI re-enable scheduled after error", "info")
                try:
                    generate_btn = self.query_one("#generate-btn", Button)
                    generate_btn.disabled = False
                except:
                    pass
                
                try:
                    file_input = self.query_one("#file-input", FileInputWidget)
                    # Re-enable buttons
                    try:
                        browse_btn = file_input.query_one("#browse-btn", Button)
                        browse_btn.disabled = False
                    except:
                        pass
                    try:
                        reload_btn = file_input.query_one("#reload-btn", Button)
                        reload_btn.disabled = False
                    except:
                        pass
                    try:
                        clear_btn = file_input.query_one("#clear-btn", Button)
                        clear_btn.disabled = False
                    except:
                        pass
                except:
                    pass
                
                try:
                    voice_selection = self.query_one("#voice-selection", VoiceSelectionWidget)
                    # Re-enable child widgets
                    try:
                        voice1_select = voice_selection.query_one("#voice-1-select", Select)
                        voice1_select.disabled = False
                    except:
                        pass
                    try:
                        voice2_select = voice_selection.query_one("#voice-2-select", Select)
                        voice2_select.disabled = False
                    except:
                        pass
                    try:
                        radio_set = voice_selection.query_one("#voice-mode", RadioSet)
                        radio_set.disabled = False
                    except:
                        pass
                except:
                    pass
                
                try:
                    output_widget = self.query_one("#output-filename", OutputFilenameWidget)
                    try:
                        output_input = output_widget.query_one("#output-filename-input", Input)
                        output_input.disabled = False
                    except:
                        pass
                except:
                    pass
                
                try:
                    blend_ratio_widget = self.query_one("#blend-ratio", BlendRatioWidget)
                    try:
                        ratio_select = blend_ratio_widget.query_one("#blend-ratio-select", Select)
                        ratio_select.disabled = False
                    except:
                        pass
                except:
                    pass
            else:
                return
    
    def _reset_ui_after_generation(self) -> None:
        """Reset UI state after successful generation (keep voices/ratio)."""
        # Reset generation state
        self.is_generating = False
        
        # Reset footer
        self.update_footer("Ready")
        
        # Re-enable generate button (only thing we disabled)
        try:
            generate_btn = self.query_one("#generate-btn", Button)
            generate_btn.disabled = False
        except:
            pass
        
        # Clear file input (reset script)
        self.selected_text = ""
        self.selected_file_path = None
        
        try:
            file_input = self.query_one("#file-input", FileInputWidget)
            file_input.selected_file = None
            file_input.file_content = ""
            
            # Reset file input widget display
            display_widget = file_input.query_one("#file-display", Static)
            display_widget.update("No file selected")
            
            # Clear file preview
            preview_widget = file_input.query_one("#file-content-preview", TextArea)
            preview_widget.text = ""
            
            # Clear status
            status_widget = file_input.query_one("#file-status", Static)
            status_widget.update("")
            status_widget.set_classes("status-text")
        except:
            pass
        
        # Reset output filename to default (but keep it enabled)
        # The smart filename will update when a new file is loaded
        try:
            output_widget = self.query_one("#output-filename", OutputFilenameWidget)
            output_input = output_widget.query_one("#output-filename-input", Input)
            output_input.value = "output"
            output_widget.current_filename = "output"
            output_widget.validate_filename()
            output_widget.update_status()
        except:
            # If widget not ready, just set the internal state
            try:
                output_widget = self.query_one("#output-filename", OutputFilenameWidget)
                output_widget.current_filename = "output"
                output_widget.validate_filename()
            except:
                pass
        
        # Log reset
        self.message_log.log("UI reset - ready for next generation", "info")
    
    def _force_enable_ui(self) -> None:
        """Force enable generate button - used as fallback if normal reset fails."""
        self.is_generating = False
        
        # Re-enable generate button (only thing we disable)
        try:
            generate_btn = self.query_one("#generate-btn", Button)
            generate_btn.disabled = False
        except:
            pass
