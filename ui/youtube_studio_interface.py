"""
YOUTUBE STUDIO INTERFACE - REDESIGNED

Professional GUI with left-sidebar navigation and dedicated control panels.
Dark theme with red accents matching YouTube branding.
"""

import sys
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ui.settings_manager import SettingsManager
from ui.control_panels import (
    ScriptGeneratorPanel,
    VoiceSynthesisPanel,
    BackgroundGeneratorPanel,
    CaptionCreationPanel,
    FinalCompositionPanel
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
    """Main application window with left-sidebar navigation"""

    def __init__(self):
        """Initialize the YouTube Studio interface"""

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create main window
        self.root = ctk.CTk()
        self.root.title("YouTube Shorts Maker")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        self.root.configure(fg_color=YOUTUBE_DARKER)

        # Initialize settings manager
        self.settings_manager = SettingsManager()

        # Current panel tracking
        self.current_panel = None
        self.panels = {}

        # Step completion tracking
        self.step_completion = {
            "script": False,
            "voice": False,
            "background": False,
            "caption": False,
            "final": False
        }

        # Build UI
        self.create_layout()

    def create_layout(self):
        """Create the main layout with left sidebar and content area"""

        # Main container
        self.main_container = ctk.CTkFrame(self.root, fg_color=YOUTUBE_DARKER)
        self.main_container.pack(fill="both", expand=True)

        # Create left sidebar
        self.create_sidebar()

        # Create main content area
        self.create_content_area()

        # Create control panels
        self.create_panels()

        # Show default panel
        self.show_panel("script")

    def create_sidebar(self):
        """Create left sidebar navigation"""

        # Sidebar frame
        self.sidebar = ctk.CTkFrame(
            self.main_container,
            width=280,
            fg_color=YOUTUBE_DARK,
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y", padx=(0, 1))
        self.sidebar.pack_propagate(False)

        # App header
        self.create_app_header()

        # Navigation items
        self.create_navigation_items()

        # Settings section
        self.create_settings_section()

    def create_app_header(self):
        """Create app header with logo and title"""

        # Logo and title frame
        self.header_frame = ctk.CTkFrame(self.sidebar, fg_color=YOUTUBE_DARK)
        self.header_frame.pack(fill="x", padx=10, pady=(20, 10))

        # Logo (simple play button icon)
        self.logo_frame = ctk.CTkFrame(self.header_frame, width=40, height=40, fg_color=YOUTUBE_RED)
        self.logo_frame.pack(pady=(10, 10))
        self.logo_frame.pack_propagate(False)

        self.logo_label = ctk.CTkLabel(
            self.logo_frame,
            text="▶",
            font=("Arial", 16, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.logo_label.pack(expand=True)

        # App title
        self.app_title = ctk.CTkLabel(
            self.header_frame,
            text="YouTube Shorts Maker",
            font=("Arial", 12, "bold"),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        self.app_title.pack(pady=(0, 10))

        # Main title
        self.main_title = ctk.CTkLabel(
            self.header_frame,
            text="YouTube Shorts",
            font=("Arial", 24, "bold"),
            text_color=YOUTUBE_TEXT
        )
        self.main_title.pack(pady=(0, 5))

        # Subtitle
        self.subtitle = ctk.CTkLabel(
            self.header_frame,
            text="AI Video Maker",
            font=("Arial", 14),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        self.subtitle.pack(pady=(0, 20))

    def create_navigation_items(self):
        """Create navigation items for each step"""

        # Navigation frame
        self.nav_frame = ctk.CTkFrame(self.sidebar, fg_color=YOUTUBE_DARK)
        self.nav_frame.pack(fill="x", padx=10, pady=(0, 20))

        # Navigation items
        self.nav_items = [
            {
                "key": "script",
                "title": "Script Generator",
                "description": "Generate AI scripts",
                "step": 1
            },
            {
                "key": "voice",
                "title": "Voice Synthesis",
                "description": "Create voice narration",
                "step": 2
            },
            {
                "key": "background",
                "title": "Background Generator",
                "description": "AI image generation",
                "step": 3
            },
            {
                "key": "caption",
                "title": "Caption Creation",
                "description": "Karaoke captions",
                "step": 4
            },
            {
                "key": "final",
                "title": "Final Video Composition",
                "description": "Combine everything",
                "step": 5
            }
        ]

        self.nav_buttons = {}

        for item in self.nav_items:
            self.create_nav_button(item)

    def create_nav_button(self, item):
        """Create a navigation button for a step"""

        # Button frame
        btn_frame = ctk.CTkFrame(self.nav_frame, fg_color=YOUTUBE_LIGHT)
        btn_frame.pack(fill="x", padx=5, pady=2)

        # Button
        btn = ctk.CTkButton(
            btn_frame,
            text=f"{item['step']}. {item['title']}",
            command=lambda: self.show_panel(item['key']),
            fg_color="transparent",
            hover_color=YOUTUBE_RED_HOVER,
            text_color=YOUTUBE_TEXT,
            font=("Arial", 12, "bold"),
            anchor="w",
            height=50
        )
        btn.pack(fill="x", padx=5, pady=5)

        # Description
        desc = ctk.CTkLabel(
            btn_frame,
            text=item['description'],
            font=("Arial", 10),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        desc.pack(padx=5, pady=(0, 5))

        # Status indicator (will be updated)
        status = ctk.CTkLabel(
            btn_frame,
            text="●",
            font=("Arial", 12),
            text_color=YOUTUBE_TEXT_SECONDARY
        )
        status.pack(padx=5, pady=(0, 5))

        # Store references
        self.nav_buttons[item['key']] = {
            'button': btn,
            'frame': btn_frame,
            'status': status,
            'description': desc
        }

    def create_settings_section(self):
        """Create settings and about section"""

        # Settings frame
        self.settings_frame = ctk.CTkFrame(self.sidebar, fg_color=YOUTUBE_DARK)
        self.settings_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Settings button
        self.settings_btn = ctk.CTkButton(
            self.settings_frame,
            text="⚙️ Settings",
            command=self.show_settings,
            fg_color="transparent",
            hover_color=YOUTUBE_RED_HOVER,
            text_color=YOUTUBE_TEXT,
            font=("Arial", 12),
            anchor="w"
        )
        self.settings_btn.pack(fill="x", padx=10, pady=5)

        # About button
        self.about_btn = ctk.CTkButton(
            self.settings_frame,
            text="ℹ️ About",
            command=self.show_about,
            fg_color="transparent",
            hover_color=YOUTUBE_RED_HOVER,
            text_color=YOUTUBE_TEXT,
            font=("Arial", 12),
            anchor="w"
        )
        self.about_btn.pack(fill="x", padx=10, pady=(0, 10))

    def create_content_area(self):
        """Create main content area for control panels"""

        # Content frame
        self.content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=YOUTUBE_DARK,
            corner_radius=0
        )
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Welcome message (shown when no panel is selected)
        self.welcome_label = ctk.CTkLabel(
            self.content_frame,
            text="Welcome to YouTube Shorts Maker!\n\nSelect a step from the sidebar to begin.",
            font=("Arial", 16),
            text_color=YOUTUBE_TEXT_SECONDARY
        )

    def create_panels(self):
        """Create all control panels"""

        # Create panel instances with master reference
        self.panels = {
            "script": ScriptGeneratorPanel(
                self.content_frame,
                self.settings_manager
            ),
            "voice": VoiceSynthesisPanel(
                self.content_frame,
                self.settings_manager
            ),
            "background": BackgroundGeneratorPanel(
                self.content_frame,
                self.settings_manager
            ),
            "caption": CaptionCreationPanel(
                self.content_frame,
                self.settings_manager
            ),
            "final": FinalCompositionPanel(
                self.content_frame,
                self.settings_manager
            )
        }

        # Set app reference for each panel (don't override master)
        for panel in self.panels.values():
            panel.app = self
            panel.pack_forget()

    def show_panel(self, panel_key):
        """Show the specified panel and hide others"""

        # Hide current panel
        if self.current_panel:
            self.current_panel.pack_forget()

        # Hide welcome message
        self.welcome_label.pack_forget()

        # Show selected panel
        if panel_key in self.panels:
            self.current_panel = self.panels[panel_key]
            self.current_panel.pack(fill="both", expand=True, padx=20, pady=20)

            # Update navigation button states
            self.update_nav_button_states(panel_key)

    def update_nav_button_states(self, active_key):
        """Update navigation button visual states"""

        for key, nav_data in self.nav_buttons.items():
            if key == active_key:
                # Active button
                nav_data['button'].configure(
                    fg_color=YOUTUBE_RED,
                    text_color=YOUTUBE_TEXT
                )
                nav_data['status'].configure(text="●", text_color=YOUTUBE_RED)
            else:
                # Inactive button
                nav_data['button'].configure(
                    fg_color="transparent",
                    text_color=YOUTUBE_TEXT
                )
                # Update status based on completion
                if self.step_completion.get(key, False):
                    nav_data['status'].configure(text="✓", text_color="#00FF00")
                else:
                    nav_data['status'].configure(text="●", text_color=YOUTUBE_TEXT_SECONDARY)

    def update_step_completion(self, step_key, completed):
        """Update step completion status"""

        self.step_completion[step_key] = completed
        self.update_nav_button_states(
            list(self.nav_buttons.keys())[0] if not self.current_panel else None
        )

    def show_settings(self):
        """Show settings dialog"""

        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("600x400")
        settings_window.configure(fg_color=YOUTUBE_DARK)

        # Settings content
        content = ctk.CTkLabel(
            settings_window,
            text="Global Settings\n\nThis will contain global application settings\nthat apply to all steps.",
            font=("Arial", 14),
            text_color=YOUTUBE_TEXT
        )
        content.pack(expand=True, padx=20, pady=20)

    def show_about(self):
        """Show about dialog"""

        about_window = ctk.CTkToplevel(self.root)
        about_window.title("About")
        about_window.geometry("500x300")
        about_window.configure(fg_color=YOUTUBE_DARK)

        # About content
        content = ctk.CTkLabel(
            about_window,
            text="YouTube Shorts Maker\n\n"
                 "AI-powered video creation tool\n"
                 "Version 2.0\n\n"
                 "Built with:\n"
                 "• Ollama (AI Scripts)\n"
                 "• Stable Diffusion (AI Images)\n"
                 "• Edge TTS (Voice Synthesis)\n"
                 "• FFmpeg (Video Processing)\n\n"
                 "© 2024",
            font=("Arial", 12),
            text_color=YOUTUBE_TEXT
        )
        content.pack(expand=True, padx=20, pady=20)

    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Launch the YouTube Shorts Maker"""
    try:
        app = YouTubeStudioApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()