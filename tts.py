import soundfile as sf
from kokoro_onnx import Kokoro

TEXT_SCRIPT = """
You type whatever you want said here.
"""

AUDIO_FILENAME = "final_audio-michael-onyx.wav"

# Blened Voices
VOICE = "am_michael+am_onyx"  # Options: af_bella, af_sarah, am_adam, bm_george etc.


# --- 2. MAIN PIPELINE ---
def main():
    
    kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
    
    # --- 🧪 THE BLENDER LAB ---
    voice_1 = kokoro.voices["am_onyx"]   # The "Expensive" voice
    voice_2 = kokoro.voices["am_eric"]   # The "Deep" voice
    
    mixed_style = (voice_1 * 0.5) + (voice_2 * 0.5)

    if not isinstance(kokoro.voices, dict):
        kokoro.voices = dict(kokoro.voices)
            
    kokoro.voices["custom_mix"] = mixed_style
    print("✅ Custom voice 'custom_mix' created!")

    samples, sample_rate = kokoro.create(
        TEXT_SCRIPT, 
        voice="custom_mix",  # <--- Use the name you just registered
        speed=1.0, 
        lang="en-us"
        )
        
    sf.write(AUDIO_FILENAME, samples, sample_rate)
    print(f"✅ Audio saved to: {AUDIO_FILENAME}")

if __name__ == "__main__":
    main()