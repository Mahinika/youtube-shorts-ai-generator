# Stable Diffusion Video Background Guide

## How It Works

### Current Setup (No GPU - Colored Backgrounds)
Since no GPU is detected, the system uses **colored background fallback**:
- Creates 4 colored clips (dark blue-gray, purple, green, orange)
- Each color displays for a portion of the video duration
- These are solid colors, not AI-generated images

### With GPU - AI Generated Backgrounds
When a compatible NVIDIA GPU is available:

1. **AI Script Generation** → Creates scene descriptions
   ```
   Example: "A rocket launching into space with stars in background"
   ```

2. **Stable Diffusion** → Generates static 1080x1920 images
   - One image per scene description
   - Optimized for vertical (9:16) format
   - High-quality, cinematic style
   - ~30 diffusion steps per image

3. **Image to Video** → Converts images to video clips
   - Each image displays for calculated duration
   - Currently static (no motion)
   - Can add Ken Burns effect (zoom/pan) if desired

4. **FFmpeg Composition** → Combines everything
   - Concatenates all image clips
   - Adds audio narration
   - Overlays karaoke captions
   - Adds AI disclosure watermark

## Requirements for AI Backgrounds

### Hardware
- **NVIDIA GPU** with CUDA support (GTX 1060 or better recommended)
- **8GB+ VRAM** for stable generation
- **20GB+ free disk space** for models

### Software (Already Installed)
- PyTorch with CUDA
- Diffusers library
- Transformers
- Accelerate

## How to Enable GPU (If You Have One)

1. **Install NVIDIA Drivers**
   - Download from: https://www.nvidia.com/download/index.aspx
   - Restart computer

2. **Install CUDA Toolkit** (Optional but recommended)
   - Download: https://developer.nvidia.com/cuda-downloads
   - Version 11.8 or 12.x

3. **Reinstall PyTorch with CUDA**
   ```batch
   D:\YouTubeShortsProject\python_env\Scripts\activate
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

4. **Verify GPU Detection**
   ```batch
   python -c "import torch; print('CUDA Available:', torch.cuda.is_available())"
   ```

5. **First Run Downloads Model** (~5GB)
   - Stable Diffusion v1.5 from Hugging Face
   - Downloads to: `D:\YouTubeShortsProject\models`
   - Only happens once

## Current Issue Fix

**Problem**: Videos showing all black
**Cause**: FFmpeg input stream indexing error with colored backgrounds
**Solution**: Fixed input_index tracking and concat filter generation

### What Was Fixed
```python
# Before (broken):
stream_labels.append(f"[{len(stream_labels)}:v]")  # Wrong index

# After (fixed):
input_index = 0
for clip in video_clips:
    # ... process clip ...
    input_index += 1
audio_input_index = input_index  # Correct audio mapping
```

## Testing the Fix

1. **Generate a short video** (15-30 seconds)
2. **Check the output** in `D:\YouTubeShortsProject\NCWM\finished_videos\`
3. **You should see**:
   - Colored backgrounds (if no GPU)
   - AI-generated images (if GPU available)
   - Word-by-word karaoke captions
   - Audio narration
   - "AI Generated" watermark

## Stable Diffusion Performance

### Without GPU (CPU Only)
- **Not Recommended** - extremely slow (10-30 min per image)
- Falls back to colored backgrounds automatically

### With GPU
- **GTX 1060/1070**: ~10-15 seconds per image
- **RTX 2060/3060**: ~5-8 seconds per image  
- **RTX 3070/4070**: ~3-5 seconds per image
- **RTX 3090/4090**: ~1-3 seconds per image

### Total Video Generation Time (with GPU)
- **Script generation**: 5-10 seconds (Ollama)
- **Voice synthesis**: 2-5 seconds (gTTS)
- **AI backgrounds**: 15-60 seconds (Stable Diffusion)
- **Video composition**: 3-10 seconds (FFmpeg)
- **Total**: 30-90 seconds for a 30-second Short

## Customization Options

### Change AI Model
Edit `D:\YouTubeShortsProject\NCWM\settings\config.py`:
```python
STABLE_DIFFUSION_MODEL = "runwayml/stable-diffusion-v1-5"  # Default
# Alternatives:
# STABLE_DIFFUSION_MODEL = "stabilityai/stable-diffusion-2-1"
# STABLE_DIFFUSION_MODEL = "dreamlike-art/dreamlike-photoreal-2.0"
```

### Adjust Image Quality
```python
SD_INFERENCE_STEPS = 30  # Higher = better quality, slower (15-50)
SD_GUIDANCE_SCALE = 7.5  # How closely to follow prompt (5-15)
```

### Add Motion to Images (Ken Burns Effect)
Edit `D:\YouTubeShortsProject\NCWM\steps\step3_generate_backgrounds.py`:
```python
# Uncomment this line:
clip = clip.resize(lambda t: 1 + 0.15 * (t / duration_per_image))
```

## Troubleshooting

### GPU Not Detected
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"
python -c "import torch; print(torch.version.cuda)"
```

### Out of Memory Error
- Reduce `VIDEO_WIDTH` and `VIDEO_HEIGHT` temporarily
- Close other GPU applications
- Reduce `SD_INFERENCE_STEPS` to 20

### Slow Generation
- Check GPU usage with Task Manager → Performance → GPU
- Ensure NVIDIA drivers are up to date
- Use "draft" quality preset for faster testing

### Black Video
- **Fixed** in latest update
- Verify by generating a new video
- Check terminal output for FFmpeg errors

## Next Steps

1. **Test the fix** by generating a video
2. **If you have a GPU**, follow enable instructions above
3. **Try different quality presets** (draft/balanced/high/production)
4. **Experiment with prompts** to see AI capabilities

---

**Note**: The system works perfectly fine without a GPU using colored backgrounds. AI backgrounds are an enhancement, not a requirement!


