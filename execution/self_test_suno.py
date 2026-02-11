import time
import os
import sys
import logging
from browser_controller import BrowserController

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def self_test():
    # Force use of the App's profile path where the user logged in
    profile_path = os.path.expanduser("~/Documents/MusicBot_Data/chrome_profile")
    logger.info(f"Targeting profile at: {profile_path}")
    
    if not os.path.exists(profile_path):
        logger.error("Profile path DOES NOT EXIST. Did you log in using the MusicBot App first?")
        return

    # Initialize with the specific profile
    # We use headless=False so the user can see what's happening, 
    # but I can also use headless=True if I just want the screenshot.
    # The user said "open the browser", so I'll keep headless=False.
    browser = BrowserController(headless=False, profile_path=profile_path)
    output_dir = "output/self_test"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        browser.start()
        logger.info("Navigating to Suno Create...")
        browser.goto("https://suno.com/create")
        
        # Give it time to load and bypass any overlays
        time.sleep(5)
        
        # Check login state
        url = browser.page.url
        logger.info(f"Current URL: {url}")
        
        browser.screenshot(f"{output_dir}/step_1_load.png")
        
        # Check for 'Custom' button
        custom_btn = browser.page.locator("button:has-text('Custom')").first
        if custom_btn.is_visible():
            logger.info("Custom button found. Clicking it...")
            custom_btn.click()
            time.sleep(2)
            browser.screenshot(f"{output_dir}/step_2_custom_clicked.png")
        else:
            logger.warning("Custom button NOT visible. Maybe already in custom mode or not logged in.")

        # Probe for textareas (Human-mimicry style)
        textareas = browser.page.locator("textarea").all()
        logger.info(f"Found {len(textareas)} textareas.")
        
        for i, ta in enumerate(textareas):
            ph = ta.get_attribute("placeholder") or "No placeholder"
            vis = ta.is_visible()
            logger.info(f"   [{i}] Visible: {vis}, Placeholder: '{ph}'")
            
            if vis:
                logger.info(f"   -> Testing CLICK on textarea {i}...")
                try:
                    ta.click()
                    logger.info("      Click successful.")
                    # Try typing
                    logger.info("      Testing TYPE...")
                    browser.page.keyboard.type(f"Self-test prompt at {time.ctime()}")
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"      Click/Type failed: {e}")

        # Check for Create button
        create_btn = browser.page.get_by_role("button", name="Create").last
        logger.info(f"Create button visible: {create_btn.is_visible()}")
        if create_btn.is_visible():
            logger.info(f"Create button enabled: {create_btn.is_enabled()}")

        browser.screenshot(f"{output_dir}/step_3_final_state.png")
        logger.info("Self-test complete. Check screenshots in output/self_test/")

    except Exception as e:
        logger.error(f"Self-test failed: {e}")
        try:
             browser.screenshot(f"{output_dir}/error_crash.png")
        except: pass
    finally:
        # Keep browser open for a few seconds so user sees result
        time.sleep(5)
        browser.stop()

if __name__ == "__main__":
    self_test()
