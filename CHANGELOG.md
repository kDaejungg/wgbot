# Changelog / Değişiklik Günlüğü

[English](#english) | [Türkçe](#türkçe)

---

## English

### v1.3.0 — Music, channel deletion and YouTube fixes

#### 🎵 New: Music
- Play songs from **YouTube and SoundCloud** in a voice channel by name or link. The bot joins your channel automatically.
- Queue controls: `/music play`, `pause`, `resume`, `skip`, `stop`, `queue`, `nowplaying`, `remove`, `clear`, `shuffle`, `loop` (off / song / queue), `volume`, `join`, `leave`.
- YouTube and SoundCloud **playlist links** add every song at once (up to 50).
- **Saved server playlists**: `/playlist save`, `add`, `play`, `list`, `delete`.
- Leaves the voice channel when the queue ends or when everyone has left.
- Only YouTube and SoundCloud links are accepted.
- Requires **FFmpeg** on the host. `yt-dlp` is a new dependency. Optional `YTDLP_COOKIES` setting in `.env` for hosts that YouTube blocks.

#### 📁 New: Channel deletion
- `/delete-channel <channel> [reason]` with a confirmation button. Checks the permissions of both the user and the bot, and logs the reason in the audit log.

#### 🎥 YouTube notification fixes
- **Role ping:** the ping now uses explicit allowed mentions, and `/youtube add` warns when the role is not mentionable and the bot lacks *Mention Everyone*.
- Notifications are saved as "seen" only **after** they are sent, so a failed send is retried instead of lost.
- One failing subscription (network error, missing permission) no longer stops the whole notification loop.
- Deleting the latest video no longer re-announces an older one; several uploads within one check are announced in order.
- Feed downloads no longer block the bot.
- `/youtube add` validates the channel ID and the bot's permissions in the target channel.
- New: `/youtube test <tag>` sends a test notification.

#### 🔧 Other
- Cogs are loaded in `setup_hook`, so a reconnect no longer tries to load them twice. A cog that fails to load no longer prevents the bot from starting.
- The `data/` folder is created automatically (a fresh clone crashed on the first save).
- An empty or missing `settings.json` no longer crashes the setup commands.
- `cookies.txt` added to `.gitignore`.
- Updated `/help`, `/about`, both READMEs and `requirements.txt` (`discord.py[voice]`, `yt-dlp`).

#### Upgrading
1. `pip install -r requirements.txt`
2. Install **FFmpeg** (`sudo apt install ffmpeg` / `winget install ffmpeg` / `brew install ffmpeg`).
3. Restart the bot. Existing YouTube subscriptions keep working, they are migrated automatically.

---

## Türkçe

### v1.3.0 — Müzik, kanal silme ve YouTube düzeltmeleri

#### 🎵 Yeni: Müzik
- Ses kanalında isim veya bağlantıyla **YouTube ve SoundCloud** şarkıları çalar. Bot kanalına kendisi bağlanır.
- Kuyruk kontrolleri: `/music play`, `pause`, `resume`, `skip`, `stop`, `queue`, `nowplaying`, `remove`, `clear`, `shuffle`, `loop` (kapalı / şarkı / kuyruk), `volume`, `join`, `leave`.
- YouTube ve SoundCloud **oynatma listesi bağlantıları** tüm şarkıları tek seferde ekler (en fazla 50).
- **Kayıtlı sunucu listeleri**: `/playlist save`, `add`, `play`, `list`, `delete`.
- Kuyruk bitince veya herkes çıkınca ses kanalından ayrılır.
- Yalnızca YouTube ve SoundCloud bağlantıları kabul edilir.
- Sunucuda **FFmpeg** gerekir. `yt-dlp` yeni bir bağımlılıktır. YouTube'un engellediği sunucular için `.env` içinde isteğe bağlı `YTDLP_COOKIES` ayarı vardır.

#### 📁 Yeni: Kanal silme
- Onay butonlu `/delete-channel <kanal> [sebep]`. Hem kullanıcının hem botun yetkisini kontrol eder, sebep denetim günlüğüne yazılır.

#### 🎥 YouTube bildirim düzeltmeleri
- **Rol pingi:** ping artık açık `allowed_mentions` ile gönderilir. Rol etiketlenebilir değilse ve botta *Mention Everyone* izni yoksa `/youtube add` uyarır.
- Bildirim "görüldü" olarak **gönderildikten sonra** kaydedilir. Gönderim başarısız olursa kaybolmaz, tekrar denenir.
- Tek bir aboneliğin hatası (ağ hatası, eksik yetki) artık tüm bildirim döngüsünü durdurmaz.
- Son video silinince eski bir video tekrar duyurulmaz. Tek kontrolde birden fazla video yüklenirse sırayla duyurulur.
- Feed indirmeleri botu artık bloklamaz.
- `/youtube add` kanal ID'sini ve botun hedef kanaldaki yetkilerini kontrol eder.
- Yeni: `/youtube test <etiket>` test bildirimi gönderir.

#### 🔧 Diğer
- Cog'lar `setup_hook` içinde yüklenir, yeniden bağlanmada ikinci kez yüklenmeye çalışılmaz. Yüklenemeyen bir cog botun açılmasını engellemez.
- `data/` klasörü otomatik oluşturulur (temiz klonda ilk kayıtta çöküyordu).
- Boş veya eksik `settings.json` artık kurulum komutlarını çökertmez.
- `.gitignore` dosyasına `cookies.txt` eklendi.
- `/help`, `/about`, iki README ve `requirements.txt` güncellendi (`discord.py[voice]`, `yt-dlp`).

#### Güncelleme
1. `pip install -r requirements.txt`
2. **FFmpeg** kur (`sudo apt install ffmpeg` / `winget install ffmpeg` / `brew install ffmpeg`).
3. Botu yeniden başlat. Mevcut YouTube abonelikleri çalışmaya devam eder, otomatik dönüştürülür.
