"""
GPU STUCK DIAGNOSIS

Run this to diagnose why Stable Diffusion is stuck at 0/15
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def diagnose():
    print("=" * 70)
    print("GPU STUCK DIAGNOSIS")
    print("=" * 70)
    
    # Check 1: GPU availability
    print("\n[1] Checking GPU availability...")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"  [OK] GPU detected: {torch.cuda.get_device_name(0)}")
            print(f"  [OK] CUDA version: {torch.version.cuda}")
            
            # Check GPU memory
            gpu_memory_allocated = torch.cuda.memory_allocated() / (1024**3)
            gpu_memory_reserved = torch.cuda.memory_reserved() / (1024**3)
            gpu_memory_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            
            print(f"  GPU Memory:")
            print(f"    Allocated: {gpu_memory_allocated:.2f} GB")
            print(f"    Reserved:  {gpu_memory_reserved:.2f} GB")
            print(f"    Total:     {gpu_memory_total:.2f} GB")
            
            if gpu_memory_allocated > 5.0:
                print("  [WARNING] GPU memory almost full!")
                print("  Try closing other GPU applications")
        else:
            print("  [ERROR] No GPU detected!")
            print("  Check: Is your GPU driver installed?")
            return False
    except ImportError:
        print("  [ERROR] PyTorch not installed!")
        return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False
    
    # Check 2: Stable Diffusion model access
    print("\n[2] Checking Stable Diffusion model...")
    try:
        from diffusers import StableDiffusionPipeline
        print("  [OK] diffusers library available")
        
        # Check if model is cached
        from huggingface_hub import scan_cache_dir
        try:
            cache_info = scan_cache_dir()
            print(f"  [OK] Hugging Face cache accessible")
        except:
            print("  [WARNING] Could not scan cache")
    except ImportError:
        print("  [ERROR] diffusers not installed!")
        return False
    
    # Check 3: CUDA operations
    print("\n[3] Testing CUDA operations...")
    try:
        import torch
        test_tensor = torch.randn(1000, 1000).cuda()
        result = torch.matmul(test_tensor, test_tensor)
        print("  [OK] CUDA operations working")
        del test_tensor, result
        torch.cuda.empty_cache()
    except Exception as e:
        print(f"  [ERROR] CUDA operations failed: {e}")
        print("  This means your GPU driver may have issues")
        return False
    
    # Check 4: Other GPU processes
    print("\n[4] Checking for other GPU processes...")
    try:
        import subprocess
        result = subprocess.run(
            ["nvidia-smi", "--query-compute-apps=pid,name,used_memory", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            processes = result.stdout.strip()
            if processes:
                print("  [WARNING] Other processes using GPU:")
                for line in processes.split('\n'):
                    print(f"    {line}")
                print("  Consider closing other GPU applications")
            else:
                print("  [OK] No other GPU processes detected")
        else:
            print("  [INFO] Could not check (nvidia-smi unavailable)")
    except Exception as e:
        print(f"  [INFO] Could not check GPU processes: {e}")
    
    # Check 5: Disk space
    print("\n[5] Checking disk space...")
    try:
        import psutil
        disk = psutil.disk_usage('D:/')
        free_gb = disk.free / (1024**3)
        total_gb = disk.total / (1024**3)
        print(f"  D: drive: {free_gb:.1f} GB free / {total_gb:.1f} GB total")
        
        if free_gb < 10:
            print("  [WARNING] Low disk space!")
            print("  Stable Diffusion needs space to cache models")
        else:
            print("  [OK] Sufficient disk space")
    except:
        print("  [INFO] Could not check disk space")
    
    print("\n" + "=" * 70)
    print("DIAGNOSIS COMPLETE")
    print("=" * 70)
    
    print("\n[RECOMMENDATIONS]")
    print("1. Try closing other applications (especially games/video editors)")
    print("2. Restart your computer to clear GPU memory")
    print("3. Update NVIDIA drivers if outdated")
    print("4. Check Task Manager for high GPU usage")
    print("5. If stuck persists, try CPU mode (slower but works)")
    
    return True


if __name__ == "__main__":
    diagnose()



