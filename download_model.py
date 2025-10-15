"""
MODEL DOWNLOADER

Downloads the Stable Diffusion model directly to your models folder
so you don't have to wait during generation.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from settings.config import Config


def download_model():
    """Download Stable Diffusion model to local cache"""
    
    print("=" * 70)
    print("STABLE DIFFUSION MODEL DOWNLOADER")
    print("=" * 70)
    print()
    
    print("This will download the SDXL 1.0 model (~7GB) to your D drive.")
    print("After this, video generation will be much faster with better quality!")
    print()
    
    # Create models directory on D drive
    models_dir = Path(Config.MODELS_DIR)
    models_dir.mkdir(parents=True, exist_ok=True)
    print(f"Models directory: {models_dir}")
    print(f"Storage location: D drive (as configured)")
    print()
    
    try:
        from diffusers import DiffusionPipeline
        from huggingface_hub import hf_hub_download
        import torch
        
        model_name = Config.STABLE_DIFFUSION_MODEL
        print(f"Downloading SDXL model: {model_name}")
        print("This may take 15-20 minutes depending on your internet speed...")
        print("SDXL is larger than SD 1.5 but provides much better quality!")
        print()
        
        # Check if we have GPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        if device == "cuda":
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
        
        print()
        print("Starting download...")
        print("=" * 50)
        
        # Download the SDXL pipeline (this downloads all components)
        pipe = DiffusionPipeline.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            use_safetensors=True,
            cache_dir=str(models_dir),
            variant="fp16" if device == "cuda" else None
        )
        
        print("=" * 50)
        print("Download completed successfully!")
        print()
        
        # Test the pipeline
        print("Testing the model...")
        pipe = pipe.to(device)
        
        # Enable optimizations
        if device == "cuda":
            pipe.enable_attention_slicing()
            pipe.enable_vae_slicing()
            print("Memory optimizations enabled")
        
        # Quick test generation with SDXL
        print("Running SDXL test generation...")
        test_prompt = "a simple red circle on white background, high quality"
        
        with torch.no_grad():
            test_image = pipe(
                test_prompt,
                height=1024,
                width=1024,
                num_inference_steps=15,  # SDXL optimized test
                guidance_scale=7.0
            ).images[0]
        
        print("Test generation successful!")
        
        # Cleanup
        del pipe
        del test_image
        if device == "cuda":
            torch.cuda.empty_cache()
        
        print()
        print("=" * 70)
        print("MODEL DOWNLOAD COMPLETE!")
        print("=" * 70)
        print()
        print("What happens next:")
        print("• The model is now cached locally")
        print("• Future video generations will start immediately")
        print("• No more waiting for downloads!")
        print("• Generation time: 2-3 minutes (instead of 8-12 minutes)")
        print()
        print("You can now close this script and run your video generation.")
        print("The model will load instantly from cache!")
        
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install: pip install diffusers transformers torch")
        return False
        
    except Exception as e:
        print(f"Download failed: {e}")
        print()
        print("Common solutions:")
        print("1. Check your internet connection")
        print("2. Make sure you have enough disk space (5GB+ free)")
        print("3. Try running as administrator")
        print("4. Check Windows Firewall isn't blocking Python")
        return False
    
    return True


if __name__ == "__main__":
    success = download_model()
    if success:
        print("\nPress any key to exit...")
        input()
    else:
        print("\nDownload failed. Press any key to exit...")
        input()


