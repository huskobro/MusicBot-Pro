import time
import os
import logging
import openpyxl
import re
import json
from browser_controller import BrowserController

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from suno_config import SunoConfig
from suno_excel import SunoExcelMixin
from suno_downloader import SunoDownloaderMixin
from suno_ui import SunoUIMixin

class SunoGenerator(SunoExcelMixin, SunoDownloaderMixin, SunoUIMixin):
    def __init__(self, project_file, output_dir="data/output", delay=10, startup_delay=5, browser=None,
                 audio_influence=25, vocal_gender="Default", lyrics_mode="Default", 
                 weirdness=50, style_influence=50, persona_link="", turbo=False):
        self.config = SunoConfig(
            delay=delay,
            startup_delay=startup_delay
        )
        self.project_file = project_file
        self.metadata_path = project_file # Backward compat
        
        self.output_dir = output_dir
        self.delay = delay
        self.startup_delay = startup_delay
        self.browser = browser or BrowserController()
        self.tab = self.browser.page
        self.base_url = "https://suno.com/create"
        self.stop_requested = False
        self.turbo = turbo
        
        # Advanced Params
        self.audio_influence = audio_influence
        self.vocal_gender = vocal_gender
        self.lyrics_mode = lyrics_mode
        self.weirdness = weirdness
        self.style_influence = style_influence
        self.persona_link = str(persona_link).strip()
        
        import sys
        self.mod = "Meta" if sys.platform == "darwin" else "Control"
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.stop_requested = False

    def run(self, max_count=None, target_ids=None, progress_callback=None, force_update=False):
        try:
            if not self.browser.context:
                self.browser.start()
            
            if self.startup_delay > 0:
                if progress_callback: progress_callback("global", f"Bekleniyor: {self.startup_delay}sn (Başlangıç Gecikmesi)...")
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
                
                # Check repeatedly for login
                for _ in range(60): # Wait up to 5 mins for user login
                    if "create" in self.tab.url and "login" not in self.tab.url:
                        break
                    time.sleep(5)
            
            if "create" not in self.tab.url:
                self.browser.goto(self.base_url, page=self.tab)
                time.sleep(3)

            if not os.path.exists(self.metadata_path):
                logger.error("Results file not found.")
                return 0

            wb = openpyxl.load_workbook(self.metadata_path)
            ws = wb.active
            headers = {str(cell.value).strip().lower(): cell.column - 1 for cell in ws[1] if cell.value}
            
            rows_data = []
            
            # Normalize target_ids for robust matching
            target_ids_set = set(str(t).strip().lower() for t in target_ids) if target_ids else None

            for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                rid_orig = row[headers.get('id', 0)] if 'id' in headers else ""
                rid = str(rid_orig).strip().lower()
                
                # Check target_ids
                if target_ids_set and rid not in target_ids_set:
                    continue
                
                status = str(row[headers.get('status', 0)]).lower() if 'status' in headers else ""
                
                # Determine if song already has music (M1 or M2 presence)
                # In scan_materials, we check files. Here we can also check the status column.
                is_done = "done" in status or "generated" in status
                
                if not force_update and is_done:
                    logger.info(f"Song {rid_orig} already generated on Suno. Skipping.")
                    if progress_callback: progress_callback(str(rid_orig), "Skip: Already Generated ✅")
                    continue
                
                row_dict = {key: row[idx] for key, idx in headers.items() if idx < len(row)}
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

    def run_batch(self, target_ids=None, progress_callback=None, force_update=False, op_mode="full"):
        """
        Orchestrates the BATCH workflow:
        1. Generate ALL requested songs (Phase 1)
        2. Wait for & Download ALL requested songs (Phase 2)
        """
        try:
            if not self.browser.context:
                self.browser.start()
            
            if self.startup_delay > 0:
                if progress_callback: progress_callback("global", f"Bekleniyor: {self.startup_delay}sn (Başlangıç Gecikmesi)...")
                time.sleep(self.startup_delay)
            
            # --- Common Setup (Persona / Login / v5) ---
            # Reuse logic from run(), or extract to common _init_session()
            if self.persona_link:
                success = self._setup_persona_workflow(progress_callback)
                if not success:
                    self.browser.goto(self.base_url, page=self.tab)
            else:
                self.browser.goto(self.base_url, page=self.tab)
            
            time.sleep(5)
            self._ensure_v5_active()

            if "login" in self.tab.url or self.browser.is_visible("text='Log In'", page=self.tab):
                logger.warning("--- LOGIN REQUIRED ---")
                if progress_callback: progress_callback("global", "Login Required! Please check Chrome.")
                for _ in range(60): 
                    if "create" in self.tab.url and "login" not in self.tab.url: break
                    time.sleep(5)
            
            if "create" not in self.tab.url:
                self.browser.goto(self.base_url, page=self.tab)
                time.sleep(3)

            # --- Prepare Data ---
            if not os.path.exists(self.metadata_path): return 0
            
            wb = openpyxl.load_workbook(self.metadata_path)
            ws = wb.active
            headers = {str(cell.value).strip().lower(): cell.column - 1 for cell in ws[1] if cell.value}
            
            rows_data = []
            target_ids_set = set(str(t).strip().lower() for t in target_ids) if target_ids else None

            for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                rid_orig = row[headers.get('id', 0)] if 'id' in headers else ""
                rid = str(rid_orig).strip().lower()
                
                if target_ids_set and rid not in target_ids_set: continue
                
                status = str(row[headers.get('status', 0)]).lower() if 'status' in headers else ""
                is_done = "done" in status or "generated" in status
                
                # Determine if song already has music (M1 or M2 presence)
                # In scan_materials, we check files. Here we can also check the status column.
                
                # [FIX] In dl_only or full mode, we DON'T skip generated items here 
                # because we need them in rows_data for the Phase 2 (Download).
                # We will skip them explicitly inside Phase 1 (Generation).
                if not force_update and is_done and op_mode == "gen_only":
                    continue
                
                row_dict = {key: row[idx] for key, idx in headers.items() if idx < len(row)}
                row_dict['_row_idx'] = i 
                rows_data.append(row_dict)
            
            if not rows_data:
                logger.info("Nothing to batch generate.")
                return 0

            generated_ids = []
            
            # --- PHASE 1: BATCH GENERATION ---
            if op_mode in ["full", "gen_only"]:
                logger.info("--- Starting Batch Generation Phase ---")
                if progress_callback: progress_callback("global", "Toplu Üretim Başlatılıyor... 🚀")
                
                for i, row_dict in enumerate(rows_data):
                    if self.stop_requested: break
                    
                    rid = str(row_dict.get('id', ''))
                    
                    # Ensure a fresh state for every song in batch mode by reloading
                    if i >= 0: # Reload for every song to be absolutely sure
                        if self.persona_link:
                            logger.info(f"Batch: Re-activating Persona for song {rid}...")
                            self._setup_persona_workflow(progress_callback)
                        else:
                            logger.info(f"Batch: Reloading /create for song {rid}...")
                            self.browser.goto(self.base_url, page=self.tab)
                        
                        time.sleep(3)
                        self._ensure_v5_active()
                    
                    if i > 0:
                        time.sleep(self.delay)
                    
                    self.update_row_status(row_dict['_row_idx'], "Processing")
                    
                    # [Safety] Skip generation if already done (and not forced)
                    status = str(row_dict.get('status', '')).lower()
                    if not force_update and ("generated" in status or "done" in status):
                        logger.info(f"Skipping Generation for {rid} (Already Generated)")
                        generated_ids.append(rid) # Move straight to potential download queue
                        continue

                    if progress_callback: progress_callback(rid, "Sıraya Alınıyor... 🎵")
                    
                    success = self._generate_single_no_wait(row_dict, progress_callback)
                    if success:
                        generated_ids.append(rid)
                        self.update_row_status(row_dict['_row_idx'], "Generating...") 
                    else:
                        self.update_row_status(row_dict['_row_idx'], "Failed")
                
                logger.info(f"Batch Generation Phase Complete. {len(generated_ids)} songs queued.")
            
            # --- PHASE 1.5: Identify Resume Items (For DL Only or Full Resume) ---
            # If we skipped generation, or if we want to pick up items that are already "Generating..."
            # Scan rows_data for items with status "Generating..." or "Processing"
            if op_mode in ["full", "dl_only"]:
                for row_dict in rows_data:
                    rid = str(row_dict.get('id', ''))
                    status = str(row_dict.get('status', '')).lower()
                    
                    # If it's a target ID, we definitely want it
                    is_target = target_ids and (rid in target_ids)
                    
                    if rid not in generated_ids:
                        if is_target or "generating" in status or "processing" in status or "suno bekleniyor" in status:
                             logger.info(f"Adding {rid} to download queue (is_target: {is_target}, status: {status})")
                             generated_ids.append(rid)

            # --- PHASE 2: BATCH DOWNLOAD ---
            if op_mode in ["full", "dl_only"] and generated_ids:
                logger.info("--- Starting Batch Download Phase ---")
                if progress_callback: progress_callback("global", "Toplu İndirme Bekleniyor... ⬇️")
                
                # PRE-DOWNLOAD PHASE: SMART WAIT ROOM
                # Only needed when songs are being GENERATED (full mode)
                # In dl_only mode, songs are already generated - skip straight to download
                missing_counts = {rid: 0 for rid in generated_ids}
                
                if op_mode == "full":
                    pending_ids = list(generated_ids)
                    start_wait = time.time()
                    total_timeout = max(600, len(pending_ids) * 180) 
                    
                    logger.info(f"Targeted Batch: Waiting for {len(pending_ids)} songs to complete before download...")
                    
                    max_row_reached = 0
                    loop_count = 0
                    missing_counts = {rid: 0 for rid in pending_ids} # Track missing loops
                    
                    while pending_ids and (time.time() - start_wait < total_timeout):
                        if self.stop_requested: break
                        loop_count += 1
                        
                        # SESSION HARDENING: Check if tab is alive, if not RECOVER
                        try:
                            # Simple check to see if tab is responsive
                            self.tab.url
                        except:
                            logger.warning("Browser tab lost or crashed! Attempting recovery...")
                            try:
                                if self.persona_link: self._setup_persona_workflow(progress_callback)
                                else: self.browser.goto(self.base_url, page=self.tab)
                                time.sleep(5)
                                self._ensure_v5_active()
                            except Exception as re_e:
                                logger.error(f"Recovery failed: {re_e}")
                                time.sleep(10)
                                continue

                        still_generating = []
                        current_max_idx = 0
                        all_targets_found_in_view = True
                        
                        # 1. SCAN AND COLLECT STATUS
                        found_this_loop = {}
                        try:
                            rows = self.tab.locator("div.clip-row")
                            row_count = rows.count()
                            for i in range(min(300, row_count)):
                                row_text = rows.nth(i).inner_text().lower()
                                for rid in pending_ids:
                                    if str(rid).lower() in row_text:
                                        found_this_loop[rid] = {"index": i, "ready": "generating" not in row_text}
                                        current_max_idx = max(current_max_idx, i)
                                        # If any target found in view, we'll track its max index
                        except Exception as scan_e:
                            logger.debug(f"Scan interrupted: {scan_e}")

                        # 2. DECIDE WHO IS STILL PENDING AND IF WE NEED TO SCROLL
                        for rid in pending_ids:
                            if rid in found_this_loop:
                                missing_counts[rid] = 0 # Reset
                                if found_this_loop[rid]["ready"]:
                                    # Extra check for robustness
                                    r_data = next((r for r in rows_data if str(r.get('id', '')).strip().lower() == rid), None)
                                    suno_title = f"{rid}_{r_data.get('title', 'Song')}"
                                    if self._check_if_ready(suno_title, rid, suffix="1") and \
                                       self._check_if_ready(suno_title, rid, suffix="2"):
                                        logger.info(f"ID {rid} is ready for download phase.")
                                        if progress_callback: progress_callback(rid, "Hazır! Beklemede... ✅")
                                    else:
                                        still_generating.append(rid)
                                else:
                                    still_generating.append(rid) # Found but still generating
                            else:
                                # NOT FOUND IN CURRENT VIEW AT ALL
                                missing_counts[rid] = missing_counts.get(rid, 0) + 1
                                if missing_counts[rid] > 12: # After ~2.5 minutes of not seeing it
                                    logger.warning(f"Timeout waiting for {rid} to appear. Skipping.")
                                    r_data = next((r for r in rows_data if str(r.get('id', '')).strip().lower() == rid), None)
                                    if r_data:
                                        self.update_row_status(r_data['_row_idx'], status="Failed", dl_status="failed")
                                    if progress_callback: progress_callback(rid, "Üretilemedi / Bulunamadı ❌")
                                    # DO NOT append to still_generating so it drops from pending_ids
                                else:
                                    still_generating.append(rid)
                                all_targets_found_in_view = False
                        
                        # 3. SMART SCROLLING: Only if someone is missing from view
                        if not all_targets_found_in_view:
                            if max_row_reached > 5:
                                try:
                                    logger.info(f"Waterfall Scroll: Pushing down from row {max_row_reached} to find missing songs...")
                                    rows = self.tab.locator("div.clip-row")
                                    if rows.count() > max_row_reached:
                                        rows.nth(min(max_row_reached, rows.count()-1)).scroll_into_view_if_needed()
                                        time.sleep(1)
                                        self.tab.mouse.wheel(0, 2500)
                                except: pass
                            else:
                                try:
                                    self.tab.mouse.wheel(0, 1500)
                                    time.sleep(1)
                                except: pass
                        else:
                            logger.debug("All pending songs found in current view. No scrolling needed.")

                        # 4. SEARCH FALLBACK: If missing for too long (e.g. 8+ attempts after scrolling)
                        if not all_targets_found_in_view and loop_count > 8:
                            missing = [rid for rid in pending_ids if rid not in found_this_loop]
                            if missing:
                                target_rid = missing[0]
                                logger.info(f"Using Search Fallback for missing ID {target_rid}...")
                                r_data = next((r for r in rows_data if str(r.get('id', '')).strip().lower() == target_rid), None)
                                try:
                                    if self._search_for_song(target_rid, r_data.get('title', 'Song')):
                                        time.sleep(3)
                                        found_it = False
                                        ready = False
                                        s_rows = self.tab.locator("div.clip-row")
                                        for si in range(min(10, s_rows.count())):
                                            s_text = s_rows.nth(si).inner_text().lower()
                                            if target_rid in s_text:
                                                found_it = True
                                                ready = "generating" not in s_text
                                                break
                                        
                                        if not found_it:
                                            missing_counts[target_rid] = missing_counts.get(target_rid, 0) + 2
                                        else:
                                            missing_counts[target_rid] = 0  # It exists!
                                            if ready:
                                                suno_title = f"{target_rid}_{r_data.get('title', 'Song')}"
                                                if self._check_if_ready(suno_title, target_rid, suffix="1") and \
                                                   self._check_if_ready(suno_title, target_rid, suffix="2"):
                                                    if target_rid in still_generating:
                                                        still_generating.remove(target_rid)
                                                    if progress_callback: progress_callback(target_rid, "Hazır! Beklemede... ✅")
                                                    
                                        # Clear search to restore default view for the next loop
                                        try:
                                            search_input = self.tab.locator("input[aria-label='Search clips']").first
                                            if search_input.is_visible():
                                                search_input.fill("")
                                                self.tab.keyboard.press("Enter")
                                                time.sleep(2)
                                        except: pass
                                except: pass

                        max_row_reached = max(max_row_reached, current_max_idx)
                        pending_ids = still_generating
                        if not pending_ids: break
                        
                        if progress_callback: progress_callback("global", f"Bekleniyor: {len(pending_ids)} şarkı kaldı... ⏳")
                        time.sleep(10)
                        
                        # Periodic reload to refresh state (Every 120-150s)
                        if (time.time() - start_wait) > 30 and (time.time() - start_wait) % 150 < 15:
                            try:
                                logger.info("Periodic reload to refresh state...")
                                self.tab.keyboard.press("Escape")
                                time.sleep(1)
                                self.tab.reload(timeout=60000)
                                time.sleep(5)
                                self._ensure_v5_active()
                            except Exception as e:
                                logger.warning(f"Reload failed: {e}")
                else:
                    logger.info(f"dl_only mode: Skipping wait phase. Going straight to download for {len(generated_ids)} songs.")

                # ACTUAL DOWNLOAD PHASE
                # Everything is ready, now we execute the persistent download logic
                # Only exclude songs that were never found (timed out in wait phase)
                download_queue = [rid for rid in generated_ids if missing_counts.get(rid, 0) <= 12]
                completed_ids = []
                
                logger.info(f"Download queue: {download_queue} ({len(download_queue)} songs)")
                
                # Clear any leftover search
                try:
                    search_input = self.tab.locator("input[aria-label='Search clips']").first
                    if search_input.is_visible() and search_input.input_value().strip():
                        search_input.fill("")
                        self.tab.keyboard.press("Enter")
                        time.sleep(2)
                except: pass
                
                # ===== PHASE A: FULL WATERFALL SCROLL =====
                # Scroll through the entire song list to load everything into DOM
                logger.info("Phase A: Full waterfall scroll to load all songs into DOM...")
                if progress_callback: progress_callback("global", "Şarkı listesi yükleniyor... ⬇️")
                try:
                    for scroll_pass in range(15):  # Up to 15 scroll passes
                        rows = self.tab.locator("div.clip-row")
                        current_count = rows.count()
                        if current_count > 0:
                            rows.last.scroll_into_view_if_needed()
                            time.sleep(0.3)
                            self.tab.mouse.wheel(0, 3000)
                            time.sleep(1.5)
                            new_count = self.tab.locator("div.clip-row").count()
                            logger.info(f"Scroll pass {scroll_pass+1}: {current_count} → {new_count} rows")
                            if new_count <= current_count:
                                break  # No more rows loading
                except Exception as e:
                    logger.warning(f"Waterfall scroll error: {e}")
                
                # Scroll back to top 
                try:
                    self.tab.keyboard.press("Home")
                    time.sleep(1)
                except: pass
                
                # ===== PHASE B: SINGLE-PASS INDEX & DOWNLOAD =====
                # ONE scan of DOM → index ALL songs → then download from index
                logger.info("Phase B: Single-pass DOM indexing...")
                if progress_callback: progress_callback("global", "DOM taranıyor... 🔍")
                
                # Step 1: Build index in ONE pass (O(n+m) instead of O(n×m))
                song_index = {}  # {rid: [row_element_1, row_element_2, ...]}
                download_set = set(download_queue)  # O(1) lookups
                
                rows = self.tab.locator("div.clip-row")
                total_rows = rows.count()
                logger.info(f"[Phase B] Indexing {total_rows} DOM rows for {len(download_queue)} target songs...")
                
                for i in range(total_rows):
                    try:
                        row_text = rows.nth(i).inner_text().lower()
                        for rid in download_set:
                            if str(rid).lower() in row_text:
                                if rid not in song_index:
                                    song_index[rid] = []
                                song_index[rid].append(rows.nth(i))
                    except:
                        continue
                
                found_count = len(song_index)
                not_found_ids = [rid for rid in download_queue if rid not in song_index]
                logger.info(f"[Phase B] Index complete: {found_count} found, {len(not_found_ids)} not found in {total_rows} rows")
                
                # Step 2: Download from index (no more DOM scanning needed!)
                for rid in download_queue:
                    if self.stop_requested: break
                    if rid not in song_index:
                        continue  # Will handle in Phase C
                    
                    # SESSION CHECK
                    try: self.tab.url
                    except:
                        logger.warning(f"Tab crashed before downloading {rid}. Recovering...")
                        if self.persona_link: self._setup_persona_workflow()
                        else: self.browser.goto(self.base_url, page=self.tab)
                        time.sleep(5)
                        self._ensure_v5_active()
                    
                    r_data = next((r for r in rows_data if str(r.get('id', '')).strip().lower() == rid), None)
                    if not r_data: continue
                    
                    row_idx = r_data['_row_idx']
                    title = r_data.get("title", "Song")
                    suno_title = f"{rid}_{title}"
                    occurrences = song_index[rid]
                    
                    logger.info(f"[Phase B] Downloading {rid} ({len(occurrences)} occurrences)...")
                    if progress_callback: progress_callback(rid, f"İndiriliyor... ⬇️")
                    
                    s1 = self._download_from_row(occurrences[0], suno_title, rid, suffix="1")
                    s2 = self._download_from_row(occurrences[1], suno_title, rid, suffix="2") if len(occurrences) > 1 else False
                    
                    if s1 or s2:
                        self.update_row_status(row_idx, status="Generated", dl_status="success", dl_attempts=0)
                        status_txt = f"{'1&2' if (s1 and s2) else ('1' if s1 else '2')} İndirildi! ✅"
                        if progress_callback: progress_callback(rid, status_txt)
                        completed_ids.append(rid)
                        logger.info(f"✅ Download SUCCESS for {rid}: s1={s1}, s2={s2}")
                    else:
                        self.update_row_status(row_idx, dl_status="failed", dl_attempts=1)
                        if progress_callback: progress_callback(rid, "İndirme Hatası! ❌")
                        logger.warning(f"❌ Download FAILED for {rid}: s1={s1}, s2={s2}")
                
                # ===== PHASE C: SEARCH FALLBACK FOR NOT-FOUND SONGS =====
                if not_found_ids:
                    logger.info(f"Phase C: Search fallback for {len(not_found_ids)} not-found songs: {not_found_ids}")
                    if progress_callback: progress_callback("global", f"Arama ile {len(not_found_ids)} şarkı aranıyor... 🔍")
                    
                    for rid in not_found_ids:
                        if self.stop_requested: break
                        
                        r_data = next((r for r in rows_data if str(r.get('id', '')).strip().lower() == rid), None)
                        if not r_data: continue
                        
                        row_idx = r_data['_row_idx']
                        title = r_data.get("title", "Song")
                        suno_title = f"{rid}_{title}"
                        
                        logger.info(f"[Phase C] Searching for {rid}...")
                        if progress_callback: progress_callback(rid, f"Aranıyor... 🔍")
                        
                        if self._search_for_song(rid, title):
                            time.sleep(2)
                            rows = self.tab.locator("div.clip-row")
                            occurrences = []
                            for i in range(min(10, rows.count())):
                                if str(rid).lower() in rows.nth(i).inner_text().lower():
                                    occurrences.append(rows.nth(i))
                            
                            if occurrences:
                                logger.info(f"[Phase C] Found {len(occurrences)} occurrences for {rid} via search.")
                                if progress_callback: progress_callback(rid, f"İndiriliyor... ⬇️")
                                
                                s1 = self._download_from_row(occurrences[0], suno_title, rid, suffix="1")
                                s2 = self._download_from_row(occurrences[1], suno_title, rid, suffix="2") if len(occurrences) > 1 else False
                                
                                if s1 or s2:
                                    self.update_row_status(row_idx, status="Generated", dl_status="success", dl_attempts=0)
                                    status_txt = f"{'1&2' if (s1 and s2) else ('1' if s1 else '2')} İndirildi! ✅"
                                    if progress_callback: progress_callback(rid, status_txt)
                                    completed_ids.append(rid)
                                    logger.info(f"✅ Download SUCCESS for {rid}: s1={s1}, s2={s2}")
                                else:
                                    self.update_row_status(row_idx, dl_status="failed", dl_attempts=1)
                                    if progress_callback: progress_callback(rid, "İndirme Hatası! ❌")
                                    logger.warning(f"❌ Download FAILED for {rid}")
                            else:
                                logger.warning(f"[Phase C] {rid} not found even via search. Skipping.")
                                if progress_callback: progress_callback(rid, "Bulunamadı ❌")
                                self.update_row_status(row_idx, dl_status="failed")
                        else:
                            logger.warning(f"[Phase C] Search failed for {rid}. Skipping.")
                            if progress_callback: progress_callback(rid, "Arama Hatası ❌")
                            self.update_row_status(row_idx, dl_status="failed")
                        
                        # Clear search after each song
                        try:
                            search_input = self.tab.locator("input[aria-label='Search clips']").first
                            if search_input.is_visible():
                                search_input.fill("")
                                self.tab.keyboard.press("Enter")
                                time.sleep(2)
                        except: pass
                
                return len(completed_ids)

            return 0

        except Exception as e:
            logger.error(f"Batch Run Error: {e}")
            raise e
        finally:
            logger.info("Batch Run Finished.")

    def _generate_single_no_wait(self, row, progress_callback=None):
        """
        Fills the form and clicks Create, then verifies 'Generating' state appeared.
        Does NOT wait for completion.
        """
        prompt = row.get("prompt", "")
        lyrics = row.get("lyrics", "")
        style = row.get("suno_style", "")
        if not str(style).strip():
            style = row.get("style", "")
        
        rid = str(row.get("id", "song"))
        title = row.get("title", "Song")
        suno_title = f"{rid}_{title}"
        
        content = lyrics if str(lyrics).strip() else prompt
        
        try:
            # Custom Mode
            if not self.tab.locator("text='Lyrics'").first.is_visible():
                custom_btn = self.tab.locator("button:has-text('Custom')").first
                if custom_btn.is_visible():
                    custom_btn.click()
                    time.sleep(3)
            
            initial_count = self.tab.locator("div.clip-row").count()

            # Fills
            textareas = [t for t in self.tab.locator("textarea").all() if t.is_visible()]
            if not textareas: return False

            # Title Logic
            input_title = None
            title_loc = self.tab.locator("input[placeholder*='title' i]")
            for i in range(title_loc.count()):
                if title_loc.nth(i).is_visible():
                    input_title = title_loc.nth(i); break
            
            if not input_title:
                title_loc_alt = self.tab.locator("input[aria-label*='title' i]")
                for i in range(title_loc_alt.count()):
                    if title_loc_alt.nth(i).is_visible():
                        input_title = title_loc_alt.nth(i); break

            def fill_field(el, val):
                if self.turbo:
                    el.fill(str(val))
                else:
                    try:
                        self.browser.humanizer.type_text(self.tab, el, val)
                    except:
                        el.fill(str(val))

            fill_field(textareas[0], content)
            
            style_textarea = self.tab.locator("textarea[placeholder*='style' i]").first
            if style_textarea.is_visible():
                fill_field(style_textarea, style)
            else:
                 if len(textareas) > 1: fill_field(textareas[1], style)
            
            if input_title:
                try: fill_field(input_title, suno_title)
                except: pass
                
            # Adv Options
            self._setup_lyrics_mode()
            self._setup_advanced_options()

            # Click Create
            create_btn = self.tab.locator("button:has-text('Create')").filter(has_not_text="Custom").last
            if not create_btn.is_visible():
                create_btn = self.tab.get_by_role("button", name="Create").last

            if create_btn.is_enabled():
                create_btn.click()
                time.sleep(1 if self.turbo else 2) 

                # Wait for clip count increase OR "Generating"
                for i in range(15):
                    if self._detect_captcha():
                        logger.warning("CAPTCHA DETECTED DURING BATCH!")
                        if progress_callback: progress_callback(rid, "⚠️ CAPTCHA! Çözün... 🕒")
                        self._play_alert()
                        while self._detect_captcha() and not self.stop_requested:
                            time.sleep(3)
                    
                    current_count = self.tab.locator("div.clip-row").count()
                    if current_count > initial_count:
                        logger.info(f"Batch: Queued {rid}")
                        return True
                    
                    time.sleep(2)
                
                return False
            return False
        except Exception as e:
            logger.error(f"Generate Batch Error {rid}: {e}")
            return False


    def process_row(self, row, progress_callback=None):
        prompt = row.get("prompt", "")
        lyrics = row.get("lyrics", "")
        style = row.get("suno_style", "")
        if not str(style).strip():
            style = row.get("style", "")
        
        # [Requirement 7] Title Format: ID_Title
        rid = str(row.get("id", "song"))
        title = row.get("title", "Song")
        suno_title = f"{rid}_{title}"
        
        content = lyrics if str(lyrics).strip() else prompt
        
        try:
            # --- Ensure Custom Mode ---
            if not self.tab.locator("text='Lyrics'").first.is_visible():
                logger.info("Custom mode not detected, clicking 'Custom'...")
                custom_btn = self.tab.locator("button:has-text('Custom')").first
                if custom_btn.is_visible():
                    custom_btn.click()
                    time.sleep(3)
            
            # Record current clip count to prevent stale downloads
            initial_count = self.tab.locator("div.clip-row").count()
            logger.info(f"Current clip count before creation: {initial_count}")

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
                    # Robust JS-based clear to ensure reactive state is reset
                    try:
                        el.scroll_into_view_if_needed()
                        self.tab.evaluate(r"""(el) => {
                            const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set || 
                                               Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
                            if (nativeSetter) {
                                nativeSetter.call(el, '');
                            } else {
                                el.value = '';
                            }
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        }""", el)
                        time.sleep(0.2)
                    except: pass

                    logger.info(f"Filling field with: {str(val)[:20]}...")
                    self.browser.humanizer.type_text(self.tab, el, val)
                except Exception as fe:
                    logger.warning(f"Humanizer failed: {fe}")
                    try:
                        el.scroll_into_view_if_needed()
                        el.fill(str(val))
                    except: pass

            fill_field(textareas[0], content)
            
            # Style: try placeholder match first, then section-based lookup
            style_textarea = self.tab.locator("textarea[placeholder*='style' i]").first
            if style_textarea.is_visible():
                fill_field(style_textarea, style)
            else:
                style_found = self.tab.evaluate(r"""() => {
                    const headers = document.querySelectorAll('div[role="button"]');
                    for (const h of headers) {
                        if (h.textContent.trim() === 'Styles') {
                            let container = h.parentElement;
                            for (let d = 0; d < 5 && container; d++) {
                                const ta = container.querySelector('textarea');
                                if (ta && ta.offsetParent !== null) {
                                    ta.scrollIntoView({ block: 'center' });
                                    return true;
                                }
                                container = container.parentElement;
                            }
                        }
                    }
                    return false;
                }""")
                if style_found and len(textareas) > 1:
                    fill_field(textareas[1], style)
                elif len(textareas) > 1:
                    fill_field(textareas[1], style)
            
            # Title fill
            if input_title:
                try:
                    fill_field(input_title, suno_title)
                except Exception:
                    pass
                actual = input_title.input_value() if input_title.is_visible() else ""
                if str(suno_title) not in actual:
                    self.tab.evaluate("""(t) => {
                        const inputs = document.querySelectorAll('input[placeholder*="Song Title" i]');
                        for (const inp of inputs) {
                            if (inp.offsetParent !== null) {
                                inp.scrollIntoView({ block: 'center' });
                                const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                                nativeSetter.call(inp, t);
                                inp.dispatchEvent(new Event('input', { bubbles: true }));
                                inp.dispatchEvent(new Event('change', { bubbles: true }));
                                return;
                            }
                        }
                    }""", str(suno_title))
                    time.sleep(1)

            # --- Persona & Advanced Options Setup ---
            self._setup_lyrics_mode()
            self._setup_advanced_options()

            # Click Create
            create_btn = self.tab.locator("button:has-text('Create')").filter(has_not_text="Custom").last
            if not create_btn.is_visible():
                create_btn = self.tab.get_by_role("button", name="Create").last

            if create_btn.is_enabled():
                logger.info(f"Clicking Create for: {suno_title}")
                create_btn.click()
                time.sleep(2) 

                # [Requirement 7 + CAPTCHA Alert]
                new_clip_appeared = False
                for i in range(25): # ~40-50s maximum wait
                    # 1. Check for success indicators
                    current_count = self.tab.locator("div.clip-row").count()
                    if current_count > initial_count:
                        new_clip_appeared = True
                        logger.info(f"New clip detected! Count: {current_count}")
                        break
                    # Check for "Generating" text in first row
                    if self.tab.locator("div.clip-row").first.locator("text='Generating'").is_visible(timeout=500):
                        new_clip_appeared = True
                        break
                    
                    # 2. Check for CAPTCHA / Challenge
                    if self._detect_captcha():
                        logger.warning("⚠️ CAPTCHA/Challenge detected on Suno!")
                        if progress_callback: progress_callback(rid, "⚠️ CAPTCHA ALGILANDI! Lütfen tarayıcıda çözün... 🕒")
                        self._play_alert()
                        # Pause until cleared
                        while self._detect_captcha() and not self.stop_requested:
                            time.sleep(3)
                        logger.info("Captcha cleared or disappeared. Resuming wait...")

                    time.sleep(2)
                
                if not new_clip_appeared:
                    if progress_callback: progress_callback(rid, "Suno Üretimi Başarısız (CAPTCHA olabilir) ❌")
                    return False

                # Trigger dual download
                logger.info(f"Triggering dual download for {rid}...")
                s1 = self._wait_and_download(suno_title, rid, progress_callback, index=0, suffix="1")
                s2 = self._wait_and_download(suno_title, rid, progress_callback, index=1, suffix="2")
                
                return s1 or s2
            
            logger.error("Create button not enabled or not found.")
            return False
        except Exception as e:
            logger.error(f"process_row failed: {e}")
            return False

    def close(self): pass


if __name__ == "__main__":
    suno = SunoGenerator(project_file="test.xlsx")
    suno.run()
