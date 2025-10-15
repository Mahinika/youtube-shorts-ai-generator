"""
STEP 4: ADD CAPTIONS

Creates large, centered karaoke-style captions for YouTube Shorts.
Optimized for mobile viewing without sound.
"""

import sys
from pathlib import Path
from typing import List, Dict

# Captions now handled by FFmpeg in step5_combine_everything.py

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from settings.config import Config


def create_shorts_captions(word_timestamps: List[Dict]) -> str:
    """
    Generate an ASS (.ass) karaoke subtitle file from per-word timestamps.

    Args:
        word_timestamps: List of dicts with keys: word, start, end (seconds)

    Returns:
        Path (str) to generated .ass file. Empty string if none.
    """

    if not word_timestamps:
        print("WARNING: No word timestamps provided for captions")
        return ""

    # Output path
    temp_dir = Path("temp_files")
    temp_dir.mkdir(parents=True, exist_ok=True)
    ass_path = temp_dir / "captions.ass"

    # Group words into short phrases for mobile readability
    words_per_phrase = getattr(Config, "WORDS_PER_CAPTION", 3) or 3
    phrases = group_words_into_short_phrases(word_timestamps, words_per_phrase=words_per_phrase)

    # ASS header and style
    play_res_x = getattr(Config, "VIDEO_WIDTH", 1080)
    play_res_y = getattr(Config, "VIDEO_HEIGHT", 1920)
    font_name = getattr(Config, "CAPTION_FONT_NAME", "Arial")
    font_size = getattr(Config, "CAPTION_FONT_SIZE", 52)
    # Keep captions above YouTube Shorts UI (safe area)
    margin_v = 300

    # Colors are in BGR with &HAABBGGRR format in ASS
    # PrimaryColour: base text; SecondaryColour: karaoke highlight
    # Use yellow with subtle darker base for visible fill effect
    primary_colour = "&H004FD5FF"   # darker yellow (#FFD54F)
    secondary_colour = "&H0000FFFF" # bright yellow (#FFFF00)
    outline_colour = "&H00000000"    # black
    back_colour = "&H00000000"       # no background box

    header = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {play_res_x}",
        f"PlayResY: {play_res_y}",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        # BorderStyle=1 (outline only), Outline=2, Shadow=1, Alignment=2 (bottom-center)
        f"Style: StyleKaraoke,{font_name},{font_size},{primary_colour},{secondary_colour},{outline_colour},{back_colour},-1,0,0,0,100,100,0,0,1,2,1,2,60,60,{margin_v},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    lines: List[str] = []

    for phrase in phrases:
        if not phrase:
            continue
        # Determine start/end for this phrase
        start = max(0.0, float(phrase[0]["start"]))
        end = max(start, float(phrase[-1]["end"]))
        # Build karaoke sequence with \kf tags (centiseconds)
        parts: List[str] = []
        for w in phrase:
            dur = max(0.08, float(w["end"]) - float(w["start"]))  # minimum 80 ms per word
            cs = int(round(dur * 100))
            word_text = str(w["word"]).replace("{", "(").replace("}", ")")
            parts.append(f"{{\\kf{cs}}}{word_text}")

        text_payload = " ".join(parts)
        start_ts = _sec_to_ass_ts(start)
        end_ts = _sec_to_ass_ts(end)
        # Bottom-center alignment via style (Alignment=2), so no \pos needed
        line = f"Dialogue: 0,{start_ts},{end_ts},StyleKaraoke,,0,0,0,,{{\\an2}}{text_payload}"
        lines.append(line)

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write("\n".join(header + lines) + "\n")

    print(f"Created karaoke ASS: {ass_path}")
    return str(ass_path)

    caption_clips = []

    # Group words into short phrases (2-3 words for mobile)
    phrases = group_words_into_short_phrases(
        word_timestamps, words_per_phrase=Config.WORDS_PER_CAPTION
    )

    print(f"  Creating {len(phrases)} caption phrases...")

    for phrase in phrases:
        phrase_clips = create_single_phrase_caption(phrase)
        caption_clips.extend(phrase_clips)

    print(f"Created {len(caption_clips)} caption clips")

    return caption_clips


