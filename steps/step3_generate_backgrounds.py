"""
STEP 3: AI BACKGROUND GENERATION

Uses Stable Diffusion to generate custom vertical backgrounds for YouTube Shorts.
Requires GPU. Generates 1080x1920 images from text descriptions.
"""

import os
import sys
import time
from pathlib import Path

import torch

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from settings.config import Config

# FFmpeg-based video processing (no MoviePy dependency)
import subprocess

# Import WebUI API helper
try:
    from helpers.sd_webui_api import SDWebUIAPI
    WEBUI_AVAILABLE = True
except ImportError:
    WEBUI_AVAILABLE = False
    print("Warning: WebUI API module not available")

# Set CUDA memory management for RTX 2060 (6GB)
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"


def check_gpu_available() -> bool:
    """Check if GPU is available for Stable Diffusion"""
    return torch.cuda.is_available()


def reset_gpu_state():
    """Completely reset GPU state to prevent stuck generations"""
    if torch.cuda.is_available():
        print("    Resetting GPU state...")
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        torch.cuda.synchronize()
        import gc
        gc.collect()
        
        # Check memory after reset
        memory_gb = torch.cuda.memory_allocated() / 1024**3
        print(f"    GPU Memory after reset: {memory_gb:.1f} GB")
        
        # If still high memory, force more aggressive cleanup
        if memory_gb > 2.0:
            print("    High memory detected, forcing aggressive cleanup...")
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            torch.cuda.synchronize()
            gc.collect()
            memory_gb = torch.cuda.memory_allocated() / 1024**3
            print(f"    GPU Memory after aggressive cleanup: {memory_gb:.1f} GB")


def generate_ai_backgrounds_webui(
    scene_descriptions: list, duration_per_scene: float = 3.0
) -> list:
    """
    Generate AI images using AUTOMATIC1111 WebUI API.
    This is faster and has more features than the diffusers method.

    Args:
        scene_descriptions: List of text descriptions for each scene
        duration_per_scene: How long each scene should display

    Returns:
        List of paths to generated images
    """
    
    print("Generating AI backgrounds with Stable Diffusion WebUI...")
    
    if not WEBUI_AVAILABLE:
        print("ERROR: WebUI API module not available")
        print("Falling back to diffusers method...")
        return generate_ai_backgrounds_diffusers(scene_descriptions, duration_per_scene)
    
    try:
        # Initialize WebUI API
        api = SDWebUIAPI(
            host=Config.SD_WEBUI_HOST,
            timeout=Config.SD_WEBUI_TIMEOUT
        )
        
        # OPTIMIZATION: Use configurable scene count for optimal performance
        max_scenes = getattr(Config, 'SD_MAX_SCENES', 2)
        optimized_scenes = scene_descriptions[:max_scenes]
        if len(scene_descriptions) > max_scenes:
            print(f"OPTIMIZATION: Reduced from {len(scene_descriptions)} to {max_scenes} scenes for speed")
        
        # Generate images
        image_paths = []
        temp_dir = Path(Config.TEMP_DIR)
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        for i, description in enumerate(optimized_scenes):
            print(f"\n[Scene {i+1}/{len(optimized_scenes)}]")
            
            # Optimize prompt for vertical format and YouTube Shorts
            vertical_prompt = (
                f"{description}, vertical composition, portrait orientation, "
                f"cinematic, high quality, detailed, vibrant colors, "
                f"mobile optimized, 9:16 aspect ratio"
            )
            
            # Generate image using WebUI API
            image = api.generate_image(
                prompt=vertical_prompt,
                negative_prompt="blurry, low quality, distorted, ugly, bad composition, horizontal",
                width=Config.SD_GENERATION_WIDTH,
                height=Config.SD_GENERATION_HEIGHT,
                steps=Config.SD_INFERENCE_STEPS,
                cfg_scale=Config.SD_GUIDANCE_SCALE,
                sampler=Config.SD_WEBUI_SAMPLER,
            )
            
            if image:
                # Upscale to final resolution if needed
                if Config.SD_GENERATION_WIDTH != Config.VIDEO_WIDTH or Config.SD_GENERATION_HEIGHT != Config.VIDEO_HEIGHT:
                    from PIL import Image as PILImage
                    image = image.resize((Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT), PILImage.Resampling.LANCZOS)
                    print(f"  ✓ Upscaled to {Config.VIDEO_WIDTH}x{Config.VIDEO_HEIGHT}")
                
                # Save image
                image_path = temp_dir / f"ai_background_{i}.png"
                image.save(image_path)
                image_paths.append(str(image_path))
                print(f"  ✓ Saved: {image_path.name}")
            else:
                print(f"  ✗ Failed to generate scene {i+1}")
        
        print(f"\n✓ Generated {len(image_paths)} AI backgrounds via WebUI")
        return image_paths
        
    except Exception as e:
        print(f"ERROR using WebUI API: {e}")
        print("Falling back to diffusers method...")
        return generate_ai_backgrounds_diffusers(scene_descriptions, duration_per_scene)


