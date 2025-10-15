"""
Robust JSON parsing utilities for AI-generated content.

This module provides multiple fallback strategies for parsing JSON responses
from AI models that may contain formatting errors or partial responses.
"""

import json
import re
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import json5
    HAS_JSON5 = True
except ImportError:
    HAS_JSON5 = False


def extract_json_from_response(text: str) -> Dict[str, Any]:
    """
    Extract and parse JSON from AI response with multiple fallback strategies.

    Args:
        text: Raw text response from AI model

    Returns:
        Parsed JSON dictionary

    Raises:
        ValueError: If no valid JSON can be extracted
    """

    # Strategy 1: Try direct JSON parsing
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Strategy 2: Try JSON5 (more tolerant) if available
    if HAS_JSON5:
        try:
            return json5.loads(text.strip())
        except Exception:
            pass

    # Strategy 3: Find JSON object with balanced braces using regex
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Strategy 4: Extract key-value pairs manually
    manual_extraction = extract_key_value_pairs(text)
    if manual_extraction:
        return manual_extraction

    # Strategy 5: Find the first and last braces and try to parse
    start_idx = text.find('{')
    end_idx = text.rfind('}') + 1

    if start_idx >= 0 and end_idx > start_idx:
        try:
            candidate = text[start_idx:end_idx]
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # Strategy 6: Clean and retry with basic fixes
    cleaned = clean_json_text(text)
    if cleaned != text:
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract valid JSON from response: {text[:200]}...")


def clean_json_text(text: str) -> str:
    """
    Clean common JSON formatting issues.

    Args:
        text: Raw text that may contain JSON

    Returns:
        Cleaned text
    """
    # Remove control characters
    text = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)

    # Remove markdown code blocks
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    # Fix common escaping issues
    text = text.replace('\\"', '"')

    # Find the outermost JSON object
    start = text.find('{')
    if start == -1:
        return text

    # Count braces to find the matching end
    brace_count = 0
    end = -1

    for i, char in enumerate(text[start:], start):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end = i
                break

    if end != -1:
        return text[start:end + 1]

    return text


def extract_key_value_pairs(text: str) -> Optional[Dict[str, Any]]:
    """
    Attempt to extract key-value pairs from malformed JSON-like text.

    Args:
        text: Text that may contain JSON-like content

    Returns:
        Dictionary of extracted key-value pairs, or None if unsuccessful
    """
    result = {}

    # Look for patterns like "key": "value" or "key": value
    patterns = [
        r'"([^"]+)":\s*"([^"]*)"',  # String values
        r'"([^"]+)":\s*(\d+(?:\.\d+)?)',  # Numeric values
        r'"([^"]+)":\s*(true|false|null)',  # Boolean/null values
        r'"([^"]+)":\s*(\[[^\]]*\])',  # Array values
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)
        for key, value in matches:
            try:
                # Try to parse the value
                if value.startswith('[') and value.endswith(']'):
                    # Handle arrays
                    try:
                        result[key] = json.loads(value)
                    except:
                        result[key] = value.strip('[]"').split('","') if '","' in value else [value.strip('"')]
                elif value in ['true', 'false', 'null']:
                    if value == 'true':
                        result[key] = True
                    elif value == 'false':
                        result[key] = False
                    else:
                        result[key] = None
                elif value.replace('.', '').isdigit():
                    result[key] = float(value) if '.' in value else int(value)
                else:
                    result[key] = value.strip('"')
            except Exception:
                continue

    return result if result else None


def validate_json_structure(data: Dict[str, Any], required_keys: list) -> bool:
    """
    Validate that JSON contains required keys with appropriate types.

    Args:
        data: Parsed JSON data
        required_keys: List of keys that must be present

    Returns:
        True if validation passes
    """
    if not isinstance(data, dict):
        return False

    return all(key in data for key in required_keys)
