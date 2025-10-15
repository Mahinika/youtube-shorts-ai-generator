"""
TEST STABLE DIFFUSION WEBUI INTEGRATION

This script tests the WebUI API integration and verifies it's working properly.
Run this after starting the WebUI with launch_sd_webui.bat
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from helpers.sd_webui_api import SDWebUIAPI
from settings.config import Config


def test_connection():
    """Test basic connection to WebUI"""
    print("=" * 70)
    print("STEP 1: Testing WebUI Connection")
    print("=" * 70)
    
    try:
        api = SDWebUIAPI(
            host=Config.SD_WEBUI_HOST,
            timeout=Config.SD_WEBUI_TIMEOUT
        )
        print("✓ Successfully connected to WebUI API\n")
        return api
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        print("\nMake sure the WebUI is running:")
        print("  1. Run: launch_sd_webui.bat")
        print("  2. Wait for 'Running on local URL: http://127.0.0.1:7860'")
        print("  3. Then run this script again\n")
        return None


def test_info(api):
    """Test getting WebUI info"""
    print("=" * 70)
    print("STEP 2: Getting WebUI Information")
    print("=" * 70)
    
    models = api.get_models()
    if models:
        print(f"✓ Found {len(models)} model(s):")
        for i, model in enumerate(models[:5], 1):
            print(f"  {i}. {model}")
        if len(models) > 5:
            print(f"  ... and {len(models) - 5} more")
    else:
        print("⚠ No models found - you may need to download a model")
    
    print()
    
    samplers = api.get_samplers()
    if samplers:
        print(f"✓ Found {len(samplers)} sampler(s):")
        for i, sampler in enumerate(samplers[:5], 1):
            print(f"  {i}. {sampler}")
    
    print()


def test_generation(api):
    """Test image generation"""
    print("=" * 70)
    print("STEP 3: Testing Image Generation")
    print("=" * 70)
    
    print("\nGenerating test image for YouTube Shorts...")
    print("Prompt: Space nebula with vibrant colors")
    print(f"Size: {Config.SD_GENERATION_WIDTH}x{Config.SD_GENERATION_HEIGHT}")
    print(f"Steps: {Config.SD_INFERENCE_STEPS}")
    print()
    
    image = api.generate_image(
        prompt="Space nebula with vibrant colors, vertical composition, 9:16, cinematic",
        negative_prompt="blurry, low quality, ugly, horizontal",
        width=Config.SD_GENERATION_WIDTH,
        height=Config.SD_GENERATION_HEIGHT,
        steps=Config.SD_INFERENCE_STEPS,
        cfg_scale=Config.SD_GUIDANCE_SCALE,
        sampler=Config.SD_WEBUI_SAMPLER,
    )
    
    if image:
        # Save test image
        output_path = Path("test_webui_generation.png")
        image.save(output_path)
        print(f"✓ Image generated successfully!")
        print(f"✓ Saved to: {output_path}")
        print(f"  Size: {image.size[0]}x{image.size[1]} pixels")
        print()
        return True
    else:
        print("✗ Image generation failed")
        print()
        return False


def test_full_workflow():
    """Test full workflow with multiple scenes"""
    print("=" * 70)
    print("STEP 4: Testing Full YouTube Shorts Workflow")
    print("=" * 70)
    
    from steps.step3_generate_backgrounds import generate_ai_backgrounds
    
    test_scenes = [
        "Ocean waves crashing on beach at sunset",
        "City skyline at night with glowing lights",
        "Mountain landscape with dramatic clouds",
    ]
    
    print("\nGenerating backgrounds for 3 test scenes...")
    print("This will use the settings from config.py")
    print()
    
    image_paths = generate_ai_backgrounds(test_scenes, duration_per_scene=3.0)
    
    if image_paths:
        print(f"\n✓ Generated {len(image_paths)} backgrounds:")
        for path in image_paths:
            print(f"  - {path}")
        print()
        return True
    else:
        print("\n✗ No backgrounds generated")
        print()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print(" STABLE DIFFUSION WEBUI INTEGRATION TEST")
    print("=" * 70)
    print()
    
    # Test 1: Connection
    api = test_connection()
    if not api:
        return False
    
    # Test 2: Info
    test_info(api)
    
    # Test 3: Single generation
    success = test_generation(api)
    if not success:
        return False
    
    # Test 4: Full workflow
    print("Do you want to test the full workflow? (generates 3 images)")
    response = input("Enter 'y' to continue or 'n' to skip: ").lower().strip()
    
    if response == 'y':
        success = test_full_workflow()
    
    # Summary
    print("=" * 70)
    print(" TEST SUMMARY")
    print("=" * 70)
    print()
    if success:
        print("✓ All tests passed!")
        print()
        print("Your WebUI integration is working correctly.")
        print("You can now generate YouTube Shorts with:")
        print("  python start_app.py")
        print()
        print("Make sure to:")
        print("  1. Keep the WebUI running (launch_sd_webui.bat)")
        print("  2. Set SD_METHOD='webui' in settings/config.py (already set)")
    else:
        print("⚠ Some tests failed")
        print()
        print("Check the errors above and try again.")
    
    print("=" * 70)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nError during testing: {e}")
        import traceback
        traceback.print_exc()

