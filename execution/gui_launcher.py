import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext, filedialog
import logging
import time
import threading
import os
import sys
import shutil
import openpyxl
import json
from openpyxl.styles import PatternFill
from browser_controller import BrowserController

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
    def __init__(self, parent, config, app_instance):
        super().__init__(parent)
        self.title("⚙️ Settings")
        self.geometry("450x650") # Larger for tabs
        self.config = config
        self.parent = parent
        self.app = app_instance
        
        # Notebook for Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- TAB 1: General Settings ---
        self.tab_general = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_general, text="General & Defaults")
        
        # Scrollable area for General Tab
        canvas = tk.Canvas(self.tab_general, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_general, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 1. Default Checked Steps
        f_defaults = ttk.LabelFrame(scroll_frame, text="Default Run Steps (Checked on Start)", padding=10)
        f_defaults.pack(fill="x", padx=10, pady=5)
        
        self.var_def_lyrics = tk.BooleanVar(value=config.get("default_run_lyrics", True))
        ttk.Checkbutton(f_defaults, text="1. Lyrics & Prompts", variable=self.var_def_lyrics).pack(anchor="w")
        self.var_def_music = tk.BooleanVar(value=config.get("default_run_music", True))
        ttk.Checkbutton(f_defaults, text="2. Suno Music", variable=self.var_def_music).pack(anchor="w")
        self.var_def_art_p = tk.BooleanVar(value=config.get("default_run_art_prompt", True))
        ttk.Checkbutton(f_defaults, text="3. Art Prompts", variable=self.var_def_art_p).pack(anchor="w")
        self.var_def_art_i = tk.BooleanVar(value=config.get("default_run_art_image", True))
        ttk.Checkbutton(f_defaults, text="4. Cover Images", variable=self.var_def_art_i).pack(anchor="w")

        # 2. Gemini Generation Logic
        f_gemini = ttk.LabelFrame(scroll_frame, text="Gemini Content Logic", padding=10)
        f_gemini.pack(fill="x", padx=10, pady=5)
        
        self.var_lyrics = tk.BooleanVar(value=config.get("gemini_lyrics", True))
        ttk.Checkbutton(f_gemini, text="Generate Lyrics (vs just Title)", variable=self.var_lyrics).pack(anchor="w")
        self.var_style = tk.BooleanVar(value=config.get("gemini_style", True))
        ttk.Checkbutton(f_gemini, text="Generate Music Style", variable=self.var_style).pack(anchor="w")
        self.var_visual = tk.BooleanVar(value=config.get("gemini_visual", True))
        ttk.Checkbutton(f_gemini, text="Generate Visual Prompts", variable=self.var_visual).pack(anchor="w")
        self.var_video = tk.BooleanVar(value=config.get("gemini_video", False))
        ttk.Checkbutton(f_gemini, text="Generate Video Prompts", variable=self.var_video).pack(anchor="w")
        
        # 3. Automation Delays
        f_suno = ttk.LabelFrame(scroll_frame, text="Automation Delays", padding=10)
        f_suno.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(f_suno, text="Suno Gen Delay (s):").pack(anchor="w")
        self.entry_delay = ttk.Entry(f_suno)
        self.entry_delay.insert(0, str(config.get("suno_delay", 15)))
        self.entry_delay.pack(fill="x", pady=2)

        ttk.Label(f_suno, text="Browser Startup Delay (s):").pack(anchor="w")
        self.entry_startup = ttk.Entry(f_suno)
        self.entry_startup.insert(0, str(config.get("startup_delay", 5)))
        self.entry_startup.pack(fill="x", pady=2)
        
        # 4. Language
        f_lang = ttk.LabelFrame(scroll_frame, text="Language & Regional", padding=10)
        f_lang.pack(fill="x", padx=10, pady=5)
        self.combo_lang = ttk.Combobox(f_lang, values=["Turkish", "English", "German", "French", "Spanish", "Italian", "Portuguese"], state="readonly")
        self.combo_lang.set(config.get("target_language", "Turkish"))
        self.combo_lang.pack(fill="x", pady=2)

        # 5. Browser Action
        f_browser = ttk.LabelFrame(scroll_frame, text="Browser Action", padding=10)
        f_browser.pack(fill="x", padx=10, pady=5)
        ttk.Button(f_browser, text="🌐 Open Chrome for Login", command=self.open_chrome).pack(fill="x")

        # --- TAB 2: Master Prompts Editor ---
        self.tab_prompts = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_prompts, text="Master Prompts")
        
        self.prompts_path = os.path.join(os.path.dirname(config.get("metadata_path", "")), "prompts.json")
        
        ttk.Label(self.tab_prompts, text="Lyrics Master Prompt (Gemini):", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.txt_lyrics = scrolledtext.ScrolledText(self.tab_prompts, height=10, wrap=tk.WORD, font=("Consolas", 10))
        self.txt_lyrics.pack(fill="both", expand=True, padx=10, pady=5)
        
        ttk.Label(self.tab_prompts, text="Art Master Prompt (Thumbnail):", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.txt_art = scrolledtext.ScrolledText(self.tab_prompts, height=10, wrap=tk.WORD, font=("Consolas", 10))
        self.txt_art.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.load_prompts_data()

        # Save Button
        f_btn = ttk.Frame(self, padding=10)
        f_btn.pack(fill="x", side="bottom")
        ttk.Button(f_btn, text="💾 Save All Settings & Prompts", command=self.save_settings).pack(fill="x")

    def load_prompts_data(self):
        import json
        if os.path.exists(self.prompts_path):
            try:
                with open(self.prompts_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.txt_lyrics.insert("1.0", data.get("lyrics_master_prompt", ""))
                    self.txt_art.insert("1.0", data.get("art_master_prompt", ""))
            except: pass

    def open_chrome(self):
        self.destroy() 
        self.app.open_chrome_profile()

    def save_settings(self):
        try:
            # 1. Config Object Update
            self.config["gemini_lyrics"] = self.var_lyrics.get()
            self.config["gemini_style"] = self.var_style.get()
            self.config["gemini_visual"] = self.var_visual.get()
            self.config["gemini_video"] = self.var_video.get()
            self.config["suno_delay"] = int(self.entry_delay.get())
            self.config["startup_delay"] = int(self.entry_startup.get())
            self.config["target_language"] = self.combo_lang.get()
            
            # Defaults Config
            self.config["default_run_lyrics"] = self.var_def_lyrics.get()
            self.config["default_run_music"] = self.var_def_music.get()
            self.config["default_run_art_prompt"] = self.var_def_art_p.get()
            self.config["default_run_art_image"] = self.var_def_art_i.get()
            
            # 2. Prompts Data Update
            import json
            prompt_data = {
                "lyrics_master_prompt": self.txt_lyrics.get("1.0", tk.END).strip(),
                "art_master_prompt": self.txt_art.get("1.0", tk.END).strip()
            }
            with open(self.prompts_path, "w", encoding="utf-8") as f:
                json.dump(prompt_data, f, indent=4, ensure_ascii=False)
            
            # 3. Request App Level Save
            # Note: app_instance must have save_settings(config)
            if hasattr(self.app, "save_settings"):
                self.app.save_settings(self.config)
            
            messagebox.showinfo("Success", "Settings and Prompts saved successfully!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

class MusicBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MusicBot Pro Dashboard")
        self.root.geometry("1100x800")
        
        # Configuration (Default Values)
        input_path, _, _ = self.get_data_paths()
        self.config = {
            "gemini_lyrics": True, "gemini_style": True, "gemini_visual": True, "gemini_video": False,
            "suno_delay": 15, "startup_delay": 5,
            "metadata_path": input_path,
            "target_language": "Turkish",
            "default_run_lyrics": True,
            "default_run_music": True,
            "default_run_art_prompt": True,
            "default_run_art_image": True
        }
        self.load_settings()
        
        # Apply Light Theme Styles (Constructs UI)
        self.setup_styles()
        
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
        style.map("Treeview", background=[("selected", accent_color)], foreground=[("selected", "white")])

        # --- LAYOUT ---
        self.setup_ui()
        
    def setup_ui(self):
        # Top Bar
        self.f_top = ttk.Frame(self.root, padding=10)
        self.f_top.pack(fill="x")
        
        ttk.Button(self.f_top, text="⚙️ Settings", command=self.open_settings).pack(side="right", padx=5)
        ttk.Button(self.f_top, text="🔄 Refresh", command=self.load_project_data).pack(side="right", padx=5)
        
        ttk.Label(self.f_top, text="MusicBot Pro", style="Header.TLabel").pack(side="left", padx=5)
        
        # Unified "Load Project" Button
        self.btn_new = ttk.Button(self.f_top, text="✨ New Project", command=self.create_new_project)
        self.btn_new.pack(side="left", padx=5)
        
        self.btn_load = ttk.Button(self.f_top, text="📂 Load Project", command=self.load_project_file)
        self.btn_load.pack(side="left", padx=5)
        
        # Project Status Label
        self.lbl_project = ttk.Label(self.f_top, text="No Project Loaded", font=("Helvetica", 10, "italic"), foreground="gray")
        self.lbl_project.pack(side="left", padx=10)
        
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
        self.log_text.configure(bg="#ffffff", fg="#333333")
        
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

        # Checkboxes for Run Steps
        f_steps = ttk.LabelFrame(self.f_bottom, text="Run Steps", padding=5)
        f_steps.pack(fill="x", pady=5)
        
        self.var_run_lyrics = tk.BooleanVar(value=self.config.get("default_run_lyrics", True))
        self.var_run_music = tk.BooleanVar(value=self.config.get("default_run_music", True))
        self.var_run_art_prompt = tk.BooleanVar(value=self.config.get("default_run_art_prompt", True))
        self.var_run_art_image = tk.BooleanVar(value=self.config.get("default_run_art_image", True))
        
        ttk.Checkbutton(f_steps, text="1. Generate Lyrics & Prompts (Gemini)", variable=self.var_run_lyrics).pack(anchor="w")
        ttk.Checkbutton(f_steps, text="2. Generate Music (Suno)", variable=self.var_run_music).pack(anchor="w")
        ttk.Checkbutton(f_steps, text="3. Generate Art Prompts (Gemini)", variable=self.var_run_art_prompt).pack(anchor="w")
        ttk.Checkbutton(f_steps, text="4. Generate Cover Images (Gemini)", variable=self.var_run_art_image).pack(anchor="w")
        
        self.btn_run = ttk.Button(self.f_bottom, text="▶ START SELECTED", style="Action.TButton", command=self.start_process)
        self.btn_run.pack(fill="x", pady=5)
        
        # Data Cache
        self.all_songs = {} 
        self.filtered_ids = []
        
        # Initial Load
        self.load_project_data() # Load last project or show no project

    def load_settings(self):
        """Loads settings from settings.json in workspace."""
        workspace = os.path.expanduser("~/Documents/MusicBot_Workspace")
        settings_path = os.path.join(workspace, "settings.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                logger.info("✅ Settings loaded from settings.json")
            except Exception as e:
                logger.error(f"Failed to load settings: {e}")

    def save_settings(self, new_config=None):
        """Saves current config to settings.json in workspace."""
        if new_config:
            self.config.update(new_config)
            
        workspace = os.path.expanduser("~/Documents/MusicBot_Workspace")
        os.makedirs(workspace, exist_ok=True)
        settings_path = os.path.join(workspace, "settings.json")
        
        try:
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info("✅ Settings saved to settings.json")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    def update_progress(self, rid, text):
        """Updates the progress text for a specific row ID."""
        if self.tree.exists(rid):
            self.tree.set(rid, "progress", text)
            # Maybe ensure row is visible?
            # self.tree.see(rid)
        
    def open_settings(self):
        # Pass the path to prompts.json for the PromptEditor
        prompts_path = self.get_prompts_path()
        self.config["metadata_path"] = prompts_path # This is a bit of a hack, but PromptEditor expects metadata_path
        SettingsDialog(self.root, self.config, self)

    def create_new_project(self):
        """Creates a new project file from template."""
        
        # 1. Define Workspace
        workspace = os.path.expanduser("~/Documents/MusicBot_Workspace")
        if not os.path.exists(workspace): os.makedirs(workspace)
        
        # 2. Ask User for Filename
        initial_file = f"Project_{int(time.time())}.xlsx"
        path = filedialog.asksaveasfilename(
            initialdir=workspace,
            initialfile=initial_file,
            title="Create New Project",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        
        if not path: return # User cancelled
        
        if not path.endswith(".xlsx"): path += ".xlsx"
        
        # 3. Create File (Using openpyxl directly to be self-contained)
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Music Project"
            
            headers = [
                "id", "prompt", "style", "title", "lyrics", "status", 
                "visual_prompt", "video_prompt", "cover_art_prompt", "cover_art_path"
            ]
            ws.append(headers)
            # Add example row
            ws.append(["EXAMPLE_01", "A happy song about coding", "Pop", "Code Joy", "", "Pending", "", "", "", ""])
            
            wb.save(path)
            logger.info(f"Created new project: {path}")
            
            # 4. Load it immediately
            self.load_project_data(path)
            messagebox.showinfo("Success", "New project created and loaded! 🚀")
            
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            messagebox.showerror("Error", f"Could not create project: {e}")

    def load_project_file(self):
        """Opens file dialog to select a project file."""
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Select Project File",
            filetypes=[("Excel Files", "*.xlsx")],
            initialdir=os.path.expanduser("~/Documents")
        )
        if path:
            self.config["last_project"] = path
            self.load_project_data(path)

    def load_project_data(self, path=None):
        """Loads data from the single project file."""
        if not path:
            path = self.config.get("last_project")
            
        if not path or not os.path.exists(path):
            self.lbl_project.config(text="No Project Loaded", foreground="gray")
            self.all_songs = {}
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.apply_filter() # Clear the treeview
            self.status_var.set("Ready")
            return

        self.project_path = path
        self.lbl_project.config(text=f"📄 {os.path.basename(path)}", foreground="green")
        
        # Ensure Output Logic (Auto-Initialize columns)
        self.ensure_project_structure(path)
        
        # Read Data
        try:
            wb = openpyxl.load_workbook(path, data_only=True)
            ws = wb.active
            headers = {str(cell.value).lower(): i for i, cell in enumerate(ws[1]) if cell.value}
            
            self.all_songs = {}
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            for row in ws.iter_rows(min_row=2, values_only=True):
                # ID Logic
                rid = str(row[headers.get('id', 0)]) if 'id' in headers and row[headers.get('id')] is not None else ""
                
                # Check Prompt/Title
                prompt = ""
                if 'prompt' in headers and row[headers['prompt']] is not None: prompt = str(row[headers['prompt']])
                elif 'title' in headers and row[headers['title']] is not None: prompt = str(row[headers['title']])
                
                style = str(row[headers.get('style', 0)]) if 'style' in headers and row[headers.get('style')] is not None else ""
                
                # Status checks
                has_lyrics = True if 'lyrics' in headers and row[headers['lyrics']] else False
                has_music = True if 'status' in headers and str(row[headers['status']]).lower() in ["completed", "generated"] else False
                has_art = True if 'cover_art_path' in headers and row[headers['cover_art_path']] else False
                
                if rid or prompt:
                    if not rid: rid = f"PENDING_{len(self.all_songs) + 1}" # Generate a temporary ID if missing
                    self.all_songs[rid] = {
                        "id": rid, "title": prompt, "style": style,
                        "lyrics": has_lyrics, "music": has_music, "art": has_art
                    }
            
            self.apply_filter()
            self.status_var.set(f"Loaded {len(self.all_songs)} songs from project.")
            
        except Exception as e:
            logger.error(f"Error loading project: {e}")
            messagebox.showerror("Error", f"Failed to load project: {e}")

    def ensure_project_structure(self, path):
        """Adds missing columns to a raw input file to make it a Project File."""
        try:
            wb = openpyxl.load_workbook(path)
            ws = wb.active
            
            # Map current headers
            headers = {str(cell.value).lower(): cell.column for cell in ws[1] if cell.value}
            
            # Required Columns
            required = [
                "id", "prompt", "style", "title", "lyrics", "status", 
                "visual_prompt", "video_prompt", "cover_art_prompt", "cover_art_path"
            ]
            
            updates = False
            for col in required:
                if col not in headers:
                    new_idx = ws.max_column + 1
                    ws.cell(row=1, column=new_idx, value=col)
                    headers[col] = new_idx
                    updates = True
            
            if updates:
                wb.save(path)
                logger.info(f"Project structure initialized for {os.path.basename(path)}")
        except Exception as e:
            logger.error(f"Structure init error: {e}")

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
        # --- Pre-flight Checks 🛡️ ---
        if not self.project_path:
            logger.error("❌ No Project Loaded! Please Load or Create a project.")
            messagebox.showerror("Error", "Please load a project file first.")
            return

        # Check input file existence
        # self.project_path is the unified file (e.g. .../MusicBot_Workspace/ProjeX/ProjeX.xlsx)
        if not os.path.exists(self.project_path):
             logger.error(f"❌ Project file not found: {self.project_path}")
             return

        # Check if at least one step is selected
        if not any([self.var_run_lyrics.get(), self.var_run_music.get(), self.var_run_art_prompt.get(), self.var_run_art_image.get()]):
            logger.error("❌ No steps selected! Please check at least one 'Run Step'.")
            messagebox.showwarning("Warning", "Please select at least one step to run.")
            return

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
            # Unified Project Path
            project_file = self.project_path
            output_media = os.path.join(os.path.dirname(project_file), "output_media")
            if not os.path.exists(output_media): os.makedirs(output_media)
            
            def progress_callback(rid, text):
                if rid == "global":
                    self.status_var.set(text)
                else:
                    self.root.after(0, lambda: self.update_progress(rid, text))

            # Process EACH song ID individually with a fresh browser session if needed
            # Or group them but isolate the high-risk steps
            
            for idx, song_id in enumerate(target_ids):
                # Update status
                self.root.after(0, lambda: self.status_var.set(f"Processing Song {idx+1}/{len(target_ids)} (ID: {song_id})"))
                
                from browser_controller import BrowserController
                # Start a fresh browser for this specific song to prevent state buildup/timeout issues
                song_browser = BrowserController(headless=False)
                
                try:
                    song_browser.start()
                    
                    # --- Step 1: Lyrics ---
                    if self.var_run_lyrics.get():
                        from gemini_prompter import GeminiPrompter
                        gemini = GeminiPrompter(
                            project_file=project_file, # Unified Path
                            browser=song_browser,
                            use_gemini_lyrics=self.config.get("gemini_lyrics", True),
                            generate_visual=self.config.get("gemini_visual", True),
                            generate_video=self.config.get("gemini_video", False),
                            generate_style=self.config.get("gemini_style", False),
                            startup_delay=self.config.get("startup_delay", 5),
                            language=self.config.get("target_language", "Turkish")
                        )
                        gemini.run(target_ids=[song_id], progress_callback=progress_callback)

                    # --- Step 2: Music ---
                    if self.var_run_music.get():
                        from suno_generator import SunoGenerator
                        suno = SunoGenerator(
                            project_file=project_file, # Unified Path
                            output_dir=output_media,
                            delay=self.config.get("suno_delay", 15),
                            startup_delay=self.config.get("startup_delay", 5),
                            browser=song_browser
                        )
                        suno.run(target_ids=[song_id], progress_callback=progress_callback)
                    
                    # --- Step 3: Art (Prompts & Images) ---
                    # Note: Art usually benefits from batching to avoid closing/opening browser too much,
                    # but here we do it per-song to ensure isolation.
                    if self.var_run_art_prompt.get() or self.var_run_art_image.get():
                        from gemini_prompter import GeminiPrompter
                        gemini_art = GeminiPrompter(
                            project_file=project_file, # Unified Path
                            browser=song_browser,
                            startup_delay=self.config.get("startup_delay", 5),
                            language=self.config.get("target_language", "Turkish")
                        )
                        
                        if self.var_run_art_prompt.get():
                            gemini_art.generate_art_prompts(target_ids=[song_id], progress_callback=progress_callback)
                        
                        if self.var_run_art_image.get():
                            gemini_art.generate_art_images(target_ids=[song_id], progress_callback=progress_callback)

                except Exception as e:
                    logger.error(f"Error processing {song_id}: {e}")
                    progress_callback(song_id, "Error in flow ❌")
                finally:
                    # Safe Shutdown
                    try:
                        time.sleep(2)
                        song_browser.stop()
                    except: pass

            self.root.after(0, lambda: messagebox.showinfo("Done", "Selected tasks completed!"))
            self.root.after(0, self.load_project_data) # Refresh UI

        except Exception as e:
            logger.error(f"Critical Process Error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Critical Error", str(e)))
        finally:
            self.root.after(0, self.enable_buttons)
            self.load_data()



    def get_prompts_path(self):
        """Returns the path to prompts.json in the workspace, initializing it if needed."""
        workspace = os.path.expanduser("~/Documents/MusicBot_Workspace")
        os.makedirs(workspace, exist_ok=True)
        prompts_path = os.path.join(workspace, "prompts.json")
        
        if not os.path.exists(prompts_path):
            # Try to migrate from old location
            old_path = os.path.join(os.getcwd(), "data", "prompts.json")
            if os.path.exists(old_path):
                import shutil
                shutil.copy(old_path, prompts_path)
            else:
                # Fallback default
                try:
                    import json
                    with open(prompts_path, "w", encoding="utf-8") as f:
                         json.dump({
                            "lyrics_master_prompt": "Sen profesyonel bir şarkı sözü yazarı ve müzik prodüktörüsün...",
                            "art_master_prompt": "Create a high-quality YouTube music thumbnail..."
                        }, f, indent=4)
                except: pass
        return prompts_path

    def get_data_paths(self):
        docs_dir = os.path.expanduser("~/Documents/MusicBot_Workspace")
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

    def open_chrome_profile(self):
        """Launches a headless=False browser for manual login."""
        
        def _launch():
            try:
                # 1. Notify User via Log
                logger.info("Initializing Chrome for Login...")
                logger.info("Please wait, browser is starting...")
                                    
                # 2. Start
                # Store in self to prevent Garbage Collection from closing it immediately
                self.chrome_session = BrowserController(headless=False)
                self.chrome_session.start()
                
                logger.info("✅ Chrome started successfully!")
                logger.info(f"📂 Profile Path: {self.chrome_session.user_data_dir}")
                logger.info("👉 Please log in to Suno/Gemini now.")
                logger.info("👉 You can close the browser window when finished.")
                
                # 3. Open Tabs
                try:
                    page = self.chrome_session.pages.get("default")
                    if page:
                        page.goto("https://suno.com/create")
                        # New tab for gemini
                        p2 = self.chrome_session.context.new_page()
                        p2.goto("https://gemini.google.com/app")
                except: pass
                
            except Exception as e:
                import traceback
                err = traceback.format_exc()
                logger.error(f"❌ Failed to open browser: {e}")
                logger.error(err)

        # Threads
        threading.Thread(target=_launch, daemon=True).start()

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
