# YouTube Shorts Automation - API Reference

## Table of Contents

1. [Step Modules](#step-modules)
2. [Utility Modules](#utility-modules)
3. [Helper Modules](#helper-modules)
4. [Settings](#settings)
5. [Error Handling](#error-handling)
6. [Type Definitions](#type-definitions)

## Step Modules

### step1_write_script.py

#### `write_script_with_ollama(user_prompt: str) -> Dict[str, Any]`

Generate YouTube Shorts script using configured AI provider.

**Parameters:**
- `user_prompt` (str): What the video should be about

**Returns:**
- `Dict[str, Any]`: Dictionary containing:
  - `topic` (str): Video topic
  - `title` (str): Video title
  - `description` (str): Video description
  - `script` (str): Video script
  - `search_keywords` (List[str]): SEO keywords
  - `scene_descriptions` (List[str]): Scene descriptions for backgrounds

**Raises:**
- `ValidationError`: If input validation fails
- `AIGenerationError`: If AI generation fails

**Example:**
```python
script_data = write_script_with_ollama("Amazing facts about space")
print(script_data['title'])  # "Mind-Blowing Space Facts You Never Knew"
```

#### `estimate_script_duration(script: str, words_per_second: float = 2.5) -> float`

Estimate script duration based on word count.

**Parameters:**
- `script` (str): Script text
- `words_per_second` (float): Speaking rate (default: 2.5)

**Returns:**
- `float`: Estimated duration in seconds

#### `generate_word_timestamps(script: str, total_duration: float) -> List[Dict[str, Any]]`

Generate word-level timestamps for karaoke captions.

**Parameters:**
- `script` (str): Script text
- `total_duration` (float): Total audio duration

**Returns:**
- `List[Dict[str, Any]]`: List of word timestamps with keys:
  - `word` (str): Word text
  - `start` (float): Start time in seconds
  - `end` (float): End time in seconds

### step2_create_voice.py

#### `create_voice_narration(script_text: str, voice_name: Optional[str] = None) -> Dict[str, Any]`

Convert script text to voice audio using TTS.

**Parameters:**
- `script_text` (str): Script text to convert
- `voice_name` (Optional[str]): Voice to use (default: config voice)

**Returns:**
- `Dict[str, Any]`: Dictionary containing:
  - `audio_path` (str): Path to generated audio file
  - `duration` (float): Audio duration in seconds
  - `voice_used` (str): Voice that was used
  - `engine_used` (str): TTS engine that was used

**Raises:**
- `ValidationError`: If input validation fails
- `TTSError`: If TTS generation fails

### step3_generate_backgrounds.py

#### `generate_ai_backgrounds(scene_descriptions: List[str], duration_per_scene: float = 3.0) -> List[str]`

Generate AI background images for video scenes.

**Parameters:**
- `scene_descriptions` (List[str]): List of scene descriptions
- `duration_per_scene` (float): Duration per scene in seconds

**Returns:**
- `List[str]`: List of paths to generated images

**Raises:**
- `ValidationError`: If input validation fails
- `AIGenerationError`: If image generation fails
- `ResourceError`: If GPU resources are insufficient

#### `generate_ai_backgrounds_enhanced(scene_descriptions: List[str], script_data: Optional[Dict[str, Any]] = None, duration_per_scene: float = 3.0) -> List[str]`

Generate AI backgrounds with AI enhancements (prompt optimization, quality analysis).

**Parameters:**
- `scene_descriptions` (List[str]): List of scene descriptions
- `script_data` (Optional[Dict[str, Any]]): Full script context
- `duration_per_scene` (float): Duration per scene in seconds

**Returns:**
- `List[str]`: List of paths to generated images

#### `images_to_video_clips(image_paths: List[str], duration_per_image: float = 3.0) -> List[str]`

Convert static images to video clips with Ken Burns effect.

**Parameters:**
- `image_paths` (List[str]): List of image file paths
- `duration_per_image` (float): Duration per image in seconds

**Returns:**
- `List[str]`: List of paths to generated video clips

#### `check_gpu_available() -> bool`

Check if GPU is available for Stable Diffusion.

**Returns:**
- `bool`: True if GPU is available and compatible

### step4_add_captions.py

#### `create_shorts_captions(word_timestamps: List[Dict[str, Any]]) -> str`

Generate ASS subtitle file from word timestamps.

**Parameters:**
- `word_timestamps` (List[Dict[str, Any]]): List of word timestamps

**Returns:**
- `str`: Path to generated ASS file (empty string if no timestamps)

### step5_combine_everything.py

#### `combine_into_final_video(video_clips: List[str], audio_path: str, audio_duration: float, caption_ass_path: str, output_name: str) -> str`

Combine all elements into final YouTube Short video.

**Parameters:**
- `video_clips` (List[str]): List of video clip paths
- `audio_path` (str): Path to audio file
- `audio_duration` (float): Audio duration in seconds
- `caption_ass_path` (str): Path to ASS subtitle file
- `output_name` (str): Output video name

**Returns:**
- `str`: Path to final video file

**Raises:**
- `ValidationError`: If input validation fails
- `VideoProcessingError`: If video processing fails

## Utility Modules

### utils/gpu_manager.py

#### `GPUMemoryManager`

GPU memory management class.

**Methods:**
- `get_memory_info() -> Dict[str, Any]`: Get GPU memory information
- `clear_cache() -> None`: Clear GPU memory cache
- `get_memory_usage() -> Dict[str, Any]`: Get memory usage statistics

#### `get_gpu_manager() -> GPUMemoryManager`

Get singleton GPU manager instance.

#### `gpu_memory_context(clear_cache: bool = True) -> ContextManager`

Context manager for GPU operations with automatic cleanup.

#### `check_gpu_compatibility() -> Tuple[bool, str]`

Check if GPU is available and compatible.

**Returns:**
- `Tuple[bool, str]`: (compatible, message)

#### `get_gpu_info() -> Dict[str, Any]`

Get detailed GPU information.

### utils/tts_manager.py

#### `TTSManager`

Text-to-speech manager with automatic fallback.

**Methods:**
- `generate_audio(text: str, output_path: Union[str, Path]) -> Dict[str, Any]`: Generate audio from text
- `cleanup() -> None`: Cleanup TTS resources

#### `create_voice_narration(script_text: str, voice_name: Optional[str] = None) -> Dict[str, Any]`

Create voice narration using TTS manager.

### utils/video_utils.py

#### `create_ken_burns_video(image_path: str, duration: float, output_path: str) -> str`

Create video with Ken Burns effect from image.

#### `create_static_video(image_path: str, duration: float, output_path: str) -> str`

Create static video from image.

#### `combine_video_with_audio(video_clips: List[Union[str, Path]], audio_path: Union[str, Path], audio_duration: float, output_path: Union[str, Path], caption_ass_path: str = "") -> str`

Combine video clips with audio and captions.

### utils/sd_generation_manager.py

#### `SDGenerationManager`

Unified Stable Diffusion generation manager.

**Methods:**
- `generate_images(prompts: List[str], **kwargs) -> List[str]`: Generate images
- `cleanup() -> None`: Cleanup resources

#### `generate_ai_backgrounds_unified(scene_descriptions: List[str], script_data: Optional[Dict[str, Any]] = None, duration_per_scene: float = 3.0, method: str = "auto", use_enhancements: bool = True) -> List[str]`

Unified AI background generation.

### utils/error_handler.py

#### Custom Exceptions

- `AIGenerationError`: AI generation errors
- `ResourceError`: Resource-related errors
- `VideoProcessingError`: Video processing errors
- `FileOperationError`: File operation errors
- `ValidationError`: Input validation errors

#### `error_handler(operation_name: str, reraise: bool = False) -> Callable`

Decorator for consistent error handling.

#### `create_error_context(operation: str, error_code: str, details: Dict[str, Any]) -> Dict[str, Any]`

Create error context dictionary.

#### `log_error_with_context(logger: logging.Logger, message: str, context: Dict[str, Any]) -> None`

Log error with context information.

### utils/validation_utils.py

#### `validate_string_input(value: Any, field_name: str, min_length: int = 1, max_length: int = 1000, allow_empty: bool = False, pattern: Optional[str] = None) -> str`

Validate string input with comprehensive checks.

#### `validate_list_input(value: Any, field_name: str, min_items: int = 1, max_items: int = 100, item_type: Optional[type] = None, allow_empty: bool = False) -> List[Any]`

Validate list input with comprehensive checks.

#### `validate_numeric_input(value: Any, field_name: str, min_value: Optional[float] = None, max_value: Optional[float] = None, allow_negative: bool = True, allow_zero: bool = True) -> float`

Validate numeric input with range checks.

#### `validate_file_path_input(value: Any, field_name: str, must_exist: bool = True, must_be_file: bool = True, must_be_directory: bool = False, allowed_extensions: Optional[List[str]] = None) -> Path`

Validate file path input with existence and type checks.

#### `validate_script_input(script_data: Dict[str, Any]) -> Dict[str, Any]`

Validate script data structure.

#### `validate_video_specs(width: int, height: int, fps: float, duration: float) -> Tuple[int, int, float, float]`

Validate video specifications.

#### `validate_audio_specs(sample_rate: int, channels: int, duration: float) -> Tuple[int, int, float]`

Validate audio specifications.

#### `validate_youtube_shorts_content(title: str, description: str, script: str, duration: float, scene_descriptions: List[str]) -> Dict[str, Any]`

Validate complete YouTube Shorts content.

### utils/resource_manager.py

#### `ResourceManager`

Centralized resource management.

**Methods:**
- `register_resource(name: str, resource: Any, cleanup_func: Optional[callable] = None) -> None`
- `unregister_resource(name: str) -> None`
- `cleanup_resource(name: str) -> bool`
- `cleanup_all() -> int`

#### Context Managers

- `gpu_memory_context(clear_cache: bool = True) -> ContextManager`
- `temp_file_context(suffix: str = ".tmp", prefix: str = "temp_", delete: bool = True) -> ContextManager`
- `temp_directory_context(prefix: str = "temp_") -> ContextManager`
- `file_handle_context(file_path: Union[str, Path], mode: str = 'r', encoding: str = 'utf-8') -> ContextManager`
- `process_context(command: List[str], **kwargs) -> ContextManager`
- `api_client_context(client_class: type, *args, **kwargs) -> ContextManager`

#### Managed Resources

- `ManagedResource`: Base class for managed resources
- `GPUResource`: GPU resource with automatic cleanup
- `FileResource`: File resource with automatic cleanup

#### Decorators

- `cleanup_on_exit(func: callable) -> callable`: Register cleanup function for exit
- `with_resource_cleanup(cleanup_func: callable) -> callable`: Ensure resource cleanup after function

### utils/performance_optimizer.py

#### `PerformanceOptimizer`

Performance optimization and caching.

**Methods:**
- `cached_function(cache_key_func: Callable, use_disk: bool = False, ttl: int = 3600) -> Callable`: Caching decorator

#### `optimize_stable_diffusion_settings(current_settings: Dict[str, Any]) -> Dict[str, Any]`

Optimize Stable Diffusion settings based on system resources.

### utils/logging_utils.py

#### `setup_logging(log_level: int = logging.INFO, log_file: Optional[str] = None, max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5) -> logging.Logger`

Setup application logging.

#### `get_logger(name: str = "youtube_shorts") -> logging.Logger`

Get logger instance.

#### `StructuredLogger`

Structured logging with context.

**Methods:**
- `set_context(**kwargs) -> None`: Set logging context
- `info(message: str, **kwargs) -> None`: Log info message
- `warning(message: str, **kwargs) -> None`: Log warning message
- `error(message: str, **kwargs) -> None`: Log error message

#### Decorators

- `log_step(step_name: str, description: str) -> Callable`: Log step entry/exit
- `log_ai_generation(provider: str, model: str) -> Callable`: Log AI generation details

## Helper Modules

### helpers/ai_prompt_optimizer.py

#### `optimize_prompts_with_ai(prompts: List[str], context: Optional[Dict[str, Any]] = None) -> List[str]`

Optimize prompts using AI.

### helpers/controlnet_processor.py

#### `process_control_images(images: List[str], control_type: str = "canny") -> List[str]`

Process images for ControlNet.

### helpers/image_quality_analyzer.py

#### `analyze_image_quality(image_path: str) -> Dict[str, Any]`

Analyze image quality metrics.

#### `generate_refinement_prompt(image_path: str, quality_issues: List[str]) -> str`

Generate refinement prompt for image.

### helpers/sd_webui_api.py

#### `SDWebUIAPI`

Stable Diffusion WebUI API client.

**Methods:**
- `generate_image(prompt: str, **kwargs) -> str`: Generate single image
- `generate_images(prompts: List[str], **kwargs) -> List[str]`: Generate multiple images

## Settings

### settings/config.py

#### `Config`

Main configuration class with settings for:

- **AI Providers**: Groq, Ollama configuration
- **Stable Diffusion**: Model and method settings
- **Video**: Resolution, FPS, duration settings
- **Audio**: Voice and language settings
- **Paths**: Directory and file path settings

## Error Handling

### Exception Hierarchy

```
Exception
├── AIGenerationError
├── ResourceError
├── VideoProcessingError
├── FileOperationError
└── ValidationError
```

### Error Codes

- `AI_ERROR`: AI generation errors
- `GPU_OOM`: GPU out of memory
- `FFMPEG_ERROR`: FFmpeg processing errors
- `FILE_NOT_FOUND`: File not found
- `INVALID_INPUT`: Input validation errors
- `RESOURCE_ERROR`: Resource management errors

## Type Definitions

### Common Types

```python
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from pathlib import Path

# Common type aliases
VideoSpecs = Tuple[int, int, float, float]  # width, height, fps, duration
AudioSpecs = Tuple[int, int, float]  # sample_rate, channels, duration
WordTimestamp = Dict[str, Any]  # word, start, end
ScriptData = Dict[str, Any]  # title, script, description, etc.
```

### Configuration Types

```python
class AIConfig:
    provider: str
    model: str
    api_key: Optional[str]
    endpoint: Optional[str]

class VideoConfig:
    width: int
    height: int
    fps: float
    max_duration: float

class AudioConfig:
    language: str
    voice: str
    engine: str
```

## Usage Patterns

### Basic Workflow

```python
# 1. Generate script
script_data = write_script_with_ollama("Space facts")

# 2. Create voice
voice_result = create_voice_narration(script_data['script'])

# 3. Generate backgrounds
backgrounds = generate_ai_backgrounds(script_data['scene_descriptions'])

# 4. Create video clips
video_clips = images_to_video_clips(backgrounds)

# 5. Generate captions
captions = create_shorts_captions(generate_word_timestamps(script_data['script'], voice_result['duration']))

# 6. Combine everything
final_video = combine_into_final_video(
    video_clips=video_clips,
    audio_path=voice_result['audio_path'],
    audio_duration=voice_result['duration'],
    caption_ass_path=captions,
    output_name="space_facts_video"
)
```

### Error Handling Pattern

```python
from utils.error_handler import error_handler, AIGenerationError

@error_handler("my_operation", reraise=True)
def my_operation():
    try:
        # Operation logic
        return result
    except Exception as e:
        raise AIGenerationError(
            "Operation failed",
            "OPERATION_ERROR",
            {"details": str(e)}
        )
```

### Resource Management Pattern

```python
from utils.resource_manager import gpu_memory_context, temp_file_context

with gpu_memory_context():
    with temp_file_context(suffix=".mp4") as temp_file:
        # GPU operations with temporary file
        process_video(temp_file)
```

### Validation Pattern

```python
from utils.validation_utils import validate_string_input, validate_video_specs

# Validate inputs
title = validate_string_input(title, "title", min_length=1, max_length=100)
width, height, fps, duration = validate_video_specs(1080, 1920, 30.0, 15.0)
```
