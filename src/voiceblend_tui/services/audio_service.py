"""Audio generation service."""

from pathlib import Path
from typing import Optional
from voiceblend_tui.core.blender import VoiceBlender


class AudioService:
    """Service for orchestrating audio generation."""
    
    def __init__(self, blender: VoiceBlender):
        """Initialize audio service.
        
        Args:
            blender: VoiceBlender instance for audio generation
        """
        self.blender = blender
    
    def generate_audio(
        self,
        text: str,
        voice_mode: int,
        voice1: str,
        output_path: Path | str,
        voice2: Optional[str] = None,
        ratio: float = 0.5,
    ) -> str:
        """
        Generate audio from text using selected voices.
        
        Args:
            text: Text to synthesize
            voice_mode: 1 or 2 (number of voices)
            voice1: First voice name
            voice2: Second voice name (required if voice_mode == 2)
            ratio: Blend ratio 0.0-1.0 (only used if voice_mode == 2)
            output_path: Output file path
            
        Returns:
            Success message string
            
        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If generation fails
        """
        if voice_mode == 1:
            # Single voice - use voice1 with 100% weight
            return self.blender.blend(
                text=text,
                model_a=voice1,
                model_b=voice1,  # Same voice, but ratio will be 0.0
                ratio=0.0,  # 100% voice1
                out_file=str(output_path),
            )
        elif voice_mode == 2:
            # Two voices - blend them
            if not voice2:
                raise ValueError("voice2 is required when voice_mode is 2")
            return self.blender.blend(
                text=text,
                model_a=voice1,
                model_b=voice2,
                ratio=ratio,
                out_file=str(output_path),
            )
        else:
            raise ValueError(f"Invalid voice_mode: {voice_mode}. Must be 1 or 2.")