def generate_ai_backgrounds_diffusers(
    scene_descriptions: list, duration_per_scene: float = 3.0
) -> list:
    """
    Generate AI images using the diffusers library (fallback method).

    Args:
        scene_descriptions: List of text descriptions for each scene
        duration_per_scene: How long each scene should display

    Returns:
        List of paths to generated images
    """

    print("Generating AI backgrounds with Stable Diffusion (diffusers)...")

    # Check if GPU available
    device = "cuda" if check_gpu_available() else "cpu"
    
    # CRITICAL: Reset GPU state before starting generation
    if device == "cuda":
        reset_gpu_state()

    if device == "cpu":
        print("WARNING: No GPU detected. Stable Diffusion requires a GPU.")
        print("Options:")
        print("  1. Install a compatible NVIDIA GPU")
        print("  2. Use Google Colab for free GPU access")
        print("  3. Use stock videos instead (set USE_STOCK_VIDEOS=True)")
        print("\nSkipping AI background generation...")
        return []

    print(f"Using device: {device}")

    # Import SDXL pipeline (only if GPU available)
    try:
        from diffusers import DiffusionPipeline
    except ImportError:
        print("ERROR: diffusers package not installed")
        print("Install with: pip install diffusers transformers accelerate")
        return []

    # OPTIMIZATION: Reduce scene count from 5 to 3 for 40% memory reduction
    optimized_scenes = scene_descriptions[:3]
    if len(scene_descriptions) > 3:
        print(f"OPTIMIZATION: Reduced from {len(scene_descriptions)} to 3 scenes for memory efficiency")

    # Load SDXL model with context manager for cleanup
    print(f"Loading SDXL model: {Config.STABLE_DIFFUSION_MODEL}")
    print("This may take a few minutes on first run (downloading ~7GB SDXL model)...")

    pipe = None
    try:
        # Clear GPU cache before loading
        if device == "cuda":
            torch.cuda.empty_cache()
            print(
                f"GPU Memory before loading: {torch.cuda.memory_allocated() / 1024**3:.1f} GB"
            )

        pipe = DiffusionPipeline.from_pretrained(
            Config.STABLE_DIFFUSION_MODEL,
            torch_dtype=torch.float16,  # Use half precision to save memory
            use_safetensors=True,
            variant="fp16" if device == "cuda" else None,
        ).to(device)

        # Enable memory optimizations for 6GB GPU
        if Config.SD_ATTENTION_SLICING:
            pipe.enable_attention_slicing(
                1
            )  # Slice size of 1 for maximum memory savings
            print("Enabled attention slicing for memory optimization")

        if Config.SD_LOW_MEMORY_MODE:
            # Enable additional memory optimizations
            pipe.enable_vae_slicing()
            print("Enabled VAE slicing for memory optimization")

        print(
            f"GPU Memory after loading: {torch.cuda.memory_allocated() / 1024**3:.1f} GB"
        )

        # Generate images with optimized settings
        image_paths = []
        temp_dir = Path(Config.TEMP_DIR)
        temp_dir.mkdir(parents=True, exist_ok=True)

        for i, description in enumerate(optimized_scenes):
            # CRITICAL: Clear GPU memory before each generation
            if device == "cuda":
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
                import gc
                gc.collect()
                print(f"    GPU Memory cleared before scene {i+1}")
            print(
                f"  Generating scene {i+1}/{len(optimized_scenes)}: {description[:50]}..."
            )

            # Optimize prompt for vertical format and YouTube Shorts
            vertical_prompt = (
                f"{description}, vertical composition, portrait orientation, "
                f"cinematic, high quality, detailed, vibrant colors, "
                f"mobile optimized, 9:16 aspect ratio"
            )

            try:
                # OPTIMIZATION: More aggressive GPU cache clearing
                if device == "cuda":
                    torch.cuda.empty_cache()
                    torch.cuda.ipc_collect()  # Additional cleanup
                    print(
                        f"    GPU Memory before generation: {torch.cuda.memory_allocated() / 1024**3:.1f} GB"
                    )
                    
                    # Check if GPU memory is too high (prevent stuck state)
                    gpu_memory_gb = torch.cuda.memory_allocated() / 1024**3
                    if gpu_memory_gb > 5.0:
                        print(f"    WARNING: High GPU memory usage ({gpu_memory_gb:.1f} GB)")
                        print("    Clearing cache to prevent stuck state...")
                        torch.cuda.empty_cache()
                        torch.cuda.ipc_collect()
                        import gc
                        gc.collect()

                # OPTIMIZATION: Use reduced inference steps
                inference_steps = Config.SD_INFERENCE_STEPS
                print(f"    Using {inference_steps} inference steps (optimized)")

                # SDXL: Generate at optimized resolution for quality and speed
                gen_width = getattr(Config, 'SD_GENERATION_WIDTH', 1024)
                gen_height = getattr(Config, 'SD_GENERATION_HEIGHT', 1024)
                
                if gen_width != Config.VIDEO_WIDTH or gen_height != Config.VIDEO_HEIGHT:
                    print(f"    SDXL generating at {gen_width}x{gen_height}, will resize to {Config.VIDEO_WIDTH}x{Config.VIDEO_HEIGHT}")

                # SDXL: Use optimized step count (minimum 10 for quality)
                if inference_steps < 10:
                    inference_steps = 10  # SDXL minimum for quality
                    print(f"    SDXL minimum steps set to {inference_steps} for quality")
                
                # Generate image with optimized settings
                print(f"    Starting generation (this should take ~10-15 seconds)...")
                start_gen_time = time.time()
                
                image = pipe(
                    vertical_prompt,
                    height=gen_height,
                    width=gen_width,
                    num_inference_steps=inference_steps,
                    guidance_scale=Config.SD_GUIDANCE_SCALE,
                    negative_prompt="blurry, low quality, distorted, ugly, bad composition",
                ).images[0]
                
                gen_time = time.time() - start_gen_time
                print(f"    Generation completed in {gen_time:.1f} seconds")
                
                # Upscale to final resolution if needed
                if gen_width != Config.VIDEO_WIDTH or gen_height != Config.VIDEO_HEIGHT:
                    from PIL import Image
                    image = image.resize((Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT), Image.Resampling.LANCZOS)
                    print(f"    Upscaled to {Config.VIDEO_WIDTH}x{Config.VIDEO_HEIGHT}")

                # Save to temp folder on D drive
                image_path = temp_dir / f"ai_background_{i}.png"
                image.save(image_path)
                image_paths.append(str(image_path))

                print(f"    Saved: {image_path.name}")

                # OPTIMIZATION: Aggressive memory cleanup after each generation
                if device == "cuda":
                    torch.cuda.empty_cache()
                    torch.cuda.ipc_collect()
                    # Force garbage collection
                    import gc
                    gc.collect()

                # Clear image reference
                del image
                
                # CRITICAL: Add small delay between generations to prevent stuck state
                if device == "cuda" and i < len(optimized_scenes) - 1:
                    print("    Brief pause between generations...")
                    time.sleep(1)  # 1 second pause between images

            except Exception as e:
                print(f"    ERROR generating scene {i+1}: {e}")
                # Clear memory on error
                if device == "cuda":
                    torch.cuda.empty_cache()
                    torch.cuda.ipc_collect()
                continue

        print(f"Generated {len(image_paths)} AI backgrounds")

        return image_paths

    except Exception as e:
        print(f"ERROR loading SDXL: {e}")
        print("SDXL model will be downloaded from Hugging Face on first run")
        print("This is a larger download (~7GB) but provides much better quality")
        return []

    finally:
        # OPTIMIZATION: Explicit SDXL model cleanup and memory release
        if pipe is not None:
            print("Cleaning up SDXL pipeline...")
            try:
                # Move pipeline off GPU
                if device == "cuda":
                    pipe = pipe.to("cpu")
                    del pipe
                    torch.cuda.empty_cache()
                    torch.cuda.ipc_collect()
                    print(f"GPU Memory after cleanup: {torch.cuda.memory_allocated() / 1024**3:.1f} GB")
            except Exception as cleanup_error:
                print(f"Warning: Error during cleanup: {cleanup_error}")
        
        # Force garbage collection
        import gc
        gc.collect()


