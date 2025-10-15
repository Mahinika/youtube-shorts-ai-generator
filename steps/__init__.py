"""
Steps Module

Contains the 5 main steps to create a YouTube Short:
1. Write script with AI (Ollama)
2. Create voice narration (gTTS)
3. Generate AI backgrounds (Stable Diffusion)
4. Add karaoke captions
5. Combine everything into final video
"""

from .step1_write_script import (
    estimate_script_duration,
    generate_word_timestamps,
    write_script_with_ollama,
)
from .step2_create_voice import create_voice_narration
from .step3_generate_backgrounds import (
    check_gpu_available,
    generate_ai_backgrounds,
    images_to_video_clips,
)
from .step4_add_captions import create_shorts_captions
from .step5_combine_everything import combine_into_final_video

__all__ = [
    "write_script_with_ollama",
    "estimate_script_duration",
    "generate_word_timestamps",
    "create_voice_narration",
    "generate_ai_backgrounds",
    "images_to_video_clips",
    "check_gpu_available",
    "create_shorts_captions",
    "combine_into_final_video",
]
