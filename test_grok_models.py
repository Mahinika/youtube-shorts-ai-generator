"""
Test script to compare different Grok models.
This will help you see the quality differences between models.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_grok_models():
    """Test different Grok models with the same prompt"""
    
    print("=" * 60)
    print("GROK MODEL COMPARISON TEST")
    print("=" * 60)
    
    test_prompt = "Make me a story about a boy playing with his red toy car"
    
    print(f"Test Prompt: '{test_prompt}'")
    print()
    
    models_to_test = ["grok-beta", "grok-3", "grok-2"]
    
    print("This test will:")
    print("1. Generate the same story with different models")
    print("2. Show you the quality differences")
    print("3. Help you choose the best model")
    print()
    
    input("Press Enter to start testing...")
    
    try:
        from utils.ai_providers import GrokProvider
        from settings.config import Config
        
        original_model = Config.GROK_MODEL
        print(f"Current model: {original_model}")
        print()
        
        results = {}
        
        for model in models_to_test:
            print(f"Testing {model}...")
            print("-" * 40)
            
            try:
                # Temporarily change model
                Config.GROK_MODEL = model
                
                # Generate story
                system_prompt = "You are a storyteller. Create engaging, pure storytelling content. Focus on narrative, characters, and emotions. Avoid adding facts, statistics, or educational content unless specifically requested."
                
                response = GrokProvider.generate(system_prompt, test_prompt)
                results[model] = response
                
                print(f"✅ {model} generated successfully")
                print(f"Response length: {len(response)} characters")
                print()
                
            except Exception as e:
                print(f"❌ {model} failed: {e}")
                results[model] = None
                print()
        
        # Restore original model
        Config.GROK_MODEL = original_model
        
        # Show results comparison
        print("=" * 60)
        print("RESULTS COMPARISON")
        print("=" * 60)
        
        for model, response in results.items():
            if response:
                print(f"\n--- {model.upper()} ---")
                print(response[:200] + "..." if len(response) > 200 else response)
                print()
        
        print("=" * 60)
        print("ANALYSIS")
        print("=" * 60)
        print("Compare the results above and look for:")
        print("• Story quality and creativity")
        print("• Character development")
        print("• Narrative flow")
        print("• Presence of unwanted facts")
        print("• Overall engagement")
        print()
        print("💡 RECOMMENDATION:")
        print("Choose the model that produces the most engaging,")
        print("story-focused content without unwanted facts!")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you have the required packages installed.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_grok_models()
