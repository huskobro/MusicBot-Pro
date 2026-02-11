
import sys
try:
    print("Attempting to import openpyxl...")
    import openpyxl
    print(f"Success! openpyxl version: {openpyxl.__version__}")
except Exception as e:
    print(f"Failed to import openpyxl: {e}")
