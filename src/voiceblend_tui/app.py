"""Main Textual application entry point."""

from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Header, Footer, Button, Select, RadioSet, Input

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
        padding: 0 1;
        width: 100%;
        border-bottom: solid $secondary;
    }
    
    /* 8a. Compact section titles */
    .section-title {
        margin: 0;
        padding: 0 0 1 0;
        text-style: bold;
    }
    
    /* 8b. Compact labels */
    .label {
        margin: 0;
        padding: 0 0 1 0;
    }
    
    /* 8c. File content preview - compact */
    #file-content-preview {
        height: 4;
        margin: 0;
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
        height: auto;
        min-height: 4;
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
        height: auto;
    }
    
    /* 8g. Compact Horizontal containers */
    Horizontal {
        margin: 0;
        padding: 0;
        height: auto;
    }
    
    /* 8h. File display (read-only) */
    #file-display {
        margin: 0;
        padding: 0 1;
        height: 3;
        border: solid $primary;
        background: $panel;
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
        
        # Apply saved settings to widgets
        self._apply_saved_settings()

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
            self.selected_text = ""
            self.selected_file_path = None
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
        # Apply voice selection settings
        voice_widget = self.query_one("#voice-selection", VoiceSelectionWidget)
        if self.voice_mode == 2:
            radio_set = voice_widget.query_one("#voice-mode", RadioSet)
            radio_set.pressed = "2 Voices"
            voice_widget.mode = 2
            voice_widget.update_voice2_visibility()
        
        if self.voice1:
            voice1_select = voice_widget.query_one("#voice-1-select", Select)
            try:
                voice1_select.value = self.voice1
            except:
                pass
        
        if self.voice2 and self.voice_mode == 2:
            # Wait for voice 2 section to be created
            self.call_after_refresh(lambda: self._set_voice2_value())
        
        # Apply blend ratio
        if self.blend_ratio != 0.5:
            blend_widget = self.query_one("#blend-ratio", BlendRatioWidget)
            blend_widget.current_ratio = self.blend_ratio
            ratio_select = blend_widget.query_one("#blend-ratio-select", Select)
            try:
                ratio_select.value = self.blend_ratio
                blend_widget.update_status()
            except:
                pass
    
    def _set_voice2_value(self) -> None:
        """Set voice 2 value after widget is created."""
        if not self.voice2:
            return
        try:
            voice_widget = self.query_one("#voice-selection", VoiceSelectionWidget)
            voice2_select = voice_widget.query_one("#voice-2-select", Select)
            voice2_select.value = self.voice2
            voice_widget.selected_voice2 = self.voice2
            voice_widget.update_status()
        except:
            pass

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
        
        # Disable UI
        self.is_generating = True
        self.update_footer("Generating audio... Please wait.")
        generate_btn = self.query_one("#generate-btn", Button)
        generate_btn.disabled = True
        
        # Disable inputs
        file_input = self.query_one("#file-input", FileInputWidget)
        voice_selection = self.query_one("#voice-selection", VoiceSelectionWidget)
        output_widget = self.query_one("#output-filename", OutputFilenameWidget)
        
        file_input.disabled = True
        voice_selection.disabled = True
        output_widget.disabled = True
        
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
        if event.worker.name == "audio_generator":
            if event.worker.state == "success":
                result = event.worker.result
                output_path = Path(result) if result else None
                
                # Build completion message
                if output_path and output_path.exists():
                    completion_msg = (
                        f"✅ Generation Complete!\n"
                        f"File: {output_path.name}\n"
                        f"Location: {output_path.parent}"
                    )
                else:
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
                
                # Reset UI state (but keep voices/ratio)
                self._reset_ui_after_generation()
                
            elif event.worker.state == "error":
                error = event.worker.error
                error_msg = str(error) if error else "Unknown error"
                self.message_log.log(f"Generation failed: {error_msg}", "error")
                self.update_footer("Ready - Generation failed")
                self.notify(
                    f"❌ Generation Failed\n{error_msg}",
                    severity="error",
                    timeout=8.0,
                )
                
                # Re-enable UI on error
                self.is_generating = False
                generate_btn = self.query_one("#generate-btn", Button)
                generate_btn.disabled = False
                
                file_input = self.query_one("#file-input", FileInputWidget)
                voice_selection = self.query_one("#voice-selection", VoiceSelectionWidget)
                output_widget = self.query_one("#output-filename", OutputFilenameWidget)
                
                file_input.disabled = False
                voice_selection.disabled = False
                output_widget.disabled = False
            else:
                return
    
    def _reset_ui_after_generation(self) -> None:
        """Reset UI state after successful generation (keep voices/ratio)."""
        # Reset generation state
        self.is_generating = False
        
        # Reset footer
        self.update_footer("Ready")
        
        # Re-enable generate button
        generate_btn = self.query_one("#generate-btn", Button)
        generate_btn.disabled = False
        
        # Re-enable widgets
        file_input = self.query_one("#file-input", FileInputWidget)
        voice_selection = self.query_one("#voice-selection", VoiceSelectionWidget)
        output_widget = self.query_one("#output-filename", OutputFilenameWidget)
        
        file_input.disabled = False
        voice_selection.disabled = False
        output_widget.disabled = False
        
        # Clear file input (reset script)
        self.selected_text = ""
        self.selected_file_path = None
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
        
        # Reset output filename to default (but keep it enabled)
        # The smart filename will update when a new file is loaded
        try:
            output_input = output_widget.query_one("#output-filename-input", Input)
            output_input.value = "output"
            output_widget.current_filename = "output"
            output_widget.validate_filename()
            output_widget.update_status()
        except:
            # If widget not ready, just set the internal state
            output_widget.current_filename = "output"
            output_widget.validate_filename()
        
        # Log reset
        self.message_log.log("UI reset - ready for next generation", "info")
