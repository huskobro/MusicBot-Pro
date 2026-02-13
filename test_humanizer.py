from browser_controller import BrowserController
import time
import os

def test_fill_and_verify():
    h_conf = {
        "level": "HIGH",
        "speed": 1.0,
        "retries": 1,
        "adaptive": True
    }
    browser = BrowserController(headless=False, humanizer_config=h_conf)
    try:
        browser.start()
        # Use a simple local HTML file or a sandbox site
        test_url = "https://www.google.com"
        browser.goto(test_url)
        
        # Test search box
        selector = "textarea[name='q']"
        test_text = "MusicBot Humanizer Test"
        
        print(f"Testing Humanized Typing into {selector}...")
        browser.fill(selector, test_text)
        
        # Settle
        time.sleep(2)
        
        # Get value back
        val = browser.get_value(selector)
        print(f"Retrieved Value: '{val}'")
        
        if val == test_text:
            print("✅ SUCCESS: Typing and verification worked perfectly.")
        else:
            print("❌ FAILURE: Value mismatch.")
            
        time.sleep(3)
    except Exception as e:
        print(f"Test Error: {e}")
    finally:
        browser.stop()

if __name__ == "__main__":
    test_fill_and_verify()
