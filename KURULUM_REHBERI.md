# MusicBot Pro - Kurulum ve Kullanım Rehberi

MusicBot Pro'yu başka bir bilgisayara en güncel haliyle kurmak için aşağıdaki yöntemlerden birini seçebilirsiniz.

---

## 🚀 Yöntem 1: GitHub'dan Otomatik Kurulum (Önerilen)

Hiçbir şey kopyalamadan, tek bir komutla en güncel sürümü indirip kurabilirsiniz.

### 🍎 macOS İçin:
1. **Terminal**'i açın.
2. Şu komutu yapıştırın (bu komut uygulamayı **İndirilenler (Downloads)** klasörüne kurar):
```bash
cd ~/Downloads && if [ -d "MusicBot-Pro" ]; then cd MusicBot-Pro && git pull; else git clone https://github.com/huskobro/MusicBot-Pro.git && cd MusicBot-Pro; fi && bash mac_install.sh
```
勾

### 🪟 Windows İçin:
1. **PowerShell**'i açın.
2. Şu komutu yapıştırın (bu komut uygulamayı **İndirilenler (Downloads)** klasörüne kurar):
```powershell
cd $env:USERPROFILE\Downloads; if (Test-Path "MusicBot-Pro") { cd MusicBot-Pro; git pull } else { git clone https://github.com/huskobro/MusicBot-Pro.git; cd MusicBot-Pro }; .\win_install.bat
```
勾

---

## 🛠️ Yöntem 2: Manuel Paketleme (Kodlar Elinizdeyse)

Eğer dosyalar zaten bilgisayarınızdaysa:

### macOS:
Klasör içinde `bash build_app.sh` komutunu çalıştırın. `dist/MusicBot.app` hazır olacaktır.

### Windows:
Klasör içindeki `build_windows.bat` dosyasına çift tıklayın. `dist/MusicBotPro.exe` hazır olacaktır.

---

## 📂 Ortak Gereksinimler (Tüm Cihazlar İçin)

Uygulamanın çalışması için bilgisayarda şunların olması gerekir:

1.  **Google Chrome:** Uygulama otomasyon için yüklü olan Chrome'u kullanır.
2.  **Git & Python:** Otomatik kurulum ve çalışma için gereklidir.

---

## 🚀 Hızlı Başlangıç

1.  Uygulamayı çalıştırın.
2.  `⚙️ Ayarlar` kısmına gidin ve `UI Language` kısmından **Turkish** seçip kaydedin. Uygulamayı kapatıp açın.
3.  `✨ Yeni Proje` butonuna basarak bir Excel dosyası oluşturun.
4.  Şarkı listenizi Excel'e ekleyin ve `▶ MOTORU BAŞLAT` butonuna basın.

---
