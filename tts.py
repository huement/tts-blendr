import os
import urllib.request
import soundfile as sf
from kokoro_onnx import Kokoro

# Minimal Script to show the basic process. 

# --- 1. CONFIGURATION ---
TEXT_SCRIPT = """
You type whatever you want said here.
"""

AUDIO_FILENAME = "final_audio-onyx-and-eric.wav"

# Blened Voices
VOICE = "am_michael+am_onyx"  # Options: af_bella, af_sarah, am_adam, bm_george etc.


# --- 2. MAIN PIPELINE ---
def main():
    # Step A: Generate Audio
    print("\n🎤 STEP 1: Generating Audio...")
    download_kokoro_files()
    
    kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
    
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

    # This Creates the File!  
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

   
    print("🚀 Process Complete!")

if __name__ == "__main__":
    main()