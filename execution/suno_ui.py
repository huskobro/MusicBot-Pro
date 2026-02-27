"""
UI interaction mixin for SunoGenerator.
Handles persona workflow, v5 switching, advanced options, lyrics mode,
captcha detection, and alert sounds.
"""
import os
import sys
import time
import json
import logging

logger = logging.getLogger(__name__)


class SunoUIMixin:
    """Suno website UI interactions: persona, advanced options, captcha, alerts."""

    def _setup_persona_workflow(self, progress_callback=None):
        """Navigates to persona page, clicks 'Create with Persona', and handles v5 modal."""
        try:
            logger.info(f"Navigating to Persona Link: {self.persona_link}")
            if progress_callback: progress_callback("global", "Persona Profili Seçiliyor... 👤")
            self.browser.goto(self.persona_link, page=self.tab)
            time.sleep(3 if self.turbo else 5)

            def find_and_click():
                return self.tab.evaluate("""() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    const btn = btns.find(b => {
                        const txt = (b.innerText || "").toLowerCase();
                        return txt.includes('create') && txt.includes('persona');
                    });
                    
                    if (btn) {
                        const style = window.getComputedStyle(btn);
                        const isVisible = btn.offsetWidth > 0 && btn.offsetHeight > 0 && style.visibility !== 'hidden' && style.display !== 'none';
                        const isEnabled = !btn.disabled && btn.getAttribute('aria-disabled') !== 'true';
                        
                        if (isVisible && isEnabled) {
                            btn.click();
                            return "clicked";
                        }
                        return "found_but_inactive";
                    }
                    return "not_found";
                }""")

            clicked = False
            logger.info("Waiting for 'Create with Persona' button...")

            for attempt in range(5):
                status = find_and_click()
                if status == "clicked":
                    clicked = True
                    break
                elif status == "found_but_inactive":
                    logger.info(f"Button found but not ready yet (Attempt {attempt+1}/5)...")
                time.sleep(3)

            if not clicked:
                logger.warning("'Create with Persona' button not found or inactive. Refreshing page in 3s...")
                time.sleep(3)
                self.browser.goto(self.persona_link, page=self.tab)
                time.sleep(5)

                logger.info("Searching for button again after refresh...")
                for attempt in range(10):
                    status = find_and_click()
                    if status == "clicked":
                        clicked = True
                        break
                    time.sleep(3)

            if clicked:
                logger.info("Clicked 'Create with Persona'. Waiting for /create page...")
                time.sleep(5)
                self._handle_v5_switch_modal()
                return True
            else:
                logger.warning("'Create with Persona' button not found after refresh and retries.")
                return False
        except Exception as e:
            logger.error(f"Persona workflow failed: {e}")
            return False

    def _handle_v5_switch_modal(self):
        """Clicks 'Switch to v5' if it appears in a modal."""
        try:
            switched = self.tab.evaluate("""() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const switchBtn = btns.find(b => {
                    const txt = b.innerText || "";
                    return txt.includes('Switch to v5');
                });
                if (switchBtn) {
                    switchBtn.click();
                    return true;
                }
                return false;
            }""")
            if switched:
                logger.info("Handled 'Switch to v5' modal.")
                time.sleep(2)
        except Exception: pass

    def _ensure_v5_active(self):
        """Checks if v5 is active, if not, tries to switch."""
        try:
            v_selector = self.tab.locator("button:has-text('v4'), button:has-text('v3')").first
            if v_selector.is_visible():
                logger.info("Non-v5 model detected. Switching to v5...")
                v_selector.click()
                time.sleep(1)
                v5_option = self.tab.locator("div[role='menuitem']:has-text('v5'), button:has-text('v5')").first
                if v5_option.is_visible():
                    v5_option.click()
                    time.sleep(2)
        except Exception: pass

    def _setup_lyrics_mode(self):
        if self.lyrics_mode == "Default": return
        try:
            self.tab.evaluate(f"""(mode) => {{
                const btns = Array.from(document.querySelectorAll('button'));
                const target = btns.find(b => b.innerText.trim() === mode);
                if (target) target.click();
            }}""", self.lyrics_mode)
            time.sleep(1)
        except Exception: pass

    def _setup_advanced_options(self):
        try:
            logger.info("Expanding Advanced Options panel...")

            for attempt in range(3):
                exclude_visible = self.tab.evaluate("""() => {
                    const inp = document.querySelector('input[placeholder*="Exclude" i]');
                    return inp && inp.offsetParent !== null;
                }""")

                if exclude_visible:
                    logger.info("Advanced Options already expanded.")
                    break

                clicked = self.tab.evaluate("""() => {
                    const candidates = Array.from(document.querySelectorAll('div[role="button"]'));
                    const advBtn = candidates.find(el => el.textContent.trim() === 'Advanced Options');
                    if (advBtn) {
                        advBtn.scrollIntoView({ block: 'center' });
                        advBtn.click();
                        return true;
                    }
                    return false;
                }""")

                if clicked:
                    logger.info(f"Clicked Advanced Options (attempt {attempt+1})")
                    time.sleep(3)
                else:
                    logger.warning(f"Advanced Options button not found (attempt {attempt+1})")
                    time.sleep(2)

            exclude_visible = self.tab.evaluate("""() => {
                const inp = document.querySelector('input[placeholder*="Exclude" i]');
                return inp && inp.offsetParent !== null;
            }""")
            if not exclude_visible:
                logger.warning("Advanced Options panel did NOT expand.")
                return

            # Vocal Gender
            if self.vocal_gender != "Default":
                self.tab.evaluate(f"""(gender) => {{
                    const btns = Array.from(document.querySelectorAll('button'));
                    const target = btns.find(b => b.innerText.trim() === gender);
                    if (target) target.click();
                }}""", self.vocal_gender)
                time.sleep(1)

            def set_numeric_value(label_text, target_val):
                if target_val == "Default" or target_val is None: return
                try:
                    logger.info(f"Setting {label_text} to {target_val}%...")

                    ready = self.tab.evaluate(r"""(args) => {
                        return new Promise((resolve) => {
                            const check = () => {
                                const allEls = Array.from(document.querySelectorAll('div, span'));
                                const labelEl = allEls.find(el => 
                                    el.childNodes.length === 1 && 
                                    el.textContent.trim() === args.label &&
                                    el.offsetParent !== null
                                );
                                if (!labelEl) return false;
                                let row = labelEl.parentElement;
                                for (let depth = 0; depth < 10 && row; depth++) {
                                    const pcts = Array.from(row.querySelectorAll('div, span'))
                                        .filter(el => /^\d+%$/.test(el.textContent.trim()) && el.offsetParent !== null);
                                    if (pcts.length === 1) return true;
                                    row = row.parentElement;
                                }
                                return false;
                            };
                            if (check()) resolve(true);
                            else {
                                let count = 0;
                                const interval = setInterval(() => {
                                    if (check() || ++count > 20) {
                                        clearInterval(interval);
                                        resolve(check());
                                    }
                                }, 500);
                            }
                        });
                    }""", {"label": label_text})

                    if not ready:
                        logger.warning(f"Slider/Label for {label_text} not found or not ready.")
                        return

                    for main_retry in range(3):
                        self.tab.keyboard.press("Escape")
                        time.sleep(0.3)

                        self.tab.evaluate(r"""(args) => {
                            const allEls = Array.from(document.querySelectorAll('div, span'));
                            const labelEl = allEls.find(el => 
                                el.childNodes.length === 1 && el.textContent.trim() === args.label && el.offsetParent !== null
                            );
                            if (labelEl) labelEl.scrollIntoView({ block: 'center' });
                        }""", {"label": label_text})
                        time.sleep(1)

                        input_ready = False
                        for retry in range(4):
                            self.tab.evaluate(r"""(args) => {
                                const allEls = Array.from(document.querySelectorAll('div, span'));
                                const labelEl = allEls.find(el => 
                                    el.childNodes.length === 1 && el.textContent.trim() === args.label && el.offsetParent !== null
                                );
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
                            }""", {"label": label_text})
                            time.sleep(0.5)

                            active_info = self.tab.evaluate("""() => {
                                const a = document.activeElement;
                                return a ? { tag: a.tagName } : null;
                            }""")

                            if active_info and active_info['tag'] == "INPUT":
                                input_ready = True
                                break

                            if active_info and active_info['tag'] == "DIV":
                                self.tab.keyboard.press("Escape")
                                time.sleep(0.3)

                        if input_ready:
                            self.tab.keyboard.press(f"{self.mod}+A")
                            time.sleep(0.1)
                            h_enabled = getattr(self.browser, "humanizer_enabled", True)
                            if self.turbo or not h_enabled:
                                self.tab.keyboard.type(str(target_val), delay=0)
                            else:
                                self.tab.keyboard.type(str(target_val), delay=100)
                            self.tab.keyboard.press("Enter")
                            time.sleep(2)

                            current_val = self.tab.evaluate(r"""(args) => {
                                const allEls = Array.from(document.querySelectorAll('div, span'));
                                const lEl = allEls.find(el => el.childNodes.length === 1 && el.textContent.trim() === args.label && el.offsetParent !== null);
                                if (!lEl) return null;
                                let row = lEl.parentElement;
                                for (let d = 0; d < 10 && row; d++) {
                                    const p = Array.from(row.querySelectorAll('div, span'))
                                        .filter(el => /^\d+%$/.test(el.textContent.trim()) && el.offsetParent !== null);
                                    if (p.length === 1) return p[0].textContent.trim();
                                    row = row.parentElement;
                                }
                                return null;
                            }""", {"label": label_text})

                            if current_val == f"{target_val}%":
                                logger.info(f"Successfully set {label_text} to {target_val}%")
                                return
                            else:
                                logger.warning(f"Value mismatch for {label_text}: got {current_val}, expected {target_val}%. Retrying (attempt {main_retry+1})...")
                        else:
                            logger.warning(f"Could not activate input for {label_text} on attempt {main_retry+1}")

                    logger.error(f"Failed to set {label_text} correctly after all retries.")
                except Exception as e:
                    logger.warning(f"Error setting {label_text}: {e}")

            if self.persona_link:
                if self.audio_influence != "Default":
                    set_numeric_value("Audio Influence", self.audio_influence)
            
            if self.weirdness != "Default":
                set_numeric_value("Weirdness", self.weirdness)
            
            if self.style_influence != "Default":
                set_numeric_value("Style Influence", self.style_influence)

            # FINAL VERIFICATION
            final_check = self.tab.evaluate(r"""() => {
                const results = {};
                const labels = ["Audio Influence", "Weirdness", "Style Influence"];
                const allEls = Array.from(document.querySelectorAll('div, span'));
                
                labels.forEach(label => {
                    const labelEl = allEls.find(el => el.childNodes.length === 1 && el.textContent.trim() === label && el.offsetParent !== null);
                    if (labelEl) {
                        let row = labelEl.parentElement;
                        for (let depth = 0; depth < 10 && row; depth++) {
                            const pcts = Array.from(row.querySelectorAll('div, span'))
                                .filter(el => /^\d+%$/.test(el.textContent.trim()) && el.offsetParent !== null);
                            if (pcts.length === 1) {
                                results[label] = pcts[0].textContent.trim();
                                break;
                            }
                            row = row.parentElement;
                        }
                    }
                });
                
                const btns = Array.from(document.querySelectorAll('button'));
                const genderBtns = btns.filter(b => ['Male', 'Female'].includes(b.textContent.trim()) && b.offsetParent !== null);
                genderBtns.forEach(b => {
                    const bg = window.getComputedStyle(b).backgroundColor;
                    if (bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
                        results['Vocal Gender'] = b.textContent.trim();
                    }
                });
                
                return results;
            }""")
            logger.info(f"Advanced Options verification: {json.dumps(final_check)}")
        except Exception as e:
            logger.warning(f"Advanced options error: {e}")

    def _detect_captcha(self):
        """Checks for known Cloudflare / hCaptcha elements."""
        captcha_selectors = [
            "iframe[title*='challenge']",
            "div#turnstile-wrapper",
            "iframe[src*='cloudflare-static']",
            "iframe[src*='hcaptcha']",
            "iframe[src*='recaptcha']",
            "#cf-turnstile-wrapper",
            ".cf-turnstile-wrapper",
            "div:has-text('Verify you are human')"
        ]
        for sel in captcha_selectors:
            try:
                if self.tab.locator(sel).is_visible(timeout=300):
                    return True
            except Exception: pass
        return False

    def _play_alert(self):
        """Plays a notification sound based on OS."""
        try:
            if sys.platform == "darwin":
                os.system("afplay /System/Library/Sounds/Glass.aiff &")
            elif sys.platform == "win32":
                import winsound
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        except Exception: pass
