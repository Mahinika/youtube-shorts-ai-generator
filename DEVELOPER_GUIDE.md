# YouTube Shorts Automation - Developer Guide

## Overview

This project is a comprehensive YouTube Shorts automation system that generates AI-powered video content using various AI providers, Stable Diffusion for background generation, and FFmpeg for video processing. The system has been extensively refactored and optimized for maintainability, performance, and reliability.

## Architecture

### Core Components

1. **Step Modules** (`steps/`): The main workflow steps
   - `step1_write_script.py`: AI script generation
   - `step2_create_voice.py`: Text-to-speech conversion
   - `step3_generate_backgrounds.py`: AI background image generation
   - `step4_add_captions.py`: Caption generation
   - `step5_combine_everything.py`: Final video assembly

2. **Utility Modules** (`utils/`): Reusable utility functions
   - `gpu_manager.py`: GPU memory management
   - `tts_manager.py`: Text-to-speech management
   - `video_utils.py`: Video processing utilities
   - `sd_generation_manager.py`: Stable Diffusion generation
   - `error_handler.py`: Error handling and custom exceptions
   - `validation_utils.py`: Input validation
   - `resource_manager.py`: Resource cleanup and management
   - `performance_optimizer.py`: Performance optimization
   - `logging_utils.py`: Logging utilities

3. **Helper Modules** (`helpers/`): AI enhancement modules
   - `ai_prompt_optimizer.py`: AI prompt optimization
   - `controlnet_processor.py`: ControlNet processing
   - `image_quality_analyzer.py`: Image quality analysis
   - `sd_webui_api.py`: Stable Diffusion WebUI API integration

4. **Settings** (`settings/`): Configuration management
   - `config.py`: Main configuration settings

## Key Features

### 1. AI Integration
- **Multiple AI Providers**: Support for Groq, Ollama, and Edge TTS
- **Automatic Fallback**: Seamless switching between providers
- **Prompt Optimization**: AI-enhanced prompt generation
- **Quality Analysis**: Automated image quality assessment

### 2. GPU Management
- **Memory Management**: Comprehensive GPU memory handling
- **Context Managers**: Safe GPU operations with automatic cleanup
- **Compatibility Checking**: Automatic GPU capability detection
- **OOM Prevention**: Out-of-memory error prevention

### 3. Resource Management
- **Context Managers**: Automatic resource cleanup
- **Resource Tracking**: Centralized resource management
- **Cleanup Decorators**: Automatic cleanup on exit
- **Memory Optimization**: Efficient memory usage

### 4. Error Handling
- **Custom Exceptions**: Specialized exception types
- **Error Context**: Detailed error information
- **Logging Integration**: Comprehensive error logging
- **Graceful Degradation**: Fallback mechanisms

### 5. Input Validation
- **Type Validation**: Comprehensive type checking
- **Range Validation**: Value range validation
- **Format Validation**: Format and pattern validation
- **Business Logic Validation**: Domain-specific validation

### 6. Performance Optimization
- **Caching**: Intelligent caching system
- **Async Operations**: Asynchronous processing
- **Resource Pooling**: Connection and resource pooling
- **Dynamic Optimization**: Runtime performance tuning

## Usage Examples

### Basic Script Generation

```python
from steps.step1_write_script import write_script_with_ollama

# Generate a script for a space facts video
script_data = write_script_with_ollama("Amazing facts about space exploration")
print(f"Title: {script_data['title']}")
print(f"Script: {script_data['script']}")
```

### Voice Generation

```python
from steps.step2_create_voice import create_voice_narration

# Generate voice narration
voice_result = create_voice_narration(
    script_text="Welcome to our space facts video!",
    voice_name="en-US-AriaNeural"
)
print(f"Audio file: {voice_result['audio_path']}")
```

### Background Generation

```python
from steps.step3_generate_backgrounds import generate_ai_backgrounds

# Generate AI backgrounds
scene_descriptions = [
    "A beautiful starfield with nebula",
    "A close-up of a planet with rings",
    "A spaceship flying through space"
]
backgrounds = generate_ai_backgrounds(scene_descriptions)
print(f"Generated {len(backgrounds)} background images")
```

### Video Assembly

```python
from steps.step5_combine_everything import combine_into_final_video

# Combine all elements into final video
video_clips = ["clip1.mp4", "clip2.mp4", "clip3.mp4"]
audio_path = "narration.mp3"
output_video = combine_into_final_video(
    video_clips=video_clips,
    audio_path=audio_path,
    audio_duration=15.0,
    caption_ass_path="captions.ass",
    output_name="space_facts_video"
)
print(f"Final video: {output_video}")
```

### Using GPU Management

```python
from utils.gpu_manager import gpu_memory_context, get_gpu_manager

# Safe GPU operations
with gpu_memory_context(clear_cache=True):
    # Your GPU operations here
    gpu_manager = get_gpu_manager()
    memory_info = gpu_manager.get_memory_info()
    print(f"GPU memory: {memory_info['free']} MB free")
```

### Using Resource Management

```python
from utils.resource_manager import temp_file_context, GPUResource

# Temporary file management
with temp_file_context(suffix=".mp4", prefix="video_") as temp_file:
    # Process video file
    process_video(temp_file)
# File automatically cleaned up

# GPU resource management
with GPUResource("my_gpu_operation") as gpu_res:
    # GPU operations
    perform_gpu_operation()
# GPU resources automatically cleaned up
```

### Input Validation

