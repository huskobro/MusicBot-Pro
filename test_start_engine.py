import tkinter as tk
import os
import sys
sys.path.append("execution")
from execution.gui_launcher import MusicBotGUI

def test_start():
    root = tk.Tk()
    app = MusicBotGUI(root)
    # mock things
    app.project_path = "test_project.xlsx"
    with open("test_project.xlsx", "w") as f:
        f.write("test")
    # try start process
    print("starting process..")
    try:
        app.start_process()
        print("start_process completed without hard crash.")
    except Exception as e:
        print("CRASHED:", e)
    root.destroy()

test_start()
