"""
YOUTUBE STUDIO INTERFACE

Professional GUI inspired by YouTube Studio.
Dark theme with red accents matching YouTube branding.
"""

import json
import os
import sys
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from helpers import cleanup_temp_files
from settings.config import Config
from steps import (
    check_gpu_available,
    combine_into_final_video,
    create_shorts_captions,
    create_voice_narration,
    estimate_script_duration,
    generate_ai_backgrounds,
    generate_word_timestamps,
    images_to_video_clips,
    write_script_with_ollama,
)

# YouTube Studio color scheme
YOUTUBE_DARK = "#282828"
YOUTUBE_DARKER = "#181818"
YOUTUBE_LIGHT = "#3f3f3f"
YOUTUBE_RED = "#FF0000"
YOUTUBE_RED_HOVER = "#CC0000"
YOUTUBE_TEXT = "#FFFFFF"
YOUTUBE_TEXT_SECONDARY = "#AAAAAA"


class YouTubeStudioApp:
    """Main application window with YouTube Studio styling"""

    def __init__(self):
        """Initialize the YouTube Studio interface"""

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create main window
        self.root = ctk.CTk()
        self.root.title("YouTube Shorts Maker")
        self.root.geometry("1200x800")
        
        # Console process for progress tracking
        self.console_process = None
        self.root.minsize(1000, 700)
        
        # Setup console window creation
        self.setup_console_window()

        # Configure colors
        self.root.configure(fg_color=YOUTUBE_DARKER)

        # State
        self.current_project = None
        self.is_generating = False
        self.generation_thread = None

        # Build UI
        self.create_layout()

    def setup_console_window(self):
        """Setup console window for progress tracking"""
        self.console_log_file = Path("temp_files") / "console_output.log"
        self.console_log_file.parent.mkdir(exist_ok=True)
        
    def open_console_window(self):
        """Open a console window to show generation progress"""
        try:
            # Create a simple console window using PowerShell
            console_script = f"""
            $Host.UI.RawUI.WindowTitle = "YouTube Shorts Maker - Generation Progress"
            Write-Host "============================================================" -ForegroundColor Yellow
            Write-Host "YOUTUBE SHORTS MAKER - GENERATION PROGRESS" -ForegroundColor Yellow
            Write-Host "============================================================" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "This window shows real-time progress during video generation..." -ForegroundColor Green
            Write-Host "Keep this window open to monitor the process!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Waiting for generation to start..." -ForegroundColor Cyan
            
            # Monitor the log file
            $logFile = "{self.console_log_file}"
            if (Test-Path $logFile) {{ Remove-Item $logFile }}
            
            # Start monitoring
            while ($true) {{
                Start-Sleep -Milliseconds 500
                if (Test-Path $logFile) {{
                    Get-Content $logFile -Tail 10 | ForEach-Object {{
                        Write-Host $_ -ForegroundColor White
                    }}
                    # Clear processed content
                    $content = Get-Content $logFile
                    if ($content.Count -gt 50) {{
                        $content[-50..-1] | Set-Content $logFile
                    }}
                }}
            }}
            """
            
            # Save the script to a temporary file
            script_file = Path("temp_files") / "console_monitor.ps1"
            script_file.parent.mkdir(exist_ok=True)
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(console_script)
            
            # Start the console window
            self.console_process = subprocess.Popen([
                "powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_file)
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
            
        except Exception as e:
            print(f"Could not open console window: {e}")
            
    def close_console_window(self):
        """Close the console window"""
        if self.console_process:
            try:
                self.console_process.terminate()
                self.console_process = None
            except:
                pass
                
    def log_to_console(self, message):
        """Log a message to the console window"""
        try:
            with open(self.console_log_file, 'a', encoding='utf-8') as f:
                f.write(f"{message}\n")
        except:
            pass

    def create_layout(self):
        """Build the main interface layout"""

        # Create main container with grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Left sidebar (YouTube Studio style)
        self.create_sidebar()

        # Main content area
        self.create_main_area()

    def create_sidebar(self):
        """Create left navigation sidebar"""

        sidebar = ctk.CTkFrame(
            self.root, width=250, corner_radius=0, fg_color=YOUTUBE_DARK
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # Logo area
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=20, pady=30)

        title_label = ctk.CTkLabel(
            logo_frame,
            text="YouTube Shorts",
            font=("Arial", 24, "bold"),
            text_color=YOUTUBE_TEXT,
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            logo_frame,
            text="AI Video Maker",
            font=("Arial", 12),
            text_color=YOUTUBE_TEXT_SECONDARY,
        )
        subtitle_label.pack(anchor="w")

        # Navigation buttons
        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=10, pady=20)

        self.create_nav_button(nav_frame, "Create Video", self.show_create_page)
        self.create_nav_button(nav_frame, "My Videos", self.show_videos_page)
        self.create_nav_button(nav_frame, "Settings", self.show_settings_page)

        # Bottom info
        info_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=20, side="bottom")

        status_label = ctk.CTkLabel(
            info_frame,
            text="Status: Ready",
            font=("Arial", 10),
            text_color=YOUTUBE_TEXT_SECONDARY,
        )
        status_label.pack(anchor="w")
        self.status_label = status_label

    def create_nav_button(self, parent, text, command):
        """Create a navigation button"""

        btn = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color="transparent",
            text_color=YOUTUBE_TEXT,
            hover_color=YOUTUBE_LIGHT,
            anchor="w",
            height=40,
            font=("Arial", 14),
        )
        btn.pack(fill="x", pady=5)
        return btn

    def create_main_area(self):
        """Create main content area"""

        self.main_area = ctk.CTkFrame(
            self.root, corner_radius=0, fg_color=YOUTUBE_DARKER
        )
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        # Show create page by default
        self.show_create_page()

    def clear_main_area(self):
        """Clear all widgets from main area"""
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def show_create_page(self):
        """Show the video creation page"""

        self.clear_main_area()

        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=40, pady=30)

        # Page title
        title = ctk.CTkLabel(
            scroll_frame,
            text="Create New Short",
            font=("Arial", 32, "bold"),
            text_color=YOUTUBE_TEXT,
        )
        title.pack(anchor="w", pady=(0, 30))

        # Input section
        input_section = ctk.CTkFrame(scroll_frame, fg_color=YOUTUBE_DARK)
        input_section.pack(fill="x", pady=10)

        # Prompt input
        prompt_label = ctk.CTkLabel(
            input_section,
            text="What should your Short be about?",
            font=("Arial", 16, "bold"),
            text_color=YOUTUBE_TEXT,
        )
        prompt_label.pack(anchor="w", padx=20, pady=(20, 10))

        self.prompt_input = ctk.CTkTextbox(
            input_section,
            height=100,
            font=("Arial", 14),
            fg_color=YOUTUBE_DARKER,
            border_color=YOUTUBE_LIGHT,
            border_width=2,
        )
        self.prompt_input.pack(fill="x", padx=20, pady=10)
        self.prompt_input.insert("1.0", "Amazing facts about space exploration")

        # Options
        options_frame = ctk.CTkFrame(input_section, fg_color="transparent")
        options_frame.pack(fill="x", padx=20, pady=10)

        # Video length
        length_label = ctk.CTkLabel(
            options_frame,
            text="Target Duration:",
            font=("Arial", 12),
            text_color=YOUTUBE_TEXT_SECONDARY,
        )
        length_label.pack(side="left", padx=(0, 10))

        self.duration_var = ctk.StringVar(value="45")
        duration_options = ["15", "30", "45", "60"]
        duration_menu = ctk.CTkOptionMenu(
            options_frame,
            values=duration_options,
            variable=self.duration_var,
            fg_color=YOUTUBE_LIGHT,
            button_color=YOUTUBE_RED,
            button_hover_color=YOUTUBE_RED_HOVER,
        )
        duration_menu.pack(side="left", padx=(0, 5))

        seconds_label = ctk.CTkLabel(
            options_frame,
            text="seconds",
            font=("Arial", 12),
            text_color=YOUTUBE_TEXT_SECONDARY,
        )
        seconds_label.pack(side="left", padx=(0, 20))

        # Quality preset
        quality_label = ctk.CTkLabel(
            options_frame,
            text="Quality:",
            font=("Arial", 12),
            text_color=YOUTUBE_TEXT_SECONDARY,
        )
        quality_label.pack(side="left", padx=(0, 10))

        self.quality_var = ctk.StringVar(value=Config.CURRENT_QUALITY_PRESET)
        quality_options = list(Config.QUALITY_PRESETS.keys())
        quality_menu = ctk.CTkOptionMenu(
            options_frame,
            values=quality_options,
            variable=self.quality_var,
            fg_color=YOUTUBE_LIGHT,
            button_color=YOUTUBE_RED,
            button_hover_color=YOUTUBE_RED_HOVER,
        )
        quality_menu.pack(side="left", padx=(0, 5))

        # Generate button
        generate_btn = ctk.CTkButton(
            input_section,
            text="Generate Short",
            command=self.start_generation,
            fg_color=YOUTUBE_RED,
            hover_color=YOUTUBE_RED_HOVER,
            height=50,
            font=("Arial", 16, "bold"),
        )
        generate_btn.pack(fill="x", padx=20, pady=20)
        self.generate_btn = generate_btn

        # Progress section
        progress_section = ctk.CTkFrame(scroll_frame, fg_color=YOUTUBE_DARK)
        progress_section.pack(fill="both", expand=True, pady=10)

        progress_title = ctk.CTkLabel(
            progress_section,
            text="Generation Progress",
            font=("Arial", 16, "bold"),
            text_color=YOUTUBE_TEXT,
        )
        progress_title.pack(anchor="w", padx=20, pady=(20, 10))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            progress_section, height=10, progress_color=YOUTUBE_RED
        )
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)

        # Status text
        self.progress_text = ctk.CTkLabel(
            progress_section,
            text="Ready to generate your Short",
            font=("Arial", 12),
            text_color=YOUTUBE_TEXT_SECONDARY,
        )
        self.progress_text.pack(anchor="w", padx=20, pady=(0, 20))

    def show_videos_page(self):
        """Show list of generated videos"""

        self.clear_main_area()

        scroll_frame = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=40, pady=30)

        title = ctk.CTkLabel(
            scroll_frame,
            text="My Videos",
            font=("Arial", 32, "bold"),
            text_color=YOUTUBE_TEXT,
        )
        title.pack(anchor="w", pady=(0, 30))

        # List videos from output directory
        output_dir = Path(Config.OUTPUT_DIR)

        if not output_dir.exists():
            no_videos_label = ctk.CTkLabel(
                scroll_frame,
                text="No videos yet. Create your first Short!",
                font=("Arial", 14),
                text_color=YOUTUBE_TEXT_SECONDARY,
            )
            no_videos_label.pack(pady=50)
            return

        video_files = list(output_dir.glob("*.mp4"))

        if not video_files:
            no_videos_label = ctk.CTkLabel(
                scroll_frame,
                text="No videos yet. Create your first Short!",
                font=("Arial", 14),
                text_color=YOUTUBE_TEXT_SECONDARY,
            )
            no_videos_label.pack(pady=50)
            return

        # Display videos
        for video_path in sorted(
            video_files, key=lambda x: x.stat().st_mtime, reverse=True
        ):
            self.create_video_card(scroll_frame, video_path)

    def create_video_card(self, parent, video_path):
        """Create a card for a generated video"""

        card = ctk.CTkFrame(parent, fg_color=YOUTUBE_DARK)
        card.pack(fill="x", pady=10)

        # Video info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=15)

        name_label = ctk.CTkLabel(
            info_frame,
            text=video_path.stem,
            font=("Arial", 16, "bold"),
            text_color=YOUTUBE_TEXT,
            anchor="w",
        )
        name_label.pack(side="left", fill="x", expand=True)

        # Action buttons
        btn_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        open_btn = ctk.CTkButton(
            btn_frame,
            text="Open",
            command=lambda: self.open_video(video_path),
            fg_color=YOUTUBE_LIGHT,
            hover_color=YOUTUBE_RED,
            width=100,
        )
        open_btn.pack(side="left", padx=5)

        folder_btn = ctk.CTkButton(
            btn_frame,
            text="Show in Folder",
            command=lambda: self.open_folder(video_path),
            fg_color=YOUTUBE_LIGHT,
            hover_color=YOUTUBE_RED,
            width=120,
        )
        folder_btn.pack(side="left", padx=5)

    def show_settings_page(self):
        """Show settings page"""

        self.clear_main_area()

        scroll_frame = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=40, pady=30)

        title = ctk.CTkLabel(
            scroll_frame,
            text="Settings",
            font=("Arial", 32, "bold"),
            text_color=YOUTUBE_TEXT,
        )
        title.pack(anchor="w", pady=(0, 30))

        # System Status
        status_section = ctk.CTkFrame(scroll_frame, fg_color=YOUTUBE_DARK)
        status_section.pack(fill="x", pady=10)

        status_title = ctk.CTkLabel(
            status_section,
            text="System Status",
            font=("Arial", 16, "bold"),
            text_color=YOUTUBE_TEXT,
        )
        status_title.pack(anchor="w", padx=20, pady=(20, 10))

        # GPU status
        gpu_available = check_gpu_available()
        self.create_status_indicator(
            status_section,
            "GPU (for AI Backgrounds)",
            "Available" if gpu_available else "Not Available",
            gpu_available,
        )

        # Ollama status
        import requests

        ollama_running = False
        try:
            response = requests.get(f"{Config.OLLAMA_HOST}/api/tags", timeout=2)
            ollama_running = response.status_code == 200
        except:
            pass

        self.create_status_indicator(
            status_section,
            "Ollama (Local AI)",
            "Running" if ollama_running else "Not Running",
            ollama_running,
        )

        # API Keys
        api_section = ctk.CTkFrame(scroll_frame, fg_color=YOUTUBE_DARK)
        api_section.pack(fill="x", pady=10)

        api_title = ctk.CTkLabel(
            api_section,
            text="API Configuration (Optional - for stock videos)",
            font=("Arial", 16, "bold"),
            text_color=YOUTUBE_TEXT,
        )
        api_title.pack(anchor="w", padx=20, pady=(20, 10))

        self.create_status_indicator(
            api_section,
            "Pexels API",
            "Configured" if Config.PEXELS_API_KEY else "Not Set",
            bool(Config.PEXELS_API_KEY),
        )

        self.create_status_indicator(
            api_section,
            "Pixabay API",
            "Configured" if Config.PIXABAY_API_KEY else "Not Set",
            bool(Config.PIXABAY_API_KEY),
        )

        # Paths info
        paths_section = ctk.CTkFrame(scroll_frame, fg_color=YOUTUBE_DARK)
        paths_section.pack(fill="x", pady=10)

        paths_title = ctk.CTkLabel(
            paths_section,
            text="Storage Locations (D Drive)",
            font=("Arial", 16, "bold"),
            text_color=YOUTUBE_TEXT,
        )
        paths_title.pack(anchor="w", padx=20, pady=(20, 10))

        self.create_path_display(paths_section, "Project", Config.OUTPUT_DIR)
        self.create_path_display(paths_section, "Models", Config.MODELS_DIR)
        self.create_path_display(paths_section, "Temp", Config.TEMP_DIR)

    def create_status_indicator(self, parent, name, status, is_ok):
        """Create status indicator"""

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)

        label = ctk.CTkLabel(
            frame, text=name, font=("Arial", 12), text_color=YOUTUBE_TEXT
        )
        label.pack(side="left")

        color = "#00FF00" if is_ok else "#FF0000"

        status_label = ctk.CTkLabel(
            frame, text=status, font=("Arial", 12), text_color=color
        )
        status_label.pack(side="right")

    def create_path_display(self, parent, name, path):
        """Create path display"""

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)

        label = ctk.CTkLabel(
            frame,
            text=f"{name}:",
            font=("Arial", 10),
            text_color=YOUTUBE_TEXT_SECONDARY,
        )
        label.pack(side="left")

        path_label = ctk.CTkLabel(
            frame,
            text=str(path)[:60] + "..." if len(str(path)) > 60 else str(path),
            font=("Arial", 10),
            text_color=YOUTUBE_TEXT_SECONDARY,
        )
        path_label.pack(side="right")

    def start_generation(self):
        """Start video generation process"""

        if self.is_generating:
            return

        prompt = self.prompt_input.get("1.0", "end-1c").strip()

        if not prompt:
            messagebox.showerror("Error", "Please enter a video prompt")
            return

        # Set quality preset from UI selection
        Config.CURRENT_QUALITY_PRESET = self.quality_var.get()

        # OPTIMIZATION: Pre-generation cleanup
        from helpers.cleanup_temp_files import cleanup_temp_files_before_generation
        cleanup_temp_files_before_generation()

        # Disable button
        self.generate_btn.configure(state="disabled", text="Generating...")
        self.is_generating = True

        # Start generation in thread
        self.generation_thread = threading.Thread(target=self.generate_video, args=(prompt,))
        self.generation_thread.daemon = True
        self.generation_thread.start()

    def generate_video(self, prompt):
        """Generate video in background thread"""

        try:
            # Open console window for progress tracking
            self.root.after(0, self.open_console_window)
            self.log_to_console("Starting video generation process...")
            self.log_to_console(f"Prompt: {prompt}")
            
            # Step 1: Write script
            self.update_progress(0.1, "Writing script with AI...")
            self.log_to_console("Step 1: Writing script with Ollama AI...")
            script_data = write_script_with_ollama(prompt)
            self.log_to_console("Script written successfully!")

            # Step 2: Create voice
            self.update_progress(0.25, "Generating voice narration...")
            self.log_to_console("Step 2: Creating voice narration...")
            voice_data = create_voice_narration(script_data["script"])
            self.log_to_console(f"Voice created: {voice_data['duration']:.1f} seconds")

            # Step 3: Generate backgrounds (AI or fallback)
            self.update_progress(0.4, "Generating AI backgrounds...")
            self.log_to_console("Step 3: Generating AI backgrounds...")

            if check_gpu_available():
                # Use Stable Diffusion
                self.log_to_console("GPU detected - using Stable Diffusion for AI backgrounds")
                images = generate_ai_backgrounds(script_data["scene_descriptions"])
                if images:
                    self.log_to_console(f"Generated {len(images)} AI background images")
                    # FFmpeg approach: Pass image paths directly
                    video_clips = images_to_video_clips(
                        images, duration_per_image=voice_data["duration"] / len(images)
                    )
                else:
                    self.update_progress(0.4, "AI generation failed, using fallback...")
                    self.log_to_console("AI generation failed - using fallback backgrounds")
                    video_clips = self.create_fallback_clips(voice_data["duration"])
            else:
                self.update_progress(0.4, "No GPU - using fallback backgrounds...")
                self.log_to_console("No GPU detected - using fallback backgrounds")
                video_clips = self.create_fallback_clips(voice_data["duration"])

            # Step 4: Create captions
            self.update_progress(0.65, "Creating karaoke captions...")
            word_times = generate_word_timestamps(
                script_data["script"], voice_data["duration"]
            )
            captions = create_shorts_captions(word_times)

            # Step 5: Combine
            self.update_progress(0.85, "Combining into final video...")
            self.log_to_console("Step 5: Combining into final video...")

            output_name = script_data["title"].replace(" ", "_")[:50]
            final_video = combine_into_final_video(
                video_clips,
                voice_data["path"],
                voice_data["duration"],
                captions,
                output_name,
            )

            # Save metadata
            metadata_path = Path(Config.METADATA_DIR) / f"{output_name}.json"
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(script_data, f, indent=2)

            # Cleanup
            self.update_progress(0.95, "Cleaning up...")
            self.log_to_console("Cleaning up temporary files...")
            cleanup_temp_files()

            # Complete
            self.update_progress(1.0, "Video created successfully!")
            self.log_to_console("Video generation completed successfully!")
            self.log_to_console(f"Final video saved: {final_video}")

            # Show success message and close console
            self.root.after(0, lambda: self.on_generation_complete(final_video))
            self.root.after(0, self.close_console_window)

        except Exception as e:
            error_msg = str(e)
            self.log_to_console(f"ERROR: {error_msg}")
            self.root.after(0, lambda: self.on_generation_error(error_msg))
            self.root.after(0, self.close_console_window)

    def create_fallback_clips(self, duration):
        """Create simple colored background clips as fallback using FFmpeg"""
        import subprocess
        from pathlib import Path
        
        colors = [
            (30, 30, 40),  # Dark blue-gray
            (40, 30, 50),  # Dark purple
            (30, 40, 30),  # Dark green
            (50, 40, 30),  # Dark orange
        ]

        # Create fallback video files using FFmpeg
        temp_dir = Path("temp_files")
        temp_dir.mkdir(exist_ok=True)
        
        clips = []
        clip_duration = duration / len(colors)

        for i, color in enumerate(colors):
            video_path = temp_dir / f"fallback_clip_{i}.mp4"
            color_hex = "%02x%02x%02x" % color
            
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-t", str(clip_duration),
                "-i", f"color=c=#{color_hex}:s={Config.VIDEO_WIDTH}x{Config.VIDEO_HEIGHT}:r={Config.VIDEO_FPS}",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                str(video_path)
            ]
            
            try:
                print(f"Creating fallback clip {i+1}/{len(colors)}...")
                result = subprocess.run(cmd, text=True)
                if result.returncode == 0:
                    clips.append(str(video_path))
                    print(f"  Fallback clip {i+1} created successfully")
                else:
                    print(f"Failed to create fallback clip {i}: return code {result.returncode}")
            except Exception as e:
                print(f"Error creating fallback clip {i}: {e}")

        return clips

    def update_progress(self, value, text):
        """Update progress bar and text"""

        def update():
            self.progress_bar.set(value)
            self.progress_text.configure(text=text)
            self.status_label.configure(text=f"Status: {text}")

        self.root.after(0, update)

    def on_generation_complete(self, video_path):
        """Called when generation is complete"""

        self.is_generating = False
        self.generate_btn.configure(state="normal", text="Generate Short")

        # OPTIMIZATION: Force garbage collection and memory cleanup
        import gc
        gc.collect()
        
        # Update status with memory info
        try:
            import psutil
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            self.status_label.configure(text=f"Status: Ready - {available_gb:.1f} GB memory available")
        except ImportError:
            self.status_label.configure(text="Status: Ready")

        result = messagebox.askyesno(
            "Success", f"Video created successfully!\n\nDo you want to open it now?"
        )

        if result:
            self.open_video(Path(video_path))

    def on_generation_error(self, error):
        """Called when generation fails"""

        self.is_generating = False
        self.generate_btn.configure(state="normal", text="Generate Short")
        self.update_progress(0, "Error occurred")

        # OPTIMIZATION: Force garbage collection even on error
        import gc
        gc.collect()
        self.status_label.configure(text="Status: Error - memory cleaned")

        messagebox.showerror("Error", f"Failed to generate video:\n\n{error}")

    def open_video(self, video_path):
        """Open video file"""
        import platform

        if platform.system() == "Windows":
            os.startfile(video_path)
        elif platform.system() == "Darwin":
            os.system(f"open '{video_path}'")
        else:
            os.system(f"xdg-open '{video_path}'")

    def open_folder(self, video_path):
        """Open containing folder"""
        import platform

        folder = video_path.parent

        if platform.system() == "Windows":
            os.startfile(folder)
        elif platform.system() == "Darwin":
            os.system(f"open '{folder}'")
        else:
            os.system(f"xdg-open '{folder}'")

    def run(self):
        """Start the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = YouTubeStudioApp()
    app.run()
