"""
Resource Management Utilities

Provides context managers and utilities for proper resource cleanup
in the YouTube Shorts automation system.
"""

import os
import gc
import tempfile
import logging
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Generator, ContextManager
from contextlib import contextmanager, ExitStack
import torch

from utils.error_handler import ResourceError, ValidationError
from utils.logging_utils import get_logger

logger = get_logger(__name__)


class ResourceManager:
    """
    Centralized resource management for the YouTube Shorts automation system.
    
    Provides context managers and utilities for proper cleanup of:
    - GPU memory and CUDA resources
    - Temporary files and directories
    - Network connections and API clients
    - File handles and streams
    - Background threads and processes
    """
    
    def __init__(self):
        """Initialize resource manager."""
        self.active_resources: Dict[str, Any] = {}
        self.cleanup_callbacks: List[callable] = []
        self._lock = threading.Lock()
    
    def register_resource(self, name: str, resource: Any, cleanup_func: Optional[callable] = None) -> None:
        """
        Register a resource for tracking and cleanup.
        
        Args:
            name: Unique name for the resource
            resource: The resource object
            cleanup_func: Optional cleanup function for the resource
        """
        with self._lock:
            self.active_resources[name] = {
                'resource': resource,
                'cleanup_func': cleanup_func,
                'created_at': time.time()
            }
            logger.debug(f"Registered resource: {name}")
    
    def unregister_resource(self, name: str) -> None:
        """
        Unregister a resource.
        
        Args:
            name: Name of the resource to unregister
        """
        with self._lock:
            if name in self.active_resources:
                del self.active_resources[name]
                logger.debug(f"Unregistered resource: {name}")
    
    def cleanup_resource(self, name: str) -> bool:
        """
        Cleanup a specific resource.
        
        Args:
            name: Name of the resource to cleanup
            
        Returns:
            True if cleanup was successful, False otherwise
        """
        with self._lock:
            if name not in self.active_resources:
                return False
            
            resource_info = self.active_resources[name]
            resource = resource_info['resource']
            cleanup_func = resource_info['cleanup_func']
            
            try:
                if cleanup_func:
                    cleanup_func(resource)
                else:
                    # Default cleanup based on resource type
                    self._default_cleanup(resource)
                
                del self.active_resources[name]
                logger.debug(f"Cleaned up resource: {name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to cleanup resource {name}: {e}")
                return False
    
    def cleanup_all(self) -> int:
        """
        Cleanup all registered resources.
        
        Returns:
            Number of resources successfully cleaned up
        """
        with self._lock:
            cleaned_count = 0
            resource_names = list(self.active_resources.keys())
            
            for name in resource_names:
                if self.cleanup_resource(name):
                    cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count}/{len(resource_names)} resources")
            return cleaned_count
    
    def _default_cleanup(self, resource: Any) -> None:
        """Default cleanup logic based on resource type."""
        if hasattr(resource, 'close'):
            resource.close()
        elif hasattr(resource, 'cleanup'):
            resource.cleanup()
        elif hasattr(resource, 'shutdown'):
            resource.shutdown()
        elif isinstance(resource, (list, tuple)):
            for item in resource:
                self._default_cleanup(item)
        elif isinstance(resource, dict):
            for value in resource.values():
                self._default_cleanup(value)


@contextmanager
def gpu_memory_context(clear_cache: bool = True) -> Generator[None, None, None]:
    """
    Context manager for GPU memory operations.
    
    Ensures proper cleanup of GPU memory and CUDA resources.
    
    Args:
        clear_cache: Whether to clear CUDA cache on exit
    """
    logger.debug("Entering GPU memory context")
    
    try:
        yield
    finally:
        if clear_cache and torch.cuda.is_available():
            try:
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
                gc.collect()
                logger.debug("Cleared GPU memory cache")
            except Exception as e:
                logger.warning(f"Failed to clear GPU cache: {e}")


@contextmanager
def temp_file_context(suffix: str = ".tmp", prefix: str = "temp_", delete: bool = True) -> Generator[Path, None, None]:
    """
    Context manager for temporary files.
    
    Args:
        suffix: File suffix
        prefix: File prefix
        delete: Whether to delete file on exit
        
    Yields:
        Path to temporary file
    """
    temp_file = None
    temp_path = None
    
    try:
        temp_file = tempfile.NamedTemporaryFile(
            suffix=suffix, prefix=prefix, delete=False
        )
        temp_path = Path(temp_file.name)
        temp_file.close()
        
        logger.debug(f"Created temporary file: {temp_path}")
        yield temp_path
        
    finally:
        if temp_path and temp_path.exists() and delete:
            try:
                temp_path.unlink()
                logger.debug(f"Cleaned up temporary file: {temp_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temporary file {temp_path}: {e}")


