"""
TTS (Text-to-Speech) Manager

Provides simplified, robust TTS functionality with connection pooling
and proper async handling for Edge TTS and gTTS fallback.
"""

import asyncio
import logging
import tempfile
import threading
import wave
from pathlib import Path
from typing import Optional, Dict, Any, Union
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    edge_tts = None

try:
    from gtts import gTTS
    from pydub import AudioSegment
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    gTTS = None
    AudioSegment = None

try:
    from piper import PiperVoice
    PIPER_TTS_AVAILABLE = True
except ImportError:
    PIPER_TTS_AVAILABLE = False
    PiperVoice = None

from settings.config import Config
from utils.performance_optimizer import performance_optimizer
from utils.resource_manager import ManagedResource, get_resource_manager

logger = logging.getLogger(__name__)


class TTSError(Exception):
    """Base exception for TTS operations"""
    pass


class TTSManager(ManagedResource):
    """Simplified TTS manager with connection pooling and fallback support"""
    
    def __init__(self, preferred_engine: str = "edge", voice: Optional[str] = None):
        """
        Initialize TTS manager
        
        Args:
            preferred_engine: Preferred TTS engine ("edge" or "gtts")
            voice: Voice to use (if None, uses config default)
        """
        self.preferred_engine = preferred_engine.lower()
        self.voice = voice or getattr(Config, "EDGE_TTS_VOICE", "en-US-AriaNeural")
        self.language = getattr(Config, "VOICE_LANGUAGE", "en")
        
        # Check availability
        self.edge_available = EDGE_TTS_AVAILABLE
        self.gtts_available = GTTS_AVAILABLE
        self.piper_available = PIPER_TTS_AVAILABLE
        
        if not (self.edge_available or self.gtts_available or self.piper_available):
            raise TTSError("No TTS engines available. Install piper-tts, edge-tts, or gtts.")
        
        # Initialize as managed resource
        super().__init__(f"tts_manager_{self.preferred_engine}_{self.voice}", self._cleanup_tts)
        self.resource_manager = get_resource_manager()
        
        logger.info(f"TTS Manager initialized - Edge: {self.edge_available}, gTTS: {self.gtts_available}")
    
    def _cleanup_tts(self) -> None:
        """Cleanup TTS resources."""
        try:
            # Cleanup any active connections or resources
            if hasattr(self, '_edge_connection'):
                self._edge_connection = None
            logger.debug("Cleaned up TTS resources")
        except Exception as e:
            logger.warning(f"Error during TTS cleanup: {e}")
    
    def _clean_text(self, text: str) -> str:
        """Clean text for TTS processing"""
        import re
        
        # Remove sound effects in parentheses
        text = re.sub(r'\([^)]*\)', '', text)
        
        # Remove sound effects in brackets
        text = re.sub(r'\[[^\]]*\]', '', text)
        
        # Remove emojis and symbols
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"  # enclosed characters
            "\U0001F900-\U0001F9FF"  # supplemental symbols
            "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
            "\U00002600-\U000026FF"  # miscellaneous symbols
            "\U00002700-\U000027BF"  # dingbats
            "]+", 
            flags=re.UNICODE
        )
        text = emoji_pattern.sub('', text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _generate_with_edge_tts(self, text: str, output_path: Path) -> bool:
        """Generate audio using Edge TTS (simplified async handling)"""
        if not self.edge_available:
            return False
        
        try:
            # Use asyncio.run() in a thread to avoid event loop conflicts
            def run_edge_tts():
                async def generate_audio():
                    communicate = edge_tts.Communicate(text, voice=self.voice)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                        await communicate.save(tmp.name)
                        return tmp.name
                
                return asyncio.run(generate_audio())
            
            # Run in thread to avoid blocking
            result_container = []
            exception_container = []
            
            def thread_worker():
                try:
                    temp_file = run_edge_tts()
                    result_container.append(temp_file)
                except Exception as e:
                    exception_container.append(e)
            
            thread = threading.Thread(target=thread_worker)
            thread.start()
            thread.join(timeout=30)  # 30 second timeout
            
            if exception_container:
                raise exception_container[0]
            
            if not result_container:
                raise TTSError("Edge TTS generation failed - no result")
            
            # Convert to final format
            temp_file = result_container[0]
            try:
                audio = AudioSegment.from_file(temp_file)
                audio.export(str(output_path), format="mp3")
                return True
            finally:
                # Clean up temp file
                try:
                    Path(temp_file).unlink()
                except:
                    pass
        
        except Exception as e:
            logger.warning(f"Edge TTS failed: {e}")
            return False
    
    def _generate_with_piper_tts(self, text: str, output_path: Path) -> bool:
        """Generate speech using Piper TTS (high quality, local)"""
        try:
            if not self.piper_available:
                logger.warning("Piper TTS not available, skipping")
                return False
            
            # Get model paths from config
            model_path = getattr(Config, 'PIPER_MODEL_PATH', None)
            config_path = getattr(Config, 'PIPER_CONFIG_PATH', None)
            use_cuda = getattr(Config, 'PIPER_USE_CUDA', False)
            
            if not model_path or not config_path:
                logger.error("Piper TTS model paths not configured")
                return False
            
            # Check if model files exist
            if not Path(model_path).exists() or not Path(config_path).exists():
                logger.error(f"Piper TTS model files not found: {model_path}, {config_path}")
                return False
            
            # Load Piper voice model
            logger.info("Loading Piper TTS model...")
            voice = PiperVoice.load(model_path, config_path, use_cuda=use_cuda)
            
            # Clean text for TTS
            cleaned_text = self._clean_text(text)
            
            # Generate audio directly to WAV file
            logger.info(f"Generating speech with Piper TTS: {len(cleaned_text)} characters")
            with wave.open(str(output_path), "wb") as wav_file:
                voice.synthesize_wav(cleaned_text, wav_file)
            
            logger.info(f"Piper TTS generated audio: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Piper TTS generation failed: {e}")
            return False
    
    def _generate_with_gtts(self, text: str, output_path: Path) -> bool:
        """Generate audio using gTTS"""
        if not self.gtts_available:
            return False
        
        try:
            tts = gTTS(text=text, lang=self.language, slow=False)
            tts.save(str(output_path))
            return True
        except Exception as e:
            logger.warning(f"gTTS failed: {e}")
            return False
    
    @performance_optimizer.cached_function(
        cache_key_func=lambda self, text, output_path: 
            f"tts_audio:{hash(text)}:{self.voice}:{self.language}",
        use_disk=True,
        ttl=7200  # 2 hour cache for audio
    )
    def generate_audio(self, text: str, output_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Generate audio from text with automatic fallback
        
        Args:
            text: Text to convert to speech
            output_path: Path to save audio file
            
        Returns:
            Dictionary with 'success', 'path', 'duration', 'engine' keys
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Clean text
        cleaned_text = self._clean_text(text)
        if not cleaned_text:
            raise TTSError("Text is empty after cleaning")
        
        logger.info(f"Generating TTS audio: {len(cleaned_text)} characters")
        logger.debug(f"Original text length: {len(text)}, Cleaned: {len(cleaned_text)}")
        
        # Try engines in order of preference
        engines_to_try = []
        
        # Check TTS provider from config
        tts_provider = getattr(Config, 'TTS_PROVIDER', 'piper').lower()
        
        if tts_provider == "piper" and self.piper_available:
            engines_to_try.append(("piper", self._generate_with_piper_tts))
        elif tts_provider == "edge" and self.edge_available:
            engines_to_try.append(("edge", self._generate_with_edge_tts))
        elif tts_provider == "gtts" and self.gtts_available:
            engines_to_try.append(("gtts", self._generate_with_gtts))
        
        # Add fallbacks
        if self.piper_available and tts_provider != "piper":
            engines_to_try.append(("piper", self._generate_with_piper_tts))
        if self.edge_available and tts_provider != "edge":
            engines_to_try.append(("edge", self._generate_with_edge_tts))
        if self.gtts_available and tts_provider != "gtts":
            engines_to_try.append(("gtts", self._generate_with_gtts))
        
        if not engines_to_try:
            raise TTSError("No TTS engines available")
        
        # Try each engine
        for engine_name, engine_func in engines_to_try:
            try:
                logger.info(f"Trying {engine_name} TTS...")
                success = engine_func(cleaned_text, output_path)
                
                if success and output_path.exists():
                    # Get duration
                    try:
                        audio = AudioSegment.from_mp3(str(output_path))
                        duration = len(audio) / 1000.0
                        
                        # Trim if exceeds maximum duration
                        max_duration = getattr(Config, "MAX_DURATION_SECONDS", 60)
                        if duration > max_duration:
                            logger.warning(f"Audio duration {duration:.1f}s exceeds max {max_duration}s")
                            logger.info(f"Trimming to {max_duration} seconds...")
                            
                            trimmed_audio = audio[:max_duration * 1000]
                            trimmed_audio.export(str(output_path), format="mp3")
                            duration = max_duration
                        
                        logger.info(f"TTS generation successful with {engine_name}: {duration:.1f}s")
                        
                        return {
                            "success": True,
                            "path": str(output_path),
                            "duration": duration,
                            "engine": engine_name
                        }
                    except Exception as e:
                        logger.warning(f"Error processing audio file: {e}")
                        continue
                
            except Exception as e:
                logger.warning(f"{engine_name} TTS failed: {e}")
                continue
        
        raise TTSError("All TTS engines failed")
    
    def get_available_voices(self) -> Dict[str, list]:
        """Get available voices for each engine"""
        voices = {}
        
        if self.edge_available:
            # Common Edge TTS voices
            voices["edge"] = [
                "en-US-AriaNeural",
                "en-US-GuyNeural", 
                "en-US-EricNeural",
                "en-US-ChristopherNeural",
                "en-US-JennyNeural",
                "en-US-MichelleNeural"
            ]
        
        if self.gtts_available:
            # gTTS languages
            voices["gtts"] = ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"]
        
        return voices


# Global TTS manager instance
_tts_manager: Optional[TTSManager] = None


def get_tts_manager() -> TTSManager:
    """Get global TTS manager instance"""
    global _tts_manager
    if _tts_manager is None:
        _tts_manager = TTSManager()
    return _tts_manager


def create_voice_narration(script_text: str, voice_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Create voice narration from script text (simplified interface)
    
    Args:
        script_text: The narrative script
        voice_name: Optional voice name override
        
    Returns:
        Dictionary with 'path' and 'duration' keys
    """
    manager = get_tts_manager()
    
    # Override voice if provided
    if voice_name:
        manager.voice = voice_name
    
    # Create temp directory
    temp_dir = Path(Config.TEMP_DIR)
    temp_dir.mkdir(parents=True, exist_ok=True)
    output_path = temp_dir / "narration.mp3"
    
    try:
        result = manager.generate_audio(script_text, output_path)
        return {
            "path": result["path"],
            "duration": result["duration"]
        }
    except TTSError as e:
        logger.error(f"Voice narration failed: {e}")
        raise


if __name__ == "__main__":
    # Test TTS manager
    print("=" * 60)
    print("TTS MANAGER TEST")
    print("=" * 60)
    
    try:
        manager = TTSManager()
        
        # Test text
        test_text = "This is a test of the TTS system. It should work with both Edge TTS and gTTS fallback."
        
        print(f"Testing with text: {test_text[:50]}...")
        
        # Generate audio
        result = manager.generate_audio(test_text, "test_output.mp3")
        
        print(f"Success: {result['success']}")
        print(f"Engine: {result['engine']}")
        print(f"Duration: {result['duration']:.1f}s")
        print(f"Output: {result['path']}")
        
        # Clean up
        Path("test_output.mp3").unlink()
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")
