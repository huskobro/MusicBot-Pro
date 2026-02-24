"""
Excel management mixin for SunoGenerator.
Handles reading/writing status, atomic saves, backups, and recovery.
"""
import os
import time
import shutil
import logging
import openpyxl

logger = logging.getLogger(__name__)


class SunoExcelMixin:
    """Excel file management: status updates, atomic writes, backup & recovery."""

    def update_row_status(self, row_idx, status=None, dl_status=None, dl_attempts=None):
        try:
            # Auto-backup before write (keep last 3 versions)
            self._backup_excel()

            wb = openpyxl.load_workbook(self.metadata_path)
            ws = wb.active
            headers = {str(cell.value).lower(): cell.column for cell in ws[1] if cell.value}

            if status is not None:
                col = headers.get("status")
                if not col:
                    col = ws.max_column + 1
                    ws.cell(row=1, column=col, value="status")
                    headers["status"] = col
                ws.cell(row=row_idx, column=col, value=status)

            if dl_status is not None:
                col = headers.get("dl_status")
                if not col:
                    col = ws.max_column + 1
                    ws.cell(row=1, column=col, value="dl_status")
                    headers["dl_status"] = col
                ws.cell(row=row_idx, column=col, value=dl_status)

            if dl_attempts is not None:
                col = headers.get("dl_attempts")
                if not col:
                    col = ws.max_column + 1
                    ws.cell(row=1, column=col, value="dl_attempts")
                    headers["dl_attempts"] = col
                ws.cell(row=row_idx, column=col, value=dl_attempts)

            # ATOMIC WRITE: Write to temp file, then rename
            temp_path = self.metadata_path + ".tmp"
            wb.save(temp_path)
            shutil.move(temp_path, self.metadata_path)

        except Exception as e:
            logger.error(f"Failed to update Excel status: {e}")
            if "not a zip file" in str(e).lower() or "BadZipFile" in str(e):
                self._recover_excel_from_backup()

    def _backup_excel(self):
        """Keep rotating backups of the Excel file (last 3 versions). Throttled to every 30s."""
        try:
            if not os.path.exists(self.metadata_path):
                return

            now = time.time()
            last_backup = getattr(self, '_last_backup_time', 0)
            if now - last_backup < self.config.backup_interval:
                return
            self._last_backup_time = now

            backup_dir = os.path.join(os.path.dirname(self.metadata_path), ".backups")
            os.makedirs(backup_dir, exist_ok=True)

            base = os.path.basename(self.metadata_path)

            for i in range(self.config.max_backups, 1, -1):
                old = os.path.join(backup_dir, f"{base}.bak{i-1}")
                new = os.path.join(backup_dir, f"{base}.bak{i}")
                if os.path.exists(old):
                    shutil.copy2(old, new)

            shutil.copy2(self.metadata_path, os.path.join(backup_dir, f"{base}.bak1"))
            logger.debug("Excel backup created (.bak1)")

        except Exception as e:
            logger.debug(f"Backup failed (non-critical): {e}")

    def _recover_excel_from_backup(self):
        """Attempt to recover Excel file from the most recent valid backup."""
        try:
            backup_dir = os.path.join(os.path.dirname(self.metadata_path), ".backups")
            base = os.path.basename(self.metadata_path)

            for i in range(1, self.config.max_backups + 1):
                backup_path = os.path.join(backup_dir, f"{base}.bak{i}")
                if os.path.exists(backup_path):
                    temp_test = backup_path + ".temp.xlsx"
                    try:
                        shutil.copy2(backup_path, temp_test)
                        openpyxl.load_workbook(temp_test)  # Verify it's valid
                        os.remove(temp_test)
                        
                        shutil.copy2(backup_path, self.metadata_path)
                        logger.info(f"✅ Excel recovered from backup .bak{i}")
                        return True
                    except Exception as e:
                        if os.path.exists(temp_test): os.remove(temp_test)
                        logger.debug(f"Failed to load backup {backup_path}: {e}")
                        continue

            logger.error("❌ No valid Excel backup found for recovery!")
            return False
        except Exception as e:
            logger.error(f"Recovery failed: {e}")
            return False
