"""
Video Processing Utilities

Provides comprehensive FFmpeg command building, video operations,
and hardware acceleration support for YouTube Shorts generation.
"""

import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from settings.config import Config

logger = logging.getLogger(__name__)


class VideoProcessingError(Exception):
    """Base exception for video processing operations"""
    pass


class FFmpegCommandBuilder:
    """Builder class for constructing FFmpeg commands with hardware acceleration"""
    
    def __init__(self, use_hardware_acceleration: bool = True):
        """
        Initialize FFmpeg command builder
        
        Args:
            use_hardware_acceleration: Whether to use hardware acceleration
        """
        self.use_hardware_acceleration = use_hardware_acceleration
        self.input_args = []
        self.filter_complex_parts = []
        self.output_args = []
        self.input_count = 0
        
        # Hardware acceleration settings
        self.hw_encoder = getattr(Config, "HARDWARE_ENCODER", "h264_nvenc")
        self.hw_decoder = getattr(Config, "HARDWARE_DECODER", "h264_cuvid")
        self.nvenc_preset = getattr(Config, "NVENC_PRESET", "p1")
        self.nvenc_tune = getattr(Config, "NVENC_TUNE", "ull")
        self.nvenc_rc = getattr(Config, "NVENC_RC", "cbr")
        self.nvenc_bitrate = getattr(Config, "NVENC_BITRATE", "5M")
        self.nvenc_max_bitrate = getattr(Config, "NVENC_MAX_BITRATE", "8M")
        self.nvenc_gop_size = getattr(Config, "NVENC_GOP_SIZE", 30)
    
    def add_input(self, path: Union[str, Path], duration: Optional[float] = None, 
                  is_image: bool = False, is_color: bool = False, 
                  color: Optional[str] = None) -> int:
        """
        Add input to the command
        
        Args:
            path: Path to input file or color specification
            duration: Duration in seconds
            is_image: Whether this is an image (will be looped)
            is_color: Whether this is a color input
            color: Color specification for color input
            
        Returns:
            Input index for referencing in filters
        """
        input_index = self.input_count
        self.input_count += 1
        
        if is_color:
            # Color input
            color_hex = color or "%02x%02x%02x" % (30, 30, 40)
            self.input_args.extend([
                "-f", "lavfi",
                "-t", str(duration or 1.0),
                "-i", f"color=c=#{color_hex}:s={Config.VIDEO_WIDTH}x{Config.VIDEO_HEIGHT}:r={Config.VIDEO_FPS}"
            ])
        elif is_image:
            # Image input (will be looped)
            self.input_args.extend([
                "-loop", "1",
                "-t", str(duration or 1.0),
                "-i", str(path)
            ])
        else:
            # Video input
            self.input_args.extend([
                "-t", str(duration or 1.0),
                "-i", str(path)
            ])
        
        return input_index
    
    def add_scale_filter(self, input_index: int, output_label: str, 
                        width: int = None, height: int = None) -> str:
        """
        Add scaling filter for input
        
        Args:
            input_index: Index of input to scale
            output_label: Label for output of this filter
            width: Target width (defaults to config)
            height: Target height (defaults to config)
            
        Returns:
            Output label for chaining
        """
        width = width or Config.VIDEO_WIDTH
        height = height or Config.VIDEO_HEIGHT
        
        filter_parts = [
            f"[{input_index}:v]",
            f"scale=w={width}:h={height}:force_original_aspect_ratio=decrease,",
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,",
            f"setsar=1[{output_label}]"
        ]
        
        self.filter_complex_parts.append("".join(filter_parts))
        return output_label
    
    def add_ken_burns_filter(self, input_index: int, output_label: str,
                            duration: float, zoom_start: float = 1.0,
                            zoom_end: float = 1.05) -> str:
        """
        Add Ken Burns effect filter
        
        Args:
            input_index: Index of input image
            output_label: Label for output
            duration: Duration of effect
            zoom_start: Starting zoom level
            zoom_end: Ending zoom level
            
        Returns:
            Output label for chaining
        """
        filter_parts = [
            f"[{input_index}:v]",
            f"scale=iw*1.12:ih*1.12,",
            f"zoompan=z='min(zoom+0.0025,1.12)':",
            f"d={int(duration * Config.VIDEO_FPS)}:",
            f"x='iw/2-(iw/zoom/2)':",
            f"y='ih/2-(ih/zoom/2)':",
            f"s={Config.VIDEO_WIDTH}x{Config.VIDEO_HEIGHT}[{output_label}]"
        ]
        
        self.filter_complex_parts.append("".join(filter_parts))
        return output_label
    
    def add_concat_filter(self, input_labels: List[str], output_label: str) -> str:
        """
        Add concatenation filter for multiple inputs
        
        Args:
            input_labels: List of input labels to concatenate
            output_label: Label for output
            
        Returns:
            Output label for chaining
        """
        concat_inputs = "".join(f"[{label}]" for label in input_labels)
        concat_filter = f"{concat_inputs}concat=n={len(input_labels)}:v=1:a=0[{output_label}]"
        
        self.filter_complex_parts.append(concat_filter)
        return output_label
    
    def add_subtitles_filter(self, input_label: str, output_label: str,
                           ass_path: str) -> str:
        """
        Add ASS subtitles filter
        
        Args:
            input_label: Input label
            output_label: Output label
            ass_path: Path to ASS subtitle file
            
        Returns:
            Output label for chaining
        """
        fonts_dir = Path("fonts")
        ass_norm = str(Path(ass_path)).replace("\\", "/")
        fonts_norm = str(fonts_dir).replace("\\", "/")
        
        filter_parts = [
            f"[{input_label}]",
            f"subtitles={ass_norm}:fontsdir={fonts_norm}[{output_label}]"
        ]
        
        self.filter_complex_parts.append("".join(filter_parts))
        return output_label
    
    def add_watermark_filter(self, input_label: str, output_label: str,
                           text: str, position: str = "top-right") -> str:
        """
        Add watermark text filter
        
        Args:
            input_label: Input label
            output_label: Output label
            text: Watermark text
            position: Position of watermark
            
        Returns:
            Output label for chaining
        """
        # Escape text for FFmpeg
        escaped_text = text.replace(":", "\\:").replace("'", "\\'")
        
        # Position calculations
        pos_map = {
            "top-right": "x=w-tw-20:y=20",
            "top-left": "x=20:y=20",
            "bottom-right": "x=w-tw-20:y=h-th-20",
            "bottom-left": "x=20:y=h-th-20"
        }
        pos_xy = pos_map.get(position, "x=w-tw-20:y=20")
        
        filter_parts = [
            f"[{input_label}]",
            f"drawtext=text='{escaped_text}':",
            f"fontcolor=white:fontsize={Config.WATERMARK_FONT_SIZE}:",
            f"{pos_xy}:alpha={Config.WATERMARK_OPACITY}[{output_label}]"
        ]
        
        self.filter_complex_parts.append("".join(filter_parts))
        return output_label
    
    def set_output_args(self, output_path: Union[str, Path], 
                       audio_input_index: int, duration: float,
                       fps: int = None) -> None:
        """
        Set output arguments
        
        Args:
            output_path: Path to output file
            audio_input_index: Index of audio input
            duration: Duration in seconds
            fps: Frames per second (defaults to config)
        """
        fps = fps or Config.VIDEO_FPS
        
        self.output_args = [
            "-map", "[vout]",
            "-map", f"{audio_input_index}:a",
            "-shortest",
            "-r", str(fps),
            "-t", str(max(0.1, duration))
        ]
        
        # Add hardware acceleration if enabled
        if self.use_hardware_acceleration:
            self.output_args.extend([
                "-c:v", self.hw_encoder,
                "-preset", self.nvenc_preset,
                "-tune", self.nvenc_tune,
                "-rc", self.nvenc_rc,
                "-b:v", self.nvenc_bitrate,
                "-maxrate", self.nvenc_max_bitrate,
                "-g", str(self.nvenc_gop_size)
            ])
        else:
            self.output_args.extend([
                "-c:v", "libx264",
                "-preset", "fast"
            ])
        
        # Audio codec
        self.output_args.extend([
            "-c:a", Config.AUDIO_CODEC,
            "-b:a", Config.AUDIO_BITRATE
        ])
        
        # Threads
        threads = getattr(Config, "FFMPEG_THREADS", 0) or 0
        if threads > 0:
            self.output_args.extend(["-threads", str(threads)])
        
        # Output file
        self.output_args.append(str(output_path))
    
    def build_command(self) -> List[str]:
        """Build the complete FFmpeg command"""
        cmd = ["ffmpeg", "-y"]
        cmd.extend(self.input_args)
        
        if self.filter_complex_parts:
            cmd.extend(["-filter_complex", ";".join(self.filter_complex_parts)])
        
        cmd.extend(self.output_args)
        return cmd
    
    def validate_command(self) -> Tuple[bool, str]:
        """
        Validate the command before execution
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.input_args:
            return False, "No inputs specified"
        
        if not self.output_args:
            return False, "No output specified"
        
        if self.input_count == 0:
            return False, "No input files added"
        
        return True, ""


def create_ken_burns_video(image_path: Union[str, Path], duration: float,
                          output_path: Union[str, Path]) -> str:
    """
    Create Ken Burns effect video from image
    
    Args:
        image_path: Path to input image
        duration: Duration of video
        output_path: Path to output video
        
    Returns:
        Path to created video
    """
    builder = FFmpegCommandBuilder()
    
    # Add image input
    input_idx = builder.add_input(image_path, duration, is_image=True)
    
    # Add Ken Burns effect
    builder.add_ken_burns_filter(input_idx, "ken_burns", duration)
    
    # Set output
    builder.set_output_args(output_path, 0, duration)  # No audio for Ken Burns
    
    # Build and execute command
    cmd = builder.build_command()
    
    try:
        logger.info(f"Creating Ken Burns video: {Path(image_path).name}")
        result = subprocess.run(cmd, text=True, capture_output=True)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg failed: {result.stderr}")
            raise VideoProcessingError(f"Ken Burns creation failed: {result.stderr}")
        
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Ken Burns error: {e}")
        raise VideoProcessingError(f"Failed to create Ken Burns video: {e}")


def create_static_video(image_path: Union[str, Path], duration: float,
                       output_path: Union[str, Path]) -> str:
    """
    Create static video from image
    
    Args:
        image_path: Path to input image
        duration: Duration of video
        output_path: Path to output video
        
    Returns:
        Path to created video
    """
    builder = FFmpegCommandBuilder()
    
    # Add image input
    input_idx = builder.add_input(image_path, duration, is_image=True)
    
    # Add scaling filter
    builder.add_scale_filter(input_idx, "scaled", Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT)
    
    # Set output
    builder.set_output_args(output_path, 0, duration)  # No audio
    
    # Build and execute command
    cmd = builder.build_command()
    
    try:
        logger.info(f"Creating static video: {Path(image_path).name}")
        result = subprocess.run(cmd, text=True, capture_output=True)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg failed: {result.stderr}")
            raise VideoProcessingError(f"Static video creation failed: {result.stderr}")
        
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Static video error: {e}")
        raise VideoProcessingError(f"Failed to create static video: {e}")


def combine_video_with_audio(video_clips: List[Union[str, Path]], 
                           audio_path: Union[str, Path],
                           audio_duration: float,
                           output_path: Union[str, Path],
                           caption_ass_path: Optional[str] = None) -> str:
    """
    Combine video clips with audio using optimized FFmpeg command
    
    Args:
        video_clips: List of video/image paths
        audio_path: Path to audio file
        audio_duration: Duration of audio
        output_path: Path to output video
        caption_ass_path: Optional path to ASS subtitle file
        
    Returns:
        Path to created video
    """
    builder = FFmpegCommandBuilder(use_hardware_acceleration=True)
    
    # Add video inputs
    video_labels = []
    for i, clip in enumerate(video_clips):
        clip_path = Path(clip)
        if clip_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
            # Video file
            input_idx = builder.add_input(clip, audio_duration / len(video_clips))
        else:
            # Image file
            input_idx = builder.add_input(clip, audio_duration / len(video_clips), is_image=True)
        
        # Scale each input
        label = f"v{i}"
        builder.add_scale_filter(input_idx, label)
        video_labels.append(label)
    
    # Concatenate videos
    if video_labels:
        concat_label = builder.add_concat_filter(video_labels, "vc")
    else:
        # No video clips, create solid background
        input_idx = builder.add_input("", audio_duration, is_color=True)
        concat_label = builder.add_scale_filter(input_idx, "vc")
    
    # Add subtitles if provided
    current_label = concat_label
    if caption_ass_path and Path(caption_ass_path).exists():
        current_label = builder.add_subtitles_filter(concat_label, "vc_subs", caption_ass_path)
    
    # Add watermark
    watermark_text = getattr(Config, "WATERMARK_TEXT", "AI Generated")
    watermark_pos = getattr(Config, "WATERMARK_POSITION_MODE", "top-right")
    final_label = builder.add_watermark_filter(current_label, "vout", watermark_text, watermark_pos)
    
    # Add audio input
    audio_input_idx = builder.add_input(audio_path)
    
    # Set output
    builder.set_output_args(output_path, audio_input_idx, audio_duration)
    
    # Build and execute command
    cmd = builder.build_command()
    
    try:
        logger.info(f"Combining video with audio: {len(video_clips)} clips")
        logger.debug(f"FFmpeg command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, text=True, capture_output=True)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg failed: {result.stderr}")
            raise VideoProcessingError(f"Video combination failed: {result.stderr}")
        
        logger.info(f"Video created successfully: {output_path}")
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Video combination error: {e}")
        raise VideoProcessingError(f"Failed to combine video: {e}")


def check_ffmpeg_availability() -> Tuple[bool, str]:
    """
    Check if FFmpeg is available and supports required features
    
    Returns:
        Tuple of (is_available, version_info)
    """
    try:
        result = subprocess.run(["ffmpeg", "-version"], 
                              text=True, capture_output=True, timeout=10)
        
        if result.returncode != 0:
            return False, "FFmpeg not found in PATH"
        
        version_info = result.stdout.split('\n')[0]
        return True, version_info
        
    except FileNotFoundError:
        return False, "FFmpeg not installed"
    except subprocess.TimeoutExpired:
        return False, "FFmpeg timeout"
    except Exception as e:
        return False, f"FFmpeg check failed: {e}"


def check_hardware_acceleration() -> Dict[str, bool]:
    """
    Check available hardware acceleration features
    
    Returns:
        Dictionary of available acceleration features
    """
    acceleration = {
        "nvenc": False,
        "cuvid": False,
        "qsv": False,
        "vaapi": False
    }
    
    try:
        result = subprocess.run(["ffmpeg", "-encoders"], 
                              text=True, capture_output=True, timeout=10)
        
        if result.returncode == 0:
            output = result.stdout.lower()
            acceleration["nvenc"] = "h264_nvenc" in output
            acceleration["cuvid"] = "h264_cuvid" in output
            acceleration["qsv"] = "h264_qsv" in output
            acceleration["vaapi"] = "h264_vaapi" in output
        
    except Exception as e:
        logger.warning(f"Could not check hardware acceleration: {e}")
    
    return acceleration


if __name__ == "__main__":
    # Test video utilities
    print("=" * 60)
    print("VIDEO UTILITIES TEST")
    print("=" * 60)
    
    # Check FFmpeg availability
    available, version = check_ffmpeg_availability()
    print(f"FFmpeg Available: {available}")
    if available:
        print(f"Version: {version}")
    
    # Check hardware acceleration
    hw_accel = check_hardware_acceleration()
    print(f"\nHardware Acceleration:")
    for feature, supported in hw_accel.items():
        print(f"  {feature}: {'✓' if supported else '✗'}")
    
    # Test command builder
    print(f"\nTesting FFmpegCommandBuilder...")
    builder = FFmpegCommandBuilder()
    
    # Add test inputs
    input1 = builder.add_input("test1.jpg", 3.0, is_image=True)
    input2 = builder.add_input("test2.jpg", 3.0, is_image=True)
    
    # Add filters
    label1 = builder.add_scale_filter(input1, "v1")
    label2 = builder.add_scale_filter(input2, "v2")
    concat_label = builder.add_concat_filter([label1, label2], "vc")
    final_label = builder.add_watermark_filter(concat_label, "vout", "Test Watermark")
    
    # Set output
    builder.set_output_args("test_output.mp4", 0, 6.0)
    
    # Build command
    cmd = builder.build_command()
    print(f"Generated command: {' '.join(cmd)}")
    
    print("\nTest completed successfully!")
