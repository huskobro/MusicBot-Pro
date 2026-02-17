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

def final_verification():
    # Camille Noctra profile settings
    project_file = "/Users/huseyincoskun/Documents/MusicBot_Workspace/camille_noctra.xlsx"
    profile_name = "Camille Noctra"
    output_media = os.path.join(os.path.dirname(project_file), "output_media", profile_name)
    persona_link = "https://suno.com/persona/86b7202e-c347-4efc-8286-301d8c366e72"
    
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
        
        # TARGETED VERIFICATION: IDs 121, 122, 123, 124 - DOWNLOAD ONLY
        logger.info("--- STARTING FINAL VERIFICATION (DL ONLY) FOR IDs 121, 122, 123, 124 ---")
        suno.run_batch(target_ids=["121", "122", "123", "124"], op_mode="dl_only", force_update=True)
        
        print("\nVerification process finished.")
        print("Expected results:")
        print("1. All 3 songs generated with Camille Noctra persona.")
        print("2. System waited until all songs reached 'Hazır!' state.")
        print("3. Exactly songs 121, 122, 123 were downloaded (both versions).")
        time.sleep(10)
    finally:
        browser.stop()

if __name__ == "__main__":
    final_verification()
