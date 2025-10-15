"""
PRODUCTION QUALITY CONFIGURATION PRESET

Use this for final videos you'll upload to YouTube.
Generation time: ~4-5 minutes for 30-second videos

To activate: Copy this file's contents over settings/config.py

BENEFITS:
- Maximum quality
- Full resolution (1080p)
- More scenes (4-5 for variety)
- Higher inference steps (20-25)
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
    # PRODUCTION MODE - OPTIMIZED FOR QUALITY
    # ==========================================

    # YouTube Shorts Specifications (FULL QUALITY)
    VIDEO_WIDTH = 1080   # Full HD width
    VIDEO_HEIGHT = 1920  # Full HD height
    VIDEO_ASPECT_RATIO = "9:16"
    VIDEO_FPS = 30  # Smooth 30 FPS

    # Duration limits
    MIN_DURATION_SECONDS = 15
    MAX_DURATION_SECONDS = 60
    DEFAULT_DURATION_SECONDS = 45

    # Video encoding (HIGH QUALITY - GPU ACCELERATED)
    VIDEO_CODEC = "h264_nvenc"  # GPU-accelerated encoding
    AUDIO_CODEC = "aac"
    VIDEO_CRF = 18  # Lower CRF = higher quality
    VIDEO_PRESET = "slow"  # Best quality GPU preset
    AUDIO_BITRATE = "192k"  # High quality audio
    FFMPEG_THREADS = 0
    
    # GPU Encoding Settings
    USE_GPU_ENCODING = True
    GPU_ENCODER_PRESET = "slow"  # Best quality
    FALLBACK_TO_CPU = True

    # Quality presets
    QUALITY_PRESETS = {
        "draft": {"crf": 26, "preset": "ultrafast"},
        "balanced": {"crf": 23, "preset": "veryfast"},
        "high": {"crf": 18, "preset": "fast"},
        "production": {"crf": 15, "preset": "medium"},  # BEST QUALITY
    }
    CURRENT_QUALITY_PRESET = "production"

    # Rendering backend
    RENDER_BACKEND = "ffmpeg"

    # AI Settings - BEST MODEL
    OLLAMA_MODEL = "llama3.2"  # Better quality than phi3
    OLLAMA_HOST = "http://localhost:11434"
    OLLAMA_MODELS_PATH = BASE_PATH / "models"

    # Stable Diffusion - SDXL HIGH QUALITY MODE
    STABLE_DIFFUSION_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
    SD_INFERENCE_STEPS = 30  # SDXL high quality: More steps for best results
    SD_GUIDANCE_SCALE = 7.5
    SD_DEVICE = "cuda"
    SD_LOW_MEMORY_MODE = True  # Still optimize memory
    SD_ATTENTION_SLICING = True
    SD_CPU_OFFLOAD = False
    
    # SDXL High Quality Resolution
    SD_GENERATION_WIDTH = 1024   # SDXL native resolution for best quality
    SD_GENERATION_HEIGHT = 1024  # Will be cropped/resized to 1080x1920

    # Video API Keys (fallback)
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
    PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

    # Voice Settings
    USE_LOCAL_TTS = False
    VOICE_SPEED = 1.0
    VOICE_LANGUAGE = "en"

    # Caption Settings (HIGH QUALITY)
    CAPTION_FONT_SIZE = 80  # Large for readability
    CAPTION_FONT_COLOR = "yellow"
    CAPTION_STROKE_COLOR = "black"
    CAPTION_STROKE_WIDTH = 4  # Thick outline
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

    # Watermark Settings
    WATERMARK_TEXT = "AI Generated"
    WATERMARK_FONT_SIZE = 16
    WATERMARK_POSITION = ("right", "top")
    WATERMARK_OPACITY = 0.6



