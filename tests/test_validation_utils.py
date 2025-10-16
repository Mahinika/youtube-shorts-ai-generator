"""
Unit tests for validation utilities.

Tests the comprehensive input validation functions used throughout
the YouTube Shorts automation system.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from utils.validation_utils import (
    validate_string_input,
    validate_list_input,
    validate_numeric_input,
    validate_file_path_input,
    validate_script_input,
    validate_video_specs,
    validate_audio_specs,
    validate_youtube_shorts_content
)
from utils.error_handler import ValidationError, FileOperationError


class TestValidateStringInput:
    """Test string input validation."""
    
    def test_valid_string(self):
        """Test valid string input."""
        result = validate_string_input("Hello World", "test_field")
        assert result == "Hello World"
    
    def test_empty_string_not_allowed(self):
        """Test empty string validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_string_input("", "test_field")
        assert "cannot be empty" in str(exc_info.value)
    
    def test_empty_string_allowed(self):
        """Test empty string when allowed."""
        result = validate_string_input("", "test_field", allow_empty=True)
        assert result == ""
    
    def test_none_value(self):
        """Test None value handling."""
        with pytest.raises(ValidationError) as exc_info:
            validate_string_input(None, "test_field")
        assert "cannot be None" in str(exc_info.value)
    
    def test_min_length_validation(self):
        """Test minimum length validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_string_input("Hi", "test_field", min_length=5)
        assert "must be at least 5 characters" in str(exc_info.value)
    
    def test_max_length_validation(self):
        """Test maximum length validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_string_input("A" * 101, "test_field", max_length=100)
        assert "must be at most 100 characters" in str(exc_info.value)
    
    def test_pattern_validation(self):
        """Test regex pattern validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_string_input("invalid@email", "email", pattern=r"^[a-zA-Z0-9]+$")
        assert "does not match required pattern" in str(exc_info.value)
    
    def test_type_conversion(self):
        """Test automatic type conversion."""
        result = validate_string_input(123, "test_field")
        assert result == "123"


class TestValidateListInput:
    """Test list input validation."""
    
    def test_valid_list(self):
        """Test valid list input."""
        result = validate_list_input(["a", "b", "c"], "test_field")
        assert result == ["a", "b", "c"]
    
    def test_empty_list_not_allowed(self):
        """Test empty list validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_list_input([], "test_field")
        assert "cannot be empty" in str(exc_info.value)
    
    def test_empty_list_allowed(self):
        """Test empty list when allowed."""
        result = validate_list_input([], "test_field", allow_empty=True)
        assert result == []
    
    def test_min_items_validation(self):
        """Test minimum items validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_list_input(["a"], "test_field", min_items=3)
        assert "must have at least 3 items" in str(exc_info.value)
    
    def test_max_items_validation(self):
        """Test maximum items validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_list_input(["a"] * 11, "test_field", max_items=10)
        assert "must have at most 10 items" in str(exc_info.value)
    
    def test_item_type_validation(self):
        """Test item type validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_list_input(["a", 123, "c"], "test_field", item_type=str)
        assert "must be str" in str(exc_info.value)
    
    def test_tuple_conversion(self):
        """Test tuple to list conversion."""
        result = validate_list_input(("a", "b", "c"), "test_field")
        assert result == ["a", "b", "c"]


class TestValidateNumericInput:
    """Test numeric input validation."""
    
    def test_valid_number(self):
        """Test valid numeric input."""
        result = validate_numeric_input(42, "test_field")
        assert result == 42.0
    
    def test_string_conversion(self):
        """Test string to number conversion."""
        result = validate_numeric_input("42", "test_field")
        assert result == 42.0
    
    def test_none_value(self):
        """Test None value handling."""
        with pytest.raises(ValidationError) as exc_info:
            validate_numeric_input(None, "test_field")
        assert "cannot be None" in str(exc_info.value)
    
    def test_min_value_validation(self):
        """Test minimum value validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_numeric_input(5, "test_field", min_value=10)
        assert "must be at least 10" in str(exc_info.value)
    
    def test_max_value_validation(self):
        """Test maximum value validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_numeric_input(15, "test_field", max_value=10)
        assert "must be at most 10" in str(exc_info.value)
    
    def test_negative_not_allowed(self):
        """Test negative value validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_numeric_input(-5, "test_field", allow_negative=False)
        assert "cannot be negative" in str(exc_info.value)
    
    def test_zero_not_allowed(self):
        """Test zero value validation."""
        with pytest.raises(ValidationError) as exc_info:
            validate_numeric_input(0, "test_field", allow_zero=False)
        assert "cannot be zero" in str(exc_info.value)
    
    def test_invalid_type(self):
        """Test invalid type handling."""
        with pytest.raises(ValidationError) as exc_info:
            validate_numeric_input("not_a_number", "test_field")
        assert "must be a number" in str(exc_info.value)


