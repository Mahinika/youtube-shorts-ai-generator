"""
Input Validation Utilities

Provides comprehensive input validation functions for all step functions
in the YouTube Shorts automation system.
"""

import re
import os
from pathlib import Path
from typing import Any, List, Dict, Union, Optional, Tuple
from utils.error_handler import ValidationError, FileOperationError


def validate_string_input(
    value: Any, 
    field_name: str, 
    min_length: int = 1, 
    max_length: int = 1000,
    allow_empty: bool = False,
    pattern: Optional[str] = None
) -> str:
    """
    Validate string input with comprehensive checks.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        min_length: Minimum string length
        max_length: Maximum string length
        allow_empty: Whether empty strings are allowed
        pattern: Optional regex pattern to validate against
        
    Returns:
        Validated string
        
    Raises:
        ValidationError: If validation fails
    """
    if value is None:
        if allow_empty:
            return ""
        raise ValidationError(
            f"{field_name} cannot be None",
            error_code="NULL_VALUE",
            details={"field_name": field_name, "value": value}
        )
    
    if not isinstance(value, str):
        try:
            value = str(value)
        except Exception as e:
            raise ValidationError(
                f"{field_name} must be a string, got {type(value).__name__}",
                error_code="INVALID_TYPE",
                details={"field_name": field_name, "value": value, "expected_type": "str"}
            )
    
    value = value.strip()
    
    if not value and not allow_empty:
        raise ValidationError(
            f"{field_name} cannot be empty",
            error_code="EMPTY_VALUE",
            details={"field_name": field_name, "value": value}
        )
    
    if len(value) < min_length and (value or not allow_empty):
        raise ValidationError(
            f"{field_name} must be at least {min_length} characters, got {len(value)}",
            error_code="TOO_SHORT",
            details={"field_name": field_name, "value": value, "min_length": min_length}
        )
    
    if len(value) > max_length:
        raise ValidationError(
            f"{field_name} must be at most {max_length} characters, got {len(value)}",
            error_code="TOO_LONG",
            details={"field_name": field_name, "value": value, "max_length": max_length}
        )
    
    if pattern and not re.match(pattern, value):
        raise ValidationError(
            f"{field_name} does not match required pattern: {pattern}",
            error_code="PATTERN_MISMATCH",
            details={"field_name": field_name, "value": value, "pattern": pattern}
        )
    
    return value


def validate_list_input(
    value: Any,
    field_name: str,
    min_items: int = 1,
    max_items: int = 100,
    item_type: Optional[type] = None,
    allow_empty: bool = False
) -> List[Any]:
    """
    Validate list input with comprehensive checks.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        min_items: Minimum number of items
        max_items: Maximum number of items
        item_type: Expected type for list items
        allow_empty: Whether empty lists are allowed
        
    Returns:
        Validated list
        
    Raises:
        ValidationError: If validation fails
    """
    if value is None:
        if allow_empty:
            return []
        raise ValidationError(
            f"{field_name} cannot be None",
            error_code="NULL_VALUE",
            details={"field_name": field_name, "value": value}
        )
    
    if not isinstance(value, (list, tuple)):
        raise ValidationError(
            f"{field_name} must be a list or tuple, got {type(value).__name__}",
            error_code="INVALID_TYPE",
            details={"field_name": field_name, "value": value, "expected_type": "list"}
        )
    
    value_list = list(value)
    
    if not value_list and not allow_empty:
        raise ValidationError(
            f"{field_name} cannot be empty",
            error_code="EMPTY_LIST",
            details={"field_name": field_name, "value": value_list}
        )
    
    if len(value_list) < min_items and (value_list or not allow_empty):
        raise ValidationError(
            f"{field_name} must have at least {min_items} items, got {len(value_list)}",
            error_code="TOO_FEW_ITEMS",
            details={"field_name": field_name, "value": value_list, "min_items": min_items}
        )
    
    if len(value_list) > max_items:
        raise ValidationError(
            f"{field_name} must have at most {max_items} items, got {len(value_list)}",
            error_code="TOO_MANY_ITEMS",
            details={"field_name": field_name, "value": value_list, "max_items": max_items}
        )
    
    if item_type:
        for i, item in enumerate(value_list):
            if not isinstance(item, item_type):
                raise ValidationError(
                    f"{field_name}[{i}] must be {item_type.__name__}, got {type(item).__name__}",
                    error_code="INVALID_ITEM_TYPE",
                    details={"field_name": field_name, "index": i, "item": item, "expected_type": item_type.__name__}
                )
    
    return value_list


