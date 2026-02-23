import os
import sys
import time
import platform
import functools
import logging
from urllib.robotparser import RobotFileParser
from playwright.sync_api import sync_playwright, Page, BrowserContext, ElementHandle
from playwright_stealth import Stealth
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
        Initializes the BrowserController with native Playwright defaults.
        """
        self.headless = headless
        
        if profile_path:
            self.user_data_dir = profile_path
        else:
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
        self.humanizer_enabled = True 
        logger.info(f"Humanizer initialized: {h_conf}")

        # --- Mandatory Google Login Compatibility ---
        if platform.system() == "Windows":
            self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        else:
            self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.7632.77 Safari/537.36"
        self.last_action_time = 0

    def _cleanup_locks(self):
        """Removes Chrome's Singleton lock files and kills stale processes."""
        import platform
        import subprocess
        import glob
        
        # Aggressive process cleanup for macOS/Linux based on profile path
        if platform.system() in ["Darwin", "Linux"]:
            try:
                # Find PIDs of processes using this specific user_data_dir
                cmd = f"ps aux | grep '{self.user_data_dir}' | grep -v grep | awk '{{print $2}}'"
                output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
                if output:
                    for pid in output.split('\n'):
                        pid = pid.strip()
                        if pid:
                            subprocess.run(f"kill -9 {pid}", shell=True, stderr=subprocess.DEVNULL)
                            logger.info(f"Killed stale browser process: {pid}")
                time.sleep(1) # Give OS time to close tracked files
            except Exception as e:
                logger.warning(f"Process cleanup warning: {e}")
                
        # Handle iCloud sync conflict files & broken symlinks
        singleton_files = glob.glob(os.path.join(self.user_data_dir, "Singleton*"))
        for path in singleton_files:
            try:
                logger.info(f"Removing stale lock file: {path}")
                os.remove(path)
            except Exception as e:
                logger.warning(f"Failed to remove lock file {path}: {e}")

    def start(self):
        """Starts the Playwright persistent context with mandatory compatibility flags."""
        if self.playwright and self.context:
            logger.info("Browser already running.")
            return

        self._cleanup_locks()

        # Windows-specific: Wait a moment for native Chrome to fully release the folder
        if platform.system() == "Windows":
             time.sleep(1.5)

        logger.info(f"Starting browser with persistent profile at: {self.user_data_dir}")
        self.playwright = sync_playwright().start()
        
        try:
            # --- Mandatory Google Login Fix ---
            # Using the exact minimal set for maximum compatibility
            
            # THE FIX: Chrome with --user-data-dir uses a 'Default' subfolder by default.
            # We must ensure Playwright also uses/sees the same structure.
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=self.headless,
                channel="chrome",
                user_agent=self.user_agent,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--lang=tr-TR",
                    "--profile-directory=Default"
                ] + (["--password-store=basic"] if platform.system() == "Darwin" else []),
                ignore_default_args=["--enable-automation"] + (["--use-mock-keychain"] if platform.system() == "Darwin" else []),
                viewport=None, 
                device_scale_factor=1,
                locale="tr-TR",
                timezone_id="Europe/Istanbul"
            )

            # Standard Stealth only, no over-the-top scripts that break context
            Stealth().apply_stealth_sync(self.context)
            
            if self.context.pages:
                self.pages["default"] = self.context.pages[0]
            else:
                self.pages["default"] = self.context.new_page()
            
            logger.info("Browser started successfully (Compatibility Mode).")
            
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
            self.stop()
            raise e

    def launch_native_chrome(self, urls=["https://suno.com/create", "https://gemini.google.com/app"]):
        """
        Launches the REAL Chrome binary as a standalone process.
        This is the only 100% way to bypass 'Unsecure Browser' during login.
        The bot should be STOPPED when this is used.
        """
        import subprocess
        self._cleanup_locks()
        
        system = platform.system()
        chrome_path = ""
        
        if system == "Darwin": # macOS
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        elif system == "Windows":
             # Standard Windows paths
             possible_paths = [
                 r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                 r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                 os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe")
             ]
             for p in possible_paths:
                 if os.path.exists(p):
                     chrome_path = p
                     break
        
        if not chrome_path or not os.path.exists(chrome_path):
            logger.error(f"Google Chrome not found at standard path for {system}.")
            return False

        cmd = [
            chrome_path,
            f"--user-data-dir={self.user_data_dir}",
            "--profile-directory=Default",
            "--no-first-run",
            "--no-default-browser-check",
            "--lang=tr-TR"
        ]
        
        if platform.system() == "Darwin":
            cmd.append("--password-store=basic")
        
        cmd += urls

        logger.info(f"Launching NATIVE Chrome for manual login: {urls}")
        try:
            # We use Popen so it doesn't block the GUI
            subprocess.Popen(cmd)
            return True
        except Exception as e:
            logger.error(f"Failed to launch native chrome: {e}")
            return False

    def get_page(self, name="default"):
        """Returns a named page, creating it if it doesn't exist."""
        if not self.context:
            self.start()
        
        if name not in self.pages:
            logger.info(f"Creating new tab: {name}")
            page = self.context.new_page()
            # Stealth is already applied to the context
            self.pages[name] = page
            
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
        if self.humanizer_enabled:
            self.humanizer.check_captcha(p)
            self.humanizer.click_element(p, selector)
        else:
            p.click(selector)


    @r_try()
    def fill(self, selector, text, page=None):
        """Fills an input field specified by the selector."""
        p = page if page else self.page
        
        logger.info(f"Filling element {selector} with text length {len(text)}")
        if self.humanizer_enabled:
            self.humanizer.check_captcha(p)
            self.humanizer.type_text(p, selector, text)
        else:
            p.fill(selector, text)


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
