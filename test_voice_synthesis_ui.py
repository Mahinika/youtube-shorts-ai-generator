"""
Test script to verify Piper TTS integration in the voice synthesis UI.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_voice_synthesis_ui():
    """Test the voice synthesis UI with Piper TTS integration"""
    
    print("=" * 60)
    print("TESTING VOICE SYNTHESIS UI INTEGRATION")
    print("=" * 60)
    
    try:
        import customtkinter as ctk
        from ui.control_panels import VoiceSynthesisPanel
        
        # Create a test window
        root = ctk.CTk()
        root.title("Voice Synthesis UI Test")
        root.geometry("800x600")
        
        # Create the voice synthesis panel
        panel = VoiceSynthesisPanel(root)
        panel.pack(fill="both", expand=True, padx=10, pady=10)
        
        print("[SUCCESS] Voice synthesis panel created successfully")
        print("[INFO] Checking for Piper TTS integration...")
        
        # Check if Piper TTS is available in the dropdown
        if hasattr(panel, 'engine_dropdown'):
            values = panel.engine_dropdown._values
            if "piper" in values:
                print("[SUCCESS] Piper TTS option found in engine dropdown")
            else:
                print("[ERROR] Piper TTS option not found in engine dropdown")
                print(f"Available options: {values}")
        
        # Check if Piper configuration section exists
        if hasattr(panel, 'piper_frame'):
            print("[SUCCESS] Piper TTS configuration section found")
        else:
            print("[ERROR] Piper TTS configuration section not found")
        
        # Check if status indicator exists
        if hasattr(panel, 'piper_status_label'):
            print("[SUCCESS] Piper TTS status indicator found")
        else:
            print("[ERROR] Piper TTS status indicator not found")
        
        print("\n[UI TEST INSTRUCTIONS]")
        print("1. The voice synthesis panel should now show:")
        print("   - TTS Engine dropdown with 'piper', 'edge', 'gtts' options")
        print("   - Piper TTS Configuration section (when 'piper' is selected)")
        print("   - Status indicator showing 'Ready (High Quality Neural Voice)'")
        print("2. Try switching between different TTS engines")
        print("3. Verify that the appropriate configuration sections appear/disappear")
        print("4. Close the window when done testing")
        
        # Run the UI
        root.mainloop()
        
    except Exception as e:
        print(f"[ERROR] UI test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_voice_synthesis_ui()
