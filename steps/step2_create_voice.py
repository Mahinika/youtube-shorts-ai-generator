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
    Convert script text to voice audio.

    Args:
        script_text: The narrative script

    Returns:
        Dictionary with 'path' and 'duration' keys
    """

    print("Creating voice narration...")
    
    # Clean the script text to remove sound effects and emojis
    cleaned_script = clean_narrative_text(script_text)
    print(f"Original script length: {len(script_text)} chars")
    print(f"Cleaned script length: {len(cleaned_script)} chars")
    
    if cleaned_script != script_text:
        print("Removed sound effects and emojis from narrative")

    # Create temp directory on D drive
    temp_dir = Path(Config.TEMP_DIR)
    temp_dir.mkdir(parents=True, exist_ok=True)

    output_path = temp_dir / "narration.mp3"

    try:
        # Prefer Edge TTS if available
        use_edge = (
            getattr(Config, "TTS_ENGINE", "edge").lower() == "edge"
            and (edge_tts is not None)
            and (not getattr(Config, "FORCE_GTTS", False))
        )
        if use_edge:
            print("  Using Edge TTS engine...")
            selected_voice = voice_name or getattr(Config, "EDGE_TTS_VOICE", "en-US-AriaNeural")
            print(f"  Edge TTS voice: {selected_voice}")

            async def synth(text: str, out_path: Path, voice: str):
                # Use defaults (no rate/volume) to avoid invalid values across versions
                communicate = edge_tts.Communicate(text, voice=voice)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    await communicate.save(tmp.name)
                    AudioSegment.from_file(tmp.name).export(str(out_path), format="mp3")

            try:
                # Check if event loop is already running (e.g., in GUI thread)
                try:
                    loop = asyncio.get_running_loop()
                    # If we get here, there's already a loop running
                    # Create a new loop in a thread to avoid conflicts
                    import threading
                    result_container = []
                    exception_container = []
                    
                    def run_in_thread():
                        try:
                            new_loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(new_loop)
                            new_loop.run_until_complete(synth(cleaned_script, output_path, selected_voice))
                            new_loop.close()
                            result_container.append(True)
                        except Exception as e:
                            exception_container.append(e)
                    
                    thread = threading.Thread(target=run_in_thread)
                    thread.start()
                    thread.join()
                    
                    if exception_container:
                        raise exception_container[0]
                except RuntimeError:
                    # No event loop running, safe to use asyncio.run()
                    asyncio.run(synth(cleaned_script, output_path, selected_voice))
            except Exception as edge_err:
                if getattr(Config, "ALLOW_TTS_FALLBACK", True):
                    print(f"  Edge TTS failed: {edge_err}. Falling back to gTTS...")
                    tts = gTTS(text=cleaned_script, lang=Config.VOICE_LANGUAGE, slow=False)
                    tts.save(str(output_path))
                else:
                    raise
        else:
            print("  Using gTTS...")
            tts = gTTS(text=cleaned_script, lang=Config.VOICE_LANGUAGE, slow=False)
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
