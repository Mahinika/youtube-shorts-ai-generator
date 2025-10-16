"""
GROK CONFIGURATION PANEL

Dedicated panel for viewing and managing Grok AI configuration.
Shows current settings, connection status, and allows testing.
"""

import sys
import threading
from pathlib import Path
from typing import Dict, Any, Optional

import customtkinter as ctk
from tkinter import messagebox

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from settings.config import Config
from utils.ai_providers import GrokProvider, AIProviderError

# YouTube Studio color scheme
YOUTUBE_DARK = "#282828"
YOUTUBE_DARKER = "#181818"
YOUTUBE_LIGHT = "#3f3f3f"
YOUTUBE_RED = "#FF0000"
YOUTUBE_RED_HOVER = "#CC0000"
YOUTUBE_TEXT = "#FFFFFF"
YOUTUBE_TEXT_SECONDARY = "#AAAAAA"
YOUTUBE_GREEN = "#00FF00"
YOUTUBE_YELLOW = "#FFFF00"


class GrokConfigPanel(ctk.CTkFrame):
    """Panel for viewing and managing Grok AI configuration"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.configure(fg_color=YOUTUBE_DARK)
        
        # Get reference to root window for thread scheduling
        self.root = parent.winfo_toplevel()
        
        # Panel state
        self.is_testing = False
        
        # Create UI elements
        self.create_header()
        self.create_config_display()
        self.create_status_section()
        self.create_test_section()
        self.create_buttons()
        
        # Load current configuration
        self.load_configuration()
        self.update_status_display()
        self.load_model_info()
    
    def create_header(self):
        """Create panel header"""
        self.header_frame = ctk.CTkFrame(self, fg_color=YOUTUBE_LIGHT)
        self.header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Title with Grok icon
        self.title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_frame.pack(fill="x", padx=10, pady=10)
        
        # Grok icon (using 🤖 emoji)
        self.icon_label = ctk.CTkLabel(
            self.title_frame,
            text="🤖",
            font=("Arial", 24)
        )
        self.icon_label.pack(side="left", padx=(0, 10))
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="Grok AI Configuration",
            font=("Arial", 18, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.title_label.pack(side="left")
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Configure and test your Grok AI connection for script generation",
            font=("Arial", 12),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        self.subtitle_label.pack(pady=(0, 10))
    
    def create_config_display(self):
        """Create configuration display section"""
        self.config_frame = ctk.CTkFrame(self, fg_color=YOUTUBE_LIGHT)
        self.config_frame.pack(fill="x", padx=10, pady=5)
        
        self.config_title = ctk.CTkLabel(
            self.config_frame,
            text="Current Configuration",
            font=("Arial", 14, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.config_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Model Selection
        self.model_selection_frame = ctk.CTkFrame(self.config_frame, fg_color=YOUTUBE_DARK)
        self.model_selection_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.model_selection_label = ctk.CTkLabel(
            self.model_selection_frame,
            text="Grok Model:",
            font=("Arial", 11, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.model_selection_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.model_var = ctk.StringVar()
        self.model_dropdown = ctk.CTkOptionMenu(
            self.model_selection_frame,
            values=["grok-beta", "grok-4-fast", "grok-3", "grok-2"],
            variable=self.model_var,
            fg_color=YOUTUBE_LIGHT,
            button_color=YOUTUBE_RED,
            button_hover_color=YOUTUBE_RED_HOVER,
            command=self.on_model_changed
        )
        self.model_dropdown.pack(fill="x", padx=10, pady=(0, 10))
        
        # Model info
        self.model_info = ctk.CTkLabel(
            self.model_selection_frame,
            text="grok-beta: Latest model with best reasoning quality",
            font=("Arial", 10),
            text_color=YOUTUBE_TEXT_SECONDARY,
            wraplength=600
        )
        self.model_info.pack(anchor="w", padx=10, pady=(0, 10))

        # Configuration details
        self.config_details = ctk.CTkTextbox(
            self.config_frame,
            height=150,
            font=("Consolas", 11),
            text_color=YOUTUBE_TEXT,
            fg_color=YOUTUBE_DARK
        )
        self.config_details.pack(fill="x", padx=10, pady=(0, 10))
        self.config_details.configure(state="disabled")
    
    def create_status_section(self):
        """Create status indicator section"""
        self.status_frame = ctk.CTkFrame(self, fg_color=YOUTUBE_LIGHT)
        self.status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_title = ctk.CTkLabel(
            self.status_frame,
            text="Connection Status",
            font=("Arial", 14, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.status_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Status indicators
        self.status_container = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        self.status_container.pack(fill="x", padx=10, pady=(0, 10))
        
        # API Key status
        self.api_key_frame = ctk.CTkFrame(self.status_container, fg_color=YOUTUBE_DARK)
        self.api_key_frame.pack(fill="x", pady=2)
        
        self.api_key_label = ctk.CTkLabel(
            self.api_key_frame,
            text="API Key:",
            font=("Arial", 11, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.api_key_label.pack(side="left", padx=10, pady=5)
        
        self.api_key_status = ctk.CTkLabel(
            self.api_key_frame,
            text="Not Set",
            font=("Arial", 11),
            text_color=YOUTUBE_YELLOW
        )
        self.api_key_status.pack(side="right", padx=10, pady=5)
        
        # Model status
        self.model_frame = ctk.CTkFrame(self.status_container, fg_color=YOUTUBE_DARK)
        self.model_frame.pack(fill="x", pady=2)
        
        self.model_label = ctk.CTkLabel(
            self.model_frame,
            text="Model:",
            font=("Arial", 11, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.model_label.pack(side="left", padx=10, pady=5)
        
        self.model_status = ctk.CTkLabel(
            self.model_frame,
            text="Unknown",
            font=("Arial", 11),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        self.model_status.pack(side="right", padx=10, pady=5)
        
        # Provider status
        self.provider_frame = ctk.CTkFrame(self.status_container, fg_color=YOUTUBE_DARK)
        self.provider_frame.pack(fill="x", pady=2)
        
        self.provider_label = ctk.CTkLabel(
            self.provider_frame,
            text="Provider:",
            font=("Arial", 11, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.provider_label.pack(side="left", padx=10, pady=5)
        
        self.provider_status = ctk.CTkLabel(
            self.provider_frame,
            text="Unknown",
            font=("Arial", 11),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        self.provider_status.pack(side="right", padx=10, pady=5)
        
        # Connection status
        self.connection_frame = ctk.CTkFrame(self.status_container, fg_color=YOUTUBE_DARK)
        self.connection_frame.pack(fill="x", pady=2)
        
        self.connection_label = ctk.CTkLabel(
            self.connection_frame,
            text="Connection:",
            font=("Arial", 11, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.connection_label.pack(side="left", padx=10, pady=5)
        
        self.connection_status = ctk.CTkLabel(
            self.connection_frame,
            text="Not Tested",
            font=("Arial", 11),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        self.connection_status.pack(side="right", padx=10, pady=5)
    
    def create_test_section(self):
        """Create test section"""
        self.test_frame = ctk.CTkFrame(self, fg_color=YOUTUBE_LIGHT)
        self.test_frame.pack(fill="x", padx=10, pady=5)
        
        self.test_title = ctk.CTkLabel(
            self.test_frame,
            text="Test Connection",
            font=("Arial", 14, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.test_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Test prompt input
        self.test_prompt_label = ctk.CTkLabel(
            self.test_frame,
            text="Test Prompt:",
            font=("Arial", 11),
            text_color=YOUTUBE_TEXT
        )
        self.test_prompt_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.test_prompt_entry = ctk.CTkTextbox(
            self.test_frame,
            height=60,
            font=("Arial", 11)
        )
        self.test_prompt_entry.pack(fill="x", padx=10, pady=(0, 5))
        self.test_prompt_entry.insert("1.0", "Say hello and tell me you're working correctly!")
        
        # Test result display
        self.test_result = ctk.CTkTextbox(
            self.test_frame,
            height=100,
            font=("Consolas", 10),
            text_color=YOUTUBE_TEXT,
            fg_color=YOUTUBE_DARK
        )
        self.test_result.pack(fill="x", padx=10, pady=(0, 10))
        self.test_result.insert("1.0", "Test results will appear here...")
        self.test_result.configure(state="disabled")
    
    def create_buttons(self):
        """Create action buttons"""
        self.buttons_frame = ctk.CTkFrame(self, fg_color=YOUTUBE_DARK)
        self.buttons_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        # Test connection button
        self.test_button = ctk.CTkButton(
            self.buttons_frame,
            text="🧪 Test Grok Connection",
            command=self.test_connection,
            fg_color=YOUTUBE_RED,
            hover_color=YOUTUBE_RED_HOVER,
            font=("Arial", 12, "bold")
        )
        self.test_button.pack(side="left", padx=(10, 5), pady=10)
        
        # Refresh button
        self.refresh_button = ctk.CTkButton(
            self.buttons_frame,
            text="🔄 Refresh Config",
            command=self.refresh_configuration,
            fg_color=YOUTUBE_LIGHT,
            hover_color=YOUTUBE_TEXT_SECONDARY,
            font=("Arial", 12)
        )
        self.refresh_button.pack(side="left", padx=5, pady=10)
        
        # Open config button
        self.open_config_button = ctk.CTkButton(
            self.buttons_frame,
            text="📝 Open Config File",
            command=self.open_config_file,
            fg_color=YOUTUBE_LIGHT,
            hover_color=YOUTUBE_TEXT_SECONDARY,
            font=("Arial", 12)
        )
        self.open_config_button.pack(side="left", padx=5, pady=10)
    
    def load_configuration(self):
        """Load current Grok configuration"""
        try:
            config_path = Path(__file__).parent.parent / 'settings' / 'config.py'
            last_updated = config_path.stat().st_mtime if config_path.exists() else 'Unknown'
            
            # Set current model in dropdown
            self.model_var.set(Config.GROK_MODEL)
            
            config_text = f"""AI Provider: {Config.AI_PROVIDER}
