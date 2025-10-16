"""
CONTROL PANELS

Base class and specific implementations for each video generation step.
Each panel provides comprehensive controls for its respective function.
"""

import sys
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

import customtkinter as ctk
from PIL import Image, ImageTk

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ui.settings_manager import SettingsManager
from settings.config import Config

# YouTube Studio color scheme
YOUTUBE_DARK = "#282828"
YOUTUBE_DARKER = "#181818"
YOUTUBE_LIGHT = "#3f3f3f"
YOUTUBE_RED = "#FF0000"
YOUTUBE_RED_HOVER = "#CC0000"
YOUTUBE_TEXT = "#FFFFFF"
YOUTUBE_TEXT_SECONDARY = "#AAAAAA"


class BaseControlPanel(ctk.CTkFrame):
    """Base class for all control panels"""
    
    def __init__(self, parent, settings_manager: SettingsManager, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.settings_manager = settings_manager
        self.configure(fg_color=YOUTUBE_DARK)
        
        # Get reference to root window for thread scheduling
        self.root = parent.winfo_toplevel()
        
        # Panel state
        self.is_running = False
        self.is_completed = False
        self.output_files = []
        
        # Create UI elements
        self.create_header()
        self.create_controls()
        self.create_status_section()
        self.create_output_section()
        self.create_buttons()
        
        # Load current settings
        self.load_settings()
    
    def create_header(self):
        """Create panel header with title and description"""
        self.header_frame = ctk.CTkFrame(self, fg_color=YOUTUBE_LIGHT)
        self.header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=self.get_title(),
            font=("Arial", 18, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.title_label.pack(pady=(10, 5))
        
        self.description_label = ctk.CTkLabel(
            self.header_frame,
            text=self.get_description(),
            font=("Arial", 12),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        self.description_label.pack(pady=(0, 10))
    
    def create_controls(self):
        """Create control widgets - override in subclasses"""
        pass
    
    def create_status_section(self):
        """Create status indicator section"""
        self.status_frame = ctk.CTkFrame(self, fg_color=YOUTUBE_LIGHT)
        self.status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Status: Ready",
            font=("Arial", 12, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.status_label.pack(pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.status_frame)
        self.progress_bar.pack(pady=(0, 10), padx=20, fill="x")
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()  # Hide initially
    
    def create_output_section(self):
        """Create output preview section"""
        self.output_frame = ctk.CTkFrame(self, fg_color=YOUTUBE_LIGHT)
        self.output_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create scrollable text widget for better text display
        self.output_text = ctk.CTkTextbox(
            self.output_frame,
            font=("Arial", 14),
            text_color=YOUTUBE_TEXT,
            fg_color=YOUTUBE_DARK,
            wrap="word",
            height=300
        )
        self.output_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.output_text.insert("1.0", "Output will appear here...")
        self.output_text.configure(state="disabled")
    
    def create_buttons(self):
        """Create action buttons"""
        self.buttons_frame = ctk.CTkFrame(self, fg_color=YOUTUBE_DARK)
        self.buttons_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        # Run button
        self.run_button = ctk.CTkButton(
            self.buttons_frame,
            text="Run Step",
            command=self.run_step,
            fg_color=YOUTUBE_RED,
            hover_color=YOUTUBE_RED_HOVER,
            font=("Arial", 12, "bold")
        )
        self.run_button.pack(side="left", padx=(10, 5), pady=10)
        
        # Save settings button
        self.save_button = ctk.CTkButton(
            self.buttons_frame,
            text="Save Settings",
            command=self.save_settings,
            fg_color=YOUTUBE_LIGHT,
            hover_color=YOUTUBE_TEXT_SECONDARY,
            font=("Arial", 12)
        )
        self.save_button.pack(side="left", padx=5, pady=10)
        
        # Reset button
        self.reset_button = ctk.CTkButton(
            self.buttons_frame,
            text="Reset",
            command=self.reset_settings,
            fg_color=YOUTUBE_LIGHT,
            hover_color=YOUTUBE_TEXT_SECONDARY,
            font=("Arial", 12)
        )
        self.reset_button.pack(side="left", padx=5, pady=10)
    
    def get_title(self) -> str:
        """Get panel title - override in subclasses"""
        return "Base Panel"
    
    def get_description(self) -> str:
        """Get panel description - override in subclasses"""
        return "Base control panel"
    
    def load_settings(self):
        """Load settings into widgets - override in subclasses"""
        pass
    
    def save_settings(self):
        """Save current widget values to settings manager"""
        try:
            # Collect widget values (implemented in subclasses)
            self.collect_widget_values()
            
            # Save to config.py file
            if self.settings_manager.save_to_file():
                self.update_output("✓ Settings saved to config.py")
            else:
                self.update_output("✗ Failed to save settings to config.py")
                
        except Exception as e:
            self.update_output(f"Error saving settings: {str(e)}")
    
    def collect_widget_values(self):
        """Collect widget values - override in subclasses"""
        pass
    
    def reset_settings(self):
        """Reset settings to defaults"""
        self.settings_manager.reset_to_defaults()
        self.load_settings()
    
    def run_step(self):
        """Run the step - override in subclasses"""
        self.set_status("Running...", True)
        self.run_button.configure(state="disabled")
    
    def set_status(self, status: str, running: bool = False, completed: bool = False):
        """Update status display"""
        self.is_running = running
        self.is_completed = completed
        
        if running:
            self.status_label.configure(text=f"Status: {status}")
            self.progress_bar.pack(pady=(0, 10), padx=20, fill="x")
            self.progress_bar.set(0.5)  # Indeterminate progress
        elif completed:
            self.status_label.configure(text=f"Status: Completed")
            self.progress_bar.pack_forget()
            self.run_button.configure(text="Re-run Step", state="normal")
        else:
            self.status_label.configure(text=f"Status: {status}")
            self.progress_bar.pack_forget()
            self.run_button.configure(text="Run Step", state="normal")
    
    def update_output(self, output_info: str):
        """Update output section with results"""
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", output_info)
        self.output_text.configure(state="disabled")
    
    def run_in_thread(self, target_func, *args, **kwargs):
        """Run a function in a separate thread to prevent UI freezing"""
        def thread_wrapper():
            try:
                result = target_func(*args, **kwargs)
                # Schedule UI update on main thread using a proper closure
                def handle_result():
                    self.handle_thread_result(result)
                self.root.after(0, handle_result)
            except Exception as e:
                # Schedule error handling on main thread using a proper closure
                def handle_error(error=e):
                    self.handle_thread_error(error)
                self.root.after(0, handle_error)
        
        thread = threading.Thread(target=thread_wrapper, daemon=True)
        thread.start()
    
    def handle_thread_result(self, result):
        """Handle successful thread completion - override in subclasses"""
        pass
    
    def handle_thread_error(self, error):
        """Handle thread error - override in subclasses"""
        self.set_status(f"Error: {str(error)}", False)
        self.update_output(f"Error during operation:\n{str(error)}\n\nTry again or check your settings.")
        self.run_button.configure(state="normal")
        
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Thread error in {self.__class__.__name__}: {str(error)}")


class ScriptGeneratorPanel(BaseControlPanel):
    """Control panel for Step 1: Script Generation"""
    
    def get_title(self) -> str:
        return "Script Generator"
    
    def get_description(self) -> str:
        return "Generate AI-powered YouTube Shorts scripts using Grok/Groq with template fallback"
    
    def create_controls(self):
        """Create script generation controls"""
        super().create_controls()
        
        # Main controls frame
        self.controls_frame = ctk.CTkScrollableFrame(self, fg_color=YOUTUBE_LIGHT)
        self.controls_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Topic input
        self.topic_label = ctk.CTkLabel(
            self.controls_frame,
            text="Chat with Grok - What should this video be about?",
            font=("Arial", 12, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.topic_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.topic_entry = ctk.CTkTextbox(
            self.controls_frame,
            height=60,
            font=("Arial", 12)
        )
        self.topic_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.topic_entry.insert("1.0", "Tell me something fascinating about space exploration")
        
        # Add help text below the textbox
        self.help_label = ctk.CTkLabel(
            self.controls_frame,
            text="💡 Examples: 'Tell me about quantum physics', 'Explain how AI works', 'Share cool space facts', 'What's interesting about psychology?'",
            font=("Arial", 10),
            text_color=YOUTUBE_TEXT,
            wraplength=600
        )
        self.help_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # AI Model selection
        self.model_frame = ctk.CTkFrame(self.controls_frame, fg_color=YOUTUBE_DARK)
        self.model_frame.pack(fill="x", padx=10, pady=5)
        
        self.model_label = ctk.CTkLabel(
            self.model_frame,
            text="AI Model:",
            font=("Arial", 12, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.model_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.model_var = ctk.StringVar()
        self.model_dropdown = ctk.CTkOptionMenu(
            self.model_frame,
            values=self.settings_manager.get_available_models(),
            variable=self.model_var,
            fg_color=YOUTUBE_LIGHT,
            button_color=YOUTUBE_RED,
            button_hover_color=YOUTUBE_RED_HOVER
        )
        self.model_dropdown.pack(fill="x", padx=10, pady=(0, 5))
        
        # Grok Status Indicator
        self.grok_status_frame = ctk.CTkFrame(self.model_frame, fg_color="transparent")
        self.grok_status_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.grok_status_label = ctk.CTkLabel(
            self.grok_status_frame,
            text="Grok Status:",
            font=("Arial", 10, "bold"),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        self.grok_status_label.pack(side="left")
        
        self.grok_status_indicator = ctk.CTkLabel(
            self.grok_status_frame,
            text="Checking...",
            font=("Arial", 10),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        self.grok_status_indicator.pack(side="right")
        
        # Grok Config Button
        self.grok_config_btn = ctk.CTkButton(
            self.model_frame,
            text="🤖 Configure Grok",
            command=self.show_grok_config,
            fg_color="transparent",
            hover_color=YOUTUBE_RED_HOVER,
            text_color=YOUTUBE_TEXT_SECONDARY,
            font=("Arial", 10),
            height=25,
            width=120
        )
        self.grok_config_btn.pack(anchor="e", padx=10, pady=(0, 10))
        
        # AI Settings
        self.ai_settings_frame = ctk.CTkFrame(self.controls_frame, fg_color=YOUTUBE_DARK)
        self.ai_settings_frame.pack(fill="x", padx=10, pady=5)
        
        self.ai_settings_label = ctk.CTkLabel(
            self.ai_settings_frame,
            text="AI Generation Settings:",
            font=("Arial", 12, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.ai_settings_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Temperature
        self.temp_label = ctk.CTkLabel(
            self.ai_settings_frame,
            text="Temperature (creativity):",
            font=("Arial", 11),
            text_color=YOUTUBE_TEXT
        )
        self.temp_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.temp_var = ctk.DoubleVar()
        self.temp_slider = ctk.CTkSlider(
            self.ai_settings_frame,
            from_=0.0,
            to=2.0,
            number_of_steps=20,
            variable=self.temp_var
        )
        self.temp_slider.pack(fill="x", padx=10, pady=(0, 5))
        
        self.temp_value_label = ctk.CTkLabel(
            self.ai_settings_frame,
            text="0.7",
            font=("Arial", 10),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        self.temp_value_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Script Settings
        self.script_settings_frame = ctk.CTkFrame(self.controls_frame, fg_color=YOUTUBE_DARK)
        self.script_settings_frame.pack(fill="x", padx=10, pady=5)
        
        self.script_settings_label = ctk.CTkLabel(
            self.script_settings_frame,
            text="Script Settings:",
            font=("Arial", 12, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.script_settings_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Target words
        self.words_label = ctk.CTkLabel(
            self.script_settings_frame,
            text="Target Words:",
            font=("Arial", 11),
            text_color=YOUTUBE_TEXT
        )
        self.words_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.words_var = ctk.IntVar()
        self.words_entry = ctk.CTkEntry(
            self.script_settings_frame,
            textvariable=self.words_var,
            width=100
        )
        self.words_entry.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Bind slider updates
        self.temp_slider.configure(command=self.update_temp_label)
    
    def update_temp_label(self, value):
        """Update temperature label when slider changes"""
        self.temp_value_label.configure(text=f"{float(value):.1f}")
    
    def load_settings(self):
        """Load current settings into widgets"""
        # Template-based fallback doesn't need model/temperature settings
        self.model_var.set("Template-based")
        self.temp_var.set(0.8)
        self.words_var.set(self.settings_manager.get_setting("SCRIPT_TARGET_WORDS", 110))
        
        # Update Grok status
        self.update_grok_status()
    
    def collect_widget_values(self):
        """Collect widget values and save to settings manager"""
        # Template-based fallback doesn't need model/temperature settings
        # self.settings_manager.update_setting("OLLAMA_MODEL", self.model_var.get())
        # self.settings_manager.update_setting("OLLAMA_TEMPERATURE", self.temp_var.get())
        self.settings_manager.update_setting("SCRIPT_TARGET_WORDS", self.words_var.get())
    
    def run_step(self):
        """Run script generation"""
        super().run_step()
        
        # Get topic from entry
        topic = self.topic_entry.get("1.0", "end-1c").strip()
        if not topic:
            self.set_status("Error: Please enter a topic", False)
            return
        
        # Update UI to show we're starting
        self.update_output("Generating script with AI...\n\nThis may take 10-30 seconds.\nPlease wait...")
        
        # Run script generation in a separate thread
        self.run_in_thread(self._generate_script_thread, topic)
    
    def _generate_script_thread(self, topic):
        """Generate script in a separate thread"""
        try:
            # Import step function
            from steps.step1_write_script import write_script_with_ollama
            
            # Run script generation
            script_data = write_script_with_ollama(topic)
            return script_data
            
        except Exception as e:
            raise e
    
    def handle_thread_result(self, script_data):
        """Handle successful script generation"""
        if script_data:
            # Display results
            output_text = f"✓ Script Generated Successfully!\n\n"
            output_text += f"Title: {script_data.get('title', 'N/A')}\n\n"
            
            # ========================================
            # NARRATOR SCRIPT - What will be spoken
            # ========================================
            output_text += "="*60 + "\n"
            output_text += "NARRATOR SCRIPT (What the narrator will say):\n"
            output_text += "="*60 + "\n\n"
            
            # Format script with proper line breaks
            script_text = script_data.get('script', 'N/A')
            # Split script into sentences and wrap at reasonable length
            sentences = script_text.split('. ')
            wrapped_script = ""
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    # Add period back if it's not the last sentence
                    if i < len(sentences) - 1 and not sentence.endswith('.'):
                        sentence += '.'
                    # Wrap long sentences
                    if len(sentence) > 80:
                        words = sentence.split()
                        line = ""
                        for word in words:
                            if len(line + word) > 80:
                                wrapped_script += line.strip() + "\n"
                                line = word + " "
                            else:
                                line += word + " "
                        wrapped_script += line.strip() + "\n"
                    else:
                        wrapped_script += sentence + "\n"
            
            output_text += wrapped_script + "\n"
            output_text += "="*60 + "\n\n"
            
            # ========================================
            # SCENE DESCRIPTIONS - Visuals
            # ========================================
            output_text += "Scene Descriptions:\n"
            for i, desc in enumerate(script_data.get('scene_descriptions', []), 1):
                output_text += f"{i}. {desc}\n"
            
            self.update_output(output_text)
            self.set_status("Completed", False, True)
            
            # Store script data for other steps
            self.script_data = script_data
            
            # Notify parent of completion
            if hasattr(self.app, 'update_step_completion'):
                self.app.update_step_completion('script', True)
        else:
            self.set_status("Error: Failed to generate script", False)
            self.update_output("Failed to generate script. Please check:\n• AI provider is configured\n• Topic is valid\n• Try again")
        
        self.run_button.configure(state="normal")
    
    def show_grok_config(self):
        """Show Grok configuration dialog"""
        if hasattr(self.app, 'show_grok_config'):
            self.app.show_grok_config()
        else:
            messagebox.showinfo("Info", "Grok configuration panel not available")
    
    def update_grok_status(self):
        """Update Grok status indicator"""
        try:
            from settings.config import Config
            
            if Config.AI_PROVIDER.lower() == "grok":
                if Config.GROK_API_KEY and len(Config.GROK_API_KEY.strip()) > 0:
                    self.grok_status_indicator.configure(
                        text="✓ Grok Ready",
                        text_color="#00FF00"
                    )
                else:
                    self.grok_status_indicator.configure(
                        text="⚠ API Key Missing",
                        text_color="#FFFF00"
                    )
            else:
                self.grok_status_indicator.configure(
                    text=f"→ {Config.AI_PROVIDER.upper()}",
                    text_color="#AAAAAA"
                )
        except Exception as e:
            self.grok_status_indicator.configure(
                text="❌ Error",
                text_color="#FF0000"
            )


class VoiceSynthesisPanel(BaseControlPanel):
    """Control panel for Step 2: Voice Synthesis"""
    
    def get_title(self) -> str:
        return "Voice Synthesis"
    
    def get_description(self) -> str:
        return "Generate high-quality voice narration using Piper TTS, Edge TTS, or gTTS"
    
    def create_controls(self):
        """Create voice synthesis controls"""
        super().create_controls()
        
        # Main controls frame
        self.controls_frame = ctk.CTkScrollableFrame(self, fg_color=YOUTUBE_LIGHT)
        self.controls_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # TTS Engine selection
        self.engine_frame = ctk.CTkFrame(self.controls_frame, fg_color=YOUTUBE_DARK)
        self.engine_frame.pack(fill="x", padx=10, pady=5)
        
        self.engine_label = ctk.CTkLabel(
            self.engine_frame,
            text="TTS Engine: (auto-detected from voice)",
            font=("Arial", 12, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.engine_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.engine_var = ctk.StringVar()
        self.engine_dropdown = ctk.CTkOptionMenu(
            self.engine_frame,
            values=["piper", "edge", "gtts"],
            variable=self.engine_var,
            fg_color=YOUTUBE_LIGHT,
            button_color=YOUTUBE_RED,
            button_hover_color=YOUTUBE_RED_HOVER,
            command=self.on_engine_changed
        )
        self.engine_dropdown.pack(fill="x", padx=10, pady=(0, 10))
        
        # Piper TTS Configuration
        self.piper_frame = ctk.CTkFrame(self.controls_frame, fg_color=YOUTUBE_DARK)
        self.piper_frame.pack(fill="x", padx=10, pady=5)
        
        self.piper_label = ctk.CTkLabel(
            self.piper_frame,
            text="Piper TTS Configuration:",
            font=("Arial", 12, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.piper_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.piper_model_label = ctk.CTkLabel(
            self.piper_frame,
            text="Model: en-us-amy-medium (Natural Female Voice)",
            font=("Arial", 10),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        self.piper_model_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.piper_status_label = ctk.CTkLabel(
            self.piper_frame,
            text="Status: Checking...",
            font=("Arial", 10),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        self.piper_status_label.pack(anchor="w", padx=10, pady=(0, 10))

        # Voice selection (for Edge TTS)
        self.voice_frame = ctk.CTkFrame(self.controls_frame, fg_color=YOUTUBE_DARK)
        self.voice_frame.pack(fill="x", padx=10, pady=5)
        
        self.voice_label = ctk.CTkLabel(
            self.voice_frame,
            text="Voice:",
            font=("Arial", 12, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.voice_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.voice_var = ctk.StringVar()
        self.voice_dropdown = ctk.CTkOptionMenu(
            self.voice_frame,
            values=self.settings_manager.get_available_voices(),
            variable=self.voice_var,
            fg_color=YOUTUBE_LIGHT,
            button_color=YOUTUBE_RED,
            button_hover_color=YOUTUBE_RED_HOVER,
            command=self.on_voice_changed  # Auto-detect TTS engine when voice changes
        )
        self.voice_dropdown.pack(fill="x", padx=10, pady=(0, 10))
        
        # Language selection (for gTTS)
        self.language_frame = ctk.CTkFrame(self.controls_frame, fg_color=YOUTUBE_DARK)
        self.language_frame.pack(fill="x", padx=10, pady=5)
        
        self.language_label = ctk.CTkLabel(
            self.language_frame,
            text="Language (gTTS):",
            font=("Arial", 12, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.language_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.language_var = ctk.StringVar()
        self.language_entry = ctk.CTkEntry(
            self.language_frame,
            textvariable=self.language_var,
            width=100
        )
        self.language_entry.pack(anchor="w", padx=10, pady=(0, 10))
    
    def on_voice_changed(self, selected_voice):
        """
        Automatically detect and set the correct TTS engine based on voice selection.
        
        Edge TTS voices follow pattern: en-US-GuyNeural, es-ES-AlvaroNeural, etc.
        gTTS uses simple language codes: en, es, fr, etc.
        """
        # Check if the selected voice looks like an Edge TTS voice
        # Edge voices have format: language-REGION-NameNeural (e.g., en-US-GuyNeural)
        if "-" in selected_voice and "Neural" in selected_voice:
            # This is an Edge TTS voice
            self.engine_var.set("edge")
            print(f"Auto-detected: Edge TTS voice '{selected_voice}'")
        elif len(selected_voice) <= 5 and "-" not in selected_voice:
            # This looks like a language code for gTTS (e.g., "en", "es", "fr")
            self.engine_var.set("gtts")
            print(f"Auto-detected: gTTS language code '{selected_voice}'")
        else:
            # Default to edge for anything else
            self.engine_var.set("edge")
    
    def load_settings(self):
        """Load current settings into widgets"""
        # Load TTS provider from config
        tts_provider = getattr(Config, 'TTS_PROVIDER', 'piper')
        self.engine_var.set(tts_provider)
        
        self.voice_var.set(self.settings_manager.get_setting("EDGE_TTS_VOICE", "en-US-AriaNeural"))
        self.language_var.set(self.settings_manager.get_setting("VOICE_LANGUAGE", "en"))
        
        # Update UI based on current engine
        self.on_engine_changed(tts_provider)
        self.update_piper_status()
    
    def collect_widget_values(self):
        """Collect widget values and save to settings manager"""
        self.settings_manager.update_setting("TTS_ENGINE", self.engine_var.get())
        self.settings_manager.update_setting("EDGE_TTS_VOICE", self.voice_var.get())
        self.settings_manager.update_setting("VOICE_LANGUAGE", self.language_var.get())
        
        # Update TTS provider in config
        Config.TTS_PROVIDER = self.engine_var.get()
    
    def on_engine_changed(self, selected_engine):
        """Handle TTS engine selection change"""
        if selected_engine == "piper":
            self.piper_frame.pack(fill="x", padx=10, pady=5)
            self.voice_frame.pack_forget()  # Hide Edge TTS voice selection
            self.language_frame.pack_forget()  # Hide language selection
        elif selected_engine == "edge":
            self.piper_frame.pack_forget()  # Hide Piper config
            self.voice_frame.pack(fill="x", padx=10, pady=5)  # Show Edge TTS
            self.language_frame.pack_forget()  # Hide language selection
        elif selected_engine == "gtts":
            self.piper_frame.pack_forget()  # Hide Piper config
            self.voice_frame.pack_forget()  # Hide Edge TTS
            self.language_frame.pack(fill="x", padx=10, pady=5)  # Show language selection
    
    def update_piper_status(self):
        """Update Piper TTS status indicator"""
        try:
            from pathlib import Path
            model_path = getattr(Config, 'PIPER_MODEL_PATH', None)
            config_path = getattr(Config, 'PIPER_CONFIG_PATH', None)
            
            if model_path and config_path and Path(model_path).exists() and Path(config_path).exists():
                self.piper_status_label.configure(
                    text="Status: Ready (High Quality Neural Voice)",
                    text_color="#00FF00"
                )
            else:
                self.piper_status_label.configure(
                    text="Status: Model files not found",
                    text_color="#FF0000"
                )
        except Exception as e:
            self.piper_status_label.configure(
                text=f"Status: Error - {str(e)[:30]}...",
                text_color="#FF0000"
            )
    
    def run_step(self):
        """Run voice synthesis"""
        super().run_step()
        
        # Check if script data is available
        script_panel = None
        if hasattr(self.app, 'panels') and hasattr(self.app.panels, 'get'):
            script_panel = self.app.panels.get('script')
        
        if not script_panel or not hasattr(script_panel, 'script_data'):
            self.set_status("Error: Please generate a script first", False)
            self.update_output("No script data available. Please run the Script Generator step first.")
            return
        
        # Get script text
        script_text = script_panel.script_data.get('script', '')
        if not script_text:
            self.set_status("Error: No script text found", False)
            self.update_output("Script data does not contain text. Please regenerate the script.")
            return
        
        # Update UI to show we're starting
        self.update_output("Generating voice narration...\n\nThis may take 10-30 seconds.\nPlease wait...")
        
        # Run voice generation in a separate thread
        self.run_in_thread(self._generate_voice_thread, script_text)
    
    def _generate_voice_thread(self, script_text):
        """Generate voice in a separate thread"""
        try:
            # Import step function
            from steps.step2_create_voice import create_voice_narration
            
            # Get the selected voice from the UI dropdown
            selected_voice = self.voice_var.get()
            
            # Run voice generation with the selected voice
            voice_result = create_voice_narration(script_text, voice_name=selected_voice)
            return voice_result
            
        except Exception as e:
            raise e
    
    def handle_thread_result(self, voice_result):
        """Handle successful voice generation"""
        if voice_result and voice_result.get('path'):
            # Display results
            output_text = f"✓ Voice Generated Successfully!\n\n"
            output_text += f"Audio file: {voice_result['path']}\n"
            output_text += f"Duration: {voice_result.get('duration', 'N/A'):.1f} seconds\n"
            output_text += f"Engine: {self.engine_var.get()}\n"
            output_text += f"Voice: {self.voice_var.get()}"
            
            self.update_output(output_text)
            self.set_status("Completed", False, True)
            
            # Store voice data for other steps
            self.voice_data = voice_result
            
            # Notify parent of completion
            if hasattr(self.app, 'update_step_completion'):
                self.app.update_step_completion('voice', True)
        else:
            self.set_status("Error: Failed to generate voice", False)
            self.update_output("Failed to generate voice. Please check:\n• TTS settings\n• Internet connection (for gTTS)\n• Try again")
        
        self.run_button.configure(state="normal")


class BackgroundGeneratorPanel(BaseControlPanel):
    """Control panel for Step 3: Background Generation"""
    
    def get_title(self) -> str:
        return "Background Generator"
    
    def get_description(self) -> str:
        return "Generate AI-powered backgrounds using Stable Diffusion"
    
    def create_controls(self):
        """Create background generation controls"""
        super().create_controls()
        
        # Main controls frame
        self.controls_frame = ctk.CTkScrollableFrame(self, fg_color=YOUTUBE_LIGHT)
        self.controls_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Method selection
        self.method_frame = ctk.CTkFrame(self.controls_frame, fg_color=YOUTUBE_DARK)
        self.method_frame.pack(fill="x", padx=10, pady=5)
        
        self.method_label = ctk.CTkLabel(
            self.method_frame,
            text="Generation Method:",
            font=("Arial", 12, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.method_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.method_var = ctk.StringVar()
        self.method_dropdown = ctk.CTkOptionMenu(
            self.method_frame,
            values=["webui", "diffusers"],
            variable=self.method_var,
            fg_color=YOUTUBE_LIGHT,
            button_color=YOUTUBE_RED,
            button_hover_color=YOUTUBE_RED_HOVER
        )
        self.method_dropdown.pack(fill="x", padx=10, pady=(0, 10))
        
        # Quality preset
        self.preset_frame = ctk.CTkFrame(self.controls_frame, fg_color=YOUTUBE_DARK)
        self.preset_frame.pack(fill="x", padx=10, pady=5)
        
        self.preset_label = ctk.CTkLabel(
            self.preset_frame,
            text="Quality Preset:",
            font=("Arial", 12, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.preset_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.preset_var = ctk.StringVar()
        self.preset_dropdown = ctk.CTkOptionMenu(
            self.preset_frame,
            values=self.settings_manager.get_available_quality_presets(),
            variable=self.preset_var,
            fg_color=YOUTUBE_LIGHT,
            button_color=YOUTUBE_RED,
            button_hover_color=YOUTUBE_RED_HOVER
        )
        self.preset_dropdown.pack(fill="x", padx=10, pady=(0, 10))
        
        # Generation settings
        self.gen_settings_frame = ctk.CTkFrame(self.controls_frame, fg_color=YOUTUBE_DARK)
        self.gen_settings_frame.pack(fill="x", padx=10, pady=5)
        
        self.gen_settings_label = ctk.CTkLabel(
            self.gen_settings_frame,
            text="Generation Settings:",
            font=("Arial", 12, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.gen_settings_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Inference steps
        self.steps_label = ctk.CTkLabel(
            self.gen_settings_frame,
            text="Inference Steps:",
            font=("Arial", 11),
            text_color=YOUTUBE_TEXT
        )
        self.steps_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        # Slider container with labels
        self.slider_container = ctk.CTkFrame(self.gen_settings_frame, fg_color="transparent")
        self.slider_container.pack(fill="x", padx=10, pady=(0, 5))
        
        # Left label (Faster)
        self.faster_label = ctk.CTkLabel(
            self.slider_container,
            text="Faster",
            font=("Arial", 10, "bold"),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        self.faster_label.pack(side="left", padx=(0, 10))
        
        # Slider
        self.steps_var = ctk.IntVar()
        self.steps_slider = ctk.CTkSlider(
            self.slider_container,
            from_=1,
            to=50,
            number_of_steps=49,
            variable=self.steps_var
        )
        self.steps_slider.pack(side="left", fill="x", expand=True, padx=5)
        
        # Right label (Better Quality)
        self.quality_label = ctk.CTkLabel(
            self.slider_container,
            text="Better Quality",
            font=("Arial", 10, "bold"),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        self.quality_label.pack(side="right", padx=(10, 0))
        
        self.steps_value_label = ctk.CTkLabel(
            self.gen_settings_frame,
            text="12",
            font=("Arial", 10),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        self.steps_value_label.pack(anchor="w", padx=10, pady=(0, 5))

        # Explanation for inference steps
        self.steps_explanation = ctk.CTkLabel(
            self.gen_settings_frame,
            text="Higher = better quality, slower generation. Lower = faster generation, lower quality. Recommended: 8-12 for speed, 15-20 for quality.",
            font=("Arial", 12, "bold"),
            text_color=YOUTUBE_TEXT,
            wraplength=500
        )
        self.steps_explanation.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Max scenes
        self.scenes_label = ctk.CTkLabel(
            self.gen_settings_frame,
            text="Max Scenes:",
            font=("Arial", 11),
            text_color=YOUTUBE_TEXT
        )
        self.scenes_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.scenes_var = ctk.IntVar()
        self.scenes_entry = ctk.CTkEntry(
            self.gen_settings_frame,
            textvariable=self.scenes_var,
            width=100
        )
        self.scenes_entry.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Bind slider updates
        self.steps_slider.configure(command=self.update_steps_label)
    
    def update_steps_label(self, value):
        """Update steps label when slider changes"""
        self.steps_value_label.configure(text=str(int(value)))
    
    def load_settings(self):
        """Load current settings into widgets"""
        self.method_var.set(self.settings_manager.get_setting("SD_METHOD", "webui"))
        self.preset_var.set(self.settings_manager.get_setting("CURRENT_QUALITY_PRESET", "balanced"))
        self.steps_var.set(self.settings_manager.get_setting("SD_INFERENCE_STEPS", 12))
        self.scenes_var.set(self.settings_manager.get_setting("SD_MAX_SCENES", 3))
    
    def collect_widget_values(self):
        """Collect widget values and save to settings manager"""
        self.settings_manager.update_setting("SD_METHOD", self.method_var.get())
        self.settings_manager.update_setting("CURRENT_QUALITY_PRESET", self.preset_var.get())
        self.settings_manager.update_setting("SD_INFERENCE_STEPS", self.steps_var.get())
        self.settings_manager.update_setting("SD_MAX_SCENES", self.scenes_var.get())
    
    def run_step(self):
        """Run background generation"""
        super().run_step()
        
        # Check if script data is available
        script_panel = None
        if hasattr(self.app, 'panels') and hasattr(self.app.panels, 'get'):
            script_panel = self.app.panels.get('script')
        
        if not script_panel or not hasattr(script_panel, 'script_data'):
            self.set_status("Error: Please generate a script first", False)
            self.update_output("No script data available. Please run the Script Generator step first.")
            return
        
        # Get scene descriptions from script
        scene_descriptions = script_panel.script_data.get('scene_descriptions', [])
        if not scene_descriptions:
            self.set_status("Error: No scene descriptions found", False)
            self.update_output("Script data does not contain scene descriptions. Please regenerate the script.")
            return
        
        # Update UI to show we're starting
        self.update_output("Generating AI backgrounds with Stable Diffusion...\n\nThis may take 2-5 minutes.\nPlease wait...")
        
        # Run background generation in a separate thread
        self.run_in_thread(self._generate_backgrounds_thread, scene_descriptions)
    
    def _generate_backgrounds_thread(self, scene_descriptions):
        """Generate backgrounds in a separate thread with AI enhancements"""
        try:
            # Import step functions
            from steps.step3_generate_backgrounds import generate_ai_backgrounds_enhanced, images_to_video_clips
            
            # Get full script data for AI enhancements
            script_data = None
            if hasattr(self.app, 'panels') and hasattr(self.app.panels, 'get'):
                script_panel = self.app.panels.get('script')
                if script_panel and hasattr(script_panel, 'script_data'):
                    script_data = script_panel.script_data
                    print("🤖 AI Enhancement: Using full script context for intelligent generation")
            
            # Run enhanced background generation
            image_paths = generate_ai_backgrounds_enhanced(
                scene_descriptions, 
                script_data=script_data,
                duration_per_scene=10.0
            )
            
            if image_paths:
                # Convert images to video clips
                video_clips = images_to_video_clips(image_paths, duration_per_image=10.0)
                return {
                    'images': image_paths,
                    'video_clips': video_clips,
                    'ai_enhanced': True
                }
            else:
                return None
                
        except Exception as e:
            raise e
    
    def handle_thread_result(self, background_data):
        """Handle successful background generation"""
        if background_data and background_data.get('images') and background_data.get('video_clips'):
            # Display results
            output_text = f"✓ Backgrounds Generated Successfully!\n\n"
            output_text += f"Generated {len(background_data['images'])} AI images:\n"
            for i, path in enumerate(background_data['images'], 1):
                output_text += f"  {i}. {Path(path).name}\n"
            output_text += f"\nCreated {len(background_data['video_clips'])} video clips with Ken Burns effect:\n"
            for i, path in enumerate(background_data['video_clips'], 1):
                output_text += f"  {i}. {Path(path).name}\n"
            output_text += f"\nMethod: {self.settings_manager.get_setting('SD_METHOD', 'webui')}\n"
            output_text += f"Quality: {self.settings_manager.get_setting('CURRENT_QUALITY_PRESET', 'balanced')}\n"
            
            # Show AI enhancement status
            if background_data.get('ai_enhanced', False):
                output_text += f"\n🤖 AI Enhancements:\n"
                output_text += f"  ✓ Prompt Optimization: Enabled\n"
                output_text += f"  ✓ ControlNet Guidance: Enabled\n"
                output_text += f"  ✓ Quality Analysis: Enabled\n"
                output_text += f"  ✓ Context-Aware Generation: Enabled"
            
            self.update_output(output_text)
            self.set_status("Completed", False, True)
            
            # Store background data for other steps
            self.background_data = background_data
            
            # Notify parent of completion
            if hasattr(self.app, 'update_step_completion'):
                self.app.update_step_completion('background', True)
        else:
            self.set_status("Error: Failed to generate backgrounds", False)
            self.update_output("Failed to generate backgrounds. Please check:\n• GPU is available\n• Stable Diffusion is running\n• Try again")
        
        self.run_button.configure(state="normal")


class CaptionCreationPanel(BaseControlPanel):
    """Control panel for Step 4: Caption Creation"""
    
    def get_title(self) -> str:
        return "Caption Creation"
    
    def get_description(self) -> str:
        return "Create karaoke-style captions optimized for mobile viewing"
    
    def create_controls(self):
        """Create caption creation controls"""
        super().create_controls()
        
        # Main controls frame
        self.controls_frame = ctk.CTkScrollableFrame(self, fg_color=YOUTUBE_LIGHT)
        self.controls_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Caption settings
        self.caption_frame = ctk.CTkFrame(self.controls_frame, fg_color=YOUTUBE_DARK)
        self.caption_frame.pack(fill="x", padx=10, pady=5)
        
        self.caption_label = ctk.CTkLabel(
            self.caption_frame,
            text="Caption Settings:",
            font=("Arial", 12, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.caption_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Font size
        self.font_size_label = ctk.CTkLabel(
            self.caption_frame,
            text="Font Size:",
            font=("Arial", 11),
            text_color=YOUTUBE_TEXT
        )
        self.font_size_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.font_size_var = ctk.IntVar()
        self.font_size_slider = ctk.CTkSlider(
            self.caption_frame,
            from_=12,
            to=100,
            number_of_steps=88,
            variable=self.font_size_var
        )
        self.font_size_slider.pack(fill="x", padx=10, pady=(0, 5))
        
        self.font_size_value_label = ctk.CTkLabel(
            self.caption_frame,
            text="52",
            font=("Arial", 10),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        self.font_size_value_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Words per caption
        self.words_per_label = ctk.CTkLabel(
            self.caption_frame,
            text="Words Per Caption:",
            font=("Arial", 11),
            text_color=YOUTUBE_TEXT
        )
        self.words_per_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.words_per_var = ctk.IntVar()
        self.words_per_slider = ctk.CTkSlider(
            self.caption_frame,
            from_=1,
            to=10,
            number_of_steps=9,
            variable=self.words_per_var
        )
        self.words_per_slider.pack(fill="x", padx=10, pady=(0, 5))
        
        self.words_per_value_label = ctk.CTkLabel(
            self.caption_frame,
            text="3",
            font=("Arial", 10),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        self.words_per_value_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Position
        self.position_label = ctk.CTkLabel(
            self.caption_frame,
            text="Position:",
            font=("Arial", 11),
            text_color=YOUTUBE_TEXT
        )
        self.position_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.position_var = ctk.StringVar()
        self.position_dropdown = ctk.CTkOptionMenu(
            self.caption_frame,
            values=self.settings_manager.get_available_caption_positions(),
            variable=self.position_var,
            fg_color=YOUTUBE_LIGHT,
            button_color=YOUTUBE_RED,
            button_hover_color=YOUTUBE_RED_HOVER
        )
        self.position_dropdown.pack(fill="x", padx=10, pady=(0, 10))
        
        # Bind slider updates
        self.font_size_slider.configure(command=self.update_font_size_label)
        self.words_per_slider.configure(command=self.update_words_per_label)
    
    def update_font_size_label(self, value):
        """Update font size label when slider changes"""
        self.font_size_value_label.configure(text=str(int(value)))
    
    def update_words_per_label(self, value):
        """Update words per caption label when slider changes"""
        self.words_per_value_label.configure(text=str(int(value)))
    
    def load_settings(self):
        """Load current settings into widgets"""
        self.font_size_var.set(self.settings_manager.get_setting("CAPTION_FONT_SIZE", 52))
        self.words_per_var.set(self.settings_manager.get_setting("WORDS_PER_CAPTION", 3))
        self.position_var.set(self.settings_manager.get_setting("CAPTION_POSITION", "center"))
    
    def collect_widget_values(self):
        """Collect widget values and save to settings manager"""
        self.settings_manager.update_setting("CAPTION_FONT_SIZE", self.font_size_var.get())
        self.settings_manager.update_setting("WORDS_PER_CAPTION", self.words_per_var.get())
        self.settings_manager.update_setting("CAPTION_POSITION", self.position_var.get())
    
    def run_step(self):
        """Run caption creation"""
        super().run_step()
        
        try:
            # Check if script and voice data are available
            script_panel = None
            voice_panel = None
            
            if hasattr(self.app, 'panels'):
                script_panel = self.app.panels.get('script')
                voice_panel = self.app.panels.get('voice')
            
            if not script_panel or not hasattr(script_panel, 'script_data'):
                self.set_status("Error: Please generate a script first", False)
                self.update_output("No script data available. Please run the Script Generator step first.")
                return
            
            if not voice_panel or not hasattr(voice_panel, 'voice_data'):
                self.set_status("Error: Please generate voice first", False)
                self.update_output("No voice data available. Please run the Voice Synthesis step first.")
                return
            
            # Import step functions
            from steps.step1_write_script import generate_word_timestamps
            from steps.step4_add_captions import create_shorts_captions
            
            # Get script text and audio duration
            script_text = script_panel.script_data.get('script', '')
            audio_duration = voice_panel.voice_data.get('duration', 30.0)
            
            if not script_text:
                self.set_status("Error: No script text found", False)
                self.update_output("Script data does not contain text. Please regenerate the script.")
                return
            
            # Run caption creation
            self.update_output("Generating word timestamps and captions...")
            word_timestamps = generate_word_timestamps(script_text, audio_duration)
            caption_file = create_shorts_captions(word_timestamps)
            
            if caption_file and Path(caption_file).exists():
                # Display results
                output_text = f"✓ Captions Generated Successfully!\n\n"
                output_text += f"Caption file: {Path(caption_file).name}\n"
                output_text += f"Format: ASS (Advanced SubStation Alpha)\n"
                output_text += f"Words processed: {len(word_timestamps)}\n"
                output_text += f"Audio duration: {audio_duration:.1f} seconds\n"
                output_text += f"Font size: {self.settings_manager.get_setting('CAPTION_FONT_SIZE', 52)}\n"
                output_text += f"Words per caption: {self.settings_manager.get_setting('WORDS_PER_CAPTION', 3)}\n"
                output_text += f"Position: {self.settings_manager.get_setting('CAPTION_POSITION', 'center')}"
                
                self.update_output(output_text)
                self.set_status("Completed", False, True)
                
                # Store caption data for other steps
                self.caption_data = {
                    'file': caption_file,
                    'word_timestamps': word_timestamps
                }
                
                # Notify parent of completion
                if hasattr(self.app, 'update_step_completion'):
                    self.app.update_step_completion('caption', True)
            else:
                self.set_status("Error: Failed to generate captions", False)
                self.update_output("Failed to generate captions. Please check the settings and try again.")
                
        except Exception as e:
            self.set_status(f"Error: {str(e)}", False)
            self.update_output(f"Error during caption creation:\n{str(e)}")
        
        finally:
            self.run_button.configure(state="normal")


class FinalCompositionPanel(BaseControlPanel):
    """Control panel for Step 5: Final Video Composition"""
    
    def get_title(self) -> str:
        return "Final Video Composition"
    
    def get_description(self) -> str:
        return "Combine all elements into final YouTube Short using FFmpeg"
    
    def create_controls(self):
        """Create final composition controls"""
        super().create_controls()
        
        # Main controls frame
        self.controls_frame = ctk.CTkScrollableFrame(self, fg_color=YOUTUBE_LIGHT)
        self.controls_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Encoding settings
        self.encoding_frame = ctk.CTkFrame(self.controls_frame, fg_color=YOUTUBE_DARK)
        self.encoding_frame.pack(fill="x", padx=10, pady=5)
        
        self.encoding_label = ctk.CTkLabel(
            self.encoding_frame,
            text="Encoding Settings:",
            font=("Arial", 12, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.encoding_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # GPU encoding checkbox
        self.gpu_encoding_var = ctk.BooleanVar()
        self.gpu_encoding_checkbox = ctk.CTkCheckBox(
            self.encoding_frame,
            text="Use GPU Encoding (NVENC)",
            variable=self.gpu_encoding_var,
            font=("Arial", 11),
            text_color=YOUTUBE_TEXT
        )
        self.gpu_encoding_checkbox.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Video preset
        self.preset_label = ctk.CTkLabel(
            self.encoding_frame,
            text="Video Preset:",
            font=("Arial", 11),
            text_color=YOUTUBE_TEXT
        )
        self.preset_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.preset_var = ctk.StringVar()
        self.preset_dropdown = ctk.CTkOptionMenu(
            self.encoding_frame,
            values=self.settings_manager.get_available_video_presets(),
            variable=self.preset_var,
            fg_color=YOUTUBE_LIGHT,
            button_color=YOUTUBE_RED,
            button_hover_color=YOUTUBE_RED_HOVER
        )
        self.preset_dropdown.pack(fill="x", padx=10, pady=(0, 10))
        
        # Watermark settings
        self.watermark_frame = ctk.CTkFrame(self.controls_frame, fg_color=YOUTUBE_DARK)
        self.watermark_frame.pack(fill="x", padx=10, pady=5)
        
        self.watermark_label = ctk.CTkLabel(
            self.watermark_frame,
            text="Watermark Settings:",
            font=("Arial", 12, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.watermark_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Watermark text
        self.watermark_text_label = ctk.CTkLabel(
            self.watermark_frame,
            text="Watermark Text:",
            font=("Arial", 11),
            text_color=YOUTUBE_TEXT
        )
        self.watermark_text_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.watermark_text_var = ctk.StringVar()
        self.watermark_text_entry = ctk.CTkEntry(
            self.watermark_frame,
            textvariable=self.watermark_text_var
        )
        self.watermark_text_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Watermark position
        self.watermark_pos_label = ctk.CTkLabel(
            self.watermark_frame,
            text="Position:",
            font=("Arial", 11),
            text_color=YOUTUBE_TEXT
        )
        self.watermark_pos_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.watermark_pos_var = ctk.StringVar()
        self.watermark_pos_dropdown = ctk.CTkOptionMenu(
            self.watermark_frame,
            values=self.settings_manager.get_available_watermark_positions(),
            variable=self.watermark_pos_var,
            fg_color=YOUTUBE_LIGHT,
            button_color=YOUTUBE_RED,
            button_hover_color=YOUTUBE_RED_HOVER
        )
        self.watermark_pos_dropdown.pack(fill="x", padx=10, pady=(0, 10))
    
    def load_settings(self):
        """Load current settings into widgets"""
        self.gpu_encoding_var.set(self.settings_manager.get_setting("USE_GPU_ENCODING", True))
        self.preset_var.set(self.settings_manager.get_setting("VIDEO_PRESET", "fast"))
        self.watermark_text_var.set(self.settings_manager.get_setting("WATERMARK_TEXT", "Generated by AI"))
        self.watermark_pos_var.set(self.settings_manager.get_setting("WATERMARK_POSITION_MODE", "top-right"))
    
    def collect_widget_values(self):
        """Collect widget values and save to settings manager"""
        self.settings_manager.update_setting("USE_GPU_ENCODING", self.gpu_encoding_var.get())
        self.settings_manager.update_setting("VIDEO_PRESET", self.preset_var.get())
        self.settings_manager.update_setting("WATERMARK_TEXT", self.watermark_text_var.get())
        self.settings_manager.update_setting("WATERMARK_POSITION_MODE", self.watermark_pos_var.get())
    
    def run_step(self):
        """Run final video composition"""
        super().run_step()
        
        # Check if all previous steps are completed
        required_panels = ['script', 'voice', 'background', 'caption']
        missing_steps = []
        
        if hasattr(self.app, 'panels'):
            for step in required_panels:
                panel = self.app.panels.get(step)
                if not panel or not hasattr(panel, f'{step}_data'):
                    missing_steps.append(step.replace('_', ' ').title())
        
        if missing_steps:
            self.set_status("Error: Missing required steps", False)
            self.update_output(f"Please complete these steps first:\n• {chr(10).join(missing_steps)}")
            return
        
        # Get data from all panels
        script_panel = self.app.panels['script']
        voice_panel = self.app.panels['voice']
        background_panel = self.app.panels['background']
        caption_panel = self.app.panels['caption']
        
        # Prepare data for composition
        video_clips = background_panel.background_data['video_clips']
        audio_path = voice_panel.voice_data['path']
        audio_duration = voice_panel.voice_data['duration']
        caption_file = caption_panel.caption_data['file']
        
        # Generate output filename from script title
        script_title = script_panel.script_data.get('title', 'YouTube_Short')
        safe_title = "".join(c for c in script_title if c.isalnum() or c in (" ", "-", "_"))[:50]
        output_name = f"Final_{safe_title}"
        
        # Update UI to show we're starting
        self.update_output("Combining all elements into final video...\n\nThis may take 1-3 minutes.\nPlease wait...")
        
        # Run final composition in a separate thread
        self.run_in_thread(self._compose_final_video_thread, video_clips, audio_path, audio_duration, caption_file, output_name)
    
    def _compose_final_video_thread(self, video_clips, audio_path, audio_duration, caption_file, output_name):
        """Compose final video in a separate thread"""
        try:
            # Import step function
            from steps.step5_combine_everything import combine_into_final_video
            
            # Run final composition
            final_video = combine_into_final_video(
                video_clips,
                audio_path,
                audio_duration,
                caption_file,
                output_name
            )
            return final_video
            
        except Exception as e:
            raise e
    
    def handle_thread_result(self, final_video):
        """Handle successful final video composition"""
        if final_video and Path(final_video).exists():
            # Display results
            file_size = Path(final_video).stat().st_size / (1024 * 1024)  # MB
            
            # Get audio duration from voice panel
            voice_panel = self.app.panels.get('voice')
            audio_duration = voice_panel.voice_data.get('duration', 0) if voice_panel else 0
            
            output_text = f"✓ Final Video Created Successfully!\n\n"
            output_text += f"Video file: {Path(final_video).name}\n"
            output_text += f"Location: {Path(final_video).parent}\n"
            output_text += f"Duration: {audio_duration:.1f} seconds\n"
            output_text += f"Resolution: 1080x1920 (9:16)\n"
            output_text += f"File size: {file_size:.1f} MB\n"
            output_text += f"Format: MP4 (H.264/AAC)\n\n"
            output_text += f"Components used:\n"
            output_text += f"• {len(self.app.panels['background'].background_data['video_clips'])} background video clips\n"
            output_text += f"• Voice narration ({self.settings_manager.get_setting('TTS_ENGINE', 'edge')})\n"
            output_text += f"• Karaoke captions (ASS format)\n"
            output_text += f"• AI watermark\n\n"
            output_text += f"Ready for YouTube Shorts upload!"
            
            self.update_output(output_text)
            self.set_status("Completed", False, True)
            
            # Store final video data
            self.final_video_data = {
                'path': final_video,
                'size_mb': file_size,
                'duration': audio_duration
            }
            
            # Notify parent of completion
            if hasattr(self.app, 'update_step_completion'):
                self.app.update_step_completion('final', True)
        else:
            self.set_status("Error: Failed to create final video", False)
            self.update_output("Failed to create final video. Please check:\n• All input files exist\n• FFmpeg is installed\n• Try again")
        
        self.run_button.configure(state="normal")
