"""
Performance Optimization Utilities

Provides comprehensive performance optimizations for image/video processing,
caching strategies, and resource management.
"""

import functools
import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from settings.config import Config

logger = logging.getLogger(__name__)


class LRUCache:
    """Simple LRU cache implementation for expensive operations"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache = {}
        self.access_order = []
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key: str, value: Any) -> None:
        """Put value in cache"""
        if key in self.cache:
            # Update existing
            self.access_order.remove(key)
        elif len(self.cache) >= self.max_size:
            # Remove least recently used
            lru_key = self.access_order.pop(0)
            del self.cache[lru_key]
        
        self.cache[key] = value
        self.access_order.append(key)
    
    def clear(self) -> None:
        """Clear cache"""
        self.cache.clear()
        self.access_order.clear()
    
    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)


class DiskCache:
    """Disk-based cache for large objects"""
    
    def __init__(self, cache_dir: Union[str, Path] = None):
        self.cache_dir = Path(cache_dir or Config.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key"""
        # Use hash to avoid filesystem issues with special characters
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from disk cache"""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data.get('value')
            except Exception as e:
                logger.warning(f"Failed to read cache file {cache_path}: {e}")
        return None
    
    def put(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Put value in disk cache with TTL"""
        cache_path = self._get_cache_path(key)
        try:
            data = {
                'value': value,
                'timestamp': time.time(),
                'ttl': ttl
            }
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Failed to write cache file {cache_path}: {e}")
    
    def is_valid(self, key: str) -> bool:
        """Check if cached value is still valid"""
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return False
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            timestamp = data.get('timestamp', 0)
            ttl = data.get('ttl', 3600)
            
            return time.time() - timestamp < ttl
        except Exception:
            return False
    
    def clear_expired(self) -> int:
        """Clear expired cache entries"""
        cleared = 0
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                timestamp = data.get('timestamp', 0)
                ttl = data.get('ttl', 3600)
                
                if time.time() - timestamp >= ttl:
                    cache_file.unlink()
                    cleared += 1
            except Exception:
                # If we can't read it, delete it
                cache_file.unlink()
                cleared += 1
        
        return cleared


class PerformanceOptimizer:
    """Main performance optimization manager"""
    
    def __init__(self):
        self.memory_cache = LRUCache(max_size=200)
        self.disk_cache = DiskCache()
        self.operation_stats = {}
        
        # Clear expired disk cache on startup
        cleared = self.disk_cache.clear_expired()
        if cleared > 0:
            logger.info(f"Cleared {cleared} expired cache entries")
    
    def cache_result(self, cache_key: str, result: Any, 
                    use_disk: bool = False, ttl: int = 3600) -> None:
        """Cache a result"""
        if use_disk:
            self.disk_cache.put(cache_key, result, ttl)
        else:
            self.memory_cache.put(cache_key, result)
    
    def get_cached_result(self, cache_key: str, use_disk: bool = False) -> Optional[Any]:
        """Get cached result"""
        if use_disk:
            if self.disk_cache.is_valid(cache_key):
                return self.disk_cache.get(cache_key)
        else:
            return self.memory_cache.get(cache_key)
        return None
    
    def cached_function(self, cache_key_func: Callable = None, 
                       use_disk: bool = False, ttl: int = 3600):
        """Decorator for caching function results"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if cache_key_func:
                    cache_key = cache_key_func(*args, **kwargs)
                else:
                    # Default cache key generation
                    key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                    cache_key = hashlib.md5(key_data.encode()).hexdigest()
                
                # Try to get cached result
                cached_result = self.get_cached_result(cache_key, use_disk)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result
                
                # Execute function and cache result
                logger.debug(f"Cache miss for {func.__name__}, executing...")
                result = func(*args, **kwargs)
                self.cache_result(cache_key, result, use_disk, ttl)
                
                return result
            
            return wrapper
        return decorator
    
    def track_operation(self, operation_name: str, duration: float, 
                       success: bool = True) -> None:
        """Track operation performance"""
        if operation_name not in self.operation_stats:
            self.operation_stats[operation_name] = {
                'count': 0,
                'total_time': 0.0,
                'success_count': 0,
                'failure_count': 0
            }
        
        stats = self.operation_stats[operation_name]
        stats['count'] += 1
        stats['total_time'] += duration
        if success:
            stats['success_count'] += 1
        else:
            stats['failure_count'] += 1
    
    def get_performance_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics"""
        stats = {}
        for operation, data in self.operation_stats.items():
            avg_time = data['total_time'] / data['count'] if data['count'] > 0 else 0
            success_rate = data['success_count'] / data['count'] if data['count'] > 0 else 0
            
            stats[operation] = {
                'count': data['count'],
                'total_time': data['total_time'],
                'average_time': avg_time,
                'success_rate': success_rate,
                'success_count': data['success_count'],
                'failure_count': data['failure_count']
            }
        
        return stats


