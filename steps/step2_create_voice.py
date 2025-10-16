"""
STEP 2: CREATE VOICE

Converts script text into speech audio using free TTS.
Outputs to D drive temp folder.
"""

import sys
from pathlib import Path
import re

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


def create_voice_narration(script_text: str, voice_name: str | None = None) -> dict:
    """
    Convert script text to voice audio using simplified TTS manager.

    Args:
        script_text: The narrative script
        voice_name: Optional voice name override

    Returns:
        Dictionary with 'path' and 'duration' keys
    """
    from utils.tts_manager import create_voice_narration as tts_create_voice
    
    print("Creating voice narration...")
    
    try:
        result = tts_create_voice(script_text, voice_name)
        print(f"Voice created: {result['duration']:.1f} seconds")
        return result
    except Exception as e:
        print(f"ERROR creating voice: {e}")
        raise


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
