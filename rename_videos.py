import os
import re
import argparse

def rename_videos(directory):
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return

    # Match pattern: {number}_{string}_{number}.mp4
    # Example: 1_Échos_de_la_Pluie_1.mp4
    # Groups: (1: leading number) (2: name part) (3: trailing number)
    pattern = re.compile(r'^(\d+)_+(.+?)_+(\d+)\.mp4$', re.IGNORECASE)
    
    count = 0
    for filename in os.listdir(directory):
        if not filename.lower().endswith(".mp4"):
            continue
            
        match = pattern.match(filename)
        if match:
            # Extract the middle 'name' part
            name_part = match.group(2)
            
            # Replace underscores with spaces
            clean_name = name_part.replace('_', ' ')
            
            # Construct new name: OriginalName - Cleaned Name.mp4
            # To keep the exact original name part without the extension, we can split
            base_name, ext = os.path.splitext(filename)
            new_filename = f"{base_name} - {clean_name}{ext}"
            
            old_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, new_filename)
            
            try:
                os.rename(old_path, new_path)
                print(f"Renamed: '{filename}' -> '{new_filename}'")
                count += 1
            except Exception as e:
                print(f"Error renaming '{filename}': {e}")
        else:
            print(f"Skipped (no match): {filename}")
            
    print(f"\nDone. Renamed {count} files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename video files dynamically based on pattern.")
    parser.add_argument("directory", nargs="?", default=".", help="Directory containing the MP4 files (default: current directory)")
    args = parser.parse_args()
    
    print(f"Scanning directory: {os.path.abspath(args.directory)}\n")
    rename_videos(args.directory)