# Global performance optimizer
performance_optimizer = PerformanceOptimizer()


def optimize_stable_diffusion_settings() -> Dict[str, Any]:
    """Get optimized Stable Diffusion settings for performance"""
    return {
        'inference_steps': min(getattr(Config, 'SD_INFERENCE_STEPS', 20), 12),  # Reduce steps
        'guidance_scale': getattr(Config, 'SD_GUIDANCE_SCALE', 7.5),
        'width': getattr(Config, 'SD_GENERATION_WIDTH', 544),
        'height': getattr(Config, 'SD_GENERATION_HEIGHT', 960),
        'use_attention_slicing': True,
        'use_vae_slicing': True,
        'enable_memory_efficient_attention': True,
        'use_torch_compile': True,  # PyTorch 2.0+ optimization
        'batch_size': 1,  # Keep at 1 for memory efficiency
        'num_images_per_prompt': 1
    }


def optimize_ffmpeg_settings() -> Dict[str, Any]:
    """Get optimized FFmpeg settings for performance"""
    return {
        'use_hardware_acceleration': getattr(Config, 'USE_HARDWARE_ACCELERATION', True),
        'encoder': getattr(Config, 'HARDWARE_ENCODER', 'h264_nvenc'),
        'preset': getattr(Config, 'NVENC_PRESET', 'p1'),
        'tune': getattr(Config, 'NVENC_TUNE', 'ull'),
        'rc': getattr(Config, 'NVENC_RC', 'cbr'),
        'bitrate': getattr(Config, 'NVENC_BITRATE', '5M'),
        'max_bitrate': getattr(Config, 'NVENC_MAX_BITRATE', '8M'),
        'gop_size': getattr(Config, 'NVENC_GOP_SIZE', 30),
        'threads': getattr(Config, 'FFMPEG_THREADS', 0) or 0,
        'pixel_format': 'yuv420p',
        'fps': getattr(Config, 'VIDEO_FPS', 24)
    }


def optimize_ai_generation_settings() -> Dict[str, Any]:
    """Get optimized AI generation settings"""
    return {
        'max_tokens': min(getattr(Config, 'GROQ_MAX_TOKENS', 1000), 800),  # Reduce tokens
        'temperature': getattr(Config, 'GROQ_TEMPERATURE', 0.8),
        'timeout': 30,  # Shorter timeout for faster failure
        'retry_count': 2,  # Fewer retries
        'stream': False,  # Disable streaming for simplicity
        'cache_responses': True,  # Enable response caching
        'cache_ttl': 3600  # 1 hour cache
    }


def optimize_tts_settings() -> Dict[str, Any]:
    """Get optimized TTS settings"""
    return {
        'use_edge_tts': True,  # Prefer Edge TTS for speed
        'voice': getattr(Config, 'EDGE_TTS_VOICE', 'en-US-AriaNeural'),
        'rate': 1.0,  # Normal speed
        'pitch': 1.0,  # Normal pitch
        'volume': 1.0,  # Normal volume
        'cache_audio': True,  # Enable audio caching
        'cache_ttl': 7200  # 2 hour cache for audio
    }


