# YouTube Shorts Maker

AI-Powered Video Creation Tool with Professional GUI

Generate engaging YouTube Shorts automatically with AI-generated scripts, backgrounds, voice narration, and karaoke captions.

---

## Features

- **AI Script Generation** - Ollama generates optimized scripts for YouTube Shorts
- **AI Backgrounds** - Stable Diffusion creates custom vertical backgrounds (requires GPU)
- **Voice Narration** - Free text-to-speech with gTTS
- **Karaoke Captions** - Word-by-word highlighting captions
- **YouTube Studio GUI** - Professional dark theme interface
- **100% D Drive** - All components install to D drive
- **YouTube Compliant** - AI disclosure, 9:16 format, proper specifications

---

## System Requirements

### Minimum (Stock Video Mode)
- Windows 10/11
- Python 3.9+
- 4 GB RAM
- 5 GB free space on D drive
- Internet connection

### Recommended (AI Background Mode)
- Windows 10/11
- Python 3.9+
- NVIDIA GPU with 6+ GB VRAM
- 16 GB RAM
- 20 GB free space on D drive
- Internet connection

---

## Quick Start

### 1. Run Setup Script

Double-click: `D:\YouTubeShortsProject\setup_complete.bat`

This creates the folder structure and sets environment variables.

### 2. Install Dependencies

Run: `D:\YouTubeShortsProject\start_project.bat`

Then:
```bash
pip install -r requirements.txt
```

### 3. Install Ollama

Download from: https://ollama.com/download

Install and run:
```bash
ollama serve
```

In another terminal:
```bash
ollama pull llama3.2
```

### 4. Get API Keys (Optional)

Only needed if you don't have a GPU for AI backgrounds:

- Pexels: https://www.pexels.com/api/ (FREE)
- Pixabay: https://pixabay.com/api/docs/ (FREE)

Copy `env.example` to `.env` and add your keys.

### 5. Run the App

```bash
python start_app.py
```

---

## Usage

### Creating Your First Short

1. Launch the app: `python start_app.py`
2. Enter your video idea in the text box
3. Select duration (15, 30, 45, or 60 seconds)
4. Click "Generate Short"
5. Wait 5-10 minutes for generation
6. Find your video in `finished_videos/`

### Example Prompts

- "Amazing facts about the ocean"
- "How to stay motivated"
- "Top 5 space discoveries"
- "Quick cooking tips"

---

## File Structure

```
D:\YouTubeShortsProject\
├── NCWM\                       # Project code
│   ├── start_app.py           # Main launcher
│   ├── requirements.txt       # Python dependencies
│   ├── env.example            # Environment template
│   ├── .env                   # Your API keys (create this)
│   ├── CODING_RULES.md        # Development guidelines
│   │
│   ├── settings\              # Configuration
│   │   └── config.py          # All settings
│   │
│   ├── steps\                 # Video generation pipeline
│   │   ├── step1_write_script.py
│   │   ├── step2_create_voice.py
│   │   ├── step3_generate_backgrounds.py
│   │   ├── step4_add_captions.py
│   │   └── step5_combine_everything.py
│   │
│   ├── helpers\               # Utilities
│   │   └── cleanup_temp_files.py
│   │
│   ├── ui\                    # User interface
│   │   └── youtube_studio_interface.py
│   │
│   ├── finished_videos\       # Your videos appear here
│   ├── temp_files\            # Temporary processing files
│   └── metadata\              # Video metadata (titles, descriptions)
│
├── python_env\                # Python virtual environment
├── models\                    # AI models (Ollama + Stable Diffusion)
├── cache\                     # Download cache
└── temp\                      # Temporary files
```

---

## How It Works

### Step 1: AI Script Writing
- Connects to local Ollama instance
- Generates topic, title, description, script
- Optimized for YouTube Shorts (hook in 3 seconds)
- Creates scene descriptions for visuals

### Step 2: Voice Generation
- Converts script to speech with gTTS
- Calculates exact duration
- Saves to temp folder on D drive

### Step 3: AI Background Generation
- If GPU available: Uses Stable Diffusion
  - Generates 1080x1920 vertical images
  - Applies Ken Burns zoom effects
  - Creates dynamic video clips
- If no GPU: Uses fallback colored backgrounds

### Step 4: Karaoke Captions
- Creates word-by-word timestamps
- Large text (80px) for mobile viewing
- Yellow text with black outline
- Centers on screen for vertical format

### Step 5: Final Composition
- Combines all elements
- Resizes/crops to 1080x1920
- Adds audio narration
- Composites caption layers
- Adds AI disclosure watermark
- Renders H.264 MP4

