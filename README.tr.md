[English](README.md) | [Türkçe](README.tr.md)

# WGBot (v1.2.0)
Slash komutlarıyla çalışan açık kaynaklı bir Discord moderasyon botu. Ban, timeout, uyarı sistemi, rank, ses yönetimi, tepki rolleri, anketler ve daha fazlasını destekler. Hiçbir dosyaya dokunmadan tamamen Discord üzerinden yapılandırılır.

## ⚠️ Botu yalnızca sunucuna eklemek istiyorsan bu bağlantıyı kullanıp aşağıdaki adımları atlayabilirsin: [![Discord Davet](https://img.shields.io/badge/Discord-Sunucuya_Ekle-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/oauth2/authorize?client_id=1485221526084128910&permissions=8&integration_type=0&scope=bot)
---

## ✨ Özellikler

### 🔨 Moderasyon
- Otomatik hiyerarşi kontrolüyle **ban, kick ve unban**
- Belirli süre için **timeout**
- Otomatik DM bildirimleri ve kalıcı kayıtlarla **uyarı sistemi**
- Onay mesajının otomatik silinmesiyle **toplu mesaj silme**
- Kanalları anında **kilitleme ve kilit açma**
- Kanal bazında **yavaş mod**

### 🔊 Ses
- Ses kanalındaki üyeleri **susturma ve susturmayı kaldırma**
- Üyeleri ses kanalları arasında **taşıma**
- **Ses kanalı kullanıcı limiti**: herhangi bir ses kanalına kullanıcı kapasitesi belirleme veya kaldırma

### 🏷️ Roller
- Hiyerarşi doğrulamasıyla üyelere **rol ekleme ve çıkarma**
- **HEX rol rengi**: herhangi bir HEX koduyla rol rengi değiştirme

### 📁 Kanallar
- Slash komutla **metin veya ses kanalı oluşturma**

### ℹ️ Bilgi
- **Üye bilgisi**: katılma tarihi, roller, hesap yaşı ve daha fazlası
- **Avatar**: herhangi bir üyenin profil fotoğrafını görüntüleme
- **Sunucu bilgisi**: üye sayısı, boost seviyesi, oluşturulma tarihi ve daha fazlası
- **Rol listesi**: sunucudaki tüm roller tek bakışta

### ⭐ Rank ve XP
- Üyeler her mesajda **15–25 XP** kazanır (spam önlemek için 60 saniyelik bekleme süresi)
- Kanalda **seviye atlama duyuruları**
- **Rol ödülleri**: üyeler belirli seviyelere ulaştığında otomatik rol atama
- `/rank` ve `/leaderboard` komutları

### 💬 Otomatik Yanıt
- Belirli mesajlarla tetiklenen **otomatik yanıtlar** oluşturma
- **Tetikleyici başına birden fazla yanıt** (bot rastgele birini seçer)
- Virgülle ayırarak birden fazla yanıtı aynı anda ekleme

### 🎥 YouTube Bildirimleri
- Sunucu başına **birden fazla YouTube kanalı** aboneliği
- Bildirimler embed ve isteğe bağlı rol pingi ile belirlenen kanala gönderilir
- Kolay yönetim için **özel etiketlerle** tanımlama
- RSS aracılığıyla her **5 dakikada bir** yeni video kontrolü (API anahtarı gerekmez)

### 📊 Anket
- En fazla 9 seçenekle **tepki tabanlı anket** oluşturma
- Seçenekleri `;` ile ayır. Bot emojileri otomatik ekler

### 🎭 Tepki Rolleri
- Üyeler **bir mesaja tepki verdiğinde** otomatik olarak rol atama
- Tepki kaldırıldığında rol da kaldırılır
- Tamamen kalıcı, bot yeniden başlatılsa da çalışmaya devam eder
- `/reactionrole add`, `/reactionrole remove`, `/reactionrole list` ile yönetim

### 🎲 Eğlence
- Özelleştirilebilir taraflı **zar atma**

