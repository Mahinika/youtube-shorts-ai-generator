"""
STEP 5: COMBINE EVERYTHING

Combines AI backgrounds, audio, and captions into final YouTube Short using pure FFmpeg.
Output: 1080x1920 vertical video, 9:16 aspect ratio, up to 60 seconds.
"""

import sys
import json
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from settings.config import Config


def combine_into_final_video(
    video_clips: list,
    audio_path: str,
    audio_duration: float,
    caption_clips: list,
    output_name: str,
) -> str:
    """
    Combine all elements into final YouTube Short using pure FFmpeg.

    Specifications:
    - Resolution: 1080x1920 (9:16 vertical)
    - Duration: Up to 60 seconds
    - Format: MP4 with H.264 codec

    Args:
        video_clips: List of image paths or video clips
        audio_path: Path to audio narration
        audio_duration: Duration in seconds
        caption_clips: List of caption data (currently unused - captions via FFmpeg)
        output_name: Output filename (without extension)

    Returns:
        Path to final video file
    """

    print("Combining into final YouTube Short using pure FFmpeg...")

    # Ensure duration does not exceed 60 seconds
    if audio_duration > Config.MAX_DURATION_SECONDS:
        print(f"WARNING: Trimming to {Config.MAX_DURATION_SECONDS} seconds")
        audio_duration = Config.MAX_DURATION_SECONDS

    # Create output directory
    output_dir = Path(Config.OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Clean output filename
    safe_name = "".join(c for c in output_name if c.isalnum() or c in (" ", "-", "_"))[
        :50
    ]
    output_path = output_dir / f"{safe_name}.mp4"

    # Ensure unique filename
    counter = 1
    while output_path.exists():
        output_path = output_dir / f"{safe_name}_{counter}.mp4"
        counter += 1

    print(f"  Output: {output_path}")

    # Build FFmpeg command
    ffmpeg_cmd = _build_ffmpeg_command(
        video_clips, audio_path, audio_duration, output_name, str(output_path)
    )

    # Execute FFmpeg with real-time output
    print("  Running FFmpeg composition...")
    print("  FFmpeg command:", " ".join(ffmpeg_cmd))
    try:
        result = subprocess.run(ffmpeg_cmd, text=True)
        if result.returncode != 0:
            print(f"FFmpeg failed with return code: {result.returncode}")
            raise RuntimeError(f"FFmpeg failed with return code: {result.returncode}")
        
        print(f"\nVideo saved: {output_path}")
        print(f"Duration: {audio_duration:.1f} seconds")
        print(f"Resolution: {Config.VIDEO_WIDTH}x{Config.VIDEO_HEIGHT} (9:16)")
        
        return str(output_path)
        
    except Exception as e:
        print(f"Error during FFmpeg execution: {e}")
        raise


def _build_ffmpeg_command(video_clips, audio_path, audio_duration, output_name, output_path):
    """Build the complete FFmpeg command for video composition."""
    
    input_args = []
    filter_complex_parts = []
    concat_parts = []
    
    # Calculate segment duration
    segment_duration = max(0.5, float(audio_duration) / max(1, len(video_clips)))
    
    input_index = 0
    
    # Process video clips
    for idx, clip in enumerate(video_clips):
        if isinstance(clip, str) and Path(clip).exists():
            clip_path = Path(clip)
            if clip_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
                # Video file - use directly
                input_args.extend([
                    "-t", f"{segment_duration}",
                    "-i", str(clip)
                ])
            else:
                # Image file - use loop input
                input_args.extend([
                    "-loop", "1",
                    "-t", f"{segment_duration}",
                    "-i", str(clip)
                ])
        elif hasattr(clip, 'filename') and clip.filename:
            # MoviePy object with filename
            input_args.extend([
                "-loop", "1",
                "-t", f"{segment_duration}",
                "-i", str(clip.filename)
            ])
        else:
            # Fallback: create colored background
            color_hex = "%02x%02x%02x" % (30, 30, 40)  # Dark blue-gray
            input_args.extend([
                "-f", "lavfi",
                "-t", f"{segment_duration}",
                "-i", f"color=c=#{color_hex}:s={Config.VIDEO_WIDTH}x{Config.VIDEO_HEIGHT}:r={Config.VIDEO_FPS}"
            ])
        
        # Scale and pad to correct resolution
        label = f"v{idx}"
        filter_complex_parts.append(
            f"[{input_index}:v]scale=w={Config.VIDEO_WIDTH}:h={Config.VIDEO_HEIGHT}:"
            f"force_original_aspect_ratio=decrease,"
            f"pad={Config.VIDEO_WIDTH}:{Config.VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
            f"setsar=1[{label}]"
        )
        concat_parts.append(f"[{label}]")
        input_index += 1
    
    # Build concat filter
    if concat_parts:
        concat_filter = "".join(concat_parts) + f"concat=n={len(concat_parts)}:v=1:a=0[vc]"
        filter_complex_parts.append(concat_filter)
    else:
        # No video clips, create solid background
        filter_complex_parts.append(
            f"[0:v]setsar=1[vc]"
        )
    
    # Add captions if available
    current_filter = "vc"
    try:
        captions = _generate_captions(output_name, audio_duration)
        if captions:
            print(f"  Adding {len(captions)} caption phrases...")
            for i, caption in enumerate(captions):
                next_filter = f"vc{i+1}" if i < len(captions)-1 else "vc_final"
                filter_complex_parts.append(
                    f"[{current_filter}]drawtext=text='{caption['text']}':"
                    f"fontcolor={Config.CAPTION_FONT_COLOR}:"
                    f"fontsize={Config.CAPTION_FONT_SIZE}:"
                    f"borderw={Config.CAPTION_STROKE_WIDTH}:"
                    f"bordercolor={Config.CAPTION_STROKE_COLOR}:"
                    f"x=(w-tw)/2:y=(h/2):"
                    f"enable='between(t,{caption['start']:.2f},{caption['end']:.2f})'[{next_filter}]"
                )
                current_filter = next_filter
    except Exception as e:
        print(f"  Caption error: {e}")
    
    # Add watermark
    wm_text = Config.WATERMARK_TEXT.replace(":", "\\:").replace("'", "\\'")
    pos = getattr(Config, "WATERMARK_POSITION_MODE", "top-right")
    if pos == "bottom-right":
        wm_xy = "x=w-tw-20:y=h-th-20"
    elif pos == "top-left":
        wm_xy = "x=20:y=20"
    elif pos == "bottom-left":
        wm_xy = "x=20:y=h-th-20"
    else:
        wm_xy = "x=w-tw-20:y=20"
    
    filter_complex_parts.append(
        f"[{current_filter}]drawtext=text='{wm_text}':"
        f"fontcolor=white:fontsize={Config.WATERMARK_FONT_SIZE}:"
        f"{wm_xy}:alpha={Config.WATERMARK_OPACITY}[vout]"
    )
    
    # Join all filters
    filter_complex = ";".join(filter_complex_parts)
    
    # Build complete command
    cmd = [
        "ffmpeg", "-y",
        *input_args,
        "-i", str(audio_path),
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", f"{input_index}:a",
        "-shortest",
        "-r", str(Config.VIDEO_FPS),
        "-vcodec", Config.VIDEO_CODEC,
        "-acodec", Config.AUDIO_CODEC,
        "-b:a", Config.AUDIO_BITRATE,
        "-preset", getattr(Config, "VIDEO_PRESET", "veryfast"),
        "-crf", str(getattr(Config, "VIDEO_CRF", 23)),
        "-t", str(max(0.1, float(audio_duration))),
        "-threads", str(getattr(Config, "FFMPEG_THREADS", 0) or 0),
        str(output_path)
    ]
    
    return cmd


def _generate_captions(output_name, audio_duration):
    """Generate caption data from script metadata."""
    try:
        from steps.step1_write_script import generate_word_timestamps
        
        sidecar = Path(Config.METADATA_DIR) / f"{output_name}.json"
        if not sidecar.exists():
            return []
            
        with open(sidecar, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            
        if "script" not in meta:
            return []
            
        words = generate_word_timestamps(meta["script"], audio_duration)
        
        # Group words into phrases (2-3 words each)
        phrases = []
        for i in range(0, len(words), 2):
            phrase_words = words[i:i+2]
            if phrase_words:
                phrase_text = " ".join([w["word"] for w in phrase_words])
                start_time = phrase_words[0]["start"]
                end_time = phrase_words[-1]["end"]
                phrases.append({
                    "text": phrase_text.upper().replace(":", "\\:").replace("'", "\\'"),
                    "start": start_time,
                    "end": end_time
                })
        
        # Limit to 20 phrases max for performance
        return phrases[:20]
        
    except Exception as e:
        print(f"  Caption generation error: {e}")
        return []


def create_ken_burns_effect(image_path: str, duration: float, output_path: str) -> str:
    """Create Ken Burns effect using FFmpeg zoom and pan."""
    
    # Ken Burns parameters
    zoom_start = 1.0
    zoom_end = 1.05  # 5% zoom in
    pan_x = 0.0      # No horizontal pan
    pan_y = 0.0      # No vertical pan
    
    # FFmpeg command for Ken Burns effect
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-t", str(duration),
        "-vf", f"scale=iw*1.1:ih*1.1,zoompan=z='if(lte(zoom,1.0),1.0,max(1.001,zoom-0.0015))':"
               f"d={int(duration * Config.VIDEO_FPS)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
               f"s={Config.VIDEO_WIDTH}x{Config.VIDEO_HEIGHT}",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-r", str(Config.VIDEO_FPS),
        str(output_path)
    ]
    
    try:
        print(f"  Creating Ken Burns effect: {Path(image_path).name}")
        result = subprocess.run(cmd, text=True)
        if result.returncode != 0:
            print(f"Ken Burns FFmpeg failed with return code: {result.returncode}")
            # Fallback: simple static image
            return _create_static_video(image_path, duration, output_path)
        return output_path
    except Exception as e:
        print(f"Ken Burns error: {e}")
        # Fallback: simple static image
        return _create_static_video(image_path, duration, output_path)


def _create_static_video(image_path: str, duration: float, output_path: str) -> str:
    """Create static video from image as fallback."""
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-t", str(duration),
        "-vf", f"scale={Config.VIDEO_WIDTH}:{Config.VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,"
               f"pad={Config.VIDEO_WIDTH}:{Config.VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-r", str(Config.VIDEO_FPS),
        str(output_path)
    ]
    
    try:
        print(f"  Creating static video: {Path(image_path).name}")
        subprocess.run(cmd, text=True)
        return output_path
    except Exception as e:
        print(f"Static video creation error: {e}")
        raise


if __name__ == "__main__":
    print("This module combines video, audio, and captions using pure FFmpeg")
    print("Run from main program, not standalone")
    print("\nTo test, use: python start_app.py")