@contextmanager
def temp_directory_context(prefix: str = "temp_") -> Generator[Path, None, None]:
    """
    Context manager for temporary directories.
    
    Args:
        prefix: Directory prefix
        
    Yields:
        Path to temporary directory
    """
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        temp_path = Path(temp_dir)
        
        logger.debug(f"Created temporary directory: {temp_path}")
        yield temp_path
        
    finally:
        if temp_dir and Path(temp_dir).exists():
            try:
                import shutil
                shutil.rmtree(temp_dir)
                logger.debug(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temporary directory {temp_dir}: {e}")


@contextmanager
def file_handle_context(file_path: Union[str, Path], mode: str = 'r', encoding: str = 'utf-8') -> Generator[Any, None, None]:
    """
    Context manager for file handles.
    
    Args:
        file_path: Path to the file
        mode: File open mode
        encoding: File encoding
        
    Yields:
        File handle
    """
    file_handle = None
    
    try:
        file_handle = open(file_path, mode, encoding=encoding)
        logger.debug(f"Opened file handle: {file_path}")
        yield file_handle
        
    finally:
        if file_handle:
            try:
                file_handle.close()
                logger.debug(f"Closed file handle: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to close file handle {file_path}: {e}")


@contextmanager
def process_context(command: List[str], **kwargs) -> Generator[Any, None, None]:
    """
    Context manager for subprocess operations.
    
    Args:
        command: Command to execute
        **kwargs: Additional subprocess arguments
        
    Yields:
        Subprocess object
    """
    process = None
    
    try:
        import subprocess
        process = subprocess.Popen(command, **kwargs)
        logger.debug(f"Started process: {' '.join(command)}")
        yield process
        
    finally:
        if process:
            try:
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                logger.debug(f"Terminated process: {' '.join(command)}")
            except Exception as e:
                logger.warning(f"Failed to terminate process: {e}")


@contextmanager
def api_client_context(client_class: type, *args, **kwargs) -> Generator[Any, None, None]:
    """
    Context manager for API clients.
    
    Args:
        client_class: API client class
        *args: Arguments for client initialization
        **kwargs: Keyword arguments for client initialization
        
    Yields:
        API client instance
    """
    client = None
    
    try:
        client = client_class(*args, **kwargs)
        logger.debug(f"Created API client: {client_class.__name__}")
        yield client
        
    finally:
        if client:
            try:
                if hasattr(client, 'close'):
                    client.close()
                elif hasattr(client, 'cleanup'):
                    client.cleanup()
                elif hasattr(client, 'shutdown'):
                    client.shutdown()
                logger.debug(f"Cleaned up API client: {client_class.__name__}")
            except Exception as e:
                logger.warning(f"Failed to cleanup API client: {e}")


class ManagedResource:
    """
    Base class for managed resources with automatic cleanup.
    """
    
    def __init__(self, name: str, cleanup_func: Optional[callable] = None):
        """
        Initialize managed resource.
        
        Args:
            name: Resource name
            cleanup_func: Cleanup function
        """
        self.name = name
        self.cleanup_func = cleanup_func
        self._is_cleaned_up = False
    
    def __enter__(self):
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager with cleanup."""
        self.cleanup()
    
    def cleanup(self) -> None:
        """Cleanup the resource."""
        if self._is_cleaned_up:
            return
        
        try:
            if self.cleanup_func:
                self.cleanup_func()
            logger.debug(f"Cleaned up managed resource: {self.name}")
        except Exception as e:
            logger.error(f"Failed to cleanup managed resource {self.name}: {e}")
        finally:
            self._is_cleaned_up = True
    
    def __del__(self):
        """Destructor with cleanup."""
        self.cleanup()


class GPUResource(ManagedResource):
    """
    Managed GPU resource with automatic memory cleanup.
    """
    
    def __init__(self, name: str = "gpu_resource"):
        """Initialize GPU resource."""
        super().__init__(name, self._cleanup_gpu)
    
    def _cleanup_gpu(self) -> None:
        """Cleanup GPU resources."""
        if torch.cuda.is_available():
            try:
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
                gc.collect()
            except Exception as e:
                logger.warning(f"Failed to cleanup GPU resources: {e}")


class FileResource(ManagedResource):
    """
    Managed file resource with automatic cleanup.
    """
    
    def __init__(self, file_path: Union[str, Path], name: Optional[str] = None):
        """
        Initialize file resource.
        
        Args:
            file_path: Path to the file
            name: Resource name (defaults to file path)
        """
        self.file_path = Path(file_path)
        super().__init__(name or str(file_path), self._cleanup_file)
    
    def _cleanup_file(self) -> None:
        """Cleanup file resource."""
        if self.file_path.exists():
            try:
                self.file_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to cleanup file {self.file_path}: {e}")


def cleanup_on_exit(func: callable) -> callable:
    """
    Decorator to register cleanup function for execution on exit.
    
    Args:
        func: Cleanup function to register
        
    Returns:
        Decorated function
    """
    import atexit
    atexit.register(func)
    return func


def with_resource_cleanup(cleanup_func: callable) -> callable:
    """
    Decorator to ensure resource cleanup after function execution.
    
    Args:
        cleanup_func: Cleanup function to call
        
    Returns:
        Decorated function
    """
    def decorator(func: callable) -> callable:
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            finally:
                try:
                    cleanup_func()
                except Exception as e:
                    logger.warning(f"Cleanup function failed: {e}")
        return wrapper
    return decorator


# Global resource manager instance
_resource_manager = ResourceManager()


def get_resource_manager() -> ResourceManager:
    """Get the global resource manager instance."""
    return _resource_manager


def cleanup_all_resources() -> int:
    """Cleanup all registered resources."""
    return _resource_manager.cleanup_all()


# Register cleanup on exit
cleanup_on_exit(cleanup_all_resources)
