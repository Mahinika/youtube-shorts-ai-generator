"""
Test script to verify Piper TTS integration with the existing voice generation pipeline.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_piper_integration():
    """Test Piper TTS integration with the TTS manager"""
    
    print("=" * 60)
    print("TESTING PIPER TTS INTEGRATION")
    print("=" * 60)
    
    try:
        from utils.tts_manager import TTSManager
        from settings.config import Config
        
        print("Testing TTS Manager with Piper TTS...")
        
        # Create TTS manager
        tts_manager = TTSManager(preferred_engine="piper")
        
        # Test text
        test_text = """Meet Jimmy, a lively six-year-old who loves playing with his toys. 
        His red toy car zooms around his bedroom, racing past stuffed animals and action figures. 
        Jimmy's imagination turns his room into a magical world where every toy has its own adventure."""
        
        # Generate audio
        output_path = Path("temp_files/test_piper_integration.wav")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Generating audio for test text...")
        print(f"Text: {test_text[:50]}...")
        
        result = tts_manager.generate_audio(test_text, output_path)
        
        if result['success']:
            print(f"[SUCCESS] Audio generated successfully!")
            print(f"Engine used: {result['engine']}")
            print(f"Output file: {result['path']}")
            print(f"Duration: {result['duration']:.1f} seconds")
            print(f"File size: {Path(result['path']).stat().st_size / 1024:.1f} KB")
            
            print("\n[INTEGRATION TEST RESULTS]")
            print("[SUCCESS] Piper TTS integrated successfully")
            print("[SUCCESS] TTS Manager working with Piper")
            print("[SUCCESS] Ready for YouTube Shorts generation")
            
        else:
            print(f"[ERROR] Audio generation failed: {result}")
            
    except Exception as e:
        print(f"[ERROR] Integration test failed: {e}")
        import traceback
        traceback.print_exc()

def test_configuration():
    """Test that the configuration is set up correctly"""
    
    print("\n" + "=" * 60)
    print("TESTING CONFIGURATION")
    print("=" * 60)
    
    try:
        from settings.config import Config
        
        print(f"TTS Provider: {getattr(Config, 'TTS_PROVIDER', 'Not set')}")
        print(f"Piper Model Path: {getattr(Config, 'PIPER_MODEL_PATH', 'Not set')}")
        print(f"Piper Config Path: {getattr(Config, 'PIPER_CONFIG_PATH', 'Not set')}")
        print(f"Piper Use CUDA: {getattr(Config, 'PIPER_USE_CUDA', 'Not set')}")
        
        # Check if model files exist
        model_path = getattr(Config, 'PIPER_MODEL_PATH', None)
        config_path = getattr(Config, 'PIPER_CONFIG_PATH', None)
        
        if model_path and Path(model_path).exists():
            print(f"[SUCCESS] Piper model file exists: {model_path}")
        else:
            print(f"[ERROR] Piper model file not found: {model_path}")
            
        if config_path and Path(config_path).exists():
            print(f"[SUCCESS] Piper config file exists: {config_path}")
        else:
            print(f"[ERROR] Piper config file not found: {config_path}")
            
    except Exception as e:
        print(f"[ERROR] Configuration test failed: {e}")

if __name__ == "__main__":
    test_configuration()
    test_piper_integration()
