"""
STEP 2: CREATE VOICE

Converts script text into speech audio using free TTS.
Outputs to D drive temp folder.
"""

import sys
from pathlib import Path

from gtts import gTTS
from pydub import AudioSegment

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from settings.config import Config


def create_voice_narration(script_text: str) -> dict:
    """
    Convert script text to voice audio.

    Args:
        script_text: The narrative script

    Returns:
        Dictionary with 'path' and 'duration' keys
    """

    print("Creating voice narration...")

    # Create temp directory on D drive
    temp_dir = Path(Config.TEMP_DIR)
    temp_dir.mkdir(parents=True, exist_ok=True)

    output_path = temp_dir / "narration.mp3"

    try:
        # Use gTTS (free and reliable)
        tts = gTTS(text=script_text, lang=Config.VOICE_LANGUAGE, slow=False)
        tts.save(str(output_path))

        # Get duration
        audio = AudioSegment.from_mp3(str(output_path))
        duration = len(audio) / 1000.0  # Convert to seconds

        # Trim if exceeds maximum duration
        if duration > Config.MAX_DURATION_SECONDS:
            print(
                f"WARNING: Audio duration {duration:.1f}s exceeds max {Config.MAX_DURATION_SECONDS}s"
            )
            print(f"Trimming to {Config.MAX_DURATION_SECONDS} seconds...")

            trimmed_audio = audio[: Config.MAX_DURATION_SECONDS * 1000]
            trimmed_audio.export(str(output_path), format="mp3")
            duration = Config.MAX_DURATION_SECONDS

        print(f"Voice created: {duration:.1f} seconds")

        return {"path": str(output_path), "duration": duration}

    except Exception as e:
        print(f"ERROR creating voice: {e}")
        raise


if __name__ == "__main__":
    # Test this module
    test_script = "This is a test of the voice narration system. It should create an audio file on the D drive."
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
