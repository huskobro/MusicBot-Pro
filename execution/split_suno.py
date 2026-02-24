import os

filepath = 'suno_generator.py'
with open(filepath, 'r') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines, 1):
    # Skip extracted methods
    if 748 <= i <= 1236: continue
    if 1423 <= i <= 1550: continue
    if 1553 <= i <= 2009: continue
    
    # Update class definition
    if line.startswith("class SunoGenerator:"):
        new_lines.extend([
            "from suno_config import SunoConfig\n",
            "from suno_excel import SunoExcelMixin\n",
            "from suno_downloader import SunoDownloaderMixin\n",
            "from suno_ui import SunoUIMixin\n",
            "\n",
            "class SunoGenerator(SunoExcelMixin, SunoDownloaderMixin, SunoUIMixin):\n"
        ])
        continue
        
    # Inject config instantiation
    if line.strip() == "self.project_file = project_file":
        new_lines.extend([
            "        self.config = SunoConfig(\n",
            "            delay=delay,\n",
            "            startup_delay=startup_delay\n",
            "        )\n",
            line
        ])
        continue
        
    new_lines.append(line)

with open(filepath, 'w') as f:
    f.writelines(new_lines)
print("done")
