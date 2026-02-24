"""
Download mixin for SunoGenerator.
Song finding (scroll, search), download flow (More→Download→Format→Popup→Save),
and post-download integrity verification.
"""
import os
import re
import time
import logging

logger = logging.getLogger(__name__)


class SunoDownloaderMixin:
    """Download logic: song finding, file downloading, and integrity verification."""

    # ──────────────────────────────────────────────────────────────
    #  Download from a pre-found row  (used by Phase B / Phase C)
    # ──────────────────────────────────────────────────────────────
    def _download_from_row(self, target_row, title, rid, suffix="1"):
        """Downloads a song from an already-found row element. Handles More→Download→Format→Popup→Save."""
        try:
            logger.info(f"[_download_from_row] Starting download for {rid}_{suffix}")

            # Scroll to row and hover to reveal buttons
            try:
                target_row.scroll_into_view_if_needed()
                time.sleep(self.config.short_delay)
                target_row.hover()
                time.sleep(self.config.short_delay)
            except Exception as e:
                logger.warning(f"[_download_from_row] Could not scroll/hover for {rid}_{suffix}: {e}")

            # Find "More" button with retries
            target_more = None
            for more_try in range(self.config.retry_count):
                target_more = target_row.locator("button[aria-label*='More' i]").first
                if target_more.count() > 0 and target_more.is_visible():
                    break
                target_more = target_row.locator("button.context-menu-button").last
                if target_more.count() > 0 and target_more.is_visible():
                    break
                try:
                    target_row.hover()
                    time.sleep(1)
                except: pass
                target_more = None

            if not target_more or not target_more.is_visible():
                logger.warning(f"[_download_from_row] 'More' button not visible for {rid}_{suffix}")
                return False

            target_more.scroll_into_view_if_needed()
            time.sleep(self.config.short_delay)
            target_more.click()
            time.sleep(2)

            # Find "Download" in dropdown
            target_dl = self.tab.locator("button:has-text('Download')").first
            if not target_dl.is_visible():
                target_dl = self.tab.get_by_text("Download", exact=True).first

            if not target_dl.is_visible():
                logger.warning(f"[_download_from_row] 'Download' not visible for {rid}_{suffix}")
                try: self.tab.keyboard.press("Escape")
                except: pass
                return False

            target_dl.hover()
            time.sleep(self.config.medium_delay)

            # Find format (WAV/MP3) — respect config preference order
            target_audio = None
            for fmt in self.config.format_preference:
                for _ in range(5):
                    loc = self.tab.locator(f"button[aria-label*='{fmt.upper()}' i]").first
                    if loc.count() > 0 and loc.is_visible():
                        target_audio = loc
                        break
                    time.sleep(1)
                if target_audio and target_audio.is_visible():
                    break

            if not target_audio or not target_audio.is_visible():
                target_audio = self.tab.locator("button:has-text('Audio')").first

            if not target_audio or not target_audio.is_visible():
                logger.warning(f"[_download_from_row] Format button not found for {rid}_{suffix}")
                try: self.tab.keyboard.press("Escape")
                except: pass
                return False

            ext = "wav" if "wav" in (target_audio.get_attribute("aria-label") or "").lower() or "wav" in target_audio.inner_text().lower() else "mp3"
            logger.info(f"[_download_from_row] {ext.upper()} format selected for {rid}_{suffix}")

            # Click format → popup → confirm download
            for dl_retry in range(self.config.retry_count):
                target_audio.click()
                time.sleep(self.config.long_delay)

                try:
                    popup = self.tab.locator("div[role='dialog'], div.chakra-modal__content").last
                    if popup.is_visible(timeout=self.config.popup_timeout):
                        dl_confirm_btn = popup.locator("button").filter(has_text="Download").last
                        if not dl_confirm_btn.is_visible():
                            dl_confirm_btn = popup.locator("button:has-text('Download File')").first

                        if dl_confirm_btn.is_visible():
                            with self.tab.expect_download(timeout=self.config.download_timeout) as download_info:
                                dl_confirm_btn.click()

                            download = download_info.value
                            clean_title = re.sub(r'[^\w\s-]', '', title).strip()
                            clean_title = re.sub(r'[-\s]+', '_', clean_title)
                            filename = f"{clean_title}_{suffix}.{ext}"
                            save_path = os.path.join(self.output_dir, filename)
                            download.save_as(save_path)

                            # ── #9: Post-download integrity check ──
                            if self.config.verify_downloads:
                                if not self._verify_audio_file(save_path, ext):
                                    logger.warning(f"[_download_from_row] ⚠️ File integrity check FAILED for {filename}")
                                    # Keep the file but warn — don't delete, user may want to inspect

                            logger.info(f"[_download_from_row] ✅ Saved {filename}")

                            try: self.tab.keyboard.press("Escape")
                            except: pass
                            return True
                    else:
                        logger.warning(f"[_download_from_row] Popup not visible for {rid}_{suffix}, retry {dl_retry+1}")
                except Exception as e:
                    logger.warning(f"[_download_from_row] Popup error for {rid}_{suffix}: {e}")

                try: self.tab.keyboard.press("Escape")
                except: pass
                time.sleep(2)

            logger.warning(f"[_download_from_row] ❌ All attempts failed for {rid}_{suffix}")
            return False
        except Exception as e:
            logger.error(f"[_download_from_row] Error for {rid}_{suffix}: {e}")
            return False

    # ──────────────────────────────────────────────────────────────
    #  Download with full finding logic (scan + scroll + search)
    # ──────────────────────────────────────────────────────────────
    def _download_specific(self, title, rid, suffix="1"):
        """Downloads a specific occurrence of a song title."""
        try:
            # Ensure safe start state - clear any leftover search and escape menus
            try: self.tab.keyboard.press("Escape")
            except: pass
            time.sleep(0.3)
            try:
                search_input = self.tab.locator("input[aria-label='Search clips']").first
                if search_input.is_visible() and search_input.input_value().strip():
                    logger.info(f"[_download_specific] Clearing leftover search before processing {rid}_{suffix}")
                    search_input.fill("")
                    self.tab.keyboard.press("Enter")
                    time.sleep(2)
            except: pass

            rows = self.tab.locator("div.clip-row")
            count = rows.count()
            if count == 0:
                logger.warning("[_download_specific] No rows found!")
                return False

            occurrence = 0
            target_occur = 0 if suffix == "1" else 1

            target_row = None

            # 1. INITIAL SCAN (Scan first N rows before fallback)
            scan_range = min(self.config.initial_scan_range, count)
            for i in range(scan_range):
                row = rows.nth(i)
                row_text = row.inner_text().lower()

                if i < 3:
                    logger.debug(f"[_download_specific] Row {i} Text Preview: {repr(row_text[:60])}...")

                if str(rid).lower() in row_text:
                    logger.info(f"[_download_specific] Found Match: ID {rid} in row {i}")
                    if occurrence == target_occur:
                        target_row = row
                        break
                    occurrence += 1

            if not target_row:
                # FALLBACK 1: WATERFALL SCROLL
                logger.info(f"[_download_specific] ID {rid} not in top {scan_range}. Using WATERFALL SCROLL...")
                if self._scroll_to_find_song(rid, title):
                    rows = self.tab.locator("div.clip-row")
                    occurrence = 0
                    for i in range(rows.count()):
                        row_text = rows.nth(i).inner_text().lower()
                        if str(rid).lower() in row_text:
                            if occurrence == target_occur:
                                target_row = rows.nth(i)
                                break
                            occurrence += 1

                # FALLBACK 2: SEARCH BAR
                if not target_row:
                    logger.info(f"[_download_specific] Scroll failed for {rid}. Using SEARCH fallback...")
                    search_was_used = False
                    if self._search_for_song(rid, title):
                        search_was_used = True
                        for wait_search in range(5):
                            time.sleep(1)
                            rows = self.tab.locator("div.clip-row")
                            if rows.count() > 0:
                                matched = False
                                for i in range(min(10, rows.count())):
                                    if str(rid).lower() in rows.nth(i).inner_text().lower():
                                        target_row = rows.nth(i)
                                        matched = True
                                        break
                                if matched: break

                    # Clear search after using it
                    if search_was_used and not target_row:
                        try:
                            search_input = self.tab.locator("input[aria-label='Search clips']").first
                            if search_input.is_visible():
                                search_input.fill("")
                                self.tab.keyboard.press("Enter")
                                time.sleep(2)
                                logger.info(f"[_download_specific] Cleared search after failed lookup for {rid}")
                        except: pass

            if not target_row:
                logger.warning(f"[_download_specific] Target row NOT FOUND for {rid}_{suffix}")
                return False

            # Delegate to _download_from_row
            return self._download_from_row(target_row, title, rid, suffix)

        except Exception as e:
            logger.error(f"Download Specific Error {rid}_{suffix}: {e}")
            return False

    # ──────────────────────────────────────────────────────────────
    #  Wait for generation then download (single-song mode)
    # ──────────────────────────────────────────────────────────────
    def _wait_and_download(self, title, rid, progress_callback=None, index=0, suffix="1"):
        try:
            logger.info(f"Waiting for {title} (ID: {rid}, Suffix: {suffix}) to finish generating...")
            if progress_callback: progress_callback(rid, f"Suno Bekleniyor ({suffix})... ⏳")

            found_ready = False
            best_index = index

            for attempt in range(120):
                try:
                    rows = self.tab.locator("div.clip-row")
                    count = rows.count()

                    match_found = False
                    occurrence_count = 0

                    for i in range(min(10, count)):
                        row = rows.nth(i)
                        row_text = row.inner_text().lower()

                        if str(rid).lower() in row_text or str(title).lower() in row_text:
                            if occurrence_count == index:
                                is_gen = row.locator("text='Generating'").is_visible(timeout=300)
                                if not is_gen:
                                    more_btn = row.locator("button[aria-label*='More' i], button.context-menu-button").first
                                    duration_loc = row.locator("text=/\\d{1,2}:\\d{2}/")

                                    if more_btn.is_visible(timeout=300) or (duration_loc.count() > 0 and duration_loc.first.is_visible(timeout=300)):
                                        logger.info(f"Occurrence {index} for {rid} is READY at row {i}.")
                                        best_index = i
                                        found_ready = True
                                        match_found = True
                                        break

                                if attempt % 5 == 0:
                                    logger.info(f"Found occurrence {index} for {rid} but it's still generating...")
                                break
                            occurrence_count += 1

                    if match_found: break
                except Exception as e:
                    logger.debug(f"Search attempt error: {e}")

                time.sleep(3)

            if not found_ready:
                logger.warning(f"Timeout waiting for {title} (suffix {suffix})")
                return False

            if progress_callback: progress_callback(rid, f"Ses İndiriliyor ({suffix})... ⬇️")
            self.tab.keyboard.press("Escape")
            time.sleep(1)

            try:
                rows = self.tab.locator("div.clip-row")
                if rows.count() <= best_index: return True
                target_row = rows.nth(best_index)
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
                time.sleep(self.config.medium_delay)

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
                filename = f"{clean_title}_{suffix}.{ext}"
                save_path = os.path.join(self.output_dir, filename)
                download.save_as(save_path)
                return True

            except Exception as e:
                logger.error(f"Error during Suno download: {e}")
                return False

        except Exception as e:
            logger.error(f"Wait and Download Error {rid}: {e}")
            return False

    # ──────────────────────────────────────────────────────────────
    #  Song readiness check
    # ──────────────────────────────────────────────────────────────
    def _check_if_ready(self, title, rid, suffix="1"):
        """Checks if a song with title/rid is ready (not generating)."""
        try:
            rows = self.tab.locator("div.clip-row")
            count = rows.count()

            occurrence = 0
            target_occur = 0 if suffix == "1" else 1

            for i in range(min(150, count)):
                row = rows.nth(i)
                row_text = row.inner_text().lower()

                if i < 3:
                    logger.debug(f"[_check_if_ready] Row {i} Text Preview: {repr(row_text[:60])}...")

                if str(title).lower() in row_text or (str(rid) + "_" in row_text):
                    logger.info(f"[_check_if_ready] Matched {rid} in row {i}. FULL TEXT: {repr(row_text)}")
                    if occurrence == target_occur:
                        try: row.hover(timeout=500)
                        except: pass

                        is_gen = row.locator("text='Generating'").is_visible(timeout=500)
                        more_btn = row.locator("button[data-context-menu-trigger='true'], button.context-menu-button, [aria-label*='More' i]").first
                        is_more = more_btn.count() > 0

                        logger.info(f"[_check_if_ready] Status: Generating={is_gen}, MoreBtnCount={more_btn.count()}")
                        if not is_gen and is_more:
                            return True
                        return False
                    occurrence += 1
            return False
        except: return False

    # ──────────────────────────────────────────────────────────────
    #  Song finding helpers
    # ──────────────────────────────────────────────────────────────
    def _scroll_to_find_song(self, rid, title):
        """Gradually scrolls the song list container to find a song."""
        logger.info(f"Scrolling to find song ID: {rid}")
        try:
            for _ in range(12):
                rows = self.tab.locator("div.clip-row")
                for i in range(rows.count()):
                    if str(rid).lower() in rows.nth(i).inner_text().lower():
                        return True

                if rows.count() > 0:
                    rows.last.hover()
                    self.tab.mouse.wheel(0, self.config.scroll_distance)
                    time.sleep(self.config.scroll_delay)
            return False
        except: return False

    def _search_for_song(self, rid, title):
        """Uses the Suno search bar to find a specific song (by ID only)."""
        query = str(rid)
        logger.info(f"Searching for song ID: {query}")
        try:
            search_selectors = [
                "input[aria-label='Search clips']",
                "input[aria-label='Search']",
                "input[placeholder*='Search']"
            ]

            search_input = None
            for selector in search_selectors:
                loc = self.tab.locator(selector).first
                if loc.is_visible(timeout=1000):
                    search_input = loc
                    break

            if not search_input:
                search_btn = self.tab.locator("button:has([aria-label*='Search' i]), button.search-toggle").first
                if search_btn.is_visible():
                    search_btn.click()
                    time.sleep(1)
                    search_input = self.tab.locator("input[aria-label='Search clips'], input[placeholder='Search']").first

            if search_input and search_input.is_visible():
                search_input.click()
                time.sleep(0.3)

                try:
                    self.tab.keyboard.press(f"{self.mod}+A")
                    self.tab.keyboard.press("Backspace")
                    time.sleep(0.2)
                except: pass

                search_input.fill("")
                time.sleep(0.3)

                search_input.type(query, delay=0 if self.turbo else 50)
                self.tab.keyboard.press("Enter")

                logger.debug(f"Search query '{query}' submitted.")
                time.sleep(4)
                return True
        except Exception as e:
            logger.warning(f"Search fallback failed: {e}")
        return False

    # ──────────────────────────────────────────────────────────────
    #  #9: Download verification
    # ──────────────────────────────────────────────────────────────
    def _verify_audio_file(self, file_path, expected_ext="wav"):
        """Verify downloaded file is a valid audio file."""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"[verify] File does not exist: {file_path}")
                return False

            size = os.path.getsize(file_path)
            if size < self.config.min_file_size:
                logger.warning(f"[verify] File too small ({size} bytes): {file_path}")
                return False

            with open(file_path, 'rb') as f:
                header = f.read(12)

            if expected_ext == "wav":
                # WAV files start with RIFF....WAVE
                if header[:4] != b'RIFF' or header[8:12] != b'WAVE':
                    logger.warning(f"[verify] Invalid WAV header: {file_path}")
                    return False
            elif expected_ext == "mp3":
                # MP3 files start with ID3 tag or sync bytes (0xFF 0xFB/0xF3/0xF2)
                if not (header[:3] == b'ID3' or (header[0] == 0xFF and (header[1] & 0xE0) == 0xE0)):
                    logger.warning(f"[verify] Invalid MP3 header: {file_path}")
                    return False

            logger.debug(f"[verify] ✅ Valid {expected_ext.upper()} file ({size:,} bytes): {os.path.basename(file_path)}")
            return True

        except Exception as e:
            logger.warning(f"[verify] Error checking {file_path}: {e}")
            return False
