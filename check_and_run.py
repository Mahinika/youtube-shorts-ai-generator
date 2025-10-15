"""
CHECK AND RUN

Verifies all requirements before launching the app.
Run this to check everything is ready.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_and_run():
    """Check all requirements and launch app if ready"""

    print("=" * 60)
    print("YOUTUBE SHORTS MAKER - PRE-LAUNCH CHECK")
    print("=" * 60)

    all_good = True

    # Check Python version
    print("\n1. Checking Python version...")
    if sys.version_info < (3, 9):
        print("   ERROR: Python 3.9+ required")
        print(f"   Current: Python {sys.version_info.major}.{sys.version_info.minor}")
        all_good = False
    else:
        print(f"   OK: Python {sys.version_info.major}.{sys.version_info.minor}")

    # Check critical packages
    print("\n2. Checking critical packages...")
    critical_packages = {
        "moviepy": "Video editing",
        "requests": "API calls",
        "gtts": "Voice generation",
        "customtkinter": "GUI",
        "PIL": "Image processing",
    }

    missing = []
    for package, description in critical_packages.items():
        try:
            __import__(package)
            print(f"   OK: {package:20} ({description})")
        except ImportError:
            print(f"   MISSING: {package:20} ({description})")
            missing.append(package)
            all_good = False

    if missing:
        print("\n   Install missing packages:")
        print("   pip install -r requirements.txt")

    # Check Ollama
    print("\n3. Checking Ollama...")
    try:
        import requests

        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("   OK: Ollama is running")

            data = response.json()
            models = data.get("models", [])

            if models:
                print(f"   OK: {len(models)} model(s) installed")
                has_llama = any("llama" in m.get("name", "") for m in models)
                if not has_llama:
                    print("   WARNING: llama3.2 not found")
                    print("   Install with: ollama pull llama3.2")
            else:
                print("   WARNING: No models installed")
                print("   Install llama3.2: ollama pull llama3.2")
                all_good = False
        else:
            print("   ERROR: Ollama not responding")
            all_good = False
    except:
        print("   ERROR: Cannot connect to Ollama")
        print("   Start Ollama: ollama serve")
        all_good = False

    # Check GPU (optional)
    print("\n4. Checking GPU (for AI backgrounds)...")
    try:
        import torch

        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"   OK: GPU available - {gpu_name}")
            print("   AI backgrounds: ENABLED")
        else:
            print("   INFO: No GPU detected")
            print("   AI backgrounds: DISABLED (will use fallback)")
            print("   This is OK - you can still create videos!")
    except ImportError:
        print("   INFO: torch not installed")
        print("   AI backgrounds: DISABLED (will use fallback)")

    # Check D drive paths
    print("\n5. Checking D drive paths...")
    from settings.config import Config

    paths = {
        "Output": Config.OUTPUT_DIR,
        "Temp": Config.TEMP_DIR,
        "Models": Config.MODELS_DIR,
    }

    for name, path in paths.items():
        if Path(path).exists():
            print(f"   OK: {name:15} {path}")
        else:
            print(f"   WARNING: {name:15} {path} (will be created)")

    # Summary
    print("\n" + "=" * 60)

    if all_good:
        print("STATUS: ALL CHECKS PASSED!")
        print("=" * 60)
        print("\nLaunching YouTube Shorts Maker...")
        print()

        # Launch the app
        from start_app import main

        main()

    else:
        print("STATUS: SOME CHECKS FAILED")
        print("=" * 60)
        print("\nPlease fix the issues above before running.")
        print("\nQuick fixes:")
        print("  1. Install packages: pip install -r requirements.txt")
        print("  2. Start Ollama: ollama serve (in another terminal)")
        print("  3. Download model: ollama pull llama3.2")
        print("\nThen run this script again: python check_and_run.py")
        print()
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    try:
        check_and_run()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)
