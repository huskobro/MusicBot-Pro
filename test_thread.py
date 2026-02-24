import tkinter as tk
from tkinter import ttk
import threading
import time

def worker(app):
    print("Worker started")
    time.sleep(1)
    print("Worker finished")

def start():
    print("Start clicked")
    threading.Thread(target=worker, args=(None,), daemon=True).start()

root = tk.Tk()
b = ttk.Button(root, text="Start", command=start)
b.pack()
root.after(1000, start)
root.after(3000, root.destroy)
root.mainloop()
