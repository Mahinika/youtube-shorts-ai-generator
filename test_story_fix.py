"""
Test script to verify that story generation no longer includes unwanted facts.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_story_generation():
    """Test story generation to ensure no facts are included"""
    
    print("=" * 60)
    print("TESTING STORY GENERATION (NO FACTS)")
    print("=" * 60)
    
    test_prompt = "Make me a story about jimmy the kid playing with his toys"
    
    print(f"Test Prompt: '{test_prompt}'")
    print()
    
    try:
        from steps.step1_write_script import write_script_with_ollama
        from settings.config import Config
        
        print("Generating story...")
        result = write_script_with_ollama(test_prompt)
        
        if result and 'script' in result:
            script = result['script']
            print("✅ Story generated successfully!")
            print()
            print("Generated Script:")
            print("-" * 40)
            print(script)
            print("-" * 40)
            print()
            
            # Check for unwanted content
            unwanted_phrases = [
                "did you know",
                "research shows", 
                "studies indicate",
                "brain development",
                "75%",
                "learning",
                "educational",
                "facts",
                "statistics"
            ]
            
            found_unwanted = []
            for phrase in unwanted_phrases:
                if phrase.lower() in script.lower():
                    found_unwanted.append(phrase)
            
            if found_unwanted:
                print("❌ PROBLEM: Found unwanted content:")
                for phrase in found_unwanted:
                    print(f"   - '{phrase}'")
                print()
                print("The story still contains facts/educational content!")
            else:
                print("✅ SUCCESS: No unwanted facts or educational content found!")
                print("The story is pure storytelling as requested.")
                
        else:
            print("❌ Failed to generate story")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_story_generation()
