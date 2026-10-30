# Changelog / Değişiklik Günlüğü

[English](#english) | [Türkçe](#türkçe)

---

## English

### v1.3.1 — Player buttons and music fixes

- **Player buttons:** the now-playing message (from `/music play`, `/music nowplaying` and when the next song starts) has ⏮️ previous, ⏸️/▶️ pause and resume, ⏭️ next and ⏹️ stop buttons. Only the newest message keeps its buttons, and they are removed when the queue ends or the bot leaves.
- **New:** `/music previous` goes back to the song that played before (the current song plays again afterwards).
- **Fix:** playback failed with FFmpeg's `Unrecognized option 'reconnect_streaming'` error. The correct option is `reconnect_streamed`.
- **Fix:** a song that fails to load is no longer replayed by loop modes or added to the "previous" history.
- **Fix:** with loop set to a single song, the now-playing message is no longer re-sent on every repeat.
- **Fix:** YouTube streams that answered `403 Forbidden` in FFmpeg. yt-dlp's HTTP headers are now passed to FFmpeg, and a long song that dies within 5 seconds is retried once with a fresh stream URL before being skipped with a message.
- New optional `.env` setting `YTDLP_YOUTUBE_CLIENTS` to choose the YouTube clients yt-dlp uses.
- Buttons on old messages stop working after the bot restarts. Run `/music nowplaying` for a new panel.

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

### v1.3.1 — Oynatıcı butonları ve müzik düzeltmeleri

- **Oynatıcı butonları:** "Şu an çalıyor" mesajında (`/music play`, `/music nowplaying` ve sıradaki şarkı başlarken) ⏮️ önceki, ⏸️/▶️ duraklat ve devam, ⏭️ sonraki ve ⏹️ durdur butonları bulunur. Butonlar yalnızca en yeni mesajda kalır, kuyruk bitince veya bot kanaldan çıkınca kaldırılır.
- **Yeni:** `/music previous` bir önceki şarkıya döner (çalan şarkı ondan sonra yeniden çalar).
- **Düzeltme:** FFmpeg'in `Unrecognized option 'reconnect_streaming'` hatası yüzünden çalma başarısız oluyordu. Doğru seçenek `reconnect_streamed`.
- **Düzeltme:** Yüklenemeyen bir şarkı artık döngü modlarında tekrar denenmez ve "önceki" geçmişine eklenmez.
- **Düzeltme:** Tek şarkı döngüsünde "Şu an çalıyor" mesajı her tekrarda yeniden gönderilmez.
- **Düzeltme:** FFmpeg'de `403 Forbidden` veren YouTube akışları. yt-dlp'nin HTTP başlıkları artık FFmpeg'e iletiliyor, başladıktan 5 saniye içinde kopan uzun bir şarkı atlanmadan önce yeni akış URL'siyle bir kez yeniden deneniyor ve atlanırsa mesaj yazılıyor.
- Yeni isteğe bağlı `.env` ayarı `YTDLP_YOUTUBE_CLIENTS`: yt-dlp'nin kullandığı YouTube istemcilerini seçer.
- Bot yeniden başlayınca eski mesajlardaki butonlar çalışmaz. Yeni panel için `/music nowplaying` yaz.

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
