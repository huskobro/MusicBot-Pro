import tkinter as tk
from tkinter import ttk
root = tk.Tk()
b = ttk.Button(root, text="Test")
try:
    b.config(state="normal")
    print("Normal config SUCCESS")
except Exception as e:
    print("CRASH:", e)

try:
    b.state(['!disabled'])
    print("state SUCCESS")
except Exception as e:
    print("CRASH:", e)
