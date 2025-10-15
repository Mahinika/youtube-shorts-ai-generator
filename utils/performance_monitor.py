"""
Performance monitoring utilities for the YouTube Shorts generation project.
"""

import time
import functools
from typing import Callable, Any
from .logging_config import get_logger

logger = get_logger("performance")


def monitor_performance(func: Callable) -> Callable:
    """
    Decorator to monitor function performance.

    Args:
        func: Function to monitor

    Returns:
        Wrapped function that logs performance metrics
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"{func.__name__} completed successfully in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.2f}s: {e}")
            raise
    return wrapper


def time_function(func: Callable, *args, **kwargs) -> tuple:
    """
    Time a function execution.

    Args:
        func: Function to time
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Tuple of (result, duration_seconds)
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    duration = time.time() - start_time
    return result, duration


class PerformanceTracker:
    """Tracks performance metrics across multiple operations."""

    def __init__(self):
        self.metrics = {}

    def start_operation(self, operation_name: str):
        """Start tracking an operation."""
        self.metrics[operation_name] = {
            'start_time': time.time(),
            'status': 'running'
        }
        logger.debug(f"Started operation: {operation_name}")

    def end_operation(self, operation_name: str, success: bool = True):
        """End tracking an operation."""
        if operation_name in self.metrics:
            duration = time.time() - self.metrics[operation_name]['start_time']
            self.metrics[operation_name].update({
                'end_time': time.time(),
                'duration': duration,
                'status': 'completed' if success else 'failed'
            })
            logger.info(f"Operation {operation_name} {'completed' if success else 'failed'} in {duration:.2f}s")
        else:
            logger.warning(f"Attempted to end untracked operation: {operation_name}")

    def get_metrics(self) -> dict:
        """Get all performance metrics."""
        return self.metrics.copy()

    def get_operation_duration(self, operation_name: str) -> float:
        """Get duration of a specific operation."""
        if operation_name in self.metrics:
            return self.metrics[operation_name].get('duration', 0.0)
        return 0.0

    def reset(self):
        """Reset all metrics."""
        self.metrics.clear()
        logger.debug("Performance metrics reset")


# Global performance tracker instance
performance_tracker = PerformanceTracker()
