import logging
import os
import sys

# Configure logging IMMEDIATELY to catch all imports and initializations.
workspace = os.path.expanduser("~/Documents/MusicBot_Workspace")
if not os.path.exists(workspace): os.makedirs(workspace)
debug_log_path = os.path.join(workspace, "musicbot_debug.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(debug_log_path, encoding='utf-8', mode='a')
    ],
    force=True
)
logger = logging.getLogger(__name__)

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext, filedialog
import time
import threading
import shutil
import openpyxl
import json
from openpyxl.styles import PatternFill
from browser_controller import BrowserController

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
        self.geometry("800x750") # Widened to ensure all tabs and columns are visible
        self.config = config
        self.parent = parent
        self.app = app_instance
        
        # Notebook for Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # --- TAB 0: Artist Profiles (NEW) ---
        self.tab_presets = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_presets, text="Artist Profiles")
        
        f_presets = ttk.LabelFrame(self.tab_presets, text="Artist Identity & Preset Management", padding=10)
        f_presets.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. Preset Selection
        ttk.Label(f_presets, text="Active Profile:").grid(row=0, column=0, sticky="w", pady=5)
        self.presets = config.get("artist_presets", {}) # Dict: {Alias: Data}
        self.combo_preset_select = ttk.Combobox(f_presets, values=list(self.presets.keys()), state="readonly")
        self.combo_preset_select.grid(row=0, column=1, sticky="ew", pady=5)
        
        # 2. Profile Alias (for saving)
        ttk.Label(f_presets, text="Preset Alias:").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_preset_alias = ttk.Entry(f_presets)
        self.ent_preset_alias.grid(row=1, column=1, sticky="ew", pady=5)

        # 3. Artist Name
        ttk.Label(f_presets, text="Artist Name:").grid(row=2, column=0, sticky="w", pady=5)
        self.ent_artist_name = ttk.Entry(f_presets)
        self.ent_artist_name.insert(0, config.get("artist_name", ""))
        self.ent_artist_name.grid(row=2, column=1, sticky="ew", pady=5)

        # 4. Artist Style
        ttk.Label(f_presets, text="Artist Music Style:").grid(row=3, column=0, sticky="w", pady=5)
        self.ent_artist_style = ttk.Entry(f_presets)
        self.ent_artist_style.insert(0, config.get("artist_style", ""))
        self.ent_artist_style.grid(row=3, column=1, sticky="ew", pady=5)

        # Buttons
        f_preset_btns = ttk.Frame(f_presets)
        f_preset_btns.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(f_preset_btns, text="💾 Save Current as Preset", command=self.save_preset).pack(side="left", padx=5)
        ttk.Button(f_preset_btns, text="📂 Load Selected", command=self.load_preset).pack(side="left", padx=5)
        ttk.Button(f_preset_btns, text="🗑️ Delete Selected", command=self.delete_preset).pack(side="left", padx=5)

        f_presets.columnconfigure(1, weight=1)
        
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

        # --- TAB 1.5: Advanced Suno ---
        self.tab_adv_suno = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_adv_suno, text="Advanced Suno")
        
        f_adv_suno = ttk.LabelFrame(self.tab_adv_suno, text="Music Generation Parameters", padding=10)
        f_adv_suno.pack(fill="both", expand=True, padx=10, pady=10)


        # Persona Profile Section
        self.var_persona_link_enabled = tk.BooleanVar(value=config.get("suno_persona_link_enabled", False))
        ttk.Checkbutton(f_adv_suno, text="Enable Persona Profile:", variable=self.var_persona_link_enabled).grid(row=1, column=0, sticky="w", pady=2)
        
        # Frame for Persona Manager
        f_persona_mgr = ttk.Frame(f_adv_suno)
        f_persona_mgr.grid(row=1, column=1, sticky="ew", pady=2)
        
        # Load Personas
        self.personas = config.get("suno_personas", {}) # Dict: {Alias: Link}
        self.active_persona_alias = config.get("suno_active_persona", "")
        
        # Combobox for Selection
        self.combo_persona_select = ttk.Combobox(f_persona_mgr, values=list(self.personas.keys()), state="readonly")
        self.combo_persona_select.pack(side="top", fill="x", pady=(0, 2))
        if self.active_persona_alias in self.personas:
            self.combo_persona_select.set(self.active_persona_alias)
        
        # Profile Management Area
        f_pm_controls = ttk.Frame(f_persona_mgr)
        f_pm_controls.pack(side="top", fill="x")
        
        ttk.Label(f_pm_controls, text="Alias:").pack(side="left")
        self.ent_pm_alias = ttk.Entry(f_pm_controls, width=10)
        self.ent_pm_alias.pack(side="left", padx=2)
        
        ttk.Label(f_pm_controls, text="Link:").pack(side="left")
        self.ent_pm_link = ttk.Entry(f_pm_controls, width=15)
        self.ent_pm_link.pack(side="left", padx=2)
        
        ttk.Button(f_pm_controls, text="+", width=3, command=self.add_persona).pack(side="left", padx=2)
        ttk.Button(f_pm_controls, text="-", width=3, command=self.delete_persona).pack(side="left", padx=2)

        # 2. Vocal Gender
        self.var_gender_enabled = tk.BooleanVar(value=config.get("vocal_gender_enabled", False))
        ttk.Checkbutton(f_adv_suno, text="Enable Vocal Gender:", variable=self.var_gender_enabled).grid(row=2, column=0, sticky="w", pady=2)
        self.combo_gender = ttk.Combobox(f_adv_suno, values=["Default", "None", "Male", "Female"], state="readonly")
        self.combo_gender.set(config.get("vocal_gender", "Default"))
        self.combo_gender.grid(row=2, column=1, sticky="ew", pady=2)

        # 3. Audio Influence (%)
        self.var_audio_enabled = tk.BooleanVar(value=config.get("audio_influence_enabled", False))
        ttk.Checkbutton(f_adv_suno, text="Enable Audio Influence (%):", variable=self.var_audio_enabled).grid(row=3, column=0, sticky="w", pady=2)
        self.scale_audio = tk.Scale(f_adv_suno, from_=10, to_=90, orient="horizontal")
        self.scale_audio.set(config.get("audio_influence", 25))
        self.scale_audio.grid(row=3, column=1, sticky="ew", pady=2)

        # 4. Weirdness
        self.var_weird_enabled = tk.BooleanVar(value=config.get("weirdness_enabled", False))
        ttk.Checkbutton(f_adv_suno, text="Enable Weirdness:", variable=self.var_weird_enabled).grid(row=4, column=0, sticky="w", pady=2)
        self.scale_weird = tk.Scale(f_adv_suno, from_=1, to_=1000, orient="horizontal")
        self.scale_weird.set(50 if config.get("weirdness") == "Default" else int(config.get("weirdness", 50)))
        self.scale_weird.grid(row=4, column=1, sticky="ew", pady=2)

        # 5. Style Influence
        self.var_style_enabled = tk.BooleanVar(value=config.get("style_influence_enabled", False))
        ttk.Checkbutton(f_adv_suno, text="Enable Style Influence:", variable=self.var_style_enabled).grid(row=5, column=0, sticky="w", pady=2)
        self.scale_style = tk.Scale(f_adv_suno, from_=1, to_=100, orient="horizontal")
        self.scale_style.set(50 if config.get("style_influence") == "Default" else int(config.get("style_influence", 50)))
        self.scale_style.grid(row=5, column=1, sticky="ew", pady=2)

        # 6. Lyrics Mode
        self.var_lyrics_mode_enabled = tk.BooleanVar(value=config.get("lyrics_mode_enabled", False))
        ttk.Checkbutton(f_adv_suno, text="Enable Lyrics Mode:", variable=self.var_lyrics_mode_enabled).grid(row=6, column=0, sticky="w", pady=2)
        self.combo_lyrics_mode = ttk.Combobox(f_adv_suno, values=["Default", "Manual", "Auto"], state="readonly")
        self.combo_lyrics_mode.set(config.get("lyrics_mode", "Default"))
        self.combo_lyrics_mode.grid(row=6, column=1, sticky="ew", pady=2)

        f_adv_suno.columnconfigure(1, weight=1)

        # --- TAB 2: Master Prompts Editor ---
        self.tab_prompts = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_prompts, text="Master Prompts")
        
        # Scrollable area for Prompts Tab
        p_canvas = tk.Canvas(self.tab_prompts, borderwidth=0, highlightthickness=0)
        p_scrollbar = ttk.Scrollbar(self.tab_prompts, orient="vertical", command=p_canvas.yview)
        p_scroll_frame = ttk.Frame(p_canvas)
        
        p_scroll_frame.bind(
            "<Configure>",
            lambda e: p_canvas.configure(scrollregion=p_canvas.bbox("all"))
        )
        p_canvas.create_window((0, 0), window=p_scroll_frame, anchor="nw")
        p_canvas.configure(yscrollcommand=p_scrollbar.set)
        
        p_canvas.pack(side="left", fill="both", expand=True)
        p_scrollbar.pack(side="right", fill="y")
        
        self.prompts_path = os.path.join(os.path.dirname(config.get("metadata_path", "")), "prompts.json")
        
        # Lyrics
        ttk.Label(p_scroll_frame, text="1. Lyrics Master Prompt (Gemini):", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.txt_lyrics = scrolledtext.ScrolledText(p_scroll_frame, height=8, wrap=tk.WORD, font=("Consolas", 10))
        self.txt_lyrics.pack(fill="x", padx=10, pady=5)
        
        # Visual
        ttk.Label(p_scroll_frame, text="2. Visual Master Prompt (Midjourney Style):", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.txt_visual = scrolledtext.ScrolledText(p_scroll_frame, height=8, wrap=tk.WORD, font=("Consolas", 10))
        self.txt_visual.pack(fill="x", padx=10, pady=5)
        
        # Video
        ttk.Label(p_scroll_frame, text="3. Video Master Prompt (Sora/Runway):", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.txt_video = scrolledtext.ScrolledText(p_scroll_frame, height=8, wrap=tk.WORD, font=("Consolas", 10))
        self.txt_video.pack(fill="x", padx=10, pady=5)
        
        # Art (Thumbnail)
        ttk.Label(p_scroll_frame, text="4. Art Master Prompt (YouTube Thumbnail):", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.txt_art = scrolledtext.ScrolledText(p_scroll_frame, height=8, wrap=tk.WORD, font=("Consolas", 10))
        self.txt_art.pack(fill="x", padx=10, pady=5)
        
        self.load_prompts_data()

        # Save Button
        f_btn = ttk.Frame(self, padding=10)
        f_btn.pack(fill="x", side="bottom")
        ttk.Button(f_btn, text="💾 Save All Settings & Prompts", command=self.save_settings).pack(fill="x")

    # --- Preset Methods ---
    def save_preset(self):
        alias = self.ent_preset_alias.get().strip()
        if not alias:
            messagebox.showwarning("Warning", "Please enter a Preset Alias name.")
            return
        
        # Capture current prompts
        prompts = {
            "lyrics_master_prompt": self.txt_lyrics.get("1.0", tk.END).strip(),
            "visual_master_prompt": self.txt_visual.get("1.0", tk.END).strip(),
            "video_master_prompt": self.txt_video.get("1.0", tk.END).strip(),
            "art_master_prompt": self.txt_art.get("1.0", tk.END).strip()
        }
        
        # Capture all configurable settings
        settings_snapshot = {
            "gemini_lyrics": self.var_lyrics.get(),
            "gemini_style": self.var_style.get(),
            "gemini_visual": self.var_visual.get(),
            "gemini_video": self.var_video.get(),
            "suno_delay": self.entry_delay.get(),
            "startup_delay": self.entry_startup.get(),
            "target_language": self.combo_lang.get(),
            "artist_name": self.ent_artist_name.get(),
            "artist_style": self.ent_artist_style.get(),
            "vocal_gender": self.combo_gender.get(),
            "vocal_gender_enabled": self.var_gender_enabled.get(),
            "audio_influence": self.scale_audio.get(),
            "audio_influence_enabled": self.var_audio_enabled.get(),
            "weirdness": self.scale_weird.get(),
            "weirdness_enabled": self.var_weird_enabled.get(),
            "style_influence": self.scale_style.get(),
            "style_influence_enabled": self.var_style_enabled.get(),
            "lyrics_mode": self.combo_lyrics_mode.get(),
            "lyrics_mode_enabled": self.var_lyrics_mode_enabled.get(),
            "suno_persona_link_enabled": self.var_persona_link_enabled.get(),
            "suno_active_persona": self.combo_persona_select.get()
        }
        
        self.presets[alias] = {
            "settings": settings_snapshot,
            "prompts": prompts
        }
        self.update_preset_combo()
        self.combo_preset_select.set(alias)
        messagebox.showinfo("Success", f"Preset '{alias}' saved successfully!")

    def load_preset(self):
        alias = self.combo_preset_select.get()
        if not alias or alias not in self.presets:
            return
        
        data = self.presets[alias]
        settings = data.get("settings", {})
        prompts = data.get("prompts", {})
        
        # Apply settings to UI
        self.var_lyrics.set(settings.get("gemini_lyrics", True))
        self.var_style.set(settings.get("gemini_style", True))
        self.var_visual.set(settings.get("gemini_visual", True))
        self.var_video.set(settings.get("gemini_video", False))
        
        self.entry_delay.delete(0, tk.END)
        self.entry_delay.insert(0, settings.get("suno_delay", "15"))
        self.entry_startup.delete(0, tk.END)
        self.entry_startup.insert(0, settings.get("startup_delay", "5"))
        self.combo_lang.set(settings.get("target_language", "Turkish"))
        
        self.ent_artist_name.delete(0, tk.END)
        self.ent_artist_name.insert(0, settings.get("artist_name", ""))
        self.ent_artist_style.delete(0, tk.END)
        self.ent_artist_style.insert(0, settings.get("artist_style", ""))
        
        self.combo_gender.set(settings.get("vocal_gender", "Default"))
        self.var_gender_enabled.set(settings.get("vocal_gender_enabled", False))
        self.scale_audio.set(settings.get("audio_influence", 25))
        self.var_audio_enabled.set(settings.get("audio_influence_enabled", False))
        self.scale_weird.set(settings.get("weirdness", 50))
        self.var_weird_enabled.set(settings.get("weirdness_enabled", False))
        self.scale_style.set(settings.get("style_influence", 50))
        self.var_style_enabled.set(settings.get("style_influence_enabled", False))
        self.combo_lyrics_mode.set(settings.get("lyrics_mode", "Default"))
        self.var_lyrics_mode_enabled.set(settings.get("lyrics_mode_enabled", False))
        
        self.var_persona_link_enabled.set(settings.get("suno_persona_link_enabled", False))
        self.combo_persona_select.set(settings.get("suno_active_persona", ""))
        
        # Apply prompts to UI
        self.txt_lyrics.delete("1.0", tk.END)
        self.txt_lyrics.insert("1.0", prompts.get("lyrics_master_prompt", ""))
        self.txt_visual.delete("1.0", tk.END)
        self.txt_visual.insert("1.0", prompts.get("visual_master_prompt", ""))
        self.txt_video.delete("1.0", tk.END)
        self.txt_video.insert("1.0", prompts.get("video_master_prompt", ""))
        self.txt_art.delete("1.0", tk.END)
        self.txt_art.insert("1.0", prompts.get("art_master_prompt", ""))
        
        self.ent_preset_alias.delete(0, tk.END)
        self.ent_preset_alias.insert(0, alias)
        
        messagebox.showinfo("Success", f"Preset '{alias}' loaded!")

    def delete_preset(self):
        alias = self.combo_preset_select.get()
        if alias and alias in self.presets:
            if messagebox.askyesno("Confirm", f"Delete preset '{alias}'?"):
                del self.presets[alias]
                self.update_preset_combo()
                self.combo_preset_select.set('')
                self.ent_preset_alias.delete(0, tk.END)

    def update_preset_combo(self):
        self.combo_preset_select['values'] = list(self.presets.keys())

    def load_prompts_data(self):
        import json
        if os.path.exists(self.prompts_path):
            try:
                with open(self.prompts_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.txt_lyrics.insert("1.0", data.get("lyrics_master_prompt", ""))
                    self.txt_visual.insert("1.0", data.get("visual_master_prompt", ""))
                    self.txt_video.insert("1.0", data.get("video_master_prompt", ""))
                    self.txt_art.insert("1.0", data.get("art_master_prompt", ""))
            except: pass

    def add_persona(self):
        alias = self.ent_pm_alias.get().strip()
        link = self.ent_pm_link.get().strip()
        if alias and link:
            self.personas[alias] = link
            self.update_persona_combo()
            self.combo_persona_select.set(alias)
            self.ent_pm_alias.delete(0, tk.END)
            self.ent_pm_link.delete(0, tk.END)

    def delete_persona(self):
        selection = self.combo_persona_select.get()
        if selection and selection in self.personas:
            del self.personas[selection]
            self.update_persona_combo()
            self.combo_persona_select.set('')

    def update_persona_combo(self):
        self.combo_persona_select['values'] = list(self.personas.keys())

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
            self.config["artist_name"] = self.ent_artist_name.get()
            self.config["artist_style"] = self.ent_artist_style.get()
            self.config["artist_presets"] = self.presets
            self.config["active_preset"] = self.combo_preset_select.get()
            
            # Defaults Config
            self.config["default_run_lyrics"] = self.var_def_lyrics.get()
            self.config["default_run_music"] = self.var_def_music.get()
            self.config["default_run_art_prompt"] = self.var_def_art_p.get()
            self.config["default_run_art_image"] = self.var_def_art_i.get()
            
            # Suno Advanced
            self.config["suno_persona_link_enabled"] = self.var_persona_link_enabled.get()
            self.config["suno_personas"] = self.personas
            self.config["suno_active_persona"] = self.combo_persona_select.get()
            
            self.config["vocal_gender"] = self.combo_gender.get()
            self.config["vocal_gender_enabled"] = self.var_gender_enabled.get()
            self.config["audio_influence"] = self.scale_audio.get()
            self.config["audio_influence_enabled"] = self.var_audio_enabled.get()
            self.config["weirdness"] = self.scale_weird.get()
            self.config["weirdness_enabled"] = self.var_weird_enabled.get()
            self.config["style_influence"] = self.scale_style.get()
            self.config["style_influence_enabled"] = self.var_style_enabled.get()
            self.config["lyrics_mode"] = self.combo_lyrics_mode.get()
            self.config["lyrics_mode_enabled"] = self.var_lyrics_mode_enabled.get()
            
            # 2. Prompts Data Update
            import json
            prompt_data = {
                "lyrics_master_prompt": self.txt_lyrics.get("1.0", tk.END).strip(),
                "visual_master_prompt": self.txt_visual.get("1.0", tk.END).strip(),
                "video_master_prompt": self.txt_video.get("1.0", tk.END).strip(),
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
            "default_run_art_image": True,
            # Suno Advanced Options
            # Suno Advanced Options
            "audio_influence": 25,
            "vocal_gender": "Default",
            "lyrics_mode": "Default",
            "weirdness": "Default",
            "style_influence": "Default",
            "artist_name": "",
            "artist_style": "",
            "artist_presets": {},
            "active_preset": "",
            # Enabled Flags
            "weirdness_enabled": False,
            "style_influence_enabled": False,
            "vocal_gender_enabled": False,
            "audio_influence_enabled": False
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
                "visual_prompt", "video_prompt", "suno_style", "cover_art_prompt", "cover_art_path"
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

    def _check_existing_data(self, target_ids):
        """Checks if any of the target songs already have data in the requested steps."""
        try:
            wb = openpyxl.load_workbook(self.project_path, data_only=True)
            ws = wb.active
            headers = {str(cell.value).lower(): i for i, cell in enumerate(ws[1]) if cell.value}
            
            lyrics_col = headers.get('lyrics')
            visual_col = headers.get('visual_prompt')
            video_col = headers.get('video_prompt')
            id_col = headers.get('id', 0)
            
            for row in ws.iter_rows(min_row=2, values_only=True):
                rid = str(row[id_col]) if row[id_col] is not None else ""
                if rid in target_ids:
                    # Check if user wants lyrics AND they exist
                    if self.var_run_lyrics.get() and lyrics_col is not None and row[lyrics_col]:
                        return True
                    # Check if user wants visuals AND they exist
                    if self.config.get("gemini_visual", True) and visual_col is not None and row[visual_col]:
                        # Note: we check config because var_run_lyrics usually triggers the sequential run
                        return True
                    # Check if user wants videos AND they exist
                    if self.config.get("gemini_video", False) and video_col is not None and row[video_col]:
                        return True
            return False
        except:
            return False

    def run_process(self, target_ids):
        try:
            # Check for existing data if we are running Gemini steps
            force_update = False
            if self.var_run_lyrics.get():
                has_data = self._check_existing_data(target_ids)
                if has_data:
                    # Ask user if they want to re-generate
                    if messagebox.askyesno("Yeniden Üret?", "Bazı satırlarda zaten veri (Söz, Prompt vb.) mevcut.\n\nBunları yeniden üretmek ister misiniz?\n\n'Evet' derseniz veriler güncellenir, 'Hayır' derseniz sadece eksikler tamamlanır."):
                        force_update = True

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
                        gemini.run(target_ids=[song_id], progress_callback=progress_callback, force_update=force_update)

                    # --- Step 2: Music ---
                    if self.var_run_music.get():
                        from suno_generator import SunoGenerator
                        suno = SunoGenerator(
                            project_file=project_file, # Unified Path
                            output_dir=output_media,
                            delay=self.config.get("suno_delay", 15),
                            startup_delay=self.config.get("startup_delay", 5),
                            browser=song_browser,
                            audio_influence=self.config.get("audio_influence", 25) if self.config.get("audio_influence_enabled") else "Default",
                            vocal_gender=self.config.get("vocal_gender", "Default") if self.config.get("vocal_gender_enabled") else "Default",
                            weirdness=self.config.get("weirdness", 50) if self.config.get("weirdness_enabled") else "Default",
                            style_influence=self.config.get("style_influence", 50) if self.config.get("style_influence_enabled") else "Default",
                            lyrics_mode=self.config.get("lyrics_mode", "Default") if self.config.get("lyrics_mode_enabled") else "Default",
                            persona_link=self.config.get("suno_personas", {}).get(self.config.get("suno_active_persona", ""), "") if self.config.get("suno_persona_link_enabled") else ""
                        )
                        suno.run(target_ids=[song_id], progress_callback=progress_callback, force_update=force_update)
                    
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
