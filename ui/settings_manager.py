"""
SETTINGS MANAGER

Handles reading, writing, and validation of configuration settings.
Manages both session settings and persistent config.py updates.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from settings.config import Config


class SettingsManager:
    """Manages configuration settings with validation and persistence"""
    
    def __init__(self):
        """Initialize settings manager"""
        self.session_settings = {}
        self.config_file_path = project_root / "settings" / "config.py"
        self.load_all_settings()
    
    def load_all_settings(self) -> Dict[str, Any]:
        """Load all settings from config.py into session settings"""
        try:
            # Get all attributes from Config class
            self.session_settings = {}
            for attr_name in dir(Config):
                if not attr_name.startswith('_') and not callable(getattr(Config, attr_name)):
                    value = getattr(Config, attr_name)
                    self.session_settings[attr_name] = value
            
            print(f"Loaded {len(self.session_settings)} settings from config.py")
            return self.session_settings
            
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.session_settings.get(key, default)
    
    def update_setting(self, key: str, value: Any) -> bool:
        """Update a setting value in session (not persisted until save)"""
        try:
            # Validate the setting value
            if self._validate_setting(key, value):
                self.session_settings[key] = value
                print(f"Updated session setting: {key} = {value}")
                return True
            else:
                print(f"Invalid value for {key}: {value}")
                return False
                
        except Exception as e:
            print(f"Error updating setting {key}: {e}")
            return False
    
    def _validate_setting(self, key: str, value: Any) -> bool:
        """Validate setting values based on their type and constraints"""
        try:
            # String settings
            if key in ['OLLAMA_MODEL', 'TTS_ENGINE', 'EDGE_TTS_VOICE', 'VOICE_LANGUAGE']:
                return isinstance(value, str) and len(value) > 0
            
            # Numeric settings with ranges
            if key == 'OLLAMA_TEMPERATURE':
                return isinstance(value, (int, float)) and 0.0 <= value <= 2.0
            elif key == 'OLLAMA_TOP_P':
                return isinstance(value, (int, float)) and 0.0 <= value <= 1.0
            elif key == 'OLLAMA_TOP_K':
                return isinstance(value, int) and 1 <= value <= 100
            elif key == 'OLLAMA_REPEAT_PENALTY':
                return isinstance(value, (int, float)) and 0.5 <= value <= 2.0
            elif key == 'SCRIPT_TARGET_WORDS':
                return isinstance(value, int) and 50 <= value <= 200
            elif key == 'SCRIPT_MIN_SCORE':
                return isinstance(value, (int, float)) and 1.0 <= value <= 10.0
            elif key == 'SD_INFERENCE_STEPS':
                return isinstance(value, int) and 1 <= value <= 50
            elif key == 'SD_GUIDANCE_SCALE':
                return isinstance(value, (int, float)) and 1.0 <= value <= 20.0
            elif key == 'SD_MAX_SCENES':
                return isinstance(value, int) and 1 <= value <= 10
            elif key == 'VIDEO_CRF':
                return isinstance(value, int) and 0 <= value <= 51
            elif key == 'CAPTION_FONT_SIZE':
                return isinstance(value, int) and 12 <= value <= 100
            elif key == 'WORDS_PER_CAPTION':
                return isinstance(value, int) and 1 <= value <= 10
            elif key == 'FFMPEG_THREADS':
                return isinstance(value, int) and value >= 0
            
            # Boolean settings
            if key in ['USE_GPU_ENCODING', 'FALLBACK_TO_CPU', 'ENABLE_PARALLEL_PROCESSING']:
                return isinstance(value, bool)
            
            # List settings
            if key in ['search_keywords']:
                return isinstance(value, list)
            
            # Default: accept any value
            return True
            
        except Exception as e:
            print(f"Validation error for {key}: {e}")
            return False
    
    def save_to_file(self) -> bool:
        """Save session settings back to config.py"""
        try:
            # Read current config.py
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                config_lines = f.readlines()
            
            # Update config.py with new values
            updated_lines = []
            updated_keys = set()
            
            for line in config_lines:
                # Check if this line contains a setting we want to update
                line_updated = False
                for key, value in self.session_settings.items():
                    if line.strip().startswith(f'{key} = '):
                        # Format the value properly
                        if isinstance(value, str):
                            # Handle strings with proper escaping
                            if '"' in value:
                                escaped_value = value.replace('"', '\\"')
                                value_str = f'"{escaped_value}"'
                            else:
                                value_str = f'"{value}"'
                        elif isinstance(value, bool):
                            value_str = "True" if value else "False"
                        elif isinstance(value, (int, float)):
                            value_str = str(value)
                        elif isinstance(value, list):
                            value_str = str(value)
                        else:
                            value_str = repr(value)
                        
                        # Preserve the original indentation
                        original_indent = len(line) - len(line.lstrip())
                        indent = ' ' * original_indent
                        updated_lines.append(f'{indent}{key} = {value_str}\n')
                        line_updated = True
                        updated_keys.add(key)
                        break
                
                if not line_updated:
                    updated_lines.append(line)
            
            # Add any new settings that weren't found in the original file
            for key, value in self.session_settings.items():
                if key not in updated_keys:
                    # Format the value properly
                    if isinstance(value, str):
                        # Handle strings with proper escaping
                        if '"' in value:
                            escaped_value = value.replace('"', '\\"')
                            value_str = f'"{escaped_value}"'
                        else:
                            value_str = f'"{value}"'
                    elif isinstance(value, bool):
                        value_str = "True" if value else "False"
                    elif isinstance(value, (int, float)):
                        value_str = str(value)
                    elif isinstance(value, list):
                        value_str = str(value)
                    else:
                        value_str = repr(value)
                    
                    # Add new setting at the end of the class (before the last line)
                    # Find the last line and insert before it
                    if updated_lines and updated_lines[-1].strip() == '':
                        # Insert before the last empty line
                        updated_lines.insert(-1, f'    {key} = {value_str}\n')
                    else:
                        # Add at the end
                        updated_lines.append(f'    {key} = {value_str}\n')
            
            # Write back to config.py
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)
            
            print(f"Saved {len(self.session_settings)} settings to config.py")
            return True
            
        except Exception as e:
            print(f"Error saving settings to file: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset session settings to original config.py values"""
        try:
            self.load_all_settings()
            print("Reset settings to defaults")
            return True
        except Exception as e:
            print(f"Error resetting settings: {e}")
            return False
    
    def get_available_models(self) -> list:
        """Get available AI models for dropdown"""
        return ["llama3.2", "mistral", "phi3", "gemma2", "qwen2.5:7b-instruct"]
    
    def get_available_voices(self) -> list:
        """Get available Edge TTS voices"""
        return [
            "en-US-AriaNeural",
            "en-US-JennyNeural", 
            "en-US-GuyNeural",
            "en-US-DavisNeural",
            "en-US-AmberNeural",
            "en-US-AnaNeural",
            "en-US-AshleyNeural",
            "en-US-BrandonNeural",
            "en-US-ChristopherNeural",
            "en-US-CoraNeural"
        ]
    
    def get_available_quality_presets(self) -> list:
        """Get available quality presets"""
        return ["draft", "balanced", "high", "production"]
    
    def get_available_caption_positions(self) -> list:
        """Get available caption positions"""
        return ["top", "center", "bottom"]
    
    def get_available_watermark_positions(self) -> list:
        """Get available watermark positions"""
        return ["top-left", "top-right", "bottom-left", "bottom-right"]
    
    def get_available_video_presets(self) -> list:
        """Get available video encoding presets"""
        return ["ultrafast", "fast", "medium", "slow", "veryslow"]


if __name__ == "__main__":
    # Test the settings manager
    sm = SettingsManager()
    
    print("Available settings:")
    for key in sorted(sm.session_settings.keys()):
        print(f"  {key}: {sm.session_settings[key]}")
    
    print(f"\nAvailable models: {sm.get_available_models()}")
    print(f"Available voices: {sm.get_available_voices()}")
    print(f"Available quality presets: {sm.get_available_quality_presets()}")
