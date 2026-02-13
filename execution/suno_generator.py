
import time
import os
import logging
import openpyxl
import re
from browser_controller import BrowserController

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SunoGenerator:
    def __init__(self, project_file, output_dir="data/output", delay=10, startup_delay=5, browser=None,
                 audio_influence=25, vocal_gender="Default", lyrics_mode="Default", 
                 weirdness=50, style_influence=50, persona_link=""):
        self.project_file = project_file
        self.metadata_path = project_file # Backward compat
        
        self.output_dir = output_dir
        self.delay = delay
        self.startup_delay = startup_delay
        self.browser = browser if browser else BrowserController()
        self.tab = self.browser.get_page("suno")
        self.base_url = "https://suno.com/create"
        
        # Advanced Params
        self.audio_influence = audio_influence
        self.vocal_gender = vocal_gender
        self.lyrics_mode = lyrics_mode
        self.weirdness = weirdness
        self.style_influence = style_influence
        self.persona_link = str(persona_link).strip()
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def run(self, max_count=None, target_ids=None, progress_callback=None, force_update=False):
        try:
            if not self.browser.context:
                self.browser.start()
            
            if self.startup_delay > 0:
                if progress_callback: progress_callback("global", f"Waiting {self.startup_delay}s (Startup Delay)...")
                time.sleep(self.startup_delay)
            
            # --- Persona Workflow (Before reaching /create) ---
            if self.persona_link:
                success = self._setup_persona_workflow(progress_callback)
                if not success:
                    logger.warning("Persona workflow failed, falling back to direct navigation.")
                    self.browser.goto(self.base_url, page=self.tab)
            else:
                self.browser.goto(self.base_url, page=self.tab)
            
            time.sleep(5) # Wait for page structure

            # Always Ensure v5 for reliability
            self._ensure_v5_active()

            if "login" in self.tab.url or self.browser.is_visible("text='Log In'", page=self.tab):
                logger.warning("--- LOGIN REQUIRED ---")
                if progress_callback: progress_callback("global", "Login Required! Please check Chrome.")
                time.sleep(5)
            
            if "create" not in self.tab.url:
                self.browser.goto(self.base_url, page=self.tab)
                time.sleep(3)

            if not os.path.exists(self.metadata_path):
                logger.error("Results file not found.")
                return 0

            wb = openpyxl.load_workbook(self.metadata_path)
            ws = wb.active
            headers = {str(cell.value).lower(): cell.column - 1 for cell in ws[1] if cell.value}
            
            rows_data = []
            for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                status = str(row[headers.get('status', 0)]).lower() if 'status' in headers else ""
                if not force_update and ("done" in status or "generated" in status): 
                    continue
                
                row_dict = {key: row[idx] for key, idx in headers.items() if idx < len(row)}
                
                # Check target_ids
                rid = str(row_dict.get('id', ''))
                if target_ids and rid not in target_ids:
                    continue
                
                row_dict['_row_idx'] = i 
                rows_data.append(row_dict)
            
            if not rows_data:
                logger.info("Nothing to generate on Suno.")
                return 0

            if max_count and max_count > 0:
                rows_data = rows_data[:max_count]

            processed_count = 0
            for i, row_dict in enumerate(rows_data): 
                rid = str(row_dict.get('id', ''))
                
                if i > 0:
                    if progress_callback: progress_callback(rid, f"Waiting {self.delay}s...")
                    time.sleep(self.delay)
                
                self.update_row_status(row_dict['_row_idx'], "Processing")
                if progress_callback: progress_callback(rid, "Generating Music... 🎵")
                
                try:
                    success = self.process_row(row_dict, progress_callback=progress_callback)
                    if success:
                        self.update_row_status(row_dict['_row_idx'], "Generated")
                        if progress_callback: progress_callback(rid, "Music Generated! 🎵")
                        processed_count += 1
                    else:
                        self.update_row_status(row_dict['_row_idx'], "Failed")
                        if progress_callback: progress_callback(rid, "Generation Failed ❌")
                except Exception as row_error:
                    logger.error(f"Row error: {row_error}")
                    self.update_row_status(row_dict['_row_idx'], "Failed")
                    if progress_callback: progress_callback(rid, "Error ❌")

            return processed_count

        except Exception as e:
            logger.error(f"Suno error: {e}")
            raise e
        finally:
            logger.info("Suno finished.")

    def _setup_persona_workflow(self, progress_callback=None):
        """Navigates to persona page, clicks 'Create with Persona', and handles v5 modal."""
        try:
            logger.info(f"Navigating to Persona Link: {self.persona_link}")
            if progress_callback: progress_callback("global", "Navigating to Persona... 👤")
            self.browser.goto(self.persona_link, page=self.tab)
            time.sleep(5)

            # Click "Create with Persona" with retries
            clicked = False
            logger.info("Waiting for 'Create with Persona' button to become active...")
            for attempt in range(15): # 15 attempts * 2s = 30s max wait
                status = self.tab.evaluate("""() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    const btn = btns.find(b => {
                        const txt = (b.innerText || "").toLowerCase();
                        return txt.includes('create') && txt.includes('persona');
                    });
                    
                    if (btn) {
                        // Check if it's actually clickable (not disabled, visible)
                        const style = window.getComputedStyle(btn);
                        const isVisible = btn.offsetWidth > 0 && btn.offsetHeight > 0 && style.visibility !== 'hidden' && style.display !== 'none';
                        const isEnabled = !btn.disabled && btn.getAttribute('aria-disabled') !== 'true';
                        
                        if (isVisible && isEnabled) {
                            const evt = new MouseEvent('click', { bubbles: true, cancelable: true, view: window });
                            btn.dispatchEvent(evt);
                            btn.click();
                            return "clicked";
                        }
                        return "found_but_inactive";
                    }
                    return "not_found";
                }""")
                
                if status == "clicked":
                    clicked = True
                    break
                elif status == "found_but_inactive":
                    logger.info(f"Button found but not ready yet (Attempt {attempt+1}/15)...")
                
                time.sleep(2)

            if clicked:
                logger.info("Clicked 'Create with Persona'. Waiting for /create page...")
                time.sleep(5)
                # Handle "Store as persona" or "Switch to v5" modals if they appear
                self._handle_v5_switch_modal()
                return True
            else:
                logger.warning("'Create with Persona' button not found.")
                return False
        except Exception as e:
            logger.error(f"Persona workflow failed: {e}")
            return False

    def _handle_v5_switch_modal(self):
        """Clicks 'Switch to v5' if it appears in a modal."""
        try:
            # Modal buttons often have "Switch to v5" text
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
        except: pass

    def _ensure_v5_active(self):
        """Checks if v5 is active, if not, tries to switch."""
        try:
            # Look for version selector
            v_selector = self.tab.locator("button:has-text('v4'), button:has-text('v3')").first
            if v_selector.is_visible():
                logger.info("Non-v5 model detected. Switching to v5...")
                v_selector.click()
                time.sleep(1)
                v5_option = self.tab.locator("div[role='menuitem']:has-text('v5'), button:has-text('v5')").first
                if v5_option.is_visible():
                    v5_option.click()
                    time.sleep(2)
        except: pass


    def process_row(self, row, progress_callback=None):
        prompt = row.get("prompt", "")
        lyrics = row.get("lyrics", "")
        style = row.get("suno_style", "")
        if not str(style).strip():
            style = row.get("style", "")
        
        title = row.get("title", "Song")
        rid = str(row.get("id", "song"))
        content = lyrics if str(lyrics).strip() else prompt
        
        try:
            # --- Ensure Custom Mode ---
            if not self.tab.locator("text='Lyrics'").first.is_visible():
                logger.info("Custom mode not detected, clicking 'Custom'...")
                custom_btn = self.tab.locator("button:has-text('Custom')").first
                if custom_btn.is_visible():
                    custom_btn.click()
                    time.sleep(3)
            
            # Ensure we are indeed in custom mode
            textareas = [t for t in self.tab.locator("textarea").all() if t.is_visible()]
            if not textareas: 
                logger.error("No textareas found on Suno.")
                return False

            # Fills
            input_title = None
            title_loc = self.tab.locator("input[placeholder*='title' i]")
            for i in range(title_loc.count()):
                if title_loc.nth(i).is_visible():
                    input_title = title_loc.nth(i)
                    break
            
            if not input_title:
                title_loc_alt = self.tab.locator("input[aria-label*='title' i]")
                for i in range(title_loc_alt.count()):
                    if title_loc_alt.nth(i).is_visible():
                        input_title = title_loc_alt.nth(i)
                        break

            def fill_field(el, val):
                if not el or val is None: return
                try:
                    logger.info(f"Filling field with: {str(val)[:20]}...")
                    el.scroll_into_view_if_needed()
                    time.sleep(1)
                    el.fill(str(val))
                    time.sleep(1)
                except Exception as fe:
                    logger.warning(f"Native fill failed, trying keyboard: {fe}")
                    try:
                        el.click()
                        self.tab.keyboard.press("Control+A")
                        self.tab.keyboard.press("Meta+A")
                        self.tab.keyboard.press("Backspace")
                        self.tab.keyboard.type(str(val), delay=30)
                    except: pass

            fill_field(textareas[0], content)
            style_textarea = self.tab.locator("textarea[placeholder*='style' i]").first
            if style_textarea.is_visible():
                fill_field(style_textarea, style)
            elif len(textareas) > 1:
                fill_field(textareas[1], style)
            
            if input_title:
                fill_field(input_title, title)

            # --- Persona & Advanced Options Setup ---
            self._setup_lyrics_mode()
            self._setup_advanced_options()

            # Click Create
            create_btn = self.tab.locator("button:has-text('Create')").filter(has_not_text="Custom").last
            if not create_btn.is_visible():
                create_btn = self.tab.get_by_role("button", name="Create").last

            if create_btn.is_enabled():
                logger.info(f"Clicking Create for: {title}")
                create_btn.click()
                time.sleep(10) # Wait for generation to start
                
                logger.info(f"Triggering dual download for {rid}...")
                s1 = self._wait_and_download(title, rid, progress_callback, index=0, suffix="1")
                s2 = self._wait_and_download(title, rid, progress_callback, index=1, suffix="2")
                
                return s1 or s2
            
            logger.error("Create button not enabled or not found.")
            return False
        except Exception as e:
            logger.error(f"process_row failed: {e}")
            return False

    def _wait_and_download(self, title, rid, progress_callback=None, index=0, suffix="1"):
        try:
            logger.info(f"Waiting for {title} (ID: {rid}) to finish generating (Row Index: {index})...")
            if progress_callback: progress_callback(rid, "Generating Music... (Polling) ⏳")
            
            found_ready = False
            for attempt in range(120):
                try:
                    rows = self.tab.locator("div.clip-row")
                    if rows.count() > index:
                        target_row = rows.nth(index)
                        if target_row.is_visible():
                            if not target_row.locator("text='Generating'").is_visible():
                                duration_loc = target_row.locator("text=/\\d{1,2}:\\d{2}/")
                                if duration_loc.count() > 0 and duration_loc.first.is_visible():
                                    found_ready = True
                                    break
                except: pass
                time.sleep(5)
            
            if not found_ready:
                return False

            if progress_callback: progress_callback(rid, "Downloading Audio... ⬇️")
            self.tab.keyboard.press("Escape")
            time.sleep(1)

            try:
                rows = self.tab.locator("div.clip-row")
                if rows.count() <= index: return True
                target_row = rows.nth(index)
                target_row.click()
                time.sleep(1)

                target_more = target_row.locator("button[aria-label*='More' i]").first
                if not target_more.is_visible():
                    target_more = target_row.locator("button.context-menu-button").last

                if not target_more.is_visible(): return False

                target_more.scroll_into_view_if_needed()
                time.sleep(1)
                target_more.click()
                time.sleep(2)
                
                target_dl = self.tab.locator("button:has-text('Download')").first
                if not target_dl.is_visible():
                    target_dl = self.tab.get_by_text("Download", exact=True).first
                
                if not target_dl.is_visible(): return False

                target_dl.hover()
                time.sleep(1.5)
                
                target_audio = None
                for _ in range(5):
                    loc = self.tab.locator("button[aria-label*='WAV' i]").first
                    if loc.is_visible():
                        target_audio = loc
                        break
                    time.sleep(1)
                
                if not target_audio or not target_audio.is_visible():
                    target_audio = self.tab.locator("button[aria-label*='MP3' i]").first
                
                if not target_audio or not target_audio.is_visible():
                    target_audio = self.tab.locator("button:has-text('Audio')").first

                if not target_audio.is_visible(): return False

                ext = "wav" if "wav" in (target_audio.get_attribute("aria-label") or "").lower() else "mp3"
                target_audio.click()
                time.sleep(2)
                
                final_btn = self.tab.locator("button:has-text('Download File')").first
                target_click = final_btn if final_btn.is_visible() else None

                with self.tab.expect_download(timeout=120000) as download_info:
                    if target_click: target_click.click()
                
                download = download_info.value
                clean_title = re.sub(r'[^\w\s-]', '', title).strip()
                clean_title = re.sub(r'[-\s]+', '_', clean_title)
                filename = f"{rid}_{clean_title}_{suffix}.{ext}"
                save_path = os.path.join(self.output_dir, filename)
                download.save_as(save_path)
                return True
                
            except: return True 
                
        except: return True

    def close(self): pass

    def _setup_lyrics_mode(self):
        if self.lyrics_mode == "Default": return
        try:
            self.tab.evaluate(f"""(mode) => {{
                const btns = Array.from(document.querySelectorAll('button'));
                const target = btns.find(b => b.innerText.trim() === mode);
                if (target) target.click();
            }}""", self.lyrics_mode)
            time.sleep(1)
        except: pass

    def _setup_advanced_options(self):
        try:
            logger.info("Expanding Advanced Options panel...")
            
            for attempt in range(3):
                # Check if already expanded
                exclude_visible = self.tab.evaluate("""() => {
                    const inp = document.querySelector('input[placeholder*="Exclude" i]');
                    return inp && inp.offsetParent !== null;
                }""")
                
                if exclude_visible:
                    logger.info("Advanced Options already expanded.")
                    break
                
                # Click the Advanced Options div[role=button] — exact text match
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
            
            # Verify
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

            # Slider helper: dispatch JS mouse events to open inline input, type value
            # NOTE: Playwright mouse.dblclick doesn't work because the Advanced Options
            # container overlay intercepts pointer events. We dispatch mouse events
            # directly on the percentage element via JS to bypass this.
            def set_numeric_value(label_text, target_val):
                if target_val == "Default" or target_val is None: return
                try:
                    logger.info(f"Setting {label_text} to {target_val}%...")
                    
                    # Scroll the label into view
                    self.tab.evaluate(r"""(args) => {
                        const allEls = Array.from(document.querySelectorAll('div, span'));
                        const labelEl = allEls.find(el => 
                            el.childNodes.length === 1 && 
                            el.textContent.trim() === args.label &&
                            el.offsetParent !== null
                        );
                        if (labelEl) labelEl.scrollIntoView({ block: 'center' });
                    }""", {"label": label_text})
                    time.sleep(1)
                    
                    # Dispatch full mouse event sequence directly on the percentage element
                    # This bypasses the AO overlay interception
                    self.tab.evaluate(r"""(args) => {
                        const allEls = Array.from(document.querySelectorAll('div, span'));
                        const labelEl = allEls.find(el => 
                            el.childNodes.length === 1 && 
                            el.textContent.trim() === args.label &&
                            el.offsetParent !== null
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
                    
                    # Select all and type the new value into the inline input
                    self.tab.keyboard.press("Meta+A")
                    time.sleep(0.1)
                    self.tab.keyboard.type(str(target_val))
                    self.tab.keyboard.press("Enter")
                    time.sleep(1.5)
                    logger.info(f"Set {label_text} to {target_val}%")
                except Exception as e:
                    logger.warning(f"Error setting {label_text}: {e}")

            if self.persona_link:
                set_numeric_value("Audio Influence", self.audio_influence)
            set_numeric_value("Weirdness", self.weirdness)
            set_numeric_value("Style Influence", self.style_influence)
        except Exception as e:
            logger.warning(f"Advanced options error: {e}")

    def update_row_status(self, row_idx, status):
        try:
            wb = openpyxl.load_workbook(self.metadata_path)
            ws = wb.active
            status_col = None
            for cell in ws[1]:
                if str(cell.value).lower() == "status": status_col = cell.column
            if not status_col: 
                status_col = ws.max_column + 1
                ws.cell(row=1, column=status_col, value="status")
            ws.cell(row=row_idx, column=status_col, value=status)
            wb.save(self.metadata_path)
        except: pass

if __name__ == "__main__":
    suno = SunoGenerator()
    suno.run()
