
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
    def __init__(self, project_file, output_dir="data/output", delay=10, startup_delay=5, browser=None):
        self.project_file = project_file
        self.metadata_path = project_file # Backward compat
        
        self.output_dir = output_dir
        self.delay = delay
        self.startup_delay = startup_delay
        self.browser = browser if browser else BrowserController()
        self.tab = self.browser.get_page("suno")
        self.base_url = "https://suno.com/create"
        
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
        title = row.get("title", "Song")
        rid = str(row.get("id", "song"))
        
        content = lyrics if str(lyrics).strip() else prompt
        
        try:
            # Clear old stuff if needed or ensure we are on create page
            if not self.browser.is_visible("textarea", page=self.tab):
                self.tab.locator("button:has-text('Custom')").first.click()
                time.sleep(2)

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
                if not el or not val: return
                try:
                    logger.info(f"Filling field with value: {str(val)[:20]}...")
                    # Critical: Ensure it's in view
                    el.scroll_into_view_if_needed()
                    time.sleep(1)
                    el.click()
                    # Use keyboard for maximum stability in Suno's custom components
                    self.tab.keyboard.press("Meta+A")
                    self.tab.keyboard.press("Backspace")
                    time.sleep(0.5)
                    self.tab.keyboard.type(str(val), delay=50) # Slower typing
                    time.sleep(1)
                except Exception as fe:
                    logger.warning(f"Fill failed for field: {fe}")

            # 1. Lyrics/Prompt
            fill_field(textareas[0], content)
            
            # 2. Style
            if len(textareas) > 1:
                fill_field(textareas[1], style)
            
            # 3. Title (Critical: Scroll and Fill)
            if input_title:
                fill_field(input_title, title)
            else:
                logger.warning("Could not find visible Song Title input field.")

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
            
            # Find the "More" button of the target item
            try:
                rows = self.tab.locator("div.clip-row")
                if rows.count() <= index:
                     logger.error(f"Row {index} disappeared during download phase.")
                     return True
                
                target_row = rows.nth(index)
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
