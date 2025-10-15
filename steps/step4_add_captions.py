"""
STEP 4: ADD CAPTIONS

Creates large, centered karaoke-style captions for YouTube Shorts.
Optimized for mobile viewing without sound.
"""

import sys
from pathlib import Path

# Captions now handled by FFmpeg in step5_combine_everything.py

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from settings.config import Config


def create_shorts_captions(word_timestamps: list) -> list:
    """
    Create YouTube Shorts optimized captions.

    Args:
        word_timestamps: List of dictionaries with word, start, end

    Returns:
        List of TextClip objects for moviepy
    """

    print("Captions handled by FFmpeg in video combination step")

    if not word_timestamps:
        print("WARNING: No word timestamps provided")
        return []

    return []  # Return empty list to disable captions

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
    word_timestamps: list, words_per_phrase: int = 2
) -> list:
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

    phrases = []

    for i in range(0, len(word_timestamps), words_per_phrase):
        phrase = word_timestamps[i : i + words_per_phrase]
        if phrase:  # Skip empty
            phrases.append(phrase)

    return phrases


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
