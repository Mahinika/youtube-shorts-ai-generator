"""
Test script for the Grok configuration interface.
Run this to verify the Grok config panel works correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import customtkinter as ctk
    from ui.grok_config_panel import GrokConfigPanel
    from settings.config import Config
    
    print("=" * 60)
    print("TESTING GROK CONFIGURATION INTERFACE")
    print("=" * 60)
    
    # Show current configuration
    print(f"Current AI Provider: {Config.AI_PROVIDER}")
    print(f"Grok API Base: {Config.GROK_API_BASE}")
    print(f"Grok Model: {Config.GROK_MODEL}")
    print(f"Grok API Key: {'*' * 20 if Config.GROK_API_KEY else 'NOT SET'}")
    print()
    
    # Create test window
    root = ctk.CTk()
    root.title("Grok Configuration Test")
    root.geometry("900x800")
    root.configure(fg_color="#181818")
    
    # Create Grok config panel
    panel = GrokConfigPanel(root)
    panel.pack(fill="both", expand=True, padx=20, pady=20)
    
    print("✅ Grok Configuration Panel loaded successfully!")
    print("📋 Features available:")
    print("  • View current Grok configuration")
    print("  • Check API key status")
    print("  • Test Grok connection")
    print("  • View connection status")
    print("  • Open config file for editing")
    print()
    print("🎯 To test:")
    print("  1. Check the status indicators")
    print("  2. Click 'Test Grok Connection'")
    print("  3. Click 'Open Config File' to edit settings")
    print("  4. Click 'Refresh Config' to reload settings")
    print()
    print("🖥️  GUI window opened - interact with it to test!")
    
    # Start the GUI
    root.mainloop()
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure all required packages are installed:")
    print("  pip install customtkinter")
    print("  pip install openai")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
