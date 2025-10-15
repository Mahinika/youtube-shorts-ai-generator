"""
ADVANCED OPTIMIZATIONS FOR YOUTUBE SHORTS MAKER

This module implements advanced optimizations to maximize performance:
- Memory management and cleanup
- Parallel processing where possible
- Intelligent caching
- Resource monitoring
"""

import gc
import threading
import time
from pathlib import Path
from typing import List, Optional
import psutil

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class PerformanceOptimizer:
    """Advanced performance optimization manager"""
    
    def __init__(self):
        self.memory_threshold = 0.8  # 80% memory usage threshold
        self.gpu_memory_threshold = 0.85  # 85% GPU memory threshold
        self.cleanup_interval = 5  # Cleanup every 5 operations
        
    def aggressive_memory_cleanup(self):
        """Aggressive memory cleanup for optimal performance"""
        print("  [OPTIMIZATION] Performing aggressive memory cleanup...")
        
        # Python garbage collection
        collected = gc.collect()
        print(f"    Python GC: Collected {collected} objects")
        
        # GPU memory cleanup
        if TORCH_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            torch.cuda.synchronize()
            
            # Get memory stats
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            
            print(f"    GPU Memory: {allocated:.1f}GB allocated, {reserved:.1f}GB reserved")
            
            # Force cleanup if memory is high
            if allocated > 3.0:  # More than 3GB allocated
                print("    [WARNING] High GPU memory usage, forcing cleanup...")
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
                torch.cuda.synchronize()
                
                # Clear any cached models
                if hasattr(torch, '_C'):
                    torch._C._cuda_emptyCache()
        
        # System memory cleanup
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > 80:
            print(f"    [WARNING] High system memory usage: {memory_percent:.1f}%")
            # Force garbage collection
            for _ in range(3):
                gc.collect()
    
    def check_system_resources(self) -> dict:
        """Check current system resource usage"""
        stats = {}
        
        # System memory
        memory = psutil.virtual_memory()
        stats['system_memory_percent'] = memory.percent
        stats['system_memory_available_gb'] = memory.available / 1024**3
        
        # GPU memory
        if TORCH_AVAILABLE and torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            
            stats['gpu_memory_allocated_gb'] = allocated
            stats['gpu_memory_reserved_gb'] = reserved
            stats['gpu_memory_total_gb'] = total
            stats['gpu_memory_percent'] = (allocated / total) * 100
        else:
            stats['gpu_memory_allocated_gb'] = 0
            stats['gpu_memory_percent'] = 0
        
        # CPU usage
        stats['cpu_percent'] = psutil.cpu_percent(interval=1)
        
        return stats
    
    def should_optimize(self) -> bool:
        """Determine if optimization is needed based on resource usage"""
        stats = self.check_system_resources()
        
        # Check if we need optimization
        needs_optimization = (
            stats['system_memory_percent'] > 75 or
            stats['gpu_memory_percent'] > 70 or
            stats['cpu_percent'] > 80
        )
        
        if needs_optimization:
            print(f"  [OPTIMIZATION NEEDED] Memory: {stats['system_memory_percent']:.1f}%, "
                  f"GPU: {stats['gpu_memory_percent']:.1f}%, CPU: {stats['cpu_percent']:.1f}%")
        
        return needs_optimization
    
    def optimize_for_generation(self):
        """Prepare system for optimal generation performance"""
        print("  [OPTIMIZATION] Preparing system for generation...")
        
        # Clean up before starting
        self.aggressive_memory_cleanup()
        
        # Check if we need to reduce quality for performance
        stats = self.check_system_resources()
        
        if stats['gpu_memory_percent'] > 60:
            print("  [OPTIMIZATION] GPU memory high, using aggressive settings")
            return "aggressive"
        elif stats['system_memory_percent'] > 70:
            print("  [OPTIMIZATION] System memory high, using conservative settings")
            return "conservative"
        else:
            print("  [OPTIMIZATION] Resources optimal, using standard settings")
            return "standard"
    
    def cleanup_after_generation(self):
        """Clean up after generation is complete"""
        print("  [OPTIMIZATION] Post-generation cleanup...")
        self.aggressive_memory_cleanup()


