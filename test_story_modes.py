"""
Test script for different story generation modes.
Run this to see the difference between story and educational modes.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.prompt_manager import PromptManager
from settings.config import Config

def test_prompt_modes():
    """Test different prompt modes"""
    
    print("=" * 60)
    print("TESTING STORY GENERATION MODES")
    print("=" * 60)
    
    prompt_manager = PromptManager()
    
    # Test prompt
    test_prompt = "Make me a story about a boy playing with his red toy car"
    
    print(f"Test Prompt: '{test_prompt}'")
    print()
    
    # Test different modes
    modes = ["auto", "story", "educational"]
    
    for mode in modes:
        print(f"--- {mode.upper()} MODE ---")
        
        # Get the prompt for this mode
        prompt_name = prompt_manager.get_prompt_mode(mode)
        system_prompt = prompt_manager.get_prompt(prompt_name)
        
        # Show key differences
        if "story" in prompt_name:
            print("✅ Focus: Pure storytelling")
            print("✅ Avoids: Facts and statistics")
            print("✅ Includes: Characters, emotions, narrative")
        else:
            print("📚 Focus: Educational content")
            print("📊 Includes: Facts, statistics, research")
            print("🎯 Auto-detects: Story vs educational requests")
        
        print(f"📄 Prompt file: {prompt_name}.txt")
        print()
    
    print("=" * 60)
    print("HOW TO CHANGE MODE:")
    print("=" * 60)
    print("1. Open settings/config.py")
    print("2. Find SCRIPT_GENERATION_MODE")
    print("3. Change to:")
    print("   - 'auto' (default, detects what you want)")
    print("   - 'story' (pure storytelling, no facts)")
    print("   - 'educational' (facts and data)")
    print("   - 'mixed' (both, with auto-detection)")
    print()
    print("4. Save and restart the app")
    print()
    print("🎯 RECOMMENDATION: Use 'auto' mode - it will detect")
    print("   when you want a story vs educational content!")

if __name__ == "__main__":
    test_prompt_modes()
