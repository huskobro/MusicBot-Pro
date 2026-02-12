import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import logging
import time
import threading
import os
import sys
import openpyxl
from openpyxl.styles import PatternFill

# Configure logging
# We will configure basic stdout logging here, but the GUI will add its own handler later.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

class GuiLogger(logging.Handler):
    """Custom logging handler that directs logs to a ScrolledText widget."""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.text_widget.tag_config("INFO", foreground="black")
        self.text_widget.tag_config("ERROR", foreground="red")
        self.text_widget.tag_config("WARNING", foreground="orange")

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n', record.levelname)
            self.text_widget.configure(state='disabled')
            self.text_widget.yview(tk.END)
        
        # Ensure thread safety by scheduling update on main loop
        self.text_widget.after(0, append)

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.title("⚙️ Settings")
        self.geometry("350x300")
        self.config = config
        self.parent = parent
        
        # Gemini Settings
        f_gemini = ttk.LabelFrame(self, text="Gemini Settings", padding=10)
        f_gemini.pack(fill="x", padx=10, pady=5)
        
        self.var_lyrics = tk.BooleanVar(value=config.get("gemini_lyrics", True))
        ttk.Checkbutton(f_gemini, text="Generate Lyrics", variable=self.var_lyrics).pack(anchor="w")
        
        self.var_style = tk.BooleanVar(value=config.get("gemini_style", True))
        ttk.Checkbutton(f_gemini, text="Generate Music Style", variable=self.var_style).pack(anchor="w")
        
        self.var_visual = tk.BooleanVar(value=config.get("gemini_visual", True))
        ttk.Checkbutton(f_visual := ttk.Frame(f_gemini), text="Generate Visual Prompts", variable=self.var_visual).pack(anchor="w")
        
        self.var_video = tk.BooleanVar(value=config.get("gemini_video", False))
        ttk.Checkbutton(f_gemini, text="Generate Video Prompts", variable=self.var_video).pack(anchor="w")
        
        # Suno Settings
        f_suno = ttk.LabelFrame(self, text="Automation Settings", padding=10)
        f_suno.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(f_suno, text="Suno Gen Delay (s):").pack(anchor="w")
        self.entry_delay = ttk.Entry(f_suno)
        self.entry_delay.insert(0, str(config.get("suno_delay", 15)))
        self.entry_delay.pack(fill="x", pady=2)

        ttk.Label(f_suno, text="Browser Startup Delay (s):").pack(anchor="w")
        self.entry_startup = ttk.Entry(f_suno)
        self.entry_startup.insert(0, str(config.get("startup_delay", 5)))
        self.entry_startup.pack(fill="x", pady=2)
        
        # Prompts
        f_prompts = ttk.LabelFrame(self, text="Master Prompts", padding=10)
        f_prompts.pack(fill="x", padx=10, pady=5)
        ttk.Button(f_prompts, text="📝 Edit Master Prompts", command=self.open_prompt_editor).pack(fill="x")
        
        # Language Settings
        f_lang = ttk.LabelFrame(self, text="Language & Regional", padding=10)
        f_lang.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(f_lang, text="Target Lyrics Language:").pack(anchor="w")
        self.combo_lang = ttk.Combobox(f_lang, values=["Turkish", "English", "German", "French", "Spanish", "Italian", "Portuguese"], state="readonly")
        self.combo_lang.set(config.get("target_language", "Turkish"))
        self.combo_lang.pack(fill="x", pady=2)

        # Buttons
        f_btn = ttk.Frame(self, padding=10)
        f_btn.pack(fill="x", side="bottom")
        ttk.Button(f_btn, text="Save & Close", command=self.save_settings).pack(fill="x")

    def open_prompt_editor(self):
        PromptEditor(self, self.config.get("metadata_path", "data/input_songs.xlsx"))

    def save_settings(self):
        try:
            self.config["gemini_lyrics"] = self.var_lyrics.get()
            self.config["gemini_style"] = self.var_style.get()
            self.config["gemini_visual"] = self.var_visual.get()
            self.config["gemini_video"] = self.var_video.get()
            self.config["suno_delay"] = int(self.entry_delay.get())
            self.config["startup_delay"] = int(self.entry_startup.get())
            self.config["target_language"] = self.combo_lang.get()
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for delay.")

