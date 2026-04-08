import sys
import os
import time
import logging

# Add project root to path
sys.path.append("/Users/huseyincoskun/Downloads/Antigravity Proje/MusicBot/execution")

from suno_generator import SunoGenerator
from browser_controller import BrowserController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_range():
    # Camille Noctra profile settings
    project_file = "/Users/huseyincoskun/Documents/MusicBot_Workspace/camille_noctra.xlsx"
    profile_name = "Camille Noctra"
    output_media = os.path.join(os.path.dirname(project_file), "output_media", profile_name)
    persona_link = "https://suno.com/voice/86b7202e-c347-4efc-8286-301d8c366e72"
    
    h_conf = {
        "level": "YÜKSEK",
        "speed": 0.05,
        "retries": 2,
        "adaptive": False
    }
    
    browser = BrowserController(headless=False, humanizer_config=h_conf)
    browser.start()
    
    try:
        suno = SunoGenerator(
            project_file=project_file,
            output_dir=output_media,
            browser=browser,
            delay=15,
            startup_delay=5,
            audio_influence=60,
            vocal_gender="Female",
            weirdness=60,
            style_influence=60,
            persona_link=persona_link
        )
        
        # TARGETED RANGE: 125 to 141
        target_ids = [str(i) for i in range(125, 142)]
        
        logger.info(f"--- STARTING DOWNLOAD FOR IDs 125-141 ({len(target_ids)} songs) ---")
        
        # We use dl_only to search and download existing generations
        suno.run_batch(target_ids=target_ids, op_mode="dl_only", force_update=True)
        
        print("\nDownload process finished.")
        time.sleep(5)
    finally:
        browser.stop()

if __name__ == "__main__":
    download_range()