### ⚙️ Kurulum
- Özelleştirilebilir metin ve üye etiketiyle **karşılama mesajları**
- Üye katılımında **otomatik rol** atama
- Tüm ayarlar **tamamen Discord üzerinden** yapılandırılır

---

# Kurulum

İşletim sistemine göre adımları takip et.

## Yapılandırma
Kurulum bölümünün birinci adımını tamamladıktan sonra şu adımları izle:

Botun çalışması için bir **Discord Bot Token** gerekir. Nasıl alacağını bilmiyorsan [Discord Developer Portal](https://discord.com/developers/applications)'a git, bir uygulama oluştur ve **Bot** sekmesinden tokenını kopyala.

### Adım Adım Token Kurulumu:

1. **Gizli Dosyaları Göster:**
   - **Windows:** Klasörde "Görünüm" sekmesine tıkla ve "Gizli Öğeler"i işaretle.
   - **Linux / macOS:** Klasör içinde `Ctrl + H` tuşlarına bas ve `.env` dosyasını bul.

2. **Tokenını Yapıştır:**
   - `.env` dosyasını Notepad veya herhangi bir metin editörüyle aç.
   - `DISCORD_TOKEN=` kısmını tokenınla değiştir: `DISCORD_TOKEN=your_teken_here`
   - Kaydet ve kapat.

> Diğer tüm ayarlar (karşılama kanalı, otomatik rol) Discord'da `/set-welcome-channel`, `/set-welcome-message` ve `/set-auto-role` komutlarıyla yapılandırılır. Herhangi bir dosyayı düzenlemeye gerek yok.

### Privileged Intent'leri Etkinleştir
[Discord Developer Portal](https://discord.com/developers/applications)'a git, uygulamanı seç, **Bot** sekmesine tıkla ve şunları etkinleştir:

- ✅ Server Members Intent
- ✅ Message Content Intent

---

## Linux

Python genellikle Linux'ta önceden yüklüdür. Terminali aç ve şu adımları izle:

1. **Depoyu klonla:**
   ```bash
   git clone https://github.com/kDaejungg/wgbot.git
   ```

   ⚠️ DEVAM ETMEDEN ÖNCE YUKARIDAKİ YAPILANDIRMA ADIMLARINI TAKİP ET

   ```bash
   cd wgbot
   ```

2. **Sanal ortam oluştur:**
   ```bash
   python3 -m venv venv
   ```

3. **Sanal ortamı etkinleştir:**
   ```bash
   source venv/bin/activate
   ```

4. **Gereksinimleri yükle:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Botu çalıştır:**
   ```bash
   python3 bot.py
   ```

---

## Windows

PowerShell veya Komut İstemi (CMD) kullanabilirsin. Python'un sistem PATH'ine eklendiğinden emin ol.

1. **Depoyu klonla:**
   ```powershell
   git clone https://github.com/kDaejungg/wgbot.git
   ```

   ⚠️ DEVAM ETMEDEN ÖNCE YUKARIDAKİ YAPILANDIRMA ADIMLARINI TAKİP ET

   ```powershell
   cd wgbot
   ```

2. **Sanal ortam oluştur:**
   ```powershell
   python -m venv venv
   ```

3. **Sanal ortamı etkinleştir:**
   ```powershell
   .\venv\Scripts\activate
   ```

4. **Gereksinimleri yükle:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Botu çalıştır:**
   ```powershell
   python bot.py
   ```

---

## macOS

Mac kullanıcıları Terminal uygulamasıyla şu adımları izleyebilir:

1. **Depoyu klonla:**
   ```bash
   git clone https://github.com/kDaejungg/wgbot.git
   ```

   ⚠️ DEVAM ETMEDEN ÖNCE YUKARIDAKİ YAPILANDIRMA ADIMLARINI TAKİP ET

   ```bash
   cd wgbot
   ```

2. **Sanal ortam oluştur:**
   ```bash
   python3 -m venv venv
   ```

3. **Sanal ortamı etkinleştir:**
   ```bash
   source venv/bin/activate
   ```

4. **Gereksinimleri yükle:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Botu çalıştır:**
   ```bash
   python3 bot.py
   ```

---

## Botu Sunucuna Ekleme

Botu çalıştırdıktan sonra sunucuna davet etmek için şu adımları izle:

### 1. OAuth2 Bağlantısı Oluştur
1. **[Discord Developer Portal](https://discord.com/developers/applications)**'a git ve uygulamanı seç.
2. Sol menüden **OAuth2** → **URL Generator**'a tıkla.
3. **Scopes** altında şunları işaretle:
   - [x] `bot`
   - [x] `applications.commands` (slash komutlar için gerekli)

### 2. Gerekli İzinleri Seç
**Bot Permissions** altında şunu işaretle:

✅ Administrator

### 3. Davet Et
4. Sayfanın altındaki **Generated URL**'yi kopyala.
5. Tarayıcına yapıştır ve botu sunucuna davet et.

> **⚠️ Not:** Botu ekledikten sonra slash komutlar görünmüyorsa Discord istemcini yeniden başlat veya botun "Use Application Commands" iznine sahip olduğundan emin ol.

---

## 📂 Dosya Yapısı

```
WGBot/
├── bot.py              # Ana bot motoru, tüm cog'ları otomatik yükler
├── config.py           # Token yükleyici ve ayar yöneticisi
├── settings.json       # Kaydedilmiş bot ayarları
├── about.json          # Bot kimlik bilgileri (sürüm, geliştirici)
├── requirements.txt    # Gerekli Python kütüphaneleri
├── .env                # Bot tokenın (asla paylaşma)
├── .gitignore          # Tokenın ve gereksiz dosyaların GitHub'a gönderilmesini engeller
├── data/
│   ├── warns.json          # Uyarı kayıtları (otomatik oluşturulur)
│   ├── ranks.json          # XP ve rank verileri (otomatik oluşturulur)
│   ├── levelroles.json     # Seviye rol ödülleri (otomatik oluşturulur)
│   ├── autoreplies.json    # Otomatik yanıt tetikleyicileri ve yanıtları (otomatik oluşturulur)
│   ├── youtube.json        # YouTube bildirim abonelikleri (otomatik oluşturulur)
│   ├── tickets.json        # Ticket sistemi yapılandırması (otomatik oluşturulur)
│   └── reactionroles.json  # Tepki rol yapılandırması (otomatik oluşturulur)
└── cogs/
    ├── moderation.py       # ban, kick, unban, timeout, delete, lock, unlock, slowmode
    ├── warns.py            # warn, warnings, clearwarnings
    ├── voice.py            # mute-voice, unmute-voice, move
    ├── voice_limit.py      # voice-limit
    ├── roles.py            # role ekle/çıkar
    ├── role_colour.py      # role-colour
    ├── channels.py         # create-channel
    ├── info.py             # userinfo, avatar, serverinfo, roles
    ├── rank.py             # rank, leaderboard, XP sistemi, levelrole
    ├── autoreply.py        # autoreply ekle/çıkar/listele
    ├── youtube.py          # youtube ekle/çıkar/listele
    ├── poll.py             # poll
    ├── reaction_roles.py   # reactionrole ekle/çıkar/listele
    ├── fun.py              # roll
    ├── welcome.py          # karşılama mesajları ve üye katılımında otomatik rol
    ├── tickets.py          # ticket-setup, ticket, bugticket, feedbackticket, supportticket
    ├── setup.py            # set-welcome-channel, set-welcome-message, set-auto-role, settings
    ├── about.py            # about
    └── help.py             # help
```

## ⚠️ Önemli Güvenlik Notu
`.env` dosyasını asla paylaşma veya herkese açık bir depoya gönderme. `.gitignore` dosyası bunu zaten hariç tutuyor ama göndermeden önce her zaman kontrol et.

---
*Enes Ramazan Whitelineage tarafından geliştirilmiştir.*

#### İletişim ve geri bildirim: [Discord](https://discord.gg/vV8gEpHDXH) & [Reddit](https://www.reddit.com/r/WhitelineageDEV/)
