"""
Full integration test: lyrics, vocal gender, all sliders, verify AO text intact.
"""
import os, time, json
from playwright.sync_api import sync_playwright

profile_path = os.path.expanduser("~/Documents/MusicBot_Workspace/chrome_profile")
persona_link = "https://suno.com/persona/b2484cf3-623e-4659-836b-fe2bb3ef3c5d"

audio_influence = 11
weirdness = 17
style_influence = 5
vocal_gender = "Female"
lyrics_mode = "Manual"
test_lyrics = "This is a test lyric line\nWith multiple lines\nFor testing purposes"
test_style = "mellow piano, dark vibes"
test_title = "Test Song Title"

results = {}

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=profile_path,
        headless=False,
        channel="chrome",
        args=["--disable-dev-shm-usage", "--no-sandbox"],
        viewport={"width": 1280, "height": 900}
    )
    
    tab = browser.pages[0]
    
    # Navigate to persona page
    print("[1] Navigating to persona...")
    tab.goto(persona_link, wait_until="domcontentloaded")
    time.sleep(5)
    
    # Click "Create with Persona"
    print("[2] Clicking 'Create with Persona'...")
    tab.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button, a'));
        const btn = btns.find(b => b.textContent.includes('Create') && b.textContent.includes('Persona'));
        if (btn) btn.click();
    }""")
    time.sleep(6)
    
    # === LYRICS TEST ===
    print("\n[3] Testing Lyrics...")
    # Check if lyrics textarea is visible
    lyrics_area = tab.locator("textarea").first
    if lyrics_area.is_visible():
        lyrics_area.fill(test_lyrics)
        time.sleep(1)
        actual_lyrics = lyrics_area.input_value()
        ok = "✅" if test_lyrics in actual_lyrics else "❌"
        print(f"    {ok} Lyrics filled: {len(actual_lyrics)} chars")
        results['lyrics'] = test_lyrics in actual_lyrics
    else:
        print("    ❌ Lyrics textarea not found")
        results['lyrics'] = False
    
    # Style
    print("[4] Testing Style...")
    style_area = tab.locator("textarea[placeholder*='style' i]").first
    if style_area.is_visible():
        style_area.fill(test_style)
        time.sleep(1)
        actual_style = style_area.input_value()
        ok = "✅" if test_style in actual_style else "❌"
        print(f"    {ok} Style filled: '{actual_style}'")
        results['style'] = test_style in actual_style
    else:
        print("    ❌ Style textarea not found")
        results['style'] = False
    
    # Title
    print("[5] Testing Title...")
    title_input = tab.locator("input[placeholder*='Song Title' i]").first
    if title_input.is_visible():
        title_input.fill(test_title)
        time.sleep(1)
        actual_title = title_input.input_value()
        ok = "✅" if test_title in actual_title else "❌"
        print(f"    {ok} Title filled: '{actual_title}'")
        results['title'] = test_title in actual_title
    else:
        print("    ❌ Title input not found")
        results['title'] = False
    
    # === LYRICS MODE TEST ===
    print(f"\n[6] Testing Lyrics Mode ({lyrics_mode})...")
    tab.evaluate("""(mode) => {
        const btns = Array.from(document.querySelectorAll('button'));
        const btn = btns.find(b => b.textContent.trim() === mode && b.offsetParent !== null);
        if (btn) btn.click();
    }""", lyrics_mode)
    time.sleep(1)
    
    lyrics_mode_check = tab.evaluate("""(mode) => {
        const btns = Array.from(document.querySelectorAll('button'));
        const modeBtns = btns.filter(b => ['Manual','Auto'].includes(b.textContent.trim()) && b.offsetParent !== null);
        return modeBtns.map(b => ({
            text: b.textContent.trim(),
            bg: window.getComputedStyle(b).backgroundColor
        }));
    }""", lyrics_mode)
    selected = any(b['text'] == lyrics_mode and 'rgba(0, 0, 0, 0)' not in b['bg'] for b in lyrics_mode_check)
    ok = "✅" if selected else "❌"
    print(f"    {ok} {lyrics_mode} selected")
    for b in lyrics_mode_check:
        print(f"       {b['text']}: bg={b['bg']}")
    results['lyrics_mode'] = selected
    
    # === ADVANCED OPTIONS ===
    print(f"\n[7] Expanding Advanced Options...")
    exclude_visible = tab.evaluate("""() => {
        const inp = document.querySelector('input[placeholder*="Exclude" i]');
        return inp && inp.offsetParent !== null;
    }""")
    if not exclude_visible:
        tab.evaluate("""() => {
            const candidates = Array.from(document.querySelectorAll('div[role="button"]'));
            const advBtn = candidates.find(el => el.textContent.trim() === 'Advanced Options');
            if (advBtn) { advBtn.scrollIntoView({block:'center'}); advBtn.click(); }
        }""")
        time.sleep(3)
    
    # === VOCAL GENDER TEST ===
    print(f"\n[8] Testing Vocal Gender ({vocal_gender})...")
    tab.evaluate(r"""() => {
        const allEls = Array.from(document.querySelectorAll('div, span'));
        const labelEl = allEls.find(el => el.textContent.trim() === 'Vocal Gender' && el.childNodes.length <= 2 && el.offsetParent !== null);
        if (labelEl) labelEl.scrollIntoView({block: 'center'});
    }""")
    time.sleep(1)
    
    tab.evaluate("""(gender) => {
        const btns = Array.from(document.querySelectorAll('button'));
        const btn = btns.find(b => b.textContent.trim() === gender && b.offsetParent !== null);
        if (btn) btn.click();
    }""", vocal_gender)
    time.sleep(1)
    
    gender_check = tab.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        return btns.filter(b => ['Male','Female'].includes(b.textContent.trim()) && b.offsetParent !== null)
            .map(b => ({text: b.textContent.trim(), bg: window.getComputedStyle(b).backgroundColor}));
    }""")
    selected_gender = any(b['text'] == vocal_gender and 'rgba(0, 0, 0, 0)' not in b['bg'] for b in gender_check)
    ok = "✅" if selected_gender else "❌"
    print(f"    {ok} {vocal_gender} selected")
    for g in gender_check:
        print(f"       {g['text']}: bg={g['bg']}")
    results['vocal_gender'] = selected_gender
    
    # === SLIDERS ===
    def set_slider(label, value):
        print(f"\n[9] Setting {label} to {value}%...")
        
        # Scroll
        tab.evaluate(r"""(args) => {
            const allEls = Array.from(document.querySelectorAll('div, span'));
            const labelEl = allEls.find(el => el.childNodes.length === 1 && el.textContent.trim() === args.label && el.offsetParent !== null);
            if (labelEl) labelEl.scrollIntoView({block: 'center'});
        }""", {"label": label})
        time.sleep(1)
        
        # JS dblclick dispatch
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
        
        # Verify INPUT is active before typing (safety guard against black box)
        for retry in range(3):
            active_tag = tab.evaluate("() => document.activeElement ? document.activeElement.tagName : null")
            if active_tag == "INPUT":
                break
            print(f"    Retry {retry+1}: active={active_tag}, re-dispatching...")
            time.sleep(0.5)
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
                        const cx = rect.x + rect.width/2; const cy = rect.y + rect.height/2;
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
        
        if active_tag == "INPUT":
            tab.keyboard.press("Meta+A")
            time.sleep(0.1)
            tab.keyboard.type(str(value))
            tab.keyboard.press("Enter")
            time.sleep(1.5)
        else:
            print(f"    ⚠️ Skipping typing - active element is {active_tag}, not INPUT")
        
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
        print(f"    {ok} {label}: {final} (expected {value}%)")
        results[label] = (final == f"{value}%")
    
    set_slider("Weirdness", weirdness)
    set_slider("Style Influence", style_influence)
    set_slider("Audio Influence", audio_influence)
    
    # === VERIFY AO BUTTON TEXT (no black box) ===
    print(f"\n[10] Checking Advanced Options button text (black box check)...")
    ao_text = tab.evaluate("""() => {
        const candidates = Array.from(document.querySelectorAll('div[role="button"]'));
        const advBtn = candidates.find(el => el.textContent.includes('Advanced'));
        return advBtn ? advBtn.textContent.trim() : 'NOT FOUND';
    }""")
    ao_ok = "Advanced Options" in ao_text
    ok = "✅" if ao_ok else "❌"
    print(f"    {ok} AO button text: '{ao_text}'")
    results['ao_button_intact'] = ao_ok
    
    # === FINAL SUMMARY ===
    print("\n" + "="*50)
    print("FINAL RESULTS:")
    print("="*50)
    all_pass = True
    for key, val in results.items():
        status = "✅ PASS" if val else "❌ FAIL"
        print(f"  {status}  {key}")
        if not val: all_pass = False
    print("="*50)
    print(f"{'✅ ALL PASSED' if all_pass else '❌ SOME FAILED'}")
    
    print("\n=== Browser open for 20s for visual inspection ===")
    time.sleep(20)
    browser.close()
