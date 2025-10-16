"""
Enhanced Logging Utilities

Provides standardized logging with performance metrics, structured logging,
and consistent formatting across all modules.
"""

import logging
import time
import functools
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Callable
import traceback

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.logging_config import setup_logging, get_logger

# Global logger instance
logger = get_logger("youtube_shorts")


class PerformanceLogger:
    """Logger that tracks performance metrics"""
    
    def __init__(self, name: str = "performance"):
        self.logger = get_logger(name)
        self.start_times = {}
        self.operation_counts = {}
        self.total_times = {}
    
    def start_operation(self, operation_name: str) -> None:
        """Start timing an operation"""
        self.start_times[operation_name] = time.time()
        self.operation_counts[operation_name] = self.operation_counts.get(operation_name, 0) + 1
        self.logger.debug(f"Starting operation: {operation_name}")
    
    def end_operation(self, operation_name: str, success: bool = True) -> float:
        """End timing an operation and log results"""
        if operation_name not in self.start_times:
            self.logger.warning(f"Operation {operation_name} was not started")
            return 0.0
        
        duration = time.time() - self.start_times[operation_name]
        del self.start_times[operation_name]
        
        # Update totals
        self.total_times[operation_name] = self.total_times.get(operation_name, 0.0) + duration
        
        # Log result
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"Operation {operation_name} {status} in {duration:.2f}s")
        
        return duration
    
    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics"""
        stats = {}
        for operation, count in self.operation_counts.items():
            total_time = self.total_times.get(operation, 0.0)
            avg_time = total_time / count if count > 0 else 0.0
            stats[operation] = {
                "count": count,
                "total_time": total_time,
                "average_time": avg_time
            }
        return stats


# Global performance logger
performance_logger = PerformanceLogger()


def log_function_call(func: Callable) -> Callable:
    """Decorator to log function calls with timing"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = f"{func.__module__}.{func.__name__}"
        performance_logger.start_operation(func_name)
        
        try:
            result = func(*args, **kwargs)
            performance_logger.end_operation(func_name, success=True)
            return result
        except Exception as e:
            performance_logger.end_operation(func_name, success=False)
            logger.error(f"Function {func_name} failed: {e}")
            raise
    
    return wrapper


def log_step(step_name: str, description: str = ""):
    """Decorator to log step execution with context"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Starting {step_name}: {description}")
            performance_logger.start_operation(step_name)
            
            try:
                result = func(*args, **kwargs)
                performance_logger.end_operation(step_name, success=True)
                logger.info(f"Completed {step_name} successfully")
                return result
            except Exception as e:
                performance_logger.end_operation(step_name, success=False)
                logger.error(f"Step {step_name} failed: {e}")
                logger.debug(f"Traceback: {traceback.format_exc()}")
                raise
        
        return wrapper
    return decorator


def log_ai_generation(provider: str, model: str = ""):
    """Decorator to log AI generation calls"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            model_info = f" ({model})" if model else ""
            logger.info(f"AI Generation with {provider}{model_info}")
            performance_logger.start_operation(f"ai_generation_{provider}")
            
            try:
                result = func(*args, **kwargs)
                performance_logger.end_operation(f"ai_generation_{provider}", success=True)
                logger.info(f"AI Generation successful with {provider}")
                return result
            except Exception as e:
                performance_logger.end_operation(f"ai_generation_{provider}", success=False)
                logger.error(f"AI Generation failed with {provider}: {e}")
                raise
        
        return wrapper
    return decorator


