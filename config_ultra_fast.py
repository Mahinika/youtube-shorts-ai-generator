"""
ULTRA FAST CONFIGURATION PRESET

Use this for maximum speed when you need quick previews or batch production.
Generation time: ~60-80 seconds for 30-second videos

To activate: Copy this file's contents over settings/config.py
Or import this config in your code.

TRADE-OFFS:
- Lower quality (but still acceptable for previews)
- Fewer scenes (2 instead of 3)
- Lower resolution (720p instead of 1080p)
- Fewer inference steps (8-10 instead of 15)
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
    # ULTRA FAST MODE - OPTIMIZED FOR SPEED
    # ==========================================

    # YouTube Shorts Specifications (REDUCED RESOLUTION)
    VIDEO_WIDTH = 720   # Reduced from 1080 for faster rendering
    VIDEO_HEIGHT = 1280  # Reduced from 1920 for faster rendering
    VIDEO_ASPECT_RATIO = "9:16"  # Vertical orientation
    VIDEO_FPS = 20  # Reduced from 24 for faster encoding

    # Duration limits
    MIN_DURATION_SECONDS = 15
    MAX_DURATION_SECONDS = 60
    DEFAULT_DURATION_SECONDS = 30  # Target 30 seconds for speed

    # Video encoding (ULTRA FAST)
    VIDEO_CODEC = "libx264"
    AUDIO_CODEC = "aac"
    VIDEO_CRF = 28  # Higher CRF = lower quality but MUCH faster
    VIDEO_PRESET = "ultrafast"  # Fastest encoding preset
    AUDIO_BITRATE = "128k"  # Lower bitrate for speed
    FFMPEG_THREADS = 0  # Use all CPU cores

    # Quality presets
    QUALITY_PRESETS = {
        "draft": {"crf": 28, "preset": "ultrafast"},
        "balanced": {"crf": 26, "preset": "veryfast"},
        "high": {"crf": 23, "preset": "fast"},
        "production": {"crf": 18, "preset": "medium"},
    }
    CURRENT_QUALITY_PRESET = "draft"

    # Rendering backend
    RENDER_BACKEND = "ffmpeg"  # FFmpeg is faster

    # AI Settings - FASTEST MODEL
    OLLAMA_MODEL = "phi3"  # Faster than llama3.2
    OLLAMA_HOST = "http://localhost:11434"
    OLLAMA_MODELS_PATH = BASE_PATH / "models"

    # Stable Diffusion - ULTRA FAST MODE
    STABLE_DIFFUSION_MODEL = "runwayml/stable-diffusion-v1-5"
    SD_INFERENCE_STEPS = 8  # MINIMUM for acceptable quality
    SD_GUIDANCE_SCALE = 7.0  # Slightly lower for speed
    SD_DEVICE = "cuda"
    SD_LOW_MEMORY_MODE = True
    SD_ATTENTION_SLICING = True
    SD_CPU_OFFLOAD = False

    # Video API Keys (fallback)
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
    PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

    # Voice Settings
    USE_LOCAL_TTS = False  # gTTS is fast enough
    VOICE_SPEED = 1.0
    VOICE_LANGUAGE = "en"

    # Caption Settings (SIMPLIFIED FOR SPEED)
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

    # Watermark Settings
    WATERMARK_TEXT = "AI Generated"
    WATERMARK_FONT_SIZE = 14  # Smaller
    WATERMARK_POSITION = ("right", "top")
    WATERMARK_OPACITY = 0.5  # Less visible



