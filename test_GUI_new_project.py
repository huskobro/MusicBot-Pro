
import os
import openpyxl
import logging
from execution.gui_launcher import MusicBotGUI
import tkinter as tk
from unittest.mock import patch, MagicMock

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_new_project_flow():
    print("--- Testing 'New Project' Button Logic ---")
    
    root = tk.Tk()
    app = MusicBotGUI(root)
    
    # Define mock path for new project
    mock_path = os.path.abspath("Mock_Project.xlsx")
    if os.path.exists(mock_path): os.remove(mock_path)
    
    # Mock filedialog.asksaveasfilename
    with patch('tkinter.filedialog.asksaveasfilename', return_value=mock_path):
        print("Simulating Button Click...")
        app.create_new_project()
        
    # Verify File Exists
    if os.path.exists(mock_path):
        print(f"SUCCESS: File created at {mock_path} ✅")
        
        # Verify Content
        wb = openpyxl.load_workbook(mock_path)
        ws = wb.active
        start_id = ws.cell(row=2, column=1).value
        if start_id == "EXAMPLE_01":
             print("SUCCESS: Template content found! ✅")
        else:
             print(f"FAILURE: Unexpected content: {start_id} ❌")
             
        # Verify GUI Loaded
        if "Mock_Project.xlsx" in app.lbl_project.cget("text"):
             print("SUCCESS: GUI loaded the new project! ✅")
        else:
             print("FAILURE: GUI did not load project. ❌")
             
    else:
        print("FAILURE: File was not created. ❌")
        
    root.destroy()
    if os.path.exists(mock_path): os.remove(mock_path)

if __name__ == "__main__":
    try:
        test_new_project_flow()
    except Exception as e:
        import traceback
        traceback.print_exc()
