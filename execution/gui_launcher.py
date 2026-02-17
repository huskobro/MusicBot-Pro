import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor

# Configure logging IMMEDIATELY to catch all imports and initializations.
def get_safe_workspace():
    ws = os.path.expanduser("~/Documents/MusicBot_Workspace")
    try:
        if not os.path.exists(ws): os.makedirs(ws, exist_ok=True)
    except: pass
    return ws

workspace = get_safe_workspace()
debug_log_path = os.path.join(workspace, "musicbot_debug.log")
crash_report_path = os.path.join(workspace, "crash_report.txt")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(debug_log_path, encoding='utf-8', mode='a')
    ],
    force=True
)
logger = logging.getLogger(__name__)

TRANSLATIONS = {
    "English": {
        "title": "MusicBot Pro",
        "settings": "⚙️ Settings",
        "refresh": "🔄 Refresh",
        "new_project": "✨ New Project",
        "load_project": "📂 Load Project",
        "images": "🖼️ Images",
        "search": "🔍 Search:",
        "global_settings": "🚀 Global Run Settings (Defaults for items)",
        "lyrics": "Lyrics",
        "music": "Music",
        "art_prompt": "Art Prompt",
        "art_prompt": "Art Prompt",
        "art_image": "Art Image",
        "video": "Video",
        "column_id": "ID",
        "column_title": "Title / Prompt",
        "column_style": "Style",
        "column_progress": "Status & Progress",
        "start": "▶ START ENGINE",
        "stop": "⬛ STOP ENGINE",
        "show_log": "▲ SHOW ACTIVITY LOG",
        "hide_log": "▼ HIDE ACTIVITY LOG",
        "no_project": "No Project Loaded",
        "ready": "Ready",
        "working_on": "Working on:",
        "processing": "Processing",
        "done": "Done",
        "error": "Error",
        "ui_language": "UI Language",
        "log_startup": "Open Activity Log at Startup",
        "active_run": "Active Run",
        "general": "General",
        "humanizer": "Humanizer",
        "prompts": "Prompts",
        "log": "Log",
        "save_all": "💾 Save All Settings & Active Profile",
        "vocal_gender": "Vocal Gender",
        "audio_influence": "Audio Influence",
        "weirdness": "Weirdness",
        "style_influence": "Style Influence",
        "lyrics_mode": "Lyrics Mode",
        "profiles_tab": "Profiles",
        "profile_mgmt": "Artist Identity & Preset Management",
        "active_profile": "Active Profile:",
        "preset_alias": "Preset Alias:",
        "artist_name_label": "Artist Name:",
        "artist_style_label": "Artist Music Style:",
        "save_preset_btn": "💾 Save Current as Preset",
        "load_selected_btn": "📂 Load Selected",
        "delete_selected_btn": "🗑️ Delete Selected",
        "default_steps": "Default Run Steps (Checked on Start)",
        "note_changes": "Note: Changes take effect on next 'Start'.",
        "gemini_logic": "Gemini Content Logic",
        "gen_lyrics_vs_title": "Generate Lyrics (vs just Title)",
        "gen_music_style": "Generate Music Style",
        "gen_visual_prompts": "Generate Visual Prompts",
        "gen_video_prompts": "Generate Video Prompts",
        "automation_delays": "Automation Delays",
        "suno_delay_label": "Suno Gen Delay (s):",
        "startup_delay_label": "Browser Startup Delay (s):",
        "lang_reg": "Language & Regional",
        "target_lang_label": "Target Song Language:",
        "browser_action_label": "Browser Action",
        "open_chrome_btn": "🌐 Open Chrome for Login",
        "suno_adv_params": "Music Generation Parameters",
        "suno_adv_tab": "Suno Adv",
        "enable_persona_label": "Enable Persona Profile:",
        "alias_label": "Alias:",
        "link_label": "Link:",
        "enable_vocal_gender_label": "Enable Vocal Gender:",
        "enable_audio_influence_label": "Enable Audio Influence (%):",
        "enable_weirdness_label": "Enable Weirdness:",
        "enable_style_influence_label": "Enable Style Influence:",
        "enable_lyrics_mode_label": "Enable Lyrics Mode:",
        "suno_batch_label": "Enable Batch Mode (Generate All -> Download All)",
        "batch_op_full": "Full Cycle (Gen + DL)",
        "batch_op_gen": "Generate Only",
        "batch_op_dl": "Download Only",
        "human_settings_label": "Human-like Interaction Settings",
        "enable_humanizer_label": "ENABLE HUMANIZER (Global)",
        "activate_humanizer_label": "Activate Humanizer in:",
        "phase1_label": "Phase 1: Gemini",
        "phase1_label": "Phase 1: Gemini",
        "phase2_label": "Phase 2: Suno",
        "phase3_label": "Phase 3: Video",
        "human_level_label": "Humanizer Level:",
        "typing_speed_label": "Typing Speed:",
        "speed_hint": "(0.05 = Fastest / 1.0 = Normal / 2.5 = Slowest)",
        "max_retries_label": "Max Retries:",
        "enable_adaptive_label": "Enable Adaptive Delays",
        "video_settings_label": "Video Generation Settings",
        "video_effect_label": "Visual Effect:",
        "lyrics_master_label": "1. Lyrics Master Prompt (Gemini):",
        "visual_master_label": "2. Visual Master Prompt (Midjourney Style):",
        "video_master_label": "3. Video Master Prompt (Sora/Runway):",
        "art_master_label": "4. Art Master Prompt (YouTube Thumbnail):",
        "startup_opts_label": "Startup Options",
        "msg_no_project": "❌ No Project Loaded! Please Load or Create a project.",
        "msg_load_first": "Please load a project file first.",
        "msg_no_steps": "❌ No steps selected! Please check at least one 'Run Step'.",
        "msg_select_step_warn": "Please select at least one step to run.",
        "msg_confirm_process_all": "No songs selected. Process ALL listed songs?",
        "msg_stopping": "Stopping engine...",
        "msg_halted": "Process halted by user command.",
        "msg_done_title": "Done",
        "msg_done_info": "Selected tasks completed! 🎵",
        "msg_critical_error": "Critical Error",
        "msg_confirm_regen": "Regenerate?",
        "msg_regen_body": "Some rows already have data (Lyrics, Prompts, etc.).\n\nDo you want to regenerate them?\n\n'Yes' will update data, 'No' will only complete missing ones.",
        "msg_restart_lang": "Restart the application to apply UI language changes.",
        "msg_settings_saved": "Settings and Prompts saved successfully!",
        "msg_enter_preset_alias": "Please enter a Profile Alias name.",
        "msg_preset_saved": "Profile '{alias}' saved successfully!",
        "msg_preset_loaded": "Profile '{alias}' loaded!",
        "msg_confirm_delete_preset": "Delete profile '{alias}'?",
        "msg_failed_to_save": "Failed to save: {error}",
        "msg_new_project_created": "New project created and loaded! 🚀",
        "msg_failed_to_create_project": "Could not create project",
        "msg_loaded_songs": "Loaded {count} songs from project.",
        "msg_failed_to_load_project": "Failed to load project",
        "vocal_default": "Default",
        "vocal_none": "None",
        "vocal_male": "Male",
        "vocal_female": "Female",
        "mode_manual": "Manual",
        "mode_auto": "Auto",
        "level_low": "LOW",
        "level_medium": "MEDIUM",
        "success": "Success",
        "error_title": "Error",
        "warning": "Warning",
        "confirm": "Confirm",
        "badge_idle": "IDLE",
        "badge_active": "ACTIVE",
        "badge_stopping": "STOPPING",
        "badge_error": "ERROR",
        "log_settings_loaded": "✅ Settings loaded from settings.json",
        "log_settings_fail": "❌ Failed to load settings: {error}",
        "log_project_init": "✅ Project structure initialized for {name}",
        "log_project_load_error": "❌ Error loading project: {error}",
        "log_halted": "🛑 Process halted by user command.",
        "log_browser_stop": "🛑 Browser terminated by user stop command.",
        "log_chrome_start": "🌐 Initializing Chrome for Login...",
        "log_wait_chrome": "⏳ Please wait, browser is starting...",
        "log_chrome_success": "✅ Chrome started successfully!",
        "log_chrome_profile": "📂 Profile Path: {path}",
        "log_chrome_login": "👉 Please log in to Suno/Gemini now.",
        "log_chrome_close": "👉 You can close the browser window when finished.",
        "video_fps_label": "Frame Rate (FPS):",
        "video_res_label": "Resolution:",
        "video_intensity_label": "Effect Intensity:",
        "video_assets_label": "Source Assets Folder:",
        "video_res_shorts": "Vertical (Shorts - 1080x1920)",
        "video_res_hd": "Horizontal (HD - 1920x1080)",
        "video_res_sd": "Horizontal (SD - 1280x720)",
        "glitch": "Glitch",
        "ken_burns": "Ken Burns (Zoom)",
        "vignette": "Vignette",
        "browse": "Browse",
        "msg_select_folder": "Please select a folder",
        "msg_enter_test_link": "Please enter a link to test or select from the list.",
        "info": "Info",
        "video_output_mode_label": "Video Output Path:",
        "video_output_same_label": "Save in input/profile folder",
        "video_output_custom_label": "Save in 'Output_Videos' (System Default)",
        "video_assets_hint": "💡 If empty, 'output_media/[Profile_Name]' will be searched for images first.",
        "last_profile_label": "Last Profile:",
        "save_to_profile_note": "Note: 'Save All' also updates the active preset.",
        "add_new_profile_btn": "✨ Add New Profile",
        "compilation": "Compilation (Step 6)",
        "phase4_label": "Phase 4: Compilation",
        "log_merge_start": "🎬 Starting Video Merger (Phase 6)...",
        "log_merge_success": "✅ Compilation video created: {path}",
        "log_merge_fail": "❌ Failed to create compilation video: {error}",
        "log_merge_no_files": "⚠️ No videos found to merge in {path}.",
        "reset_chrome_btn": "🧹 Reset Chrome Profile (Fresh Install)",
        "msg_confirm_reset_chrome": "Are you sure you want to RESET Chrome?\n\nThis will CLOSE the browser, backup your current login sessions, and start with a completely FRESH profile.\n\nYou will need to login again to Suno/Gemini.",
        "log_chrome_reset_success": "✅ Chrome profile reset successfully. New profile will be created on next launch.",
        "log_chrome_reset_fail": "❌ Failed to reset Chrome profile: {error}",
        "select_all": "Select All",
        "deselect_all": "Deselect All",
        "active_only": "⚡ Show Active/Selected Only",
        "eta_label": "ETA: {time}",
        "filter_status": "Filter Status:",
        "f_all": "All",
        "f_done": "Completed",
        "f_pending": "Pending/Incomplete",
        "f_no_lyrics": "Missing Lyrics",
        "f_no_music": "Missing Music",
        "f_no_art": "Missing Art",
        "f_no_video": "Missing Video",
        "video_parallel_label": "Parallel Render Count:",
        "video_quality_label": "Video Quality & Performance",
        "video_selection_label": "Video Selection Mode:",
        "v_mode_1": "Only _1",
        "v_mode_2": "Only _2",
        "v_mode_both": "Both (_1 & _2)",
        "column_materials": "Materials",
        "f_missing_r": "Missing Images",
        "f_missing_m1": "Missing Music 1",
        "f_missing_m2": "Missing Music 2",
        "video_assets_output_label": "Assets & Output Settings"
    },
    "Turkish": {
        "title": "MusicBot Pro",
        "settings": "⚙️ Ayarlar",
        "refresh": "🔄 Yenile",
        "new_project": "✨ Yeni Proje",
        "load_project": "📂 Proje Yükle",
        "images": "🖼️ Resimler",
        "search": "🔍 Ara:",
        "global_settings": "🚀 Global Çalıştırma Ayarları (Varsayılanlar)",
        "lyrics": "Sözler",
        "music": "Müzik",
        "art_prompt": "Resim Prompt",
        "art_prompt": "Resim Prompt",
        "art_image": "Resim Üretim",
        "video": "Video",
        "column_id": "ID",
        "column_title": "Başlık / Prompt",
        "column_style": "Tarz",
        "column_progress": "Durum & İlerleme",
        "start": "▶ MOTORU BAŞLAT",
        "stop": "⬛ MOTORU DURDUR",
        "show_log": "▲ AKTİVİTE GÜNLÜĞÜNÜ GÖSTER",
        "hide_log": "▼ AKTİVİTE GÜNLÜĞÜNÜ GİZLE",
        "no_project": "Proje Yüklü Değil",
        "ready": "Hazır",
        "working_on": "Çalışılan:",
        "processing": "İşleniyor",
        "done": "Tamamlandı",
        "error": "Hata",
        "ui_language": "Arayüz Dili",
        "log_startup": "Başlangıçta Günlüğü Aç",
        "active_run": "Aktif Çalışma",
        "general": "Genel",
        "humanizer": "İnsanlaştırıcı",
        "prompts": "Promptlar",
        "log": "Günlük",
        "save_all": "💾 Tüm Ayarları ve Aktif Profili Kaydet",
        "vocal_gender": "Vokal Cinsiyeti",
        "audio_influence": "Ses Etkisi",
        "weirdness": "Tuhaflık",
        "style_influence": "Stil Etkisi",
        "lyrics_mode": "Şarkı Sözü Modu",
        "profiles_tab": "Profiller",
        "profile_mgmt": "Sanatçı Kimliği ve Profil Yönetimi",
        "active_profile": "Aktif Profil Seçimi:",
        "preset_alias": "Profil İsmi (Alias):",
        "artist_name_label": "Sanatçı Adı:",
        "artist_style_label": "Sanatçı Müzik Tarzı:",
        "save_preset_btn": "💾 Profili Kaydet/Güncelle",
        "load_selected_btn": "📂 Seçileni Yükle",
        "delete_selected_btn": "🗑️ Seçileni Sil",
        "default_steps": "Varsayılan Çalıştırma Aşamaları (Başlangıçta Seçili)",
        "note_changes": "Not: Değişiklikler bir sonraki 'Başlat' işleminde etkili olur.",
        "gemini_logic": "Gemini İçerik Mantığı",
        "gen_lyrics_vs_title": "Söz Üret (Sadece Başlık Yerine)",
        "gen_music_style": "Müzik Tarzı Üret",
        "gen_visual_prompts": "Görsel Promptları Üret",
        "gen_video_prompts": "Video Promptları Üret",
        "automation_delays": "Otomasyon Gecikmeleri",
        "suno_delay_label": "Suno Üretim Gecikmesi (sn):",
        "startup_delay_label": "Tarayıcı Başlangıç Gecikmesi (sn):",
        "lang_reg": "Dil ve Bölgesel",
        "target_lang_label": "Hedef Şarkı Dili:",
        "browser_action_label": "Tarayıcı İşlemi",
        "open_chrome_btn": "🌐 Giriş için Chrome'u Aç",
        "suno_adv_params": "Müzik Üretim Parametreleri",
        "suno_adv_tab": "Suno Gelişmiş",
        "enable_persona_label": "Persona Profilini Etkinleştir:",
        "alias_label": "Takma Ad:",
        "link_label": "Bağlantı:",
        "enable_vocal_gender_label": "Vokal Cinsiyetini Etkinleştir:",
        "enable_audio_influence_label": "Ses Etkisini Etkinleştir (%):",
        "enable_weirdness_label": "Tuhaflığı Etkinleştir:",
        "enable_style_influence_label": "Stil Etkisini Etkinleştir:",
        "enable_lyrics_mode_label": "Şarkı Sözü Modunu Etkinleştir:",
        "suno_batch_label": "Toplu Modu Etkinleştir (Hepsini Üret -> Hepsini İndir)",
        "batch_op_full": "Tam Döngü (Üret + İndir)",
        "batch_op_gen": "Sadece Üret",
        "batch_op_dl": "Sadece İndir",
        "human_settings_label": "İnsan Benzeri Etkileşim Ayarları",
        "enable_humanizer_label": "İNSANLAŞTIRICIYI ETKİNLEŞTİR (Global)",
        "activate_humanizer_label": "İnsanlaştırıcıyı Şurada Aktifleştir:",
        "phase1_label": "Aşama 1: Gemini",
        "phase1_label": "Aşama 1: Gemini",
        "phase2_label": "Aşama 2: Suno",
        "phase3_label": "Aşama 3: Video",
        "human_level_label": "İnsanlaştırma Seviyesi:",
        "typing_speed_label": "Yazma Hızı:",
        "speed_hint": "(0.05 = En Hızlı / 1.0 = Normal / 2.5 = En Yavaş)",
        "max_retries_label": "Maksimum Deneme:",
        "enable_adaptive_label": "Uyarlanabilir Gecikmeleri Etkinleştir",
        "video_settings_label": "Video Oluşturma Ayarları",
        "video_effect_label": "Görsel Efekt:",
        "lyrics_master_label": "1. Şarkı Sözü Ana Promptu (Gemini):",
        "visual_master_label": "2. Görsel Ana Promptu (Midjourney):",
        "video_master_label": "3. Video Ana Promptu (Sora/Runway):",
        "art_master_label": "4. Resim Ana Promptu (YouTube):",
        "startup_opts_label": "Başlangıç Seçenekleri",
        "msg_no_project": "❌ Proje Yüklü Değil! Lütfen bir proje yükleyin veya oluşturun.",
        "msg_load_first": "Lütfen önce bir proje dosyası yükleyin.",
        "msg_no_steps": "❌ Hiçbir aşama seçilmedi! Lütfen en az bir 'Çalıştırma Aşaması' seçin.",
        "msg_select_step_warn": "Lütfen çalıştırmak için en az bir aşama seçin.",
        "msg_confirm_process_all": "Şarkı seçilmedi. Listedeki TÜM şarkılar işlensin mi?",
        "msg_stopping": "Motor durduruluyor...",
        "msg_halted": "İşlem kullanıcı komutuyla durduruldu.",
        "msg_done_title": "Tamamlandı",
        "msg_done_info": "Seçilen işlemler tamamlandı! 🎵",
        "msg_critical_error": "Kritik Hata",
        "msg_confirm_regen": "Yeniden Üret?",
        "msg_regen_body": "Bazı satırlarda zaten veri (Söz, Prompt vb.) mevcut.\n\nBunları yeniden üretmek ister misiniz?\n\n'Evet' derseniz veriler güncellenir, 'Hayır' derseniz sadece eksikler tamamlanır.",
        "msg_restart_lang": "Arayüz dili değişikliklerinin uygulanması için uygulamayı yeniden başlatın.",
        "msg_settings_saved": "Ayarlar ve Promptlar başarıyla kaydedildi!",
        "msg_enter_preset_alias": "Lütfen bir Preset Adı girin.",
        "msg_preset_saved": "Preset '{alias}' başarıyla kaydedildi!",
        "msg_preset_loaded": "Preset '{alias}' yüklendi!",
        "msg_confirm_delete_preset": "Preset '{alias}' silinsin mi?",
        "msg_failed_to_save": "Kaydetme hatası: {error}",
        "msg_new_project_created": "Yeni proje oluşturuldu ve yüklendi! 🚀",
        "msg_failed_to_create_project": "Proje oluşturulamadı",
        "msg_loaded_songs": "Projeden {count} şarkı yüklendi.",
        "msg_failed_to_load_project": "Proje yüklenemedi",
        "vocal_default": "Varsayılan",
        "vocal_none": "Yok",
        "vocal_male": "Erkek",
        "vocal_female": "Kadın",
        "mode_manual": "Manuel",
        "mode_auto": "Otomatik",
        "level_low": "DÜŞÜK",
        "level_medium": "ORTA",
        "level_high": "YÜKSEK",
        "success": "Başarı",
        "error_title": "Hata",
        "warning": "Uyarı",
        "confirm": "Onay",
        "badge_idle": "BEKLEMEDE",
        "badge_active": "AKTİF",
        "badge_stopping": "DURDURULUYOR",
        "badge_error": "HATA",
        "log_settings_loaded": "✅ Ayarlar settings.json dosyasından yüklendi",
        "log_settings_fail": "❌ Ayarlar yüklenemedi: {error}",
        "log_project_init": "✅ Proje yapısı {name} için hazırlandı",
        "log_project_load_error": "❌ Proje yükleme hatası: {error}",
        "log_halted": "🛑 İşlem kullanıcı komutuyla durduruldu.",
        "log_browser_stop": "🛑 Tarayıcı kullanıcı tarafından kapatıldı.",
        "log_chrome_start": "🌐 Giriş için Chrome başlatılıyor...",
        "log_wait_chrome": "⏳ Lütfen bekleyin, tarayıcı açılıyor...",
        "log_chrome_success": "✅ Chrome başarıyla başlatıldı!",
        "log_chrome_profile": "📂 Profil Yolu: {path}",
        "log_chrome_login": "👉 Lütfen şimdi Suno/Gemini oturumu açın.",
        "log_chrome_close": "👉 İşleminiz bitince tarayıcı penceresini kapatabilirsiniz.",
        "video_fps_label": "Kare Hızı (FPS):",
        "video_res_label": "Çözünürlük:",
        "video_intensity_label": "Efekt Yoğunluğu:",
        "video_assets_label": "Kaynak Materyal Klasörü:",
        "video_res_shorts": "Dikey (Shorts - 1080x1920)",
        "video_res_hd": "Yatay (HD - 1920x1080)",
        "video_res_sd": "Yatay (SD - 1280x720)",
        "snow": "Kar Efekti",
        "rain": "Yağmur Efekti",
        "particles": "Parçacıklar",
        "glitch": "Bozulma (Glitch)",
        "ken_burns": "Yakınlaşma (Ken Burns)",
        "vignette": "Köşe Karartma (Vignette)",
        "browse": "Gözat",
        "msg_select_folder": "Lütfen bir klasör seçin",
        "msg_persona_loaded": "'{alias}' düzenleme için yüklendi.\nDeğişiklik yapıp '+' butonuna basın.",
        "msg_enter_test_link": "Lütfen test edilecek bir link girin veya listeden seçin.",
        "info": "Bilgi",
        "video_output_mode_label": "Video Çıktı Yolu:",
        "video_output_same_label": "Girdi/Profil klasörüne kaydet",
        "video_output_custom_label": "'Output_Videos' klasörüne kaydet (Varsayılan)",
        "video_assets_hint": "💡 Boş bırakılırsa, resimler için önce 'output_media/[Profil_Adı]' klasörüne bakılır.",
        "last_profile_label": "Son Profil:",
        "save_to_profile_note": "💡 İpucu: Yeni bir profil oluşturmak için 'Profil İsmi'ni değiştirip '+'ya basın. Mevcutu silmek için '-'ye, formu temizlemek için '✨'ye basın.",
        "add_new_profile_btn": "✨ Yeni Profil Ekle",
        "compilation": "Birleştirme",
        "phase4_label": "Aşama 4: Birleştirme",
        "log_merge_start": "🎬 Video Birleştirme Başlatılıyor...",
        "log_merge_success": "✅ Uzun video başarıyla oluşturuldu: {path}",
        "log_merge_fail": "❌ Uzun video oluşturulamadı: {error}",
        "log_merge_no_files": "⚠️ {path} klasöründe birleştirilecek video bulunamadı.",
        "reset_chrome_btn": "🧹 Chrome Profilini Sıfırla (Sıfırdan Kur)",
        "msg_confirm_reset_chrome": "Chrome'u SIFIRLAMAK istediğinize emin misiniz?\n\nBu işlem tarayıcıyı KAPATACAK, mevcut girişlerinizi yedekleyecek ve tamamen TEMİZ bir profil ile başlayacaktır.\n\nSuno/Gemini girişlerini tekrar yapmanız gerekecektir.",
        "log_chrome_reset_success": "✅ Chrome profili başarıyla sıfırlandı. Bir sonraki açılışta yeni profil oluşturulacak.",
        "log_chrome_reset_fail": "❌ Chrome profili sıfırlanamadı: {error}",
        "select_all": "Hepsini Seç",
        "deselect_all": "Seçimi Kaldır",
        "active_only": "⚡ Sadece Aktif/Seçili Olanları Göster",
        "eta_label": "Tahmini Bitiş: {time}",
        "filter_status": "Durum Filtresi:",
        "f_all": "Hepsi",
        "f_done": "Tamamlananlar",
        "f_pending": "Eksik/Bekleyenler",
        "f_no_lyrics": "Sözü Olmayanlar",
        "f_no_music": "Müziği Olmayanlar",
        "f_no_art": "Kapağı Olmayanlar",
        "f_no_video": "Videosu Olmayanlar",
        "video_parallel_label": "Paralel Render Sayısı:",
        "video_quality_label": "Video Kalitesi ve Performans",
        "video_selection_label": "Video Seçim Modu:",
        "v_mode_1": "Sadece _1",
        "v_mode_2": "Sadece _2",
        "v_mode_both": "Her İkisi (_1 & _2)",
        "column_materials": "Materyaller",
        "f_missing_r": "Eksik Resimler",
        "f_missing_m1": "Eksik Müzik 1",
        "f_missing_m2": "Eksik Müzik 2",
        "video_assets_output_label": "Klasör ve Çıktı Ayarları"
    }
}

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext, filedialog
import time
import threading
import shutil
import openpyxl
import json
from openpyxl.styles import PatternFill
from browser_controller import BrowserController

