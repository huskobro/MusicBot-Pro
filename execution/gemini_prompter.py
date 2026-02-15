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
    def __init__(self, project_file, output_dir=None, headless=False, 
                 use_gemini_lyrics=True, generate_visual=True, generate_video=True, generate_style=False, startup_delay=5, 
                 language="Turkish", browser=None):
        self.project_file = project_file
        self.output_dir = output_dir if output_dir else os.path.dirname(project_file)
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

    def run(self, max_count=None, target_ids=None, progress_callback=None, force_update=False):
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
            import uuid
            wb = openpyxl.load_workbook(self.metadata_path)
            ws = wb.active
            headers = {str(cell.value).lower(): cell.column - 1 for cell in ws[1] if cell.value}
            
            # Column mapping for status check
            lyr_col_idx = headers.get('lyrics')
            vis_col_idx = headers.get('visual_prompt')
            vid_col_idx = headers.get('video_prompt')
            status_col_idx = headers.get('status', ws.max_column)
            id_col_idx = headers.get('id', 0)
            prompt_col_idx = headers.get('prompt', 1)
            style_col_idx = headers.get('style', 2)

            pending_rows = []
            updates_needed = False
            for i, row in enumerate(ws.iter_rows(min_row=2), start=2):
                rid = row[id_col_idx].value
                # 1. Ensure ID exists
                if not rid:
                    rid = str(uuid.uuid4())[:8]
                    row[id_col_idx].value = rid
                    updates_needed = True
                
                rid = str(rid)
                if target_ids and rid not in target_ids:
                    continue
                
                # 2. Check if song needs processing
                status_val = str(row[status_col_idx].value).lower() if status_col_idx < len(row) else ""
                
                # We process if:
                # - Status is not 'done'
                # - OR any requested step is missing data
                needs_work = False
                if "done" not in status_val and "completed" not in status_val:
                    needs_work = True
                
                # Even if status is 'done', check for missing components
                lyrics_val = row[lyr_col_idx].value if lyr_col_idx is not None else ""
                visual_val = row[vis_col_idx].value if vis_col_idx is not None else ""
                video_val = row[vid_col_idx].value if vid_col_idx is not None else ""
                
                if self.use_gemini_lyrics and not lyrics_val: needs_work = True
                if self.generate_visual and not visual_val: needs_work = True
                if self.generate_video and not video_val: needs_work = True
                
                if needs_work or force_update:
                    pending_rows.append({
                        'id': rid, 
                        'row_idx': i, 
                        'theme': row[prompt_col_idx].value, 
                        'style': row[style_col_idx].value if style_col_idx is not None else "",
                        'existing_lyrics': lyrics_val,
                        'existing_visual': visual_val,
                        'existing_video': video_val
                    })
            
            if updates_needed:
                wb.save(self.metadata_path)

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
                if (self.use_gemini_lyrics and not rowdata.get('existing_lyrics')) or force_update:
                    if progress_callback: progress_callback(row_id, "Step 1: Lyrics... ✍️")
                    lyrics_res = self.generate_content(theme, style=style_init)
                    if lyrics_res:
                        # Map Gemini's style to suno_style
                        output_payload = lyrics_res.copy()
                        if "style" in lyrics_res:
                            output_payload["suno_style"] = lyrics_res["style"]
                            # Don't overwrite the original 'style' column if it exists in data
                            # Actually, update_output_data handles this by only updating if empty,
                            # but we explicitly want Gemini style in 'suno_style'.
                        self.update_output_data(row_id, output_payload)
                        final_title = lyrics_res.get("title", "")
                        final_style = lyrics_res.get("style", style_init)
                        if progress_callback: progress_callback(row_id, "Lyrics Saved! ✅")
                    else:
                        if progress_callback: progress_callback(row_id, "Lyrics Failed ❌")
                        continue
                else:
                    # Skip or Load existing for next steps
                    logger.info(f"   -> Lyrics already exist for {row_id}, skipping to prompt design.")
                    # We might need to extract title/style from excel if lyrics exist
                    # For now, we'll try to generate prompts if they are missing
                    # We'll use the theme as a fallback for prompt generation if Title isn't parsed
                    final_title = theme # Fallback

                # --- Step 2: Visual Prompt ---
                if self.generate_visual and self.visual_master_prompt and (not rowdata.get('existing_visual') or force_update):
                    if progress_callback: progress_callback(row_id, "Step 2: Visual Design... 🎨")
                    vis_res = self.generate_focused_prompt("visual", final_title, final_style)
                    if vis_res:
                        # Clean markdown bolding if any
                        vis_res = vis_res.replace("**", "").replace("__", "").strip()
                        self.update_output_data(row_id, {"visual_prompt": vis_res})
                        if progress_callback: progress_callback(row_id, "Visual Ready! ✅")
                    else:
                        if progress_callback: progress_callback(row_id, "Visual Failed ❌")

                # --- Step 3: Video Prompt ---
                if self.generate_video and self.video_master_prompt and (not rowdata.get('existing_video') or force_update):
                    if progress_callback: progress_callback(row_id, "Step 3: Video Design... 🎬")
                    vid_res = self.generate_focused_prompt("video", final_title, final_style)
                    if vid_res:
                        vid_res = vid_res.replace("**", "").replace("__", "").strip()
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

            self.tab.click(input_box)
            time.sleep(1)
            self.browser.fill(input_box, full_prompt, page=self.tab)
            time.sleep(2)
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
                # Strip markdown bolding and other markers for tag detection
                tag_check = clean_line.replace("*", "").replace("#", "").strip().lower()
                
                if tag_check.startswith("başlık"):
                    if current_section: result[current_section] = "\n".join(buffer).strip()
                    parts = clean_line.split(":", 1)
                    val = parts[1].strip() if len(parts) > 1 else ""
                    result["title"] = val.replace("[", "").replace("]", "")
                    current_section = None
                    buffer = []
                elif tag_check.startswith("sözler"):
                    if current_section: result[current_section] = "\n".join(buffer).strip()
                    current_section = "lyrics"
                    parts = clean_line.split(":", 1)
                    buffer = [parts[1].strip()] if len(parts) > 1 and parts[1].strip() else []
                elif tag_check.startswith("stil"):
                    if current_section: result[current_section] = "\n".join(buffer).strip()
                    current_section = "style"
                    parts = clean_line.split(":", 1)
                    buffer = [parts[1].strip()] if len(parts) > 1 and parts[1].strip() else []
                elif tag_check.startswith("görsel prompt"):
                    if current_section: result[current_section] = "\n".join(buffer).strip()
                    current_section = "visual_prompt"
                    parts = clean_line.split(":", 1)
                    buffer = [parts[1].strip()] if len(parts) > 1 and parts[1].strip() else []
                elif tag_check.startswith("video prompt"):
                    if current_section: result[current_section] = "\n".join(buffer).strip()
                    current_section = "video_prompt"
                    parts = clean_line.split(":", 1)
                    buffer = [parts[1].strip()] if len(parts) > 1 and parts[1].strip() else []
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
            # FIX: Use string selector directly to avoid "Locator not JSON serializable"
            input_box_selector = 'div[contenteditable="true"]'
            
            template = self.visual_master_prompt if ptype == "visual" else self.video_master_prompt
            if not template: return None

            full_prompt = template.replace("{title}", str(title)).replace("{style}", str(style))
            
            self.tab.click(input_box_selector)
            time.sleep(1)
            self.browser.fill(input_box_selector, full_prompt, page=self.tab)
            time.sleep(2)
            self.tab.keyboard.press("Enter")
            
            return self._wait_for_response()
        except Exception as e:
            logger.error(f"Gemini {ptype} Step Error: {e}")
            return None

    def _wait_for_response(self, timeout=120):
        """Helper to wait for Gemini response to stabilize."""
        logger.info("Waiting for Gemini response to appear and stabilize...")
        start_time = time.time()
        
        # 1. First, wait for a NEW message to appear
        # We assume the last message currently exists (it's either our prompt or a previous response)
        initial_candidates = self.tab.locator("message-content").all()
        if not initial_candidates: initial_candidates = self.tab.locator(".model-response-text").all()
        initial_count = len(initial_candidates)
        logger.info(f"Initial message count: {initial_count}")

        last_text = ""
        stable_count = 0
        new_message_detected = False
        
        while time.time() - start_time < timeout:
            candidates = self.tab.locator("message-content").all() 
            if not candidates: candidates = self.tab.locator(".model-response-text").all()
            
            current_count = len(candidates)
            
            if current_count > initial_count:
                if not new_message_detected:
                    logger.info("New message detected, waiting for content...")
                    new_message_detected = True
                
                current_text = candidates[-1].inner_text().strip()
                
                # If message is still empty, keep waiting
                if not current_text:
                    time.sleep(1)
                    continue

                if current_text == last_text:
                    stable_count += 1
                    # Reduced to 2 checks (4s) for snappiness, but ensure it's not just "typing..."
                    if stable_count >= 2: 
                        logger.info(f"Response stabilized. Length: {len(current_text)}")
                        return current_text
                else:
                    last_text = current_text
                    stable_count = 0
            else:
                # Still waiting for the new message to appear
                pass

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
                img_dir = self.output_dir
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
            for key in ["title", "lyrics", "visual_prompt", "video_prompt", "style", "suno_style", "status", "cover_art_prompt", "cover_art_path"]:
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
            if "suno_style" in data: update_cell("suno_style", data["suno_style"])
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