def validate_numeric_input(
    value: Any,
    field_name: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    allow_negative: bool = True,
    allow_zero: bool = True
) -> float:
    """
    Validate numeric input with range checks.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        allow_negative: Whether negative values are allowed
        allow_zero: Whether zero is allowed
        
    Returns:
        Validated numeric value
        
    Raises:
        ValidationError: If validation fails
    """
    if value is None:
        raise ValidationError(
            f"{field_name} cannot be None",
            error_code="NULL_VALUE",
            details={"field_name": field_name, "value": value}
        )
    
    try:
        numeric_value = float(value)
    except (ValueError, TypeError) as e:
        raise ValidationError(
            f"{field_name} must be a number, got {type(value).__name__}",
            error_code="INVALID_NUMERIC_TYPE",
            details={"field_name": field_name, "value": value, "error": str(e)}
        )
    
    if not allow_negative and numeric_value < 0:
        raise ValidationError(
            f"{field_name} cannot be negative, got {numeric_value}",
            error_code="NEGATIVE_VALUE",
            details={"field_name": field_name, "value": numeric_value}
        )
    
    if not allow_zero and numeric_value == 0:
        raise ValidationError(
            f"{field_name} cannot be zero, got {numeric_value}",
            error_code="ZERO_VALUE",
            details={"field_name": field_name, "value": numeric_value}
        )
    
    if min_value is not None and numeric_value < min_value:
        raise ValidationError(
            f"{field_name} must be at least {min_value}, got {numeric_value}",
            error_code="VALUE_TOO_SMALL",
            details={"field_name": field_name, "value": numeric_value, "min_value": min_value}
        )
    
    if max_value is not None and numeric_value > max_value:
        raise ValidationError(
            f"{field_name} must be at most {max_value}, got {numeric_value}",
            error_code="VALUE_TOO_LARGE",
            details={"field_name": field_name, "value": numeric_value, "max_value": max_value}
        )
    
    return numeric_value


def validate_file_path_input(
    value: Any,
    field_name: str,
    must_exist: bool = True,
    must_be_file: bool = True,
    must_be_directory: bool = False,
    allowed_extensions: Optional[List[str]] = None
) -> Path:
    """
    Validate file path input with comprehensive checks.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        must_exist: Whether the path must exist
        must_be_file: Whether the path must be a file
        must_be_directory: Whether the path must be a directory
        allowed_extensions: List of allowed file extensions
        
    Returns:
        Validated Path object
        
    Raises:
        ValidationError: If validation fails
        FileOperationError: If file operation requirements not met
    """
    if value is None:
        raise ValidationError(
            f"{field_name} cannot be None",
            error_code="NULL_VALUE",
            details={"field_name": field_name, "value": value}
        )
    
    try:
        path_obj = Path(value)
    except Exception as e:
        raise ValidationError(
            f"{field_name} is not a valid path: {value}",
            error_code="INVALID_PATH",
            details={"field_name": field_name, "value": value, "error": str(e)}
        )
    
    if must_exist and not path_obj.exists():
        raise FileOperationError(
            f"{field_name} does not exist: {path_obj}",
            error_code="PATH_NOT_FOUND",
            details={"field_name": field_name, "path": str(path_obj)}
        )
    
    if must_be_file and path_obj.exists() and not path_obj.is_file():
        raise ValidationError(
            f"{field_name} must be a file, got directory: {path_obj}",
            error_code="NOT_A_FILE",
            details={"field_name": field_name, "path": str(path_obj)}
        )
    
    if must_be_directory and path_obj.exists() and not path_obj.is_dir():
        raise ValidationError(
            f"{field_name} must be a directory, got file: {path_obj}",
            error_code="NOT_A_DIRECTORY",
            details={"field_name": field_name, "path": str(path_obj)}
        )
    
    if allowed_extensions and path_obj.is_file():
        file_extension = path_obj.suffix.lower()
        if file_extension not in [ext.lower() for ext in allowed_extensions]:
            raise ValidationError(
                f"{field_name} must have one of these extensions: {allowed_extensions}, got {file_extension}",
                error_code="INVALID_EXTENSION",
                details={"field_name": field_name, "path": str(path_obj), "allowed_extensions": allowed_extensions}
            )
    
    return path_obj


