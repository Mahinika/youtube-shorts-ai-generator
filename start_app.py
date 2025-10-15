"""
YOUTUBE SHORTS MAKER - LAUNCHER

Main entry point for the application.
Checks dependencies and launches the YouTube Studio GUI.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_dependencies():
    """Make sure all required packages are installed"""

    missing = []

    # Check critical imports
    try:
        import customtkinter
    except ImportError:
        missing.append("customtkinter")

    try:
        from PIL import Image
    except ImportError:
        missing.append("pillow")

    try:
        from dotenv import load_dotenv
    except ImportError:
        missing.append("python-dotenv")

    # MoviePy removed - using pure FFmpeg instead

    try:
        import requests
    except ImportError:
        missing.append("requests")

    try:
        import gtts
    except ImportError:
        missing.append("gtts")

    if missing:
        print("=" * 60)
        print("ERROR: Missing required packages!")
        print("=" * 60)
        print("\nPlease install missing packages:")
        print(f"  pip install {' '.join(missing)}")
        print("\nOr install all dependencies:")
        print("  pip install -r requirements.txt")
        print("\n" + "=" * 60)
        input("\nPress Enter to exit...")
        sys.exit(1)


def check_ollama():
    """Check if Ollama is running"""
    import requests

    from settings.config import Config

    try:
        response = requests.get(f"{Config.OLLAMA_HOST}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def check_gpu():
    """Check if GPU is available for Stable Diffusion"""
    try:
        import torch

        return torch.cuda.is_available()
    except ImportError:
        return False


def check_memory_health():
    """OPTIMIZATION: Check available system memory"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        total_gb = memory.total / (1024**3)
        
        print(f"  Memory: {available_gb:.1f} GB available / {total_gb:.1f} GB total")
        
        if available_gb < 2.0:
            print("  [!] WARNING: Low memory available (< 2 GB)")
            print("      Consider closing other applications before video generation")
            return False
        elif available_gb < 4.0:
            print("  [!] INFO: Limited memory available (< 4 GB)")
            print("      Video generation may be slower")
            return True
        else:
            print("  [OK] Sufficient memory available")
            return True
    except ImportError:
        print("  [!] INFO: psutil not available - cannot check memory")
        return True


def print_startup_info():
    """Print startup information"""
    from settings.config import Config
    from helpers.cleanup_temp_files import cleanup_temp_files_before_generation, cleanup_cache

    print("=" * 60)
    print("YOUTUBE SHORTS MAKER")
    print("AI-Powered Video Creation Tool")
    print("=" * 60)
    print()
    
    # OPTIMIZATION: Pre-startup cleanup
    print("System Optimization:")
    cleanup_temp_files_before_generation()
    cleanup_cache()
    print()

    print("System Check:")

    # Check memory health
    memory_ok = check_memory_health()

    # Check Ollama
    if check_ollama():
        print("  [OK] Ollama is running")
    else:
        print("  [!] WARNING: Ollama is not running")
        print("      Start Ollama with: ollama serve")
        print("      Or the app will use fallback scripts")

    # Check GPU
    if check_gpu():
        import torch

        gpu_name = torch.cuda.get_device_name(0)
        print(f"  [OK] GPU available: {gpu_name}")
        print("      AI backgrounds will be generated with Stable Diffusion")
    else:
        print("  [!] No GPU detected")
        print("      AI backgrounds will use fallback (colored backgrounds)")
        print("      For best results, use a system with NVIDIA GPU")

    # Check paths
    print()
    print("Storage:")
    print(f"  Project: {Config.OUTPUT_DIR}")
    print(f"  Models:  {Config.MODELS_DIR}")
    print(f"  Temp:    {Config.TEMP_DIR}")

    print()
    print("=" * 60)
    print()


def main():
    """Launch the YouTube Shorts Maker"""

    # Check dependencies
    check_dependencies()

    # Print startup info
    print_startup_info()

    # Import and launch UI
    print("Launching YouTube Studio interface...")

    from ui.youtube_studio_interface import YouTubeStudioApp

    app = YouTubeStudioApp()
    app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutdown requested... goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        print("\nPlease check:")
        print("  1. All dependencies are installed (pip install -r requirements.txt)")
        print("  2. Ollama is running (ollama serve)")
        print("  3. You're running from D:\\YouTubeShortsProject\\NCWM")
        input("\nPress Enter to exit...")
        sys.exit(1)
