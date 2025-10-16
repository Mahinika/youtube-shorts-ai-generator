"""
Error Handling Utilities

Provides standardized error handling, custom exceptions, and recovery strategies
across all modules in the YouTube Shorts automation system.
"""

import logging
import traceback
import functools
from typing import Any, Callable, Optional, Dict, List, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class YouTubeShortsError(Exception):
    """Base exception for all YouTube Shorts automation errors."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/serialization."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class AIGenerationError(YouTubeShortsError):
    """Errors related to AI generation (script, voice, images)."""
    pass


class VideoProcessingError(YouTubeShortsError):
    """Errors related to video processing and FFmpeg operations."""
    pass


class FileOperationError(YouTubeShortsError):
    """Errors related to file operations (reading, writing, validation)."""
    pass


class ConfigurationError(YouTubeShortsError):
    """Errors related to configuration and settings."""
    pass


class ResourceError(YouTubeShortsError):
    """Errors related to system resources (GPU, memory, disk space)."""
    pass


class NetworkError(YouTubeShortsError):
    """Errors related to network operations and API calls."""
    pass


class ValidationError(YouTubeShortsError):
    """Errors related to input validation and data integrity."""
    pass


class ErrorHandler:
    """
    Centralized error handling and recovery system.
    
    Provides consistent error handling patterns, logging, and recovery strategies
    across all modules.
    """
    
    def __init__(self, module_name: str = "unknown"):
        self.module_name = module_name
        self.logger = logging.getLogger(f"error_handler.{module_name}")
    
    def handle_error(
        self,
        error: Exception,
        context: str = "",
        recovery_strategy: Optional[Callable] = None,
        reraise: bool = True,
        log_level: int = logging.ERROR
    ) -> Any:
        """
        Handle an error with standardized logging and optional recovery.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            recovery_strategy: Optional function to attempt recovery
            reraise: Whether to reraise the exception after handling
            log_level: Logging level for the error
            
        Returns:
            Result of recovery strategy if successful, None otherwise
        """
        # Create error context
        error_context = {
            "module": self.module_name,
            "context": context,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc()
        }
        
        # Log the error
        self.logger.log(
            log_level,
            f"Error in {self.module_name}: {context} - {type(error).__name__}: {error}",
            extra=error_context
        )
        
        # Attempt recovery if strategy provided
        if recovery_strategy:
            try:
                self.logger.info(f"Attempting recovery strategy for {context}")
                result = recovery_strategy()
                self.logger.info(f"Recovery successful for {context}")
                return result
            except Exception as recovery_error:
                self.logger.error(f"Recovery failed for {context}: {recovery_error}")
        
        # Reraise if requested
        if reraise:
            raise
        
        return None
    
    def safe_execute(
        self,
        func: Callable,
        *args,
        context: str = "",
        fallback_value: Any = None,
        recovery_strategy: Optional[Callable] = None,
        **kwargs
    ) -> Any:
        """
        Safely execute a function with error handling and fallback.
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            context: Context description for error logging
            fallback_value: Value to return if function fails and no recovery
            recovery_strategy: Optional recovery function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Function result, recovery result, or fallback value
        """
        try:
            return func(*args, **kwargs)
        except Exception as error:
            self.logger.warning(f"Function {func.__name__} failed in {context}: {error}")
            
            # Try recovery strategy
            if recovery_strategy:
                try:
                    return recovery_strategy()
                except Exception as recovery_error:
                    self.logger.error(f"Recovery strategy failed: {recovery_error}")
            
            return fallback_value


def error_handler(module_name: str = "unknown", reraise: bool = True, recovery_strategy: Optional[Callable] = None):
    """
    Decorator for standardized error handling on functions.
    
    Args:
        module_name: Name of the module for error context
        reraise: Whether to reraise exceptions after handling
        recovery_strategy: Optional recovery function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            handler = ErrorHandler(module_name)
            try:
                return func(*args, **kwargs)
            except Exception as error:
                return handler.handle_error(
                    error=error,
                    context=f"{func.__name__}",
                    recovery_strategy=recovery_strategy,
                    reraise=reraise
                )
        return wrapper
    return decorator


def validate_file_path(path: Union[str, Path], must_exist: bool = True) -> Path:
    """
    Validate file path and raise appropriate errors.
    
    Args:
        path: File path to validate
        must_exist: Whether the file must exist
        
    Returns:
        Validated Path object
        
    Raises:
        ValidationError: If path validation fails
        FileOperationError: If file doesn't exist when required
    """
    try:
        path_obj = Path(path)
        
        if not path_obj.is_absolute():
            path_obj = path_obj.resolve()
        
        if must_exist and not path_obj.exists():
            raise FileOperationError(
                f"File does not exist: {path_obj}",
                error_code="FILE_NOT_FOUND",
                details={"path": str(path_obj), "must_exist": must_exist}
            )
        
        return path_obj
        
    except Exception as error:
        if isinstance(error, (ValidationError, FileOperationError)):
            raise
        raise ValidationError(
            f"Invalid file path: {path}",
            error_code="INVALID_PATH",
            details={"path": str(path), "error": str(error)}
        )


