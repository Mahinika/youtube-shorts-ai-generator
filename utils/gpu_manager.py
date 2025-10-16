"""
GPU Memory Management Utility

Provides comprehensive GPU memory management with context managers,
VRAM monitoring, and OOM prevention for Stable Diffusion operations.
"""

import gc
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

from settings.config import Config
from utils.error_handler import ResourceError, ValidationError
from utils.resource_manager import gpu_memory_context, GPUResource

logger = logging.getLogger(__name__)


class GPUMemoryError(Exception):
    """Raised when GPU memory operations fail"""
    pass


class GPUMemoryManager:
    """Comprehensive GPU memory management with monitoring and optimization"""
    
    def __init__(self, device: str = "cuda", safety_margin_gb: float = 1.0):
        """
        Initialize GPU memory manager
        
        Args:
            device: CUDA device to manage
            safety_margin_gb: Safety margin in GB to prevent OOM
        """
        self.device = device
        self.safety_margin_gb = safety_margin_gb
        self.is_available = TORCH_AVAILABLE and torch.cuda.is_available()
        self.initial_memory = self.get_memory_info() if self.is_available else None
        self.peak_memory = 0.0
        
        if self.is_available:
            logger.info(f"GPU Memory Manager initialized on {torch.cuda.get_device_name(0)}")
            logger.info(f"Total VRAM: {self.get_total_memory():.1f} GB")
        else:
            logger.warning("CUDA not available - GPU memory management disabled")
    
    def get_total_memory(self) -> float:
        """Get total GPU memory in GB"""
        if not self.is_available:
            return 0.0
        return torch.cuda.get_device_properties(0).total_memory / (1024**3)
    
    def get_memory_info(self) -> Dict[str, float]:
        """Get current GPU memory usage info"""
        if not self.is_available:
            return {"allocated": 0.0, "cached": 0.0, "free": 0.0, "total": 0.0}
        
        allocated = torch.cuda.memory_allocated() / (1024**3)
        cached = torch.cuda.memory_reserved() / (1024**3)
        total = self.get_total_memory()
        free = total - allocated
        
        return {
            "allocated": allocated,
            "cached": cached,
            "free": free,
            "total": total
        }
    
    def get_memory_usage_percent(self) -> float:
        """Get memory usage as percentage"""
        if not self.is_available:
            return 0.0
        info = self.get_memory_info()
        return (info["allocated"] / info["total"]) * 100
    
    def is_memory_available(self, required_gb: float) -> bool:
        """Check if enough memory is available"""
        if not self.is_available:
            return False
        
        info = self.get_memory_info()
        available = info["free"] - self.safety_margin_gb
        return available >= required_gb
    
    def clear_cache(self, aggressive: bool = False) -> None:
        """Clear GPU memory cache"""
        if not self.is_available:
            return
        
        logger.debug("Clearing GPU cache...")
        
        # Standard cleanup
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        torch.cuda.synchronize()
        gc.collect()
        
        if aggressive:
            # More aggressive cleanup
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            torch.cuda.synchronize()
            gc.collect()
            
            # Force garbage collection multiple times
            for _ in range(3):
                gc.collect()
        
        # Update peak memory tracking
        current_allocated = torch.cuda.memory_allocated() / (1024**3)
        self.peak_memory = max(self.peak_memory, current_allocated)
        
        info = self.get_memory_info()
        logger.debug(f"GPU Memory after cleanup: {info['allocated']:.1f} GB allocated, {info['free']:.1f} GB free")
    
    def reset_state(self) -> None:
        """Completely reset GPU state"""
        if not self.is_available:
            return
        
        logger.info("Resetting GPU state...")
        
        # Clear all caches
        self.clear_cache(aggressive=True)
        
        # Reset peak memory tracking
        self.peak_memory = 0.0
        
        # Log final state
        info = self.get_memory_info()
        logger.info(f"GPU state reset - Memory: {info['allocated']:.1f} GB allocated, {info['free']:.1f} GB free")
    
    def check_memory_health(self) -> bool:
        """Check if GPU memory is in a healthy state"""
        if not self.is_available:
            return True
        
        info = self.get_memory_info()
        usage_percent = self.get_memory_usage_percent()
        
        # Check for potential issues
        if usage_percent > 90:
            logger.warning(f"High GPU memory usage: {usage_percent:.1f}%")
            return False
        
        if info["free"] < self.safety_margin_gb:
            logger.warning(f"Low free GPU memory: {info['free']:.1f} GB")
            return False
        
        return True
    
    def optimize_for_generation(self) -> None:
        """Optimize GPU state for image generation"""
        if not self.is_available:
            return
        
        logger.debug("Optimizing GPU for generation...")
        
        # Clear cache before generation
        self.clear_cache()
        
        # Check memory health
        if not self.check_memory_health():
            logger.warning("GPU memory health check failed - performing aggressive cleanup")
            self.clear_cache(aggressive=True)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        if not self.is_available:
            return {"available": False}
        
        info = self.get_memory_info()
        return {
            "available": True,
            "device": torch.cuda.get_device_name(0),
            "total_gb": info["total"],
            "allocated_gb": info["allocated"],
            "cached_gb": info["cached"],
            "free_gb": info["free"],
            "usage_percent": self.get_memory_usage_percent(),
            "peak_allocated_gb": self.peak_memory,
            "safety_margin_gb": self.safety_margin_gb
        }


