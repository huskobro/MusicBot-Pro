import time
import os
import logging
import openpyxl
import traceback
from browser_controller import BrowserController
from openpyxl.styles import PatternFill

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiPrompter:
    def __init__(self, project_file, headless=False, 
                 use_gemini_lyrics=True, generate_visual=True, generate_video=True, generate_style=False, startup_delay=5, 
                 language="Turkish", browser=None):
        self.project_file = project_file
        # Backward compatibility for internal methods
        self.output_path = project_file
        self.metadata_path = project_file
        
        self.use_gemini_lyrics = use_gemini_lyrics
        self.generate_visual = generate_visual
        self.generate_video = generate_video
        self.generate_style = generate_style
        self.startup_delay = startup_delay
        self.language = language
        self.browser = browser if browser else BrowserController(headless=headless)
        self.tab = self.browser.get_page("gemini")
        self.base_url = "https://gemini.google.com/app"
        
        # Load Prompts
        self.prompts_path = os.path.join(os.path.dirname(self.metadata_path), "prompts.json")
        self.load_prompts()

    def load_prompts(self):
        import json
        default_lyrics = """Sen profesyonel bir şarkı sözü yazarı ve müzik prodüktörüsün. Suno.ai modelinin en iyi şekilde besteleyebilmesi için, sana vereceğim temalarda içerik oluşturmanı istiyorum.
Tema: {theme}
Language: {language} (IMPORTANT: Use only {language} for lyrics and title)

Lütfen şu formatta yanıt ver (başka bir şey yazma, markdown kullanma):
Başlık: [{language} dilinde şarkı başlığı]
Sözler:
[{language} dilinde, vurucu ve kafiyeli şarkı sözleri... (Intro, Verse 1, Chorus, Verse 2, Bridge, Outro etiketleriyle)]
Stil: [Müzik tarzı, enstrümanlar ve tempo (Örn: Lo-fi, Melancholic Piano, 90bpm)]
Görsel Prompt: [Albüm kapağı için İngilizce, detaylı Stable Diffusion promptu]
Video Prompt: [Müzik videosu için İngilizce, detaylı video üretim promptu]
"""
        default_art = """Create a high-quality YouTube music thumbnail inspired by modern romantic/lofi/ballad compilation channels...
Main title: “{title}”
""" 

        if os.path.exists(self.prompts_path):
            try:
                with open(self.prompts_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.master_prompt_template = data.get("lyrics_master_prompt", default_lyrics)
                    self.visual_master_prompt = data.get("visual_master_prompt", "")
                    self.video_master_prompt = data.get("video_master_prompt", "")
                    self.art_master_prompt = data.get("art_master_prompt", default_art)
            except Exception as e:
                logger.error(f"Error loading prompts.json: {e}")
                self.master_prompt_template = default_lyrics
                self.visual_master_prompt = ""
                self.video_master_prompt = ""
                self.art_master_prompt = default_art
        else:
             self.master_prompt_template = default_lyrics
             self.visual_master_prompt = ""
             self.video_master_prompt = ""
             self.art_master_prompt = default_art

    def run(self, max_count=None, target_ids=None, progress_callback=None):
        try:
            if not self.browser.context:
                self.browser.start()
            
            if self.startup_delay > 0:
                if progress_callback: progress_callback("global", f"Waiting {self.startup_delay}s (Startup Delay)...")
                time.sleep(self.startup_delay)
            
            self.browser.goto(self.base_url, page=self.tab)
            time.sleep(3) 

            # Check if login is needed
            if "accounts.google.com" in self.tab.url:
                logger.warning("--- LOGIN REQUIRED ---")
                if progress_callback: progress_callback("global", "Gemini Login Required! Please check Chrome.")
                time.sleep(1)

            if not os.path.exists(self.metadata_path):
                logger.error("Input file not found.")
                return 0

            # Load pending rows logic
            import openpyxl
            wb = openpyxl.load_workbook(self.metadata_path)
            ws = wb.active
            headers = {str(cell.value).lower(): cell.column - 1 for cell in ws[1] if cell.value}
            
            pending_rows = []
            for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                status_val = str(row[headers.get('status', ws.max_column)]).lower() if 'status' in headers else ""
                if "done" in status_val or "completed" in status_val: continue
                
                rid = str(row[headers.get('id', 0)])
                if target_ids and rid not in target_ids:
                    continue
                
                pending_rows.append({'id': rid, 'row_idx': i, 'theme': row[headers.get('prompt', 1)], 'style': row[headers.get('style', 2)]})
            
            if not pending_rows:
                logger.info("Nothing to process in Gemini.")
                return 0

            if max_count: pending_rows = pending_rows[:max_count]

            processed_count = 0
            for i, rowdata in enumerate(pending_rows):
                row_id = rowdata['id']
                theme = rowdata['theme']
                style_init = rowdata['style']
                
                logger.info(f"Processing Song {i+1}/{len(pending_rows)} ID: {row_id}")
                
                # --- Step 1: Lyrics ---
                final_title = ""
                final_style = style_init
                if self.use_gemini_lyrics:
                    if progress_callback: progress_callback(row_id, "Step 1: Lyrics... ✍️")
                    lyrics_res = self.generate_content(theme, style=style_init)
                    if lyrics_res:
                        self.update_output_data(row_id, lyrics_res)
                        final_title = lyrics_res.get("title", "")
                        final_style = lyrics_res.get("style", style_init)
                        if progress_callback: progress_callback(row_id, "Lyrics Saved! ✅")
                    else:
                        if progress_callback: progress_callback(row_id, "Lyrics Failed ❌")
                        continue

                # --- Step 2: Visual Prompt ---
                if self.generate_visual and self.visual_master_prompt:
                    if progress_callback: progress_callback(row_id, "Step 2: Visual Design... 🎨")
                    vis_res = self.generate_focused_prompt("visual", final_title, final_style)
                    if vis_res:
                        self.update_output_data(row_id, {"visual_prompt": vis_res})
                        if progress_callback: progress_callback(row_id, "Visual Ready! ✅")
                    else:
                        if progress_callback: progress_callback(row_id, "Visual Failed ❌")

                # --- Step 3: Video Prompt ---
                if self.generate_video and self.video_master_prompt:
                    if progress_callback: progress_callback(row_id, "Step 3: Video Design... 🎬")
                    vid_res = self.generate_focused_prompt("video", final_title, final_style)
                    if vid_res:
                        self.update_output_data(row_id, {"video_prompt": vid_res})
                        if progress_callback: progress_callback(row_id, "Video Ready! ✅")
                    else:
                        if progress_callback: progress_callback(row_id, "Video Failed ❌")

                processed_count += 1
                
                if i < len(pending_rows) - 1:
                    time.sleep(5)
            
            return processed_count

        except Exception as e:
            logger.error(f"Gemini error: {e}")
            if progress_callback: progress_callback("global", f"Gemini Process Error: {e}")
        finally:
             logger.info("Gemini finished.")

    # ... (Actual run implementation logic) ...


    def run(self, max_count=None, target_ids=None, progress_callback=None):
        try:
            # 1. Read Metadata from Input XLSX
            if not os.path.exists(self.metadata_path):
                logger.error(f"Input Metadata file not found: {self.metadata_path}")
                return 0

            # Ensure Output exists
            if not os.path.exists(self.output_path):
                logger.info("Output file missing. Initializing from input...")
                import shutil
                shutil.copy(self.metadata_path, self.output_path)

            wb_in = openpyxl.load_workbook(self.metadata_path)
            ws_in = wb_in.active
            
            headers_in = {}
            for cell in ws_in[1]:
                if cell.value:
                    headers_in[str(cell.value).lower()] = cell.column - 1
            
            # Load Output
            wb_out = openpyxl.load_workbook(self.output_path)
            ws_out = wb_out.active
            headers_out = {}
            for cell in ws_out[1]:
                if cell.value:
                    headers_out[str(cell.value).lower()] = cell.column - 1

            rows_data = []
            
            # --- Auto-Validation & ID Generation ---
            input_updates_needed = False
            import uuid
            
            # Identify headers
            id_col_idx = headers_in.get("id")
            prompt_col_idx = headers_in.get("prompt")
            
            if prompt_col_idx is None:
                logger.error("Input file missing 'prompt' column.")
                return 0

            for i, row in enumerate(ws_in.iter_rows(min_row=2), start=2):
                r_id = row[id_col_idx].value if id_col_idx is not None else None
                r_prompt = row[prompt_col_idx].value
                
                if not r_prompt: continue # Skip empty prompts
                
                # Auto-generate ID if missing
                if not r_id:
                    new_id = str(uuid.uuid4())[:8]
                    row[id_col_idx].value = new_id
                    r_id = new_id
                    input_updates_needed = True
                
                # Filter by target_ids if provided
                if target_ids and str(r_id) not in target_ids:
                    continue

                rows_data.append({
                    "id": str(r_id),
                    "prompt": r_prompt,
                    "style": row[headers_in["style"]].value if "style" in headers_in else "",
                    "_row_idx": i
                })
            
            if input_updates_needed:
                wb_in.save(self.metadata_path)
            
            # --- START SYNC: Update Output Styles from Input ---
            sync_count = 0
            # ... (Sync Logic Omitted for brevity, logic maintained implicitly if not changed) ...
            # Wait, I must include content if I replace the block.
            # I should use SEARCH/REPLACE blocks more targetedly to avoid re-pasting entire files.
            # But the tool requires contiguous replacement.
            # I'll restart the replacement chunk from line 57 to the start of the loop to inject the callback.

   # ... Retrying with better strategy: Just change the def line and the loop.

            if not os.path.exists(self.metadata_path):
                logger.error(f"Input Metadata file not found: {self.metadata_path}")
                return 0

            # Ensure Output exists
            if not os.path.exists(self.output_path):
                logger.info("Output file missing. Initializing from input...")
                import shutil
                shutil.copy(self.metadata_path, self.output_path)

            wb_in = openpyxl.load_workbook(self.metadata_path)
            ws_in = wb_in.active
            
            headers_in = {}
            for cell in ws_in[1]:
                if cell.value:
                    headers_in[str(cell.value).lower()] = cell.column - 1
            
            # Load Output
            wb_out = openpyxl.load_workbook(self.output_path)
            ws_out = wb_out.active
            headers_out = {}
            for cell in ws_out[1]:
                if cell.value:
                    headers_out[str(cell.value).lower()] = cell.column - 1

            rows_data = []
            
            # --- Auto-Validation & ID Generation ---
            input_updates_needed = False
            import uuid
            
            # Identify headers
            id_col_idx = headers_in.get("id")
            prompt_col_idx = headers_in.get("prompt")
            
            if prompt_col_idx is None:
                logger.error("Input file missing 'prompt' column.")
                return 0

            for i, row in enumerate(ws_in.iter_rows(min_row=2), start=2):
                r_id = row[id_col_idx].value if id_col_idx is not None else None
                r_prompt = row[prompt_col_idx].value
                
                if not r_prompt: continue # Skip empty prompts
                
                # Auto-generate ID if missing
                if not r_id:
                    new_id = str(uuid.uuid4())[:8]
                    row[id_col_idx].value = new_id
                    r_id = new_id
                    input_updates_needed = True
                
                # Filter by target_ids if provided
                if target_ids and str(r_id) not in target_ids:
                    continue

                rows_data.append({
                    "id": str(r_id),
                    "prompt": r_prompt,
                    "style": row[headers_in["style"]].value if "style" in headers_in else "",
                    "_row_idx": i
                })
            
            if input_updates_needed:
                wb_in.save(self.metadata_path)
            
            # --- START SYNC: Update Output Styles from Input ---
            sync_count = 0
            id_col_out = headers_out.get("id")
            style_col_out = headers_out.get("style")

            if id_col_out is not None and style_col_out is not None:
                # Create a map of ID -> Row Index for Output sheet for faster lookup
                out_id_map = {}
                for r_idx, row in enumerate(ws_out.iter_rows(min_row=2), start=2):
                    # row is tuple of cells
                    if id_col_out < len(row):
                        val = row[id_col_out].value
                        if val: out_id_map[str(val)] = r_idx
                
                # Iterate Input and Update Output
                for r_in in rows_data:
                    rid = str(r_in.get("id", ""))
                    style_val = r_in.get("style", "")
                    
                    if rid in out_id_map and style_val:
                        target_row_idx = out_id_map[rid]
                        # Check current value
                        current_cell = ws_out.cell(row=target_row_idx, column=style_col_out+1)
                        if str(current_cell.value) != str(style_val):
                             current_cell.value = style_val
                             sync_count += 1
            
            if sync_count > 0:
                wb_out.save(self.output_path)
                logger.info(f"Synced styles for {sync_count} existing songs.")
            # --- END SYNC ---

            # Filter pending rows
            done_ids = set()
            # Reload to get latest state in memory? (wb_out is already updated in memory)
            # Actually wb_out is active, so we just iterate it.
            for r in ws_out.iter_rows(min_row=2, values_only=True):
                rid_val = r[headers_out.get('id', 0)]
                if rid_val is None: continue
                rid = str(rid_val)
                
                lyrics = r[headers_out.get('lyrics', -1)] if 'lyrics' in headers_out else None
                visual = r[headers_out.get('visual_prompt', -1)] if 'visual_prompt' in headers_out else None
                video = r[headers_out.get('video_prompt', -1)] if 'video_prompt' in headers_out else None
                style = r[headers_out.get('style', -1)] if 'style' in headers_out else None
                
                is_done = True
                if self.use_gemini_lyrics and not lyrics: is_done = False
                if self.generate_visual and not visual: is_done = False
                if self.generate_video and not video: is_done = False
                if self.generate_style and not style: is_done = False
                
                if is_done:
                    done_ids.add(rid)

            pending_rows = []
            for r in rows_data:
                rid = str(r.get("id", ""))
                if rid not in done_ids and r.get("prompt"):
                    pending_rows.append(r)
            
            if not pending_rows:
                logger.info("No rows found needing Gemini update.")
                return 0

            # Apply max_count
            if max_count and max_count > 0:
                pending_rows = pending_rows[:max_count]

            logger.info(f"Processing {len(pending_rows)} songs.")

            # 2. Start Browser
            self.browser.start()
            self.tab.bring_to_front()
            if self.startup_delay > 0:
                if progress_callback: progress_callback("global", f"Waiting {self.startup_delay}s (Startup Delay)...")
                time.sleep(self.startup_delay)

            self.browser.goto(self.base_url, page=self.tab)

            # Login Check
            if "accounts.google.com" in self.tab.url:
                logger.warning("--- LOGIN REQUIRED ---")
                if progress_callback: progress_callback("global", "Login Required! Please check Chrome.")
                # We don't use input() here anymore to avoid blocking the GUI thread if possible,
                # but for simplicity in this flow we might still need a wait.
                # Actually, the user can just log in in the opened tab.
                time.sleep(5) 
            
            # 3. Process Rows
            processed_count = 0
            for i, row in enumerate(pending_rows):
                theme = row.get("prompt")
                row_id = row.get("id")
                style = row.get("style") # Extract input style
                
                logger.info(f"Generating content for: {theme} (ID: {row_id}, Style: {style})")
                if progress_callback: progress_callback(row_id, "Generating Content...")
                
                result = self.generate_content(theme, style)
                
                if result:
                    if progress_callback: progress_callback(row_id, "Content Generated ✅")
                    self.update_output_data(row_id, result)
                    processed_count += 1
                else:
                    if progress_callback: progress_callback(row_id, "Error: Generation Failed ❌")
                    logger.error("   -> Failed.")
                
                if i < len(pending_rows) - 1:
                    time.sleep(10)
            
            return processed_count

        except Exception as e:
            logger.error(f"Gemini error: {e}")
            raise e # Re-raise to let GUI handle it
        finally:
             logger.info("Gemini finished.")

    def generate_content(self, theme, style=None):
        try:
            input_box = None
            possible_selectors = ["div[contenteditable='true']", "textarea[aria-label*='prompt']", "textarea"]
            for selector in possible_selectors:
                if self.browser.is_visible(selector, page=self.tab):
                    input_box = selector
                    break
            
            if not input_box: return None

            # Using .replace() instead of .format() for better robustness against unknown braces in template
            full_prompt = self.master_prompt_template.replace("{theme}", str(theme)).replace("{language}", str(self.language))
            
            # Inject style instruction if provided
            if style:
                full_prompt += f"\n\n[IMPORTANT] Target Music Style: {style}\nPlease ensure all outputs (lyrics, art, video, style) follow this style precisely."

            self.browser.fill(input_box, full_prompt, page=self.tab)
            time.sleep(1)
            self.tab.keyboard.press("Enter")
            
            response_text = self._wait_for_response()
            if not response_text:
                return None
            
            result = {}
            lines = response_text.split('\n')
            current_section = None
            buffer = []
            
            for line in lines:
                clean_line = line.strip()
                lower_line = clean_line.lower()
                
                if lower_line.startswith("başlık:"):
                    if current_section: result[current_section] = "\n".join(buffer).strip()
                    result["title"] = clean_line.split(":", 1)[1].strip()
                    current_section = None
                    buffer = []
                elif lower_line.startswith("sözler:"):
                    if current_section: result[current_section] = "\n".join(buffer).strip()
                    current_section = "lyrics"
                    buffer = []
                elif lower_line.startswith("stil:"):
                    if current_section: result[current_section] = "\n".join(buffer).strip()
                    current_section = "style"
                    buffer = []
                elif lower_line.startswith("görsel prompt:"):
                    if current_section: result[current_section] = "\n".join(buffer).strip()
                    current_section = "visual_prompt"
                    buffer = []
                elif lower_line.startswith("video prompt:"):
                    if current_section: result[current_section] = "\n".join(buffer).strip()
                    current_section = "video_prompt"
                    buffer = []
                else:
                    if current_section: buffer.append(line)
            
            if current_section: result[current_section] = "\n".join(buffer).strip()
            
            # Unify art prompt naming
            if "visual_prompt" in result:
                result["cover_art_prompt"] = result["visual_prompt"]
                
            return result
        except Exception as e:
            logger.error(f"Gemini Step Error: {e}")
            logger.error(traceback.format_exc())
            return None
    def generate_focused_prompt(self, ptype, title, style):
        """Generates a focused prompt (visual or video) as a separate interaction."""
        try:
            # Re-locate input box to be sure
            input_box = self.tab.locator('div[contenteditable="true"]').first
            if not input_box: return None

            template = self.visual_master_prompt if ptype == "visual" else self.video_master_prompt
            if not template: return ""

            full_prompt = template.replace("{title}", str(title)).replace("{style}", str(style))
            
            self.browser.fill(input_box, full_prompt, page=self.tab)
            time.sleep(1)
            self.tab.keyboard.press("Enter")
            
            return self._wait_for_response()
        except Exception as e:
            logger.error(f"Gemini {ptype} Step Error: {e}")
            return None

    def _wait_for_response(self, timeout=120):
        """Helper to wait for Gemini response to stabilize."""
        logger.info("Waiting for Gemini response to stabilize...")
        start_time = time.time()
        last_text = ""
        stable_count = 0
        
        while time.time() - start_time < timeout:
            candidates = self.tab.locator("message-content").all() 
            if not candidates: candidates = self.tab.locator(".model-response-text").all()
            
            if candidates:
                current_text = candidates[-1].inner_text()
                if current_text and current_text == last_text:
                    stable_count += 1
                    if stable_count >= 3: 
                        return current_text
                else:
                    last_text = current_text
                    stable_count = 0
            
            time.sleep(2)
        
        logger.error("Gemini response timed out or returned no content.")
        return None

    
    def generate_art_prompts(self, max_count=None, target_ids=None, progress_callback=None):
        """Step 3a: Generates ONLY the text prompt for Cover Art."""
        return self._run_art_step(mode="prompt", max_count=max_count, target_ids=target_ids, progress_callback=progress_callback)

    def generate_art_images(self, max_count=None, target_ids=None, progress_callback=None):
        """Step 3b: Generates Image from existing 'cover_art_prompt'."""
        return self._run_art_step(mode="image", max_count=max_count, target_ids=target_ids, progress_callback=progress_callback)

    def _run_art_step(self, mode="prompt", max_count=None, target_ids=None, progress_callback=None):
        try:
            logger.info(f"Starting Art Step (Mode: {mode})...")
            
            if not os.path.exists(self.output_path):
                # Attempt to initialize from input if available
                # Assuming input is in same dir as 'input_songs.xlsx'
                base_dir = os.path.dirname(self.output_path)
                input_path = os.path.join(base_dir, "input_songs.xlsx")
                
                if os.path.exists(input_path):
                    logger.warning(f"Output file not found at {self.output_path}. Initializing from {input_path}...")
                    import shutil
                    shutil.copy(input_path, self.output_path)
                    if progress_callback: progress_callback("global", "Initialized Output File from Input.")
                else:
                    logger.error(f"Output file not found at {self.output_path} and Input not found.")
                    if progress_callback: progress_callback("global", "Error: Missing Input/Output Files! Run Step 1.")
                    return 0
            
            wb = openpyxl.load_workbook(self.output_path)
            ws = wb.active
            headers = {str(cell.value).lower(): cell.column - 1 for cell in ws[1] if cell.value}
            
            rows_to_process = []
            for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                rid = str(row[headers.get('id', 0)]) if 'id' in headers else ""
                
                if target_ids and rid not in target_ids: 
                    continue
                
                # Needs cover_art_prompt but NO cover_art_path
                p_idx = headers.get('cover_art_prompt')
                v_idx = headers.get('visual_prompt')
                i_idx = headers.get('cover_art_path')
                
                # Dynamic value lookup
                prompt_val = row[p_idx] if p_idx is not None else None
                # Fallback to visual_prompt if cover_art_prompt is empty
                if (not prompt_val or str(prompt_val).strip() == "") and v_idx is not None:
                     prompt_val = row[v_idx]
                
                path_val = row[i_idx] if i_idx is not None else None
                
                if mode == "prompt":
                    if not prompt_val or str(prompt_val).strip() == "":
                        rows_to_process.append({"id": rid, "row": row, "_row_idx": i, "headers": headers})
                    else:
                        logger.info(f"Skipping Art Prompt for {rid}: Prompt already exists (Found in cover_art_prompt or visual_prompt).")
                elif mode == "image":
                    if prompt_val and str(prompt_val).strip() != "" and not path_val:
                        rows_to_process.append({"id": rid, "row": row, "_row_idx": i, "headers": headers, "art_prompt": prompt_val})
                    elif not prompt_val or str(prompt_val).strip() == "":
                        logger.warning(f"Skipping Art Image for {rid}: No prompt found in 'cover_art_prompt' or 'visual_prompt'.")
                        if progress_callback: progress_callback(rid, "Error: No Art Prompt Found! ❌")
                    else:
                        logger.info(f"Skipping Art Image for {rid}: Image already exists or not needed.")

            if not rows_to_process:
                logger.info(f"Nothing to process for Step 3/4 (Mode: {mode}) for IDs: {target_ids}")
                return 0
            
            if max_count: rows_to_process = rows_to_process[:max_count]
            
            self.browser.start()
            self.tab.bring_to_front()
            if self.startup_delay > 0:
                if progress_callback: progress_callback("global", f"Waiting {self.startup_delay}s (Startup Delay)...")
                time.sleep(self.startup_delay)
            self.browser.goto(self.base_url, page=self.tab)
            
            # Login Check
            if "accounts.google.com" in self.tab.url:
                 if progress_callback: progress_callback("global", "Login Required!")
                 time.sleep(5)

            count = 0
            for item in rows_to_process:
                rid = item['id']
                
                if mode == "prompt":
                    if progress_callback: progress_callback(rid, "Generating Art Prompt...")
                    # Get Data
                    row = item["row"]
                    headers = item["headers"]
                    title = row[headers.get('title', 0)] or ""
                    
                    # Fill Master Prompt
                    full_prompt = self.art_master_prompt.replace("{title}", str(title))
                    
                    # Send
                    result_text = self._send_and_get_text(full_prompt)
                    if result_text:
                        self.update_output_data(rid, {"cover_art_prompt": result_text})
                        if progress_callback: progress_callback(rid, "Prompt Generated ✅")
                        count += 1
                    else:
                        if progress_callback: progress_callback(rid, "Prompt Failed ❌")

                elif mode == "image":
                    if progress_callback: progress_callback(rid, "Generating Image... 🎨")
                    art_prompt = item["art_prompt"]
                    
                    # Trigger Image Gen
                    img_trigger = f"Generate an image based on this description:\n\n{art_prompt}"
                    save_path = self._generate_and_download_image(img_trigger, rid)
                    
                    if save_path:
                        self.update_output_data(rid, {"cover_art_path": save_path})
                        if progress_callback: progress_callback(rid, "Image Saved 🖼️")
                        count += 1
                    else:
                        if progress_callback: progress_callback(rid, "Image Failed ❌")
            
            return count
        except Exception as e:
            logger.error(f"Art Error: {e}")
            raise e
        finally:
            logger.info("Art Step Finished")

    def _send_and_get_text(self, prompt):
        try:
            input_box = None
            possible_selectors = ["div[contenteditable='true']", "textarea[aria-label*='prompt']", "textarea"]
            for selector in possible_selectors:
                if self.browser.is_visible(selector, page=self.tab):
                    input_box = selector
                    break
            
            if not input_box: return None
            
            self.browser.fill(input_box, prompt, page=self.tab)
            time.sleep(1)
            self.tab.keyboard.press("Enter")
            time.sleep(10) # Wait for text gen
            
            candidates = self.tab.locator("message-content").all()
            if candidates: return candidates[-1].inner_text().strip()
            return None
        except: return None

    def _generate_and_download_image(self, prompt, rid):
        try:
            input_box = "div[contenteditable='true']"
            if not self.browser.is_visible(input_box, page=self.tab): 
                logger.warning("Gemini input box not found for image gen.")
                return None
            
            # Step 0: Count existing image containers to avoid stale detection
            initial_containers = self.tab.locator("div.image-set-container, sac-image-set, sac-single-image-set").count()
            logger.info(f"Initial image container count: {initial_containers}")

            logger.info("Sending image generation prompt to Gemini...")
            self.browser.fill(input_box, prompt, page=self.tab)
            self.tab.keyboard.press("Enter")
            
            # Step 1: Wait for generation to start (indicator to appear)
            logger.info("Waiting for generation indicator to appear...")
            indicator_selectors = [
                "text='Görüntüler oluşturuluyor...'", 
                "text='Generating images...'",
                ".loading-indicator", 
                "div:has-text('Nanobanana')"
            ]
            
            # Brief wait for indicator to appear
            time.sleep(3)
            
            # Step 2: Poll for generation completion (New container appearing)
            logger.info("Waiting for NEW images to be fully rendered (polling up to 90s)...")
            found_img = None
            
            for attempt in range(18): # 18 * 5s = 90s
                # Check if still generating
                is_loading = False
                for sel in indicator_selectors:
                    try:
                        if self.tab.locator(sel).first.is_visible():
                            is_loading = True
                            break
                    except: pass
                
                if is_loading:
                    logger.info(f"   Still generating (Attempt {attempt+1}/18)...")
                else:
                    # Look for NEW image containers
                    current_containers = self.tab.locator("div.image-set-container, sac-image-set, sac-single-image-set")
                    current_count = current_containers.count()
                    
                    if current_count > initial_containers:
                        # New container found!
                        container = current_containers.last
                        if container.is_visible():
                            logger.info("Generation finished (New container detected). Finding primary image...")
                            time.sleep(3) # Extra wait for full high-res render
                            
                            # Find the largest image in the newest container
                            images = container.locator("img").all()
                            if images:
                                for img in reversed(images):
                                    box = img.bounding_box()
                                    if box and box['width'] > 300 and box['height'] > 300:
                                        src = img.get_attribute("src") or ""
                                        if "blob:" in src or "googleusercontent" in src:
                                            found_img = img
                                            break
                            if found_img: break
                    else:
                        logger.info(f"   Waiting for new container (Current: {current_count}, Initial: {initial_containers})...")
                
                time.sleep(5)
            
            if found_img:
                img_dir = os.path.join(os.path.dirname(self.output_path), "images")
                os.makedirs(img_dir, exist_ok=True)
                save_path = os.path.join(img_dir, f"{rid}.png")
                logger.info(f"Found image. Saving with screenshot to: {save_path}")
                found_img.screenshot(path=save_path)
                return save_path
            
            logger.warning("Image generation timed out or no image element discovered.")
            return None
        except Exception as e:
            logger.error(f"Image gen error: {e}")
            return None

    
    
    def close(self):
        # We no longer stop the browser here, as it's shared/managed by the GUI
        pass

    def update_output_data(self, row_id, data):
        try:
            wb = openpyxl.load_workbook(self.output_path)
            ws = wb.active
            col_map = {str(cell.value).lower(): cell.column for cell in ws[1] if cell.value}
            
            # Ensure columns exist
            for key in ["title", "lyrics", "visual_prompt", "video_prompt", "style", "status", "cover_art_prompt", "cover_art_path"]:
                if key not in col_map:
                    new_idx = ws.max_column + 1
                    ws.cell(row=1, column=new_idx, value=key)
                    col_map[key] = new_idx
            
            target_row = None
            id_col = col_map.get("id", 1)
            for row in range(2, ws.max_row + 1):
                if str(ws.cell(row=row, column=id_col).value) == str(row_id):
                    target_row = row
                    break
            
            if not target_row: target_row = ws.max_row + 1
            
            fill_new = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
            
            # Helper to update cell if empty or force update(though we default to skip if exists)
            def update_cell(col_name, new_value):
                if col_name in col_map:
                    cell = ws.cell(row=target_row, column=col_map[col_name])
                    if not cell.value: # Only update if empty
                        cell.value = new_value
                        cell.fill = fill_new
            
            ws.cell(row=target_row, column=col_map["id"], value=row_id)
            
            if "title" in data: update_cell("title", data["title"])
            if self.use_gemini_lyrics and "lyrics" in data: update_cell("lyrics", data["lyrics"])
            if self.generate_style and "style" in data: update_cell("style", data["style"])
            if self.generate_visual and "visual_prompt" in data: update_cell("visual_prompt", data["visual_prompt"])
            if self.generate_video and "video_prompt" in data: update_cell("video_prompt", data["video_prompt"])
            if "cover_art_prompt" in data: update_cell("cover_art_prompt", data["cover_art_prompt"])
            if "cover_art_path" in data: update_cell("cover_art_path", data["cover_art_path"])
            
            wb.save(self.output_path)
        except Exception as e:
            logger.error(f"Save error: {e}")

if __name__ == "__main__":
    gemini = GeminiPrompter()
    gemini.run()
