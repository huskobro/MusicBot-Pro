"""
Use Playwright locator force=True to bypass AO overlay intercept.
"""
import os, time, json
from playwright.sync_api import sync_playwright

profile_path = os.path.expanduser("~/Documents/MusicBot_Workspace/chrome_profile")
persona_link = "https://suno.com/persona/b2484cf3-623e-4659-836b-fe2bb3ef3c5d"

audio_influence = 11
weirdness = 17
style_influence = 5

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=profile_path,
        headless=False,
        channel="chrome",
        args=["--disable-dev-shm-usage", "--no-sandbox"],
        viewport={"width": 1280, "height": 900}
    )
    
    tab = browser.pages[0]
    tab.goto(persona_link, wait_until="domcontentloaded")
    time.sleep(5)
    
    tab.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button, a'));
        const btn = btns.find(b => b.textContent.includes('Create') && b.textContent.includes('Persona'));
        if (btn) btn.click();
    }""")
    time.sleep(6)
    
    def set_slider(label, value):
        print(f"\n--- Setting {label} to {value}% ---")
        
        # Scroll into view
        tab.evaluate(r"""(args) => {
            const allEls = Array.from(document.querySelectorAll('div, span'));
            const labelEl = allEls.find(el => el.childNodes.length === 1 && el.textContent.trim() === args.label && el.offsetParent !== null);
            if (labelEl) labelEl.scrollIntoView({block: 'center'});
        }""", {"label": label})
        time.sleep(1)
        
        # Get percentage element coords
        coords = tab.evaluate(r"""(args) => {
            const allEls = Array.from(document.querySelectorAll('div, span'));
            const labelEl = allEls.find(el => el.childNodes.length === 1 && el.textContent.trim() === args.label && el.offsetParent !== null);
            if (!labelEl) return null;
            let row = labelEl.parentElement;
            for (let depth = 0; depth < 10 && row; depth++) {
                const pcts = Array.from(row.querySelectorAll('div, span'))
                    .filter(el => /^\d+%$/.test(el.textContent.trim()) && el.offsetParent !== null);
                if (pcts.length === 1) {
                    const rect = pcts[0].getBoundingClientRect();
                    return {x: rect.x + rect.width/2, y: rect.y + rect.height/2};
                }
                row = row.parentElement;
            }
            return null;
        }""", {"label": label})
        
        if not coords:
            print(f"    ❌ Not found")
            return
        
        print(f"    Coords: ({coords['x']:.0f}, {coords['y']:.0f})")
        
        # Use mouse.dblclick with position - Playwright still sends the actual mouse event
        # But we need to avoid the overlay. Use force by clicking at the exact position.
        # The trick: dispatch proper mouse events (mousedown, mouseup x2, dblclick) via CDP
        tab.evaluate(r"""(args) => {
            const allEls = Array.from(document.querySelectorAll('div, span'));
            const labelEl = allEls.find(el => el.childNodes.length === 1 && el.textContent.trim() === args.label && el.offsetParent !== null);
            if (!labelEl) return;
            let row = labelEl.parentElement;
            for (let depth = 0; depth < 10 && row; depth++) {
                const pcts = Array.from(row.querySelectorAll('div, span'))
                    .filter(el => /^\d+%$/.test(el.textContent.trim()) && el.offsetParent !== null);
                if (pcts.length === 1) {
                    const el = pcts[0];
                    const rect = el.getBoundingClientRect();
                    const cx = rect.x + rect.width/2;
                    const cy = rect.y + rect.height/2;
                    
                    // Simulate full mouse sequence: mousedown, mouseup, click, mousedown, mouseup, click, dblclick
                    const opts = {bubbles: true, cancelable: true, view: window, clientX: cx, clientY: cy, detail: 1};
                    el.dispatchEvent(new MouseEvent('mousedown', {...opts}));
                    el.dispatchEvent(new MouseEvent('mouseup', {...opts}));
                    el.dispatchEvent(new MouseEvent('click', {...opts}));
                    const opts2 = {...opts, detail: 2};
                    el.dispatchEvent(new MouseEvent('mousedown', opts2));
                    el.dispatchEvent(new MouseEvent('mouseup', opts2));
                    el.dispatchEvent(new MouseEvent('click', opts2));
                    el.dispatchEvent(new MouseEvent('dblclick', opts2));
                    return;
                }
                row = row.parentElement;
            }
        }""", {"label": label})
        time.sleep(0.5)
        
        # Check active element
        active = tab.evaluate("""() => {
            const a = document.activeElement;
            if (!a) return null;
            return {tag: a.tagName, type: a.type || null, value: a.value || null};
        }""")
        print(f"    Active: {json.dumps(active)}")
        
        if active and active.get('tag') == 'INPUT':
            tab.keyboard.press("Meta+A")
            time.sleep(0.1)
            tab.keyboard.type(str(value))
            tab.keyboard.press("Enter")
            time.sleep(1.5)
            print(f"    ✅ Typed into INPUT")
        else:
            print(f"    ❌ No INPUT active")
        
        # Verify
        final = tab.evaluate(r"""(args) => {
            const allEls = Array.from(document.querySelectorAll('div, span'));
            const labelEl = allEls.find(el => el.childNodes.length === 1 && el.textContent.trim() === args.label && el.offsetParent !== null);
            if (!labelEl) return 'not found';
            let row = labelEl.parentElement;
            for (let d = 0; d < 10 && row; d++) {
                const pcts = Array.from(row.querySelectorAll('div, span'))
                    .filter(el => /^\d+%$/.test(el.textContent.trim()) && el.offsetParent !== null);
                if (pcts.length === 1) return pcts[0].textContent.trim();
                row = row.parentElement;
            }
            return 'not found';
        }""", {"label": label})
        ok = "✅" if final == f"{value}%" else "❌"
        print(f"    {ok} Result: {final} (expected {value}%)")
    
    set_slider("Weirdness", weirdness)
    set_slider("Style Influence", style_influence)
    set_slider("Audio Influence", audio_influence)
    
    print("\n=== Browser open for 10s ===")
    time.sleep(10)
    browser.close()
