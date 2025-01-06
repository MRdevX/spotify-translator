import sys

# Check Python version before anything else
if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
    print("""
Error: This application requires Python 3.11

Please install Python 3.11 and set up the environment:

macOS:
    brew install python@3.11
    brew install python-tk@3.11
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Then run the application again.
    """)
    sys.exit(1)

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    print("""
Error: Tkinter is not installed!

Please install Python 3.11 and Tkinter:

macOS:
    brew install python@3.11
    brew install python-tk@3.11

Ubuntu/Debian:
    sudo apt-get install python3.11-tk

Fedora:
    sudo dnf install python3.11-tkinter
    """)
    exit(1)

from deep_translator import GoogleTranslator
from syrics.api import Spotify
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
import os
import sv_ttk
import webbrowser
import json

# Constants
CONFIG_FILE = 'config.json'
CACHE_FILE = 'lyrics_cache.pkl'
MAX_CACHE_SIZE = 1000

class SpotifyLyricsTranslator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Spotify Lyrics Translator")
        self.sp = None
        self.setup_gui()
        
    def setup_gui(self):
        # Initialize the authentication first
        sp_dc = self.load_or_get_spotify_cookie()
        if sp_dc:
            try:
                self.sp = Spotify(sp_dc)
                self.sp.get_current_song()  # Test the connection
                self.initialize_main_gui()
            except Exception as e:
                messagebox.showerror("Error", f"Authentication failed: {str(e)}")
                self.show_spotify_login_dialog()
        else:
            self.show_spotify_login_dialog()

    def load_or_get_spotify_cookie(self):
        """Load SP_DC cookie from config file"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return config.get('sp_dc')
            except Exception:
                return None
        return None

    def show_spotify_login_dialog(self):
        """Show dialog with instructions to get SP_DC cookie"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Spotify Authentication")
        dialog.geometry("700x600")
        dialog.configure(bg='#282828')  # Spotify's dark theme
        dialog.transient(self.root)
        dialog.grab_set()

        # Make dialog resizable
        dialog.resizable(True, True)
        
        # Center the dialog on screen
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Connect to Spotify",
            font=('Helvetica', 16, 'bold'),
            wraplength=600
        )
        title_label.pack(pady=(0, 20))

        # Step by step instructions with icons
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

        # Create frame for steps
        steps_frame = ttk.Frame(main_frame)
        steps_frame.pack(fill=tk.BOTH, padx=20, pady=10)

        for step in steps:
            step_label = ttk.Label(
                steps_frame,
                text=step,
                font=('Helvetica', 11),
                wraplength=550
            )
            step_label.pack(anchor='w', pady=5)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)

        def open_spotify():
            webbrowser.open('https://open.spotify.com')

        # Open Spotify button with icon
        open_button = ttk.Button(
            button_frame,
            text="Open Spotify",
            command=open_spotify,
            style='Accent.TButton'
        )
        open_button.pack(pady=10)

        # Cookie entry frame
        entry_frame = ttk.Frame(main_frame)
        entry_frame.pack(fill=tk.X, pady=10)

        # Label for cookie entry
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

        def save_cookie():
            sp_dc = cookie_var.get().strip()
            if sp_dc:
                try:
                    # Test the cookie
                    self.sp = Spotify(sp_dc)
                    
                    # Try to get current song to verify authentication
                    try:
                        current_song = self.sp.get_current_song()
                        if current_song:
                            print("Successfully retrieved current song")
                        else:
                            raise Exception("Could not retrieve current song")
                    except Exception as song_error:
                        print(f"Error getting current song: {str(song_error)}")
                        raise Exception(f"Could not verify Spotify connection: {str(song_error)}")
                    
                    # Save to config if valid
                    config_dir = os.path.dirname(CONFIG_FILE)
                    if config_dir:
                        os.makedirs(config_dir, exist_ok=True)
                    
                    with open(CONFIG_FILE, 'w') as f:
                        json.dump({'sp_dc': sp_dc}, f)
                    
                    print("Successfully saved cookie to config file")
                    dialog.destroy()
                    self.initialize_main_gui()
                except Exception as e:
                    error_message = f"""
Authentication Error

Please check:
• You're logged into Spotify in your browser
• You copied the entire cookie value
• The cookie is fresh (try logging out and back in)

Technical details: {str(e)}
"""
                    print(f"Authentication error: {str(e)}")
                    messagebox.showerror("Authentication Failed", error_message)
            else:
                messagebox.showerror("Error", "Please enter the SP_DC cookie value.")

        # Save button with accent style
        save_button = ttk.Button(
            entry_frame,
            text="Connect",
            command=save_cookie,
            style='Accent.TButton'
        )
        save_button.pack(pady=10)

        # Help text
        help_text = ttk.Label(
            main_frame,
            text="Having trouble? Try logging out of Spotify and back in to get a fresh cookie.",
            font=('Helvetica', 10),
            wraplength=550
        )
        help_text.pack(pady=20)

    def initialize_main_gui(self):
        """Initialize the main application GUI"""
        # Configure the window with app name
        self.root.title("Spotify Lyrics Translator")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        
        # Apply theme and styles
        style = ttk.Style(self.root)
        sv_ttk.set_theme("dark")
        
        # Configure custom styles
        style.configure(
            "Song.TLabel",
            font=('Helvetica', 14, 'bold'),
            foreground='#1DB954'  # Spotify green
        )
        style.configure(
            "Info.TLabel",
            font=('Helvetica', 10),
            foreground='#B3B3B3'  # Spotify light gray
        )
        
        # Configure Treeview style with column dividers
        style.configure(
            "Treeview",
            font=('Helvetica', 11),
            rowheight=30,
            background='#282828',
            foreground='#FFFFFF',
            fieldbackground='#282828',
            borderwidth=0,  # Remove default borders
            dividerwidth=2,  # Add custom divider width
            dividercolor='#404040'  # Divider color
        )
        
        style.configure(
            "Treeview.Heading",
            font=('Helvetica', 12, 'bold'),
            background='#1DB954',
            foreground='white'
        )
        
        # Configure selection colors
        style.map(
            'Treeview',
            background=[('selected', '#1DB954')],  # Spotify green for selected item
            foreground=[('selected', 'white')]
        )

        # Create tooltip
        self.tooltip = None
        
        # Create right-click menu for column management
        self.column_menu = tk.Menu(self.root, tearoff=0)
        self.column_menu.add_command(label="Reset Column Widths", command=self.reset_column_widths)
        
        # Main container with animation frame
        self.animation_frame = ttk.Frame(self.root)
        self.animation_frame.pack(fill=tk.BOTH, expand=True)
        
        main_container = ttk.Frame(self.animation_frame, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Song info frame
        song_info_frame = ttk.Frame(main_container)
        song_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left side: Song info
        song_details_frame = ttk.Frame(song_info_frame)
        song_details_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Song title and artist
        self.song_label = ttk.Label(
            song_details_frame,
            text="Loading...",
            style="Song.TLabel"
        )
        self.song_label.pack(anchor='w')
        
        # Album name
        self.album_label = ttk.Label(
            song_details_frame,
            text="",
            style="Info.TLabel"
        )
        self.album_label.pack(anchor='w')
        
        # Right side: Time info
        time_frame = ttk.Frame(song_info_frame)
        time_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Current/Total time
        self.time_label = ttk.Label(
            time_frame,
            text="0:00 / 0:00",
            style="Info.TLabel"
        )
        self.time_label.pack(anchor='e')
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_container,
            variable=self.progress_var,
            mode='determinate',
            style="Spotify.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Configure progress bar style
        style.configure(
            "Spotify.Horizontal.TProgressbar",
            troughcolor='#404040',
            background='#1DB954',
            darkcolor='#1DB954',
            lightcolor='#1DB954'
        )

        # Create frame for Treeview and Scrollbar
        tree_frame = ttk.Frame(main_container)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create and configure Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Time", "Original Lyrics", "Translated Lyrics"),
            show="headings",
            style="Treeview"
        )
        
        # Enable column resizing
        for col in ("Time", "Original Lyrics", "Translated Lyrics"):
            self.tree.heading(col, text=col, anchor='w')
            self.tree.column(col, stretch=True)  # Allow column stretching
        
        # Store original column widths
        self.default_widths = {
            "Time": 60,
            "Original Lyrics": 350,
            "Translated Lyrics": 350
        }
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack Treeview and Scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events AFTER creating the methods
        self.tree.bind('<Motion>', self.show_tooltip)
        self.tree.bind('<Leave>', self.hide_tooltip)
        self.tree.bind('<Button-3>', self.show_column_menu)  # Right-click menu
        
        # Status bar
        self.status_bar = ttk.Label(
            main_container,
            text="Ready",
            font=('Helvetica', 10),
            anchor='w'
        )
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Initialize other variables
        self.current_song_id = None
        self.translation_complete = False
        self.translated_lyrics_cache = None
        self.language = ""
        
        # Load cache
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'rb') as f:
                self.lyrics_cache = pickle.load(f)
        else:
            self.lyrics_cache = {}
        
        # Start update loop
        self.root.after(500, self.update_display)

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def save_cache(self):
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(self.lyrics_cache, f)

    def get_current_playback_position(self):
        try:
            current_song = self.sp.get_current_song()
            position_ms = current_song['progress_ms']
            return current_song, position_ms
        except Exception as e:
            print(f"Error fetching current song playback position: {e}")
            return None, 0

    def update_display(self):
        current_song, current_position = self.get_current_playback_position()
        if current_song:
            song_id = current_song['item']['id']
            song_name = current_song['item']['name']
            artist_name = current_song['item']['artists'][0]['name']
            album_name = current_song['item']['album']['name']
            duration = current_song['item']['duration_ms']
            is_playing = current_song['is_playing']
            
            # Update song info
            song_display = f"{song_name} - {artist_name}"
            self.song_label.config(text=song_display)
            self.album_label.config(text=album_name)
            
            # Update time and progress
            current_time = self.ms_to_min_sec(current_position)
            total_time = self.ms_to_min_sec(duration)
            self.time_label.config(text=f"{current_time} / {total_time}")
            
            # Update progress bar
            progress_percent = (current_position / duration) * 100
            self.progress_var.set(progress_percent)
            
            # Update lyrics if song changed
            if song_id != self.current_song_id:
                self.current_song_id = song_id
                self.update_lyrics()
            
            # Update currently playing line in lyrics
            self.update_current_lyric(current_position)
        else:
            # No song is playing
            self.song_label.config(text="No song playing")
            self.album_label.config(text="")
            self.time_label.config(text="0:00 / 0:00")
            self.progress_var.set(0)
        
        self.root.after(500, self.update_display)

    def update_current_lyric(self, current_position):
        """Update the currently playing lyric in the tree view"""
        last_index = None
        for item in self.tree.get_children():
            item_data = self.tree.item(item)
            start_time = int(item_data['values'][0].split(":")[0]) * 60000 + int(item_data['values'][0].split(":")[1]) * 1000
            if start_time <= current_position:
                last_index = item
            else:
                break
        if last_index:
            self.tree.selection_set(last_index)
            self.tree.see(last_index)

    def ms_to_min_sec(self, ms):
        """Convert milliseconds to MM:SS format"""
        ms = int(ms)
        minutes = ms // 60000
        seconds = (ms % 60000) // 1000
        return f"{minutes}:{seconds:02d}"

    def translate_line(self, translator, line):
        original_text = line['words']
        try:
            translated_text = translator.translate(original_text)
        except Exception as e:
            print(f"Error translating '{original_text}': {e}")
            translated_text = original_text
        return {'startTimeMs': line['startTimeMs'], 'words': original_text, 'translated': translated_text}

    def translate_words(self, lyrics, song_name, song_id, callback):
        translator = GoogleTranslator(source='auto', target='en')
        translated_song_name = translator.translate(song_name)
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.translate_line, translator, line) for line in lyrics]
            translated_lyrics = [future.result() for future in as_completed(futures)]
        self.lyrics_cache[song_id] = translated_lyrics

        if len(self.lyrics_cache) > MAX_CACHE_SIZE:
            self.lyrics_cache.pop(next(iter(self.lyrics_cache)))

        self.save_cache()
        callback(translated_lyrics)
        self.translation_complete = True

    def update_lyrics(self):
        current_song = self.sp.get_current_song()
        song_id = current_song['item']['id']
        song_name = current_song['item']['name']
        artist_name = current_song['item']['artists'][0]['name']
        lyrics = self.sp.get_lyrics(song_id)
        lyrics_data = lyrics['lyrics']['lines'] if lyrics and 'lyrics' in lyrics and 'lines' in lyrics['lyrics'] else None

        # Update song label with current song info
        song_display = f"{song_name} - {artist_name}"
        self.song_label.config(text=song_display)
        
        self.tree.delete(*self.tree.get_children())

        if lyrics_data:
            detected_lang = lyrics['lyrics']['language']
            self.language = detected_lang
            self.tree.heading("Original Lyrics", text=f"Original Lyrics ({detected_lang})")

            for lyric in lyrics_data:
                self.tree.insert("", "end", values=(self.ms_to_min_sec(lyric['startTimeMs']), lyric['words'], ""))
            self.translation_complete = False
            if song_id in self.lyrics_cache:
                self.update_translations(self.lyrics_cache[song_id])
            else:
                threading.Thread(target=self.translate_words, 
                              args=(lyrics_data, song_name, song_id, self.update_translations)).start()
        else:
            self.tree.insert("", "end", values=("0:00", "(No lyrics available)", ""))
        self.adjust_column_widths()

    def update_translations(self, translated_lyrics):
        for item in self.tree.get_children():
            item_data = self.tree.item(item)
            start_time = item_data['values'][0]
            original_lyrics = item_data['values'][1]
            for lyric in translated_lyrics:
                if self.ms_to_min_sec(lyric['startTimeMs']) == start_time and lyric['words'] == original_lyrics:
                    self.tree.set(item, column="Translated Lyrics", value=lyric['translated'])
                    break
        if self.tree.get_children():
            first_item = self.tree.get_children()[0]
            self.tree.set(first_item, column="Translated Lyrics", value=translated_lyrics[0]['translated'])
        self.adjust_column_widths()

    def adjust_column_widths(self):
        """Adjust column widths with animation"""
        min_time_width = 60
        max_original_length = 0
        max_translated_length = 0
        line_count = 0

        for item in self.tree.get_children():
            line_count += 1
            original_length = len(self.tree.item(item)['values'][1])
            translated_length = len(self.tree.item(item)['values'][2])
            if original_length > max_original_length:
                max_original_length = original_length
            if translated_length > max_translated_length:
                max_translated_length = translated_length

        self.root.update_idletasks()
        width = self.tree.winfo_reqwidth()

        # Calculate widths based on content
        orig_length = max_original_length * 15
        trans_length = max_translated_length * 15

        # Adjust for different languages
        if self.language == "ja":
            orig_length = max_original_length * 23
        if self.language == "ru":
            orig_length = max_original_length * 18
            trans_length = max_translated_length * 19

        # Get window width
        window_width = self.root.winfo_width()
        available_width = window_width - min_time_width - 50  # Account for scrollbar and padding

        # Calculate proportional widths
        total_content = orig_length + trans_length
        if total_content > 0:
            orig_ratio = orig_length / total_content
            trans_ratio = trans_length / total_content
            
            orig_width = int(available_width * orig_ratio)
            trans_width = int(available_width * trans_ratio)
        else:
            orig_width = available_width // 2
            trans_width = available_width // 2

        # Set minimum widths
        orig_width = max(200, orig_width)
        trans_width = max(200, trans_width)

        # Animate the resizing
        for col, (old_width, new_width) in {
            "Time": (self.tree.column("Time")['width'], min_time_width),
            "Original Lyrics": (self.tree.column("Original Lyrics")['width'], orig_width),
            "Translated Lyrics": (self.tree.column("Translated Lyrics")['width'], trans_width)
        }.items():
            if abs(old_width - new_width) > 5:  # Only animate if change is significant
                self.smooth_resize(col, old_width, new_width)
            else:
                self.tree.column(col, width=new_width)

        # Update window height
        height = line_count * 30 + 100
        self.root.geometry(f"{window_width}x{height}")

    def on_window_resize(self, event=None):
        """Handle window resize event"""
        if event.widget == self.root:
            self.adjust_column_widths()

    def show_tooltip(self, event):
        """Show tooltip for truncated text"""
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        if item and column:
            col_idx = int(column[1]) - 1
            values = self.tree.item(item)['values']
            if col_idx < len(values):
                cell_value = str(values[col_idx])
                
                # Get cell width
                col_width = self.tree.column(self.tree.heading(column)['text'])['width']
                text_width = self.tree.tk.call('font', 'measure', self.tree.cget('font'), cell_value)
                
                # Show tooltip only if text is truncated
                if text_width > col_width:
                    if self.tooltip:
                        self.tooltip.destroy()
                    
                    x, y, _, _ = self.tree.bbox(item, column)
                    x += self.tree.winfo_rootx()
                    y += self.tree.winfo_rooty()
                    
                    self.tooltip = tk.Toplevel(self.tree)
                    self.tooltip.wm_overrideredirect(True)
                    
                    label = ttk.Label(
                        self.tooltip,
                        text=cell_value,
                        background='#282828',
                        foreground='white',
                        padding=5
                    )
                    label.pack()
                    
                    self.tooltip.geometry(f"+{x}+{y+25}")

    def hide_tooltip(self, event=None):
        """Hide the tooltip"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def show_column_menu(self, event):
        """Show right-click menu for column management"""
        self.column_menu.post(event.x_root, event.y_root)

    def reset_column_widths(self):
        """Reset columns to default widths"""
        for col, width in self.default_widths.items():
            self.tree.column(col, width=width)
        self.adjust_column_widths()

    def smooth_resize(self, column, start_width, end_width, steps=10):
        """Animate column resizing"""
        if steps <= 0:
            self.tree.column(column, width=end_width)
            return
        
        current_width = start_width + (end_width - start_width) * (1 - steps/10)
        self.tree.column(column, width=int(current_width))
        
        self.root.after(20, lambda: self.smooth_resize(column, start_width, end_width, steps-1))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SpotifyLyricsTranslator()
    app.run()
