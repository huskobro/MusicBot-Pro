import sys
import os
import openpyxl

backup_dir = "test_env/.backups"
base = "test.xlsx"

for i in range(1, 4):
    path = f"{backup_dir}/{base}.bak{i}"
    print(f"Checking {path} - exists:", os.path.exists(path))
    if os.path.exists(path):
        try:
            openpyxl.load_workbook(path)
            print("  -> VALID")
        except Exception as e:
            print("  -> INVALID:", e)
