import os
import urllib.request
import soundfile as sf
from kokoro_onnx import Kokoro
from faster_whisper import WhisperModel
import datetime

# --- 1. CONFIGURATION ---
TEXT_SCRIPT = """
Here we see the wild Brother-in-Law in his natural habitat. 
Observe as he stares at his phone, blissfully unaware that this voice is not real.
He believes he is listening to a human, but in reality, I am just a Python script running on a 2019 Mac that is currently overheating.
Fascinating.
"""

AUDIO_FILENAME = "final_audio-onyx-and-eric.wav"
VOICE = "am_michael+am_onyx"  # Options: af_bella, af_sarah, am_adam, bm_george

# --- Update these filenames to v1.0 ---
KOKORO_MODEL = "kokoro-v1.0.onnx"
VOICES_FILE = "voices-v1.0.bin"

# --- 2. DOWNLOAD MODELS (Auto-run) ---
def download_kokoro_files():
    """Downloads the voice model files (~300MB) if missing."""
    # Define the V1.0 file targets
    model_file = "kokoro-v1.0.onnx"
    voices_file = "voices-v1.0.bin"

    if not os.path.exists(model_file):
        print(f"⬇️  Downloading {model_file}...")
        urllib.request.urlretrieve(
            "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
            model_file
        )
        
    if not os.path.exists(voices_file):
        print(f"⬇️  Downloading {voices_file}...")
        urllib.request.urlretrieve(
            "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
            voices_file
        )

# --- 4. MAIN PIPELINE ---
def main():
    # Step A: Generate Audio
    print("\n🎤 STEP 1: Generating Audio...")
    download_kokoro_files()
    
    kokoro = Kokoro(KOKORO_MODEL, VOICES_FILE)
    
    # --- 🧪 THE BLENDER LAB ---
    print("⚗️  Blending Voices...")
    # 1. Get the raw style vectors (these are just big arrays of numbers)
    # You can pick ANY two voices from your pack
    voice_1 = kokoro.voices["am_onyx"]   # The "Expensive" voice
    voice_2 = kokoro.voices["am_eric"]   # The "Deep" voice
    
    # 2. Mix them! 
    # 0.5 is a 50/50 split. 
    # Change to 0.7 * voice_1 + 0.3 * voice_2 to make it mostly Onyx.
    mixed_style = (voice_1 * 0.5) + (voice_2 * 0.5)
    # 3. Register this new style into the library's dictionary
    # We give it a custom name so we can call it later
    if not isinstance(kokoro.voices, dict):
        kokoro.voices = dict(kokoro.voices)
            
    kokoro.voices["custom_mix"] = mixed_style
    print("✅ Custom voice 'custom_mix' created!")

    # samples, sample_rate = kokoro.create(TEXT_SCRIPT, voice=VOICE, speed=1.0, lang="en-us")
    # 4. Use the custom name
    samples, sample_rate = kokoro.create(
        TEXT_SCRIPT, 
        voice="custom_mix",  # <--- Use the name you just registered
        speed=1.0, 
        lang="en-us"
        )
        
    sf.write(AUDIO_FILENAME, samples, sample_rate)
    print(f"✅ Audio saved to: {AUDIO_FILENAME}")

   
    print("🚀 Pipeline Complete!")

if __name__ == "__main__":
    main()