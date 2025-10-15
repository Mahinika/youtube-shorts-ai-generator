# 🎬 YouTube Shorts AI Generator

**AI-powered automated YouTube Shorts creation using Stable Diffusion, Ollama, and FFmpeg**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![GPU Accelerated](https://img.shields.io/badge/GPU-CUDA-green.svg)](https://developer.nvidia.com/cuda-toolkit)

## ✨ Features

- 🤖 **AI Script Writing** - Uses Ollama + Mistral to generate engaging YouTube Shorts scripts
- 🎤 **Voice Synthesis** - High-quality voice narration using Edge TTS
- 🎨 **AI Background Generation** - Stable Diffusion creates custom backgrounds (GPU accelerated)
- 🎬 **Ken Burns Effects** - Smooth zoom/pan effects on AI-generated images
- 🔄 **Pure FFmpeg Pipeline** - No MoviePy dependency - faster and more reliable
- 🎛️ **Professional UI** - CustomTkinter-based YouTube Studio inspired interface
- 📊 **Real-time Progress** - Console window shows detailed generation progress
- 🚀 **GPU Optimization** - Memory management and CUDA acceleration
- 📱 **YouTube Shorts Ready** - Optimized 9:16 vertical format

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **NVIDIA GPU** (for AI background generation)
- **Ollama** (for AI script writing)
- **FFmpeg** (for video processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mahinika/youtube-shorts-ai-generator.git
   cd youtube-shorts-ai-generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Ollama and download model**
   ```bash
   # Install Ollama from https://ollama.com
   ollama pull mistral
   ```

4. **Run the application**
   ```bash
   python start_app.py
   ```

## 🎯 How It Works

### The Pipeline
1. **Script Generation** - Ollama AI creates engaging YouTube Shorts scripts
2. **Voice Creation** - Edge TTS generates natural-sounding narration
3. **Background Generation** - Stable Diffusion creates custom AI backgrounds
4. **Video Effects** - FFmpeg applies Ken Burns effects to backgrounds
5. **Composition** - FFmpeg combines everything into final video

### Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Script     │ -> │   Voice TTS     │ -> │  AI Backgrounds │
│   (Ollama)      │    │   (Edge TTS)    │    │  (Stable Diff)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Ken Burns    │
                    │   Effects      │
                    │   (FFmpeg)     │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Final Video  │
                    │   Composition  │
                    │   (FFmpeg)     │
                    └─────────────────┘
```

## 📋 Requirements

### System Requirements
- **OS**: Windows 10/11, Linux, macOS
- **RAM**: 16GB+ recommended
- **GPU**: NVIDIA GPU with CUDA support (RTX series recommended)
- **Storage**: 10GB+ free space

### Python Dependencies
```
torch>=2.0.0
diffusers>=0.35.0
transformers>=4.35.0
accelerate>=1.10.0
numpy>=1.24.0,<2.0.0
customtkinter>=5.2.0
ollama>=0.1.0
pydub>=0.25.1
pillow>=10.0.0
```

### External Dependencies
- **Ollama** - AI model server
- **FFmpeg** - Video processing
- **Edge TTS** - Voice synthesis (built-in)

## 🎮 Usage

1. **Start the application**
   ```bash
   python start_app.py
   ```

2. **Enter your video topic**
   - Example: "Amazing space facts that will blow your mind"

3. **Click "Generate Video"**
   - Watch the console window for real-time progress
   - AI generates script → voice → backgrounds → video

4. **Find your video**
   - Videos saved in `finished_videos/` folder
   - Ready to upload to YouTube Shorts!

## 🔧 Configuration

### GPU Settings
```python
# In settings/config.py
SD_DEVICE = "cuda"  # Use GPU for AI generation
SD_ATTENTION_SLICING = True  # Memory optimization
```

### Video Settings
```python
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920  # 9:16 aspect ratio
VIDEO_FPS = 24
```

### AI Models
```python
OLLAMA_MODEL = "mistral"  # Script writing
SD_MODEL = "runwayml/stable-diffusion-v1-5"  # Backgrounds
```

## 🚀 Optimization Features

- **GPU Memory Management** - Prevents VRAM exhaustion
- **Batch Processing** - Efficient background generation
- **Automatic Cleanup** - Removes temporary files
- **Error Recovery** - Fallback mechanisms for failed generations
- **Progress Tracking** - Real-time console output

## 🛠️ Development

### Project Structure
```
youtube-shorts-ai-generator/
├── steps/                 # Processing pipeline
│   ├── step1_write_script.py
│   ├── step2_create_voice.py
│   ├── step3_generate_backgrounds.py
│   ├── step4_add_captions.py
│   └── step5_combine_everything.py
├── ui/                    # User interface
│   └── youtube_studio_interface.py
├── helpers/               # Utility functions
├── settings/              # Configuration
├── finished_videos/       # Output directory
├── temp_files/           # Temporary files
└── requirements.txt
```

### Adding New Features
1. Create new step in `steps/` directory
2. Update `ui/youtube_studio_interface.py` to call new step
3. Add configuration in `settings/config.py`
4. Update `requirements.txt` if needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Stable Diffusion** - For AI image generation
- **Ollama** - For local AI model hosting
- **FFmpeg** - For video processing
- **Edge TTS** - For voice synthesis
- **YouTube** - For Shorts format inspiration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Mahinika/youtube-shorts-ai-generator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Mahinika/youtube-shorts-ai-generator/discussions)

---

**Made with ❤️ for content creators who want to automate their YouTube Shorts workflow**