import os
import re
import argparse

def revert_videos(directory):
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return

    # Match pattern: {number}_{string}_{number} - {Cleaned Name}.mp4
    # Example: 1_Échos_de_la_Pluie_1 - Échos de la Pluie.mp4
    # Group 1 captures the original core: "1_Échos_de_la_Pluie_1"
    pattern = re.compile(r'^(\d+_.+?_\d+)\s+-\s+.*\.mp4$', re.IGNORECASE)
    
    count = 0
    for filename in os.listdir(directory):
        if not filename.lower().endswith(".mp4"):
            continue
            
        match = pattern.match(filename)
        if match:
            original_base = match.group(1)
            ext = os.path.splitext(filename)[1]
            new_filename = f"{original_base}{ext}"
            
            old_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, new_filename)
            
            try:
                os.rename(old_path, new_path)
                print(f"Reverted: '{filename}' -> '{new_filename}'")
                count += 1
            except Exception as e:
                print(f"Error renaming '{filename}': {e}")
        else:
            print(f"Skipped (no match): {filename}")
            
    print(f"\nDone. Reverted {count} files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Revert video files back to their original MusicBot naming pattern.")
    parser.add_argument("directory", nargs="?", default=".", help="Directory containing the MP4 files (default: current directory)")
    args = parser.parse_args()
    
    print(f"Scanning directory: {os.path.abspath(args.directory)}\n")
    revert_videos(args.directory)
