"""
STEP 1: WRITE THE SCRIPT

Uses Ollama (local AI) to generate YouTube Shorts optimized script.
Generates topic, title, description, script, and scene descriptions.
"""

import json
import sys
from pathlib import Path

import requests

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from settings.config import Config


def write_script_with_ollama(user_prompt: str) -> dict:
    """
    Generate YouTube Shorts script using LOCAL Ollama AI.

    Args:
        user_prompt: What the video should be about

    Returns:
        Dictionary with: topic, title, description, script, search_keywords, scene_descriptions
    """

    system_instructions = """You are a YouTube Shorts expert creator.
    
    IMPORTANT RULES FOR YOUTUBE SHORTS:
    1. Hook in first 3 seconds (attention grabbing)
    2. Script must be 30-50 seconds when spoken
    3. Use VERTICAL video thinking (people, faces, close-ups)
    4. Write for mobile viewers (short sentences, punchy)
    5. Include call-to-action at end
    6. Optimized for watching WITHOUT sound (visual first)
    
    Create engaging, fast-paced content that keeps viewers watching."""

    user_message = f"""Create a YouTube Short based on: "{user_prompt}"

Return ONLY valid JSON with these exact keys:
{{
  "topic": "One clear sentence about the Short",
  "title": "Catchy YouTube Shorts title (max 60 chars)",
  "description": "Description with AI disclosure and hashtags",
  "script": "30-50 second script with strong hook and call to action",
  "search_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "scene_descriptions": ["scene1 description", "scene2 description", "scene3 description", "scene4 description", "scene5 description"]
}}

Make it punchy and engaging. Hook viewers in 3 seconds."""

    ollama_url = f"{Config.OLLAMA_HOST}/api/generate"

    payload = {
        "model": Config.OLLAMA_MODEL,
        "prompt": f"{system_instructions}\n\n{user_message}",
        "stream": False,
    }

    try:
        print(f"Asking Ollama ({Config.OLLAMA_MODEL}) to write the script...")

        response = requests.post(ollama_url, json=payload, timeout=60)
        response.raise_for_status()

        ollama_response = response.json()
        generated_text = ollama_response.get("response", "")

        # Clean up markdown code blocks if present
        if "```json" in generated_text:
            generated_text = generated_text.split("```json")[1].split("```")[0].strip()
        elif "```" in generated_text:
            generated_text = generated_text.split("```")[1].split("```")[0].strip()

        # Remove control characters that can break JSON parsing
        import re

        generated_text = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", generated_text)

        # Try to find JSON object in the response
        json_start = generated_text.find("{")
        json_end = generated_text.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            generated_text = generated_text[json_start:json_end]

        content = json.loads(generated_text)

        # Add AI disclosure if missing
        if "AI" not in content.get("description", ""):
            content["description"] += f"\n\n{Config.AI_DISCLOSURE_TEXT}"

        print("Script written successfully")
        return content

    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to Ollama")
        print("Make sure Ollama is running: ollama serve")
        print(f"Check: curl {Config.OLLAMA_HOST}")
        return create_fallback_script(user_prompt)

    except json.JSONDecodeError as e:
        print(f"Ollama response was not valid JSON: {e}")
        print(f"Raw response: {generated_text[:200] if generated_text else 'empty'}")
        return create_fallback_script(user_prompt)

    except Exception as e:
        print(f"ERROR: {e}")
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

    for word in words:
        timestamps.append(
            {
                "word": word,
                "start": round(current_time, 2),
                "end": round(current_time + time_per_word, 2),
            }
        )
        current_time += time_per_word

    return timestamps


if __name__ == "__main__":
    # Test this module
    test_prompt = "Amazing facts about the ocean"
    result = write_script_with_ollama(test_prompt)

    print("\n" + "=" * 60)
    print("TEST RESULT:")
    print("=" * 60)
    print(json.dumps(result, indent=2))

    estimated_duration = estimate_script_duration(result["script"])
    print(f"\nEstimated duration: {estimated_duration:.1f} seconds")

    if estimated_duration > Config.MAX_DURATION_SECONDS:
        print(
            f"WARNING: Script too long for YouTube Shorts (max {Config.MAX_DURATION_SECONDS}s)"
        )
    elif estimated_duration < Config.MIN_DURATION_SECONDS:
        print(
            f"WARNING: Script too short for YouTube Shorts (min {Config.MIN_DURATION_SECONDS}s)"
        )
    else:
        print("Perfect length for YouTube Shorts")
