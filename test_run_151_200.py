import sys
import os
import time
import logging

# Add project root to path
sys.path.append("/Users/huseyincoskun/Downloads/Antigravity Proje/MusicBot/execution")

from suno_generator import SunoGenerator
from browser_controller import BrowserController

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_test_range():
    # Olivia Rodrigo profile settings
    project_file = "/Users/huseyincoskun/Documents/MusicBot_Workspace/olivia_rodrigo.xlsx"
    profile_name = "Olivia Rodrigo"
    output_media = os.path.join("/Users/huseyincoskun/Documents/MusicBot_Workspace", "output_media", profile_name)
    persona_link = "https://suno.com/persona/6b8123d4-b425-4dd5-be4d-0e2d736c045c"
    
    h_conf = {
        "level": "YÜKSEK",
        "speed": 0.05,
        "retries": 2,
        "adaptive": False
    }
    
    # Ensure output dir exists
    if not os.path.exists(output_media):
        os.makedirs(output_media, exist_ok=True)

    browser = BrowserController(headless=False, humanizer_config=h_conf)
    browser.start()
    
    try:
        suno = SunoGenerator(
            project_file=project_file,
            output_dir=output_media,
            browser=browser,
            delay=5,
            startup_delay=5,
            audio_influence=60,
            vocal_gender="Female",
            weirdness=60,
            style_influence=60,
            persona_link=persona_link
        )
        
        # TARGETED RANGE: 151 to 200, excluding 171 and 179
        exclude_ids = {171, 179}
        target_ids = [str(i) for i in range(151, 201) if i not in exclude_ids]
        
        logger.info(f"--- STARTING BATCH DOWNLOAD FOR IDs 151-200 (excluding 171, 179) - Total: {len(target_ids)} songs ---")
        
        # Using dl_only mode for pure download/search test
        # op_mode="dl_only" will skip generation and go straight to search/download
        suno.run_batch(target_ids=target_ids, op_mode="dl_only", force_update=True)
        
        logger.info("Test run completed.")
    except Exception as e:
        logger.error(f"Test run failed: {e}")
    finally:
        browser.stop()

if __name__ == "__main__":
    run_test_range()
