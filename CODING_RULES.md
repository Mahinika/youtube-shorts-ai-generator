# CODING RULES FOR THIS PROJECT

## RULE ZERO: NO EMOJIS IN CODE

Emojis are NOT allowed in:
- Code files (.py)
- Comments in code
- Variable names, function names
- Print statements in code
- Docstrings

Emojis ARE allowed in:
- README files (.md)
- Documentation
- UI text shown to users (in strings displayed to user)
- This rules file

---

## YOUTUBE SHORTS SPECIFICATIONS

All videos MUST follow these official requirements:
- **Aspect Ratio**: 9:16 (vertical)
- **Resolution**: 1080x1920 pixels (width x height)
- **Duration**: 15-60 seconds
- **Format**: MP4, H.264 codec
- **Orientation**: Portrait/Vertical only
- **AI Disclosure**: Required for AI-generated content

---

## FILE NAMING RULES

Use lowercase_with_underscores.py (snake_case)
Name files by WHAT THEY DO
Max 3 words in a filename

**GOOD Examples:**
- `write_script.py`
- `create_voice.py`
- `download_videos.py`
- `add_captions.py`

**BAD Examples:**
- `utils.py` (what utilities?)
- `handler.py` (handles what?)
- `manager.py` (manages what?)
- `VideoDownloaderFactoryManager.py` (too complex!)

---

## FUNCTION NAMING RULES

Start with a VERB
Say WHAT you're doing to WHAT
Use full words, no abbreviations

**GOOD Examples:**
```python
def download_video_from_pexels(keyword):
def create_voice_narration(text):
def generate_ai_backgrounds(scenes):
```

**BAD Examples:**
```python
def process():  # Process what?
def handle():   # Handle what?
def do_thing(): # What thing?
def dl_vid():   # Use full words
```

---

## VARIABLE NAMING RULES

Full words, NO abbreviations (except very common: num, i, url, id)
Be SPECIFIC
Include units for numbers

**GOOD Examples:**
```python
video_file_path = "video.mp4"
duration_in_seconds = 45.5
number_of_scenes = 5
is_gpu_available = True
```

**BAD Examples:**
```python
vfp = "video.mp4"    # What is vfp?
dur = 45.5           # Duration of what?
num = 5              # Number of what?
flag = True          # What flag?
```

---

## CONSTANTS NAMING RULES

CONSTANTS in ALL_CAPS_WITH_UNDERSCORES
Include units in name
Group related constants together

**Example:**
```python
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
MAX_DURATION_SECONDS = 60
```

---

## COMMENT RULES

Explain WHY, not WHAT (the code shows what)
Write for your FUTURE SELF who forgot everything
If code needs a comment to understand, the name is probably bad

**GOOD Comments:**
```python
# Trim audio to 60 seconds to comply with YouTube Shorts max duration
audio = audio[:60000]

# Use GPU if available for 10x speed improvement
device = "cuda" if torch.cuda.is_available() else "cpu"
```

**BAD Comments:**
```python
# Trim audio
audio = audio[:60000]  # This just repeats the code

# Set device
device = "cuda" if torch.cuda.is_available() else "cpu"  # Too vague
```

---

## FILE STRUCTURE

Every file MUST have:

```python
"""
MODULE NAME IN CAPS

Brief explanation of what this file does.
Who uses it and when.
"""

# Imports at top
import standard_library
from pathlib import Path
import third_party

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import project modules
from settings.config import Config

# Constants
DEFAULT_VALUE = 10

# Functions with docstrings
def main_function():
    """
    What it does.
    
    Args:
        param: What it is
    
    Returns:
        What it returns
    """
    pass

# Test code
if __name__ == "__main__":
    # Test this module
    pass
```

---

## ERROR HANDLING RULES

Tell user EXACTLY what went wrong
Tell user HOW TO FIX IT
Never just say "error"

**GOOD Error Messages:**
```python
print("ERROR: Cannot connect to Ollama")
print("Make sure Ollama is running: ollama serve")
print(f"Check: curl {Config.OLLAMA_HOST}")
```

**BAD Error Messages:**
```python
print("Error")              # What error?
raise Exception("Failed")   # Why? How to fix?
```

---

## DOCSTRING RULES

Every function needs a docstring
Explain what, args, returns
Be specific

**Template:**
```python
def function_name(param1: str, param2: int) -> dict:
    """
    Brief description of what this function does.
    
    More detailed explanation if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ExceptionType: When this exception occurs
    """
    pass
```

---

## IMPORT RULES

1. Standard library imports first
2. Third-party imports second
3. Local imports last
4. Alphabetical within each group
5. One import per line for clarity

**Example:**
```python
import json
import sys
from pathlib import Path

import requests
import torch
from moviepy.editor import VideoFileClip

from settings.config import Config
from steps.step1_write_script import write_script
```

---

## PATH RULES

Always use Path from pathlib
All paths point to D drive
Use forward slashes or Path objects

**GOOD:**
```python
from pathlib import Path

output_dir = Path(Config.OUTPUT_DIR)
video_file = output_dir / "video.mp4"
```

**BAD:**
```python
output_dir = "C:\\Users\\..."  # Hardcoded C drive
video_file = output_dir + "\\video.mp4"  # String concatenation
```

---

## D DRIVE STRUCTURE

All components MUST be on D drive:
- **D:\YouTubeShortsProject\NCWM** - Project code
- **D:\YouTubeShortsProject\python_env** - Python packages
- **D:\YouTubeShortsProject\models** - AI models
- **D:\YouTubeShortsProject\cache** - Download cache
- **D:\YouTubeShortsProject\temp** - Temporary files

Never hardcode C drive paths!

---

## TESTING RULES

Every important module should be testable
Use `if __name__ == "__main__":` for test code
Test with realistic data

**Example:**
```python
if __name__ == "__main__":
    # Test the module
    test_prompt = "Amazing facts about space"
    result = write_script(test_prompt)
    print(json.dumps(result, indent=2))
```

---

## CHECKLIST BEFORE COMMITTING

- [ ] All file names describe what they do
- [ ] All function names start with verbs
- [ ] All variables have clear, full names
- [ ] Every function has a docstring
- [ ] Error messages explain HOW to fix
- [ ] No file is longer than 500 lines
- [ ] Removed all unused code
- [ ] Tested the code works
- [ ] Added comments for tricky parts
- [ ] NO EMOJIS in code
- [ ] All paths point to D drive

---

## REMEMBER

**Code is read 100 times more than it's written.**

**Write for the confused beginner who will read this at 2am.**

**That beginner is FUTURE YOU!**

