"""
CLEANUP TEMP FILES

Removes temporary files after video generation.
Preserves folder structure on D drive.
"""

import shutil
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from settings.config import Config


def cleanup_temp_files():
    """Remove all temporary files from D drive temp folder"""

    temp_dir = Path(Config.TEMP_DIR)

    if not temp_dir.exists():
        print("No temporary files to clean")
        return

    print("Cleaning up temporary files...")

    # Count files before cleanup
    files_before = list(temp_dir.glob("*"))
    file_count = len([f for f in files_before if f.is_file()])

    if file_count == 0:
        print("  No files to clean")
        return

    # OPTIMIZATION: Calculate total size being cleaned
    total_size = 0
    for item in temp_dir.iterdir():
        if item.is_file():
            total_size += item.stat().st_size

    size_mb = total_size / (1024 * 1024)
    print(f"  Cleaning {file_count} files ({size_mb:.1f} MB)")

    # Remove all files in temp directory
    for item in temp_dir.iterdir():
        try:
            if item.is_file():
                item.unlink()
                print(f"  Removed: {item.name}")
            elif item.is_dir():
                shutil.rmtree(item)
                print(f"  Removed folder: {item.name}")
        except Exception as e:
            print(f"  Error removing {item.name}: {e}")

    # Recreate temp directory (empty)
    temp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Cleanup complete - removed {file_count} files ({size_mb:.1f} MB freed)")


def cleanup_temp_files_before_generation():
    """OPTIMIZATION: Clean temp files before starting generation to free memory"""
    
    temp_dir = Path(Config.TEMP_DIR)
    
    if not temp_dir.exists():
        return
    
    # Quick cleanup of any leftover files
    files = list(temp_dir.glob("*"))
    if files:
        print("Pre-generation cleanup: Removing leftover temporary files...")
        for item in files:
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception:
                pass  # Ignore cleanup errors
        print(f"  Cleaned {len(files)} leftover files")


def cleanup_intermediate_file(file_path):
    """OPTIMIZATION: Clean up a specific intermediate file immediately after use"""
    
    try:
        path = Path(file_path)
        if path.exists() and path.is_file():
            size_mb = path.stat().st_size / (1024 * 1024)
            path.unlink()
            print(f"  Cleaned intermediate file: {path.name} ({size_mb:.1f} MB)")
    except Exception as e:
        print(f"  Warning: Could not clean {file_path}: {e}")


def cleanup_cache():
    """Clean pip cache if needed"""

    cache_dir = Path(Config.CACHE_DIR)

    if not cache_dir.exists():
        print("No cache to clean")
        return

    # Calculate cache size
    total_size = sum(f.stat().st_size for f in cache_dir.glob("**/*") if f.is_file())
    size_mb = total_size / (1024 * 1024)

    print(f"Cache size: {size_mb:.1f} MB")

    # OPTIMIZATION: Auto-purge cache if it gets too large
    max_cache_mb = 2000  # 2GB limit
    if size_mb > max_cache_mb:
        print(f"Cache exceeds {max_cache_mb} MB limit. Auto-purging...")
        try:
            shutil.rmtree(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
            print(f"  Cache purged - freed {size_mb:.1f} MB")
        except Exception as e:
            print(f"  Warning: Could not purge cache: {e}")
    elif size_mb > 1000:  # Over 1GB
        print("Cache is large. Consider cleaning:")
        print(f"  Folder: {cache_dir}")
        print("  Command: rmdir /s /q {cache_dir}")
    else:
        print("Cache size is acceptable")


if __name__ == "__main__":
    print("=" * 60)
    print("CLEANUP UTILITY")
    print("=" * 60)

    cleanup_temp_files()
    print()
    cleanup_cache()
