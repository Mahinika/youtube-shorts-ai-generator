#!/usr/bin/env python3
"""Test caption generation and word timestamps"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from steps.step1_write_script import generate_word_timestamps
from settings.config import Config

# Test script
test_script = "Hey, space fans! Did you know that there's a giant storm on Jupiter that's been raging for CENTURIES?"
test_duration = 10.0  # 10 seconds

print("Testing word timestamp generation...")
print(f"Script: {test_script}")
print(f"Duration: {test_duration} seconds")
print()

# Generate word timestamps
words = generate_word_timestamps(test_script, test_duration)

print(f"Generated {len(words)} word timestamps:")
for i, word in enumerate(words[:10]):  # Show first 10
    print(f"  {i+1:2d}. '{word['word']}' - {word['start']:.2f}s to {word['end']:.2f}s")

if len(words) > 10:
    print(f"  ... and {len(words) - 10} more words")

print()
print("Testing FFmpeg drawtext filter generation...")

# Test FFmpeg filter generation
filter_parts = []
for w in words[:5]:  # Test first 5 words
    txt = (
        str(w["word"]).upper().replace(":", "\\:").replace("'", "\\'").replace(" ", "")
    )
    start = max(0.0, float(w["start"]))
    end = max(start + 0.05, float(w["end"]))
    filter_part = (
        f"[vc]drawtext=text='{txt}':fontcolor={Config.CAPTION_FONT_COLOR}:fontsize={Config.CAPTION_FONT_SIZE}:"
        f"borderw={Config.CAPTION_STROKE_WIDTH}:bordercolor={Config.CAPTION_STROKE_COLOR}:"
        f"x=(w-tw)/2:y=(h/2):enable='between(t,{start:.2f},{end:.2f})'[vc]"
    )
    filter_parts.append(filter_part)

print("Generated FFmpeg filters:")
for i, part in enumerate(filter_parts):
    print(f"  {i+1}. {part[:80]}...")

print()
print("Test completed successfully!")

