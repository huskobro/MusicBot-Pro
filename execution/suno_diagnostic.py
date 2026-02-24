import time
import os
import logging
from browser_controller import BrowserController

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_diagnostic():
    browser = BrowserController(headless=False)
    output_dir = "output/diagnostics"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        browser.start()
        logger.info("Navigating to Suno Create page...")
        browser.goto("https://suno.com/create")
        
        # Wait for user to ensure they are on the right page
        input("\n--- DIAGNOSTIC PAUSE ---\n1. Ensure you are LOGGED IN.\n2. Ensure you are on the 'Create' page.\n3. Press Enter to start probing the DOM...")

        logger.info("Probing DOM for interactive elements...")
        
        # 1. Probe Textareas
        textareas = browser.page.locator("textarea").all()
        logger.info(f"FOUND {len(textareas)} textareas:")
        for i, ta in enumerate(textareas):
            try:
                box = ta.bounding_box()
                logger.info(f"   [{i}] Placeholder: '{ta.get_attribute('placeholder')}', Visible: {ta.is_visible()}, Box: {box}")
                if ta.is_visible():
                    # Highlight it on page for visual confirmation
                    browser.page.evaluate(f"() => {{ const el = document.querySelectorAll('textarea')[{i}]; el.style.border = '5px solid red'; el.style.zIndex = '9999'; }}")
            except Exception: pass

        # 2. Probe Inputs
        inputs = browser.page.locator("input").all()
        logger.info(f"FOUND {len(inputs)} inputs:")
        for i, inp in enumerate(inputs):
            try:
                box = inp.bounding_box()
                logger.info(f"   [{i}] Type: {inp.get_attribute('type')}, Placeholder: '{inp.get_attribute('placeholder')}', Box: {box}")
                if inp.is_visible():
                     browser.page.evaluate(f"() => {{ const el = document.querySelectorAll('input')[{i}]; el.style.border = '5px solid blue'; }}")
            except Exception: pass

        # 3. Probe ContentEditable Divs (Modern UI often uses these)
        editables = browser.page.locator("div[contenteditable='true']").all()
        logger.info(f"FOUND {len(editables)} contenteditable divs:")
        for i, ed in enumerate(editables):
            try:
                box = ed.bounding_box()
                logger.info(f"   [{i}] Role: {ed.get_attribute('role')}, Aria-Label: {ed.get_attribute('aria-label')}, Box: {box}")
                if ed.is_visible():
                     browser.page.evaluate(f"() => {{ const el = document.querySelectorAll('div[contenteditable=\"true\"]')[{i}]; el.style.border = '5px solid green'; }}")
            except Exception: pass

        # 4. Probe Buttons (Specifically 'Custom' and 'Create')
        buttons = browser.page.locator("button").all()
        logger.info(f"FOUND {len(buttons)} buttons. Searching for 'Custom' and 'Create'...")
        for i, btn in enumerate(buttons):
            text = btn.inner_text().strip()
            if text in ["Custom", "Create"]:
                box = btn.bounding_box()
                logger.info(f"   MATCH: '{text}' Button at {box}")
                if btn.is_visible():
                    browser.page.evaluate(f"() => {{ const btns = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.includes('{text}')); btns.forEach(b => b.style.outline = '5px solid yellow'); }}")

        # Take diagnostic screenshot
        browser.screenshot(f"{output_dir}/diagnostic_map.png")
        logger.info(f"Diagnostic map saved to {output_dir}/diagnostic_map.png")
        logger.info("Check the screenshot! Red=Textarea, Blue=Input, Green=EditableDiv, Yellow=KeyButtons.")

        # 5. Test Clickability
        logger.info("Testing click on first visible textarea...")
        for ta in textareas:
            if ta.is_visible():
                try:
                    ta.click()
                    logger.info("   -> Click successful (no error).")
                    break
                except Exception as e:
                    logger.error(f"   -> Click failed: {e}")

    except Exception as e:
        logger.error(f"Diagnostic crash: {e}")
    finally:
        browser.stop()

if __name__ == "__main__":
    run_diagnostic()
