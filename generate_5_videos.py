"""
Generate 5 YouTube Shorts with Stable Diffusion backgrounds
Each video will be 30 seconds with unique topics
"""

import json
import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from steps.step1_write_script import write_script_with_ollama
from steps.step2_create_voice import create_voice_narration
from steps.step3_generate_backgrounds import generate_ai_backgrounds, images_to_video_clips
from steps.step4_add_captions import create_shorts_captions
from steps.step5_combine_everything import combine_into_final_video
from settings.config import Config

# 5 unique video topics for 30-second clips
VIDEO_TOPICS = [
    "Mind-blowing facts about space exploration that will shock you",
    "Amazing ocean mysteries scientists still can't explain",
    "Incredible animal superpowers that seem impossible",
    "Fascinating psychology facts that explain human behavior",
    "Mind-bending physics facts that will change how you see reality"
]

def generate_single_video(topic: str, video_number: int) -> dict:
    """Generate a complete video for one topic"""
    
    print(f"\n{'='*60}")
    print(f"GENERATING VIDEO {video_number}/5")
    print(f"Topic: {topic}")
    print(f"{'='*60}")
    
    try:
        # Step 1: Generate script
        print(f"\n[STEP 1] Writing script...")
        script_data = write_script_with_ollama(topic)
        
        if not script_data:
            print(f"ERROR: Failed to generate script for: {topic}")
            return None
            
        # Save metadata
        metadata_file = Path(Config.METADATA_DIR) / f"video_{video_number}_{script_data['title'].replace(' ', '_').replace(':', '')}.json"
        metadata_file.parent.mkdir(exist_ok=True)
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(script_data, f, indent=2, ensure_ascii=False)
        
        print(f"Script saved: {metadata_file.name}")
        
        # Step 2: Generate voice
        print(f"\n[STEP 2] Creating voiceover...")
        
        # Ensure script is a string, not a list or dict
        script_text = script_data['script']
        if isinstance(script_text, list):
            # Join list elements into a single string
            script_text = ' '.join(str(item) for item in script_text)
        elif isinstance(script_text, dict):
            # Convert dict to string
            script_text = str(script_text)
        
        voice_result = create_voice_narration(script_text)
        
        if not voice_result or not voice_result.get('audio_path'):
            print(f"ERROR: Failed to generate voice for: {topic}")
            return None
            
        voice_file = voice_result['audio_path']
        audio_duration = voice_result.get('duration', 30.0)
        print(f"Voice generated: {voice_file} ({audio_duration:.1f}s)")
        
        # Step 3: Generate backgrounds with Stable Diffusion
        print(f"\n[STEP 3] Generating AI backgrounds with Stable Diffusion...")
        
        # Use scene descriptions from script, or create default ones
        scene_descriptions = script_data.get('scene_descriptions', [
            f"cinematic scene related to {topic}",
            f"dramatic visual representing {topic}",
            f"engaging background for {topic}"
        ])
        
        # Generate AI images
        image_paths = generate_ai_backgrounds(scene_descriptions, duration_per_scene=10.0)  # 30s total / 3 scenes
        
        if not image_paths:
            print(f"ERROR: Failed to generate backgrounds for: {topic}")
            return None
            
        print(f"Generated {len(image_paths)} AI backgrounds")
        
        # Convert images to video clips with Ken Burns effect
        print(f"\n[STEP 3B] Converting images to video clips...")
        video_clips = images_to_video_clips(image_paths, duration_per_image=10.0)
        
        if not video_clips:
            print(f"ERROR: Failed to create video clips for: {topic}")
            return None
            
        print(f"Created {len(video_clips)} video clips")
        
        # Step 4: Generate captions
        print(f"\n[STEP 4] Generating captions...")
        
        # Create word timestamps for captions
        from steps.step1_write_script import generate_word_timestamps
        word_timestamps = generate_word_timestamps(script_text, audio_duration)
        caption_file = create_shorts_captions(word_timestamps)
        
        print(f"Captions generated: {caption_file}")
        
        # Step 5: Combine everything into final video
        print(f"\n[STEP 5] Combining final video...")
        final_video = combine_into_final_video(
            video_clips,
            voice_file,
            audio_duration,
            caption_file,
            f"video_{video_number}_{script_data['title'].replace(' ', '_').replace(':', '')}"
        )
        
        if not final_video:
            print(f"ERROR: Failed to create final video for: {topic}")
            return None
            
        print(f"Final video created: {final_video}")
        
        return {
            'topic': topic,
            'title': script_data['title'],
            'script_data': script_data,
            'voice_file': voice_file,
            'audio_duration': audio_duration,
            'background_images': image_paths,
            'video_clips': video_clips,
            'caption_file': caption_file,
            'final_video': final_video,
            'metadata_file': str(metadata_file)
        }
        
    except Exception as e:
        print(f"ERROR generating video {video_number}: {e}")
        return None

def main():
    """Generate 5 complete YouTube Shorts"""
    
    print("STARTING BATCH VIDEO GENERATION")
    print(f"Generating 5 videos with Stable Diffusion backgrounds")
    print(f"Each video will be ~30 seconds")
    print(f"Using GPU-accelerated generation")
    
    # Check if Stable Diffusion WebUI is running
    try:
        import requests
        response = requests.get(f"{Config.SD_WEBUI_HOST}/sdapi/v1/options", timeout=5)
        if response.status_code == 200:
            print(f"Stable Diffusion WebUI is running at {Config.SD_WEBUI_HOST}")
        else:
            print(f"WARNING: Stable Diffusion WebUI may not be running properly")
    except:
        print(f"WARNING: Cannot connect to Stable Diffusion WebUI at {Config.SD_WEBUI_HOST}")
        print("   Make sure it's running: launch_sd_webui.bat")
    
    generated_videos = []
    start_time = time.time()
    
    for i, topic in enumerate(VIDEO_TOPICS, 1):
        video_result = generate_single_video(topic, i)
        
        if video_result:
            generated_videos.append(video_result)
            print(f"\nVIDEO {i} COMPLETED SUCCESSFULLY")
            print(f"   Title: {video_result['title']}")
            print(f"   Final video: {video_result['final_video']}")
        else:
            print(f"\nVIDEO {i} FAILED")
        
        # Small delay between videos to prevent resource conflicts
        if i < len(VIDEO_TOPICS):
            print(f"\nBrief pause before next video...")
            time.sleep(2)
    
    # Summary
    total_time = time.time() - start_time
    successful_videos = len(generated_videos)
    
    print(f"\n{'='*60}")
    print(f"BATCH GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"Successfully generated: {successful_videos}/5 videos")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Output directory: {Config.OUTPUT_DIR}")
    
    if generated_videos:
        print(f"\nGENERATED VIDEOS:")
        for i, video in enumerate(generated_videos, 1):
            print(f"   {i}. {video['title']}")
            print(f"      File: {video['final_video']}")
    
    if successful_videos < 5:
        print(f"\nWARNING: {5 - successful_videos} videos failed to generate")
        print("   Check error messages above for details")
    
    return generated_videos

if __name__ == "__main__":
    main()
