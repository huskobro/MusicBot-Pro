import sys
import os
import time
import logging

# Add project root to path
sys.path.append("/Users/huseyincoskun/Downloads/Antigravity Proje/MusicBot/execution")

from suno_generator import SunoGenerator
from browser_controller import BrowserController

logging.basicConfig(level=logging.INFO)

def test_full_cycle():
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
        
        # Testing with user requested IDs in FULL cycle
        suno.run_batch(target_ids=["119", "120", "121"], op_mode="full", force_update=True)
        
        print("Test complete. Verify that it waited for all 3 and then downloaded them.")
        time.sleep(30)
    finally:
        browser.stop()

if __name__ == "__main__":
    test_full_cycle()
