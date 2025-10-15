#!/usr/bin/env python3
"""
Unit tests for script generation utility functions.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from steps.step1_write_script import estimate_script_duration, generate_word_timestamps


class TestScriptFunctions(unittest.TestCase):
    """Test script utility functions."""

    def test_estimate_script_duration(self):
        """Test script duration estimation accuracy."""
        # Test basic estimation
        script = "This is a test script with exactly ten words total."
        duration = estimate_script_duration(script, words_per_second=2.5)
        expected = 10 / 2.5  # 4.0 seconds
        self.assertAlmostEqual(duration, expected, places=1)

        # Test empty script
        duration = estimate_script_duration("", words_per_second=2.5)
        self.assertEqual(duration, 0.0)

        # Test different speaking rates
        script = "Hello world test"
        duration_fast = estimate_script_duration(script, words_per_second=3.0)
        duration_slow = estimate_script_duration(script, words_per_second=2.0)
        self.assertGreater(duration_slow, duration_fast)

    def test_generate_word_timestamps_basic(self):
        """Test word timestamp generation with basic input."""
        script = "Hello world test"
        duration = 3.0
        timestamps = generate_word_timestamps(script, duration)

        self.assertEqual(len(timestamps), 3)

        # Check word extraction
        self.assertEqual(timestamps[0]["word"], "Hello")
        self.assertEqual(timestamps[1]["word"], "world")
        self.assertEqual(timestamps[2]["word"], "test")

        # Check timing progression - words should be continuous (no gaps)
        self.assertEqual(timestamps[0]["start"], 0.0)
        self.assertEqual(timestamps[0]["end"], timestamps[1]["start"])
        self.assertEqual(timestamps[1]["end"], timestamps[2]["start"])
        self.assertEqual(timestamps[-1]["end"], duration)

        # Check total duration
        self.assertAlmostEqual(timestamps[-1]["end"], duration, places=1)

    def test_generate_word_timestamps_punctuation(self):
        """Test word timestamp generation handles punctuation correctly."""
        script = "Hello, world! This is a test."
        duration = 6.0
        timestamps = generate_word_timestamps(script, duration)

        # Should have 6 words (punctuation removed)
        self.assertEqual(len(timestamps), 6)

        # Check words are cleaned
        words = [t["word"] for t in timestamps]
        self.assertEqual(words, ["Hello", "world", "This", "is", "a", "test"])

    def test_generate_word_timestamps_empty(self):
        """Test word timestamp generation with empty input."""
        timestamps = generate_word_timestamps("", 10.0)
        self.assertEqual(timestamps, [])

        timestamps = generate_word_timestamps("   ", 10.0)
        self.assertEqual(timestamps, [])

    def test_generate_word_timestamps_quotes(self):
        """Test word timestamp generation handles quotes correctly."""
        script = '"Hello world," he said.'
        duration = 4.0
        timestamps = generate_word_timestamps(script, duration)

        # Should have 4 words (quotes and punctuation removed)
        self.assertEqual(len(timestamps), 4)
        words = [t["word"] for t in timestamps]
        self.assertEqual(words, ["Hello", "world", "he", "said"])

    def test_generate_word_timestamps_timing_accuracy(self):
        """Test that timestamps are evenly distributed."""
        script = "One two three four five"
        duration = 10.0
        timestamps = generate_word_timestamps(script, duration)

        self.assertEqual(len(timestamps), 5)

        # Each word should get equal time (10s / 5 words = 2s each)
        expected_duration_per_word = duration / len(timestamps)

        for i, timestamp in enumerate(timestamps):
            expected_start = i * expected_duration_per_word
            expected_end = (i + 1) * expected_duration_per_word

            self.assertAlmostEqual(timestamp["start"], expected_start, places=2)
            self.assertAlmostEqual(timestamp["end"], expected_end, places=2)

    def test_generate_word_timestamps_realistic_script(self):
        """Test with a realistic YouTube Shorts script."""
        script = "Did you know that honey never spoils? Archaeologists found 3000 year old honey that's still edible. That's amazing!"
        duration = 12.0
        timestamps = generate_word_timestamps(script, duration)

        # Should have meaningful timestamps
        self.assertGreater(len(timestamps), 10)
        self.assertLess(len(timestamps), 25)  # Reasonable word count

        # Check timing is continuous and monotonic
        for i in range(1, len(timestamps)):
            self.assertEqual(timestamps[i-1]["end"], timestamps[i]["start"])
            self.assertLess(timestamps[i]["start"], timestamps[i]["end"])

        # Total duration should be preserved
        self.assertAlmostEqual(timestamps[-1]["end"], duration, places=1)


if __name__ == "__main__":
    unittest.main()
