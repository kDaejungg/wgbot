[English](README.md) | [Türkçe](README.tr.md)

# WGBot (v1.1.1)

Slash (eğik çizgi) komutlarını destekleyen; yasaklama, zamanaşımı, uyarı, seviye sistemi, ses yönetimi ve daha fazlasını içeren açık kaynaklı bir Discord moderasyon botu. Herhangi bir konfigürasyon dosyasına dokunmadan tamamen Discord üzerinden yapılandırılır.

## ⚠️ Botu sadece sunucunuza eklemek istiyorsanız, aşağıdaki linki kullanın ve kurulum adımlarını atlayın:[![Discord'a Davet Et](https://img.shields.io/badge/Discord-Add_to_Server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/oauth2/authorize?client_id=1485221526084128910&permissions=8&integration_type=0&scope=bot)

-----

## ✨ Özellikler

### 🔨 Moderasyon

  - **Yasaklama, Atma ve Yasak Kaldırma:** Otomatik hiyerarşi kontrolü ile üyeleri yönetin.
  - **Zamanaşımı (Timeout):** Üyeleri belirli bir süre boyunca susturun.
  - **Uyarı Sistemi:** Otomatik DM bildirimi ve kalıcı uyarı kayıtları.
  - **Toplu Mesaj Silme:** Otomatik silinen onay mesajı ile kanal temizliği.
  - **Kilit Açma/Kapatma:** Kanalları anında kilitleyin veya açın.
  - **Yavaş Mod:** Kanal bazlı mesaj gönderim hızı ayarı.

### 🔊 Ses

  - **Seste Sustur/Aç:** Üyeleri sesli kanallarda sunucu genelinde susturun veya açın.
  - **Taşı:** Üyeleri sesli kanallar arasında taşıyın.

### 🏷️ Roller

  - **Rol Ekle/Çıkar:** Hiyerarşi doğrulaması ile üyelerin rollerini yönetin.

### 📁 Kanallar

  - **Kanal Oluşturma:** Slash komutu ile anında metin veya ses kanalı oluşturun.

### ℹ️ Bilgi

  - **Kullanıcı Bilgisi:** Katılım tarihi, roller, hesap yaşı ve daha fazlası.
  - **Avatar:** Herhangi bir üyenin profil resmini görüntüleyin.
  - **Sunucu Bilgisi:** Üye sayısı, takviye seviyesi, oluşturma tarihi vb.
  - **Rol Listesi:** Sunucudaki tüm rollere hızlıca göz atın.

### ⭐ Seviye & XP

  - Mesaj başına **15–25 XP** kazancı (spam önlemek için 60 saniye bekleme süresi).
  - Kanal içi **seviye atlama duyuruları**.
  - **Rol Ödülleri:** Belirli seviyelere ulaşıldığında otomatik rol atama.
  - `/rank` ve `/leaderboard` komutları.

### 💬 Otomatik Yanıt

  - Belirli mesajlar tarafından tetiklenen **otomatik yanıtlar** oluşturun.
  - **Tetikleyici başına birden fazla yanıt:** Bot rastgele birini seçer.
  - Virgülle ayırarak tek seferde birden fazla yanıt ekleme özelliği.

### 🎥 YouTube Bildirimleri

  - Sunucu başına **birden fazla YouTube kanalına** abone olun.
  - Özel bir kanala gönderilen, embed içeren ve isteğe bağlı rol etiketlemeli bildirimler.
  - Kolay yönetim için **özel etiketlerle** tanımlanır.
  - RSS aracılığıyla her **5 dakikada bir** kontrol eder (API anahtarı gerektirmez).

### 🎲 Eğlence

  - **Zar Atma:** Özelleştirilebilir kenar sayısına sahip zar komutu.

### ⚙️ Kurulum (Setup)

  - Özelleştirilebilir metin ve üye etiketleme içeren **hoş geldin mesajları**.
  - Üye katıldığında **otomatik rol** atama.
  - Tüm ayarlar **tamamen Discord üzerinden** yapılandırılır.

-----

