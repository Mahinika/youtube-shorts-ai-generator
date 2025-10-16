"""
SETTINGS - All configuration in one place

Everything runs from D drive for optimal storage management.
All paths point to D:/YouTubeShortsProject
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

    # YouTube Shorts Official Specifications
    VIDEO_DURATION = 60  # seconds (YouTube Shorts max)
    VIDEO_WIDTH = 1080
    VIDEO_HEIGHT = 1920
    VIDEO_FPS = 30

    # AI Provider Selection
    AI_PROVIDER = "groq"  # Options: "grok", "groq", "ollama"

    # Script Generation Mode
    # Options: "auto" (detects story vs educational), "story" (pure storytelling), "educational" (facts and data), "mixed" (both)
    SCRIPT_GENERATION_MODE = "story"  # Force pure storytelling mode

    # Grok AI Settings (xAI) - Internet-Connected, Smart
    # Available Grok Models (choose the best for your needs):
    # "grok-beta" - Latest model with best reasoning (recommended for quality)
    # "grok-2" - Previous generation, good balance
    # "grok-3" - Current default, reliable performance
    # "grok-4-fast" - Newest, optimized for speed and efficiency (2M context, 344 tokens/sec)
    GROK_API_KEY = os.getenv("GROK_API_KEY", "")
    GROK_MODEL = "grok-beta"
    GROK_API_BASE = "https://api.x.ai/v1"
    GROK_TEMPERATURE = 0.8
    GROK_MAX_TOKENS = 1000
    
    # Token Optimization Settings
    GROK_USE_EFFICIENT_MODE = True  # Enable token-efficient generation
    GROK_OPTIMIZE_RESPONSES = True  # Auto-optimize response length

    # Groq Settings (Free, Fast, Internet-Connected)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = "llama-3.3-70b-versatile"
    GROQ_TEMPERATURE = 0.8
    GROQ_MAX_TOKENS = 1000
    
    # Template-based Fallback System (No Internet Required)
    USE_TEMPLATE_FALLBACK = True
    SCRIPT_TARGET_WORDS = 110
    SCRIPT_TEMPLATE_PATH = "prompts/template_scripts"

    # TTS Settings
    VOICE_LANGUAGE = "en"
    
    # TTS Provider Selection
    TTS_PROVIDER = "piper"  # Options: "piper", "edge", "gtts" (piper recommended for quality)
    
    # Piper TTS Settings (High Quality, Local, Free)
    PIPER_MODEL_PATH = r"D:\YouTubeShortsProject\NCWM\models\piper\en-us-amy-medium.onnx"
    PIPER_CONFIG_PATH = r"D:\YouTubeShortsProject\NCWM\models\piper\en-us-amy-medium.onnx.json"
    PIPER_USE_CUDA = False  # Set to True if you have CUDA GPU for faster generation
    
    # Edge TTS Settings (Fallback)
    EDGE_VOICE_NAME = "en-US-AriaNeural"
    EDGE_VOICE_RATE = "+0%"
    EDGE_VOICE_PITCH = "+0Hz"
    EDGE_VOICE_VOLUME = "+0%"

    # Stable Diffusion Settings
    SD_METHOD = "webui"  # Options: "webui", "diffusers"
    SD_WEBUI_URL = "http://127.0.0.1:7860"
    SD_MODEL_NAME = "sd_xl_base_1.0.safetensors"
    SD_INFERENCE_STEPS = 12
    SD_GUIDANCE_SCALE = 7.5
    SD_WIDTH = 1024
    SD_HEIGHT = 1024
    SD_MAX_SCENES = 3
    SD_USE_AI_PROMPT_OPTIMIZER = True
    SD_PROMPT_OPTIMIZER_PROVIDER = "groq"

    # Quality presets for different use cases
    QUALITY_PRESETS = {
        "draft": {"crf": 26, "preset": "ultrafast"},  # Fast preview (optimized)
        "balanced": {"crf": 23, "preset": "veryfast"},  # Default
        "high": {"crf": 18, "preset": "fast"},  # Better quality
        "production": {"crf": 15, "preset": "medium"},  # Best quality
    }
    CURRENT_QUALITY_PRESET = "production"

    # Rendering backend: "ffmpeg" (recommended) or "moviepy"
    RENDER_BACKEND = "ffmpeg"

    # GPU Encoding Settings
    USE_GPU_ENCODING = True
    GPU_ENCODER = "h264_nvenc"  # Options: "h264_nvenc", "hevc_nvenc"
    GPU_PRESET = "fast"
    GPU_RC = "cbr"
    GPU_BITRATE = "5M"
    GPU_MAX_BITRATE = "8M"
    GPU_GOP_SIZE = 30

    # Advanced GPU Settings
    NVENC_PRESET = "fast"
    NVENC_RC = "cbr"
    NVENC_BITRATE = "5M"
    NVENC_MAX_BITRATE = "8M"
    NVENC_GOP_SIZE = 30

    # Caption Settings
    CAPTION_FONT_SIZE = 52
    CAPTION_FONT_COLOR = "white"
    CAPTION_BACKGROUND_COLOR = "black"
    CAPTION_POSITION = "center"
    CAPTION_MAX_WIDTH_PERCENT = 0.85
    WORDS_PER_CAPTION = 3

    # Folder Structure - ALL ON D DRIVE
    # Using raw strings (r"...") to prevent Unicode escape errors with backslashes
    OUTPUT_DIR = r"D:\YouTubeShortsProject\NCWM\finished_videos"
    TEMP_DIR = r"D:\YouTubeShortsProject\temp"
    METADATA_DIR = r"D:\YouTubeShortsProject\NCWM\metadata"
    CACHE_DIR = r"D:\YouTubeShortsProject\cache"
    MODELS_DIR = r"D:\YouTubeShortsProject\models"

    # YouTube Compliance
    AI_DISCLOSURE_TEXT = "This YouTube Short was created using AI-generated content including script and voice narration.\n\n#AIGenerated #YouTubeShorts"

    # Watermark Settings
    WATERMARK_TEXT = "AI Generated"
    WATERMARK_FONT_SIZE = 16
    WATERMARK_POSITION = ('right', 'top')

    # Video Settings
    VIDEO_PRESET = "fast"
    VIDEO_CRF = 23
    WATERMARK_POSITION_MODE = "top-right"

    # Performance Settings
    MAX_CONCURRENT_OPERATIONS = 2
    ENABLE_CACHING = True
    CACHE_EXPIRY_HOURS = 24

    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "logs/script_generation.log"
    ENABLE_DEBUG_LOGGING = False

    # Development Settings
    DEBUG_MODE = False
    VERBOSE_OUTPUT = True
    SAVE_INTERMEDIATE_FILES = False

    # Error Handling
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 2
    FALLBACK_ON_ERROR = True

    # Memory Management
    MAX_MEMORY_USAGE_PERCENT = 80
    CLEANUP_TEMP_FILES = True
    ENABLE_MEMORY_OPTIMIZATION = True

    # Network Settings
    REQUEST_TIMEOUT = 30
    MAX_CONCURRENT_REQUESTS = 5
    ENABLE_RATE_LIMITING = True

    # Security
    ENABLE_SSL_VERIFICATION = True
    SANITIZE_INPUTS = True
    LOG_SECURITY_EVENTS = True