# PyInstaller bundle path handling
def get_bundle_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    # If not frozen, we assume we are in 'MusicBot/execution/gui_launcher.py'
    # So root is two levels up
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

bundle_dir = get_bundle_dir()

class GuiLogger(logging.Handler):
    """Custom logging handler that directs logs to a ScrolledText widget."""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.text_widget.tag_config("INFO", foreground="#333333")
        self.text_widget.tag_config("ERROR", foreground="#d9534f", font=("Consolas", 9, "bold"))
        self.text_widget.tag_config("WARNING", foreground="#f0ad4e")
        self.text_widget.tag_config("SYSTEM", foreground="#5bc0de", font=("Consolas", 9, "italic"))

    def emit(self, record):
        msg = self.format(record)
        def append():
            try:
                if self.text_widget.winfo_exists():
                    self.text_widget.configure(state='normal')
                    self.text_widget.insert(tk.END, msg + '\n', record.levelname)
                    self.text_widget.configure(state='disabled')
                    self.text_widget.yview(tk.END)
            except:
                pass
        
        # Ensure thread safety by scheduling update on main loop
        try:
            if self.text_widget.winfo_exists():
                self.text_widget.after(0, append)
        except:
            pass

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, config, app_instance):
        super().__init__(parent)
        self.title(app_instance.t("settings"))
        self.geometry("950x750") # Widened to ensure all tabs are visible on all OSs
        self.config = config
        self.parent = parent
        self.app = app_instance
        
        # Initialize variables early to avoid AttributeErrors
        self.var_video_output_mode = tk.StringVar(value=config.get("video_output_mode", "profile"))
        
        # Root Configuration: Force Button Frame to Bottom using PACK (safer than grid for footers)
        # 1. Create Notebook (but don't pack yet)
        self.notebook = ttk.Notebook(self)
        
        # 2. Create and Pack Button Frame (BOTTOM) - Guaranteed Visibility
        f_btn = ttk.Frame(self, padding=10)
        f_btn.pack(side="bottom", fill="x")
        
        btn_save = ttk.Button(f_btn, text=self.app.t("save_all"), command=self.save_settings, style="Action.TButton")
        btn_save.pack(fill="x", ipady=12) 

        self.notebook.pack(side="top", fill="both", expand=True, padx=10, pady=(10, 5))

        # --- PRE-INITIALIZE ALL UI ATTRIBUTES TO PREVENT ATTRIBUTE ERRORS ---
        self.prompts_path = os.path.join(os.path.dirname(config.get("metadata_path", "")), "prompts.json")
        self.personas = []
        self.ent_preset_alias = None
        self.ent_artist_name = None
        self.ent_artist_style = None
        self.combo_preset_select = None
        self.ent_video_assets = None
        self.ent_video_custom_path = None
        self.combo_res = None
        self.spin_fps = None
        self.scale_intensity = None
        self.txt_lyrics = None
        self.txt_visual = None
        self.txt_video = None
        self.txt_art = None
        self.var_lyrics = None
        self.var_style = None
        self.var_visual = None
        self.var_video = None
        self.entry_delay = None
        self.entry_startup = None
        self.combo_lang = None
        self.combo_ui_lang = None
        self.var_log_at_start = None
        self.var_def_lyrics = None
        self.var_def_music = None
        self.var_def_art_p = None
        self.var_def_art_i = None
        self.var_def_video = None
        self.var_def_compilation = None
        self.var_persona_link_enabled = None
        self.combo_persona_select = None
        self.var_gender_enabled = None
        self.combo_gender = None
        self.scale_audio = None
        self.var_audio_enabled = None
        self.scale_weird = None
        self.var_weird_enabled = None
        self.scale_style = None
        self.var_style_enabled = None
        self.var_lyrics_mode_enabled = None
        self.combo_lyrics_mode = None
        self.var_humanizer_enabled = None
        self.var_h_gemini = None
        self.var_h_suno = None
        self.var_h_video = None
        self.combo_human_level = None
        self.scale_speed = None
        self.spin_retries = None
        self.var_adaptive = None
        self.combo_parallel_render = None
        self.combo_video_selection = None
        self.effect_vars = {}
        self.var_suno_batch = None
        self.var_batch_op = None

        # --- TAB 0: Profiles ---
        self.tab_presets = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_presets, text=self.app.t("profiles_tab"))
        
        f_pre_root = ttk.Frame(self.tab_presets, padding=15)
        f_pre_root.pack(fill="both", expand=True)

        f_presets = ttk.LabelFrame(f_pre_root, text=self.app.t("profile_mgmt"), padding=15)
        f_presets.pack(fill="x", padx=5, pady=5)

        # 1. Selection Row (Which profile are we viewing/using?)
        f_sel = ttk.Frame(f_presets)
        f_sel.pack(fill="x", pady=(0, 10))
        ttk.Label(f_sel, text=self.app.t("active_profile"), font=("Helvetica", 10, "bold")).pack(side="left")
        
        self.presets = config.get("artist_presets", {})
        self.combo_preset_select = ttk.Combobox(f_sel, values=list(self.presets.keys()), state="readonly")
        self.combo_preset_select.pack(side="left", fill="x", expand=True, padx=10)
        self.combo_preset_select.bind("<<ComboboxSelected>>", lambda e: self.load_preset())

        # 2. Management & Alias Row (Persona style)
        f_mgmt = ttk.Frame(f_presets)
        f_mgmt.pack(fill="x", pady=(0, 15))
        
        ttk.Label(f_mgmt, text=self.app.t("preset_alias")).pack(side="left")
        self.ent_preset_alias = ttk.Entry(f_mgmt)
        self.ent_preset_alias.pack(side="left", padx=5, fill="x", expand=True)
        
        # Action Buttons clustered next to the Alias entry
        btn_add = ttk.Button(f_mgmt, text="+", width=3, command=lambda: self.save_preset(silent=False))
        btn_add.pack(side="left", padx=1)
        btn_del = ttk.Button(f_mgmt, text="-", width=3, command=self.delete_preset)
        btn_del.pack(side="left", padx=1)
        btn_clear = ttk.Button(f_mgmt, text="✨", width=3, command=self.clear_preset_form)
        btn_clear.pack(side="left", padx=1)

        # 3. Details Grid (The "Old Beauty" - for artist specific fields)
        f_grid = ttk.Frame(f_presets)
        f_grid.pack(fill="x")

        # Artist Name
        ttk.Label(f_grid, text=self.app.t("artist_name_label")).grid(row=0, column=0, sticky="w", pady=5)
        self.ent_artist_name = ttk.Entry(f_grid)
        self.ent_artist_name.grid(row=0, column=1, sticky="ew", pady=5)

        # Artist Style
        ttk.Label(f_grid, text=self.app.t("artist_style_label")).grid(row=1, column=0, sticky="w", pady=5)
        self.ent_artist_style = ttk.Entry(f_grid)
        self.ent_artist_style.grid(row=1, column=1, sticky="ew", pady=5)

        f_grid.columnconfigure(1, weight=1)

        ttk.Label(f_pre_root, text=self.app.t("save_to_profile_note"), font=("Helvetica", 9, "italic"), foreground="gray", wraplength=800).pack(pady=10)
        
        # --- TAB 1: General ---
        self.tab_general = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_general, text=self.app.t("general"))
        
        # Scrollable area for General Tab
        canvas = tk.Canvas(self.tab_general, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_general, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 1. Default Checked Steps
        f_defaults = ttk.LabelFrame(scroll_frame, text=self.app.t("default_steps"), padding=10)
        f_defaults.pack(fill="x", padx=10, pady=5)
        
        self.var_def_lyrics = tk.BooleanVar(value=config.get("default_run_lyrics", True))
        ttk.Checkbutton(f_defaults, text="1. " + self.app.t("lyrics"), variable=self.var_def_lyrics).pack(anchor="w")
        self.var_def_music = tk.BooleanVar(value=config.get("default_run_music", True))
        ttk.Checkbutton(f_defaults, text="2. " + self.app.t("music"), variable=self.var_def_music).pack(anchor="w")
        self.var_def_art_p = tk.BooleanVar(value=config.get("default_run_art_prompt", True))
        ttk.Checkbutton(f_defaults, text="3. " + self.app.t("art_prompt"), variable=self.var_def_art_p).pack(anchor="w")
        self.var_def_art_i = tk.BooleanVar(value=config.get("default_run_art_image", True))
        ttk.Checkbutton(f_defaults, text="4. " + self.app.t("art_image"), variable=self.var_def_art_i).pack(anchor="w")
        self.var_def_video = tk.BooleanVar(value=config.get("default_run_video", False))
        ttk.Checkbutton(f_defaults, text="5. " + self.app.t("video"), variable=self.var_def_video).pack(anchor="w")
        
        self.var_def_compilation = tk.BooleanVar(value=config.get("default_run_compilation", True))
        ttk.Checkbutton(f_defaults, text="6. " + self.app.t("compilation"), variable=self.var_def_compilation).pack(anchor="w")

        # --- TAB 1.2: Active Workflow ---
        self.tab_workflow = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_workflow, text=self.app.t("active_run"))
        
        f_active = ttk.LabelFrame(self.tab_workflow, text=self.app.t("active_run"), padding=15)
        f_active.pack(fill="both", expand=True, padx=10, pady=10)
        
        ttk.Checkbutton(f_active, text="1. " + self.app.t("lyrics"), variable=self.app.var_run_lyrics).pack(anchor="w", pady=5)
        ttk.Checkbutton(f_active, text="2. " + self.app.t("music"), variable=self.app.var_run_music).pack(anchor="w", pady=5)
        ttk.Checkbutton(f_active, text="3. " + self.app.t("art_prompt"), variable=self.app.var_run_art_prompt).pack(anchor="w", pady=5)
        ttk.Checkbutton(f_active, text="4. " + self.app.t("art_image"), variable=self.app.var_run_art_image).pack(anchor="w", pady=5)
        ttk.Checkbutton(f_active, text="5. " + self.app.t("video"), variable=self.app.var_run_video).pack(anchor="w", pady=5)
        
        ttk.Checkbutton(f_active, text="6. " + self.app.t("compilation"), variable=self.app.var_run_compilation).pack(anchor="w", pady=5)
        
        ttk.Label(f_active, text=self.app.t("note_changes"), font=("Helvetica", 9, "italic"), foreground="gray").pack(pady=20)

        # 2. Gemini Generation Logic
        f_gemini = ttk.LabelFrame(scroll_frame, text=self.app.t("gemini_logic"), padding=10)
        f_gemini.pack(fill="x", padx=10, pady=5)
        
        self.var_lyrics = tk.BooleanVar(value=config.get("gemini_lyrics", True))
        ttk.Checkbutton(f_gemini, text=self.app.t("gen_lyrics_vs_title"), variable=self.var_lyrics).pack(anchor="w")
        self.var_style = tk.BooleanVar(value=config.get("gemini_style", True))
        ttk.Checkbutton(f_gemini, text=self.app.t("gen_music_style"), variable=self.var_style).pack(anchor="w")
        self.var_visual = tk.BooleanVar(value=config.get("gemini_visual", True))
        ttk.Checkbutton(f_gemini, text=self.app.t("gen_visual_prompts"), variable=self.var_visual).pack(anchor="w")
        self.var_video = tk.BooleanVar(value=config.get("gemini_video", False))
        ttk.Checkbutton(f_gemini, text=self.app.t("gen_video_prompts"), variable=self.var_video).pack(anchor="w")
        
        # 3. Automation Delays
        f_suno = ttk.LabelFrame(scroll_frame, text=self.app.t("automation_delays"), padding=10)
        f_suno.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(f_suno, text=self.app.t("suno_delay_label")).pack(anchor="w")
        self.entry_delay = ttk.Entry(f_suno)
        self.entry_delay.insert(0, str(config.get("suno_delay", 15)))
        self.entry_delay.pack(fill="x", pady=2)
        
        ttk.Label(f_suno, text=self.app.t("startup_delay_label")).pack(anchor="w")
        self.entry_startup = ttk.Entry(f_suno)
        self.entry_startup.insert(0, str(config.get("startup_delay", 5)))
        self.entry_startup.pack(fill="x", pady=2)
        
        # 4. Language
        f_lang = ttk.LabelFrame(scroll_frame, text=self.app.t("lang_reg"), padding=10)
        f_lang.pack(fill="x", padx=10, pady=5)
        ttk.Label(f_lang, text=self.app.t("target_lang_label")).pack(anchor="w")
        self.combo_lang = ttk.Combobox(f_lang, values=["Turkish", "English", "German", "French", "Spanish", "Italian", "Portuguese"], state="readonly")
        self.combo_lang.set(config.get("target_language", "Turkish"))
        self.combo_lang.pack(fill="x", pady=2)

        # UI Language
        f_ui_lang = ttk.LabelFrame(scroll_frame, text=self.app.t("ui_language"), padding=10)
        f_ui_lang.pack(fill="x", padx=10, pady=5)
        
        self.combo_ui_lang = ttk.Combobox(f_ui_lang, values=["Turkish", "English"], state="readonly")
        self.combo_ui_lang.set(config.get("ui_language", "Turkish"))
        self.combo_ui_lang.pack(fill="x", pady=2)

        # Activity Log Startup State
        f_startup_opts = ttk.LabelFrame(scroll_frame, text=self.app.t("startup_opts_label"), padding=10)
        f_startup_opts.pack(fill="x", padx=10, pady=5)
        self.var_log_at_start = tk.BooleanVar(value=config.get("log_open_at_start", False))
        ttk.Checkbutton(f_startup_opts, text=self.app.t("log_startup"), variable=self.var_log_at_start).pack(anchor="w")

        # 5. Browser Operations
        f_browser = ttk.LabelFrame(scroll_frame, text=self.app.t("browser_action_label"), padding=10)
        f_browser.pack(fill="x", padx=10, pady=5)
        
        btn_grid = ttk.Frame(f_browser)
        btn_grid.pack(fill="x")
        
        ttk.Button(btn_grid, text=self.app.t("open_chrome_btn"), command=self.open_chrome, style="Action.TButton").pack(side="left", fill="x", expand=True, padx=2, pady=5)
        ttk.Button(btn_grid, text=self.app.t("reset_chrome_btn"), command=self.reset_chrome).pack(side="left", fill="x", expand=True, padx=2, pady=5)

        # --- TAB 1.5: Suno Adv ---
        self.tab_adv_suno = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_adv_suno, text=self.app.t("suno_adv_tab"))
        
        f_adv_suno = ttk.LabelFrame(self.tab_adv_suno, text=self.app.t("suno_adv_params"), padding=10)
        f_adv_suno.pack(fill="both", expand=True, padx=10, pady=10)


        # Persona Profile Section
        self.var_persona_link_enabled = tk.BooleanVar(value=config.get("suno_persona_link_enabled", False))
        ttk.Checkbutton(f_adv_suno, text=self.app.t("enable_persona_label"), variable=self.var_persona_link_enabled).grid(row=0, column=0, sticky="w", pady=2)
        
        # Frame for Persona Manager
        f_persona_mgr = ttk.Frame(f_adv_suno)
        f_persona_mgr.grid(row=0, column=1, sticky="ew", pady=2)
        
        # Load Personas
        self.personas = config.get("suno_personas", {}) # Dict: {Alias: Link}
        self.active_persona_alias = config.get("suno_active_persona", "")
        
        # Combobox for Selection
        self.combo_persona_select = ttk.Combobox(f_persona_mgr, values=list(self.personas.keys()), state="readonly")
        self.combo_persona_select.pack(side="top", fill="x", pady=(0, 2))
        if self.active_persona_alias in self.personas:
            self.combo_persona_select.set(self.active_persona_alias)
        
        # Profile Management Area
        f_pm_controls = ttk.Frame(f_persona_mgr)
        f_pm_controls.pack(side="top", fill="x")
        
        ttk.Label(f_pm_controls, text=self.app.t("alias_label")).pack(side="left")
        self.ent_pm_alias = ttk.Entry(f_pm_controls, width=10)
        self.ent_pm_alias.pack(side="left", padx=2)
        
        ttk.Label(f_pm_controls, text=self.app.t("link_label")).pack(side="left")
        self.ent_pm_link = ttk.Entry(f_pm_controls, width=30) # Increased width
        self.ent_pm_link.pack(side="left", padx=2, fill="x", expand=True)
        
        ttk.Button(f_pm_controls, text="+", width=3, command=self.add_persona).pack(side="left", padx=2)
        ttk.Button(f_pm_controls, text="-", width=3, command=self.delete_persona).pack(side="left", padx=2)
        ttk.Button(f_pm_controls, text="✎", width=3, command=self.edit_persona).pack(side="left", padx=2)
        ttk.Button(f_pm_controls, text="🧪", width=3, command=self.test_persona_link).pack(side="left", padx=2)

        # 2. Vocal Gender
        self.var_gender_enabled = tk.BooleanVar(value=config.get("vocal_gender_enabled", False))
        ttk.Checkbutton(f_adv_suno, text=self.app.t("enable_vocal_gender_label"), variable=self.var_gender_enabled).grid(row=1, column=0, sticky="w", pady=2)
        self.combo_gender = ttk.Combobox(f_adv_suno, values=[self.app.t("vocal_default"), self.app.t("vocal_none"), self.app.t("vocal_male"), self.app.t("vocal_female")], state="readonly")
        self.combo_gender.set(config.get("vocal_gender", self.app.t("vocal_default")))
        self.combo_gender.grid(row=1, column=1, sticky="ew", pady=2)

        # 3. Audio Influence (%)
        self.var_audio_enabled = tk.BooleanVar(value=config.get("audio_influence_enabled", False))
        ttk.Checkbutton(f_adv_suno, text=self.app.t("enable_audio_influence_label"), variable=self.var_audio_enabled).grid(row=2, column=0, sticky="w", pady=2)
        self.scale_audio = tk.Scale(f_adv_suno, from_=10, to_=90, orient="horizontal")
        self.scale_audio.set(config.get("audio_influence", 25))
        self.scale_audio.grid(row=2, column=1, sticky="ew", pady=2)

        # 4. Weirdness
        self.var_weird_enabled = tk.BooleanVar(value=config.get("weirdness_enabled", False))
        ttk.Checkbutton(f_adv_suno, text=self.app.t("enable_weirdness_label"), variable=self.var_weird_enabled).grid(row=3, column=0, sticky="w", pady=2)
        self.scale_weird = tk.Scale(f_adv_suno, from_=1, to_=100, orient="horizontal")
        self.scale_weird.set(50 if config.get("weirdness") == "Default" else int(config.get("weirdness", 50)))
        self.scale_weird.grid(row=3, column=1, sticky="ew", pady=2)

        # 5. Style Influence
        self.var_style_enabled = tk.BooleanVar(value=config.get("style_influence_enabled", False))
        ttk.Checkbutton(f_adv_suno, text=self.app.t("enable_style_influence_label"), variable=self.var_style_enabled).grid(row=4, column=0, sticky="w", pady=2)
        self.scale_style = tk.Scale(f_adv_suno, from_=1, to_=100, orient="horizontal")
        self.scale_style.set(50 if config.get("style_influence") == "Default" else int(config.get("style_influence", 50)))
        self.scale_style.grid(row=4, column=1, sticky="ew", pady=2)

        # 6. Lyrics Mode
        self.var_lyrics_mode_enabled = tk.BooleanVar(value=config.get("lyrics_mode_enabled", False))
        ttk.Checkbutton(f_adv_suno, text=self.app.t("enable_lyrics_mode_label"), variable=self.var_lyrics_mode_enabled).grid(row=5, column=0, sticky="w", pady=2)
        self.combo_lyrics_mode = ttk.Combobox(f_adv_suno, values=[self.app.t("vocal_default"), self.app.t("mode_manual"), self.app.t("mode_auto")], state="readonly")
        self.combo_lyrics_mode.set(config.get("lyrics_mode", self.app.t("vocal_default")))
        self.combo_lyrics_mode.grid(row=5, column=1, sticky="ew", pady=2)

        f_adv_suno.columnconfigure(1, weight=1)

        # --- TAB 2: Humanizer ---
        self.tab_humanizer = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_humanizer, text=self.app.t("humanizer"))
        
        f_human = ttk.LabelFrame(self.tab_humanizer, text=self.app.t("human_settings_label"), padding=10)
        f_human.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 1. Main Toggle
        self.var_humanizer_enabled = tk.BooleanVar(value=config.get("humanizer_enabled", True))
        ttk.Checkbutton(f_human, text=self.app.t("enable_humanizer_label"), variable=self.var_humanizer_enabled).grid(row=0, column=0, columnspan=2, sticky="w", pady=10)

        # 2. Phase-specific activity
        ttk.Label(f_human, text=self.app.t("activate_humanizer_label")).grid(row=1, column=0, sticky="w", pady=5)
        self.var_h_gemini = tk.BooleanVar(value=config.get("h_activate_gemini", True))
        ttk.Checkbutton(f_human, text=self.app.t("phase1_label"), variable=self.var_h_gemini).grid(row=2, column=0, sticky="w")
        self.var_h_suno = tk.BooleanVar(value=config.get("h_activate_suno", True))
        ttk.Checkbutton(f_human, text=self.app.t("phase2_label"), variable=self.var_h_suno).grid(row=2, column=1, sticky="w")
        self.var_h_video = tk.BooleanVar(value=config.get("h_activate_video", False))
        ttk.Checkbutton(f_human, text=self.app.t("phase3_label"), variable=self.var_h_video).grid(row=2, column=2, sticky="w")

        # 3. Levels and Speed
        ttk.Label(f_human, text=self.app.t("human_level_label")).grid(row=3, column=0, sticky="w", pady=5)
        self.combo_human_level = ttk.Combobox(f_human, values=[self.app.t("level_low"), self.app.t("level_medium"), self.app.t("level_high")], state="readonly")
        self.combo_human_level.set(config.get("humanizer_level", self.app.t("level_medium")))
        self.combo_human_level.grid(row=3, column=1, sticky="w", pady=5)
        
        ttk.Label(f_human, text=self.app.t("typing_speed_label")).grid(row=4, column=0, sticky="w", pady=5)
        self.scale_speed = tk.Scale(f_human, from_=0.05, to_=2.5, resolution=0.05, orient="horizontal")
        self.scale_speed.set(config.get("humanizer_speed", 1.0))
        self.scale_speed.grid(row=4, column=1, sticky="ew", pady=5)
        ttk.Label(f_human, text=self.app.t("speed_hint"), foreground="gray").grid(row=5, column=1, sticky="w")
        
        ttk.Label(f_human, text=self.app.t("max_retries_label")).grid(row=6, column=0, sticky="w", pady=5)
        self.spin_retries = tk.Spinbox(f_human, from_=0, to_=3, width=5)
        self.spin_retries.delete(0, tk.END)
        self.spin_retries.insert(0, str(config.get("humanizer_retries", 1)))
        self.spin_retries.grid(row=6, column=1, sticky="w", pady=5)
        
        self.var_adaptive = tk.BooleanVar(value=config.get("humanizer_adaptive", True))
        ttk.Checkbutton(f_human, text=self.app.t("enable_adaptive_label"), variable=self.var_adaptive).grid(row=7, column=0, columnspan=2, sticky="w", pady=5)
        
        f_human.columnconfigure(1, weight=1)

        # --- TAB 3: Video ---
        self.tab_video = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_video, text=self.app.t("video")) # Use t("video") for localization
        
        # Scrollable area for Video Tab (to match others)
        v_canvas = tk.Canvas(self.tab_video, borderwidth=0, highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(self.tab_video, orient="vertical", command=v_canvas.yview)
        v_scroll_frame = ttk.Frame(v_canvas)
        v_scroll_frame.bind("<Configure>", lambda e: v_canvas.configure(scrollregion=v_canvas.bbox("all")))
        v_canvas.create_window((0, 0), window=v_scroll_frame, anchor="nw")
        v_canvas.configure(yscrollcommand=v_scrollbar.set)
        v_canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")

        # 1. Visual Effects (Multi-Select)
        f_v_effects = ttk.LabelFrame(v_scroll_frame, text=self.app.t("video_effect_label"), padding=10)
        f_v_effects.pack(fill="x", padx=10, pady=5)
        
        self.effect_vars = {}
        effects = ["Snow", "Rain", "Particles", "Glitch", "Ken Burns", "Vignette"]
        saved_effects = config.get("video_effects", [config.get("video_effect", "None")])
        
        for i, eff in enumerate(effects):
            var = tk.BooleanVar(value=eff in saved_effects)
            self.effect_vars[eff] = var
            cb = ttk.Checkbutton(f_v_effects, text=self.app.t(eff.lower().replace(" ", "_")), variable=var)
            cb.grid(row=i//3, column=i%3, sticky="w", padx=10, pady=2)

        # 2. Quality & Performance Settings
        f_v_quality = ttk.LabelFrame(v_scroll_frame, text=self.app.t("video_quality_label"), padding=10)
        f_v_quality.pack(fill="x", padx=10, pady=5)
        
        # Parallel Render Count (NEW)
        ttk.Label(f_v_quality, text=self.app.t("video_parallel_label")).grid(row=0, column=0, sticky="w", pady=5)
        self.combo_parallel_render = ttk.Combobox(f_v_quality, values=["1", "2", "4", "6", "8"], state="readonly", width=5)
        self.combo_parallel_render.set(str(config.get("video_parallel_count", 1)))
        self.combo_parallel_render.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Video Selection Mode (NEW)
        ttk.Label(f_v_quality, text=self.app.t("video_selection_label")).grid(row=1, column=0, sticky="w", pady=5)
        self.combo_video_selection = ttk.Combobox(f_v_quality, values=[self.app.t("v_mode_1"), self.app.t("v_mode_2"), self.app.t("v_mode_both")], state="readonly")
        self.combo_video_selection.set(config.get("video_selection_mode", self.app.t("v_mode_both")))
        self.combo_video_selection.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # FPS
        ttk.Label(f_v_quality, text=self.app.t("video_fps_label")).grid(row=2, column=0, sticky="w", pady=5)
        self.spin_fps = tk.Spinbox(f_v_quality, from_=1, to_=60, width=5)
        self.spin_fps.delete(0, tk.END)
        self.spin_fps.insert(0, str(config.get("video_fps", 30)))
        self.spin_fps.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Resolution
        ttk.Label(f_v_quality, text=self.app.t("video_res_label")).grid(row=3, column=0, sticky="w", pady=5)
        self.combo_res = ttk.Combobox(f_v_quality, values=[self.app.t("video_res_shorts"), self.app.t("video_res_hd"), self.app.t("video_res_sd")], state="readonly")
        self.combo_res.set(config.get("video_resolution", self.app.t("video_res_shorts")))
        self.combo_res.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        # Intensity
        ttk.Label(f_v_quality, text=self.app.t("video_intensity_label")).grid(row=4, column=0, sticky="w", pady=5)
        self.scale_intensity = tk.Scale(f_v_quality, from_=0.1, to_=2.0, resolution=0.1, orient="horizontal")
        self.scale_intensity.set(config.get("video_intensity", 1.0))
        self.scale_intensity.grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        # 3. Assets & Output
        f_v_assets = ttk.LabelFrame(v_scroll_frame, text=self.app.t("video_assets_output_label"), padding=10)
        f_v_assets.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(f_v_assets, text=self.app.t("video_assets_label")).pack(anchor="w")
        f_path = ttk.Frame(f_v_assets)
        f_path.pack(fill="x", pady=2)
        self.ent_video_assets = ttk.Entry(f_path)
        self.ent_video_assets.insert(0, config.get("video_assets_path", ""))
        self.ent_video_assets.pack(side="left", fill="x", expand=True)
        ttk.Button(f_path, text="...", width=3, command=lambda: self.browse_folder(self.ent_video_assets)).pack(side="left", padx=2)
        ttk.Label(f_v_assets, text=self.app.t("video_assets_hint"), font=("Helvetica", 8, "italic"), foreground="gray").pack(anchor="w")

        ttk.Label(f_v_assets, text=self.app.t("video_output_mode_label")).pack(anchor="w", pady=(10,0))
        ttk.Radiobutton(f_v_assets, text=self.app.t("video_output_same_label"), variable=self.var_video_output_mode, value="profile").pack(anchor="w")
        ttk.Radiobutton(f_v_assets, text=self.app.t("video_output_custom_label"), variable=self.var_video_output_mode, value="custom").pack(anchor="w")
        
        f_custom_path = ttk.Frame(f_v_assets)
        f_custom_path.pack(fill="x", pady=2)
        self.ent_video_custom_path = ttk.Entry(f_custom_path)
        self.ent_video_custom_path.insert(0, config.get("video_custom_output_path", ""))
        self.ent_video_custom_path.pack(side="left", fill="x", expand=True)
        ttk.Button(f_custom_path, text="...", width=3, command=lambda: self.browse_folder(self.ent_video_custom_path)).pack(side="left", padx=2)

        # --- TAB 3: Prompts ---
        self.tab_prompts = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_prompts, text=self.app.t("prompts"))
        
        # Scrollable area for Prompts Tab
        p_canvas = tk.Canvas(self.tab_prompts, borderwidth=0, highlightthickness=0)
        p_scrollbar = ttk.Scrollbar(self.tab_prompts, orient="vertical", command=p_canvas.yview)
        p_scroll_frame = ttk.Frame(p_canvas)
        
        p_scroll_frame.bind(
            "<Configure>",
            lambda e: p_canvas.configure(scrollregion=p_canvas.bbox("all"))
        )
        p_canvas.create_window((0, 0), window=p_scroll_frame, anchor="nw")
        p_canvas.configure(yscrollcommand=p_scrollbar.set)
        
        p_canvas.pack(side="left", fill="both", expand=True)
        p_scrollbar.pack(side="right", fill="y")
        
        # Lyrics
        ttk.Label(p_scroll_frame, text=self.app.t("lyrics_master_label"), font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.txt_lyrics = scrolledtext.ScrolledText(p_scroll_frame, height=8, wrap=tk.WORD, font=("Consolas", 10))
        self.txt_lyrics.pack(fill="x", padx=10, pady=5)
        
        # Visual
        ttk.Label(p_scroll_frame, text=self.app.t("visual_master_label"), font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.txt_visual = scrolledtext.ScrolledText(p_scroll_frame, height=8, wrap=tk.WORD, font=("Consolas", 10))
        self.txt_visual.pack(fill="x", padx=10, pady=5)
        
        # Video
        ttk.Label(p_scroll_frame, text=self.app.t("video_master_label"), font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.txt_video = scrolledtext.ScrolledText(p_scroll_frame, height=8, wrap=tk.WORD, font=("Consolas", 10))
        self.txt_video.pack(fill="x", padx=10, pady=5)
        
        # Art (Thumbnail)
        ttk.Label(p_scroll_frame, text=self.app.t("art_master_label"), font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.txt_art = scrolledtext.ScrolledText(p_scroll_frame, height=8, wrap=tk.WORD, font=("Consolas", 10))
        self.txt_art.pack(fill="x", padx=10, pady=5)
        
        self.load_prompts_data()

        # --- TAB: Activity Log (MOVED TO END) ---
        self.tab_logs = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_logs, text=self.app.t("log"))
        
        self.log_disp = scrolledtext.ScrolledText(self.tab_logs, state='disabled', font=("Consolas", 9), bg="#ffffff", fg="#1e1e1e")
        self.log_disp.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Live Logger handler for Settings window
        self.settings_handler = GuiLogger(self.log_disp)
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')
        self.settings_handler.setFormatter(formatter)
        logging.getLogger().addHandler(self.settings_handler)
        
        # Populate with current logs from main app
        if hasattr(self.app, "log_text"):
            self.log_disp.configure(state='normal')
            logs = self.app.log_text.get("1.0", tk.END).strip()
            self.log_disp.insert("1.0", logs + "\n--- Settings Window Log Start ---\n")
            self.log_disp.configure(state='disabled')
            self.log_disp.yview(tk.END)

        # Save Button (Locked at bottom via Grid Row 1)
        # NOW PACKED AT TOP OF INIT
        
        # Initialize with current active profile (Ref 2)
        initial_p = config.get("active_preset")
        if initial_p and initial_p in self.presets:
            self.combo_preset_select.set(initial_p)
            self.load_preset()
        
        # Cleanup handler on close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        logging.getLogger().removeHandler(self.settings_handler)
        self.destroy()

    # --- Preset Methods ---
    def save_preset(self, silent=False):
        alias = self.ent_preset_alias.get().strip()
        if not alias:
            # If silent, we don't warn, we just skip saving preset
            if not silent:
                messagebox.showwarning(self.app.t("warning"), self.app.t("msg_enter_preset_alias"))
            return
        
        # Capture current prompts
        prompts = {
            "lyrics_master_prompt": self.txt_lyrics.get("1.0", tk.END).strip() if self.txt_lyrics else "",
            "visual_master_prompt": self.txt_visual.get("1.0", tk.END).strip() if self.txt_visual else "",
            "video_master_prompt": self.txt_video.get("1.0", tk.END).strip() if self.txt_video else "",
            "art_master_prompt": self.txt_art.get("1.0", tk.END).strip() if self.txt_art else ""
        }
        
        # Capture all configurable settings
        settings_snapshot = {}
        
        if self.var_lyrics: settings_snapshot["gemini_lyrics"] = self.var_lyrics.get()
        if self.var_style: settings_snapshot["gemini_style"] = self.var_style.get()
        if self.var_visual: settings_snapshot["gemini_visual"] = self.var_visual.get()
        if self.var_video: settings_snapshot["gemini_video"] = self.var_video.get()
        if self.entry_delay: settings_snapshot["suno_delay"] = self.entry_delay.get()
        if self.entry_startup: settings_snapshot["startup_delay"] = self.entry_startup.get()
        if self.combo_lang: settings_snapshot["target_language"] = self.combo_lang.get()
        if self.ent_artist_name: settings_snapshot["artist_name"] = self.ent_artist_name.get()
        if self.ent_artist_style: settings_snapshot["artist_style"] = self.ent_artist_style.get()
        if self.combo_gender: settings_snapshot["vocal_gender"] = self.combo_gender.get()
        if self.var_gender_enabled: settings_snapshot["vocal_gender_enabled"] = self.var_gender_enabled.get()
        if self.scale_audio: settings_snapshot["audio_influence"] = self.scale_audio.get()
        if self.var_audio_enabled: settings_snapshot["audio_influence_enabled"] = self.var_audio_enabled.get()
        if self.scale_weird: settings_snapshot["weirdness"] = self.scale_weird.get()
        if self.var_weird_enabled: settings_snapshot["weirdness_enabled"] = self.var_weird_enabled.get()
        if self.scale_style: settings_snapshot["style_influence"] = self.scale_style.get()
        if self.var_style_enabled: settings_snapshot["style_influence_enabled"] = self.var_style_enabled.get()
        if self.combo_lyrics_mode: settings_snapshot["lyrics_mode"] = self.combo_lyrics_mode.get()
        if self.var_lyrics_mode_enabled: settings_snapshot["lyrics_mode_enabled"] = self.var_lyrics_mode_enabled.get()
        if self.var_persona_link_enabled: settings_snapshot["suno_persona_link_enabled"] = self.var_persona_link_enabled.get()
        if self.combo_persona_select: settings_snapshot["suno_active_persona"] = self.combo_persona_select.get()
        
        # Defaults
        if self.var_def_lyrics: settings_snapshot["default_run_lyrics"] = self.var_def_lyrics.get()
        if self.var_def_music: settings_snapshot["default_run_music"] = self.var_def_music.get()
        if self.var_def_art_p: settings_snapshot["default_run_art_prompt"] = self.var_def_art_p.get()
        if self.var_def_art_i: settings_snapshot["default_run_art_image"] = self.var_def_art_i.get()
        if self.var_def_video: settings_snapshot["default_run_video"] = self.var_def_video.get()
        if self.var_def_compilation: settings_snapshot["default_run_compilation"] = self.var_def_compilation.get()

        # Video
        if self.effect_vars: settings_snapshot["video_effects"] = [eff for eff, var in self.effect_vars.items() if var and var.get()]
        if self.spin_fps: settings_snapshot["video_fps"] = int(self.spin_fps.get())
        if self.combo_res: settings_snapshot["video_resolution"] = self.combo_res.get()
        if self.scale_intensity: settings_snapshot["video_intensity"] = self.scale_intensity.get()
        if self.ent_video_assets: settings_snapshot["video_assets_path"] = self.ent_video_assets.get()
        if self.var_video_output_mode: settings_snapshot["video_output_mode"] = self.var_video_output_mode.get()
        if self.ent_video_custom_path: settings_snapshot["video_custom_output_path"] = self.ent_video_custom_path.get()
        if self.combo_parallel_render: settings_snapshot["video_parallel_count"] = int(self.combo_parallel_render.get())
        if self.combo_video_selection: settings_snapshot["video_selection_mode"] = self.combo_video_selection.get()
        
        # Humanizer
        if self.var_humanizer_enabled: settings_snapshot["humanizer_enabled"] = self.var_humanizer_enabled.get()
        if self.var_h_gemini: settings_snapshot["h_activate_gemini"] = self.var_h_gemini.get()
        if self.var_h_suno: settings_snapshot["h_activate_suno"] = self.var_h_suno.get()
        if self.var_h_video: settings_snapshot["h_activate_video"] = self.var_h_video.get()
        if self.combo_human_level: settings_snapshot["humanizer_level"] = self.combo_human_level.get()
        if self.scale_speed: settings_snapshot["humanizer_speed"] = self.scale_speed.get()
        if self.spin_retries: settings_snapshot["humanizer_retries"] = int(self.spin_retries.get())
        if self.var_adaptive: settings_snapshot["humanizer_adaptive"] = self.var_adaptive.get()
        
        self.presets[alias] = {
            "settings": settings_snapshot,
            "prompts": prompts
        }
        self.update_preset_combo()
        self.combo_preset_select.set(alias)
        if not silent:
            messagebox.showinfo(self.app.t("success"), self.app.t("msg_preset_saved").format(alias=alias))

    def load_preset(self, silent=True):
        alias = self.combo_preset_select.get()
        if not alias or alias not in self.presets:
            return
        
        # Mark as active immediately (User requirement)
        self.config["active_preset"] = alias
        
        data = self.presets[alias]
        settings = data.get("settings", {})
        prompts = data.get("prompts", {})
        
        # Apply settings to UI
        if self.var_lyrics: self.var_lyrics.set(settings.get("gemini_lyrics", True))
        if self.var_style: self.var_style.set(settings.get("gemini_style", True))
        if self.var_visual: self.var_visual.set(settings.get("gemini_visual", True))
        if self.var_video: self.var_video.set(settings.get("gemini_video", False))
        
        if self.entry_delay:
            self.entry_delay.delete(0, tk.END)
            self.entry_delay.insert(0, settings.get("suno_delay", "15"))
        if self.entry_startup:
            self.entry_startup.delete(0, tk.END)
            self.entry_startup.insert(0, settings.get("startup_delay", "5"))
        if self.combo_lang: self.combo_lang.set(settings.get("target_language", "Turkish"))
        
        if self.ent_artist_name:
            self.ent_artist_name.delete(0, tk.END)
            self.ent_artist_name.insert(0, settings.get("artist_name", ""))
        if self.ent_artist_style:
            self.ent_artist_style.delete(0, tk.END)
            self.ent_artist_style.insert(0, settings.get("artist_style", ""))
        
        if self.combo_gender: self.combo_gender.set(settings.get("vocal_gender", "Default"))
        if self.var_gender_enabled: self.var_gender_enabled.set(settings.get("vocal_gender_enabled", False))
        if self.scale_audio: self.scale_audio.set(int(settings.get("audio_influence", 25)))
        if self.var_audio_enabled: self.var_audio_enabled.set(settings.get("audio_influence_enabled", False))
        if self.scale_weird: self.scale_weird.set(int(settings.get("weirdness", 50)))
        if self.var_weird_enabled: self.var_weird_enabled.set(settings.get("weirdness_enabled", False))
        if self.scale_style: self.scale_style.set(int(settings.get("style_influence", 50)))
        if self.var_style_enabled: self.var_style_enabled.set(settings.get("style_influence_enabled", False))
        if self.combo_lyrics_mode: self.combo_lyrics_mode.set(settings.get("lyrics_mode", "Default"))
        if self.var_lyrics_mode_enabled: self.var_lyrics_mode_enabled.set(settings.get("lyrics_mode_enabled", False))
        
        if self.combo_persona_select: self.combo_persona_select.set(settings.get("suno_active_persona", ""))
        
        if self.var_suno_batch: self.var_suno_batch.set(settings.get("suno_batch_mode", False))
        if self.var_batch_op: self.var_batch_op.set(settings.get("suno_batch_op_mode", "full"))

        # Defaults
        if self.var_def_lyrics: self.var_def_lyrics.set(settings.get("default_run_lyrics", True))
        if self.var_def_music: self.var_def_music.set(settings.get("default_run_music", True))
        if self.var_def_art_p: self.var_def_art_p.set(settings.get("default_run_art_prompt", True))
        if self.var_def_art_i: self.var_def_art_i.set(settings.get("default_run_art_image", True))
        if self.var_def_video: self.var_def_video.set(settings.get("default_run_video", False))
        if self.var_def_compilation: self.var_def_compilation.set(settings.get("default_run_compilation", True))
        
        # Apply Video Settings to UI
        target_effects = settings.get("video_effects", [settings.get("video_effect", "None")])
        if self.effect_vars:
            for eff, var in self.effect_vars.items():
                if var: var.set(eff in target_effects)
            
        if self.spin_fps:
            self.spin_fps.delete(0, tk.END)
            self.spin_fps.insert(0, str(settings.get("video_fps", 30)))
        if self.combo_res: self.combo_res.set(settings.get("video_resolution", self.app.t("video_res_shorts")))
        if self.scale_intensity: self.scale_intensity.set(float(settings.get("video_intensity", 1.0)))
        if self.ent_video_assets:
            self.ent_video_assets.delete(0, tk.END)
            self.ent_video_assets.insert(0, settings.get("video_assets_path", ""))
        if self.var_video_output_mode: self.var_video_output_mode.set(settings.get("video_output_mode", "profile"))
        if self.ent_video_custom_path:
            self.ent_video_custom_path.delete(0, tk.END)
            self.ent_video_custom_path.insert(0, settings.get("video_custom_output_path", ""))
        if self.combo_parallel_render: self.combo_parallel_render.set(str(settings.get("video_parallel_count", 1)))
        if self.combo_video_selection: self.combo_video_selection.set(settings.get("video_selection_mode", self.app.t("v_mode_both")))
        
        # Humanizer
        if self.var_humanizer_enabled: self.var_humanizer_enabled.set(settings.get("humanizer_enabled", True))
        if self.var_h_gemini: self.var_h_gemini.set(settings.get("h_activate_gemini", True))
        if self.var_h_suno: self.var_h_suno.set(settings.get("h_activate_suno", True))
        if self.var_h_video: self.var_h_video.set(settings.get("h_activate_video", False))
        if self.combo_human_level: self.combo_human_level.set(settings.get("humanizer_level", self.app.t("level_medium")))
        if self.scale_speed: self.scale_speed.set(float(settings.get("humanizer_speed", 1.0)))
        if self.spin_retries:
            self.spin_retries.delete(0, tk.END)
            self.spin_retries.insert(0, str(settings.get("humanizer_retries", 1)))
        if self.var_adaptive: self.var_adaptive.set(settings.get("humanizer_adaptive", True))
        
        # Apply prompts to UI
        if self.txt_lyrics:
            self.txt_lyrics.delete("1.0", tk.END)
            self.txt_lyrics.insert("1.0", prompts.get("lyrics_master_prompt", ""))
        if self.txt_visual:
            self.txt_visual.delete("1.0", tk.END)
            self.txt_visual.insert("1.0", prompts.get("visual_master_prompt", ""))
        if self.txt_video:
            self.txt_video.delete("1.0", tk.END)
            self.txt_video.insert("1.0", prompts.get("video_master_prompt", ""))
        if self.txt_art:
            self.txt_art.delete("1.0", tk.END)
            self.txt_art.insert("1.0", prompts.get("art_master_prompt", ""))
        
        # Apply Alias to Entry (Crucial for user feedback)
        self.ent_preset_alias.delete(0, tk.END)
        self.ent_preset_alias.insert(0, str(alias))
        
        # Select in combobox to stay in sync if called externally
        if self.combo_preset_select.get() != alias:
            self.combo_preset_select.set(alias)
            
        # Refresh UI state
        self.update_idletasks()

    def clear_preset_form(self):
        """Clears the form to allow adding a new profile easily."""
        self.combo_preset_select.set('')
        self.ent_preset_alias.delete(0, tk.END)
        self.ent_artist_name.delete(0, tk.END)
        self.ent_artist_style.delete(0, tk.END)
        # We don't clear master prompts to allow users to use current ones as base
        messagebox.showinfo(self.app.t("info"), self.app.t("msg_enter_preset_alias"))

    def delete_preset(self):
        alias = self.combo_preset_select.get()
        if alias and alias in self.presets:
            if messagebox.askyesno(self.app.t("confirm"), self.app.t("msg_confirm_delete_preset").format(alias=alias)):
                del self.presets[alias]
                self.update_preset_combo()
                self.combo_preset_select.set('')
                self.ent_preset_alias.delete(0, tk.END)

    def update_preset_combo(self):
        self.combo_preset_select['values'] = list(self.presets.keys())

    def load_prompts_data(self):
        import json
        if os.path.exists(self.prompts_path):
            try:
                with open(self.prompts_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.txt_lyrics.insert("1.0", data.get("lyrics_master_prompt", ""))
                    self.txt_visual.insert("1.0", data.get("visual_master_prompt", ""))
                    self.txt_video.insert("1.0", data.get("video_master_prompt", ""))
                    self.txt_art.insert("1.0", data.get("art_master_prompt", ""))
            except Exception as e:
                logger.error(f"Failed to load prompts data: {e}")

    def add_persona(self):
        alias = self.ent_pm_alias.get().strip()
        link = self.ent_pm_link.get().strip()
        if alias and link:
            self.personas[alias] = link
            self.update_persona_combo()
            self.combo_persona_select.set(alias)
            self.ent_pm_alias.delete(0, tk.END)
            self.ent_pm_link.delete(0, tk.END)

    def delete_persona(self):
        selection = self.combo_persona_select.get()
        if selection and selection in self.personas:
            del self.personas[selection]
            self.update_persona_combo()
            self.combo_persona_select.set('')

    def edit_persona(self):
        selection = self.combo_persona_select.get()
        if selection and selection in self.personas:
            link = self.personas[selection]
            # Load into entry fields
            self.ent_pm_alias.delete(0, tk.END)
            self.ent_pm_alias.insert(0, selection)
            self.ent_pm_link.delete(0, tk.END)
            self.ent_pm_link.insert(0, link)
            messagebox.showinfo("Bilgi", f"'{selection}' düzenleme için yüklendi.\nDeğişiklik yapıp '+' butonuna basın.")

    def test_persona_link(self):
        """Opens the entered link in system default browser to check for 404s."""
        link = self.ent_pm_link.get().strip()
        if not link:
            # If entry empty, try selected item
            selection = self.combo_persona_select.get()
            if selection and selection in self.personas:
                link = self.personas[selection]
        
        if link:
            import webbrowser
            webbrowser.open(link)
        else:
            messagebox.showwarning(self.app.t("warning"), "Lütfen test edilecek bir link girin veya listeden seçin.")

    def update_persona_combo(self):
        self.combo_persona_select['values'] = list(self.personas.keys())

    def open_chrome(self):
        self.app.open_chrome_profile()

    def reset_chrome(self):
        if messagebox.askyesno(self.app.t("confirm"), self.app.t("msg_confirm_reset_chrome")):
            self.app.reset_chrome_profile()

    def browse_folder(self, target_entry):
        folder = filedialog.askdirectory(title=self.app.t("msg_select_folder"))
        if folder:
            target_entry.delete(0, tk.END)
            target_entry.insert(0, folder)

    def save_settings(self):
        try:
            # 0. Automatically update active profile first (Ref 7) - SILENTLY
            self.save_preset(silent=True)
            self.config["artist_presets"] = self.presets
            
            # 1. Config Object Update
            if self.var_lyrics: self.config["gemini_lyrics"] = self.var_lyrics.get()
            if self.var_style: self.config["gemini_style"] = self.var_style.get()
            if self.var_visual: self.config["gemini_visual"] = self.var_visual.get()
            if self.var_video: self.config["gemini_video"] = self.var_video.get()
            
            if self.entry_delay: self.config["suno_delay"] = int(self.entry_delay.get())
            if self.entry_startup: self.config["startup_delay"] = int(self.entry_startup.get())
            if self.combo_lang: self.config["target_language"] = self.combo_lang.get()
            if self.combo_ui_lang: self.config["ui_language"] = self.combo_ui_lang.get()
            if self.var_log_at_start: self.config["log_open_at_start"] = self.var_log_at_start.get()
            
            if self.ent_artist_name: self.config["artist_name"] = self.ent_artist_name.get()
            if self.ent_artist_style: self.config["artist_style"] = self.ent_artist_style.get()
            
            # Humanizer Configs
            if self.var_humanizer_enabled: self.config["humanizer_enabled"] = self.var_humanizer_enabled.get()
            if self.var_h_gemini: self.config["h_activate_gemini"] = self.var_h_gemini.get()
            if self.var_h_suno: self.config["h_activate_suno"] = self.var_h_suno.get()
            if self.var_h_video: self.config["h_activate_video"] = self.var_h_video.get()
            if self.combo_human_level: self.config["humanizer_level"] = self.combo_human_level.get()
            if self.scale_speed: self.config["humanizer_speed"] = self.scale_speed.get()
            if self.spin_retries: self.config["humanizer_retries"] = int(self.spin_retries.get())
            if self.var_adaptive: self.config["humanizer_adaptive"] = self.var_adaptive.get()

            # Defaults Config
            if self.var_def_lyrics: self.config["default_run_lyrics"] = self.var_def_lyrics.get()
            if self.var_def_music: self.config["default_run_music"] = self.var_def_music.get()
            if self.var_def_art_p: self.config["default_run_art_prompt"] = self.var_def_art_p.get()
            if self.var_def_art_i: self.config["default_run_art_image"] = self.var_def_art_i.get()
            if self.var_def_compilation: self.config["default_run_compilation"] = self.var_def_compilation.get()
            
            # Suno Advanced
            if self.var_persona_link_enabled: self.config["suno_persona_link_enabled"] = self.var_persona_link_enabled.get()
            self.config["suno_personas"] = getattr(self, "personas", {})
            if self.combo_persona_select: self.config["suno_active_persona"] = self.combo_persona_select.get()
            
            if self.combo_gender: self.config["vocal_gender"] = self.combo_gender.get()
            if self.var_gender_enabled: self.config["vocal_gender_enabled"] = self.var_gender_enabled.get()
            if self.scale_audio: self.config["audio_influence"] = self.scale_audio.get()
            if self.var_audio_enabled: self.config["audio_influence_enabled"] = self.var_audio_enabled.get()
            if self.scale_weird: self.config["weirdness"] = self.scale_weird.get()
            if self.var_weird_enabled: self.config["weirdness_enabled"] = self.var_weird_enabled.get()
            if self.scale_style: self.config["style_influence"] = self.scale_style.get()
            if self.var_style_enabled: self.config["style_influence_enabled"] = self.var_style_enabled.get()
            if self.combo_lyrics_mode: self.config["lyrics_mode"] = self.combo_lyrics_mode.get()
            if self.var_lyrics_mode_enabled: self.config["lyrics_mode_enabled"] = self.var_lyrics_mode_enabled.get()
            
            # Video Configs
            if self.effect_vars: self.config["video_effects"] = [eff for eff, var in self.effect_vars.items() if var and var.get()]
            if self.spin_fps: self.config["video_fps"] = int(self.spin_fps.get())
            if self.combo_res: self.config["video_resolution"] = self.combo_res.get()
            if self.scale_intensity: self.config["video_intensity"] = self.scale_intensity.get()
            if self.ent_video_assets: self.config["video_assets_path"] = self.ent_video_assets.get()
            if self.var_video_output_mode: self.config["video_output_mode"] = self.var_video_output_mode.get()
            if self.ent_video_custom_path: self.config["video_custom_output_path"] = self.ent_video_custom_path.get()
            if self.combo_video_selection: self.config["video_selection_mode"] = self.combo_video_selection.get()
            if self.combo_parallel_render: self.config["video_parallel_count"] = int(self.combo_parallel_render.get())
            
            # 2. Prompts Data Update
            import json
            prompt_data = {
                "lyrics_master_prompt": self.txt_lyrics.get("1.0", tk.END).strip() if self.txt_lyrics else "",
                "visual_master_prompt": self.txt_visual.get("1.0", tk.END).strip() if self.txt_visual else "",
                "video_master_prompt": self.txt_video.get("1.0", tk.END).strip() if self.txt_video else "",
                "art_master_prompt": self.txt_art.get("1.0", tk.END).strip() if self.txt_art else ""
            }
            if self.prompts_path:
                with open(self.prompts_path, "w", encoding="utf-8") as f:
                    json.dump(prompt_data, f, indent=4, ensure_ascii=False)
            
            # 3. Request App Level Save
            # Note: app_instance must have save_settings(config)
            if hasattr(self.app, "save_settings"):
                self.app.save_settings(self.config)
            
            # Warn about language change
            if self.combo_ui_lang and self.combo_ui_lang.get() != self.app.config.get("ui_language"):
                messagebox.showinfo(self.app.t("ready"), self.app.t("msg_restart_lang"))

            messagebox.showinfo(self.app.t("success"), self.app.t("msg_settings_saved"))
            self.destroy()
        except Exception as e:
            messagebox.showerror(self.app.t("error"), self.app.t("msg_failed_to_save").format(error=e))

class MusicBotGUI:
    def t(self, key):
        lang = self.config.get("ui_language", "Turkish")
        return TRANSLATIONS.get(lang, TRANSLATIONS["Turkish"]).get(key, key)

    def __init__(self, root):
        self.root = root
        
        # 1. State & Logic Flags (Initialize FIRST)
        self.stop_requested = False
        self.active_browser = None
        self._search_timer = None
        self._drag_data = {"item": None}
        self.log_visible = tk.BooleanVar(value=False)
        self.current_song_var = tk.StringVar(value="")
        self.selected_songs = set()
        self.song_steps = {} # Per-song phase selection: {rid: [L, M, AP, AI]}

        # 2. Configuration (Default Values)
        input_path, _, _ = self.get_data_paths()
        self.config = {
            "gemini_lyrics": True, "gemini_style": True, "gemini_visual": True, "gemini_video": False,
            "suno_delay": 15, "startup_delay": 5,
            "metadata_path": input_path,
            "default_run_art_image": True,
            "ui_language": "Turkish",
            "log_open_at_start": False,
            "audio_influence": 25,
            "vocal_gender": "Default",
            "lyrics_mode": "Default",
            "weirdness": "Default",
            "style_influence": "Default",
            "artist_name": "",
            "artist_style": "",
            "artist_presets": {},
            "active_preset": "",
            "weirdness_enabled": False,
            "style_influence_enabled": False,
            "vocal_gender_enabled": False,
            "audio_influence_enabled": False,
            "video_parallel_count": 1,
            "video_selection_mode": "Both (_1 & _2)",
            "suno_batch_mode": False,
            "suno_batch_op_mode": "full"
        }
        
        # 3. Load Saved Settings
        self.load_settings()

        # 4. Finalize Window
        self.root.title(self.t("title"))
        self.root.geometry("1200x850") # Slightly larger for more columns

        # --- THEME (Modernized) ---

        # Workflow Logic Variables
        self.var_run_lyrics = tk.BooleanVar(value=self.config.get("default_run_lyrics", True))
        self.var_run_music = tk.BooleanVar(value=self.config.get("default_run_music", True))
        self.var_run_art_prompt = tk.BooleanVar(value=self.config.get("default_run_art_prompt", True))
        self.var_run_art_image = tk.BooleanVar(value=self.config.get("default_run_art_image", True))
        self.var_run_video = tk.BooleanVar(value=self.config.get("default_run_video", False))
        self.var_run_compilation = tk.BooleanVar(value=self.config.get("default_run_compilation", True))

        # Keyboard Bindings
        self.root.bind("<Return>", lambda e: self.start_process())
        self.root.bind("<Escape>", lambda e: self.stop_process())
        self.root.bind("<Control-f>", lambda e: self.ent_filter.focus())
        self.root.bind("<Command-f>", lambda e: self.ent_filter.focus())
        self.root.bind("<space>", self.on_space_toggle)

        # Apply Light Theme Styles (Constructs UI)
        self.setup_styles()
        
        # --- STYLES ---
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam") # Clam supports color customization better
        
        # Colors
        bg_color = "#f0f2f5"
        accent_color = "#4a90e2" 
        text_color = "#333333"
        white = "#ffffff"
        
        self.root.configure(bg=bg_color)
        
        # General
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=text_color, font=("Helvetica", 11))
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), foreground="#1a1a1a")
        style.configure("TLabelframe", background=bg_color, borderwidth=1)
        style.configure("TLabelframe.Label", background=bg_color, foreground=text_color, font=("Helvetica", 10, "bold"))
        
        # Buttons
        style.configure("TButton", font=("Helvetica", 10), padding=6, borderwidth=1, focuscolor="none")
        style.map("TButton", background=[("active", "#e1e4e8")])
        style.configure("Action.TButton", font=("Helvetica", 11, "bold"), background=white, foreground=accent_color)
        
        # Treeview
        style.configure("Treeview", 
                        background=white, 
                        foreground=text_color, 
                        fieldbackground=white, 
                        rowheight=30, 
                        font=("Helvetica", 10))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), background="#e1e4e8")
        style.map("Treeview", background=[("selected", accent_color)], foreground=[("selected", "white")])

        # --- LAYOUT ---
        self.setup_ui()
        
    def setup_ui(self):
        # Top Bar
        self.f_top = ttk.Frame(self.root, padding=10)
        self.f_top.pack(fill="x")
        
        ttk.Button(self.f_top, text=self.t("settings"), command=self.open_settings).pack(side="right", padx=5)
        ttk.Button(self.f_top, text=self.t("refresh"), command=self.load_project_data).pack(side="right", padx=5)
        
        ttk.Label(self.f_top, text="MusicBot Pro", style="Header.TLabel").pack(side="left", padx=5)
        
        # Unified "Load Project" Button
        self.btn_new = ttk.Button(self.f_top, text=self.t("new_project"), command=self.create_new_project)
        self.btn_new.pack(side="left", padx=5)
        
        self.btn_load = ttk.Button(self.f_top, text=self.t("load_project"), command=self.load_project_file)
        self.btn_load.pack(side="left", padx=5)
        
        # Project Status Label
        self.lbl_project_text = tk.StringVar(value=self.t("no_project"))
        self.lbl_project = ttk.Label(self.f_top, textvariable=self.lbl_project_text, font=("Helvetica", 10, "italic"), foreground="gray")
        self.lbl_project.pack(side="left", padx=10)
        
        ttk.Button(self.f_top, text=self.t("open_project_btn"), command=self.open_xlsx).pack(side="left", padx=2)

        # Filter (Enhanced)
        self.f_filter = ttk.Frame(self.root, padding="5 0 5 10")
        self.f_filter.pack(fill="x", padx=10)
        ttk.Label(self.f_filter, text=self.t("search")).pack(side="left")
        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", self.apply_filter)
        self.ent_filter = ttk.Entry(self.f_filter, textvariable=self.filter_var)
        self.ent_filter.pack(side="left", fill="x", expand=True, padx=5)

        # Select All / Deselect All / Active Only
        self.f_sel_controls = ttk.Frame(self.f_filter)
        self.f_sel_controls.pack(side="right")
        
        ttk.Button(self.f_sel_controls, text=self.t("select_all"), command=self.select_all, width=12).pack(side="left", padx=2)
        ttk.Button(self.f_sel_controls, text=self.t("deselect_all"), command=self.deselect_all, width=12).pack(side="left", padx=2)
        
        self.var_active_only = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.f_sel_controls, text=self.t("active_only"), variable=self.var_active_only, command=self.apply_filter).pack(side="left", padx=5)

        # Status Filter Dropdown
        ttk.Label(self.f_sel_controls, text=self.t("filter_status")).pack(side="left", padx=(10, 2))
        self.status_filter_var = tk.StringVar(value="All")
        self.cmb_status = ttk.Combobox(self.f_sel_controls, textvariable=self.status_filter_var, 
                                       state="readonly", width=18)
        # Update values with new options
        self.cmb_status['values'] = [
            self.t("f_all"), self.t("f_done"), self.t("f_pending"),
            self.t("f_no_lyrics"), self.t("f_no_music"), self.t("f_no_art"), self.t("f_no_video"),
            self.t("f_missing_r"), self.t("f_missing_m1"), self.t("f_missing_m2")
        ]
        self.cmb_status.current(0)
        self.cmb_status.bind("<<ComboboxSelected>>", self.apply_filter)
        self.cmb_status.pack(side="left", padx=2)

        # Active Run Controls (MODERNIZED & INTEGRATED TO DASHBOARD)
        self.f_run_ops = ttk.LabelFrame(self.root, text=self.t("global_settings"), padding=5)
        self.f_run_ops.pack(fill="x", padx=10, pady=(0, 5))
        
        ttk.Checkbutton(self.f_run_ops, text=self.t("lyrics"), variable=self.var_run_lyrics, command=self.apply_filter).pack(side="left", padx=10)
        ttk.Checkbutton(self.f_run_ops, text=self.t("music"), variable=self.var_run_music, command=self.apply_filter).pack(side="left", padx=10)
        ttk.Checkbutton(self.f_run_ops, text=self.t("art_prompt"), variable=self.var_run_art_prompt, command=self.apply_filter).pack(side="left", padx=10)
        ttk.Checkbutton(self.f_run_ops, text=self.t("art_image"), variable=self.var_run_art_image, command=self.apply_filter).pack(side="left", padx=10)
        ttk.Checkbutton(self.f_run_ops, text=self.t("video"), variable=self.var_run_video, command=self.apply_filter).pack(side="left", padx=10)
        ttk.Checkbutton(self.f_run_ops, text=self.t("compilation"), variable=self.var_run_compilation, command=self.apply_filter).pack(side="left", padx=10)

        # Batch Mode Section (Moved to Main)
        ttk.Separator(self.f_run_ops, orient="vertical").pack(side="left", fill="y", padx=10)
        
        self.var_suno_batch = tk.BooleanVar(value=self.config.get("suno_batch_mode", False))
        ttk.Checkbutton(self.f_run_ops, text="Batch", variable=self.var_suno_batch).pack(side="left", padx=5)
        
        self.var_batch_op = tk.StringVar(value=self.config.get("suno_batch_op_mode", "full"))
        ttk.Radiobutton(self.f_run_ops, text="Full", variable=self.var_batch_op, value="full").pack(side="left", padx=2)
        ttk.Radiobutton(self.f_run_ops, text="Gen", variable=self.var_batch_op, value="gen_only").pack(side="left", padx=2)
        ttk.Radiobutton(self.f_run_ops, text="DL", variable=self.var_batch_op, value="dl_only").pack(side="left", padx=2)

        # Main Table
        self.f_tree = ttk.Frame(self.root)
        self.f_tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Columns
        columns = ("sel", "id", "title", "style", "progress", "lyrics", "music", "art", "video_status", "materials", "run_l", "run_m", "run_ap", "run_ai", "run_v")
        self.tree = ttk.Treeview(self.f_tree, columns=columns, show="headings", selectmode="extended")
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<Motion>", self.on_tree_hover)
        self.tree.bind("<Leave>", self.on_tree_leave)
        
        # Style Tags
        self.tree.tag_configure("hover", background="#eef6ff") 
        
        # Drag & Drop Events
        self.tree.bind("<ButtonPress-1>", self.on_reorder_start, add="+")
        self.tree.bind("<B1-Motion>", self.on_reorder_motion)
        self.tree.bind("<ButtonRelease-1>", self.on_reorder_stop)

        # Setup Columns
        self.tree.heading("sel", text="✔")
        self.tree.heading("id", text="ID", command=lambda: self.sort_tree("id", False))
        self.tree.heading("title", text=self.t("column_title"), command=lambda: self.sort_tree("title", False))
        self.tree.heading("style", text=self.t("column_style"))
        self.tree.heading("progress", text=self.t("column_progress"))
        self.tree.heading("lyrics", text="📝", command=lambda: self.sort_tree("lyrics", False))
        self.tree.heading("music", text="🎵", command=lambda: self.sort_tree("music", False))
        self.tree.heading("art", text="🎨", command=lambda: self.sort_tree("art", False))
        self.tree.heading("video_status", text="🎬", command=lambda: self.sort_tree("video_status", False))
        self.tree.heading("materials", text=self.t("column_materials"), command=lambda: self.sort_tree("materials", False))
        self.tree.heading("run_l", text="L")
        self.tree.heading("run_m", text="M")
        self.tree.heading("run_ap", text="AP")
        self.tree.heading("run_ai", text="AI")
        self.tree.heading("run_v", text="V")
        
        # Columns Config
        self.tree.column("sel", width=30, anchor="center")
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("title", width=200)
        self.tree.column("style", width=100)
        self.tree.column("progress", width=120)
        self.tree.column("lyrics", width=30, anchor="center")
        self.tree.column("music", width=30, anchor="center")
        self.tree.column("art", width=30, anchor="center")
        self.tree.column("video_status", width=30, anchor="center")
        self.tree.column("materials", width=80, anchor="center")
        self.tree.column("run_l", width=30, anchor="center")
        self.tree.column("run_m", width=30, anchor="center")
        self.tree.column("run_ap", width=30, anchor="center")
        self.tree.column("run_ai", width=30, anchor="center")
        self.tree.column("run_v", width=30, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.f_tree, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # --- STATUS & CONTROL (CLEAN UI) ---
        self.f_bottom = ttk.Frame(self.root, padding=10)
        self.f_bottom.pack(fill="x", side="bottom")
        
        self.status_bar = ttk.Frame(self.f_bottom)
        self.status_bar.pack(fill="x", pady=(0, 5))
        
        self.lbl_badge = tk.Label(self.status_bar, text=f" ● {self.t('badge_idle')} ", font=("Helvetica", 9, "bold"), bg="#888888", fg="white", padx=8, pady=2)
        self.lbl_badge.pack(side="left")
        
        self.status_var = tk.StringVar(value=self.t("ready"))
        ttk.Label(self.status_bar, textvariable=self.status_var, font=("Helvetica", 10, "italic")).pack(side="left", padx=10)
        
        ttk.Label(self.status_bar, text="|", foreground="gray").pack(side="left", padx=5)
        self.lbl_current_song = ttk.Label(self.status_bar, textvariable=self.current_song_var, font=("Helvetica", 10, "bold"), foreground="#4a90e2")
        self.lbl_current_song.pack(side="left", padx=5, fill="x", expand=True)

        # Action Buttons
        self.f_btns = ttk.Frame(self.f_bottom)
        self.f_btns.pack(fill="x")
        
        self.btn_run = ttk.Button(self.f_btns, text=self.t("start"), style="Action.TButton", command=self.start_process)
        self.btn_run.pack(side="left", fill="x", expand=True, padx=2)
        
        self.btn_stop = ttk.Button(self.f_btns, text=self.t("stop"), command=self.stop_process)
        self.btn_stop.pack(side="left", fill="x", expand=True, padx=2)
        self.btn_stop.configure(state="disabled")

        # --- COLLAPSIBLE LOGS (NEW) ---
        self.f_log_container = ttk.Frame(self.root)
        self.f_log_container.pack(fill="x", side="bottom", padx=10, pady=(0, 5))
        
        self.btn_toggle_log = ttk.Button(self.f_log_container, text=self.t("show_log"), command=self.toggle_logs)
        self.btn_toggle_log.pack(fill="x")
        
        self.f_log_content = ttk.Frame(self.f_log_container)
        # Initially hidden:
        self.log_text = scrolledtext.ScrolledText(self.f_log_content, height=10, font=("Consolas", 9), bg="#ffffff")
        self.log_text.pack(fill="both", expand=True)

        # Connect Logger
        self.gui_handler = GuiLogger(self.log_text)
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')
        self.gui_handler.setFormatter(formatter)
        logging.getLogger().addHandler(self.gui_handler)
        
        # Data Cache
        self.all_songs = {} 
        self.filtered_ids = []
        
        # Initial Load
        self.load_project_data() # Load last project or show no project
        
        # Handle log visibility at startup
        if self.config.get("log_open_at_start", False):
            self.root.after(100, self.toggle_logs)

    def load_settings(self):
        """Loads settings from settings.json in workspace."""
        workspace = os.path.expanduser("~/Documents/MusicBot_Workspace")
        settings_path = os.path.join(workspace, "settings.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        saved_config = json.loads(content)
                        if isinstance(saved_config, dict):
                            self.config.update(saved_config)
                            logger.info(self.t("log_settings_loaded"))
                            
                            # Restore last profile
                            last_p = self.config.get("last_active_profile")
                            if last_p and last_p in self.config.get("artist_presets", {}):
                                self.config["active_preset"] = last_p
            except Exception as e:
                logger.error(f"❌ {self.t('log_settings_fail').format(error=e)}")
                # If settings are corrupted, we just continue with defaults

    def save_settings(self, new_config=None):
        """Saves current config to settings.json in workspace."""
        if new_config:
            self.config.update(new_config)
        
        # Sync dashboard variables to config
        if hasattr(self, "var_suno_batch"):
            self.config["suno_batch_mode"] = self.var_suno_batch.get()
        if hasattr(self, "var_batch_op"):
            self.config["suno_batch_op_mode"] = self.var_batch_op.get()

        workspace = os.path.expanduser("~/Documents/MusicBot_Workspace")
        os.makedirs(workspace, exist_ok=True)
        settings_path = os.path.join(workspace, "settings.json")
        
        try:
            # Save last profile for persistence
            if "active_preset" in self.config:
                self.config["last_active_profile"] = self.config["active_preset"]
                
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info("✅ Settings saved to settings.json")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    def update_progress(self, rid, text):
        """Updates the progress text for a specific row ID."""
        if self.tree.exists(rid):
            # If text is something like 'Suno: Generating 20%', we can extract info
            # For now, we update the progress column directly
            self.tree.set(rid, "progress", text)
            
            # If it's a completion mark, we might want to refresh the bar
            if "✅" in text or "Done" in text:
                # Re-fetch song state and update
                pass 
        
    def open_settings(self):
        # Pass the path to prompts.json for the PromptEditor
        prompts_path = self.get_prompts_path()
        self.config["metadata_path"] = prompts_path # This is a bit of a hack, but PromptEditor expects metadata_path
        SettingsDialog(self.root, self.config, self)

    def create_new_project(self):
        """Creates a new project file from template."""
        
        # 1. Define Workspace
        workspace = os.path.expanduser("~/Documents/MusicBot_Workspace")
        if not os.path.exists(workspace): os.makedirs(workspace)
        
        # 2. Ask User for Filename
        initial_file = f"Project_{int(time.time())}.xlsx"
        path = filedialog.asksaveasfilename(
            initialdir=workspace,
            initialfile=initial_file,
            title=self.t("new_project"),
            filetypes=[("Excel Files", "*.xlsx")]
        )
        
        if not path: return # User cancelled
        
        if not path.endswith(".xlsx"): path += ".xlsx"
        
        # 3. Create File (Using openpyxl directly to be self-contained)
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Music Project"
            
            headers = [
                "id", "prompt", "style", "title", "lyrics", "status", 
                "visual_prompt", "video_prompt", "cover_art_prompt", "cover_art_path"
            ]
            ws.append(headers)
            # Add example row
            ws.append(["EXAMPLE_01", "A happy song about coding", "Pop", "Code Joy", "", "Pending", "", "", "", ""])
            
            wb.save(path)
            logger.info(f"Created new project: {path}")
            
            # 4. Load it immediately
            self.load_project_data(path)
            messagebox.showinfo(self.t("success"), self.t("msg_new_project_created"))
            
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            messagebox.showerror(self.t("error"), f"{self.t('msg_failed_to_create_project')}: {e}")

    def load_project_file(self):
        """Opens file dialog to select a project file."""
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title=self.t("load_project"),
            filetypes=[("Excel Files", "*.xlsx")],
            initialdir=os.path.expanduser("~/Documents")
        )
        if path:
            self.config["last_project"] = path
            self.load_project_data(path)

    def load_project_data(self, path=None):
        """Loads data from the single project file."""
        if not path:
            path = self.config.get("last_project")
            
        if not path or not os.path.exists(path):
            self.lbl_project.config(text=self.t("no_project"), foreground="gray")
            self.all_songs = {}
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.apply_filter() # Clear the treeview
            self.status_var.set(self.t("ready"))
            return

        self.project_path = path
        self.lbl_project_text.set(f"📄 {os.path.basename(path)}")
        self.lbl_project.config(foreground="green")
        
        # Ensure Output Logic (Auto-Initialize columns)
        self.ensure_project_structure(path)
        
        # Read Data
        try:
            wb = openpyxl.load_workbook(path, data_only=True)
            ws = wb.active
            headers = {str(cell.value).strip().lower(): i for i, cell in enumerate(ws[1]) if cell.value}
            
            self.all_songs = {}
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            for row in ws.iter_rows(min_row=2, values_only=True):
                # ID Logic (Robust)
                id_idx = headers.get('id')
                if id_idx is None: id_idx = 0 # Default to column A
                rid = str(row[id_idx]) if id_idx < len(row) and row[id_idx] is not None else ""
                
                # Check Prompt/Title
                prompt = ""
                if 'prompt' in headers and row[headers['prompt']] is not None: prompt = str(row[headers['prompt']])
                elif 'title' in headers and row[headers['title']] is not None: prompt = str(row[headers['title']])
                
                style = str(row[headers.get('style', 0)]) if 'style' in headers and row[headers.get('style')] is not None else ""
                
                # Status checks
                has_lyrics = True if 'lyrics' in headers and row[headers['lyrics']] else False
                has_music = True if 'status' in headers and str(row[headers['status']]).lower() in ["completed", "generated"] else False
                has_art = True if 'cover_art_path' in headers and row[headers['cover_art_path']] else False
                has_video = True if 'video_path' in headers and row[headers['video_path']] else False
                
                if rid or prompt:
                    if not rid: rid = f"PENDING_{len(self.all_songs) + 1}"
                    self.all_songs[rid] = {
                        "id": rid, "title": prompt, "style": style,
                        "lyrics": has_lyrics, "music": has_music, "art": has_art, "video": has_video,
                        "video_exists": False, "material_status": ""
                    }
            
            self.scan_materials()
            self.apply_filter()
            self.status_var.set(f"{self.t('msg_loaded_songs').format(count=len(self.all_songs))}")
            
        except Exception as e:
            logger.error(f"Error loading project: {e}")
            messagebox.showerror(self.t("error"), f"{self.t('msg_failed_to_load_project')}: {e}")

    def scan_materials(self):
        """Scans filesystem to detect material presence and existing videos."""
        if not self.project_path: return
        
        profile_name = self.config.get("active_preset", "Default")
        output_media = os.path.join(os.path.dirname(self.project_path), "output_media", profile_name)
        if not os.path.exists(output_media): return

        videos_dir = os.path.join(output_media, "videos")
        done_dir = os.path.join(output_media, "done")
        not_used_dir = os.path.join(output_media, "not_used")
        
        # Collect ONLY files in the root for material status (Ref: User request)
        all_files = []
        if os.path.exists(output_media):
            all_files = [f.lower() for f in os.listdir(output_media)]
        
        video_files = []
        if os.path.exists(videos_dir):
            video_files = [f.lower() for f in os.listdir(videos_dir) if f.endswith(".mp4")]

        for rid, s in self.all_songs.items():
            rid_l = str(rid).lower()
            
            # 1. Check Video Status
            has_v = False
            for vf in video_files:
                if vf.startswith(f"{rid_l}_") or vf == f"{rid_l}.mp4":
                    has_v = True; break
            s["video_exists"] = has_v

            # If video already exists, we don't need to scan materials
            if has_v:
                s["material_status"] = "DONE"
                continue
            
            # 2. Check Materials (R, M1, M2)
            has_r = False
            for rf in all_files:
                if rf == f"{rid_l}.png" or rf == f"{rid_l}.jpg" or rf == f"{rid_l}.jpeg":
                    has_r = True; break
                # Also check sequence patterns or files starting with ID_
                if rf.startswith(f"{rid_l}_") and rf.split(".")[-1] in ["png", "jpg", "jpeg"]:
                    has_r = True; break

            has_m1 = False
            has_m2 = False
            for af in all_files:
                # Check exact matches or files starting with ID_ and ending with _1/_2
                if af == f"{rid_l}.mp3" or af == f"{rid_l}.wav": 
                    has_m1 = True
                
                if af.startswith(f"{rid_l}_") and af.lower().endswith((".mp3", ".wav")):
                    name_no_ext = os.path.splitext(af)[0]
                    if name_no_ext.endswith("_1") or name_no_ext == f"{rid_l}_1":
                        has_m1 = True
                    if name_no_ext.endswith("_2") or name_no_ext == f"{rid_l}_2":
                        has_m2 = True
            
            status_parts = []
            if not has_r: status_parts.append("R")
            if not has_m1: status_parts.append("M1")
            if not has_m2: status_parts.append("M2")
            
            s["material_status"] = "/".join(status_parts) if status_parts else "OK"

    def ensure_project_structure(self, path):
        """Adds missing columns to a raw input file to make it a Project File."""
        try:
            wb = openpyxl.load_workbook(path)
            ws = wb.active
            
            # Map current headers
            headers = {str(cell.value).lower(): cell.column for cell in ws[1] if cell.value}
            
            # Required Columns
            required = [
                "id", "prompt", "style", "title", "lyrics", "status", 
                "visual_prompt", "video_prompt", "suno_style", "cover_art_prompt", "cover_art_path"
            ]
            
            updates = False
            for col in required:
                if col not in headers:
                    new_idx = ws.max_column + 1
                    ws.cell(row=1, column=new_idx, value=col)
                    headers[col] = new_idx
                    updates = True
            
            if updates:
                wb.save(path)
                logger.info(f"Project structure initialized for {os.path.basename(path)}")
        except Exception as e:
            logger.error(f"Structure init error: {e}")
    def get_progress_bar(self, current, total=3):
        """Returns a text-based progress bar."""
        try:
            percent = (current / total) * 100
            filled_len = int(10 * current // total)
            bar = "█" * filled_len + "░" * (10 - filled_len)
            return f"{bar} {int(percent)}%"
        except: return "░░░░░░░░░░ 0%"

    def apply_filter(self, *args):
        # Debounced Search (300ms)
        if not hasattr(self, "_search_timer"):
            return # Safety for early calls
            
        if self._search_timer:
            self.root.after_cancel(self._search_timer)
        self._search_timer = self.root.after(300, self._do_filter)

    def _do_filter(self):
        query = self.filter_var.get().lower()
        active_only = self.var_active_only.get()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.filtered_ids = []
        
        for rid, s in self.all_songs.items():
            # 1. Text Query
            if query and query not in s["title"].lower() and query not in rid.lower():
                continue
            
            # 2. Active Only Filter
            if active_only and rid not in self.selected_songs:
                # Also check if it's currently processing
                is_active = False
                if hasattr(self, "processing_ids") and rid in self.processing_ids:
                    is_active = True
                if not is_active:
                    continue

            # 3. Status Filter (Done/Pending/Specifics)
            s_filter = self.status_filter_var.get()
            done_cnt = sum([1 for k in ["lyrics", "music", "art"] if s.get(k)])
            
            if s_filter == self.t("f_done") and done_cnt < 3:
                continue
            elif s_filter == self.t("f_pending") and done_cnt == 3:
                continue
            elif s_filter == self.t("f_no_lyrics") and s.get("lyrics"):
                continue
            elif s_filter == self.t("f_no_music") and s.get("music"):
                continue
            elif s_filter == self.t("f_no_art") and s.get("art"):
                continue
            elif s_filter == self.t("f_no_video") and s.get("video"):
                continue
            elif s_filter == self.t("f_missing_r") and "R" not in s.get("material_status", ""):
                continue
            elif s_filter == self.t("f_missing_m1") and "M1" not in s.get("material_status", ""):
                continue
            elif s_filter == self.t("f_missing_m2") and "M2" not in s.get("material_status", ""):
                continue

            self.filtered_ids.append(rid)
            
            # Symbols
            s_lyrics = "✅" if s["lyrics"] else "⚪"
            s_music = "✅" if s["music"] else "⚪"
            s_art = "✅" if s["art"] else "⚪"
            s_v = "✅" if s.get("video") or s.get("video_exists") else "⚪"
            s_mat = s.get("material_status", "")
            s_sel = "☑️" if rid in self.selected_songs else "☐"
            
            # Progress Logic
            done_cnt_v = sum([1 for k in ["lyrics", "music", "art", "video"] if s.get(k)])
            prog_bar = self.get_progress_bar(done_cnt_v, 4)
            
            # Step Toggles (Per-song Phase Selection)
            steps = self.song_steps.get(rid)
            if steps is None:
                steps = [
                    self.var_run_lyrics.get(), 
                    self.var_run_music.get(), 
                    self.var_run_art_prompt.get(), 
                    self.var_run_art_image.get(),
                    self.var_run_video.get()
                ]
            
            # UNIQUE COLORS per step
            s_rl = "🟣" if steps[0] else "☐"
            s_rm = "🔵" if steps[1] else "☐"
            s_rap = "🟡" if steps[2] else "☐"
            s_rai = "🟢" if steps[3] else "☐"
            s_rv = "🟠" if (len(steps) > 4 and steps[4]) else "☐"

            self.tree.insert("", "end", iid=rid, values=(
                s_sel, s["id"], s["title"], s.get("style", ""), prog_bar, s_lyrics, s_music, s_art, s_v, s_mat,
                s_rl, s_rm, s_rap, s_rai, s_rv
            ))

    def select_all(self):
        """Selects all songs currently visible in the filtered list."""
        for rid in self.filtered_ids:
            if rid not in self.selected_songs:
                self.selected_songs.add(rid)
        self.apply_filter()

    def deselect_all(self):
        """Deselects all songs currently visible in the filtered list."""
        for rid in self.filtered_ids:
            if rid in self.selected_songs:
                self.selected_songs.remove(rid)
        self.apply_filter()

    def sort_tree(self, col, reverse):
        """Sorts the treeview by column."""
        # Get data from tree
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        
        # Try to sort numerically if possible
        try:
            l.sort(key=lambda x: float(re.sub(r'[^\d.]', '', x[0])), reverse=reverse)
        except:
            l.sort(reverse=reverse)

        # Rearrange items in tree
        for index, (val, k) in enumerate(l):
            self.tree.move(k, "", index)

        # Reverse sort next time
        self.tree.heading(col, command=lambda: self.sort_tree(col, not reverse))
            
    def set_badge(self, text, bg, fg="white"):
        self.lbl_badge.config(text=f" ● {text} ", bg=bg, fg=fg)

    def toggle_logs(self):
        if self.log_visible.get():
            self.f_log_content.pack_forget()
            self.btn_toggle_log.config(text=self.t("show_log"))
            self.log_visible.set(False)
        else:
            self.f_log_content.pack(fill="x", pady=5)
            self.btn_toggle_log.config(text=self.t("hide_log"))
            self.log_visible.set(True)

    def on_space_toggle(self, event):
        """Selected rows toggle checkbox with space."""
        selected = self.tree.selection()
        if not selected: return
        
        for item_id in selected:
            if item_id in self.selected_songs:
                self.selected_songs.remove(item_id)
                self.tree.set(item_id, "sel", "☐")
            else:
                self.selected_songs.add(item_id)
                self.tree.set(item_id, "sel", "☑️")

    def play_chime(self):
        """Plays a notification sound based on OS."""
        try:
            if sys.platform == "darwin":
                os.system("afplay /System/Library/Sounds/Glass.aiff &")
            elif sys.platform == "win32":
                import winsound
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
        except: pass



    # --- DRAG & DROP REORDERING ---
    def on_reorder_start(self, event):
        item = self.tree.identify_row(event.y)
        if item: self._drag_data["item"] = item

    def on_reorder_motion(self, event):
        pass

    def on_reorder_stop(self, event):
        target = self.tree.identify_row(event.y)
        source = self._drag_data.get("item")
        if target and source and target != source:
            self.tree.move(source, "", self.tree.index(target))
        self._drag_data["item"] = None

    def on_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item_id = self.tree.identify_row(event.y)
            if not item_id: return

            if column not in ["#10", "#11", "#12", "#13", "#14"]: # Any column EXCEPT the phase toggles
                if item_id in self.selected_songs:
                    self.selected_songs.remove(item_id)
                    self.tree.set(item_id, "sel", "☐")
                else:
                    self.selected_songs.add(item_id)
                    self.tree.set(item_id, "sel", "☑️")
                
                # Visual Highlight
                self.tree.selection_set(item_id)
                self.tree.focus(item_id)
            
            elif column in ["#10", "#11", "#12", "#13", "#14"]: # L, M, AP, AI, V
                idx = int(column[1:]) - 10 # 0, 1, 2, 3, 4
                
                # Get current setting or defaults
                current_defaults = [
                    self.var_run_lyrics.get(),
                    self.var_run_music.get(),
                    self.var_run_art_prompt.get(),
                    self.var_run_art_image.get(),
                    self.var_run_video.get()
                ]
                
                steps = self.song_steps.get(item_id, current_defaults).copy()
                
                # Ensure steps list is long enough (backwards compatibility)
                while len(steps) < 5: steps.append(False)
                
                steps[idx] = not steps[idx]
                self.song_steps[item_id] = steps
                
                # Update UI with UNIQUE COLORS
                char = "☐"
                if steps[idx]:
                    if idx == 0: char = "🟣"
                    elif idx == 1: char = "🔵"
                    elif idx == 2: char = "🟡"
                    elif idx == 3: char = "🟢"
                    elif idx == 4: char = "🟠"

                col_name = self.tree.cget("columns")[idx + 9] # column name index 9 is run_l
                self.tree.set(item_id, col_name, char)
            
            return "break" # Prevent selection change if clicking checkbox
            
    def on_tree_hover(self, event):
        item = self.tree.identify_row(event.y)
        # Clear existing hover tags
        for i in self.tree.tag_has("hover"):
            self.tree.item(i, tags=())
        # Apply to current
        if item:
            self.tree.item(item, tags=("hover",))

    def on_tree_leave(self, event):
        # Clear all hover tags when mouse leaves the widget
        for i in self.tree.tag_has("hover"):
            self.tree.item(i, tags=())

    def start_process(self):
        # --- Pre-flight Checks 🛡️ ---
        if not self.project_path:
            logger.error(self.t("msg_no_project"))
            messagebox.showerror(self.t("error"), self.t("msg_load_first"))
            return

        # Check input file existence
        # self.project_path is the unified file (e.g. .../MusicBot_Workspace/ProjeX/ProjeX.xlsx)
        if not os.path.exists(self.project_path):
             logger.error(f"❌ Project file not found: {self.project_path}")
             return

        # Check if at least one step is selected
        if not any([self.var_run_lyrics.get(), self.var_run_music.get(), self.var_run_art_prompt.get(), self.var_run_art_image.get(), self.var_run_video.get(), self.var_run_compilation.get()]):
            logger.error(self.t("msg_no_steps"))
            messagebox.showwarning(self.t("warning"), self.t("msg_select_step_warn"))
            return

        # 1. Use manual checkboxes if any
        target_ids = list(self.selected_songs)
        
        # 2. If no checkboxes, use tree selection
        if not target_ids:
            selected_items = self.tree.selection()
            if selected_items:
                target_ids = list(selected_items)
            else:
                # If filter is active and nothing selected, ask to process all filtered
                if messagebox.askyesno(self.t("confirm"), self.t("msg_confirm_process_all")):
                    target_ids = self.filtered_ids
        
        if not target_ids:
            return

        # [Requirement 6] Strict Sequential Processing by ID
        try:
            target_ids.sort(key=lambda x: (float(re.sub(r'[^\d.]', '', x)) if re.search(r'\d', x) else 0, x))
        except:
            target_ids.sort()

        self.stop_requested = False
        self.disable_buttons()
        threading.Thread(target=self.run_process, args=(target_ids,), daemon=True).start()

    def stop_process(self):
        self.stop_requested = True
        self.status_var.set(self.t("msg_stopping"))
        self.set_badge(self.t("badge_stopping"), "#ffaa00")
        if self.active_browser:
            try:
                self.active_browser.stop()
                logger.warning(self.t("log_browser_stop"))
            except: pass

    def _check_existing_data(self, target_ids):
        """Checks if any of the target songs already have data in the requested steps."""
        try:
            wb = openpyxl.load_workbook(self.project_path, data_only=True)
            ws = wb.active
            headers = {str(cell.value).lower(): i for i, cell in enumerate(ws[1]) if cell.value}
            
            # Robust column mapping (Case insensitive)
            col_map = {str(cell.value).strip().lower(): cell.column - 1 for cell in ws[1] if cell.value}
            lyrics_col = col_map.get("lyrics")
            visual_col = col_map.get("visual_prompt") or col_map.get("visual prompt") or col_map.get("visual_prompts")
            video_col = col_map.get("video_prompt") or col_map.get("video prompt") or col_map.get("video_prompts")
            id_col = col_map.get("id", 0)

            # Normalize target_ids set
            target_ids_set = set(str(t).strip().lower() for t in target_ids)

            for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                rid_orig = row[id_col]
                rid = str(rid_orig).strip().lower() if rid_orig is not None else ""
                
                if not rid: rid = f"PENDING_{i}"
                
                if rid in target_ids_set:
                    # Get specific steps for THIS song
                    s_steps = self.song_steps.get(str(rid_orig))
                    if s_steps is None:
                        s_steps = [
                            self.var_run_lyrics.get(), 
                            self.var_run_music.get(),
                            self.var_run_art_prompt.get(),
                            self.var_run_art_image.get(),
                            self.var_run_video.get()
                        ]

                    # Check if user wants lyrics for THIS song AND they exist
                    if s_steps[0] and lyrics_col is not None and row[lyrics_col] and str(row[lyrics_col]).strip():
                        return True
                    # Check if user wants visuals for THIS song AND they exist
                    if s_steps[2] and visual_col is not None and row[visual_col] and str(row[visual_col]).strip():
                        return True
                    # Check if user wants video prompts for THIS song AND they exist
                    if s_steps[2] and self.config.get("gemini_video", False) and video_col is not None and row[video_col] and str(row[video_col]).strip():
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking existing data: {e}")
            return False

    def run_process(self, target_ids):
        start_time = time.time()
        total_songs = len(target_ids)
        self.video_render_queue = [] # Fixed: Always initialize at start
        
        try:
            # Check for existing data if we are running Gemini steps
            force_update = False
            # We must check if ANY of the target songs have s_steps[0] (Purple) or s_steps[2] (Yellow) enabled
            # before calling _check_existing_data
            any_gemini_requested = False
            for rid in target_ids:
                s_steps = self.song_steps.get(rid)
                if s_steps is None:
                    s_steps = [
                        self.var_run_lyrics.get(),
                        self.var_run_music.get(),
                        self.var_run_art_prompt.get(),
                        self.var_run_art_image.get(),
                        self.var_run_video.get()
                    ]
                
                if s_steps[0] or s_steps[2]:
                    any_gemini_requested = True
                    break

            if any_gemini_requested:
                has_data = self._check_existing_data(target_ids)
                if has_data:
                    # Ask user if they want to re-generate
                    if messagebox.askyesno(self.t("msg_confirm_regen"), self.t("msg_regen_body")):
                        force_update = True

            # Unified Project Path (Profile-based: output_media/[Profile_Name])
            project_file = self.project_path
            profile_name = self.config.get("active_preset", "Default")
            workspace = os.path.expanduser("~/Documents/MusicBot_Workspace")
            output_media = os.path.join(os.path.dirname(project_file), "output_media", profile_name)
            if not os.path.exists(output_media): os.makedirs(output_media, exist_ok=True)
            
            def progress_callback(rid, text):
                if rid == "global":
                    self.status_var.set(text)
                else:
                    self.root.after(0, lambda: self.update_progress(rid, text))

                    self.active_browser = None
                
            
            # =================================================================================================
            # DECISION POINT: Batch Mode vs Sequential Mode
            # =================================================================================================
            is_batch_mode = self.var_suno_batch.get() if hasattr(self, "var_suno_batch") else self.config.get("suno_batch_mode", False)
            # Sync op_mode to config for use inside batch methods
            if hasattr(self, "var_batch_op"):
                self.config["suno_batch_op_mode"] = self.var_batch_op.get()

            if is_batch_mode:
                logger.info(f"🚀 STARTING ENGINE IN BATCH MODE (PHASED EXECUTION - {self.config.get('suno_batch_op_mode')})")
                self._run_process_batch_mode(target_ids, project_file, output_media, workspace, start_time, progress_callback, force_update)
            else:
                logger.info("🚂 STARTING ENGINE IN SEQUENTIAL MODE")
                self._run_process_sequential_mode(target_ids, project_file, output_media, workspace, start_time, progress_callback, force_update)

            # --- Phase 2: Parallel Video Rendering ---
                
            # --- Phase 2: Parallel Video Rendering ---
            if hasattr(self, "video_render_queue") and self.video_render_queue and not self.stop_requested:
                parallel_count = int(self.config.get("video_parallel_count", 1))
                logger.info(f"Starting Parallel Video Rendering: {len(video_render_queue)} tasks, pool size: {parallel_count}")
                self.root.after(0, lambda: self.status_var.set(f"Rendering {len(video_render_queue)} Videos ({parallel_count} parallel)..."))
                
                from video_generator import VideoGenerator
                
                def run_parallel_task(task):
                    if self.stop_requested: return
                    try:
                        vgen = VideoGenerator(output_dir=task["output_dir"])
                        success = vgen.generate_video(
                            audio_path=task["audio_path"],
                            image_path=task["image_path"],
                            output_filename=task["output_filename"],
                            **task["params"],
                            progress_callback=progress_callback
                        )
                        if success:
                            # Move used materials to 'done' (Ref: output_media/[profile]/done)
                            try:
                                done_dir = os.path.join(task["profile_dir"], "done")
                                if not os.path.exists(done_dir): os.makedirs(done_dir, exist_ok=True)
                                # Audio
                                if os.path.exists(task["audio_path"]):
                                    shutil.move(task["audio_path"], os.path.join(done_dir, os.path.basename(task["audio_path"])))
                                # Image
                                if os.path.exists(task["image_path"]):
                                    shutil.move(task["image_path"], os.path.join(done_dir, os.path.basename(task["image_path"])))
                            except Exception as me:
                                logger.warning(f"Failed to move files to done/: {me}")
                    except Exception as ve:
                        logger.error(f"Parallel Render Error ({task['rid']}): {ve}")
                        progress_callback(task["rid"], "Render Failed ❌")

                # Run pool
                with ThreadPoolExecutor(max_workers=parallel_count) as pool:
                    pool.map(run_parallel_task, self.video_render_queue)
                
                logger.info("Parallel Video Rendering Phase Completed.")
                self.scan_materials() # Refresh status icons

            # --- Step 6: Video Merger (Compilation) ---
            if self.var_run_compilation.get() and not self.stop_requested:
                try:
                    logger.info(self.t("log_merge_start"))
                    self.root.after(0, lambda: self.status_var.set(self.t("compilation")))
                    
                    video_dir = os.path.join(output_media, "videos")
                    if self.config.get("video_output_mode") == "custom":
                        video_dir = self.config.get("video_custom_output_path") or os.path.join(workspace, "Output_Videos")
                    
                    if os.path.exists(video_dir):
                        # Get all .mp4 files in the video dir, excluding existing compilations
                        all_vids = [os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.endswith(".mp4") and not f.startswith("Compilation_")]
                        all_vids.sort() # Sort by name (ids usually)
                        
                        if all_vids:
                            from video_merger import VideoMerger
                            merger = VideoMerger(output_dir=video_dir)
                            compilation_name = f"Compilation_{profile_name}_{int(time.time())}.mp4"
                            success = merger.merge_videos(all_vids, compilation_name)
                            if success:
                                logger.info(self.t("log_merge_success").format(path=compilation_name))
                            else:
                                logger.error(self.t("log_merge_fail").format(error="Process Interrupted or Failed"))
                        else:
                            logger.warning(self.t("log_merge_no_files").format(path=video_dir))
                except Exception as e:
                    logger.error(self.t("log_merge_fail").format(error=str(e)))

            self.root.after(0, lambda: self.current_song_var.set(""))
            self.play_chime()
            self.root.after(0, lambda: messagebox.showinfo(self.t("msg_done_title"), self.t("msg_done_info")))
            self.root.after(0, self.load_project_data) # Refresh UI

        except Exception as e:
            err_msg = str(e)
            logger.error(f"Critical Process Error: {err_msg}")
            self.root.after(0, lambda m=err_msg: messagebox.showerror(self.t("msg_critical_error"), m))
        finally:
            self.root.after(0, self.enable_buttons)
            self.load_data()



    def get_prompts_path(self):
        """Returns the path to prompts.json in the workspace, initializing it if needed."""
        workspace = os.path.expanduser("~/Documents/MusicBot_Workspace")
        os.makedirs(workspace, exist_ok=True)
        prompts_path = os.path.join(workspace, "prompts.json")
        
        if not os.path.exists(prompts_path):
            # Try to migrate from old location
            old_path = os.path.join(os.getcwd(), "data", "prompts.json")
            if os.path.exists(old_path):
                import shutil
                shutil.copy(old_path, prompts_path)
            else:
                # Fallback default
                try:
                    import json
                    with open(prompts_path, "w", encoding="utf-8") as f:
                         json.dump({
                            "lyrics_master_prompt": "Sen profesyonel bir şarkı sözü yazarı ve müzik prodüktörüsün...",
                            "art_master_prompt": "Create a high-quality YouTube music thumbnail..."
                        }, f, indent=4)
                except: pass
        return prompts_path

    def get_data_paths(self):
        docs_dir = os.path.expanduser("~/Documents/MusicBot_Workspace")
        os.makedirs(docs_dir, exist_ok=True)
        
        input_path = os.path.join(docs_dir, "input_songs.xlsx")
        output_path = os.path.join(docs_dir, "output_results.xlsx")
        output_dir = os.path.join(docs_dir, "output_media")
        prompts_path = os.path.join(docs_dir, "prompts.json")
        
        # Init prompts.json if missing
        if not os.path.exists(prompts_path):
            # Try to find default prompts in bundle or source
            bundle_prompts = os.path.join(bundle_dir, "data", "prompts.json")
            
            if os.path.exists(bundle_prompts):
                import shutil
                try:
                    shutil.copy(bundle_prompts, prompts_path)
                except Exception as e:
                    logger.error(f"Failed to copy prompts: {e}")
            else:
                # Fallback: Create with basic defaults if bundle also missing
                try:
                    import json
                    with open(prompts_path, "w", encoding="utf-8") as f:
                        json.dump({
                            "lyrics_master_prompt": "Sen profesyonel bir şarkı sözü yazarı ve müzik prodüktörüsün...",
                            "art_master_prompt": "Create a high-quality YouTube music thumbnail..."
                        }, f, indent=4)
                except Exception as e:
                    logger.error(f"Failed to create default prompts.json: {e}")

        # Init Input if missing
        if not os.path.exists(input_path):
            try:
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.append(["id", "prompt", "style"])
                wb.save(input_path)
            except Exception as e:
                logger.error(f"Failed to create default input_songs.xlsx: {e}")
            
        return input_path, output_path, output_dir

    def open_xlsx(self, type="input"):
        input_path, output_path, _ = self.get_data_paths()
        path = input_path if type == "input" else output_path
        if os.path.exists(path):
            os.system(f"open '{path}'")
        else:
            messagebox.showinfo("Wait", "File not created yet.")

    def open_image_folder(self):
        _, output_path, _ = self.get_data_paths()
        img_dir = os.path.join(os.path.dirname(output_path), "images")
        if not os.path.exists(img_dir):
            os.makedirs(img_dir, exist_ok=True)
        os.system(f"open '{img_dir}'")

    def open_chrome_profile(self):
        """Launches a headless=False browser for manual login."""
        
        def _launch():
            try:
                # 1. Notify User via Log
                logger.info(self.t("log_chrome_start"))
                logger.info(self.t("log_wait_chrome"))
                                    
                # 2. Start
                # Store in self to prevent Garbage Collection from closing it immediately
                self.chrome_session = BrowserController(headless=False)
                self.chrome_session.start()
                
                logger.info(self.t("log_chrome_success"))
                logger.info(self.t("log_chrome_profile").format(path=self.chrome_session.user_data_dir))
                logger.info(self.t("log_chrome_login"))
                logger.info(self.t("log_chrome_close"))
                
                # 3. Open Tabs
                try:
                    page = self.chrome_session.pages.get("default")
                    if page:
                        page.goto("https://suno.com/create")
                        # New tab for gemini
                        p2 = self.chrome_session.context.new_page()
                        p2.goto("https://gemini.google.com/app")
                except Exception as e:
                    logger.warning(f"Failed to open browser tabs: {e}")
                
            except Exception as e:
                import traceback
                err = traceback.format_exc()
                logger.error(f"❌ Failed to open browser: {e}")
                logger.error(err)

        # Threads
        threading.Thread(target=_launch, daemon=True).start()

    def reset_chrome_profile(self):
        """Total reset of the Chrome profile to clear all cookies, cache, and history."""
        try:
            # 1. Close active session if any
            if hasattr(self, "chrome_session") and self.chrome_session:
                try:
                    logger.info("Stopping active browser session for reset...")
                    self.chrome_session.stop()
                    self.chrome_session = None
                    time.sleep(2) # Wait for file handles to release
                except: pass
            
            # 2. Delete profile folder
            workspace = os.path.expanduser("~/Documents/MusicBot_Workspace")
            profile_path = os.path.join(workspace, "chrome_profile")
            
            if os.path.exists(profile_path):
                import shutil
                # Using rmtree for a truly fresh start (no remnants)
                logger.info(f"Removing profile directory: {profile_path}")
                shutil.rmtree(profile_path, ignore_errors=True)
                
                # Double check - if still exists (locked), try renaming it as fallback
                if os.path.exists(profile_path):
                    timestamp = int(time.time())
                    backup_path = os.path.join(workspace, f"chrome_profile_locked_{timestamp}")
                    os.rename(profile_path, backup_path)
                
                logger.info(self.t("log_chrome_reset_success"))
                messagebox.showinfo(self.t("success"), self.t("log_chrome_reset_success"))
            else:
                logger.info("No chrome profile found to reset.")
                messagebox.showinfo(self.t("info"), "Zaten mevcut bir profil bulunamadı, tertemiz bir başlangıç için her şey hazır.")
                
        except Exception as e:
            logger.error(self.t("log_chrome_reset_fail").format(error=str(e)))
            messagebox.showerror(self.t("error_title"), self.t("log_chrome_reset_fail").format(error=str(e)))

    def disable_buttons(self):
        self.btn_run.config(state="disabled")
        self.btn_stop.config(state="normal")

    def enable_buttons(self):
        self.root.after(0, lambda: self.btn_run.config(state="normal"))
        self.root.after(0, lambda: self.btn_stop.config(state="disabled"))
        self.root.after(0, lambda: self.status_var.set(self.t("ready")))
        self.root.after(0, lambda: self.set_badge(self.t("badge_idle"), "#888888"))
        self.root.after(0, lambda: self.load_project_data()) # Auto refresh

    def _run_process_sequential_mode(self, target_ids, project_file, output_media, workspace, start_time, progress_callback, force_update):
        """Original flow: Process each song 1-by-1 through all selected steps."""
        total_songs = len(target_ids)
        self.video_render_queue = [] # Queue for parallel rendering (Pass 2) will be populated here
        
        for idx, song_id in enumerate(target_ids):
            if self.stop_requested:
                logger.info(self.t("log_halted"))
                break
                
            # Update status
            song_data = self.all_songs.get(song_id, {})
            title = song_data.get("title", "Unknown")
            title_short = title[:50] + ".." if len(title) > 50 else title
            self.root.after(0, lambda id=song_id, t=title_short: self.current_song_var.set(f"{self.t('working_on')} {id} ({t})"))
            
            # Calculate ETA
            elapsed = time.time() - start_time
            avg_time = elapsed / idx if idx > 0 else 0
            remaining = total_songs - idx
            eta_val = ""
            if idx > 0:
                eta_seconds = int(avg_time * remaining)
                hrs = eta_seconds // 3600
                mins = (eta_seconds % 3600) // 60
                secs = eta_seconds % 60
                time_str = f"{hrs:02d}:{mins:02d}:{secs:02d}" if hrs > 0 else f"{mins:02d}:{secs:02d}"
                eta_val = f" | {self.t('eta_label').format(time=time_str)}"

            self.root.after(0, lambda: self.status_var.set(f"{self.t('processing')} ({idx+1}/{total_songs}){eta_val}"))
            self.root.after(0, lambda: self.set_badge(self.t("badge_active"), "#00aa00"))
            
            # Start browser ONLY IF NEEDED
            song_browser = None
            self.active_browser = None
            
            # Global Humanizer State
            global_human = self.config.get("humanizer_enabled", True)

            try:
                # Get specific steps for THIS song
                s_steps = self.song_steps.get(song_id)
                if s_steps is None:
                    s_steps = [
                        self.var_run_lyrics.get(),
                        self.var_run_music.get(),
                        self.var_run_art_prompt.get(),
                        self.var_run_art_image.get(),
                        self.var_run_video.get()
                    ]
                
                # Ensure length
                while len(s_steps) < 5: s_steps.append(False)

                # Determine if browser is actually needed
                browser_needed = s_steps[0] or s_steps[1] or s_steps[2] # Lyrics, Music, or Art Prompt
                
                if browser_needed:
                    from browser_controller import BrowserController
                    h_conf = {
                        "level": self.config.get("humanizer_level", "MEDIUM"),
                        "speed": self.config.get("humanizer_speed", 1.0),
                        "retries": self.config.get("humanizer_retries", 1),
                        "adaptive": self.config.get("humanizer_adaptive", True)
                    }
                    song_browser = BrowserController(headless=False, humanizer_config=h_conf)
                    song_browser.start()
                    self.active_browser = song_browser
                
                # --- Step 1: Lyrics ---
                if s_steps[0] and not self.stop_requested and song_browser:
                    # Phase-based Humanizer Activation
                    song_browser.humanizer_enabled = global_human and self.config.get("h_activate_gemini", True)
                    
                    from gemini_prompter import GeminiPrompter
                    gemini = GeminiPrompter(
                        project_file=project_file, 
                        browser=song_browser,
                        use_gemini_lyrics=self.config.get("gemini_lyrics", True),
                        generate_visual=self.config.get("gemini_visual", True),
                        generate_video=self.config.get("gemini_video", False),
                        generate_style=self.config.get("gemini_style", False),
                        startup_delay=self.config.get("startup_delay", 5),
                        language=self.config.get("target_language", "Turkish")
                    )
                    gemini.run(target_ids=[song_id], progress_callback=progress_callback, force_update=force_update)
                
                # --- Step 2: Music ---
                if s_steps[1] and not self.stop_requested and song_browser:
                    # Phase-based Humanizer Activation
                    song_browser.humanizer_enabled = global_human and self.config.get("h_activate_suno", True)
                    
                    from suno_generator import SunoGenerator
                    suno = SunoGenerator(
                        project_file=project_file, # Unified Path
                        output_dir=output_media,
                        delay=self.config.get("suno_delay", 15),
                        startup_delay=self.config.get("startup_delay", 5),
                        browser=song_browser,
                        audio_influence=self.config.get("audio_influence", 25) if self.config.get("audio_influence_enabled") else "Default",
                        vocal_gender=self.config.get("vocal_gender", "Default") if self.config.get("vocal_gender_enabled") else "Default",
                        weirdness=self.config.get("weirdness", 50) if self.config.get("weirdness_enabled") else "Default",
                        style_influence=self.config.get("style_influence", 50) if self.config.get("style_influence_enabled") else "Default",
                        lyrics_mode=self.config.get("lyrics_mode", "Default") if self.config.get("lyrics_mode_enabled") else "Default",
                        persona_link=self.config.get("suno_personas", {}).get(self.config.get("suno_active_persona", ""), "") if self.config.get("suno_persona_link_enabled") else ""
                    )
                    suno.run(target_ids=[song_id], progress_callback=progress_callback, force_update=force_update)
                
                # --- Step 3: Art (Prompts & Images) ---
                if (s_steps[2] or s_steps[3]) and not self.stop_requested:
                    from gemini_prompter import GeminiPrompter
                    gemini_art = GeminiPrompter(
                        project_file=project_file, # Unified Path
                        output_dir=output_media,
                        browser=song_browser if s_steps[2] else None, # Only needs browser for prompts
                        startup_delay=self.config.get("startup_delay", 5),
                        language=self.config.get("target_language", "Turkish")
                    )
                    
                    if s_steps[2] and not self.stop_requested and song_browser:
                        gemini_art.generate_art_prompts(target_ids=[song_id], progress_callback=progress_callback)
                    
                    if s_steps[3] and not self.stop_requested:
                        gemini_art.generate_art_images(target_ids=[song_id], progress_callback=progress_callback)

                # --- Step 4: Video Generation (Consolidated) ---
                if len(s_steps) > 4 and s_steps[4] and not self.stop_requested:
                    self._prepare_video_task(song_id, output_media, workspace, progress_callback)
                self.active_browser = None
            except Exception as e:
                logger.error(f"Error processing {song_id}: {e}")
                progress_callback(song_id, "Error in flow ❌")
                self.active_browser = None
            finally:
                # Safe Shutdown for Phase 1-3
                try:
                    time.sleep(1)
                    if song_browser:
                        song_browser.stop()
                except: pass
                self.active_browser = None

    def _prepare_video_task(self, song_id, output_media, workspace, progress_callback=None):
        """Helper to prepare a video task for a single song and add it to self.video_render_queue."""
        found_audio = []
        all_materials = [] # Track all found for not_used
        try:
            # Selection logic: _1, _2 or Both
            selection_mode = self.config.get("video_selection_mode", "Both")
            # Map localization to internal suffixes
            suffix_map = {
                self.t("v_mode_1"): "_1",
                self.t("v_mode_2"): "_2",
                "Only _1": "_1",
                "Only _2": "_2"
            }
            target_suffix = suffix_map.get(selection_mode)

            for f in os.listdir(output_media):
                if f.startswith(f"{song_id}_") or f.startswith(f"{song_id}."):
                    if f.lower().endswith((".mp3", ".wav", ".png", ".jpg", ".jpeg")):
                        all_materials.append(f)
                        
                if f.startswith(f"{song_id}_") and f.lower().endswith((".mp3", ".wav")):
                    # Filter by selection mode if applicable
                    if not target_suffix or f.lower().endswith(f"{target_suffix.lower()}.mp3") or f.lower().endswith(f"{target_suffix.lower()}.wav"):
                        found_audio.append(f)
            if os.path.exists(os.path.join(output_media, f"{song_id}.mp3")):
                if not target_suffix: # Generic file only if 'Both' or no specific suffix requested
                    found_audio.append(f"{song_id}.mp3")
        except: pass
        found_audio = sorted(list(set(found_audio)))
        used_in_tasks = []

        if found_audio:
            v_params = {
                "effect_types": self.config.get("video_effects", [self.config.get("video_effect", "None")]),
                "fps": int(self.config.get("video_fps", 30)),
                "resolution": self.config.get("video_resolution", self.t("video_res_shorts")),
                "intensity": int(self.config.get("video_intensity", 1.0) * 50) # Scale 1.0 to 50
            }
            
            for aud_file in found_audio:
                if self.stop_requested: break
                aud_full_path = os.path.join(output_media, aud_file)
                aud_base = os.path.splitext(aud_file)[0]
                parts = aud_base.split("_")
                seq_name = None
                if len(parts) >= 2:
                    last_part = parts[-1]
                    if last_part.isdigit():
                        seq_name = f"{song_id}_{last_part}"

                if not hasattr(self, "video_render_queue"): self.video_render_queue = []

                # Find matching image logic duplicated from sequential... 
                # To save space, we assume it's same logic.
                img_path = None
                search_dirs = []
                assets_folder = self.config.get("video_assets_path")
                if assets_folder and os.path.exists(assets_folder):
                    search_dirs.append(assets_folder)
                search_dirs.append(output_media) 
                
                for s_dir in search_dirs:
                    for ext in [".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"]:
                        if os.path.exists(os.path.join(s_dir, f"{aud_base}{ext}")):
                            img_path = os.path.join(s_dir, f"{aud_base}{ext}"); break
                        if seq_name and os.path.exists(os.path.join(s_dir, f"{seq_name}{ext}")):
                            img_path = os.path.join(s_dir, f"{seq_name}{ext}"); break
                        if os.path.exists(os.path.join(s_dir, f"{song_id}{ext}")):
                            img_path = os.path.join(s_dir, f"{song_id}{ext}"); break
                    if img_path: break
                
                if img_path:
                    video_out_dir = os.path.join(output_media, "videos")
                    if self.config.get("video_output_mode") == "custom":
                        video_out_dir = self.config.get("video_custom_output_path") or os.path.join(workspace, "Output_Videos")
                    if not os.path.exists(video_out_dir): os.makedirs(video_out_dir, exist_ok=True)
                    
                    self.video_render_queue.append({
                        "rid": song_id,
                        "audio_path": aud_full_path,
                        "image_path": img_path,
                        "output_dir": video_out_dir,
                        "profile_dir": output_media,
                        "output_filename": f"{aud_base}.mp4",
                        "params": v_params
                    })
                    used_in_tasks.append(aud_file)
                    used_in_tasks.append(os.path.basename(img_path))
        
        # Move Unused
        try:
            not_used_dir = os.path.join(output_media, "not_used")
            for mat in all_materials:
                if mat not in used_in_tasks:
                    if not os.path.exists(not_used_dir): os.makedirs(not_used_dir, exist_ok=True)
                    shutil.move(os.path.join(output_media, mat), os.path.join(not_used_dir, mat))
        except Exception as ne:
             logger.warning(f"Failed to move unused materials for {song_id}: {ne}")

    def _run_process_batch_mode(self, target_ids, project_file, output_media, workspace, start_time, progress_callback, force_update):
        """Batch executed flow: Lyrics(All) -> Suno_Batch(All) -> Art(All) -> Video(All)"""
        
        def get_song_steps(sid):
            return self.song_steps.get(sid) or [
                self.var_run_lyrics.get(),
                self.var_run_music.get(),
                self.var_run_art_prompt.get(),
                self.var_run_art_image.get(),
                self.var_run_video.get()
            ]

        try:
            # 1. Establish SINGLE Browser Session for Phases 1 & 2 & 3
            # We use one browser session for everything to avoid startups/shutdowns
            from browser_controller import BrowserController
            h_conf = {
                "level": self.config.get("humanizer_level", "MEDIUM"),
                "speed": self.config.get("humanizer_speed", 1.0),
                "retries": self.config.get("humanizer_retries", 1),
                "adaptive": self.config.get("humanizer_adaptive", True)
            }
            batch_browser = BrowserController(headless=False, humanizer_config=h_conf)
            batch_browser.start()
            self.active_browser = batch_browser
            global_human = self.config.get("humanizer_enabled", True)
            
            # --- PHASE 1: LYRICS & PREP (Gemini) ---
            gemini_ids = [id for id in target_ids if get_song_steps(id)[0]] # Step 1 enabled
            if gemini_ids:
                logger.info(f"Batch Phase 1: Gemini Lyrics ({len(gemini_ids)} songs)")
                batch_browser.humanizer_enabled = global_human and self.config.get("h_activate_gemini", True)
                
                from gemini_prompter import GeminiPrompter
                gemini = GeminiPrompter(
                    project_file=project_file, 
                    browser=batch_browser,
                    use_gemini_lyrics=self.config.get("gemini_lyrics", True),
                    generate_visual=self.config.get("gemini_visual", True),
                    generate_video=self.config.get("gemini_video", False),
                    generate_style=self.config.get("gemini_style", False),
                    startup_delay=self.config.get("startup_delay", 5),
                    language=self.config.get("target_language", "Turkish")
                )
                # Gemini doesn't have internal batch support yet, so we loop but REUSE browser
                for idx, song_id in enumerate(gemini_ids):
                    if self.stop_requested: break
                    progress_callback(song_id, "Gemini İşleniyor... ✍️")
                    gemini.run(target_ids=[song_id], progress_callback=progress_callback, force_update=force_update)
            
            # --- PHASE 2: SUNO BATCH (Gen & Download) ---
            suno_ids = [id for id in target_ids if get_song_steps(id)[1]] # Step 2 enabled
            if suno_ids and not self.stop_requested:
                logger.info(f"Batch Phase 2: Suno Batch ({len(suno_ids)} songs)")
                batch_browser.humanizer_enabled = global_human and self.config.get("h_activate_suno", True)
                
                from suno_generator import SunoGenerator
                suno = SunoGenerator(
                    project_file=project_file, 
                    output_dir=output_media,
                    delay=self.config.get("suno_delay", 15),
                    startup_delay=self.config.get("startup_delay", 5),
                    browser=batch_browser,
                    audio_influence=self.config.get("audio_influence", 25) if self.config.get("audio_influence_enabled") else "Default",
                    vocal_gender=self.config.get("vocal_gender", "Default") if self.config.get("vocal_gender_enabled") else "Default",
                    weirdness=self.config.get("weirdness", 50) if self.config.get("weirdness_enabled") else "Default",
                    style_influence=self.config.get("style_influence", 50) if self.config.get("style_influence_enabled") else "Default",
                    lyrics_mode=self.config.get("lyrics_mode", "Default") if self.config.get("lyrics_mode_enabled") else "Default",
                    persona_link=self.config.get("suno_personas", {}).get(self.config.get("suno_active_persona", ""), "") if self.config.get("suno_persona_link_enabled") else ""
                )
                # Use the new Batch Method with OP MODE!
                op_mode = self.config.get("suno_batch_op_mode", "full")
                logger.info(f"Batch Suno Op Mode: {op_mode}")
                suno.run_batch(target_ids=suno_ids, progress_callback=progress_callback, force_update=force_update, op_mode=op_mode)

            # --- PHASE 3: ART (Prompts & Images) ---
            art_p_ids = [id for id in target_ids if get_song_steps(id)[2]] # Step 3 enabled
            art_i_ids = [id for id in target_ids if get_song_steps(id)[3]] # Step 4 enabled
            
            if (art_p_ids or art_i_ids) and not self.stop_requested:
                logger.info("Batch Phase 3: Art Generation")
                from gemini_prompter import GeminiPrompter
                gemini_art = GeminiPrompter(
                    project_file=project_file,
                    output_dir=output_media,
                    browser=batch_browser, 
                    startup_delay=self.config.get("startup_delay", 5),
                    language=self.config.get("target_language", "Turkish")
                )
                
                # Prompts via Browser
                if art_p_ids:
                    for song_id in art_p_ids:
                        if self.stop_requested: break
                        gemini_art.generate_art_prompts(target_ids=[song_id], progress_callback=progress_callback)
                
                # Images (Local, but using same logical flow)
                if art_i_ids:
                    for song_id in art_i_ids:
                        if self.stop_requested: break
                        gemini_art.generate_art_images(target_ids=[song_id], progress_callback=progress_callback)

            # Clean up browser
            batch_browser.stop()
            self.active_browser = None

            # --- PHASE 4: VIDEO PREP & QUEUE ---
            video_ids = [id for id in target_ids if get_song_steps(id)[4]] # Step 5 enabled
            if video_ids and not self.stop_requested:
                self.video_render_queue = []
                for song_id in video_ids:
                    self._prepare_video_task(song_id, output_media, workspace, progress_callback)

        except Exception as e:
            logger.error(f"Batch Mode Error: {e}")
            messagebox.showerror(self.t("error"), str(e))
        finally:
            if self.active_browser:
                try: self.active_browser.stop()
                except: pass
                self.active_browser = None

    def load_data(self):
        # Dummy load_data for the finally block
        pass

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = MusicBotGUI(root)
        root.mainloop()
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        # Log to console
        print(f"CRITICAL STARTUP ERROR:\n{error_msg}")
        # Log to crash report file
        try:
            ws_path = os.path.expanduser("~/Documents/MusicBot_Workspace")
            os.makedirs(ws_path, exist_ok=True)
            with open(os.path.join(ws_path, "crash_report.txt"), "w", encoding="utf-8") as f:
                f.write(f"Timestamp: {time.ctime()}\n")
                f.write(error_msg)
        except Exception as file_e:
            print(f"Failed to write crash report: {file_e}")
        sys.exit(1)
