
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
                 weirdness=50, style_influence=50, persona_name=""):
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
        self.persona_name = persona_name
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def run(self, max_count=None, target_ids=None, progress_callback=None, force_update=False):
        try:
            if not self.browser.context:
                self.browser.start()
            
            if self.startup_delay > 0:
                if progress_callback: progress_callback("global", f"Waiting {self.startup_delay}s (Startup Delay)...")
                time.sleep(self.startup_delay)
            
            self.browser.goto(self.base_url, page=self.tab)
            time.sleep(5) # Increased wait for Suno load

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
            for i, row_dict in enumerate(rows_data): # Changed row to row_dict for clarity
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

    def process_row(self, row, progress_callback=None):
        prompt = row.get("prompt", "")
        lyrics = row.get("lyrics", "")
        # Priority: suno_style (Gemini suggested) > style (User provided)
        style = row.get("suno_style", "")
        if not str(style).strip():
            style = row.get("style", "")
        
        # --- Persona Integration ---
        # We will handle persona via the formal Suno UI selection in _setup_persona().
        # However, we keep a fallback or allow the user to still see it in the style if they want, 
        # but the primary goal is the official UI selection.
        
        title = row.get("title", "Song")
        rid = str(row.get("id", "song"))
        
        content = lyrics if str(lyrics).strip() else prompt
        
        try:
            # --- Ensure Custom Mode ---
            # Check for "Lyrics" text to distinguish from "Simple" mode
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
            
            # If still None, try a broader search within the Create column
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
                    # Try native fill first as it's most reliable for clearing/setting
                    el.fill(str(val))
                    time.sleep(1)
                except Exception as fe:
                    logger.warning(f"Native fill failed, trying keyboard: {fe}")
                    try:
                        el.click()
                        self.tab.keyboard.press("Control+A")
                        self.tab.keyboard.press("Meta+A") # Mac support
                        self.tab.keyboard.press("Backspace")
                        self.tab.keyboard.type(str(val), delay=30)
                    except: pass

            # 1. Lyrics/Prompt
            # Usually the first visible textarea
            fill_field(textareas[0], content)
            
            # 2. Style (Target by placeholder for stability)
            style_textarea = self.tab.locator("textarea[placeholder*='style' i]").first
            if style_textarea.is_visible():
                fill_field(style_textarea, style)
            elif len(textareas) > 1:
                fill_field(textareas[1], style)
            
            # 3. Title (Critical: Scroll and Fill)
            if input_title:
                fill_field(input_title, title)
            else:
                logger.warning("Could not find visible Song Title input field.")

            # --- Persona Setup --- (Moved here for better UI flow)
            self._setup_persona()
            
            # --- Advanced Options Setup ---
            self._setup_advanced_options()

            # Click Create
            create_btn = self.tab.locator("button:has-text('Create')").filter(has_not_text="Custom").last
            if not create_btn.is_visible():
                create_btn = self.tab.get_by_role("button", name="Create").last

            if create_btn.is_enabled():
                logger.info(f"Clicking Create for: {title}")
                create_btn.click()
                time.sleep(10) # Wait for generation to start
                
                # NEW: Wait and Download BOTH versions
                # Suno generates 2 versions. We'll try to download both.
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
        """Polls for completion and triggers download via context menu. index=0 for top song."""
        try:
            logger.info(f"Waiting for {title} (ID: {rid}) to finish generating (Row Index: {index})...")
            if progress_callback: progress_callback(rid, "Generating Music... (Polling) ⏳")
            
            # Polling loop (Up to 10 minutes)
            found_ready = False
            for attempt in range(120): # 120 * 5s = 600s
                try:
                    # Look for the specific song row in the library (right side)
                    rows = self.tab.locator("div.clip-row")
                    if rows.count() > index:
                        target_row = rows.nth(index)
                        if target_row.is_visible():
                            # Duration check as suggested by user
                            if not target_row.locator("text='Generating'").is_visible():
                                duration_loc = target_row.locator("text=/\\d{1,2}:\\d{2}/")
                                if duration_loc.count() > 0 and duration_loc.first.is_visible():
                                    logger.info(f"Detected duration: {duration_loc.first.inner_text()}")
                                    found_ready = True
                                    break
                    elif attempt > 10: # If row not found after some time
                        logger.warning(f"Row index {index} not found yet.")
                except Exception as pe:
                    logger.debug(f"Polling check failed: {pe}")
                time.sleep(5)
            
            if not found_ready:
                logger.warning("Generation timed out or could not detect completion safely.")
                return False

            if progress_callback: progress_callback(rid, "Downloading Audio... ⬇️")
            
            # NEW: Deselect everything first to ensure context menu shows 'Download'
            # Pressing Escape usually deselects in Suno, or clicking a neutral area.
            logger.info("Deselecting previous items for clean download menu...")
            self.tab.keyboard.press("Escape")
            time.sleep(1)

            # Find the "More" button of the target item
            try:
                rows = self.tab.locator("div.clip-row")
                if rows.count() <= index:
                     logger.error(f"Row {index} disappeared during download phase.")
                     return True
                
                target_row = rows.nth(index)
                
                # Explicitly click the row first to select ONLY this one
                target_row.click()
                time.sleep(1)

                # Avoid strict mode violation by being more specific
                target_more = target_row.locator("button[aria-label*='More' i]").first
                
                if not target_more.is_visible():
                    # Try by class if aria-label fails
                    target_more = target_row.locator("button.context-menu-button").last

                if not target_more.is_visible():
                    logger.error(f"Could not find visible 'More' button for row {index}.")
                    return False

                logger.info(f"Clicking 'More' menu for row {index}...")
                target_more.scroll_into_view_if_needed()
                time.sleep(1)
                target_more.click()
                time.sleep(2)
                
                # 2. Find "Download" in the context menu
                target_dl = self.tab.locator("button:has-text('Download')").first
                if not target_dl.is_visible():
                    target_dl = self.tab.get_by_text("Download", exact=True).first
                
                if not target_dl.is_visible():
                    logger.error("Could not find 'Download' menu item.")
                    return False

                logger.info("Hovering 'Download'...")
                target_dl.hover()
                time.sleep(1.5)
                
                # 3. Target WAV first, then MP3 (with retry for WAV availability)
                target_audio = None
                for _ in range(5): # 5 retries for WAV item to appear (Suno can be slow)
                    loc = self.tab.locator("button[aria-label*='WAV' i]").first
                    if loc.is_visible():
                        target_audio = loc
                        logger.info("Targeting WAV format.")
                        break
                    time.sleep(1)
                
                if not target_audio or not target_audio.is_visible():
                    logger.warning("WAV Audio not found in menu after retries, trying MP3...")
                    target_audio = self.tab.locator("button[aria-label*='MP3' i]").first
                
                if not target_audio or not target_audio.is_visible():
                    # Last ditch effort: any button with 'Audio'
                    target_audio = self.tab.locator("button:has-text('Audio')").first

                if not target_audio.is_visible():
                    logger.error("Could not find any download button (WAV or MP3).")
                    return False

                # Determine extension based on what we clicked (simple guess)
                ext = "wav" if "wav" in (target_audio.get_attribute("aria-label") or "").lower() else "mp3"
                
                logger.info(f"Clicking {ext.upper()} option...")
                target_audio.click()
                time.sleep(2) # Wait for potential modal
                
                # NEW: Check for "Download File" button in modal
                final_btn = self.tab.locator("button:has-text('Download File')").first
                if final_btn.is_visible():
                    logger.info("Found 'Download File' modal button. Clicking...")
                    target_click = final_btn
                else:
                    # If no modal, we assume the previous click started the download
                    # But since we clicked it, we might have missed the expect_download start.
                    # Let's wrap the logic properly.
                    target_click = None

                logger.info(f"Triggering final download for {ext.upper()}...")
                # Setup download listener
                with self.tab.expect_download(timeout=120000) as download_info:
                    if target_click:
                        target_click.click()
                    else:
                        # If we already clicked and it was a direct download, it might have failed.
                        # Re-click if needed? Or just assume it works.
                        # For WAV, we know it's a modal.
                        pass
                
                download = download_info.value
                
                # Sanitize title for filename
                clean_title = re.sub(r'[^\w\s-]', '', title).strip()
                clean_title = re.sub(r'[-\s]+', '_', clean_title)
                filename = f"{rid}_{clean_title}_{suffix}.{ext}"
                
                save_path = os.path.join(self.output_dir, filename)
                download.save_as(save_path)
                logger.info(f"Successfully downloaded to: {save_path}")
                return True
                
            except Exception as dl_err:
                logger.error(f"Download interaction failed: {dl_err}")
                return True 
                
        except Exception as e:
            logger.error(f"Wait/Download error: {e}")
            return True

    def close(self):
        # Browser is shared, don't stop here
        pass

    def _setup_persona(self):
        """Handles the formal Persona selection via Suno's '+ Persona' modal."""
        if not self.persona_name or not str(self.persona_name).strip():
            return

        target_persona = str(self.persona_name).strip()
        
        # If persona is "Default", we treat it as no persona requested.
        if target_persona.lower() == "default":
            logger.info("Persona is set to 'Default', ensuring modal is closed and skipping selection.")
            try:
                # Safety: Check if modal is accidentally open and close it
                modal = self.tab.locator("div[role='dialog']").first
                if modal.is_visible():
                    self.tab.keyboard.press("Escape")
                    time.sleep(1)
            except: pass
            return

        try:
            # 1. Check if a persona is already selected
            add_btn = self.tab.locator("button[aria-label='Add Persona']").first
            if not add_btn.is_visible():
                # Check if the right persona is already there
                if self.tab.locator(f"div:has-text('{target_persona}')").count() > 0:
                    logger.info(f"Persona '{target_persona}' is already selected.")
                    return
                else:
                    logger.info("A different persona is selected. Removing it...")
                    # Find remove button. Usually an 'x' or close icon in the card.
                    remove_btn = self.tab.locator("button:has([data-icon='x'])").first
                    if remove_btn.is_visible():
                        remove_btn.click()
                        time.sleep(1)

            # 2. Click "+ Persona"
            if add_btn.is_visible():
                logger.info(f"Opening Persona modal to select: {target_persona}")
                add_btn.click()
                time.sleep(2)
                
                # 3. Find and select in modal
                # Wait for modal content
                modal = self.tab.locator("div[role='dialog']")
                if modal.is_visible():
                    item = modal.locator(f"text='{target_persona}'").first
                    if item.is_visible():
                        item.click()
                        logger.info(f"Selected persona: {target_persona}")
                        time.sleep(2)
                    else:
                        logger.warning(f"Persona '{target_persona}' not found in modal.")
                        # Close modal by clicking outside or escape
                        self.tab.keyboard.press("Escape")
        except Exception as e:
            logger.warning(f"Persona setup failed: {e}")

    def _setup_advanced_options(self):
        """Sets up the 'Advanced Options' panel in Suno using robust selectors and interaction."""
        try:
            # 1. Expand Panel
            logger.info("Checking Advanced Options panel...")
            adv_btn = self.tab.locator("div[role='button']:has-text('Advanced Options'), button:has-text('Advanced Options')").first
            
            if adv_btn.is_visible():
                adv_btn.scroll_into_view_if_needed()
                # Check visibility of a sub-element to see if already expanded
                exclude_input = self.tab.locator("input[placeholder*='Exclude' i]").first
                if not exclude_input.is_visible():
                    logger.info("Advanced Options not expanded. Clicking...")
                    adv_btn.click(force=True)
                    time.sleep(2)
                else:
                    logger.info("Advanced Options already expanded.")
            else:
                logger.warning("Advanced Options button not found on screen.")
            
            # Double check expansion
            exclude_input = self.tab.locator("input[placeholder*='Exclude' i]").first
            if not exclude_input.is_visible():
                logger.warning("Panel still not visible, trying one more click...")
                adv_btn.click(force=True)
                time.sleep(2)

            # 2. Vocal Gender
            if self.vocal_gender != "Default":
                logger.info(f"Setting Vocal Gender to: {self.vocal_gender}")
                # Primary target: button with a span matching the text
                gender_btn = self.tab.locator(f"button:has(span:text-is('{self.vocal_gender}'))").first
                if not gender_btn.is_visible():
                     gender_btn = self.tab.locator(f"button:has-text('{self.vocal_gender}')").first
                
                if gender_btn.is_visible():
                    gender_btn.scroll_into_view_if_needed()
                    gender_btn.click(force=True)
                    logger.info(f"Clicked {self.vocal_gender} button.")
                    time.sleep(1.5)
                else:
                    logger.warning(f"Could not find gender button for: {self.vocal_gender}")

            # --- Helper for Numeric Inputs ---
            def set_numeric_value(label_text, target_val):
                if target_val == "Default" or target_val is None: 
                    logger.info(f"Skipping {label_text} (Value is Default)")
                    return
                try:
                    logger.info(f"Attempting to set {label_text} to {target_val}...")
                    # 1. Find the slider
                    slider = self.tab.locator(f"div[aria-label='{label_text}'][role='slider']").first
                    val_text = None
                    
                    if slider.is_visible():
                        # The percentage is usually in a sibling div
                        slider_container = slider.locator("xpath=./ancestor::div[1]").first
                        val_text = slider_container.locator("text=/\\d+%/").first
                        if not val_text.is_visible():
                            # Broad search in row
                            row = slider.locator("xpath=./ancestor::div[contains(@class, 'flex') or contains(@class, 'row')][1]").first
                            val_text = row.locator("text=/\\d+%/").first
                    
                    # 2. Fallback to label-based search
                    if not val_text or not val_text.is_visible():
                        label_loc = self.tab.locator(f"div:text-is('{label_text}'), span:text-is('{label_text}')").first
                        if label_loc.is_visible():
                            row = label_loc.locator("xpath=./ancestor::div[contains(@class, 'flex') or contains(@class, 'row')][1]").first
                            val_text = row.locator("text=/\\d+%/").first

                    if val_text and val_text.is_visible():
                        logger.info(f"Changing {label_text} percentage value...")
                        val_text.scroll_into_view_if_needed()
                        val_text.dblclick(force=True)
                        time.sleep(1)
                        self.tab.keyboard.press("Control+A")
                        self.tab.keyboard.press("Meta+A")
                        self.tab.keyboard.press("Backspace")
                        self.tab.keyboard.type(str(target_val))
                        self.tab.keyboard.press("Enter")
                        time.sleep(2)
                        
                        # Verify
                        final_text = val_text.inner_text()
                        logger.info(f"Final UI value for {label_text}: {final_text}")
                    else:
                        logger.warning(f"Value text for {label_text} not found. UI might have shifted.")

                except Exception as ne:
                    logger.warning(f"Error setting {label_text}: {ne}")

            # 3. Audio Influence (Only visible if persona/upload is active)
            if self.persona_name and self.persona_name != "Default":
                set_numeric_value("Audio Influence", self.audio_influence)
                time.sleep(1)

            # 4. Weirdness
            set_numeric_value("Weirdness", self.weirdness)
            time.sleep(1)

            # 5. Style Influence
            set_numeric_value("Style Influence", self.style_influence)
            time.sleep(1)

        except Exception as e:
            logger.warning(f"Failed to setup advanced options: {e}")

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