Grok API Base: {Config.GROK_API_BASE}
Grok Model: {Config.GROK_MODEL}
Grok Temperature: {Config.GROK_TEMPERATURE}
Grok Max Tokens: {Config.GROK_MAX_TOKENS}
Grok API Key: {'*' * 20 if Config.GROK_API_KEY else 'NOT SET'}
Token Optimization: {getattr(Config, 'GROK_USE_EFFICIENT_MODE', False)}

Configuration File: {config_path}
Last Updated: {last_updated}

Note: Use the dropdown above to change the model, or edit config.py directly."""
            
            self.config_details.configure(state="normal")
            self.config_details.delete("1.0", "end")
            self.config_details.insert("1.0", config_text)
            self.config_details.configure(state="disabled")
            
        except Exception as e:
            error_text = f"Error loading configuration:\n{str(e)}"
            self.config_details.configure(state="normal")
            self.config_details.delete("1.0", "end")
            self.config_details.insert("1.0", error_text)
            self.config_details.configure(state="disabled")
    
    def update_status_display(self):
        """Update status indicators"""
        try:
            # API Key status
            if Config.GROK_API_KEY and len(Config.GROK_API_KEY.strip()) > 0:
                self.api_key_status.configure(
                    text="✓ Set",
                    text_color=YOUTUBE_GREEN
                )
            else:
                self.api_key_status.configure(
                    text="✗ Not Set",
                    text_color=YOUTUBE_YELLOW
                )
            
            # Model status
            self.model_status.configure(
                text=Config.GROK_MODEL,
                text_color=YOUTUBE_TEXT
            )
            
            # Provider status
            provider_text = f"{Config.AI_PROVIDER.upper()}"
            if Config.AI_PROVIDER.lower() == "grok":
                provider_text += " (Primary)"
                color = YOUTUBE_GREEN
            else:
                provider_text += " (Fallback)"
                color = YOUTUBE_YELLOW
            
            self.provider_status.configure(
                text=provider_text,
                text_color=color
            )
            
        except Exception as e:
            print(f"Error updating status display: {e}")
    
    def test_connection(self):
        """Test Grok connection"""
        if self.is_testing:
            return
        
        self.is_testing = True
        self.test_button.configure(state="disabled", text="🧪 Testing...")
        
        # Get test prompt
        test_prompt = self.test_prompt_entry.get("1.0", "end-1c").strip()
        if not test_prompt:
            test_prompt = "Say hello and tell me you're working correctly!"
        
        # Clear previous results
        self.test_result.configure(state="normal")
        self.test_result.delete("1.0", "end")
        self.test_result.insert("1.0", "Testing Grok connection...\nPlease wait...")
        self.test_result.configure(state="disabled")
        
        # Run test in separate thread
        self.run_in_thread(self._test_connection_thread, test_prompt)
    
    def _test_connection_thread(self, test_prompt):
        """Test connection in a separate thread"""
        try:
            # Test Grok provider
            system_prompt = "You are a helpful AI assistant. Respond briefly and clearly."
            response = GrokProvider.generate(system_prompt, test_prompt)
            
            return {
                'success': True,
                'response': response,
                'provider': 'Grok'
            }
            
        except AIProviderError as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'Grok'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'provider': 'Grok'
            }
    
    def handle_test_result(self, result):
        """Handle test connection result"""
        self.is_testing = False
        self.test_button.configure(state="normal", text="🧪 Test Grok Connection")
        
        if result['success']:
            # Update connection status
            self.connection_status.configure(
                text="✓ Connected",
                text_color=YOUTUBE_GREEN
            )
            
            # Display successful result
            result_text = f"✅ SUCCESS: Grok connection working!\n\n"
            result_text += f"Provider: {result['provider']}\n"
            result_text += f"Response:\n{result['response']}"
            
            self.test_result.configure(state="normal")
            self.test_result.delete("1.0", "end")
            self.test_result.insert("1.0", result_text)
            self.test_result.configure(state="disabled")
            
        else:
            # Update connection status
            self.connection_status.configure(
                text="✗ Failed",
                text_color=YOUTUBE_YELLOW
            )
            
            # Display error result
            result_text = f"❌ FAILED: Grok connection failed\n\n"
            result_text += f"Provider: {result['provider']}\n"
            result_text += f"Error: {result['error']}\n\n"
            result_text += f"Troubleshooting:\n"
            result_text += f"• Check your API key is correct\n"
            result_text += f"• Verify internet connection\n"
            result_text += f"• Check xAI service status\n"
            result_text += f"• Try again in a few minutes"
            
            self.test_result.configure(state="normal")
            self.test_result.delete("1.0", "end")
            self.test_result.insert("1.0", result_text)
            self.test_result.configure(state="disabled")
    
    def handle_test_error(self, error):
        """Handle test connection error"""
        self.is_testing = False
        self.test_button.configure(state="normal", text="🧪 Test Grok Connection")
        
        self.connection_status.configure(
            text="✗ Error",
            text_color=YOUTUBE_YELLOW
        )
        
        error_text = f"❌ ERROR: Test failed unexpectedly\n\n{str(error)}"
        
        self.test_result.configure(state="normal")
        self.test_result.delete("1.0", "end")
        self.test_result.insert("1.0", error_text)
        self.test_result.configure(state="disabled")
    
    def refresh_configuration(self):
        """Refresh configuration display"""
        self.load_configuration()
        self.update_status_display()
        
        # Show refresh message
        self.test_result.configure(state="normal")
        self.test_result.delete("1.0", "end")
        self.test_result.insert("1.0", "Configuration refreshed successfully!")
        self.test_result.configure(state="disabled")
    
    def open_config_file(self):
        """Open config file for editing"""
        try:
            config_path = Path(__file__).parent.parent / 'settings' / 'config.py'
            
            if config_path.exists():
                import subprocess
                import os
                
                # Try to open with default editor
                if os.name == 'nt':  # Windows
                    os.startfile(str(config_path))
                elif os.name == 'posix':  # macOS and Linux
                    subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', str(config_path)])
                
                self.test_result.configure(state="normal")
                self.test_result.delete("1.0", "end")
                self.test_result.insert("1.0", f"Opened config file:\n{config_path}\n\nMake changes and click 'Refresh Config' to update.")
                self.test_result.configure(state="disabled")
            else:
                messagebox.showerror("Error", f"Config file not found:\n{config_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open config file:\n{str(e)}")
    
    def run_in_thread(self, target_func, *args, **kwargs):
        """Run a function in a separate thread to prevent UI freezing"""
        def thread_wrapper():
            try:
                result = target_func(*args, **kwargs)
                # Schedule UI update on main thread using a proper closure
                def handle_result():
                    self.handle_test_result(result)
                self.root.after(0, handle_result)
            except Exception as e:
                # Schedule error handling on main thread using a proper closure
                def handle_error(error=e):
                    self.handle_test_error(error)
                self.root.after(0, handle_error)
        
        thread = threading.Thread(target=thread_wrapper, daemon=True)
        thread.start()
    
    def on_model_changed(self, selected_model):
        """Handle model selection change"""
        model_info = {
            "grok-beta": "Latest model with best reasoning quality - Recommended for script generation",
            "grok-4-fast": "Newest model with 2M context, 344 tokens/sec - Best for speed and efficiency",
            "grok-3": "Current default model - Reliable performance",
            "grok-2": "Previous generation model - Legacy support"
        }
        
        info_text = model_info.get(selected_model, "Unknown model")
        self.model_info.configure(text=info_text)
        
        # Update test result to show model change
        self.test_result.configure(state="normal")
        self.test_result.delete("1.0", "end")
        self.test_result.insert("1.0", f"Model changed to: {selected_model}\n{info_text}\n\nClick 'Test Grok Connection' to test the new model.")
        self.test_result.configure(state="disabled")
    
    def load_model_info(self):
        """Load model information for current selection"""
        current_model = Config.GROK_MODEL
        self.on_model_changed(current_model)


if __name__ == "__main__":
    # Test the panel standalone
    import customtkinter as ctk
    
    root = ctk.CTk()
    root.title("Grok Configuration Panel Test")
    root.geometry("800x700")
    
    panel = GrokConfigPanel(root)
    panel.pack(fill="both", expand=True, padx=20, pady=20)
    
    root.mainloop()