@contextmanager
def gpu_memory_context(required_gb: float = 2.0, cleanup_after: bool = True):
    """
    Context manager for GPU memory operations
    
    Args:
        required_gb: Required memory in GB
        cleanup_after: Whether to cleanup after context exit
    """
    manager = GPUMemoryManager()
    
    if not manager.is_available:
        logger.warning("GPU not available - skipping memory management")
        yield manager
        return
    
    try:
        # Check if enough memory is available
        if not manager.is_memory_available(required_gb):
            logger.warning(f"Insufficient GPU memory for {required_gb} GB operation")
            manager.clear_cache(aggressive=True)
            
            if not manager.is_memory_available(required_gb):
                raise GPUMemoryError(f"Not enough GPU memory available for {required_gb} GB operation")
        
        # Optimize for operation
        manager.optimize_for_generation()
        
        yield manager
        
    finally:
        if cleanup_after:
            manager.clear_cache()
            logger.debug("GPU memory context cleanup completed")


def get_gpu_info() -> Dict[str, Any]:
    """Get comprehensive GPU information"""
    if not TORCH_AVAILABLE or not torch.cuda.is_available():
        return {"available": False, "reason": "CUDA not available"}
    
    try:
        device = torch.cuda.current_device()
        props = torch.cuda.get_device_properties(device)
        
        return {
            "available": True,
            "device_name": props.name,
            "compute_capability": f"{props.major}.{props.minor}",
            "total_memory_gb": props.total_memory / (1024**3),
            "multiprocessor_count": props.multi_processor_count,
            "max_threads_per_block": getattr(props, 'max_threads_per_block', 1024),
            "max_threads_per_multiprocessor": getattr(props, 'max_threads_per_multiprocessor', 2048),
            "memory_clock_rate": getattr(props, 'memory_clock_rate', 0),
            "memory_bus_width": getattr(props, 'memory_bus_width', 0)
        }
    except Exception as e:
        logger.error(f"Error getting GPU info: {e}")
        return {"available": False, "reason": str(e)}


def check_gpu_compatibility() -> Tuple[bool, str]:
    """
    Check if GPU is compatible with Stable Diffusion
    
    Returns:
        Tuple of (is_compatible, reason)
    """
    gpu_info = get_gpu_info()
    
    if not gpu_info["available"]:
        return False, gpu_info.get("reason", "GPU not available")
    
    # Check minimum memory requirement (4GB)
    min_memory_gb = 4.0
    if gpu_info["total_memory_gb"] < min_memory_gb:
        return False, f"Insufficient VRAM: {gpu_info['total_memory_gb']:.1f} GB < {min_memory_gb} GB required"
    
    # Check compute capability (minimum 6.0 for modern PyTorch)
    try:
        major, minor = map(int, gpu_info["compute_capability"].split("."))
        if major < 6 or (major == 6 and minor < 0):
            return False, f"Unsupported compute capability: {gpu_info['compute_capability']} (minimum 6.0 required)"
    except (ValueError, AttributeError):
        return False, "Could not determine compute capability"
    
    return True, "GPU is compatible"


# Global GPU manager instance
_gpu_manager: Optional[GPUMemoryManager] = None


def get_gpu_manager() -> GPUMemoryManager:
    """Get global GPU manager instance"""
    global _gpu_manager
    if _gpu_manager is None:
        _gpu_manager = GPUMemoryManager()
    return _gpu_manager


def reset_gpu_state() -> None:
    """Reset global GPU state (convenience function)"""
    manager = get_gpu_manager()
    manager.reset_state()


def clear_gpu_cache() -> None:
    """Clear GPU cache (convenience function)"""
    manager = get_gpu_manager()
    manager.clear_cache()


if __name__ == "__main__":
    # Test GPU manager
    print("=" * 60)
    print("GPU MEMORY MANAGER TEST")
    print("=" * 60)
    
    # Check GPU compatibility
    compatible, reason = check_gpu_compatibility()
    print(f"GPU Compatible: {compatible}")
    if not compatible:
        print(f"Reason: {reason}")
        exit(1)
    
    # Get GPU info
    gpu_info = get_gpu_info()
    print(f"\nGPU Info:")
    for key, value in gpu_info.items():
        print(f"  {key}: {value}")
    
    # Test memory manager
    manager = GPUMemoryManager()
    print(f"\nMemory Manager Stats:")
    stats = manager.get_memory_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test context manager
    print(f"\nTesting memory context...")
    with gpu_memory_context(required_gb=1.0) as ctx:
        print(f"  Context active - Memory: {ctx.get_memory_info()['allocated']:.1f} GB")
    
    print("\nTest completed successfully!")
