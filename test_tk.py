
import tkinter as tk
root = tk.Tk()
root.title("Test")
label = tk.Label(root, text="Hello World")
label.pack()
root.after(2000, lambda: root.destroy())
root.mainloop()
print("Tkinter works")
