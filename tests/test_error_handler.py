"""
Unit tests for error handling utilities.

Tests the comprehensive error handling system including custom exceptions,
error context creation, and the error_handler decorator.
"""

import pytest
import logging
from unittest.mock import patch, MagicMock
from io import StringIO

from utils.error_handler import (
    AIGenerationError,
    ResourceError,
    VideoProcessingError,
    FileOperationError,
    ValidationError,
    create_error_context,
    log_error_with_context,
    error_handler,
    validate_duration,
    validate_image_dimensions
)


class TestCustomExceptions:
    """Test custom exception classes."""
    
    def test_ai_generation_error(self):
        """Test AIGenerationError exception."""
        error = AIGenerationError("AI generation failed", "GENERATION_ERROR", {"model": "test"})
        assert str(error) == "AI generation failed"
        assert error.error_code == "GENERATION_ERROR"
        assert error.details == {"model": "test"}
    
    def test_resource_error(self):
        """Test ResourceError exception."""
        error = ResourceError("GPU memory exhausted", "GPU_OOM", {"vram_used": "6GB"})
        assert str(error) == "GPU memory exhausted"
        assert error.error_code == "GPU_OOM"
        assert error.details == {"vram_used": "6GB"}
    
    def test_video_processing_error(self):
        """Test VideoProcessingError exception."""
        error = VideoProcessingError("FFmpeg failed", "FFMPEG_ERROR", {"command": "ffmpeg -i input.mp4"})
        assert str(error) == "FFmpeg failed"
        assert error.error_code == "FFMPEG_ERROR"
        assert error.details == {"command": "ffmpeg -i input.mp4"}
    
    def test_file_operation_error(self):
        """Test FileOperationError exception."""
        error = FileOperationError("File not found", "FILE_NOT_FOUND", {"path": "/tmp/file.txt"})
        assert str(error) == "File not found"
        assert error.error_code == "FILE_NOT_FOUND"
        assert error.details == {"path": "/tmp/file.txt"}
    
    def test_validation_error(self):
        """Test ValidationError exception."""
        error = ValidationError("Invalid input", "INVALID_INPUT", {"field": "title"})
        assert str(error) == "Invalid input"
        assert error.error_code == "INVALID_INPUT"
        assert error.details == {"field": "title"}


class TestErrorContext:
    """Test error context creation and logging."""
    
    def test_create_error_context(self):
        """Test error context creation."""
        context = create_error_context(
            operation="test_operation",
            error_code="TEST_ERROR",
            details={"param1": "value1", "param2": 42}
        )
        
        assert context["operation"] == "test_operation"
        assert context["error_code"] == "TEST_ERROR"
        assert context["details"] == {"param1": "value1", "param2": 42}
        assert "timestamp" in context
        assert "context_id" in context
    
    def test_log_error_with_context(self):
        """Test error logging with context."""
        # Capture log output
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger("test_logger")
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)
        
        context = create_error_context(
            operation="test_operation",
            error_code="TEST_ERROR",
            details={"param1": "value1"}
        )
        
        log_error_with_context(logger, "Test error message", context)
        
        log_output = log_capture.getvalue()
        assert "Test error message" in log_output
        assert "test_operation" in log_output
        assert "TEST_ERROR" in log_output
        assert "param1" in log_output


class TestErrorHandlerDecorator:
    """Test the error_handler decorator."""
    
    def test_successful_execution(self):
        """Test decorator with successful execution."""
        @error_handler("test_operation", reraise=False)
        def test_func():
            return "success"
        
        result = test_func()
        assert result == "success"
    
    def test_exception_handling_without_reraising(self):
        """Test decorator with exception handling without reraising."""
        @error_handler("test_operation", reraise=False)
        def test_func():
            raise ValueError("Test error")
        
        result = test_func()
        assert result is None
    
    def test_exception_handling_with_reraising(self):
        """Test decorator with exception handling and reraising."""
        @error_handler("test_operation", reraise=True)
        def test_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError) as exc_info:
            test_func()
        assert "Test error" in str(exc_info.value)
    
    def test_custom_exception_handling(self):
        """Test decorator with custom exception handling."""
        @error_handler("test_operation", reraise=True)
        def test_func():
            raise AIGenerationError("AI failed", "AI_ERROR", {"model": "test"})
        
        with pytest.raises(AIGenerationError) as exc_info:
            test_func()
        assert exc_info.value.error_code == "AI_ERROR"
    
    def test_logging_with_decorator(self):
        """Test that decorator logs errors properly."""
        # Capture log output
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger("test_operation")
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)
        
        @error_handler("test_operation", reraise=False)
        def test_func():
            raise ValueError("Test error")
        
        test_func()
        
        log_output = log_capture.getvalue()
        assert "Test error" in log_output
        assert "test_operation" in log_output