def log_gpu_operation(operation: str):
    """Decorator to log GPU operations with memory info"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"GPU Operation: {operation}")
            performance_logger.start_operation(f"gpu_{operation}")
            
            try:
                result = func(*args, **kwargs)
                performance_logger.end_operation(f"gpu_{operation}", success=True)
                logger.info(f"GPU Operation {operation} completed successfully")
                return result
            except Exception as e:
                performance_logger.end_operation(f"gpu_{operation}", success=False)
                logger.error(f"GPU Operation {operation} failed: {e}")
                raise
        
        return wrapper
    return decorator


def log_file_operation(operation: str, file_path: str = ""):
    """Decorator to log file operations"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            file_info = f" ({file_path})" if file_path else ""
            logger.info(f"File Operation: {operation}{file_info}")
            performance_logger.start_operation(f"file_{operation}")
            
            try:
                result = func(*args, **kwargs)
                performance_logger.end_operation(f"file_{operation}", success=True)
                logger.info(f"File Operation {operation} completed successfully")
                return result
            except Exception as e:
                performance_logger.end_operation(f"file_{operation}", success=False)
                logger.error(f"File Operation {operation} failed: {e}")
                raise
        
        return wrapper
    return decorator


class StructuredLogger:
    """Logger that provides structured logging with context"""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
        self.context = {}
    
    def set_context(self, **kwargs) -> None:
        """Set logging context"""
        self.context.update(kwargs)
    
    def clear_context(self) -> None:
        """Clear logging context"""
        self.context.clear()
    
    def _format_message(self, message: str, **kwargs) -> str:
        """Format message with context"""
        context_str = " | ".join(f"{k}={v}" for k, v in {**self.context, **kwargs}.items())
        return f"{message} | {context_str}" if context_str else message
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with context"""
        self.logger.debug(self._format_message(message, **kwargs))
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with context"""
        self.logger.info(self._format_message(message, **kwargs))
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with context"""
        self.logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with context"""
        self.logger.error(self._format_message(message, **kwargs))
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with context"""
        self.logger.critical(self._format_message(message, **kwargs))


def get_structured_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance"""
    return StructuredLogger(name)


def log_system_info() -> None:
    """Log system information for debugging"""
    import platform
    import psutil
    
    logger.info("System Information:")
    logger.info(f"  Platform: {platform.platform()}")
    logger.info(f"  Python: {platform.python_version()}")
    logger.info(f"  CPU Cores: {psutil.cpu_count()}")
    logger.info(f"  Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    
    # Check GPU if available
    try:
        import torch
        if torch.cuda.is_available():
            logger.info(f"  GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"  GPU Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
        else:
            logger.info("  GPU: Not available")
    except ImportError:
        logger.info("  GPU: PyTorch not available")


def log_performance_summary() -> None:
    """Log performance summary"""
    stats = performance_logger.get_stats()
    
    if not stats:
        logger.info("No performance data available")
        return
    
    logger.info("Performance Summary:")
    for operation, data in stats.items():
        logger.info(f"  {operation}: {data['count']} calls, "
                   f"{data['total_time']:.2f}s total, "
                   f"{data['average_time']:.2f}s average")


def replace_print_with_logging(module_name: str) -> None:
    """Replace print statements with logging in a module"""
    import sys
    import builtins
    
    original_print = builtins.print
    
    def logging_print(*args, **kwargs):
        """Replacement print function that logs instead"""
        message = " ".join(str(arg) for arg in args)
        logger.info(f"[{module_name}] {message}")
    
    # Monkey patch print for the module
    builtins.print = logging_print


if __name__ == "__main__":
    # Test logging utilities
    print("=" * 60)
    print("LOGGING UTILITIES TEST")
    print("=" * 60)
    
    # Test basic logging
    logger.info("Testing basic logging")
    logger.warning("Testing warning message")
    logger.error("Testing error message")
    
    # Test performance logging
    performance_logger.start_operation("test_operation")
    time.sleep(0.1)  # Simulate work
    performance_logger.end_operation("test_operation")
    
    # Test structured logging
    structured_logger = get_structured_logger("test")
    structured_logger.set_context(step="test", user="test_user")
    structured_logger.info("Testing structured logging")
    
    # Test decorators
    @log_function_call
    def test_function():
        time.sleep(0.05)
        return "success"
    
    @log_step("test_step", "Testing step logging")
    def test_step():
        time.sleep(0.05)
        return "step_success"
    
    # Run tests
    test_function()
    test_step()
    
    # Log system info
    log_system_info()
    
    # Log performance summary
    log_performance_summary()
    
    print("Logging utilities test completed!")
