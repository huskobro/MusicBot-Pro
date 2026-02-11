import os
import sys
import logging
import time

# Add execution dir to path
sys.path.append(os.path.join(os.getcwd(), "execution"))

from suno_generator import SunoGenerator

# Setup logging to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_integration_test():
    # 1. Resolve Paths (Exact same logic as App)
    base_data_dir = os.path.expanduser("~/Documents/MusicBot_Data")
    csv_path = os.path.join(base_data_dir, "metadata.csv")
    output_dir = os.path.join(base_data_dir, "output")
    profile_path = os.path.join(base_data_dir, "chrome_profile")
    
    logger.info("--- INTEGRATION TEST START ---")
    logger.info(f"CSV Path: {csv_path}")
    logger.info(f"Profile: {profile_path}")
    
    if not os.path.exists(csv_path):
        logger.error(f"FAIL: metadata.csv not found at {csv_path}")
        return

    # 2. Run Generator
    try:
        # We manually initialize the browser controller with the profile path
        # The SunoGenerator usually creates its own, but we want to ensure it uses the RIGHT one.
        # Actually, SunoGenerator.__init__ takes no profile arg, it uses BrowserController's default
        # logic which we already set to ~/Documents/MusicBot_Data/chrome_profile if sys.frozen is False?
        # Let's check browser_controller.py again.
        
        suno = SunoGenerator(metadata_path=csv_path, output_dir=output_dir)
        
        # Override the browser's user_data_dir just to be 100% sure for this test
        suno.browser.user_data_dir = profile_path
        
        logger.info("Starting Suno.run()...")
        suno.run()
        
        logger.info("--- INTEGRATION TEST FINISHED ---")
    except Exception as e:
        logger.error(f"Integration test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    run_integration_test()