# Kurulum

İşletim sisteminize uygun adımları takip edin.

## Konfigürasyon

Kurulum bölümünün ilk adımını tamamladıktan sonra şu adımları izleyin:

Botun çalışması için bir **Discord Bot Token** gereklidir. Nasıl alacağınızı bilmiyorsanız, [Discord Developer Portal](https://discord.com/developers/applications) adresine gidin, bir uygulama oluşturun ve **Bot** sekmesinden tokeninizi kopyalayın.

### Adım Adım Token Kurulumu:

1.  **Gizli Dosyaları Göster:**

      - **Windows:** Klasörde "Görünüm" sekmesine tıklayın ve "Gizli Öğeler" kutucuğunu işaretleyin.
      - **Linux / macOS:** Klasör içinde `.env` dosyasını görmek için `Ctrl + H` tuşlarına basın.

2.  **Tokeni Yapıştırın:**

      - `.env` dosyasını Not Defteri veya herhangi bir metin düzenleyici ile açın.
      - `DISCORD_TOKEN=` kısmını kendi tokeninizle değiştirin: `DISCORD_TOKEN=tokeniniz_buraya`
      - Dosyayı kaydedip kapatın.

> Diğer tüm ayarlar (hoş geldin kanalı, oto-rol vb.) doğrudan Discord içinden `/set-welcome-channel`, `/set-welcome-message` ve `/set-auto-role` komutları ile yapılır. Dosya düzenlemeye gerek yoktur.

### Privileged Intents (Ayrıcalıklı Niyetler) Etkinleştirme

[Discord Developer Portal](https://discord.com/developers/applications) adresine gidin, uygulamanızı seçin, **Bot** sekmesine tıklayın ve şunları etkinleştirin:

  - ✅ Server Members Intent
  - ✅ Message Content Intent

-----

## Linux

Linux'ta Python genellikle yüklü gelir. Terminalinizi açın ve şu adımları izleyin:

1.  **Depoyu kopyalayın:**

    ```bash
    git clone https://github.com/kDaejungg/wgbot.git
    ```

    ⚠️ DEVAM ETMEDEN ÖNCE YUKARIDAKİ KONFİGÜRASYON ADIMLARINI TAMAMLAYIN

    ```bash
    cd wgbot
    ```

2.  **Sanal ortam (venv) oluşturun:**

    ```bash
    python3 -m venv venv
    ```

3.  **Sanal ortamı aktifleştirin:**

    ```bash
    source venv/bin/activate
    ```

4.  **Gereksinimleri yükleyin:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Botu çalıştırın:**

    ```bash
    python3 bot.py
    ```

-----

## Windows

PowerShell veya Komut İstemi (CMD) kullanabilirsiniz. Python'un sistem yoluna (PATH) eklendiğinden emin olun.

1.  **Depoyu kopyalayın:**

    ```powershell
    git clone https://github.com/kDaejungg/wgbot.git
    ```

    ⚠️ DEVAM ETMEDEN ÖNCE YUKARIDAKİ KONFİGÜRASYON ADIMLARINI TAMAMLAYIN

    ```powershell
    cd wgbot
    ```

2.  **Sanal ortam (venv) oluşturun:**

    ```powershell
    python -m venv venv
    ```

3.  **Sanal ortamı aktifleştirin:**

    ```powershell
    .\venv\Scripts\activate
    ```

4.  **Gereksinimleri yükleyin:**

    ```powershell
    pip install -r requirements.txt
    ```

5.  **Botu çalıştırın:**

    ```powershell
    python bot.py
    ```

-----

## macOS

Mac kullanıcıları Terminal uygulamasını kullanarak şu adımları izleyebilir:

1.  **Depoyu kopyalayın:**

    ```bash
    git clone https://github.com/kDaejungg/wgbot.git
    ```

    ⚠️ DEVAM ETMEDEN ÖNCE YUKARIDAKİ KONFİGÜRASYON ADIMLARINI TAMAMLAYIN

    ```bash
    cd wgbot
    ```

2.  **Sanal ortam (venv) oluşturun:**

    ```bash
    python3 -m venv venv
    ```

3.  **Sanal ortamı aktifleştirin:**

    ```bash
    source venv/bin/activate
    ```

4.  **Gereksinimleri yükleyin:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Botu çalıştırın:**

    ```bash
    python3 bot.py
    ```

-----

## Botu Sunucunuza Ekleme

Botu çalıştırdıktan sonra sunucunuza davet etmek için şu adımları izleyin:

### 1\. OAuth2 Bağlantısı Oluşturun

1.  **[Discord Developer Portal](https://discord.com/developers/applications)**'a gidin ve uygulamanızı seçin.
2.  Sol menüde **OAuth2** → **URL Generator** seçeneğine tıklayın.
3.  **Scopes** altında şunları işaretleyin:
      - [x] `bot`
      - [x] `applications.commands` (Slash komutları için gereklidir)

### 2\. Gerekli İzinleri Seçin

**Bot Permissions** altında şu izni işaretleyin:

✅ Administrator (Yönetici)

### 3\. Davet Edin

4.  Sayfanın altındaki **Generated URL** bağlantısını kopyalayın.
5.  Tarayıcınıza yapıştırın ve botu sunucunuza davet edin.

> **⚠️ Not:** Botu ekledikten sonra slash komutları görünmüyorsa, Discord istemcinizi yeniden başlatın veya botun "Uygulama Komutlarını Kullan" iznine sahip olduğundan emin olun.

-----

## 📂 Dosya Yapısı

```
WGBot/
├── bot.py             # Ana bot motoru, tüm modülleri (cog) otomatik yükler
├── config.py           # Token yükleyici ve ayar yöneticisi
├── settings.json       # Kaydedilmiş bot yapılandırması
├── about.json          # Bot kimlik bilgileri (versiyon, geliştirici)
├── requirements.txt    # Gerekli Python kütüphaneleri
├── .env                # Bot tokeniniz (asla paylaşmayın)
├── .gitignore          # Token ve gereksiz dosyaların GitHub'a yüklenmesini önler
├── data/
│   ├── warns.json      # Uyarı kayıtları (otomatik oluşturulur)
│   ├── ranks.json      # XP ve seviye verileri (otomatik oluşturulur)
│   ├── levelroles.json # Seviye rol ödülleri (otomatik oluşturulur)
│   ├── autoreplies.json# Otomatik yanıt tetikleyicileri (otomatik oluşturulur)
│   └── youtube.json    # YouTube bildirim abonelikleri (otomatik oluşturulur)
└── cogs/
    ├── moderation.py   # yasaklama, atma, susturma, silme, kilitleme vb.
    ├── warns.py        # uyarı komutları ve yönetimi
    ├── voice.py        # sesli kanal susturma ve taşıma
    ├── roles.py        # rol ekleme/çıkarma
    ├── channels.py     # kanal oluşturma
    ├── info.py         # kullanıcı, sunucu, avatar bilgileri
    ├── rank.py         # seviye sistemi, sıralama ve rol ödülleri
    ├── autoreply.py    # otomatik yanıt ekleme/silme/listeleme
    ├── youtube.py      # youtube bildirimi ekleme/silme/listeleme
    ├── fun.py          # eğlence komutları
    ├── welcome.py      # hoş geldin mesajları ve oto-rol
    ├── setup.py        # sunucu ayarları komutları
    ├── about.py        # bot hakkında bilgisi
    └── help.py         # yardım menüsü
```

## ⚠️ Önemli Güvenlik Notu

`.env` dosyanızı asla başkalarıyla paylaşmayın veya halka açık bir depoya (repository) göndermeyin. `.gitignore` dosyası bunu engellemek için yapılandırılmıştır, ancak her zaman kontrol etmenizde fayda var.

-----

*Enes Ramazan Whitelineage tarafından yapıldı.*

#### İletişim ve Geri Bildirim: [Discord](https://discord.gg/vV8gEpHDXH) & [Reddit](https://www.reddit.com/r/WhitelineageDEV/)
