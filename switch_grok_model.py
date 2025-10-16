"""
Quick script to switch between Grok models.
Run this to easily change your Grok model without editing config files.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def switch_grok_model():
    """Interactive script to switch Grok models"""
    
    print("=" * 60)
    print("GROK MODEL SWITCHER")
    print("=" * 60)
    
    # Available models with descriptions
    models = {
        "1": {
            "name": "grok-beta",
            "description": "Latest model with best reasoning quality",
            "best_for": "Script generation, creative content",
            "tokens": "Same as grok-3, better quality"
        },
        "2": {
            "name": "grok-4-fast", 
            "description": "Newest model optimized for speed and efficiency",
            "best_for": "High-volume generation, speed priority",
            "tokens": "2M context, 344 tokens/sec, more efficient"
        },
        "3": {
            "name": "grok-3",
            "description": "Current default model",
            "best_for": "Reliable performance, current setup",
            "tokens": "Standard token usage"
        },
        "4": {
            "name": "grok-2",
            "description": "Previous generation model",
            "best_for": "Legacy support, compatibility",
            "tokens": "Standard token usage"
        }
    }
    
    print("Available Grok Models:")
    print()
    
    for key, model in models.items():
        print(f"{key}. {model['name']}")
        print(f"   Description: {model['description']}")
        print(f"   Best for: {model['best_for']}")
        print(f"   Token usage: {model['tokens']}")
        print()
    
    print("=" * 60)
    
    # Get user choice
    while True:
        choice = input("Enter the number of the model you want to use (1-4): ").strip()
        
        if choice in models:
            selected_model = models[choice]
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")
    
    # Update config file
    try:
        config_path = Path("settings/config.py")
        
        if not config_path.exists():
            print(f"Error: Config file not found at {config_path}")
            return
        
        # Read current config
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # Update the model line
        import re
        pattern = r'GROK_MODEL = "[^"]*"'
        replacement = f'GROK_MODEL = "{selected_model["name"]}"'
        
        new_config = re.sub(pattern, replacement, config_content)
        
        # Write updated config
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(new_config)
        
        print()
        print("✅ SUCCESS!")
        print(f"Switched to: {selected_model['name']}")
        print(f"Description: {selected_model['description']}")
        print()
        print("🚀 Next steps:")
        print("1. Restart your YouTube Shorts Maker")
        print("2. Test the new model using 'Test Grok Connection'")
        print("3. Generate a script to see the improvements")
        
        # Show recommendation
        if selected_model['name'] == 'grok-beta':
            print()
            print("💡 RECOMMENDATION: grok-beta is perfect for script generation!")
            print("   You should see better story quality and creativity.")
        elif selected_model['name'] == 'grok-4-fast':
            print()
            print("⚡ SPEED BOOST: grok-4-fast will generate scripts much faster!")
            print("   You should see 3x faster response times.")
        
    except Exception as e:
        print(f"❌ Error updating config: {e}")
        print("Please manually edit settings/config.py and change GROK_MODEL")

if __name__ == "__main__":
    switch_grok_model()
