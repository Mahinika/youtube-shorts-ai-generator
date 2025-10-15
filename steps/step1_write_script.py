"""
STEP 1: WRITE THE SCRIPT

Uses Ollama (local AI) to generate YouTube Shorts optimized script.
Generates topic, title, description, script, and scene descriptions.
"""

import json
import re
import sys
import time
from pathlib import Path

import requests

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from settings.config import Config
from utils import (
    extract_json_from_response,
    validate_json_structure,
    prompt_manager,
    logger,
    monitor_performance,
    performance_tracker
)
from utils.ai_providers import generate_with_ai


def get_topic_specific_context(topic: str) -> str:
    """Add topic-specific context to improve script generation."""
    return prompt_manager.get_topic_context(topic)


@monitor_performance
def write_script_with_ollama(user_prompt: str) -> dict:
    """
    Generate YouTube Shorts script using configured AI provider (Groq or Ollama).

    Args:
        user_prompt: What the video should be about

    Returns:
        Dictionary with: topic, title, description, script, search_keywords, scene_descriptions
    """
    logger.info(f"Starting script generation for prompt: {user_prompt[:100]}...")
    performance_tracker.start_operation("script_generation")

    system_instructions = prompt_manager.get_prompt("script_gen")

    # Get topic-specific context
    topic_context = get_topic_specific_context(user_prompt)
    
    user_message = f"""{topic_context}

Create a YouTube Short based on: "{user_prompt}"

Return ONLY valid JSON."""

    try:
        logger.info(f"Asking AI ({Config.AI_PROVIDER}) to write the script...")

        # Use the unified AI provider with automatic fallback
        generated_text = generate_with_ai(system_instructions, user_message, logger)

        # Use robust JSON parsing
        try:
            content = extract_json_from_response(generated_text)
            logger.info("Successfully parsed JSON response")
            logger.debug(f"Parsed content keys: {list(content.keys()) if isinstance(content, dict) else 'Not a dict'}")
            logger.debug(f"Parsed content: {content}")
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {generated_text[:500]}...")
            return create_fallback_script(user_prompt)

        # Inline validation and safe adjustments
        def _word_count_okay(text) -> bool:
            if not isinstance(text, str):
                return False
            wc = len(text.split()) if text else 0
            return 85 <= wc <= 130

        # Validate and fill missing required fields
        required_keys = ["topic", "title", "description", "script"]
        optional_keys = ["search_keywords", "scene_descriptions", "beats"]

        # Check if we have the minimum required keys
        if not validate_json_structure(content, required_keys):
            logger.warning("JSON response missing required keys")
            logger.debug(f"Required keys: {required_keys}")
            logger.debug(f"Actual keys in response: {list(content.keys()) if isinstance(content, dict) else 'Not a dict'}")
            return create_fallback_script(user_prompt)

        # Fill in missing optional fields with defaults
        if "search_keywords" not in content:
            # Generate keywords from topic and prompt
            base_words = user_prompt.lower().split()[:3]
            content["search_keywords"] = base_words + ["facts", "amazing"]

        if "scene_descriptions" not in content:
            # Generate generic but topic-relevant scene descriptions
            content["scene_descriptions"] = [
                f"Dynamic {user_prompt.lower()} themed opening scene",
                f"Close-up details showcasing {user_prompt.lower()} elements",
                f"Animated graphics highlighting key {user_prompt.lower()} facts",
                f"Fast-paced montage of {user_prompt.lower()} examples",
                f"Vibrant conclusion with engaging visuals"
            ]

        logger.info("JSON validation passed, proceeding with content generation")

        # Ensure script is a proper string
        script = content.get("script", "")
        if isinstance(script, list):
            # Join list items and clean up
            script = " ".join(str(item) for item in script)
        elif isinstance(script, dict):
            # Convert dict to string
            script = " ".join(str(value) for value in script.values())
        else:
            script = str(script)

        # Clean up the script text
        script = script.strip()
        # Remove common AI formatting artifacts
        script = script.replace('[\\n    "', '').replace('"]', '')
        script = script.replace('\\n', ' ').replace('\\t', ' ')
        script = script.replace('  ', ' ')  # Remove double spaces

        # Remove malformed brackets at start
        if script.startswith('["[') and script.endswith('"]'):
            script = script[3:-2]
        elif script.startswith('[\n    "') and '"]' in script:
            # Handle the specific case we saw
            script = script.replace('[\n    "', '').replace('"]', '')

        # Remove visual annotations that would sound bad when read aloud
        # These are common patterns like [animation], [Brain scan animation], [Clock animation], etc.
        script = re.sub(r'\s*\[[\w\s]+\]\s*', ' ', script)  # Remove [any text in brackets]
        script = re.sub(r'\s+', ' ', script)  # Remove extra spaces left by bracket removal

        # Final cleanup
        script = script.strip()
        if not script or len(script) < 10:
            # If script is too short or empty, create a basic one
            script = f"Did you know about {user_prompt}? Here are some amazing facts that will surprise you. The truth is more interesting than you think. Comment below what you think!"

        content["script"] = script

        # Clamp/add disclosure
        if "AI" not in content.get("description", ""):
            content["description"] += f"\n\n{Config.AI_DISCLOSURE_TEXT}"

        # Beats validation if present
        beats = content.get("beats")
        if beats and isinstance(beats, list):
            valid_beats = []
            total_beats_duration = 0.0
            for b in beats[:5]:
                try:
                    dur = float(b.get("duration_seconds", 0))
                except Exception:
                    dur = 0.0
                if 6 <= dur <= 12:
                    total_beats_duration += dur
                    valid_beats.append(b)
            if 3 <= len(valid_beats) <= 5 and 34 <= total_beats_duration <= 52:
                content["beats"] = valid_beats
            else:
                # Drop invalid beats to stay backward compatible
                content.pop("beats", None)

        # TODO: Re-enable judge/revision process after fixing judge prompt issues
        # For now, skip quality assessment to get basic generation working
        logger.info("Skipping judge/revision process for now - basic generation completed")

        logger.info("Script generation completed successfully")
        performance_tracker.end_operation("script_generation", success=True)
        return content

    except Exception as e:
        logger.error(f"Script generation failed: {e}")
        logger.debug(f"Generated text: {generated_text[:200] if 'generated_text' in locals() else 'N/A'}")
        
        # Provide helpful error messages
        if Config.AI_PROVIDER == "groq" and not Config.GROQ_API_KEY:
            logger.error("GROQ_API_KEY not set! Get one at https://console.groq.com")
            logger.error("Add it to your .env file: GROQ_API_KEY=your_key_here")
        elif Config.AI_PROVIDER == "ollama":
            logger.error(f"Make sure Ollama is running: ollama serve")
            logger.error(f"Check: curl {Config.OLLAMA_HOST}")
        
        performance_tracker.end_operation("script_generation", success=False)
        return create_fallback_script(user_prompt)


