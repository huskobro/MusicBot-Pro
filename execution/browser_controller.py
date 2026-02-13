import os
import sys
import time
import functools
import logging
from playwright.sync_api import sync_playwright, Page, BrowserContext, ElementHandle
from humanizer import Humanizer


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def r_try(max_retries=3, delay=2):
    """
    Decorator to retry a function call multiple times.
    Useful for network requests or UI interactions that might flake.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt}/{max_retries} failed for {func.__name__}: {e}")
                    if attempt < max_retries:
                        time.sleep(delay)
            logger.error(f"Function {func.__name__} failed after {max_retries} attempts.")
            raise last_exception
        return wrapper
    return decorator

class BrowserController:
    """
    Manages the Playwright browser instance, context, and page.
    Uses a persistent context to maintain login sessions (cookies, local storage).
    """

    def __init__(self, headless=False, profile_path=None, humanizer_config=None):

        """
        Initializes the BrowserController.
        
        Args:
            headless (bool): Whether to run the browser in headless mode.
            profile_path (str): Path to the Chrome user data directory. 
                                Defaults to the standard macOS Chrome profile location if not provided.
        """
        self.headless = headless
        
        if profile_path:
            self.user_data_dir = profile_path
        else:
            # Use a local profile directory in the project/app support folder
            # This ensures we don't conflict with the user's main open Chrome instance
            # and allows us to save the login state portably.
            if getattr(sys, 'frozen', False):
                # If packaged, keep profile near the app or in Documents to persist
                base_path = os.path.expanduser("~/Documents/MusicBot_Workspace")
            else:
                # If script, keep in Documents to match packaged app behavior (Unified Workspace)
                base_path = os.path.expanduser("~/Documents/MusicBot_Workspace")
            
            self.user_data_dir = os.path.join(base_path, "chrome_profile")
            os.makedirs(self.user_data_dir, exist_ok=True)

        self.playwright = None
        self.context = None
        self.pages = {} # Map names to page objects

        # Initialize Humanizer
        h_conf = humanizer_config or {}
        self.humanizer = Humanizer(
            level=h_conf.get("level", "MEDIUM"),
            speed_multiplier=h_conf.get("speed", 1.0),
            retry_attempts=h_conf.get("retries", 1),
            adaptive_delay=h_conf.get("adaptive", True)
        )
        logger.info(f"Humanizer initialized: {h_conf}")


    def _cleanup_locks(self):
        """Removes Chrome's Singleton lock files that prevent multi-instance launch."""
        lock_files = ["SingletonLock", "SingletonCookie", "SingletonSocket"]
        for lock in lock_files:
            path = os.path.join(self.user_data_dir, lock)
            if os.path.exists(path):
                try:
                    logger.info(f"Removing stale lock file: {path}")
                    os.remove(path)
                except Exception as e:
                    logger.warning(f"Failed to remove lock file {path}: {e}")

    def start(self):
        """Starts the Playwright persistent context."""
        if self.playwright and self.context:
            logger.info("Browser already running.")
            return

        # Always try to clear locks before starting
        self._cleanup_locks()

        logger.info(f"Starting browser with persistent profile at: {self.user_data_dir}")
        self.playwright = sync_playwright().start()
        
        try:
            # Launch persistent context
            # Adding channel="chrome" back - it's REQUIRED for the bundled app to find the system Chrome.
            # The SIGTRAP/Lock issues are now handled by _cleanup_locks().
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=self.headless,
                channel="chrome",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox"
                ],
                viewport={"width": 1280, "height": 800} 
            )
            
            # Default page
            if self.context.pages:
                self.pages["default"] = self.context.pages[0]
            else:
                self.pages["default"] = self.context.new_page()
            
            logger.info("Browser started successfully.")
            
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
            self.stop()
            raise e

    def get_page(self, name="default"):
        """Returns a named page, creating it if it doesn't exist."""
        if not self.context:
            self.start()
        
        if name not in self.pages:
            logger.info(f"Creating new tab: {name}")
            self.pages[name] = self.context.new_page()
            
        return self.pages[name]

    @property
    def page(self):
        """Standard 'page' property for backward compatibility (returns default)."""
        return self.get_page("default")

    def stop(self):
        """Closes the browser and context."""
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser stopped.")

    @r_try()
    def goto(self, url, page=None):
        """Navigates to a URL with retry logic."""
        p = page if page else self.page
        logger.info(f"Navigating to {url}")
        
        # Humanizer wait before navigation
        self.humanizer.smart_wait(0.5, 1.2)
        
        p.goto(url, wait_until="domcontentloaded")
        
        # Wait for CAPTCHA if any
        self.humanizer.check_captcha(p)
        
        # Light settle wait
        self.humanizer.smart_wait(0.4, 0.8)


    @r_try()
    def click(self, selector, page=None):
        """Clicks an element specified by the selector."""
        p = page if page else self.page
        logger.info(f"Clicking element: {selector}")
        self.humanizer.check_captcha(p)
        self.humanizer.click_element(p, selector)


    @r_try()
    def fill(self, selector, text, page=None):
        """Fills an input field specified by the selector."""
        p = page if page else self.page
        logger.info(f"Filling element {selector} with text length {len(text)}")
        self.humanizer.check_captcha(p)
        self.humanizer.type_text(p, selector, text)


    @r_try()
    def get_text(self, selector, page=None):
        """Gets the text content of an element."""
        p = page if page else self.page
        return p.inner_text(selector)

    @r_try()
    def wait_for_selector(self, selector, timeout=60000, page=None):
        """Waits for an element to appear (Increased timeout to 60s)."""
        p = page if page else self.page
        logger.info(f"Waiting for selector: {selector} (timeout={timeout})")
        p.wait_for_selector(selector, timeout=timeout)

    @r_try()
    def is_visible(self, selector, page=None):
        """Checks if an element is visible (Wait briefly first)."""
        p = page if page else self.page
        try:
            p.wait_for_selector(selector, timeout=2000)
        except: pass
        return p.is_visible(selector)

    def wait_for_stable_dom(self, page=None, timeout=3000):
        """Waits until the DOM stops changing for a short period."""
        p = page if page else self.page
        try:
            p.wait_for_load_state("networkidle", timeout=timeout)
        except: pass
        time.sleep(0.3) # Short settle


    def get_value(self, selector, page=None):
        """Gets the value of an input element."""
        p = page if page else self.page
        try:
            return p.eval_on_selector(selector, "el => el.value")
        except:
            return None

    def screenshot(self, path, page=None):

        """Takes a screenshot and saves it to the given path."""
        p = page if page else self.page
        p.screenshot(path=path)
        logger.info(f"Screenshot saved to {path}")

# Example usage (for testing purposes)
if __name__ == "__main__":
    browser = BrowserController(headless=False)
    try:
        browser.start()
        browser.goto("https://www.google.com")
        print("Page title:", browser.page.title())
        time.sleep(2) # Keep open briefly to see
    except Exception as e:
        print(f"Error: {e}")
    finally:
        browser.stop()
