#!/bin/bash

# MusicBot Pro - macOS Tam Otomatik Kurulum Betigi
echo "MusicBot Pro Tam Kurulumu Basliyor..."
echo "Kurulum Dizini: $(pwd)"
echo "------------------------------------------------"

# 1. Projeyi Guncelle (Eger klasorun icindeysen sadece pull yap)
if [ -d ".git" ]; then
    echo "Mevcut klasor guncelleniyor..."
    git pull
elif [ -d "MusicBot-Pro" ]; then
    echo "MusicBot-Pro klasoru bulundu, guncelleniyor..."
    cd MusicBot-Pro
    git pull
else
    echo "Kodlar GitHub'dan indiriliyor..."
    git clone https://github.com/huskobro/MusicBot-Pro.git
    cd MusicBot-Pro
fi

# 2. Python Ortami
echo "Python sanal ortami hazirlaniyor..."
python3 -m venv .venv
source .venv/bin/activate

# 3. Bağımlılıkları yükle
echo "Gerekli tum kutuphaneler yukleniyor (bu biraz zaman alabilir)..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Tarayici bilesenlerini kur (Playwright)
echo "Tarayici bilesenleri yukleniyor..."
playwright install chromium

# 5. Uygulamayı paketle
echo "Uygulama macOS paketi (.app) haline getiriliyor..."
bash build_app.sh

echo "------------------------------------------------"
echo "KURULUM BASARIYLA TAMAMLANDI!"
echo "Uygulama: $(pwd)/dist/MusicBot.app"
echo "Simdi uygulama klasoru aciliyor..."
echo "------------------------------------------------"
open dist/
