"""
Configuration Validation Utilities

Provides comprehensive configuration validation and environment setup
for the YouTube Shorts automation system.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from utils.error_handler import ConfigurationError, ValidationError, FileOperationError
from utils.validation_utils import validate_string_input, validate_numeric_input, validate_file_path_input


logger = logging.getLogger(__name__)


class ConfigValidator:
    """
    Comprehensive configuration validator for the YouTube Shorts automation system.
    
    Validates all configuration values, checks dependencies, and ensures
    the system is properly set up for operation.
    """
    
    def __init__(self, config_module):
        """
        Initialize configuration validator.
        
        Args:
            config_module: The Config module to validate
        """
        self.config = config_module
        self.validation_results = {}
        self.errors = []
        self.warnings = []
    
    def validate_all(self) -> Dict[str, Any]:
        """
        Validate all configuration settings.
        
        Returns:
            Dictionary with validation results and recommendations
        """
        logger.info("Starting comprehensive configuration validation...")
        
        # Clear previous results
        self.validation_results = {}
        self.errors = []
        self.warnings = []
        
        # Validate core settings
        self._validate_paths()
        self._validate_ai_providers()
        self._validate_video_settings()
        self._validate_audio_settings()
        self._validate_stable_diffusion_settings()
        self._validate_environment_variables()
        self._validate_dependencies()
        
        # Compile results
        result = {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "recommendations": self._generate_recommendations(),
            "summary": self._generate_summary()
        }
        
        self.validation_results = result
        return result
    
    def _validate_paths(self):
        """Validate all path-related configuration."""
        logger.info("Validating paths...")
        
        # Validate output directory
        try:
            output_dir = validate_file_path_input(
                self.config.OUTPUT_DIR, "OUTPUT_DIR", must_exist=False
            )
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ Output directory: {output_dir}")
        except Exception as e:
            self.errors.append(f"Output directory validation failed: {e}")
        
        # Validate temp directory
        try:
            temp_dir = validate_file_path_input(
                self.config.TEMP_DIR, "TEMP_DIR", must_exist=False
            )
            temp_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ Temp directory: {temp_dir}")
        except Exception as e:
            self.errors.append(f"Temp directory validation failed: {e}")
        
        # Validate logs directory
        try:
            logs_dir = Path(self.config.LOGS_DIR)
            logs_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ Logs directory: {logs_dir}")
        except Exception as e:
            self.errors.append(f"Logs directory validation failed: {e}")
    
    def _validate_ai_providers(self):
        """Validate AI provider configuration."""
        logger.info("Validating AI providers...")
        
        # Validate AI provider selection
        valid_providers = ["groq", "ollama", "grok"]
        if self.config.AI_PROVIDER not in valid_providers:
            self.errors.append(f"Invalid AI provider: {self.config.AI_PROVIDER}. Must be one of {valid_providers}")
        
        # Validate provider-specific settings
        if self.config.AI_PROVIDER == "groq":
            self._validate_groq_config()
        elif self.config.AI_PROVIDER == "ollama":
            self._validate_ollama_config()
        elif self.config.AI_PROVIDER == "grok":
            self._validate_grok_config()
    
    def _validate_groq_config(self):
        """Validate Groq-specific configuration."""
        if not hasattr(self.config, 'GROQ_API_KEY') or not self.config.GROQ_API_KEY:
            self.errors.append("GROQ_API_KEY not set for Groq provider")
        else:
            try:
                validate_string_input(self.config.GROQ_API_KEY, "GROQ_API_KEY", min_length=10)
                logger.info("✓ Groq API key configured")
            except Exception as e:
                self.errors.append(f"Groq API key validation failed: {e}")
        
        if not hasattr(self.config, 'GROQ_MODEL') or not self.config.GROQ_MODEL:
            self.warnings.append("GROQ_MODEL not set, using default")
    
    def _validate_ollama_config(self):
        """Validate Ollama-specific configuration."""
        if not hasattr(self.config, 'OLLAMA_HOST') or not self.config.OLLAMA_HOST:
            self.warnings.append("OLLAMA_HOST not set, using default localhost:11434")
        
        if not hasattr(self.config, 'OLLAMA_MODEL') or not self.config.OLLAMA_MODEL:
            self.warnings.append("OLLAMA_MODEL not set, using default")
    
    def _validate_grok_config(self):
        """Validate Grok-specific configuration."""
        if not hasattr(self.config, 'GROK_API_KEY') or not self.config.GROK_API_KEY:
            self.errors.append("GROK_API_KEY not set for Grok provider")
        else:
            try:
                validate_string_input(self.config.GROK_API_KEY, "GROK_API_KEY", min_length=10)
                logger.info("✓ Grok API key configured")
            except Exception as e:
                self.errors.append(f"Grok API key validation failed: {e}")
    
    def _validate_video_settings(self):
        """Validate video-related configuration."""
        logger.info("Validating video settings...")
        
        # Validate video dimensions
        try:
            width = validate_numeric_input(
                self.config.VIDEO_WIDTH, "VIDEO_WIDTH", min_value=64, max_value=4096
            )
            height = validate_numeric_input(
                self.config.VIDEO_HEIGHT, "VIDEO_HEIGHT", min_value=64, max_value=4096
            )
            
            # Check if dimensions are divisible by 8 (SD requirement)
            if width % 8 != 0 or height % 8 != 0:
                self.warnings.append(f"Video dimensions {width}x{height} not divisible by 8 (SD requirement)")
            
            logger.info(f"✓ Video dimensions: {width}x{height}")
        except Exception as e:
            self.errors.append(f"Video dimensions validation failed: {e}")
        
        # Validate FPS
        try:
            fps = validate_numeric_input(
                self.config.VIDEO_FPS, "VIDEO_FPS", min_value=1.0, max_value=120.0
            )
            logger.info(f"✓ Video FPS: {fps}")
        except Exception as e:
            self.errors.append(f"Video FPS validation failed: {e}")
        
        # Validate duration limits
        try:
            max_duration = validate_numeric_input(
                self.config.MAX_DURATION_SECONDS, "MAX_DURATION_SECONDS", 
                min_value=1.0, max_value=60.0
            )
            logger.info(f"✓ Max duration: {max_duration}s")
        except Exception as e:
            self.errors.append(f"Max duration validation failed: {e}")
    
    def _validate_audio_settings(self):
        """Validate audio-related configuration."""
        logger.info("Validating audio settings...")
        
        # Validate TTS settings
        if hasattr(self.config, 'TTS_VOICE'):
            try:
                validate_string_input(self.config.TTS_VOICE, "TTS_VOICE", min_length=1, max_length=50)
                logger.info(f"✓ TTS voice: {self.config.TTS_VOICE}")
            except Exception as e:
                self.warnings.append(f"TTS voice validation failed: {e}")
        
        # Validate audio quality settings
        if hasattr(self.config, 'AUDIO_QUALITY'):
            valid_qualities = ["low", "medium", "high"]
            if self.config.AUDIO_QUALITY not in valid_qualities:
                self.warnings.append(f"Invalid audio quality: {self.config.AUDIO_QUALITY}")
    
    def _validate_stable_diffusion_settings(self):
        """Validate Stable Diffusion configuration."""
        logger.info("Validating Stable Diffusion settings...")
        
        # Validate model path
        if hasattr(self.config, 'STABLE_DIFFUSION_MODEL'):
            try:
                validate_string_input(self.config.STABLE_DIFFUSION_MODEL, "STABLE_DIFFUSION_MODEL", min_length=1)
                logger.info(f"✓ SD model: {self.config.STABLE_DIFFUSION_MODEL}")
            except Exception as e:
                self.warnings.append(f"SD model validation failed: {e}")
        
        # Validate generation settings
        if hasattr(self.config, 'SD_INFERENCE_STEPS'):
            try:
                steps = validate_numeric_input(
                    self.config.SD_INFERENCE_STEPS, "SD_INFERENCE_STEPS", 
                    min_value=1, max_value=100
                )
                logger.info(f"✓ SD inference steps: {steps}")
            except Exception as e:
                self.warnings.append(f"SD inference steps validation failed: {e}")
        
        # Validate WebUI settings
        if hasattr(self.config, 'SD_WEBUI_HOST'):
            try:
                validate_string_input(self.config.SD_WEBUI_HOST, "SD_WEBUI_HOST", min_length=1)
                logger.info(f"✓ SD WebUI host: {self.config.SD_WEBUI_HOST}")
            except Exception as e:
                self.warnings.append(f"SD WebUI host validation failed: {e}")
    
    def _validate_environment_variables(self):
        """Validate required environment variables."""
        logger.info("Validating environment variables...")
        
        required_vars = []
        if self.config.AI_PROVIDER == "groq":
            required_vars.append("GROQ_API_KEY")
        elif self.config.AI_PROVIDER == "grok":
            required_vars.append("GROK_API_KEY")
        
        for var in required_vars:
            if not os.getenv(var):
                self.errors.append(f"Required environment variable {var} not set")
            else:
                logger.info(f"✓ Environment variable {var} is set")
    
    def _validate_dependencies(self):
        """Validate required dependencies."""
        logger.info("Validating dependencies...")
        
        # Check for required Python packages
        required_packages = [
            "torch", "diffusers", "transformers", "accelerate",
            "gtts", "pydub", "requests", "PIL"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"✓ Package {package} available")
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.errors.append(f"Missing required packages: {missing_packages}")
        
        # Check for FFmpeg
        try:
            import subprocess
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✓ FFmpeg available")
            else:
                self.errors.append("FFmpeg not available or not working")
        except FileNotFoundError:
            self.errors.append("FFmpeg not found in PATH")
        except Exception as e:
            self.warnings.append(f"Could not verify FFmpeg: {e}")
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if self.warnings:
            recommendations.append("Review warnings above for potential improvements")
        
        if not self.errors:
            recommendations.append("Configuration is valid and ready for use")
        
        # Performance recommendations
        if hasattr(self.config, 'SD_ATTENTION_SLICING') and not self.config.SD_ATTENTION_SLICING:
            recommendations.append("Consider enabling SD_ATTENTION_SLICING for better memory usage")
        
        if hasattr(self.config, 'SD_LOW_MEMORY_MODE') and not self.config.SD_LOW_MEMORY_MODE:
            recommendations.append("Consider enabling SD_LOW_MEMORY_MODE for 6GB GPUs")
        
        return recommendations
    
    def _generate_summary(self) -> str:
        """Generate validation summary."""
        if not self.errors and not self.warnings:
            return "✅ Configuration is valid and ready for use"
        elif not self.errors:
            return f"⚠️ Configuration is valid with {len(self.warnings)} warnings"
        else:
            return f"❌ Configuration has {len(self.errors)} errors and {len(self.warnings)} warnings"


def validate_configuration(config_module) -> Dict[str, Any]:
    """
    Validate configuration module.
    
    Args:
        config_module: The Config module to validate
        
    Returns:
        Validation results dictionary
    """
    validator = ConfigValidator(config_module)
    return validator.validate_all()


def check_system_requirements() -> Dict[str, Any]:
    """
    Check system requirements for the YouTube Shorts automation system.
    
    Returns:
        System requirements check results
    """
    logger.info("Checking system requirements...")
    
    results = {
        "python_version": None,
        "gpu_available": False,
        "gpu_info": {},
        "memory_available": 0,
        "disk_space": 0,
        "recommendations": []
    }
    
    # Check Python version
    import sys
    results["python_version"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    if sys.version_info < (3, 8):
        results["recommendations"].append("Python 3.8+ recommended")
    
    # Check GPU availability
    try:
        import torch
        if torch.cuda.is_available():
            results["gpu_available"] = True
            results["gpu_info"] = {
                "name": torch.cuda.get_device_name(0),
                "memory": torch.cuda.get_device_properties(0).total_memory / 1024**3,
                "count": torch.cuda.device_count()
            }
            logger.info(f"✓ GPU available: {results['gpu_info']['name']}")
        else:
            results["recommendations"].append("GPU recommended for Stable Diffusion")
    except ImportError:
        results["recommendations"].append("PyTorch not installed")
    
    # Check memory
    try:
        import psutil
        memory = psutil.virtual_memory()
        results["memory_available"] = memory.available / 1024**3
        if memory.available < 8 * 1024**3:  # 8GB
            results["recommendations"].append("8GB+ RAM recommended")
    except ImportError:
        results["recommendations"].append("psutil not available for memory check")
    
    # Check disk space
    try:
        import shutil
        free_space = shutil.disk_usage(".").free / 1024**3
        results["disk_space"] = free_space
        if free_space < 10:  # 10GB
            results["recommendations"].append("10GB+ free disk space recommended")
    except Exception as e:
        results["recommendations"].append(f"Could not check disk space: {e}")
    
    return results
