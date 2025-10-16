"""
STEP 2: CREATE VOICE

Converts script text into speech audio using free TTS.
Outputs to D drive temp folder.
"""

import sys
from pathlib import Path
import re
from typing import Dict, Any, Optional, Union

from gtts import gTTS
from pydub import AudioSegment
import asyncio
import tempfile
try:
    import edge_tts  # optional, free, reliable
except Exception:  # pragma: no cover
    edge_tts = None

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from settings.config import Config
from utils.error_handler import (
    error_handler, AIGenerationError, ValidationError, 
    validate_duration, create_error_context, log_error_with_context
)
from utils.validation_utils import (
    validate_string_input, validate_numeric_input, validate_audio_specs
)
from utils.logging_utils import get_logger

logger = get_logger("voice_generation")


def clean_narrative_text(text: str) -> str:
    """
    Clean narrative text by removing sound effects, emojis, and other non-speech elements.
    
    Args:
        text: Raw script text that may contain sound effects and emojis
        
    Returns:
        Cleaned text suitable for text-to-speech
    """
    # Remove sound effects in parentheses like (whoosh), (boom), etc.
    text = re.sub(r'\([^)]*\)', '', text)
    
    # Remove sound effects in brackets like [SFX: whoosh], [SOUND: boom], etc.
    text = re.sub(r'\[[^\]]*\]', '', text)
    
    # Remove emojis and other Unicode symbols
    # This regex matches most emoji ranges and symbols
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"  # enclosed characters
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
        "\U00002600-\U000026FF"  # miscellaneous symbols
        "\U00002700-\U000027BF"  # dingbats
        "]+", 
        flags=re.UNICODE
    )
    text = emoji_pattern.sub('', text)
    
    # Remove multiple spaces and clean up
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text


@error_handler("voice_generation", reraise=True)
def create_voice_narration(script_text: str, voice_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Convert script text to voice audio using simplified TTS manager.

    Args:
        script_text: The narrative script
        voice_name: Optional voice name override

    Returns:
        Dictionary with 'path' and 'duration' keys
    """
    from utils.tts_manager import create_voice_narration as tts_create_voice
    
    # Validate input
    script_text = validate_string_input(
        script_text, "script_text", min_length=1, max_length=2000
    )
    
    logger.info("Creating voice narration...")
    
    try:
        result = tts_create_voice(script_text, voice_name)
        
        # Validate result
        if not result or 'duration' not in result:
            raise AIGenerationError(
                "TTS generation returned invalid result",
                error_code="INVALID_TTS_RESULT",
                details={"result": result}
            )
        
        # Validate duration
        duration = validate_duration(result['duration'], min_duration=1.0, max_duration=60.0)
        result['duration'] = duration
        
        logger.info(f"Voice created: {duration:.1f} seconds")
        return result
        
    except Exception as e:
        context = create_error_context("voice_generation", script_length=len(script_text), voice_name=voice_name)
        log_error_with_context(logger, e, context)
        raise AIGenerationError(
            f"Voice generation failed: {e}",
            error_code="VOICE_GENERATION_FAILED",
            details={"script_length": len(script_text), "voice_name": voice_name}
        )


if __name__ == "__main__":
    # Test this module
    test_script = "This is a test of the voice narration system (whoosh) 🚀. It should create an audio file on the D drive [SFX: beep]."
    result = create_voice_narration(test_script)

    print("\n" + "=" * 60)
    print("TEST RESULT:")
    print("=" * 60)
    print(f"Audio file: {result['path']}")
    print(f"Duration: {result['duration']:.1f} seconds")

    # Verify file exists
    if Path(result["path"]).exists():
        print("File exists: YES")
    else:
        print("File exists: NO")
