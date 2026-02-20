@echo off
echo MusicBot Pro - Windows Tam Otomatik Kurulum Araci
echo --------------------------------------------------

:: 1. Git Kontrol
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Git yuklu degil! Lutfen git-scm.com adresinden Git kurun.
    pause
    exit /b
)

:: 2. Projeyi Guncelle (Eger klasorun icindeysen sadece pull yap)
if exist ".git" (
    echo Mevcut klasor guncelleniyor...
    git pull
) else if exist "MusicBot-Pro" (
    echo MusicBot-Pro klasoru bulundu, guncelleniyor...
    cd MusicBot-Pro
    git pull
) else (
    echo Kodlar GitHub'dan indiriliyor...
    git clone https://github.com/huskobro/MusicBot-Pro.git
    cd MusicBot-Pro
)

:: 3. Python ve venv
echo Python sanal ortami hazirlaniyor...
python -m venv .venv
call .venv\Scripts\activate

:: 4. Bağımlılıklar
echo Gerekli tum kutuphaneler yukleniyor...
pip install --upgrade pip
pip install -r requirements.txt

:: 5. Tarayici bilesenlerini kur (Playwright)
echo Tarayici bilesenleri yukleniyor...
python -m pip install playwright
python -m playwright install chromium

:: 6. Paketleme
echo Uygulama paketleniyor (Windows exe olusturuluyor)...
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

echo --------------------------------------------------
echo KURULUM BASARIYLA TAMAMLANDI!
echo Uygulama 'dist' klasoru icindeki 'MusicBotPro.exe' dosyasidir.
echo --------------------------------------------------
start dist
pause
