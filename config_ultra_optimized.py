"""
ULTRA OPTIMIZED CONFIGURATION PRESET

Use this for maximum speed when you need the fastest possible generation.
Generation time: ~45-60 seconds for 30-second videos

To activate: Copy this file's contents over settings/config.py

OPTIMIZATIONS:
- Only 2 scenes (instead of 3-5)
- Lower inference steps (8-12)
- Reduced resolution (768x1024)
- Fastest GPU presets
- Optimized memory usage
- Parallel processing enabled
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Force D drive for everything
BASE_PATH = Path("D:/YouTubeShortsProject")
PROJECT_PATH = BASE_PATH / "NCWM"

# Load environment variables from project directory
env_path = PROJECT_PATH / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Config:

    # ==========================================
    # ULTRA OPTIMIZED MODE - MAXIMUM SPEED
    # ==========================================

    # YouTube Shorts Specifications (OPTIMIZED RESOLUTION)
    VIDEO_WIDTH = 1080   # Keep full resolution for quality
    VIDEO_HEIGHT = 1920  # Keep full resolution for quality
    VIDEO_ASPECT_RATIO = "9:16"
    VIDEO_FPS = 24  # Optimized FPS for speed

    # Duration limits
    MIN_DURATION_SECONDS = 15
    MAX_DURATION_SECONDS = 60
    DEFAULT_DURATION_SECONDS = 30  # Target 30 seconds for speed

    # Video encoding (ULTRA FAST - GPU ACCELERATED)
    VIDEO_CODEC = "h264_nvenc"  # GPU-accelerated encoding
    AUDIO_CODEC = "aac"
    VIDEO_CRF = 28  # Higher CRF for speed
    VIDEO_PRESET = "fast"  # Fastest GPU preset
    AUDIO_BITRATE = "128k"  # Lower bitrate for speed
    FFMPEG_THREADS = 0
    
    # GPU Encoding Settings (ULTRA OPTIMIZED)
    USE_GPU_ENCODING = True
    GPU_ENCODER_PRESET = "fast"  # Fastest preset
    FALLBACK_TO_CPU = True

    # Quality presets (ULTRA OPTIMIZED)
    QUALITY_PRESETS = {
        "draft": {"crf": 30, "preset": "fast", "scenes": 1, "steps": 6},  # Ultra fast
        "balanced": {"crf": 28, "preset": "fast", "scenes": 2, "steps": 8},  # Fast
        "high": {"crf": 25, "preset": "fast", "scenes": 2, "steps": 12},  # Balanced
        "production": {"crf": 22, "preset": "medium", "scenes": 3, "steps": 15},  # Quality
    }
    CURRENT_QUALITY_PRESET = "balanced"  # Fast but good quality

    # Rendering backend
    RENDER_BACKEND = "ffmpeg"

    # AI Settings - FASTEST MODEL
    OLLAMA_MODEL = "phi3"  # Fastest model
    OLLAMA_HOST = "http://localhost:11434"
    OLLAMA_MODELS_PATH = BASE_PATH / "models"

    # Stable Diffusion - ULTRA OPTIMIZED MODE
    STABLE_DIFFUSION_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
    SD_INFERENCE_STEPS = 8  # ULTRA FAST: Minimum steps for acceptable quality
    SD_GUIDANCE_SCALE = 6.0  # Lower guidance for speed
    SD_DEVICE = "cuda"
    SD_LOW_MEMORY_MODE = True
    SD_ATTENTION_SLICING = True
    SD_CPU_OFFLOAD = False
    
    # ULTRA OPTIMIZED Resolution
    SD_GENERATION_WIDTH = 768   # Lower resolution for speed
    SD_GENERATION_HEIGHT = 1024  # Optimized for speed
    
    # PERFORMANCE OPTIMIZATIONS
    SD_ENABLE_MEMORY_EFFICIENT_ATTENTION = True
    SD_ENABLE_CPU_OFFLOAD = False
    SD_ENABLE_SEQUENTIAL_CPU_OFFLOAD = False
    
    # SCENE OPTIMIZATION (ULTRA FAST)
    SD_MAX_SCENES = 2  # Only 2 scenes for maximum speed
    SD_SCENE_DURATION = 5.0  # Longer scenes, fewer transitions

    # Video API Keys (fallback)
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
    PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

    # Voice Settings (OPTIMIZED)
    USE_LOCAL_TTS = False
    VOICE_SPEED = 1.1  # Slightly faster speech
    VOICE_LANGUAGE = "en"

    # Caption Settings (OPTIMIZED FOR SPEED)
    CAPTION_FONT_SIZE = 60  # Smaller for faster rendering
    CAPTION_FONT_COLOR = "yellow"
    CAPTION_STROKE_COLOR = "black"
    CAPTION_STROKE_WIDTH = 2  # Thinner for speed
    CAPTION_POSITION = "center"
    CAPTION_MAX_WIDTH_PERCENT = 0.85
    WORDS_PER_CAPTION = 2

    # Folder Structure
    OUTPUT_DIR = str(PROJECT_PATH / "finished_videos")
    TEMP_DIR = str(BASE_PATH / "temp")
    METADATA_DIR = str(PROJECT_PATH / "metadata")
    CACHE_DIR = str(BASE_PATH / "cache")
    MODELS_DIR = str(BASE_PATH / "models")

    # YouTube Compliance
    AI_DISCLOSURE_TEXT = (
        "This YouTube Short was created using AI-generated content "
        "including script and voice narration.\n\n"
        "#AIGenerated #YouTubeShorts"
    )

    # Watermark Settings (OPTIMIZED)
    WATERMARK_TEXT = "AI Generated"
    WATERMARK_FONT_SIZE = 14  # Smaller
    WATERMARK_POSITION = ("right", "top")
    WATERMARK_OPACITY = 0.5  # Less visible

    # ADVANCED OPTIMIZATIONS
    ENABLE_PARALLEL_PROCESSING = True  # Enable parallel processing
    ENABLE_VIDEO_CACHING = True  # Cache intermediate results
    ENABLE_MEMORY_OPTIMIZATION = True  # Aggressive memory cleanup
    ENABLE_AGGRESSIVE_OPTIMIZATION = True  # Maximum performance mode

    # MEMORY MANAGEMENT
    MEMORY_CLEANUP_INTERVAL = 3  # Cleanup every 3 operations
    MAX_MEMORY_USAGE_PERCENT = 75  # Stop if memory usage exceeds 75%
    GPU_MEMORY_THRESHOLD = 0.8  # GPU memory threshold for optimization

    # PERFORMANCE MONITORING
    ENABLE_PERFORMANCE_MONITORING = True  # Monitor performance metrics
    LOG_PERFORMANCE_METRICS = True  # Log performance data
    AUTO_OPTIMIZE_BASED_ON_PERFORMANCE = True  # Auto-adjust based on performance