def generate_ai_backgrounds(
    scene_descriptions: list, duration_per_scene: float = 3.0
) -> list:
    """
    Generate AI images for each scene using Stable Diffusion.
    
    Automatically chooses between WebUI API or diffusers based on config.

    Args:
        scene_descriptions: List of text descriptions for each scene
        duration_per_scene: How long each scene should display

    Returns:
        List of paths to generated images
    """
    
    # Choose method based on config
    method = getattr(Config, 'SD_METHOD', 'diffusers').lower()
    
    if method == 'webui':
        print("Using AUTOMATIC1111 WebUI API method")
        return generate_ai_backgrounds_webui(scene_descriptions, duration_per_scene)
    else:
        print("Using diffusers library method")
        return generate_ai_backgrounds_diffusers(scene_descriptions, duration_per_scene)


def images_to_video_clips(image_paths: list, duration_per_image: float = 3.0):
    """
    Convert static AI images to video clips with Ken Burns effect using FFmpeg.
    
    Creates video files with subtle zoom/pan motion for engaging YouTube Shorts backgrounds.

    Args:
        image_paths: List of image file paths
        duration_per_image: How long each image shows

    Returns:
        List of video file paths with Ken Burns effect
    """

    if not image_paths:
        print("WARNING: No images to convert")
        return []

    print(f"Converting {len(image_paths)} images to video clips with Ken Burns effect...")

    video_clips = []
    temp_dir = Path("temp_files")
    temp_dir.mkdir(exist_ok=True)

    for i, img_path in enumerate(image_paths):
        try:
            print(f"  Creating Ken Burns clip {i+1}: {duration_per_image}s")
            
            # Output video path
            video_path = temp_dir / f"ken_burns_clip_{i}.mp4"
            
            # FFmpeg command for Ken Burns effect (stronger zoom & gentle pan)
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-t", str(duration_per_image),
                "-i", str(img_path),
                "-vf", f"scale=iw*1.12:ih*1.12,"
                      f"zoompan=z='min(zoom+0.0025,1.12)':"
                      f"d={int(duration_per_image * Config.VIDEO_FPS)}:"
                      f"x='iw/2-(iw/zoom/2)':"
                      f"y='ih/2-(ih/zoom/2)':"
                      f"s={Config.VIDEO_WIDTH}x{Config.VIDEO_HEIGHT}",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-r", str(Config.VIDEO_FPS),
                str(video_path)
            ]
            
            # Execute FFmpeg command
            print(f"    Running FFmpeg for Ken Burns effect...")
            result = subprocess.run(cmd, text=True)
            
            if result.returncode == 0:
                video_clips.append(str(video_path))
                print(f"    Ken Burns effect applied (zoom: 1.05x)")
            else:
                print(f"    FFmpeg failed with return code: {result.returncode}")
                # Fallback: create static video
                video_clips.append(_create_static_video_fallback(img_path, duration_per_image, temp_dir, i))
                print(f"    Fallback: Static video created")

        except Exception as e:
            print(f"  ERROR creating Ken Burns clip from {img_path}: {e}")
            # Fallback: create static video
            try:
                video_path = _create_static_video_fallback(img_path, duration_per_image, temp_dir, i)
                video_clips.append(video_path)
                print(f"    Fallback: Static video created")
            except Exception as fallback_error:
                print(f"    ERROR: Could not create fallback video: {fallback_error}")
                continue

    print(f"Created {len(video_clips)} video clips with Ken Burns effect")
    return video_clips


