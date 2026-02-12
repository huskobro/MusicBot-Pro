
import sys
import os
import traceback
import tkinter as tk
from tkinter import messagebox

# Add execution dir to path to mimic app structure
sys.path.append(os.path.join(os.getcwd(), "execution"))

def test_chrome_launch():
    print("--- Testing Chrome Launch Logic ---")
    try:
        from execution.browser_controller import BrowserController
        print("BrowserController imported successfully.")
        
        print("Attempting to start browser...")
        bc = BrowserController(headless=False)
        bc.start()
        print("Browser started.")
        
        page = bc.pages.get("default")
        if page:
            print("Navigating to Google...")
            page.goto("https://www.google.com")
            
        print("Press Enter to close browser...")
        input()
        
        bc.stop()
        print("Browser stopped.")
        
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    test_chrome_launch()
