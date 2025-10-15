"""
RESOURCE MONITOR

Real-time monitoring tool to track memory and performance improvements.
Run this in a separate terminal while generating videos.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def monitor_system():
    """Monitor system resources in real-time"""
    
    try:
        import psutil
        import torch
    except ImportError as e:
        print(f"ERROR: Missing required package: {e}")
        print("Install with: pip install psutil torch")
        return
    
    print("=" * 70)
    print("YOUTUBE SHORTS MAKER - RESOURCE MONITOR")
    print("=" * 70)
    print("\nMonitoring system resources...")
    print("Press Ctrl+C to stop\n")
    
    start_time = time.time()
    peak_ram_gb = 0
    peak_gpu_gb = 0
    
    try:
        while True:
            # Clear screen (Windows compatible)
            print("\033[H\033[J", end="")
            
            elapsed = time.time() - start_time
            
            # System RAM
            memory = psutil.virtual_memory()
            ram_used_gb = (memory.total - memory.available) / (1024**3)
            ram_total_gb = memory.total / (1024**3)
            ram_percent = memory.percent
            
            # Track peak
            if ram_used_gb > peak_ram_gb:
                peak_ram_gb = ram_used_gb
            
            # GPU Memory
            gpu_available = torch.cuda.is_available()
            if gpu_available:
                gpu_used_gb = torch.cuda.memory_allocated() / (1024**3)
                gpu_reserved_gb = torch.cuda.memory_reserved() / (1024**3)
                gpu_total_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                gpu_name = torch.cuda.get_device_name(0)
                
                if gpu_used_gb > peak_gpu_gb:
                    peak_gpu_gb = gpu_used_gb
            
            # Python Process
            process = psutil.Process()
            process_ram_gb = process.memory_info().rss / (1024**3)
            
            # Display
            print("=" * 70)
            print(f"RESOURCE MONITOR - Runtime: {elapsed:.1f}s")
            print("=" * 70)
            
            print("\n[SYSTEM RAM]")
            print(f"  Used:    {ram_used_gb:.2f} GB / {ram_total_gb:.1f} GB ({ram_percent:.1f}%)")
            print(f"  Peak:    {peak_ram_gb:.2f} GB")
            print(f"  Status:  ", end="")
            if ram_percent > 80:
                print("[HIGH USAGE - Consider closing apps]")
            elif ram_percent > 60:
                print("[MODERATE USAGE]")
            else:
                print("[OK]")
            
            print("\n[GPU MEMORY]")
            if gpu_available:
                print(f"  Device:  {gpu_name}")
                print(f"  Used:    {gpu_used_gb:.2f} GB / {gpu_total_gb:.1f} GB")
                print(f"  Reserved:{gpu_reserved_gb:.2f} GB")
                print(f"  Peak:    {peak_gpu_gb:.2f} GB")
                gpu_percent = (gpu_used_gb / gpu_total_gb) * 100 if gpu_total_gb > 0 else 0
                print(f"  Status:  ", end="")
                if gpu_percent > 85:
                    print("[HIGH USAGE - May slow down]")
                elif gpu_percent > 60:
                    print("[MODERATE USAGE]")
                else:
                    print("[OK]")
            else:
                print("  No GPU detected")
            
            print("\n[PYTHON PROCESS]")
            print(f"  Memory:  {process_ram_gb:.2f} GB")
            print(f"  CPU:     {process.cpu_percent():.1f}%")
            
            print("\n[OPTIMIZATION TARGETS]")
            print(f"  Target Peak GPU: < 3.5 GB (Current: {peak_gpu_gb:.2f} GB)")
            if peak_gpu_gb < 3.5:
                print("  [OK] GPU usage optimized!")
            elif peak_gpu_gb < 4.5:
                print("  [GOOD] Better than unoptimized (typically 4-5 GB)")
            else:
                print("  [WARNING] Higher than expected")
            
            print(f"  Target Python: < 1.5 GB (Current: {process_ram_gb:.2f} GB)")
            if process_ram_gb < 1.5:
                print("  [OK] Process memory optimized!")
            elif process_ram_gb < 2.0:
                print("  [GOOD] Better than unoptimized (typically 2-3 GB)")
            else:
                print("  [WARNING] Higher than expected")
            
            print("\n[TIPS]")
            print("  - GPU peaks during AI background generation")
            print("  - RAM peaks during video rendering")
            print("  - Watch for cleanup after each step (memory should drop)")
            print("  - Press Ctrl+C to stop monitoring")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("MONITORING STOPPED - SUMMARY")
        print("=" * 70)
        print(f"\nTotal Runtime: {elapsed:.1f} seconds")
        print(f"Peak RAM Usage: {peak_ram_gb:.2f} GB")
        if gpu_available:
            print(f"Peak GPU Usage: {peak_gpu_gb:.2f} GB")
        
        print("\n[OPTIMIZATION RESULTS]")
        
        # GPU Assessment
        if gpu_available:
            if peak_gpu_gb < 3.0:
                print(f"  GPU: EXCELLENT! ({peak_gpu_gb:.2f} GB - vs typical 4-5 GB unoptimized)")
                savings = ((4.5 - peak_gpu_gb) / 4.5) * 100
                print(f"       ~{savings:.0f}% memory savings achieved!")
            elif peak_gpu_gb < 3.5:
                print(f"  GPU: GOOD! ({peak_gpu_gb:.2f} GB - vs typical 4-5 GB unoptimized)")
                savings = ((4.5 - peak_gpu_gb) / 4.5) * 100
                print(f"       ~{savings:.0f}% memory savings achieved!")
            elif peak_gpu_gb < 4.5:
                print(f"  GPU: OK ({peak_gpu_gb:.2f} GB - slightly better than baseline)")
            else:
                print(f"  GPU: Higher than expected ({peak_gpu_gb:.2f} GB)")
        
        # RAM Assessment
        if process_ram_gb < 1.2:
            print(f"  Python Process: EXCELLENT! ({process_ram_gb:.2f} GB)")
        elif process_ram_gb < 1.8:
            print(f"  Python Process: GOOD! ({process_ram_gb:.2f} GB)")
        else:
            print(f"  Python Process: OK ({process_ram_gb:.2f} GB)")
        
        print("\n")


if __name__ == "__main__":
    monitor_system()