```python
from utils.validation_utils import validate_string_input, validate_video_specs

# Validate string input
title = validate_string_input(
    "My Video Title",
    "title",
    min_length=1,
    max_length=100
)

# Validate video specifications
width, height, fps, duration = validate_video_specs(
    1080, 1920, 30.0, 15.0
)
```

### Error Handling

```python
from utils.error_handler import error_handler, AIGenerationError

@error_handler("my_operation", reraise=True)
def my_ai_operation():
    try:
        # AI operation
        result = perform_ai_operation()
        return result
    except Exception as e:
        raise AIGenerationError(
            "AI operation failed",
            "AI_ERROR",
            {"operation": "my_operation", "error": str(e)}
        )
```

## Configuration

### Main Configuration (`settings/config.py`)

```python
# AI Provider Settings
AI_PROVIDER = "groq"  # or "ollama"
GROQ_MODEL = "llama-3.1-70b-versatile"
OLLAMA_MODEL = "llama3.1:70b"

# Stable Diffusion Settings
SD_METHOD = "webui"  # or "diffusers"
SD_WEBUI_HOST = "http://localhost:7860"
SD_MODEL = "dreamshaper_8.safetensors"

# Video Settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30.0
MAX_VIDEO_DURATION = 60.0

# Audio Settings
VOICE_LANGUAGE = "en"
EDGE_TTS_VOICE = "en-US-AriaNeural"
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_validation_utils.py -v

# Run with coverage
python -m pytest tests/ --cov=utils --cov-report=html
```

### Test Structure

- `tests/test_validation_utils.py`: Input validation tests
- `tests/test_error_handler.py`: Error handling tests
- `tests/test_gpu_manager.py`: GPU management tests
- `tests/test_resource_manager.py`: Resource management tests

## Performance Optimization

### Caching

```python
from utils.performance_optimizer import performance_optimizer

@performance_optimizer.cached_function(
    cache_key_func=lambda text: f"tts_{hash(text)}",
    use_disk=True,
    ttl=3600  # 1 hour cache
)
def expensive_operation(text):
    # Expensive operation here
    return result
```

### GPU Optimization

```python
from utils.gpu_manager import get_gpu_manager

gpu_manager = get_gpu_manager()
# Optimize GPU settings based on available memory
optimized_settings = gpu_manager.optimize_for_memory()
```

## Error Handling Best Practices

### 1. Use Custom Exceptions

```python
from utils.error_handler import AIGenerationError, ValidationError

# Good
if not valid_input:
    raise ValidationError("Invalid input", "INVALID_INPUT")

# Bad
if not valid_input:
    raise ValueError("Invalid input")
```

### 2. Provide Error Context

```python
try:
    result = ai_operation()
except Exception as e:
    raise AIGenerationError(
        "AI operation failed",
        "AI_ERROR",
        {"input": input_data, "error": str(e)}
    )
```

### 3. Use Error Handler Decorator

```python
@error_handler("operation_name", reraise=True)
def my_function():
    # Function implementation
    pass
```

## Resource Management Best Practices

### 1. Use Context Managers

```python
# Good
with gpu_memory_context():
    perform_gpu_operation()

# Bad
perform_gpu_operation()
# Manual cleanup required
```

### 2. Register Resources

```python
from utils.resource_manager import get_resource_manager

resource_manager = get_resource_manager()
resource_manager.register_resource("my_resource", resource, cleanup_func)
```

### 3. Automatic Cleanup

```python
from utils.resource_manager import cleanup_on_exit

@cleanup_on_exit
def cleanup_function():
    # Cleanup code
    pass
```

## Logging

### Structured Logging

```python
from utils.logging_utils import get_structured_logger

logger = get_structured_logger("my_module")
logger.set_context(operation="video_processing", user_id="123")
logger.info("Processing started")
```

### Step Logging

```python
from utils.logging_utils import log_step

@log_step("video_processing", "Process video file")
def process_video(file_path):
    # Processing logic
    pass
```

## Development Guidelines

### 1. Code Organization
- Keep functions small and focused
- Use type hints for all functions
- Add comprehensive docstrings
- Follow PEP 8 style guidelines

### 2. Error Handling
- Use custom exceptions for domain errors
- Provide detailed error context
- Implement graceful degradation
- Log all errors appropriately

### 3. Testing
- Write unit tests for all utility functions
- Test error conditions
- Use mocking for external dependencies
- Maintain high test coverage

### 4. Performance
- Use caching for expensive operations
- Implement resource cleanup
- Monitor memory usage
- Optimize for GPU operations

### 5. Documentation
- Document all public APIs
- Provide usage examples
- Keep documentation up to date
- Include error handling examples

## Troubleshooting

### Common Issues

1. **GPU Memory Errors**
   - Use `gpu_memory_context()` for GPU operations
   - Check available GPU memory
   - Reduce batch sizes if needed

2. **AI Provider Errors**
   - Check provider availability
   - Verify API keys and endpoints
   - Use fallback providers

3. **File Operation Errors**
   - Check file permissions
   - Verify file paths
   - Use proper error handling

4. **Validation Errors**
   - Check input data types
   - Verify required fields
   - Use validation utilities

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug logging for specific modules
logger = logging.getLogger("utils.gpu_manager")
logger.setLevel(logging.DEBUG)
```

## Contributing

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Add comprehensive docstrings
- Write unit tests

### Pull Request Process
1. Create feature branch
2. Write tests for new functionality
3. Update documentation
4. Submit pull request
5. Address review feedback

### Testing Requirements
- All new code must have tests
- Maintain test coverage above 80%
- Test error conditions
- Use mocking for external dependencies

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Check the documentation
- Review existing issues
- Create a new issue with detailed information
- Include error logs and system information
