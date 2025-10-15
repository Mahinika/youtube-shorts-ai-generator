#!/usr/bin/env python3
"""
Check Cursor resource usage and provide recommendations
"""

import psutil
import os
import subprocess
import json

def find_cursor_processes():
    """Find all Cursor processes and their resource usage"""
    cursor_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'cmdline']):
        try:
            if 'cursor' in proc.info['name'].lower():
                memory_mb = proc.info['memory_info'].rss / 1024 / 1024
                cursor_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'memory_mb': memory_mb,
                    'cpu_percent': proc.info['cpu_percent'],
                    'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return cursor_processes

def get_system_resources():
    """Get current system resource usage"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'memory_available_gb': memory.available / 1024 / 1024 / 1024,
        'memory_used_gb': memory.used / 1024 / 1024 / 1024
    }

def check_gpu_memory():
    """Check GPU memory usage"""
    try:
        import torch
        if torch.cuda.is_available():
            return {
                'gpu_available': True,
                'gpu_name': torch.cuda.get_device_name(0),
                'memory_allocated_gb': torch.cuda.memory_allocated() / 1024**3,
                'memory_reserved_gb': torch.cuda.memory_reserved() / 1024**3,
                'memory_total_gb': torch.cuda.get_device_properties(0).total_memory / 1024**3
            }
        else:
            return {'gpu_available': False}
    except ImportError:
        return {'gpu_available': False, 'error': 'PyTorch not available'}

def main():
    print("=" * 60)
    print("CURSOR RESOURCE ANALYSIS")
    print("=" * 60)
    
    # Get system resources
    system = get_system_resources()
    print(f"\nSYSTEM RESOURCES:")
    print(f"  CPU Usage: {system['cpu_percent']:.1f}%")
    print(f"  Memory Usage: {system['memory_percent']:.1f}% ({system['memory_used_gb']:.1f} GB used)")
    print(f"  Memory Available: {system['memory_available_gb']:.1f} GB")
    
    # Get GPU resources
    gpu = check_gpu_memory()
    print(f"\nGPU RESOURCES:")
    if gpu['gpu_available']:
        print(f"  GPU: {gpu['gpu_name']}")
        print(f"  GPU Memory: {gpu['memory_allocated_gb']:.1f} GB allocated / {gpu['memory_total_gb']:.1f} GB total")
        print(f"  GPU Reserved: {gpu['memory_reserved_gb']:.1f} GB")
    else:
        print(f"  GPU: Not available")
    
    # Find Cursor processes
    cursor_procs = find_cursor_processes()
    print(f"\nCURSOR PROCESSES ({len(cursor_procs)} found):")
    
    total_cursor_memory = 0
    total_cursor_cpu = 0
    
    for proc in cursor_procs:
        print(f"  PID {proc['pid']}: {proc['name']}")
        print(f"    Memory: {proc['memory_mb']:.1f} MB")
        print(f"    CPU: {proc['cpu_percent']:.1f}%")
        print(f"    Command: {proc['cmdline'][:100]}...")
        print()
        
        total_cursor_memory += proc['memory_mb']
        total_cursor_cpu += proc['cpu_percent']
    
    print(f"CURSOR TOTALS:")
    print(f"  Total Memory: {total_cursor_memory:.1f} MB ({total_cursor_memory/1024:.1f} GB)")
    print(f"  Total CPU: {total_cursor_cpu:.1f}%")
    
    # Analysis and recommendations
    print(f"\nANALYSIS:")
    
    if total_cursor_memory > 1000:  # More than 1GB
        print("  [RED] HIGH MEMORY USAGE: Cursor is using too much RAM")
        print("     Recommendations:")
        print("     - Close unnecessary Cursor windows/tabs")
        print("     - Disable extensions (especially AI/code completion)")
        print("     - Restart Cursor to clear memory leaks")
    
    if total_cursor_cpu > 20:  # More than 20% CPU
        print("  [RED] HIGH CPU USAGE: Cursor is using too much CPU")
        print("     Recommendations:")
        print("     - Disable real-time extensions (linters, formatters)")
        print("     - Close large files or projects")
        print("     - Disable AI features temporarily")
    
    if len(cursor_procs) > 20:
        print("  [RED] TOO MANY PROCESSES: Cursor has spawned too many processes")
        print("     Recommendations:")
        print("     - Restart Cursor completely")
        print("     - Check for extension conflicts")
    
    if gpu['gpu_available'] and gpu['memory_allocated_gb'] > 0.1:
        print("  [YELLOW] GPU MEMORY IN USE: Some GPU memory is allocated")
        print("     This is normal if you've been using AI features")
    
    print(f"\nQUICK FIXES:")
    print(f"  1. Close all Cursor windows and restart")
    print(f"  2. Disable extensions: Ctrl+Shift+X → Disable heavy extensions")
    print(f"  3. Close unnecessary files/tabs")
    print(f"  4. For YouTube Shorts Maker: Close Cursor when generating videos")

if __name__ == "__main__":
    main()