class PromptEditor(tk.Toplevel):
    def __init__(self, parent, metadata_path):
        super().__init__(parent)
        self.title("📝 Edit Master Prompts")
        self.geometry("600x600")
        self.prompts_path = os.path.join(os.path.dirname(metadata_path), "prompts.json")
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.txt_lyrics = self._add_tab("Lyrics Prompt")
        self.txt_art = self._add_tab("Art Prompt")
        
        self.load_prompts()
        
        ttk.Button(self, text="Save Prompts", command=self.save_prompts).pack(pady=10)
        
    def _add_tab(self, title):
        f = ttk.Frame(self.notebook)
        self.notebook.add(f, text=title)
        txt = scrolledtext.ScrolledText(f, wrap=tk.WORD, font=("Consolas", 10))
        txt.pack(fill="both", expand=True, padx=5, pady=5)
        return txt

    def load_prompts(self):
        import json
        if os.path.exists(self.prompts_path):
            try:
                with open(self.prompts_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.txt_lyrics.insert("1.0", data.get("lyrics_master_prompt", ""))
                    self.txt_art.insert("1.0", data.get("art_master_prompt", ""))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load prompts: {e}")

    def save_prompts(self):
        import json
        data = {
            "lyrics_master_prompt": self.txt_lyrics.get("1.0", tk.END).strip(),
            "art_master_prompt": self.txt_art.get("1.0", tk.END).strip()
        }
        try:
            with open(self.prompts_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Success", "Prompts saved successfully!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save prompts: {e}")

class MusicBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MusicBot Pro Dashboard")
        self.root.geometry("1100x800")
        
        # Apply Light Theme Styles
        self.setup_styles()
        
        # Configuration (Default Values)
        input_path, _, _ = self.get_data_paths()
        self.config = {
            "gemini_lyrics": True, "gemini_style": True, "gemini_visual": True, "gemini_video": False,
            "suno_delay": 15, "startup_delay": 5,
            "metadata_path": input_path,
            "target_language": "Turkish"
        }
        
        # --- STYLES ---
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam") # Clam supports color customization better
        
        # Colors
        bg_color = "#f0f2f5"
        accent_color = "#4a90e2" 
        text_color = "#333333"
        white = "#ffffff"
        
        self.root.configure(bg=bg_color)
        
        # General
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=text_color, font=("Helvetica", 11))
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), foreground="#1a1a1a")
        style.configure("TLabelframe", background=bg_color, borderwidth=1)
        style.configure("TLabelframe.Label", background=bg_color, foreground=text_color, font=("Helvetica", 10, "bold"))
        
        # Buttons
        style.configure("TButton", font=("Helvetica", 10), padding=6, borderwidth=1, focuscolor="none")
        style.map("TButton", background=[("active", "#e1e4e8")])
        style.configure("Action.TButton", font=("Helvetica", 11, "bold"), background=white, foreground=accent_color)
        
        # Treeview
        style.configure("Treeview", 
                        background=white, 
                        foreground=text_color, 
                        fieldbackground=white, 
                        rowheight=30, 
                        font=("Helvetica", 10))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), background="#e1e4e8")
        style.map("Treeview", background=[("selected", accent_color)], foreground=[("selected", white)])

        # --- LAYOUT ---
        
        # Top Bar
        self.f_top = ttk.Frame(self.root, padding=10)
        self.f_top.pack(fill="x")
        
        ttk.Button(self.f_top, text="⚙️ Settings", command=self.open_settings).pack(side="right", padx=5)
        ttk.Button(self.f_top, text="🔄 Refresh", command=self.load_data).pack(side="right", padx=5)
        
        ttk.Label(self.f_top, text="MusicBot Pro", style="Header.TLabel").pack(side="left", padx=5)
        ttk.Button(self.f_top, text="📂 Input", command=lambda: self.open_xlsx("input")).pack(side="left", padx=5)
        ttk.Button(self.f_top, text="📂 Output", command=lambda: self.open_xlsx("output")).pack(side="left", padx=2)
        ttk.Button(self.f_top, text="🖼️ Images", command=self.open_image_folder).pack(side="left", padx=2)

        # Filter
        self.f_filter = ttk.Frame(self.root, padding="5 0 5 0")
        self.f_filter.pack(fill="x", padx=10)
        ttk.Label(self.f_filter, text="🔍 Search:").pack(side="left")
        self.filter_var = tk.StringVar()
        self.filter_var.trace("w", self.apply_filter)
        ttk.Entry(self.f_filter, textvariable=self.filter_var).pack(side="left", fill="x", expand=True, padx=5)

        # Main Table
        self.f_tree = ttk.Frame(self.root)
        self.f_tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Columns: Add Style
        columns = ("sel", "id", "title", "style", "progress", "lyrics", "music", "art")
        self.tree = ttk.Treeview(self.f_tree, columns=columns, show="headings", selectmode="extended")
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.selected_songs = set() # Track manually checked songs
        
        # Setup Columns
        self.tree.heading("sel", text="✔")
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Title / Prompt")
        self.tree.heading("style", text="Style")
        self.tree.heading("progress", text="Status & Progress")
        self.tree.heading("lyrics", text="Lyrics")
        self.tree.heading("music", text="Music")
        self.tree.heading("art", text="Art")
        
        self.tree.column("sel", width=40, anchor="center")
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("title", width=200)
        self.tree.column("style", width=120)
        self.tree.column("progress", width=200, anchor="w") 
        self.tree.column("lyrics", width=50, anchor="center")
        self.tree.column("music", width=50, anchor="center")
        self.tree.column("art", width=50, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.f_tree, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        
        # Setup Checkbox Logic (using tags or images is hard in standard Treeview without icons)
        # Using Selection Event instead of checkboxes for now as standard Treeview doesn't support native checkboxes easily
        # But we can add a column for selection status if needed. 
        # Multi-select is enabled by default.
        
        # --- LOG CONSOLE ---
        self.f_log = ttk.LabelFrame(self.root, text="📜 Activity Log", padding=5)
        self.f_log.pack(fill="x", padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(self.f_log, height=8, state='disabled', font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True)
        self.log_text.configure(bg=white, fg=text_color)
        
        # Connect Logger
        self.gui_handler = GuiLogger(self.log_text)
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')
        self.gui_handler.setFormatter(formatter)
        logging.getLogger().addHandler(self.gui_handler)
        # Also add to root logger to catch libraries
        logging.getLogger().addHandler(self.gui_handler)

        # --- CONTROLS ---
        self.f_bottom = ttk.LabelFrame(self.root, text="🚀 Execution", padding=10)
        self.f_bottom.pack(fill="x", padx=10, pady=10, side="bottom")
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.f_bottom, textvariable=self.status_var, font=("Helvetica", 10, "italic")).pack(side="bottom", anchor="w")

        f_steps = ttk.Frame(self.f_bottom)
        f_steps.pack(fill="x", pady=5)
        
        ttk.Label(f_steps, text="Run Steps:").pack(side="left")
        self.var_run_lyrics = tk.BooleanVar(value=True)
        ttk.Checkbutton(f_steps, text="1. Lyrics", variable=self.var_run_lyrics).pack(side="left", padx=5)
        self.var_run_music = tk.BooleanVar(value=True)
        ttk.Checkbutton(f_steps, text="2. Music", variable=self.var_run_music).pack(side="left", padx=5)
        
        self.var_run_art_prompt = tk.BooleanVar(value=True)
        ttk.Checkbutton(f_steps, text="3a. Art Prompts", variable=self.var_run_art_prompt).pack(side="left", padx=5)
        
        self.var_run_art_image = tk.BooleanVar(value=True)
        ttk.Checkbutton(f_steps, text="3b. Art Images", variable=self.var_run_art_image).pack(side="left", padx=5)
        
        self.btn_run = ttk.Button(self.f_bottom, text="▶ START SELECTED", style="Action.TButton", command=self.start_process)
        self.btn_run.pack(fill="x", pady=5)
        
        # Data Cache
        self.all_songs = {} 
        self.filtered_ids = []
        
        # Initial Load
        self.load_data()

    def update_progress(self, rid, text):
        """Updates the progress text for a specific row ID."""
        if self.tree.exists(rid):
            self.tree.set(rid, "progress", text)
            # Maybe ensure row is visible?
            # self.tree.see(rid)
        
    def open_settings(self):
        SettingsDialog(self.root, self.config)

    def load_data(self):
        """Loads and merges data from Input and Output excels."""
        input_path, output_path, _ = self.get_data_paths()
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.all_songs = {} 
        
        # 1. Read Input (Prompts & Styles)
        if os.path.exists(input_path):
            try:
                wb = openpyxl.load_workbook(input_path, data_only=True)
                ws = wb.active
                headers = {str(cell.value).lower(): i for i, cell in enumerate(ws[1]) if cell.value}
                
                for row in ws.iter_rows(min_row=2, values_only=True):
                    rid = str(row[headers.get('id', 0)]) if 'id' in headers and row[headers.get('id')] else ""
                    prompt = row[headers.get('prompt', 0)] if 'prompt' in headers else ""
                    style = row[headers.get('style', 0)] if 'style' in headers else ""
                    
                    if rid or prompt: # Valid row
                        if not rid: rid = "PENDING..."
                        self.all_songs[rid] = {
                            "id": rid, "title": prompt, "style": style,
                            "lyrics": False, "music": False, "art": False
                        }
            except Exception as e:
                logger.error(f"Error reading input: {e}")

        # 2. Read Output
        if os.path.exists(output_path):
            try:
                wb = openpyxl.load_workbook(output_path, data_only=True)
                ws = wb.active
                headers = {str(cell.value).lower(): i for i, cell in enumerate(ws[1]) if cell.value}
                
                for row in ws.iter_rows(min_row=2, values_only=True):
                    rid = str(row[headers.get('id', 0)]) if 'id' in headers and row[headers.get('id')] else ""
                    
                    if rid in self.all_songs:
                        if 'title' in headers and row[headers['title']]:
                            self.all_songs[rid]["title"] = row[headers['title']]
                        
                        has_lyrics = False
                        if 'lyrics' in headers and row[headers['lyrics']]: has_lyrics = True
                        
                        has_music = False
                        if 'status' in headers and str(row[headers['status']]).lower() in ["completed", "generated"]: has_music = True
                        
                        has_art = False
                        if 'cover_art_path' in headers and row[headers['cover_art_path']]: has_art = True
                        
                        self.all_songs[rid]["lyrics"] = has_lyrics
                        self.all_songs[rid]["music"] = has_music
                        self.all_songs[rid]["art"] = has_art

            except Exception as e:
                logger.error(f"Error reading output: {e}")

        self.apply_filter()

    def apply_filter(self, *args):
        query = self.filter_var.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.filtered_ids = []
        
        for rid, s in self.all_songs.items():
            if query and query not in s["title"].lower() and query not in rid.lower():
                continue
                
            self.filtered_ids.append(rid)
            
            # Symbols
            s_lyrics = "✅" if s["lyrics"] else "⚪"
            s_music = "✅" if s["music"] else "⚪"
            s_art = "✅" if s["art"] else "⚪"
            s_sel = "☑️" if rid in self.selected_songs else "☐"
            
            # Progress Logic
            done_cnt = sum([s["lyrics"], s["music"], s["art"]])
            prog_text = f"In Progress ({done_cnt}/3)" if done_cnt < 3 else "Completed! 🎉"
            if done_cnt == 0: prog_text = "Idle"

            self.tree.insert("", "end", iid=rid, values=(
                s_sel, s["id"], s["title"], s.get("style", ""), prog_text, s_lyrics, s_music, s_art
            ))
            
        self.status_var.set(f"Loaded {len(self.filtered_ids)} songs.")

    def on_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#1": # 'sel' column
                item_id = self.tree.identify_row(event.y)
                if item_id:
                    if item_id in self.selected_songs:
                        self.selected_songs.remove(item_id)
                        self.tree.set(item_id, "sel", "☐")
                    else:
                        self.selected_songs.add(item_id)
                        self.tree.set(item_id, "sel", "☑️")
                    return "break" # Prevent selection change if clicking checkbox

    def start_process(self):
        # 1. Use manual checkboxes if any
        target_ids = list(self.selected_songs)
        
        # 2. If no checkboxes, use tree selection
        if not target_ids:
            selected_items = self.tree.selection()
            if selected_items:
                target_ids = list(selected_items)
            else:
                # If filter is active and nothing selected, ask to process all filtered
                if messagebox.askyesno("Confirm", "No songs selected. Process ALL listed songs?"):
                    target_ids = self.filtered_ids
        
        if not target_ids:
            return

        self.disable_buttons()
        threading.Thread(target=self.run_process, args=(target_ids,), daemon=True).start()

    def run_process(self, target_ids):
        try:
            input_xlsx, output_xlsx, output_media = self.get_data_paths()
            
            def progress_callback(rid, text):
                if rid == "global":
                    self.status_var.set(text)
                else:
                    self.root.after(0, lambda: self.update_progress(rid, text))

            # Process EACH song ID individually with a fresh browser session if needed
            # Or group them but isolate the high-risk steps
            
            for idx, song_id in enumerate(target_ids):
                self.status_var.set(f"Processing Song {idx+1}/{len(target_ids)} (ID: {song_id})")
                
                from browser_controller import BrowserController
                # Start a fresh browser for this specific song to prevent state buildup/timeout issues
                song_browser = BrowserController(headless=False)
                
                try:
                    song_browser.start()
                    
                    # 1. Gemini
                    if self.var_run_lyrics.get():
                        from gemini_prompter import GeminiPrompter
                        prompter = GeminiPrompter(
                            metadata_path=input_xlsx, # Keep input_xlsx as it's the source for prompts
                            output_path=output_xlsx,
                            headless=False,
                            use_gemini_lyrics=self.config["gemini_lyrics"],
                            generate_visual=self.config["gemini_visual"],
                            generate_video=self.config["gemini_video"],
                            generate_style=self.config["gemini_style"],
                            startup_delay=self.config["startup_delay"], # Changed from .get with default
                            language=self.config.get("target_language", "Turkish"), # Added new argument
                            browser=song_browser
                        )
                        prompter.run(max_count=1, target_ids=[song_id], progress_callback=progress_callback)

                    # 2. Suno
                    if self.var_run_music.get():
                        from suno_generator import SunoGenerator
                        suno = SunoGenerator(
                            metadata_path=output_xlsx, 
                            output_dir=output_media, 
                            delay=5, # Reduced internal delay as we restart browser
                            startup_delay=self.config.get("startup_delay", 2),
                            browser=song_browser
                        )
                        suno.run(max_count=1, target_ids=[song_id], progress_callback=progress_callback)

                    # 3. Art Prompt
                    if self.var_run_art_prompt.get():
                        from gemini_prompter import GeminiPrompter
                        gemini_art = GeminiPrompter(output_path=output_xlsx, headless=False, browser=song_browser)
                        gemini_art.generate_art_prompts(max_count=1, target_ids=[song_id], progress_callback=progress_callback)

                    # 4. Art Image
                    if self.var_run_art_image.get():
                        from gemini_prompter import GeminiPrompter
                        gemini_art_img = GeminiPrompter(output_path=output_xlsx, headless=False, browser=song_browser)
                        gemini_art_img.generate_art_images(max_count=1, target_ids=[song_id], progress_callback=progress_callback)

                except Exception as song_err:
                    logger.error(f"Error on song {song_id}: {song_err}")
                    progress_callback(song_id, f"Error: {song_err} ❌")
                finally:
                    # NEW: Lifecycle delay to ensure media saves complete fully
                    time.sleep(5)
                    song_browser.stop()
                    time.sleep(2) # Brief cooldown between songs
            
            self.status_var.set("Batch Finished! 🎉")
            messagebox.showinfo("Success", f"Finished {len(target_ids)} songs.")
            
        except Exception as e:
            logger.error(f"Batch Process error: {e}")
            messagebox.showerror("Complete Failure", f"The entire process stopped: {e}")
        finally:
            self.enable_buttons()
            self.load_data()


    def get_data_paths(self):
        if getattr(sys, 'frozen', False):
            docs_dir = os.path.expanduser("~/Documents/MusicBot_Data")
            bundle_dir = sys._MEIPASS
        else:
            docs_dir = os.path.join(os.getcwd(), "data")
            bundle_dir = os.getcwd()
            
        os.makedirs(docs_dir, exist_ok=True)
        
        input_path = os.path.join(docs_dir, "input_songs.xlsx")
        output_path = os.path.join(docs_dir, "output_results.xlsx")
        output_dir = os.path.join(docs_dir, "output_media")
        prompts_path = os.path.join(docs_dir, "prompts.json")
        
        # Init prompts.json if missing
        if not os.path.exists(prompts_path):
            # Try to find default prompts in bundle or source
            bundle_prompts = os.path.join(bundle_dir, "data", "prompts.json") if getattr(sys, 'frozen', False) else os.path.join("data", "prompts.json")
            if os.path.exists(bundle_prompts):
                import shutil
                shutil.copy(bundle_prompts, prompts_path)
            else:
                # Fallback: Create with basic defaults if bundle also missing
                try:
                    import json
                    with open(prompts_path, "w", encoding="utf-8") as f:
                        json.dump({
                            "lyrics_master_prompt": "Sen profesyonel bir şarkı sözü yazarı ve müzik prodüktörüsün...",
                            "art_master_prompt": "Create a high-quality YouTube music thumbnail..."
                        }, f, indent=4)
                except: pass

        # Init Input if missing
        if not os.path.exists(input_path):
            try:
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.append(["id", "prompt", "style"])
                wb.save(input_path)
            except: pass
            
        return input_path, output_path, output_dir

    def open_xlsx(self, type="input"):
        input_path, output_path, _ = self.get_data_paths()
        path = input_path if type == "input" else output_path
        if os.path.exists(path):
            os.system(f"open '{path}'")
        else:
            messagebox.showinfo("Wait", "File not created yet.")

    def open_image_folder(self):
        _, output_path, _ = self.get_data_paths()
        img_dir = os.path.join(os.path.dirname(output_path), "images")
        if not os.path.exists(img_dir):
            os.makedirs(img_dir, exist_ok=True)
        os.system(f"open '{img_dir}'")

    def disable_buttons(self):
        self.btn_run.config(state="disabled")

    def enable_buttons(self):
        self.root.after(0, lambda: self.btn_run.config(state="normal"))
        self.root.after(0, lambda: self.status_var.set("Ready"))
        self.root.after(0, lambda: self.load_data()) # Auto refresh

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = MusicBotGUI(root)
        root.mainloop()
    except Exception as e:
        with open("CRASH_LOG.txt", "w") as f:
            import traceback
            f.write(str(e) + "\n" + traceback.format_exc())
