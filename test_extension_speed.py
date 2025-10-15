"""Test Stable Diffusion extension speed improvements"""
import time
from settings.config import Config
from helpers.sd_webui_api import SDWebUIAPI

def test_generation_speed():
    """Test image generation speed with extensions enabled"""
    api = SDWebUIAPI(Config.SD_WEBUI_HOST, Config.SD_WEBUI_TIMEOUT)
    
    test_prompt = "futuristic cityscape at sunset, cinematic, 8k"
    
    print("Testing image generation speed...")
    print(f"Resolution: {Config.SD_GENERATION_WIDTH}x{Config.SD_GENERATION_HEIGHT}")
    print(f"Steps: {Config.SD_INFERENCE_STEPS}")
    print(f"Sampler: {Config.SD_WEBUI_SAMPLER}")
    print(f"Tiled Diffusion: {getattr(Config, 'SD_ENABLE_TILED_DIFFUSION', False)}")
    print(f"Tiled VAE: {getattr(Config, 'SD_ENABLE_TILED_VAE', False)}")
    
    start = time.time()
    image = api.generate_image(
        prompt=test_prompt,
        width=Config.SD_GENERATION_WIDTH,
        height=Config.SD_GENERATION_HEIGHT,
        steps=Config.SD_INFERENCE_STEPS,
        sampler=Config.SD_WEBUI_SAMPLER,
    )
    elapsed = time.time() - start
    
    print(f"\nGeneration completed in {elapsed:.2f} seconds")
    print(f"Expected improvement: 20-25% faster (target: 12-16 seconds)")
    
    if elapsed < 16:
        print("✓ Speed target achieved!")
    else:
        print("⚠ Speed target not met - check extensions are installed")
    
    return elapsed

def test_batch_generation():
    """Test batch generation speed"""
    api = SDWebUIAPI(Config.SD_WEBUI_HOST, Config.SD_WEBUI_TIMEOUT)
    
    test_prompts = [
        "space station orbiting Earth, cinematic",
        "underwater city with glowing lights, sci-fi",
        "mountain peak at sunrise, epic landscape"
    ]
    
    print(f"\nTesting batch generation ({len(test_prompts)} images)...")
    
    start = time.time()
    images = api.generate_batch(
        prompts=test_prompts,
        width=Config.SD_GENERATION_WIDTH,
        height=Config.SD_GENERATION_HEIGHT,
        steps=Config.SD_INFERENCE_STEPS,
        sampler=Config.SD_WEBUI_SAMPLER,
    )
    elapsed = time.time() - start
    
    print(f"Batch generation completed in {elapsed:.2f} seconds")
    print(f"Average per image: {elapsed/len(images):.2f} seconds")
    print(f"Generated {len(images)}/{len(test_prompts)} images successfully")
    
    return elapsed

if __name__ == "__main__":
    print("=" * 60)
    print("STABLE DIFFUSION EXTENSION SPEED TEST")
    print("=" * 60)
    
    # Test single image generation
    single_time = test_generation_speed()
    
    # Test batch generation
    batch_time = test_batch_generation()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Single image: {single_time:.2f}s")
    print(f"Batch (3 images): {batch_time:.2f}s")
    print(f"Average per image: {batch_time/3:.2f}s")
    
    if single_time < 16:
        print("✓ Extensions working - speed improvement detected!")
    else:
        print("⚠ No speed improvement detected - check extension installation")

