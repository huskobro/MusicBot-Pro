@echo off
echo MusicBot Pro - Windows Paketleme Araci
echo --------------------------------------

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python yuklu degil veya PATH'e eklenmemis!
    echo Lutfen python.org adresinden Python kurun.
    pause
    exit /b
)

echo [1/3] Python sanal ortami hazirlaniyor...
if not exist ".venv" (
    python -m venv .venv
)
call .venv\Scripts\activate

echo [2/3] Gerekli kutuphaneler yukleniyor...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium

echo [3/4] Uygulama paketleniyor (Bu islem birkac dakika surebilir)...
python -m PyInstaller --noconfirm --clean ^
    --name "MusicBotPro" ^
    --windowed ^
    --add-data "data;data" ^
    --add-data "execution;execution" ^
    --paths "execution" ^
    --collect-all moviepy ^
    --collect-all imageio ^
    --collect-all playwright ^
    --collect-all playwright_stealth ^
    --hidden-import playwright.sync_api ^
    execution/gui_launcher.py

echo [4/4] Temizlik yapiliyor...
echo.
echo --------------------------------------
echo ISLEM TAMAMLANDI! 
echo Uygulama 'dist' klasoru icindeki 'MusicBotPro.exe' dosyasidir.
echo --------------------------------------
pause
