"""Dialog components for the application."""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from typing import Callable
import os
from PIL import Image, ImageTk
import json
import sys

from src.gui.utils.gui_utils import center_window
from src.config.app_config import AppConfig

def get_version() -> str:
    """Get current version from version.json."""
    try:
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))  # dialogs.py directory
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
        version_file = os.path.join(project_root, 'version.json')
        
        # For frozen app (when bundled)
        if getattr(sys, 'frozen', False):
            if sys.platform == 'darwin':
                # For macOS app bundle
                version_file = os.path.join(os.path.dirname(sys.executable), '..', 'Resources', 'version.json')
            else:
                # For Windows executable
                version_file = os.path.join(os.path.dirname(sys.executable), 'version.json')
        
        print(f"Looking for version.json at: {version_file}")
        
        if not os.path.exists(version_file):
            print(f"Error: version.json not found at {version_file}")
            return "Unknown"
        
        with open(version_file, 'r') as f:
            version_data = json.load(f)
            version = f"{version_data['major']}.{version_data['minor']}.{version_data['patch']}"
            print(f"Successfully read version: {version}")
            return version
    except Exception as e:
        print(f"Error reading version from version.json: {str(e)}")
        return "Unknown"

class LoginDialog:
    """Dialog for Spotify authentication."""

    def __init__(self, parent: tk.Tk, on_cookie_save: Callable[[str], None]):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Spotify Authentication")
        self.dialog.geometry("700x600")
        self.dialog.configure(bg='#282828')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.on_cookie_save = on_cookie_save

        # Make dialog resizable
        self.dialog.resizable(True, True)
        
        # Center the dialog
        center_window(self.dialog, 700, 600)
        self._init_components()

    def _init_components(self) -> None:
        """Initialize dialog components."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Connect to Spotify",
            font=('Helvetica', 16, 'bold'),
            wraplength=600
        )
        title_label.pack(pady=(0, 20))

        self._add_instructions(main_frame)
        self._add_buttons(main_frame)
        self._add_cookie_entry(main_frame)
        self._add_help_text(main_frame)

    def _add_instructions(self, container: ttk.Frame) -> None:
        """Add instruction steps to the dialog."""
        steps = [
            "1. Click the 'Open Spotify' button below",
            "2. Log in to Spotify if needed",
            "3. Press F12 to open Developer Tools",
            "4. Click 'Application' tab in Developer Tools",
            "5. Under 'Storage' expand 'Cookies'",
            "6. Click on 'https://spotify.com'",
            "7. Find 'sp_dc' cookie and copy its value",
            "8. Paste the value below"
        ]

        steps_frame = ttk.Frame(container)
        steps_frame.pack(fill=tk.BOTH, padx=20, pady=10)

        for step in steps:
            step_label = ttk.Label(
                steps_frame,
                text=step,
                font=('Helvetica', 11),
                wraplength=550
            )
            step_label.pack(anchor='w', pady=5)

    def _add_buttons(self, container: ttk.Frame) -> None:
        """Add buttons to the dialog."""
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=20)

        open_button = ttk.Button(
            button_frame,
            text="Open Spotify",
            command=lambda: webbrowser.open('https://open.spotify.com'),
            style='Accent.TButton'
        )
        open_button.pack(pady=10)

    def _add_cookie_entry(self, container: ttk.Frame) -> None:
        """Add cookie entry field to the dialog."""
        entry_frame = ttk.Frame(container)
        entry_frame.pack(fill=tk.X, pady=10)

        entry_label = ttk.Label(
            entry_frame,
            text="Paste your sp_dc cookie value here:",
            font=('Helvetica', 11)
        )
        entry_label.pack(anchor='w', pady=(0, 5))

        cookie_var = tk.StringVar()
        cookie_entry = ttk.Entry(
            entry_frame,
            textvariable=cookie_var,
            width=50,
            font=('Helvetica', 11)
        )
        cookie_entry.pack(fill=tk.X, pady=5)

        save_button = ttk.Button(
            entry_frame,
            text="Connect",
            command=lambda: self._save_cookie(cookie_var.get()),
            style='Accent.TButton'
        )
        save_button.pack(pady=10)

    def _add_help_text(self, container: ttk.Frame) -> None:
        """Add help text to the dialog."""
        help_text = ttk.Label(
            container,
            text="Having trouble? Try logging out of Spotify and back in to get a fresh cookie.",
            font=('Helvetica', 10),
            wraplength=550
        )
        help_text.pack(pady=20)

    def _save_cookie(self, cookie: str) -> None:
        """Handle cookie saving."""
        if cookie.strip():
            self.on_cookie_save(cookie.strip())
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Please enter the SP_DC cookie value.")

class AboutDialog:
    """Dialog for displaying application information."""

    def __init__(self, parent: tk.Tk):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("About Spotify Lyrics Translator")
        self.dialog.geometry("600x650")
        self.dialog.configure(bg='#282828')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Make dialog resizable
        self.dialog.resizable(True, True)
        
        # Center the dialog
        center_window(self.dialog, 600, 650)
        self._init_components()

    def _init_components(self) -> None:
        """Initialize dialog components."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # App Logo
        try:
            # Get the absolute path to the icon file
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                                   'assets', 'app_icon.png')
            
            # Load and resize the image
            image = Image.open(icon_path)
            image = image.resize((128, 128), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Create label with image
            logo_label = ttk.Label(main_frame, image=photo)
            logo_label.image = photo  # Keep a reference to prevent garbage collection
            logo_label.pack(pady=(0, 10))
        except Exception as e:
            print(f"Error loading app icon: {e}")
            # Fallback to text if image loading fails
            logo_label = ttk.Label(
                main_frame,
                text="🎵",
                font=('Helvetica', 48)
            )
            logo_label.pack(pady=(0, 10))

        # App title
        title_label = ttk.Label(
            main_frame,
            text="Spotify Lyrics Translator",
            font=('Helvetica', 20, 'bold'),
            wraplength=500
        )
        title_label.pack(pady=(0, 5))

        # Version
        version_label = ttk.Label(
            main_frame,
            text=f"Version {get_version()}",
            font=('Helvetica', 12),
        )
        version_label.pack(pady=(0, 20))

        self._add_description(main_frame)
        self._add_author_info(main_frame)
        self._add_social_links(main_frame)
        self._add_credits(main_frame)
        self._add_close_button(main_frame)

    def _add_description(self, container: ttk.Frame) -> None:
        """Add application description."""
        desc_label = ttk.Label(
            container,
            text="A powerful desktop application that provides real-time translations of Spotify lyrics while you listen to music. Experience your favorite songs in any language with synchronized translations.",
            font=('Helvetica', 11),
            wraplength=500,
            justify=tk.CENTER
        )
        desc_label.pack(pady=(0, 20))

    def _add_author_info(self, container: ttk.Frame) -> None:
        """Add author information."""
        author_frame = ttk.Frame(container)
        author_frame.pack(fill=tk.X, pady=10)

        # Developer info
        dev_label = ttk.Label(
            author_frame,
            text="Developed by",
            font=('Helvetica', 11)
        )
        dev_label.pack()

        name_label = ttk.Label(
            author_frame,
            text="Mahdi Rashidi",
            font=('Helvetica', 12, 'bold')
        )
        name_label.pack()

    def _add_social_links(self, container: ttk.Frame) -> None:
        """Add social and contact links."""
        links_frame = ttk.Frame(container)
        links_frame.pack(fill=tk.X, pady=10)

        links = [
            ("🌐 Website", "https://notablenomads.com"),
            ("💼 LinkedIn", "https://www.linkedin.com/in/mrdevx/"),
            ("📧 Email", "mailto:m8rashidi@gmail.com"),
            ("🐙 GitHub", "https://github.com/MRdevX/spotify-lyrics-translator")
        ]

        for icon, url in links:
            link_label = ttk.Label(
                links_frame,
                text=icon,
                font=('Helvetica', 11),
                cursor="hand2",
                foreground="#1DB954"
            )
            link_label.pack(pady=2)
            link_label.bind("<Button-1>", lambda e, url=url: webbrowser.open(url))

    def _add_credits(self, container: ttk.Frame) -> None:
        """Add credits information."""
        credits_frame = ttk.Frame(container)
        credits_frame.pack(fill=tk.X, pady=20)

        credits_label = ttk.Label(
            credits_frame,
            text="Built with",
            font=('Helvetica', 12, 'bold'),
        )
        credits_label.pack(pady=(0, 5))

        technologies = [
            ("Spotify API", "https://developer.spotify.com"),
            ("Syrics", "https://github.com/akashrchandran/syrics"),
            ("Deep Translator", "https://github.com/nidhaloff/deep-translator"),
            ("Sun Valley TTK Theme", "https://github.com/rdbende/Sun-Valley-ttk-theme")
        ]

        for tech, url in technologies:
            tech_label = ttk.Label(
                credits_frame,
                text=tech,
                font=('Helvetica', 11),
                cursor="hand2",
                foreground="#1DB954"
            )
            tech_label.pack(pady=2)
            tech_label.bind("<Button-1>", lambda e, url=url: webbrowser.open(url))

    def _add_close_button(self, container: ttk.Frame) -> None:
        """Add close button."""
        close_button = ttk.Button(
            container,
            text="Close",
            command=self.dialog.destroy,
            style='Accent.TButton'
        )
        close_button.pack(pady=20)

        # Copyright notice
        copyright_label = ttk.Label(
            container,
            text="© 2025 Mahdi Rashidi. All rights reserved.",
            font=('Helvetica', 9),
            foreground="#808080"
        )
        copyright_label.pack(pady=(0, 10)) 