def validate_duration(duration: Union[int, float], min_duration: float = 0.0, max_duration: float = 60.0) -> float:
    """
    Validate duration value for video/audio content.
    
    Args:
        duration: Duration to validate
        min_duration: Minimum allowed duration
        max_duration: Maximum allowed duration
        
    Returns:
        Validated duration as float
        
    Raises:
        ValidationError: If duration is invalid
    """
    try:
        duration_float = float(duration)
        
        if duration_float < min_duration:
            raise ValidationError(
                f"Duration {duration_float}s is below minimum {min_duration}s",
                error_code="DURATION_TOO_SHORT",
                details={"duration": duration_float, "min_duration": min_duration}
            )
        
        if duration_float > max_duration:
            raise ValidationError(
                f"Duration {duration_float}s exceeds maximum {max_duration}s",
                error_code="DURATION_TOO_LONG",
                details={"duration": duration_float, "max_duration": max_duration}
            )
        
        return duration_float
        
    except (ValueError, TypeError) as error:
        raise ValidationError(
            f"Invalid duration value: {duration}",
            error_code="INVALID_DURATION",
            details={"duration": duration, "error": str(error)}
        )


def validate_image_dimensions(width: int, height: int, min_size: int = 64, max_size: int = 4096) -> tuple:
    """
    Validate image dimensions for Stable Diffusion compatibility.
    
    Args:
        width: Image width
        height: Image height
        min_size: Minimum dimension size
        max_size: Maximum dimension size
        
    Returns:
        Validated (width, height) tuple
        
    Raises:
        ValidationError: If dimensions are invalid
    """
    try:
        width_int = int(width)
        height_int = int(height)
        
        if width_int < min_size or height_int < min_size:
            raise ValidationError(
                f"Image dimensions {width_int}x{height_int} below minimum {min_size}x{min_size}",
                error_code="DIMENSIONS_TOO_SMALL",
                details={"width": width_int, "height": height_int, "min_size": min_size}
            )
        
        if width_int > max_size or height_int > max_size:
            raise ValidationError(
                f"Image dimensions {width_int}x{height_int} exceed maximum {max_size}x{max_size}",
                error_code="DIMENSIONS_TOO_LARGE",
                details={"width": width_int, "height": height_int, "max_size": max_size}
            )
        
        # Check if dimensions are divisible by 8 (SD requirement)
        if width_int % 8 != 0 or height_int % 8 != 0:
            # Auto-correct to nearest multiple of 8
            corrected_width = (width_int // 8) * 8
            corrected_height = (height_int // 8) * 8
            logger.warning(f"Corrected dimensions from {width_int}x{height_int} to {corrected_width}x{corrected_height} (SD requirement)")
            return corrected_width, corrected_height
        
        return width_int, height_int
        
    except (ValueError, TypeError) as error:
        raise ValidationError(
            f"Invalid image dimensions: {width}x{height}",
            error_code="INVALID_DIMENSIONS",
            details={"width": width, "height": height, "error": str(error)}
        )


def create_error_context(operation: str, **kwargs) -> Dict[str, Any]:
    """
    Create standardized error context dictionary.
    
    Args:
        operation: Description of the operation
        **kwargs: Additional context data
        
    Returns:
        Error context dictionary
    """
    return {
        "operation": operation,
        "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None)),
        **kwargs
    }


def log_error_with_context(logger: logging.Logger, error: Exception, context: Dict[str, Any]):
    """
    Log error with structured context information.
    
    Args:
        logger: Logger instance to use
        error: Exception that occurred
        context: Context information dictionary
    """
    logger.error(
        f"Error in {context.get('operation', 'unknown operation')}: {type(error).__name__}: {error}",
        extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            **context
        }
    )


# Convenience functions for common error patterns
def handle_ai_generation_error(error: Exception, context: str = "") -> None:
    """Handle AI generation errors with appropriate logging and recovery."""
    handler = ErrorHandler("ai_generation")
    handler.handle_error(
        error=error,
        context=context,
        reraise=False,
        log_level=logging.ERROR
    )


def handle_video_processing_error(error: Exception, context: str = "") -> None:
    """Handle video processing errors with appropriate logging and recovery."""
    handler = ErrorHandler("video_processing")
    handler.handle_error(
        error=error,
        context=context,
        reraise=False,
        log_level=logging.ERROR
    )


def handle_file_operation_error(error: Exception, context: str = "") -> None:
    """Handle file operation errors with appropriate logging and recovery."""
    handler = ErrorHandler("file_operations")
    handler.handle_error(
        error=error,
        context=context,
        reraise=False,
        log_level=logging.ERROR
    )