class TestValidationFunctions:
    """Test validation utility functions."""
    
    def test_validate_duration_valid(self):
        """Test valid duration validation."""
        result = validate_duration(15.5, "test_duration")
        assert result == 15.5
    
    def test_validate_duration_string_conversion(self):
        """Test duration validation with string input."""
        result = validate_duration("15.5", "test_duration")
        assert result == 15.5
    
    def test_validate_duration_negative(self):
        """Test duration validation with negative value."""
        with pytest.raises(ValidationError) as exc_info:
            validate_duration(-5.0, "test_duration")
        assert "cannot be negative" in str(exc_info.value)
    
    def test_validate_duration_zero(self):
        """Test duration validation with zero value."""
        with pytest.raises(ValidationError) as exc_info:
            validate_duration(0.0, "test_duration")
        assert "cannot be zero" in str(exc_info.value)
    
    def test_validate_duration_too_long(self):
        """Test duration validation with too long value."""
        with pytest.raises(ValidationError) as exc_info:
            validate_duration(300.0, "test_duration", max_duration=60.0)
        assert "cannot exceed 60.0 seconds" in str(exc_info.value)
    
    def test_validate_image_dimensions_valid(self):
        """Test valid image dimensions validation."""
        width, height = validate_image_dimensions(1080, 1920, "test_image")
        assert width == 1080
        assert height == 1920
    
    def test_validate_image_dimensions_negative(self):
        """Test image dimensions validation with negative values."""
        with pytest.raises(ValidationError) as exc_info:
            validate_image_dimensions(-1080, 1920, "test_image")
        assert "cannot be negative" in str(exc_info.value)
    
    def test_validate_image_dimensions_not_divisible_by_8(self):
        """Test image dimensions validation with values not divisible by 8."""
        with pytest.raises(ValidationError) as exc_info:
            validate_image_dimensions(1081, 1921, "test_image")
        assert "must be divisible by 8" in str(exc_info.value)
    
    def test_validate_image_dimensions_too_small(self):
        """Test image dimensions validation with too small values."""
        with pytest.raises(ValidationError) as exc_info:
            validate_image_dimensions(64, 64, "test_image", min_width=128, min_height=128)
        assert "must be at least 128x128" in str(exc_info.value)
    
    def test_validate_image_dimensions_too_large(self):
        """Test image dimensions validation with too large values."""
        with pytest.raises(ValidationError) as exc_info:
            validate_image_dimensions(4096, 4096, "test_image", max_width=2048, max_height=2048)
        assert "must be at most 2048x2048" in str(exc_info.value)


class TestErrorHandlerIntegration:
    """Test error handler integration with other components."""
    
    def test_error_handler_with_validation_error(self):
        """Test error handler with ValidationError."""
        @error_handler("validation_test", reraise=True)
        def test_func():
            raise ValidationError("Invalid input", "INVALID_INPUT", {"field": "test"})
        
        with pytest.raises(ValidationError) as exc_info:
            test_func()
        assert exc_info.value.error_code == "INVALID_INPUT"
    
    def test_error_handler_with_resource_error(self):
        """Test error handler with ResourceError."""
        @error_handler("resource_test", reraise=True)
        def test_func():
            raise ResourceError("GPU memory exhausted", "GPU_OOM", {"vram": "6GB"})
        
        with pytest.raises(ResourceError) as exc_info:
            test_func()
        assert exc_info.value.error_code == "GPU_OOM"
    
    def test_error_handler_with_multiple_exceptions(self):
        """Test error handler with multiple exception types."""
        @error_handler("multi_test", reraise=True)
        def test_func(exception_type):
            if exception_type == "validation":
                raise ValidationError("Validation failed", "VALIDATION_ERROR")
            elif exception_type == "resource":
                raise ResourceError("Resource failed", "RESOURCE_ERROR")
            elif exception_type == "ai":
                raise AIGenerationError("AI failed", "AI_ERROR")
            else:
                raise ValueError("Unknown error")
        
        # Test ValidationError
        with pytest.raises(ValidationError) as exc_info:
            test_func("validation")
        assert exc_info.value.error_code == "VALIDATION_ERROR"
        
        # Test ResourceError
        with pytest.raises(ResourceError) as exc_info:
            test_func("resource")
        assert exc_info.value.error_code == "RESOURCE_ERROR"
        
        # Test AIGenerationError
        with pytest.raises(AIGenerationError) as exc_info:
            test_func("ai")
        assert exc_info.value.error_code == "AI_ERROR"
        
        # Test generic ValueError
        with pytest.raises(ValueError) as exc_info:
            test_func("unknown")
        assert "Unknown error" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__])
