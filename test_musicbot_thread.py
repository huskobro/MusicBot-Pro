import tkinter as tk
import os
import sys
sys.path.append("execution")
from gui_launcher import MusicBotGUI

def test_start():
    root = tk.Tk()
    app = MusicBotGUI(root)
    app.project_path = "test_project.xlsx"
    with open("test_project.xlsx", "w") as f: f.write("test")
    app.var_run_lyrics.set(True)
    app.target_ids = ["test1"]
    
    print("Setting up test...")
    def run_thread_test():
        print("Calling start_process...")
        try:
            app.selected_songs = {"test1"}
            app.start_process()
            print("called start_process")
        except Exception as e:
            print("Error in start_process:", e)
        
    root.after(1000, run_thread_test)
    root.after(3000, root.destroy)
    root.mainloop()

test_start()
