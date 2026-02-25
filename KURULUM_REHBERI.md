# MusicBot Pro — Kurulum ve Kullanım Rehberi

MusicBot Pro'yu yeni bir bilgisayara kurmak ve sorunsuz çalıştırmak için aşağıdaki adımları izleyin.

---

## �️ Ön Gereksinimler (Tüm Sistemler İçin)

Uygulamanın çalışması için aşağıdaki yazılımların bilgisayarınızda yüklü olması şarttır:

1.  **Google Chrome:** Güncel sürüm kurulu olmalıdır.
2.  **FFmpeg (Önerilir):** Donanım hızlandırmalı hızlı video üretimi için gereklidir.
    -   *Mac:* `brew install ffmpeg` komutuyla kurabilirsiniz.
    -   *Windows:* `ffmpeg.org` sitesinden indirip sistem PATH'ine eklemelisiniz.
3.  **Python 3.10+:** Bilgisayarınızda Python yüklü olmalıdır.

---

## 🚀 1. Kurulum Adımları

### 🍎 MacBook (macOS) İçin
1.  **Terminal** uygulamasını açın.
2.  Uygulamayı indirmek ve kurmak için şu komutu yapıştırıp Enter'a basın:
    ```bash
    cd ~/Downloads && git clone https://github.com/huskobro/MusicBot-Pro.git && cd MusicBot-Pro && bash mac_install.sh
    ```
3.  **Uygulamayı Paketlemek (App Sunumu için):**
    Uygulamayı bir `.app` dosyasına çevirmek isterseniz:
    ```bash
    bash build_app.sh
    ```
    Bu komut sonunda `dist/MusicBot.app` dosyası oluşacaktır.

### 🪟 Windows İçin
1.  **PowerShell** uygulamasını açın.
2.  Şu komutu yapıştırıp Enter'a basın:
    ```powershell
    cd $env:USERPROFILE\Downloads; git clone https://github.com/huskobro/MusicBot-Pro.git; cd MusicBot-Pro; .\win_install.bat
    ```
3.  **Uygulamayı Paketlemek (EXE Sunumu için):**
    `build_windows.bat` dosyasına çift tıklayın. `dist/MusicBot.exe` dosyanız hazır olacaktır.

---

## � 2. Tarayıcı ve Oturum Hazırlığı (Suno & Gemini)

Botun otomatik işlem yapabilmesi için Chrome profillerinizin açık olması gerekir:

1.  Uygulamayı açın ve **Settings (Ayarlar)** sekmesine gidin.
2.  **Chrome Profiles** listesinden bir profil seçin veya yeni bir isimle (Örn: `Lina_Zahara`) oluşturun.
3.  **"Open Chrome to Login"** (veya benzeri bir isimdeki butona) basın.
4.  Açılan tarayıcıda `suno.com` ve `gemini.google.com` adreslerine gidip hesaplarınıza **el ile giriş yapın.**
5.  **ÖNEMLİ:** Suno'da `/create` sayfasına girdiğinizde sağ taraftaki şarkı listesinin üzerinde **"Search clips"** yazan arama kutusunun göründüğünden emin olun. Bot bu kutuyu kullanarak şarkıları bulur.
6.  Giriş yaptıktan sonra o tarayıcıyı kapatın ve bot üzerinden **Motoru Başlat** deyin.

---

## ⚠️ 3. Sıkça Sorulan Sorular ve Çözümler

- **"Arama kutusu bulunamadı" uyarısı:** Suno sayfasında giriş yapmamış olabilirsiniz veya internet yavaş geldiği için sayfa tam yüklenmemiş olabilir. Sayfayı yenileyip girişinizi kontrol edin.
- **Mac'te "The default interactive shell is now zsh" uyarısı:** Bu bir hata değildir. Apple, yeni Mac'lerde varsayılan terminal dilini değiştirdiği için bu uyarıyı verir. Bu mesajı görmezden gelip komutu yapıştırmaya devam edebilirsiniz; kurulum normal şekilde sürecektir.
- **Mac'te "Hasarlı/Damarlı" Dosya Hatası:** Eğer `.app` dosyasını çalıştıramazsanız Terminal'e şunu yazın: `xattr -cr dist/MusicBot.app`
- **Video Üretimi Çok Yavaş:** Ayarlardan "Video Render Motoru"nu **FFmpeg** olarak seçtiğinizden emin olun (FFmpeg yüklü olmalıdır).

---

## 📈 4. Hızlı Kullanım Döngüsü
1.  **Excel Hazırla:** `Yeni Proje` butonuyla bir template oluşturun ve şarkılarınızı içine yazın.
2.  **Şarkı Seç:** Listeden işlem yapmak istediğiniz şarkıları seçin.
3.  **Başlat:** `MOTORU BAŞLAT` butonuna basın ve botun Gemini ile söz yazıp Suno'dan indirmesini izleyin!