def batch_process_items(items: List[Any], process_func: Callable, 
                       batch_size: int = 3, max_workers: int = 2) -> List[Any]:
    """Process items in batches for better performance"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    results = []
    
    # Process in batches
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit batch jobs
            future_to_item = {
                executor.submit(process_func, item): item 
                for item in batch
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_item):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Batch processing failed for item: {e}")
                    results.append(None)
    
    return results


def optimize_memory_usage() -> None:
    """Optimize memory usage by clearing caches and garbage collection"""
    import gc
    
    # Clear memory caches
    performance_optimizer.memory_cache.clear()
    
    # Clear expired disk cache
    cleared = performance_optimizer.disk_cache.clear_expired()
    if cleared > 0:
        logger.info(f"Cleared {cleared} expired cache entries")
    
    # Force garbage collection
    gc.collect()
    
    # Clear CUDA cache if available
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
    except ImportError:
        pass


def get_optimization_recommendations() -> List[str]:
    """Get performance optimization recommendations"""
    recommendations = []
    
    # Check GPU settings
    try:
        import torch
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            if gpu_memory < 8:
                recommendations.append(f"Consider upgrading GPU (current: {gpu_memory:.1f}GB)")
        else:
            recommendations.append("Install CUDA-compatible GPU for better performance")
    except ImportError:
        recommendations.append("Install PyTorch with CUDA support")
    
    # Check FFmpeg hardware acceleration
    try:
        from utils.video_utils import check_hardware_acceleration
        hw_accel = check_hardware_acceleration()
        if not hw_accel.get('nvenc', False):
            recommendations.append("Enable NVENC hardware acceleration for faster video encoding")
    except ImportError:
        pass
    
    # Check memory usage
    try:
        import psutil
        memory = psutil.virtual_memory()
        if memory.percent > 80:
            recommendations.append(f"High memory usage ({memory.percent:.1f}%) - consider closing other applications")
    except ImportError:
        pass
    
    # Check disk space
    try:
        import shutil
        free_space = shutil.disk_usage(Config.OUTPUT_DIR).free / (1024**3)
        if free_space < 5:
            recommendations.append(f"Low disk space ({free_space:.1f}GB) - consider cleaning up")
    except:
        pass
    
    return recommendations


if __name__ == "__main__":
    # Test performance optimizer
    print("=" * 60)
    print("PERFORMANCE OPTIMIZER TEST")
    print("=" * 60)
    
    # Test caching
    @performance_optimizer.cached_function(use_disk=False)
    def expensive_operation(x: int) -> int:
        time.sleep(0.1)  # Simulate expensive operation
        return x * x
    
    # First call (cache miss)
    start = time.time()
    result1 = expensive_operation(5)
    time1 = time.time() - start
    
    # Second call (cache hit)
    start = time.time()
    result2 = expensive_operation(5)
    time2 = time.time() - start
    
    print(f"First call: {result1} in {time1:.3f}s")
    print(f"Second call: {result2} in {time2:.3f}s")
    print(f"Speedup: {time1/time2:.1f}x")
    
    # Test optimization settings
    print(f"\nOptimized SD settings: {optimize_stable_diffusion_settings()}")
    print(f"Optimized FFmpeg settings: {optimize_ffmpeg_settings()}")
    print(f"Optimized AI settings: {optimize_ai_generation_settings()}")
    print(f"Optimized TTS settings: {optimize_tts_settings()}")
    
    # Test recommendations
    recommendations = get_optimization_recommendations()
    print(f"\nOptimization recommendations:")
    for rec in recommendations:
        print(f"  - {rec}")
    
    # Test performance stats
    performance_optimizer.track_operation("test_op", 0.1, True)
    stats = performance_optimizer.get_performance_stats()
    print(f"\nPerformance stats: {stats}")
    
    print("\nPerformance optimizer test completed!")
