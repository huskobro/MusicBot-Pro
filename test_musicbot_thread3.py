import tkinter as tk
import os
import sys
import logging
import threading
import time

logging.basicConfig(level=logging.INFO)

root = tk.Tk()

def run_process(target_ids, force_update):
    print("INSIDE RUN PROCESS THREAD!")
    print(f"target_ids: {target_ids}, force_update: {force_update}")

def btn_click():
    print("Button clicked")
    try:
        target_ids = ["test1"]
        force_update = False
        print("Starting thread...")
        threading.Thread(target=run_process, args=(target_ids, force_update), daemon=True).start()
        print("Thread started call finished.")
    except Exception as e:
        print("ERROR:", e)

btn = tk.Button(root, text="Click Me", command=btn_click)
btn.pack()

def auto_click():
    print("Auto clicking...")
    btn.invoke()

root.after(1000, auto_click)
root.after(3000, root.destroy)
root.mainloop()

