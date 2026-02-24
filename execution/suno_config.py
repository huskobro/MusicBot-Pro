"""
Centralized configuration for SunoGenerator.
All hardcoded values extracted into a single config dataclass.
"""
from dataclasses import dataclass, field


@dataclass
class SunoConfig:
    """All tunable parameters for SunoGenerator in one place."""

    # --- Scan ---
    initial_scan_range: int = 300       # How many rows to check before fallback
    scroll_passes: int = 15             # Max waterfall scroll iterations
    scroll_delay: float = 1.5           # Seconds between scroll passes
    scroll_distance: int = 3000         # Pixels per scroll pass

    # --- Download ---
    popup_timeout: int = 5000           # ms to wait for download popup
    download_timeout: int = 60000       # ms to wait for file download
    retry_count: int = 3                # Retries for download/popup/hover
    format_preference: list = field(default_factory=lambda: ["wav", "mp3"])

    # --- Excel ---
    backup_interval: int = 30           # Seconds between auto-backups
    max_backups: int = 3                # Number of rotating backups to keep

    # --- Timing ---
    short_delay: float = 0.5            # Quick UI settle
    medium_delay: float = 1.5           # Menu open / hover reveal
    long_delay: float = 3.0             # Page load / heavy operation

    # --- Download Verification ---
    min_file_size: int = 10240          # 10 KB - minimum valid audio file
    verify_downloads: bool = True       # Enable post-download integrity check