def validate_script_input(script_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate script data structure and content.
    
    Args:
        script_data: Script data dictionary to validate
        
    Returns:
        Validated script data
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(script_data, dict):
        raise ValidationError(
            "Script data must be a dictionary",
            error_code="INVALID_SCRIPT_TYPE",
            details={"script_data": script_data}
        )
    
    required_fields = ["title", "script", "scene_descriptions"]
    for field in required_fields:
        if field not in script_data:
            raise ValidationError(
                f"Script data missing required field: {field}",
                error_code="MISSING_REQUIRED_FIELD",
                details={"field": field, "script_data": script_data}
            )
    
    # Validate title
    script_data["title"] = validate_string_input(
        script_data["title"], "title", min_length=1, max_length=100
    )
    
    # Validate script
    script_data["script"] = validate_string_input(
        script_data["script"], "script", min_length=10, max_length=2000
    )
    
    # Validate scene descriptions
    script_data["scene_descriptions"] = validate_list_input(
        script_data["scene_descriptions"], "scene_descriptions", 
        min_items=1, max_items=10, item_type=str
    )
    
    # Validate optional fields
    if "duration_seconds" in script_data:
        script_data["duration_seconds"] = validate_numeric_input(
            script_data["duration_seconds"], "duration_seconds",
            min_value=1.0, max_value=60.0
        )
    
    if "search_keywords" in script_data:
        script_data["search_keywords"] = validate_list_input(
            script_data["search_keywords"], "search_keywords",
            min_items=1, max_items=20, item_type=str
        )
    
    return script_data


def validate_video_specs(
    width: int,
    height: int,
    fps: float,
    duration: float
) -> Tuple[int, int, float, float]:
    """
    Validate video specifications for YouTube Shorts.
    
    Args:
        width: Video width
        height: Video height
        fps: Frames per second
        duration: Video duration in seconds
        
    Returns:
        Validated (width, height, fps, duration) tuple
        
    Raises:
        ValidationError: If validation fails
    """
    # Validate dimensions
    width = int(width)
    height = int(height)
    
    if width <= 0 or height <= 0:
        raise ValidationError(
            f"Video dimensions must be positive, got {width}x{height}",
            error_code="INVALID_DIMENSIONS",
            details={"width": width, "height": height}
        )
    
    # Check if dimensions are divisible by 8 (SD requirement)
    if width % 8 != 0 or height % 8 != 0:
        corrected_width = (width // 8) * 8
        corrected_height = (height // 8) * 8
        raise ValidationError(
            f"Video dimensions must be divisible by 8 for Stable Diffusion, got {width}x{height}, corrected to {corrected_width}x{corrected_height}",
            error_code="DIMENSIONS_NOT_DIVISIBLE_BY_8",
            details={"width": width, "height": height, "corrected_width": corrected_width, "corrected_height": corrected_height}
        )
    
    # Validate FPS
    fps = validate_numeric_input(fps, "fps", min_value=1.0, max_value=120.0)
    
    # Validate duration
    duration = validate_numeric_input(duration, "duration", min_value=1.0, max_value=60.0)
    
    return width, height, fps, duration


def validate_audio_specs(
    sample_rate: int,
    channels: int,
    duration: float
) -> Tuple[int, int, float]:
    """
    Validate audio specifications.
    
    Args:
        sample_rate: Audio sample rate in Hz
        channels: Number of audio channels
        duration: Audio duration in seconds
        
    Returns:
        Validated (sample_rate, channels, duration) tuple
        
    Raises:
        ValidationError: If validation fails
    """
    # Validate sample rate
    sample_rate = int(sample_rate)
    if sample_rate not in [8000, 16000, 22050, 44100, 48000]:
        raise ValidationError(
            f"Sample rate must be one of [8000, 16000, 22050, 44100, 48000], got {sample_rate}",
            error_code="INVALID_SAMPLE_RATE",
            details={"sample_rate": sample_rate}
        )
    
    # Validate channels
    channels = int(channels)
    if channels not in [1, 2]:
        raise ValidationError(
            f"Channels must be 1 or 2, got {channels}",
            error_code="INVALID_CHANNELS",
            details={"channels": channels}
        )
    
    # Validate duration
    duration = validate_numeric_input(duration, "duration", min_value=0.1, max_value=60.0)
    
    return sample_rate, channels, duration


def validate_api_key(api_key: str, provider: str) -> str:
    """
    Validate API key format and presence.
    
    Args:
        api_key: API key to validate
        provider: API provider name for error messages
        
    Returns:
        Validated API key
        
    Raises:
        ValidationError: If validation fails
    """
    api_key = validate_string_input(
        api_key, f"{provider} API key", min_length=10, max_length=200
    )
    
    # Basic format validation (most API keys are alphanumeric with some special chars)
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', api_key):
        raise ValidationError(
            f"{provider} API key contains invalid characters",
            error_code="INVALID_API_KEY_FORMAT",
            details={"provider": provider, "api_key_length": len(api_key)}
        )
    
    return api_key


def validate_environment_variables(required_vars: List[str]) -> Dict[str, str]:
    """
    Validate that required environment variables are set.
    
    Args:
        required_vars: List of required environment variable names
        
    Returns:
        Dictionary of validated environment variables
        
    Raises:
        ValidationError: If any required variables are missing
    """
    missing_vars = []
    validated_vars = {}
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or not value.strip():
            missing_vars.append(var)
        else:
            validated_vars[var] = value.strip()
    
    if missing_vars:
        raise ValidationError(
            f"Missing required environment variables: {missing_vars}",
            error_code="MISSING_ENV_VARS",
            details={"missing_vars": missing_vars, "required_vars": required_vars}
        )
    
    return validated_vars


def validate_youtube_shorts_content(
    title: str,
    description: str,
    script: str,
    duration: float,
    scene_descriptions: List[str]
) -> Dict[str, Any]:
    """
    Validate complete YouTube Shorts content for compliance.
    
    Args:
        title: Video title
        description: Video description
        script: Video script
        duration: Video duration
        scene_descriptions: List of scene descriptions
        
    Returns:
        Validated content dictionary
        
    Raises:
        ValidationError: If validation fails
    """
    # Validate title (YouTube limit is 100 characters)
    title = validate_string_input(title, "title", min_length=1, max_length=100)
    
    # Validate description (YouTube limit is 5000 characters)
    description = validate_string_input(description, "description", min_length=1, max_length=5000)
    
    # Validate script
    script = validate_string_input(script, "script", min_length=10, max_length=2000)
    
    # Validate duration (YouTube Shorts limit is 60 seconds)
    duration = validate_numeric_input(duration, "duration", min_value=1.0, max_value=60.0)
    
    # Validate scene descriptions
    scene_descriptions = validate_list_input(
        scene_descriptions, "scene_descriptions", 
        min_items=1, max_items=10, item_type=str
    )
    
    # Check for appropriate content length
    if len(script) < 50:
        raise ValidationError(
            "Script is too short for a meaningful YouTube Short (minimum 50 characters)",
            error_code="SCRIPT_TOO_SHORT",
            details={"script_length": len(script), "min_length": 50}
        )
    
    if duration < 3.0:
        raise ValidationError(
            "Duration is too short for a YouTube Short (minimum 3 seconds)",
            error_code="DURATION_TOO_SHORT",
            details={"duration": duration, "min_duration": 3.0}
        )
    
    return {
        "title": title,
        "description": description,
        "script": script,
        "duration": duration,
        "scene_descriptions": scene_descriptions
    }