class TestValidateFilePathInput:
    """Test file path input validation."""
    
    def test_valid_file_path(self):
        """Test valid file path."""
        with tempfile.NamedTemporaryFile() as tmp:
            result = validate_file_path_input(tmp.name, "test_field")
            assert result == Path(tmp.name)
    
    def test_none_value(self):
        """Test None value handling."""
        with pytest.raises(ValidationError) as exc_info:
            validate_file_path_input(None, "test_field")
        assert "cannot be None" in str(exc_info.value)
    
    def test_file_not_exists_when_required(self):
        """Test file existence validation."""
        with pytest.raises(FileOperationError) as exc_info:
            validate_file_path_input("/nonexistent/file.txt", "test_field", must_exist=True)
        assert "does not exist" in str(exc_info.value)
    
    def test_file_not_exists_when_not_required(self):
        """Test file existence when not required."""
        result = validate_file_path_input("/nonexistent/file.txt", "test_field", must_exist=False)
        assert result == Path("/nonexistent/file.txt")
    
    def test_directory_when_file_required(self):
        """Test directory when file is required."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with pytest.raises(ValidationError) as exc_info:
                validate_file_path_input(tmp_dir, "test_field", must_be_file=True)
            assert "must be a file" in str(exc_info.value)
    
    def test_file_when_directory_required(self):
        """Test file when directory is required."""
        with tempfile.NamedTemporaryFile() as tmp:
            with pytest.raises(ValidationError) as exc_info:
                validate_file_path_input(tmp.name, "test_field", must_be_directory=True)
            assert "must be a directory" in str(exc_info.value)
    
    def test_extension_validation(self):
        """Test file extension validation."""
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            with pytest.raises(ValidationError) as exc_info:
                validate_file_path_input(tmp.name, "test_field", allowed_extensions=[".pdf"])
            assert "must have one of these extensions" in str(exc_info.value)


class TestValidateScriptInput:
    """Test script input validation."""
    
    def test_valid_script_data(self):
        """Test valid script data."""
        script_data = {
            "title": "Test Title",
            "script": "This is a test script with enough content to be valid.",
            "scene_descriptions": ["Scene 1", "Scene 2"]
        }
        result = validate_script_input(script_data)
        assert result["title"] == "Test Title"
        assert result["script"] == "This is a test script with enough content to be valid."
        assert result["scene_descriptions"] == ["Scene 1", "Scene 2"]
    
    def test_missing_required_fields(self):
        """Test missing required fields."""
        script_data = {"title": "Test Title"}
        with pytest.raises(ValidationError) as exc_info:
            validate_script_input(script_data)
        assert "missing required field" in str(exc_info.value)
    
    def test_invalid_type(self):
        """Test invalid data type."""
        with pytest.raises(ValidationError) as exc_info:
            validate_script_input("not_a_dict")
        assert "must be a dictionary" in str(exc_info.value)
    
    def test_optional_fields(self):
        """Test optional fields validation."""
        script_data = {
            "title": "Test Title",
            "script": "This is a test script with enough content to be valid.",
            "scene_descriptions": ["Scene 1", "Scene 2"],
            "duration_seconds": 30.5,
            "search_keywords": ["test", "keywords"]
        }
        result = validate_script_input(script_data)
        assert result["duration_seconds"] == 30.5
        assert result["search_keywords"] == ["test", "keywords"]


class TestValidateVideoSpecs:
    """Test video specifications validation."""
    
    def test_valid_video_specs(self):
        """Test valid video specifications."""
        width, height, fps, duration = validate_video_specs(1080, 1920, 30.0, 15.0)
        assert width == 1080
        assert height == 1920
        assert fps == 30.0
        assert duration == 15.0
    
    def test_dimensions_not_divisible_by_8(self):
        """Test dimensions not divisible by 8."""
        with pytest.raises(ValidationError) as exc_info:
            validate_video_specs(1081, 1921, 30.0, 15.0)
        assert "must be divisible by 8" in str(exc_info.value)
    
    def test_invalid_fps(self):
        """Test invalid FPS."""
        with pytest.raises(ValidationError) as exc_info:
            validate_video_specs(1080, 1920, 0.5, 15.0)
        assert "must be at least 1.0" in str(exc_info.value)
    
    def test_invalid_duration(self):
        """Test invalid duration."""
        with pytest.raises(ValidationError) as exc_info:
            validate_video_specs(1080, 1920, 30.0, 0.5)
        assert "must be at least 1.0" in str(exc_info.value)


class TestValidateAudioSpecs:
    """Test audio specifications validation."""
    
    def test_valid_audio_specs(self):
        """Test valid audio specifications."""
        sample_rate, channels, duration = validate_audio_specs(44100, 2, 15.0)
        assert sample_rate == 44100
        assert channels == 2
        assert duration == 15.0
    
    def test_invalid_sample_rate(self):
        """Test invalid sample rate."""
        with pytest.raises(ValidationError) as exc_info:
            validate_audio_specs(48001, 2, 15.0)
        assert "must be one of" in str(exc_info.value)
    
    def test_invalid_channels(self):
        """Test invalid channels."""
        with pytest.raises(ValidationError) as exc_info:
            validate_audio_specs(44100, 3, 15.0)
        assert "must be 1 or 2" in str(exc_info.value)
    
    def test_invalid_duration(self):
        """Test invalid duration."""
        with pytest.raises(ValidationError) as exc_info:
            validate_audio_specs(44100, 2, 0.05)
        assert "must be at least 0.1" in str(exc_info.value)


class TestValidateYouTubeShortsContent:
    """Test YouTube Shorts content validation."""
    
    def test_valid_content(self):
        """Test valid YouTube Shorts content."""
        content = {
            "title": "Amazing Facts About Space",
            "description": "Discover incredible facts about space exploration and astronomy.",
            "script": "Welcome to our space facts! Did you know that the sun is actually a star? It's so massive that it contains 99.86% of the solar system's mass!",
            "duration": 15.0,
            "scene_descriptions": ["Space scene", "Star field", "Planet view"]
        }
        result = validate_youtube_shorts_content(**content)
        assert result["title"] == "Amazing Facts About Space"
        assert result["script"] == content["script"]
        assert result["duration"] == 15.0
    
    def test_title_too_long(self):
        """Test title length validation."""
        content = {
            "title": "A" * 101,  # Too long
            "description": "Test description",
            "script": "This is a test script with enough content to be valid for YouTube Shorts.",
            "duration": 15.0,
            "scene_descriptions": ["Scene 1", "Scene 2"]
        }
        with pytest.raises(ValidationError) as exc_info:
            validate_youtube_shorts_content(**content)
        assert "must be at most 100 characters" in str(exc_info.value)
    
    def test_script_too_short(self):
        """Test script length validation."""
        content = {
            "title": "Test Title",
            "description": "Test description",
            "script": "This is a short script.",  # Too short for YouTube Shorts
            "duration": 15.0,
            "scene_descriptions": ["Scene 1", "Scene 2"]
        }
        with pytest.raises(ValidationError) as exc_info:
            validate_youtube_shorts_content(**content)
        assert "Script is too short for a meaningful YouTube Short" in str(exc_info.value)
    
    def test_duration_too_short(self):
        """Test duration validation."""
        content = {
            "title": "Test Title",
            "description": "Test description",
            "script": "This is a test script with enough content to be valid for YouTube Shorts.",
            "duration": 2.0,  # Too short
            "scene_descriptions": ["Scene 1", "Scene 2"]
        }
        with pytest.raises(ValidationError) as exc_info:
            validate_youtube_shorts_content(**content)
        assert "too short for a YouTube Short" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__])
