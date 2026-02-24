import tkinter as tk
import os
import sys
import logging
import threading
import time
sys.path.append("execution")
from gui_launcher import MusicBotGUI

logging.basicConfig(level=logging.INFO)

root = tk.Tk()
app = MusicBotGUI(root)
app.project_path = "/Users/huseyincoskun/Documents/MusicBot_Workspace/lina_zahara.xlsx"
app.var_run_lyrics.set(True)
app.var_run_music.set(False)
app.var_run_art_prompt.set(False)
app.var_run_art_image.set(False)
app.var_run_video.set(False)
app.var_run_compilation.set(False)
app.selected_songs = {"18ce96dd"}  # Take an ID from lina_zahara.xlsx if known, or just any test ID

def click_start():
    print("----- START PROCESS -----")
    try:
        app.start_process()
        print("----- END START PROCESS (Sync) -----")
    except Exception as e:
        print("CRASH IN START PROCESS:", e)

root.after(1000, click_start)
root.after(5000, root.destroy)
root.mainloop()

