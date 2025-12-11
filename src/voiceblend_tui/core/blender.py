"""Voice blending logic using kokoro-onnx."""

import os
import urllib.request
from pathlib import Path
from typing import List
import soundfile as sf
from kokoro_onnx import Kokoro


class VoiceBlender:
    """Handles voice blending operations using kokoro-onnx."""

    KOKORO_MODEL = "kokoro-v1.0.onnx"
    VOICES_FILE = "voices-v1.0.bin"
    
    def __init__(self, voices_path: Path = None):
        """Initialize the voice blender."""
        self.voices_path = voices_path or Path("voices")
        self.model_path = self.voices_path / self.KOKORO_MODEL
        self.voices_file_path = self.voices_path / self.VOICES_FILE
        self._kokoro: Kokoro | None = None

    def _ensure_models_downloaded(self) -> None:
        """Download kokoro model files if they don't exist."""
        self.voices_path.mkdir(parents=True, exist_ok=True)
        
        if not self.model_path.exists():
            print(f"⬇️  Downloading {self.KOKORO_MODEL}...")
            urllib.request.urlretrieve(
                "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
                str(self.model_path)
            )
            print(f"✅ Downloaded {self.KOKORO_MODEL}")
        
        if not self.voices_file_path.exists():
            print(f"⬇️  Downloading {self.VOICES_FILE}...")
            urllib.request.urlretrieve(
                "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
                str(self.voices_file_path)
            )
            print(f"✅ Downloaded {self.VOICES_FILE}")

    def _get_kokoro(self) -> Kokoro:
        """Get or initialize Kokoro instance."""
        if self._kokoro is None:
            self._ensure_models_downloaded()
            self._kokoro = Kokoro(str(self.model_path), str(self.voices_file_path))
        return self._kokoro

    def list_models(self) -> List[str]:
        """List available voice models from kokoro."""
        try:
            kokoro = self._get_kokoro()
            # Get available voice names
            if isinstance(kokoro.voices, dict):
                voices = list(kokoro.voices.keys())
            else:
                # If it's not a dict, try to convert or get names another way
                voices = list(kokoro.voices) if hasattr(kokoro.voices, '__iter__') else []
            
            # Sort for consistent display
            return sorted(voices) if voices else []
        except Exception as e:
            # If kokoro isn't initialized yet, return common voice names
            # These are typical kokoro voice names
            return [
                "af_bella",
                "af_sarah",
                "am_adam",
                "am_eric",
                "am_michael",
                "am_onyx",
                "bm_george",
            ]

    def blend(
        self,
        text: str,
        model_a: str,
        model_b: str,
        ratio: float,
        out_file: str,
    ) -> str:
        """
        Blend two voice models and generate audio.

        Args:
            text: Text to synthesize
            model_a: First voice model name (kokoro voice name)
            model_b: Second voice model name (kokoro voice name)
            ratio: Blend ratio (0.0 to 1.0, where 0.0 = all model_a, 1.0 = all model_b)
            out_file: Output file path

        Returns:
            Success message string

        Raises:
            ValueError: If voice names are invalid
            RuntimeError: If audio generation fails
        """
        try:
            kokoro = self._get_kokoro()
            
            # Ensure voices is a dict
            if not isinstance(kokoro.voices, dict):
                kokoro.voices = dict(kokoro.voices)
            
            # Validate voice names
            if model_a not in kokoro.voices:
                raise ValueError(f"Voice '{model_a}' not found. Available: {list(kokoro.voices.keys())}")
            if model_b not in kokoro.voices:
                raise ValueError(f"Voice '{model_b}' not found. Available: {list(kokoro.voices.keys())}")
            
            # Get voice style vectors
            voice_1 = kokoro.voices[model_a]
            voice_2 = kokoro.voices[model_b]
            
            # Blend the voices
            # ratio: 0.0 = all voice_1, 1.0 = all voice_2
            # So: (1 - ratio) * voice_1 + ratio * voice_2
            weight_1 = 1.0 - ratio
            weight_2 = ratio
            mixed_style = (voice_1 * weight_1) + (voice_2 * weight_2)
            
            # Register custom blend
            custom_name = f"blend_{model_a}_{model_b}_{int(ratio * 100)}"
            kokoro.voices[custom_name] = mixed_style
            
            # Generate audio
            samples, sample_rate = kokoro.create(
                text,
                voice=custom_name,
                speed=1.0,
                lang="en-us"
            )
            
            # Ensure output directory exists
            out_path = Path(out_file)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save audio file
            sf.write(str(out_path), samples, sample_rate)
            
            ratio_percent = int(ratio * 100)
            return (
                f"✅ Successfully generated audio!\n"
                f"Text: {text[:50]}{'...' if len(text) > 50 else ''}\n"
                f"Voice A: {model_a} ({100 - ratio_percent}%)\n"
                f"Voice B: {model_b} ({ratio_percent}%)\n"
                f"Output: {out_path}\n"
                f"Duration: ~{len(samples) / sample_rate:.2f}s"
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate audio: {e}") from e

