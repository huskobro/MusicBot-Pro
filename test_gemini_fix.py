import os
import sys
import logging

# Add execution folder to path
sys.path.append(os.path.abspath("execution"))

from gemini_prompter import GeminiPrompter
from browser_controller import BrowserController

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_gemini():
    # Paths
    project_root = "/Users/huseyincoskun/Downloads/Antigravity Proje/MusicBot"
    metadata_path = os.path.join(project_root, "input_songs.xlsx") # Dummy or real
    
    # Initialize prompter with the real Chrome profile
    prompter = GeminiPrompter(
        project_file=metadata_path,
        headless=False,
        language="Turkish"
    )
    
    # Attempt a single generation
    theme = "Yağmurlu bir gecede İstanbul sokaklarında geçen hüzünlü bir ayrılık hikayesi."
    logger.info(f"Testing Gemini with theme: {theme}")
    
    # Start browser via prompter's internal browser controller
    prompter.browser.start()
    prompter.tab.goto(prompter.base_url)
    
    # Give it a moment to load
    import time
    time.sleep(5)
    
    result = prompter.generate_content(theme=theme, style="Türkçe Slow Pop, Akustik Gitar")
    
    if result:
        logger.info("SUCCESS: Gemini responded correctly!")
        logger.info(f"Title: {result.get('title')}")
        logger.info(f"Lyrics snippet: {result.get('lyrics')[:50]}...")
    else:
        logger.error("FAILED: Gemini did not respond or interaction failed.")

if __name__ == "__main__":
    test_gemini()