class ParallelProcessor:
    """Handle parallel processing where possible"""
    
    def __init__(self):
        self.threads = []
    
    def can_run_parallel(self) -> bool:
        """Check if parallel processing is feasible"""
        stats = psutil.virtual_memory()
        return stats.percent < 70  # Only if memory usage is below 70%
    
    def run_voice_and_ai_parallel(self, voice_func, ai_func, voice_args, ai_args):
        """Run voice generation and AI background generation in parallel"""
        if not self.can_run_parallel():
            print("  [OPTIMIZATION] Sequential processing (high memory usage)")
            # Run sequentially
            voice_result = voice_func(*voice_args)
            ai_result = ai_func(*ai_args)
            return voice_result, ai_result
        
        print("  [OPTIMIZATION] Parallel processing enabled")
        
        voice_result = [None]
        ai_result = [None]
        
        def voice_thread():
            voice_result[0] = voice_func(*voice_args)
        
        def ai_thread():
            ai_result[0] = ai_func(*ai_args)
        
        # Start both threads
        voice_t = threading.Thread(target=voice_thread)
        ai_t = threading.Thread(target=ai_thread)
        
        voice_t.start()
        ai_t.start()
        
        # Wait for both to complete
        voice_t.join()
        ai_t.join()
        
        return voice_result[0], ai_result[0]


class IntelligentCaching:
    """Intelligent caching system for frequently used resources"""
    
    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_metadata = {}
    
    def get_cache_key(self, content_type: str, content_hash: str) -> str:
        """Generate cache key for content"""
        return f"{content_type}_{content_hash}"
    
    def is_cached(self, cache_key: str) -> bool:
        """Check if content is cached"""
        cache_file = self.cache_dir / f"{cache_key}.cache"
        return cache_file.exists()
    
    def get_cached(self, cache_key: str) -> Optional[bytes]:
        """Get cached content"""
        cache_file = self.cache_dir / f"{cache_key}.cache"
        if cache_file.exists():
            return cache_file.read_bytes()
        return None
    
    def cache_content(self, cache_key: str, content: bytes):
        """Cache content"""
        cache_file = self.cache_dir / f"{cache_key}.cache"
        cache_file.write_bytes(content)
        
        # Update metadata
        self.cache_metadata[cache_key] = {
            'size': len(content),
            'created': time.time()
        }
    
    def cleanup_old_cache(self, max_age_hours: int = 24):
        """Clean up old cache files"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        for cache_file in self.cache_dir.glob("*.cache"):
            if cache_file.stat().st_mtime < cutoff_time:
                cache_file.unlink()
                print(f"  [CACHE] Removed old cache: {cache_file.name}")


# Global optimization instances
performance_optimizer = PerformanceOptimizer()
parallel_processor = ParallelProcessor()
intelligent_cache = IntelligentCaching("D:/YouTubeShortsProject/cache")


def optimize_before_generation():
    """Optimize system before starting generation"""
    return performance_optimizer.optimize_for_generation()


def optimize_after_generation():
    """Clean up after generation"""
    performance_optimizer.cleanup_after_generation()


def run_parallel_voice_and_ai(voice_func, ai_func, voice_args, ai_args):
    """Run voice and AI generation in parallel if possible"""
    return parallel_processor.run_voice_and_ai_parallel(
        voice_func, ai_func, voice_args, ai_args
    )


def get_system_stats() -> dict:
    """Get current system statistics"""
    return performance_optimizer.check_system_resources()


if __name__ == "__main__":
    print("Advanced Optimizations Module")
    print("=" * 50)
    
    # Test optimization system
    print("\nTesting performance optimization...")
    mode = optimize_before_generation()
    print(f"Optimization mode: {mode}")
    
    # Show system stats
    stats = get_system_stats()
    print(f"\nSystem Stats:")
    print(f"  System Memory: {stats['system_memory_percent']:.1f}%")
    print(f"  GPU Memory: {stats['gpu_memory_percent']:.1f}%")
    print(f"  CPU Usage: {stats['cpu_percent']:.1f}%")
    
    optimize_after_generation()
    print("\nOptimization test complete!")