def create_single_phrase_caption(phrase: list) -> list:
    """
    Create caption for one phrase with karaoke effect.

    Args:
        phrase: List of word timing dictionaries

    Returns:
        List of TextClip objects
    """

    clips = []

    # Calculate position (center of vertical video)
    if Config.CAPTION_POSITION == "center":
        y_position = Config.VIDEO_HEIGHT * 0.5
    elif Config.CAPTION_POSITION == "top":
        y_position = Config.VIDEO_HEIGHT * 0.2
    else:  # bottom
        y_position = Config.VIDEO_HEIGHT * 0.8

    # Create highlighting effect for each word
    for i, word_data in enumerate(phrase):
        try:
            # Create clip with current word
            clip = (
                TextClip(
                    text=word_data["word"].upper(),  # Uppercase for emphasis
                    font_size=Config.CAPTION_FONT_SIZE,
                    color=Config.CAPTION_FONT_COLOR,
                    stroke_color=Config.CAPTION_STROKE_COLOR,
                    stroke_width=Config.CAPTION_STROKE_WIDTH,
                    method="caption",
                    size=(
                        int(Config.VIDEO_WIDTH * Config.CAPTION_MAX_WIDTH_PERCENT),
                        None,
                    ),
                    text_align="center",
                )
                .set_position(("center", y_position))
                .set_start(word_data["start"])
                .set_duration(word_data["end"] - word_data["start"])
            )

            clips.append(clip)

        except Exception as e:
            print(f"  WARNING: Error creating caption for '{word_data['word']}': {e}")
            # Continue with other words even if one fails
            continue

    return clips


def group_words_into_short_phrases(
    word_timestamps: List[Dict], words_per_phrase: int = 3
) -> List[List[Dict]]:
    """
    Group words into short, punchy phrases for mobile.

    Shorts need:
    - Fewer words per line (mobile screen is small)
    - Quick changes (keeps attention)
    - Easy to read while scrolling

    Args:
        word_timestamps: All word timings
        words_per_phrase: How many words per caption

    Returns:
        List of phrase groups
    """

    phrases: List[List[Dict]] = []

    for i in range(0, len(word_timestamps), words_per_phrase):
        phrase = word_timestamps[i : i + words_per_phrase]
        if phrase:  # Skip empty
            phrases.append(phrase)

    return phrases


def _sec_to_ass_ts(sec: float) -> str:
    """Convert seconds (float) to ASS timestamp H:MM:SS.cs (centiseconds)."""
    if sec < 0:
        sec = 0.0
    total_cs = int(round(sec * 100))
    cs = total_cs % 100
    total_s = total_cs // 100
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


if __name__ == "__main__":
    # Test this module
    print("=" * 60)
    print("TESTING CAPTION GENERATION")
    print("=" * 60)

    test_words = [
        {"word": "This", "start": 0.0, "end": 0.3},
        {"word": "is", "start": 0.3, "end": 0.5},
        {"word": "an", "start": 0.5, "end": 0.7},
        {"word": "amazing", "start": 0.7, "end": 1.2},
        {"word": "YouTube", "start": 1.2, "end": 1.6},
        {"word": "Short", "start": 1.6, "end": 2.0},
    ]

    print(f"\nInput: {len(test_words)} words")
    print(f"Words per caption: {Config.WORDS_PER_CAPTION}")

    captions = create_shorts_captions(test_words)

    print(f"\nOutput: {len(captions)} caption clips")

    if captions:
        print("\nCaption details:")
        for i, clip in enumerate(captions):
            print(
                f"  Clip {i+1}: start={clip.start:.2f}s, duration={clip.duration:.2f}s"
            )

    print("\nTest complete")
