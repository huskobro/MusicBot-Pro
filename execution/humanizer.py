import time
import random
import logging

logger = logging.getLogger(__name__)

class Humanizer:
    def __init__(self, level="MEDIUM", speed_multiplier=1.0, retry_attempts=1, adaptive_delay=True):
        self.level = level.upper()
        self.speed_multiplier = speed_multiplier
        self.retry_attempts = retry_attempts # Now strictly capped or small
        self.adaptive_delay = adaptive_delay

    def smart_wait(self, min_s=0.2, max_s=0.6):
        """Randomized wait within bounds, scaled by level."""
        if self.level == "LOW":
            delay = random.uniform(0.1, 0.4)
        elif self.level == "HIGH":
            delay = random.uniform(min_s * 2, max_s * 2.5)
        else: # MEDIUM
            delay = random.uniform(min_s, max_s)
            
        final_delay = delay * self.speed_multiplier
        # logger.debug(f"Humanizer: Waiting {final_delay:.2f}s (Level: {self.level})")
        time.sleep(final_delay)

    def type_text(self, page, selector_or_loc, text):
        """Strict character-by-character typing with verification. No copy-paste fallbacks."""
        if not text: return
        
        logger.info(f"Humanizer ({self.level}): Typing activity started - STRICT MODE")
        
        # 1. Ensure element is ready and FOCUSED
        try:
            if isinstance(selector_or_loc, str):
                ele = page.wait_for_selector(selector_or_loc, state="visible", timeout=7000)
            else:
                ele = selector_or_loc
            
            ele.scroll_into_view_if_needed()
            self.smart_wait(0.3, 0.6)
            
            # Defensive focus: Hover, Focus, then Click
            try: ele.hover(timeout=2000)
            except: pass
            
            ele.focus()
            ele.click(force=True) # Ensure it's active
            time.sleep(0.5) 
            
        except Exception as e:
            logger.error(f"Humanizer: CRITICAL - Could not focus {selector_or_loc}: {e}")
            # Instead of silent fill, we try one more focus attempt
            try:
                page.click(selector_or_loc if isinstance(selector_or_loc, str) else selector_or_loc.selector, force=True)
            except: pass
            
        # 2. Clear existing (Human-like)
        import sys
        mod = "Meta" if sys.platform == "darwin" else "Control"
        page.keyboard.press(f"{mod}+A")
        page.keyboard.press("Backspace")
        time.sleep(0.3)

        # 3. Typing logic (Strictly via keyboard)
        def perform_typing(input_text):
            for i, char in enumerate(input_text):
                page.keyboard.type(char)
                
                # Base delay per level
                if self.level == "LOW":
                    base_delay = random.uniform(0.02, 0.05)
                elif self.level == "HIGH":
                    base_delay = random.uniform(0.12, 0.30) # Significantly slower
                else: # MEDIUM
                    base_delay = random.uniform(0.05, 0.15)
                
                # Random human imperfections (small delays)
                if i > 0 and i % random.randint(8, 15) == 0:
                    time.sleep(random.uniform(0.3, 0.8) * self.speed_multiplier)
                
                time.sleep(base_delay * self.speed_multiplier)

        # Execute typing
        perform_typing(str(text))
        
        # 4. Verification & Single Retry
        self.smart_wait(0.5, 1.2)
        try:
            if isinstance(selector_or_loc, str):
                current_val = page.eval_on_selector(selector_or_loc, "el => el.value")
            else:
                current_val = selector_or_loc.input_value()
            
            if current_val != str(text) and self.retry_attempts > 0:
                logger.warning(f"Humanizer: Verification failed. Retrying typing strictly...")
                # Try to fix by clicking again before retry
                if isinstance(selector_or_loc, str): page.click(selector_or_loc, force=True)
                else: selector_or_loc.click(force=True)
                
                import sys
                mod = "Meta" if sys.platform == "darwin" else "Control"
                page.keyboard.press(f"{mod}+A"); page.keyboard.press("Backspace")
                perform_typing(str(text))
        except: pass
            
    def click_element(self, page, selector_or_loc):
        """Clicks an element with level-based delay and stability check."""
        try:
            if isinstance(selector_or_loc, str):
                ele = page.wait_for_selector(selector_or_loc, state="visible", timeout=5000)
            else:
                ele = selector_or_loc
            
            # Pre-click settle
            self.smart_wait(0.3, 0.7)
            
            if self.level == "HIGH":
                logger.info("Humanizer (HIGH): Performing slow hover before click...")
                try: ele.hover(timeout=2000)
                except: pass
                time.sleep(0.5)
                
            ele.click()
            # Post-click settle
            self.smart_wait(0.4, 0.8)
        except Exception as e:
            logger.error(f"Humanizer: Safe click failed: {e}")
            if isinstance(selector_or_loc, str): page.click(selector_or_loc)
            else: selector_or_loc.click()

    def check_captcha(self, page):
        """Checks for common captcha elements and logs/waits."""
        captcha_selectors = [
            "iframe[title*='reCAPTCHA']",
            "div.g-recaptcha",
            "iframe[src*='hcaptcha']",
            "text='Verify you are human'",
            "text='Cloudflare'"
        ]
        
        for sel in captcha_selectors:
            try:
                if page.locator(sel).first.is_visible():
                    logger.warning("--- CAPTCHA DETECTED --- Please solve manually in Chrome.")
                    return True
            except: pass
        return False