def _create_static_video_fallback(img_path: str, duration: float, temp_dir: Path, index: int) -> str:
    """Create static video from image as fallback."""
    
    video_path = temp_dir / f"static_clip_{index}.mp4"
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(img_path),
        "-t", str(duration),
        "-vf", f"scale={Config.VIDEO_WIDTH}:{Config.VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,"
               f"pad={Config.VIDEO_WIDTH}:{Config.VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-r", str(Config.VIDEO_FPS),
        str(video_path)
    ]
    
    print(f"    Creating static video fallback...")
    result = subprocess.run(cmd, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Static video creation failed with return code: {result.returncode}")
    
    return str(video_path)


if __name__ == "__main__":
    # Test this module
    print("=" * 60)
    print("TESTING AI BACKGROUND GENERATION")
    print("=" * 60)

    # Check GPU
    if check_gpu_available():
        print(f"\nGPU Available: YES")
        print(f"GPU Name: {torch.cuda.get_device_name(0)}")
        print(
            f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB"
        )
    else:
        print(f"\nGPU Available: NO")
        print("Stable Diffusion requires a GPU")
        print("Exiting test...")
        sys.exit(0)

    # Test scene generation
    test_scenes = [
        "Ocean waves at sunset, cinematic lighting",
        "City skyline at night with neon lights",
        "Mountain landscape with dramatic clouds",
    ]

    print(f"\nGenerating {len(test_scenes)} test scenes...")
    images = generate_ai_backgrounds(test_scenes, duration_per_scene=3.0)

    if images:
        print(f"\nGenerated {len(images)} backgrounds")
        print("\nTesting video clip conversion...")
        clips = images_to_video_clips(images, duration_per_image=3.0)
        print(f"Created {len(clips)} video clips")
    else:
        print("\nNo images generated (check errors above)")
