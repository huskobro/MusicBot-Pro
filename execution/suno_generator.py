
import time
import os
import logging
import openpyxl
from browser_controller import BrowserController

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SunoGenerator:
    def __init__(self, metadata_path="data/output_results.xlsx", output_dir="data/output", delay=10, startup_delay=5, browser=None):
        self.metadata_path = metadata_path
        self.output_dir = output_dir
        self.delay = delay
        self.startup_delay = startup_delay
        self.browser = browser if browser else BrowserController()
        self.tab = self.browser.get_page("suno")
        self.base_url = "https://suno.com/create"
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def run(self, max_count=None, target_ids=None, progress_callback=None):
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
                if "done" in status or "generated" in status: continue
                
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
                
                self.update_row_status(row_dict['_row_idx'], "Processing") # Fixed: passed index, not dict
                if progress_callback: progress_callback(rid, "Generating Music... 🎵")
                
                try:
                    success = self.process_row(row_dict)
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

    def process_row(self, row):
        prompt = row.get("prompt", "")
        lyrics = row.get("lyrics", "")
        style = row.get("style", "")
        title = row.get("title", "Song")
        
        content = lyrics if str(lyrics).strip() else prompt
        
        try:
            if not self.browser.is_visible("textarea", page=self.tab):
                self.tab.locator("button:has-text('Custom')").first.click()
                time.sleep(2)

            textareas = [t for t in self.tab.locator("textarea").all() if t.is_visible()]
            if not textareas: return False

            # Fill
            input_title = self.tab.locator("input[placeholder*='title' i]").first
            
            def fill_field(el, val):
                if not el or not val: return
                el.click()
                self.tab.keyboard.press("Meta+A")
                self.tab.keyboard.press("Backspace")
                el.type(str(val), delay=10)

            fill_field(textareas[0], content)
            if len(textareas) > 1: fill_field(textareas[1], style)
            if input_title.is_visible(): fill_field(input_title, title)

            create_btn = self.tab.get_by_role("button", name="Create").last
            if create_btn.is_enabled():
                create_btn.click()
                time.sleep(5)
                return True
            return False
        except: return False

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