---

## YouTube Upload Guide

### Before Uploading

1. Find your video in `finished_videos/`
2. Find metadata in `metadata/` (same name as video)
3. Copy title and description from metadata JSON

### Upload Checklist

- [ ] Check "Altered content" box on YouTube
- [ ] Select "I used AI to generate content"
- [ ] Use title from metadata file
- [ ] Use description from metadata file (includes AI disclosure)
- [ ] Add #Shorts hashtag (already in description)
- [ ] Set as "Not made for kids"
- [ ] Choose appropriate category

### YouTube Shorts Requirements

Your videos are already compliant:
- 9:16 aspect ratio
- 1080x1920 resolution
- Under 60 seconds
- AI disclosure included
- Proper format (MP4, H.264)

---

## Troubleshooting

### "Cannot connect to Ollama"
**Solution**: Start Ollama in another terminal
```bash
ollama serve
```

### "No GPU detected"
**Solution**: Either:
1. Get API keys for stock videos (Pexels/Pixabay)
2. Use Google Colab for free GPU access
3. Accept fallback colored backgrounds

### "Missing packages"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### "Video generation failed"
**Check**:
1. Ollama is running
2. All packages installed
3. Enough disk space (5+ GB free)
4. Internet connection active

### "Out of memory"
**Solution**: 
- Close other programs
- Reduce video duration to 30 seconds
- Use stock videos instead of AI backgrounds

---

## Configuration

Edit `settings/config.py` to customize:

- Video resolution and FPS
- Caption styling (size, color, position)
- AI model selection
- Stable Diffusion parameters
- Output folders

---

## Storage Requirements

### With Stock Videos (No GPU)
- Python packages: ~800 MB
- Ollama + llama3.2: ~2.5 GB
- Per video: ~100 MB
- **Total: ~4 GB**

### With AI Backgrounds (GPU)
- Python packages: ~800 MB
- Ollama + llama3.2: ~2.5 GB
- Stable Diffusion model: ~5 GB
- PyTorch: ~2 GB
- Per video: ~100 MB
- **Total: ~13 GB**

### C Drive Usage
Only ~200 MB (Ollama program only)

---

## Performance

### Generation Time
- Stock videos: 4-7 minutes per Short
- AI backgrounds: 5-11 minutes per Short (with GPU)

### Bottlenecks
- Script generation: 10-30 seconds
- Voice generation: 5-10 seconds
- AI backgrounds: 2-5 minutes (GPU) or instant (fallback)
- Video rendering: 2-5 minutes

---

## Advanced Usage

### Command Line Mode

```python
from steps import *

# Generate script
script = write_script_with_ollama("Amazing facts about space")

# Create voice
voice = create_voice_narration(script["script"])

# Generate backgrounds
backgrounds = generate_ai_backgrounds(script["scene_descriptions"])
clips = images_to_video_clips(backgrounds)

# Add captions
timestamps = generate_word_timestamps(script["script"], voice["duration"])
captions = create_shorts_captions(timestamps)

# Combine
final = combine_into_final_video(clips, voice["path"], voice["duration"], captions, "my_video")
```

### Batch Processing

Create multiple videos from a list of prompts:

```python
prompts = [
    "Amazing ocean facts",
    "Quick cooking tips",
    "Space discoveries"
]

for prompt in prompts:
    # Generate each video
    pass
```

---

## Development

### Adding Features

1. Follow CODING_RULES.md
2. No emojis in code
3. Use beginner-friendly names
4. All paths on D drive
5. Test thoroughly

### Contributing

1. Create a feature branch
2. Follow coding rules
3. Test on D drive setup
4. Submit pull request

---

## License

This project is for educational purposes.

**Third-party components**:
- Ollama: Apache 2.0
- Stable Diffusion: CreativeML Open RAIL-M
- MoviePy: MIT
- Pexels/Pixabay: Free with attribution

---

## Support

### Issues

Common issues and solutions are in the Troubleshooting section above.

### Verification

Run the verification script to check your setup:
```bash
python ..\verify_setup.py
```

---

## Credits

**AI Models**:
- Ollama (llama3.2)
- Stable Diffusion v1.5
- Google TTS

**APIs**:
- Pexels (stock videos)
- Pixabay (stock videos)

**Libraries**:
- MoviePy (video editing)
- CustomTkinter (GUI)
- PyTorch (AI framework)
- Diffusers (Stable Diffusion)

---

## Version

**Version**: 1.0.0
**Release Date**: 2025
**Python**: 3.9+
**Platform**: Windows (D drive optimized)

---

**Happy creating! Generate amazing YouTube Shorts with AI!**