def create_fallback_script(prompt: str) -> dict:
    """Create a basic script if Ollama fails"""

    clean_prompt = prompt[:100] if prompt else "content"

    return {
        "topic": f"YouTube Short about {clean_prompt}",
        "title": f"{clean_prompt[:50]}",
        "description": f"A YouTube Short about {clean_prompt}\n\n{Config.AI_DISCLOSURE_TEXT}",
        "script": f"Want to know about {clean_prompt}? Here's something cool you need to see. This is amazing and interesting. Follow for more awesome Shorts!",
        "search_keywords": (
            prompt.split()[:5]
            if prompt
            else ["video", "content", "short", "amazing", "cool"]
        ),
        "scene_descriptions": [
            "dynamic colorful background",
            "engaging visual scene",
            "interesting composition",
            "eye-catching display",
            "vibrant finale",
        ],
    }


@monitor_performance
def estimate_script_duration(script: str, words_per_second: float = 2.5) -> float:
    """
    Estimate how long the script will take to speak.

    Args:
        script: The text script
        words_per_second: Speaking speed (2.5 is conversational)

    Returns:
        Estimated duration in seconds
    """

    word_count = len(script.split())
    duration = word_count / words_per_second
    return duration


@monitor_performance
def generate_word_timestamps(script: str, total_duration: float) -> list:
    """
    Create timestamps for each word (for karaoke captions).

    Args:
        script: The text to split into words
        total_duration: Total audio length in seconds

    Returns:
        List of dictionaries with word, start, end times
    """

    # Clean script and split into words
    cleaned = (
        script.replace(",", "")
        .replace(".", "")
        .replace("!", "")
        .replace("?", "")
        .replace('"', "")
        .replace("'", "")
    )
    words = cleaned.split()

    if not words:
        return []

    time_per_word = total_duration / len(words)

    timestamps = []
    current_time = 0

    for i, word in enumerate(words):
        start_time = round(current_time, 2)
        # For the last word, ensure it ends at the total duration
        if i == len(words) - 1:
            end_time = round(total_duration, 2)
        else:
            end_time = round(current_time + time_per_word, 2)
        timestamps.append(
            {
                "word": word,
                "start": start_time,
                "end": end_time,
            }
        )
        current_time += time_per_word

    return timestamps


if __name__ == "__main__":
    # Test this module
    test_prompt = "Amazing facts about the ocean"
    logger.info(f"Running test with prompt: {test_prompt}")

    result = write_script_with_ollama(test_prompt)

    print("\n" + "=" * 60)
    print("TEST RESULT:")
    print("=" * 60)
    print(json.dumps(result, indent=2))

    estimated_duration = estimate_script_duration(result["script"])
    print(f"\nEstimated duration: {estimated_duration:.1f} seconds")

    if estimated_duration > Config.MAX_DURATION_SECONDS:
        logger.warning(
            f"Script too long for YouTube Shorts (max {Config.MAX_DURATION_SECONDS}s)"
        )
    elif estimated_duration < Config.MIN_DURATION_SECONDS:
        logger.warning(
            f"Script too short for YouTube Shorts (min {Config.MIN_DURATION_SECONDS}s)"
        )
    else:
        logger.info("Perfect length for YouTube Shorts")
