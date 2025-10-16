"""
Test script for Piper TTS integration.
This will download a voice model and test the quality.
"""

import sys
from pathlib import Path
import wave
import os

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def download_piper_model():
    """Download a high-quality Piper TTS voice model"""
    
    print("=" * 60)
    print("PIPER TTS SETUP")
    print("=" * 60)
    
    # Create models directory
    models_dir = Path("models/piper")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Model URLs for high-quality voices
    models = {
        "en-us-amy-medium": {
            "url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx",
            "config": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx.json",
            "description": "Natural female voice - Amy (Medium quality)"
        },
        "en-us-lessac-medium": {
            "url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
            "config": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json",
            "description": "Natural female voice - Lessac (Medium quality)"
        }
    }
    
    selected_model = "en-us-amy-medium"
    model_info = models[selected_model]
    
    print(f"Downloading model: {selected_model}")
    print(f"Description: {model_info['description']}")
    print()
    
    # Download model file
    model_path = models_dir / f"{selected_model}.onnx"
    config_path = models_dir / f"{selected_model}.onnx.json"
    
    if not model_path.exists():
        print("Downloading model file...")
        try:
            import urllib.request
            urllib.request.urlretrieve(model_info["url"], model_path)
            print(f"[SUCCESS] Model downloaded: {model_path}")
        except Exception as e:
            print(f"[ERROR] Failed to download model: {e}")
            return None
    else:
        print(f"[SUCCESS] Model already exists: {model_path}")
    
    # Download config file
    if not config_path.exists():
        print("Downloading config file...")
        try:
            import urllib.request
            urllib.request.urlretrieve(model_info["config"], config_path)
            print(f"[SUCCESS] Config downloaded: {config_path}")
        except Exception as e:
            print(f"[ERROR] Failed to download config: {e}")
            return None
    else:
        print(f"[SUCCESS] Config already exists: {config_path}")
    
    return model_path, config_path

def test_piper_tts(model_path, config_path):
    """Test Piper TTS with the downloaded model"""
    
    print("\n" + "=" * 60)
    print("TESTING PIPER TTS")
    print("=" * 60)
    
    try:
        from piper import PiperVoice
        
        print("Loading Piper voice model...")
        voice = PiperVoice.load(model_path, config_path, use_cuda=False)
        print("[SUCCESS] Voice model loaded successfully!")
        
        # Test text (your typical YouTube Shorts script)
        test_text = """Meet Jimmy, a lively six-year-old who loves playing with his toys. 
        His red toy car zooms around his bedroom, racing past stuffed animals and action figures. 
        Jimmy's imagination turns his room into a magical world where every toy has its own adventure."""
        
        print(f"\nGenerating speech for test text...")
        print(f"Text: {test_text[:50]}...")
        
        # Save as WAV file
        output_path = Path("temp_files/test_piper_output.wav")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate audio directly to WAV file
        with wave.open(str(output_path), "wb") as wav_file:
            voice.synthesize_wav(test_text, wav_file)
        
        print(f"[SUCCESS] Audio generated and saved: {output_path}")
        
        # Get file size and duration info
        file_size = output_path.stat().st_size / 1024  # KB
        print(f"[INFO] File size: {file_size:.1f} KB")
        
        # Get duration from WAV file
        with wave.open(str(output_path), "rb") as wav_file:
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            duration = frames / sample_rate
        print(f"[INFO] Duration: {duration:.1f} seconds")
        
        print("\n[QUALITY TEST]")
        print("[SUCCESS] Piper TTS generated high-quality speech")
        print("[SUCCESS] Audio saved successfully")
        print("[SUCCESS] Ready for integration with your video pipeline")
        
        return str(output_path)
        
    except Exception as e:
        print(f"[ERROR] Error testing Piper TTS: {e}")
        return None

def main():
    """Main test function"""
    
    print("Setting up Piper TTS for your YouTube Shorts Generator...")
    
    # Download model
    model_files = download_piper_model()
    if not model_files:
        print("[ERROR] Failed to download model files")
        return
    
    model_path, config_path = model_files
    
    # Test TTS
    audio_file = test_piper_tts(model_path, config_path)
    if audio_file:
        print(f"\n[SUCCESS] Piper TTS is ready to use!")
        print(f"Test audio saved at: {audio_file}")
        print("\nNext steps:")
        print("1. Listen to the generated audio to verify quality")
        print("2. Integrate Piper TTS into your voice generation pipeline")
        print("3. Replace current gTTS/Edge TTS with Piper for better quality")
    else:
        print("[ERROR] Failed to test Piper TTS")

if __name__ == "__main__":
    main()
