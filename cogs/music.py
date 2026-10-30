import asyncio
import collections
import json
import os
import random
import re
import shlex
import time
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp

PLAYLISTS_FILE = "data/playlists.json"

MAX_QUEUE = 200            # songs in the queue per server
MAX_PLAYLIST_IMPORT = 50   # songs imported from a single YouTube/SoundCloud playlist link
MAX_SAVED_PLAYLISTS = 25   # saved playlists per server
MAX_SAVED_TRACKS = 100     # songs per saved playlist
IDLE_TIMEOUT = 180         # seconds of silence before the bot leaves the voice channel
ALONE_TIMEOUT = 30         # seconds before leaving when everyone else has left
STREAM_URL_TTL = 600       # stream URLs expire, so a resolved URL is only reused for a short time
EARLY_END_SECONDS = 5      # a long song that ends within this many seconds is treated as a failed stream
EARLY_END_MIN_DURATION = 15

# Only these sites are accepted as links. yt-dlp can fetch almost any URL, and on a public
# bot that would let members make the host request arbitrary addresses.
ALLOWED_HOSTS = ("youtube.com", "youtu.be", "soundcloud.com")
URL_RE = re.compile(r"^https?://", re.IGNORECASE)

FFMPEG_BEFORE = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"


def ffmpeg_options(headers: Optional[dict] = None) -> dict:
    """FFmpeg arguments for a stream. YouTube's stream URLs often answer 403 unless FFmpeg sends
    the same HTTP headers (User-Agent etc.) that yt-dlp used to obtain them."""
    before = FFMPEG_BEFORE
    headers = dict(headers or {})
    user_agent = next((headers.pop(key) for key in list(headers) if key.lower() == "user-agent"), None)
    if user_agent:
        before += f" -user_agent {shlex.quote(user_agent)}"
    if headers:
        joined = "".join(f"{key}: {value}\r\n" for key, value in headers.items())
        before += f" -headers {shlex.quote(joined)}"
    return {"before_options": before, "options": "-vn"}


class MusicError(Exception):
    """An error whose message is safe to show to the user."""


@dataclass
class Track:
    title: str
    url: str
    duration: Optional[int]
    requester_id: int
    stream_url: Optional[str] = None
    resolved_at: float = 0.0
    headers: Optional[dict] = None  # HTTP headers yt-dlp used for the stream URL
    retries: int = 0                # how often the stream was re-resolved after failing right away


class GuildPlayer:
    def __init__(self):
        self.queue: collections.deque = collections.deque()
        self.current: Optional[Track] = None
        self.loop = "off"          # off | track | queue
        self.volume = 0.5
        self.starting = False      # True while the next track is being resolved/started
        self.started_at = 0.0      # time.monotonic() when the current track started playing
        self.skipped = False       # True when the current track was ended by /music skip or stop
        self.text_channel_id: Optional[int] = None
        self.idle_task: Optional[asyncio.Task] = None
        self.history: collections.deque = collections.deque(maxlen=50)  # songs that already played, for "previous"
        self.going_back = False    # True while /music previous (or the button) is switching to the last song
        self.panel: Optional[tuple] = None  # (channel_id, message_id) of the message that currently has the buttons


# ---------------------------------------------------------------- helpers

def fmt_duration(seconds) -> str:
    if not seconds:
        return "?"
    seconds = int(seconds)
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"


def link(track: Track, limit: int = 60) -> str:
    title = track.title if len(track.title) <= limit else track.title[:limit - 1] + "…"
    title = discord.utils.escape_markdown(title).replace("[", "(").replace("]", ")")
    return f"[{title}]({track.url})"


def host_allowed(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == h or host.endswith("." + h) for h in ALLOWED_HOSTS)


def make_ytdl(extra: Optional[dict] = None) -> yt_dlp.YoutubeDL:
    options = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "socket_timeout": 15,
        "source_address": "0.0.0.0",  # force IPv4, YouTube streams often fail over broken IPv6
    }
    # Optional: servers/VPS IPs are often asked to "sign in to confirm you're not a bot".
    # Point YTDLP_COOKIES in .env to an exported cookies.txt to work around that.
    cookies = os.getenv("YTDLP_COOKIES")
    if cookies and os.path.exists(cookies):
        options["cookiefile"] = cookies
    # Optional: comma separated YouTube player clients for yt-dlp (see the yt-dlp docs for valid names).
    clients = os.getenv("YTDLP_YOUTUBE_CLIENTS")
    if clients:
        options["extractor_args"] = {"youtube": {"player_client": [c.strip() for c in clients.split(",") if c.strip()]}}
    if extra:
        options.update(extra)
    return yt_dlp.YoutubeDL(options)


def extract_tracks(query: str, requester_id: int):
    """Blocking. Returns (playlist_title_or_None, [Track, ...]). Run it in a thread."""
    query = query.strip()
    if URL_RE.match(query):
        if not host_allowed(query):
            raise MusicError("Only YouTube and SoundCloud links are supported.")
        parsed = urlparse(query)
        if parsed.path.startswith("/playlist") or "/sets/" in parsed.path:
            with make_ytdl({"noplaylist": False, "extract_flat": "in_playlist", "playlistend": MAX_PLAYLIST_IMPORT}) as ydl:
                info = ydl.extract_info(query, download=False)
            tracks = []
            for entry in (info.get("entries") or []):
                if not entry:
                    continue
                url = entry.get("webpage_url") or entry.get("url")
                title = entry.get("title") or "Unknown title"
                if not url or title in ("[Private video]", "[Deleted video]"):
                    continue
                tracks.append(Track(title, url, entry.get("duration"), requester_id))
            if not tracks:
                raise MusicError("That playlist is empty or private.")
            return info.get("title") or "playlist", tracks
        target = query
    else:
        target = f"ytsearch1:{query}"

    with make_ytdl() as ydl:
        info = ydl.extract_info(target, download=False)
    if info and "entries" in info:
        entries = [e for e in info["entries"] if e]
        if not entries:
            raise MusicError("I couldn't find anything for that search.")
        info = entries[0]
    if not info:
        raise MusicError("I couldn't load that.")

    track = Track(
        title=info.get("title") or "Unknown title",
        url=info.get("webpage_url") or info.get("original_url") or target,
        duration=info.get("duration"),
        requester_id=requester_id,
        stream_url=info.get("url"),
        resolved_at=time.time(),
        headers=info.get("http_headers"),
    )
    return None, [track]


def extract_stream(url: str) -> dict:
    """Blocking. Resolves a fresh direct audio URL for a track."""
    with make_ytdl() as ydl:
        info = ydl.extract_info(url, download=False)
    if info and "entries" in info:
        info = next((e for e in info["entries"] if e), None)
    if not info or not info.get("url"):
        raise MusicError("No playable audio stream was found.")
    return info


def load_playlists() -> dict:
    if not os.path.exists(PLAYLISTS_FILE):
        return {}
    with open(PLAYLISTS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_playlists(data: dict):
    os.makedirs(os.path.dirname(PLAYLISTS_FILE), exist_ok=True)
    with open(PLAYLISTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def track_to_dict(track: Track) -> dict:
    return {"title": track.title, "url": track.url, "duration": track.duration}


# ---------------------------------------------------------------- player buttons

class PlayerControls(discord.ui.View):
    """Previous / pause-resume / next / stop buttons under the now-playing message."""

    def __init__(self, cog: "Music", guild_id: int, paused: bool = False):
        super().__init__(timeout=None)
        self.cog = cog
        self.guild_id = guild_id
        self.pause_button.emoji = "▶️" if paused else "⏸️"

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        active = await self.cog._require_active(interaction)
        if active is None:
            return
        vc, player = active
        title = await self.cog._do_previous(interaction.guild, vc, player)
        if title is None:
            await interaction.response.send_message("❌ There is no previous song.", ephemeral=True)
            return
        await interaction.response.defer()  # the new now-playing message announces the change

    @discord.ui.button(emoji="⏸️", style=discord.ButtonStyle.primary)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        active = await self.cog._require_active(interaction)
        if active is None:
            return
        vc, _ = active
        if vc.is_playing():
            vc.pause()
            button.emoji = "▶️"
        elif vc.is_paused():
            vc.resume()
            button.emoji = "⏸️"
        else:
            await interaction.response.send_message("❌ Nothing is playing.", ephemeral=True)
            return
        await interaction.response.edit_message(view=self)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        active = await self.cog._require_active(interaction)
        if active is None:
            return
        vc, player = active
        if self.cog._do_skip(vc, player) is None:
            await interaction.response.send_message("❌ Nothing is playing.", ephemeral=True)
            return
        await interaction.response.defer()

    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        active = await self.cog._require_active(interaction)
        if active is None:
            return
        vc, player = active
        self.cog._do_stop(vc, player)
        await interaction.response.send_message(f"⏹️ Stopped by {interaction.user.mention}.", allowed_mentions=discord.AllowedMentions.none())


# ---------------------------------------------------------------- cog

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players: dict[int, GuildPlayer] = {}

    async def cog_unload(self):
        for guild_id in list(self.players):
            self._cleanup(guild_id)
        for vc in list(self.bot.voice_clients):
            try:
                await vc.disconnect(force=True)
            except Exception:
                pass

    # ------------------------------------------------------------ state

    def _player(self, guild_id: int) -> GuildPlayer:
        player = self.players.get(guild_id)
        if player is None:
            player = self.players[guild_id] = GuildPlayer()
        return player

    def _cleanup(self, guild_id: int):
        player = self.players.pop(guild_id, None)
        if player and player.idle_task:
            player.idle_task.cancel()

    async def _say(self, player: GuildPlayer, content=None, embed=None, view=None):
        channel = self.bot.get_channel(player.text_channel_id) if player.text_channel_id else None
        if channel is None:
            return None
        kwargs = {"view": view} if view is not None else {}
        try:
            return await channel.send(content, embed=embed, allowed_mentions=discord.AllowedMentions.none(), **kwargs)
        except discord.HTTPException:
            return None

    async def _clear_panel(self, player: GuildPlayer):
        """Removes the buttons from the old now-playing message so only the newest one is active."""
        reference, player.panel = player.panel, None
        if not reference:
            return
        channel = self.bot.get_channel(reference[0])
        if channel is None:
            return
        try:
            await channel.get_partial_message(reference[1]).edit(view=None)
        except discord.HTTPException:
            pass

    async def _reply_with_panel(self, interaction: discord.Interaction, player: GuildPlayer, content=None, embed=None):
        """Answers a deferred interaction with a message that has the player buttons."""
        await self._clear_panel(player)
        view = PlayerControls(self, interaction.guild.id, paused=bool(interaction.guild.voice_client and interaction.guild.voice_client.is_paused()))
        message = await interaction.followup.send(
            content, embed=embed, view=view, wait=True, allowed_mentions=discord.AllowedMentions.none())
        player.panel = (interaction.channel_id, message.id)

    # ------------------------------------------------------------ playback engine

    def _next_track(self, player: GuildPlayer) -> Optional[Track]:
        previous = player.current
        if previous is not None and not player.going_back:
            if player.loop == "track" and not player.skipped:
                return previous
            player.history.append(previous)
            if player.loop == "queue":
                player.queue.append(previous)
        # When going back, the current song was already put back at the front of the queue.
        player.skipped = False
        player.going_back = False
        return player.queue.popleft() if player.queue else None

    async def _stream_url(self, track: Track) -> str:
        if track.stream_url and time.time() - track.resolved_at < STREAM_URL_TTL:
            return track.stream_url
        info = await asyncio.to_thread(extract_stream, track.url)
        track.stream_url = info["url"]
        track.headers = info.get("http_headers")
        track.resolved_at = time.time()
        if not track.duration:
            track.duration = info.get("duration")
        return track.stream_url

    async def _advance(self, guild: discord.Guild, announce: bool = False):
        """Starts the next track. Safe to call when something is already starting."""
        player = self.players.get(guild.id)
        if player is None:
            return
        player.starting = True
        if player.idle_task:
            player.idle_task.cancel()
            player.idle_task = None
        try:
            while True:
                vc = guild.voice_client
                if vc is None or not vc.is_connected():
                    self._cleanup(guild.id)
                    return

                previous = player.current
                ended_early = (
                    previous is not None and not player.skipped and not player.going_back
                    and player.started_at > 0
                    and time.monotonic() - player.started_at < EARLY_END_SECONDS
                    and (previous.duration or 0) > EARLY_END_MIN_DURATION
                )
                if ended_early and previous.retries < 1:
                    # e.g. 403 from YouTube: get a fresh stream URL and try the same song once more.
                    previous.retries += 1
                    previous.stream_url = None
                    print(f"[music] '{previous.title}' ended right after starting, retrying with a fresh stream URL.")
                    track = previous
                else:
                    if ended_early:
                        await self._say(player, f"❌ Couldn't stream **{discord.utils.escape_markdown(previous.title)}** (YouTube rejected the stream). Skipping.")
                    if previous is not None:
                        previous.retries = 0
                    track = self._next_track(player)
                if track is None:
                    player.current = None
                    await self._clear_panel(player)
                    player.idle_task = asyncio.create_task(self._idle_disconnect(guild.id))
                    return

                repeated = track is previous  # loop=track: same song again, keep the buttons where they are
                if not repeated:
                    await self._clear_panel(player)
                player.current = track
                try:
                    stream_url = await self._stream_url(track)
                except MusicError as e:
                    problem = str(e)
                except Exception as e:
                    print(f"[music] Could not load '{track.title}': {e!r}")
                    problem = "YouTube refused the request or the video is unavailable"
                else:
                    problem = None

                if problem:
                    player.current = None  # forget the broken track so loop modes can't retry it forever
                    await self._say(player, f"❌ Couldn't play **{discord.utils.escape_markdown(track.title)}** ({problem}). Skipping.")
                    continue

                if guild.voice_client is None or not guild.voice_client.is_connected():
                    self._cleanup(guild.id)
                    return

                source = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(stream_url, **ffmpeg_options(track.headers)),
                    volume=player.volume,
                )
                guild.voice_client.play(source, after=lambda error, gid=guild.id: self._after(gid, error))
                player.started_at = time.monotonic()
                if announce and not repeated:
                    message = await self._say(
                        player, embed=self._now_playing_embed(player, "▶️ Now playing"),
                        view=PlayerControls(self, guild.id))
                    if message:
                        player.panel = (message.channel.id, message.id)
                return
        finally:
            player.starting = False

    def _after(self, guild_id: int, error):
        # Runs in the audio thread, so hop back onto the event loop.
        if error:
            print(f"[music] Player error in guild {guild_id}: {error!r}")
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return
        asyncio.run_coroutine_threadsafe(self._advance(guild, announce=True), self.bot.loop)

    async def _idle_disconnect(self, guild_id: int):
        await asyncio.sleep(IDLE_TIMEOUT)
        guild = self.bot.get_guild(guild_id)
        player = self.players.get(guild_id)
        if guild is None or player is None:
            return
        vc = guild.voice_client
        if vc and not vc.is_playing() and not vc.is_paused() and player.current is None and not player.starting:
            await self._say(player, "👋 Nothing left to play, leaving the voice channel.")
            await self._clear_panel(player)
            self._cleanup(guild_id)
            await vc.disconnect()

    # ------------------------------------------------------------ actions shared by commands and buttons

    def _do_skip(self, vc: discord.VoiceClient, player: GuildPlayer) -> Optional[str]:
        """Returns the skipped title, or None if nothing was playing."""
        if player.current is None or not (vc.is_playing() or vc.is_paused()):
            return None
        title = player.current.title
        player.skipped = True
        vc.stop()  # the after-callback starts the next track
        return title

    def _do_stop(self, vc: discord.VoiceClient, player: GuildPlayer):
        player.queue.clear()
        player.loop = "off"
        player.skipped = True
        if vc.is_playing() or vc.is_paused():
            vc.stop()

    async def _do_previous(self, guild: discord.Guild, vc: discord.VoiceClient, player: GuildPlayer) -> Optional[str]:
        """Goes back to the song that played before. Returns its title, or None if there is none."""
        if not player.history:
            return None
        previous = player.history.pop()
        if player.loop == "queue":
            # It was appended to the end of the queue when it finished; it is about to play now.
            for index in range(len(player.queue) - 1, -1, -1):
                if player.queue[index] is previous:
                    del player.queue[index]
                    break
        if player.current is not None:
            player.queue.appendleft(player.current)  # the current song plays again after the previous one
        player.queue.appendleft(previous)
        player.going_back = True
        if vc.is_playing() or vc.is_paused():
            vc.stop()  # the after-callback starts `previous`
        elif not player.starting:
            await self._advance(guild, announce=True)
        return previous.title

    # ------------------------------------------------------------ embeds

    def _now_playing_embed(self, player: GuildPlayer, heading: str) -> discord.Embed:
        track = player.current
        embed = discord.Embed(title=heading, description=link(track, 90), colour=discord.Colour.green())
        embed.add_field(name="Duration", value=fmt_duration(track.duration), inline=True)
        embed.add_field(name="Requested by", value=f"<@{track.requester_id}>", inline=True)
        embed.add_field(name="Loop", value=player.loop.capitalize(), inline=True)
        return embed

    # ------------------------------------------------------------ voice helpers

    async def _ensure_voice(self, interaction: discord.Interaction) -> Optional[discord.VoiceClient]:
        """For deferred interactions. Joins the user's channel, or sends an error and returns None."""
        guild = interaction.guild
        voice = interaction.user.voice
        if voice is None or voice.channel is None:
            await interaction.followup.send("❌ Join a voice channel first.", ephemeral=True)
            return None
        channel = voice.channel
        if not isinstance(channel, discord.VoiceChannel):
            await interaction.followup.send("❌ I can only play in regular voice channels, not stages.", ephemeral=True)
            return None

        perms = channel.permissions_for(guild.me)
        if not (perms.view_channel and perms.connect and perms.speak):
            await interaction.followup.send(f"❌ I need **Connect** and **Speak** permissions in {channel.mention}.", ephemeral=True)
            return None

        vc = guild.voice_client
        player = self._player(guild.id)
        if vc is not None and vc.is_connected():
            if vc.channel != channel:
                if vc.is_playing() or vc.is_paused():
                    await interaction.followup.send(f"❌ I'm already playing music in {vc.channel.mention}.", ephemeral=True)
                    return None
                await vc.move_to(channel)
            return vc

        try:
            vc = await channel.connect(self_deaf=True)
        except (asyncio.TimeoutError, discord.ClientException, discord.HTTPException) as e:
            print(f"[music] Could not join voice in guild {guild.id}: {e!r}")
            self._cleanup(guild.id)
            await interaction.followup.send("❌ I couldn't connect to that voice channel. Try again in a moment.", ephemeral=True)
            return None
        player.text_channel_id = interaction.channel_id
        return vc

    async def _require_active(self, interaction: discord.Interaction):
        """For control commands. Returns (vc, player) or sends an error and returns None."""
        guild = interaction.guild
        vc = guild.voice_client
        if vc is None or not vc.is_connected():
            await interaction.response.send_message("❌ I'm not connected to a voice channel.", ephemeral=True)
            return None
        voice = interaction.user.voice
        if voice is None or voice.channel != vc.channel:
            await interaction.response.send_message(f"❌ You need to be in {vc.channel.mention} to do that.", ephemeral=True)
            return None
        return vc, self._player(guild.id)

    async def _enqueue(self, interaction: discord.Interaction, tracks: list, source_name: Optional[str], shuffle: bool = False):
        """Adds tracks, starts playback if idle and answers the (deferred) interaction."""
        guild = interaction.guild
        player = self._player(guild.id)
        player.text_channel_id = interaction.channel_id

        room = MAX_QUEUE - len(player.queue)
        if room <= 0:
            await interaction.followup.send(f"❌ The queue is full ({MAX_QUEUE} songs).")
            return
        tracks = tracks[:room]
        if shuffle:
            tracks = random.sample(tracks, len(tracks))
        position = len(player.queue) + 1
        player.queue.extend(tracks)

        # No await between this check and _advance setting `starting`, so two /play
        # commands at the same time can't both start a track.
        if player.current is None and not player.starting:
            await self._advance(guild)

        started = player.current is tracks[0]
        if len(tracks) == 1:
            if started:
                await self._reply_with_panel(interaction, player, embed=self._now_playing_embed(player, "▶️ Now playing"))
            else:
                embed = discord.Embed(title="➕ Added to queue", description=link(tracks[0], 90), colour=discord.Colour.blurple())
                embed.add_field(name="Position", value=str(position), inline=True)
                embed.add_field(name="Duration", value=fmt_duration(tracks[0].duration), inline=True)
                await interaction.followup.send(embed=embed)
            return

        text = f"➕ Added **{len(tracks)}** songs from **{discord.utils.escape_markdown(source_name or 'playlist')}**."
        if started:
            text += f"\n▶️ Now playing: {link(player.current)}"
            await self._reply_with_panel(interaction, player, content=text)
            return
        await interaction.followup.send(text, allowed_mentions=discord.AllowedMentions.none())

    # ------------------------------------------------------------ voice events

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = member.guild

        if member.id == self.bot.user.id:
            if before.channel is not None and after.channel is None:
                self._cleanup(guild.id)  # disconnected or kicked
            return

        vc = guild.voice_client
        if vc is None or vc.channel is None:
            return
        if before.channel == vc.channel and after.channel != vc.channel:
            if not any(not m.bot for m in vc.channel.members):
                await asyncio.sleep(ALONE_TIMEOUT)
                vc = guild.voice_client
                if vc and vc.channel and not any(not m.bot for m in vc.channel.members):
                    player = self.players.get(guild.id)
                    if player:
                        await self._say(player, "👋 Everyone left, so I left too.")
                        await self._clear_panel(player)
                    self._cleanup(guild.id)
                    await vc.disconnect()

    # ------------------------------------------------------------ /music

    music = app_commands.Group(name="music", description="Play music in voice channels.", guild_only=True)

    @music.command(name="play", description="Plays a song or adds it to the queue.")
    @app_commands.describe(query="Song name, or a YouTube / SoundCloud link (playlist links add every song)")
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        vc = await self._ensure_voice(interaction)
        if vc is None:
            return

        try:
            source_name, tracks = await asyncio.to_thread(extract_tracks, query, interaction.user.id)
        except MusicError as e:
            await interaction.followup.send(f"❌ {e}", ephemeral=True)
            return
        except Exception as e:
            print(f"[music] Search failed for {query!r}: {e!r}")
            await interaction.followup.send(
                "❌ I couldn't load that. The video may be private, age-restricted or region-locked, "
                "or YouTube blocked the request.", ephemeral=True)
            return

        await self._enqueue(interaction, tracks, source_name if len(tracks) > 1 else None)

    @music.command(name="join", description="Makes the bot join your voice channel.")
    async def join(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        vc = await self._ensure_voice(interaction)
        if vc is not None:
            await interaction.followup.send(f"✅ Joined {vc.channel.mention}.", ephemeral=True)

    @music.command(name="pause", description="Pauses the current song.")
    async def pause(self, interaction: discord.Interaction):
        active = await self._require_active(interaction)
        if active is None:
            return
        vc, _ = active
        if not vc.is_playing():
            await interaction.response.send_message("❌ Nothing is playing.", ephemeral=True)
            return
        vc.pause()
        await interaction.response.send_message("⏸️ Paused.")

    @music.command(name="resume", description="Resumes the paused song.")
    async def resume(self, interaction: discord.Interaction):
        active = await self._require_active(interaction)
        if active is None:
            return
        vc, _ = active
        if not vc.is_paused():
            await interaction.response.send_message("❌ Nothing is paused.", ephemeral=True)
            return
        vc.resume()
        await interaction.response.send_message("▶️ Resumed.")

    @music.command(name="skip", description="Skips the current song.")
    async def skip(self, interaction: discord.Interaction):
        active = await self._require_active(interaction)
        if active is None:
            return
        vc, player = active
        title = self._do_skip(vc, player)
        if title is None:
            await interaction.response.send_message("❌ Nothing is playing.", ephemeral=True)
            return
        await interaction.response.send_message(
            f"⏭️ Skipped **{discord.utils.escape_markdown(title)}**.", allowed_mentions=discord.AllowedMentions.none())

    @music.command(name="previous", description="Goes back to the previous song.")
    async def previous(self, interaction: discord.Interaction):
        active = await self._require_active(interaction)
        if active is None:
            return
        vc, player = active
        title = await self._do_previous(interaction.guild, vc, player)
        if title is None:
            await interaction.response.send_message("❌ There is no previous song.", ephemeral=True)
            return
        await interaction.response.send_message(
            f"⏮️ Going back to **{discord.utils.escape_markdown(title)}**.", allowed_mentions=discord.AllowedMentions.none())

    @music.command(name="stop", description="Stops the music and clears the queue.")
    async def stop(self, interaction: discord.Interaction):
        active = await self._require_active(interaction)
        if active is None:
            return
        vc, player = active
        self._do_stop(vc, player)
        await interaction.response.send_message("⏹️ Stopped and cleared the queue.")

    @music.command(name="leave", description="Disconnects the bot from the voice channel.")
    async def leave(self, interaction: discord.Interaction):
        active = await self._require_active(interaction)
        if active is None:
            return
        vc, player = active
        await self._clear_panel(player)
        self._cleanup(interaction.guild.id)
        await vc.disconnect()
        await interaction.response.send_message("👋 Disconnected.")

    @music.command(name="nowplaying", description="Shows the song that is currently playing.")
    async def nowplaying(self, interaction: discord.Interaction):
        player = self.players.get(interaction.guild.id)
        if player is None or player.current is None:
            await interaction.response.send_message("❌ Nothing is playing.", ephemeral=True)
            return
        await interaction.response.defer()
        await self._reply_with_panel(interaction, player, embed=self._now_playing_embed(player, "🎵 Now playing"))

    @music.command(name="queue", description="Shows the queue.")
    @app_commands.describe(page="Page number")
    async def queue(self, interaction: discord.Interaction, page: app_commands.Range[int, 1] = 1):
        player = self.players.get(interaction.guild.id)
        if player is None or (player.current is None and not player.queue):
            await interaction.response.send_message("❌ The queue is empty.", ephemeral=True)
            return

        per_page = 10
        pages = max(1, -(-len(player.queue) // per_page))
        page = min(page, pages)
        start = (page - 1) * per_page

        embed = discord.Embed(title="🎶 Queue", colour=discord.Colour.blurple())
        if player.current:
            embed.add_field(name="Now playing", value=f"{link(player.current)} `[{fmt_duration(player.current.duration)}]`", inline=False)
        if player.queue:
            lines = [
                f"`{start + i}.` {link(track)} `[{fmt_duration(track.duration)}]`"
                for i, track in enumerate(list(player.queue)[start:start + per_page], start=1)
            ]
            embed.add_field(name="Up next", value="\n".join(lines), inline=False)

        total = sum(t.duration or 0 for t in player.queue)
        embed.set_footer(text=f"Page {page}/{pages} • {len(player.queue)} in queue • {fmt_duration(total)} total • Loop: {player.loop}")
        await interaction.response.send_message(embed=embed)

    @music.command(name="remove", description="Removes a song from the queue.")
    @app_commands.describe(position="Position in the queue (see /music queue)")
    async def remove(self, interaction: discord.Interaction, position: app_commands.Range[int, 1]):
        active = await self._require_active(interaction)
        if active is None:
            return
        _, player = active
        if position > len(player.queue):
            await interaction.response.send_message("❌ There is no song at that position.", ephemeral=True)
            return
        track = player.queue[position - 1]
        del player.queue[position - 1]
        await interaction.response.send_message(
            f"🗑️ Removed **{discord.utils.escape_markdown(track.title)}** from the queue.",
            allowed_mentions=discord.AllowedMentions.none())

    @music.command(name="clear", description="Clears the queue but keeps the current song playing.")
    async def clear(self, interaction: discord.Interaction):
        active = await self._require_active(interaction)
        if active is None:
            return
        _, player = active
        count = len(player.queue)
        player.queue.clear()
        await interaction.response.send_message(f"🧹 Removed **{count}** song(s) from the queue.")

    @music.command(name="shuffle", description="Shuffles the queue.")
    async def shuffle(self, interaction: discord.Interaction):
        active = await self._require_active(interaction)
        if active is None:
            return
        _, player = active
        if len(player.queue) < 2:
            await interaction.response.send_message("❌ Not enough songs in the queue to shuffle.", ephemeral=True)
            return
        items = list(player.queue)
        random.shuffle(items)
        player.queue = collections.deque(items)
        await interaction.response.send_message("🔀 Queue shuffled.")

    @music.command(name="loop", description="Sets the loop mode.")
    @app_commands.describe(mode="off, repeat the current song, or repeat the whole queue")
    @app_commands.choices(mode=[
        app_commands.Choice(name="Off", value="off"),
        app_commands.Choice(name="Current song", value="track"),
        app_commands.Choice(name="Whole queue", value="queue"),
    ])
    async def loop(self, interaction: discord.Interaction, mode: app_commands.Choice[str]):
        active = await self._require_active(interaction)
        if active is None:
            return
        _, player = active
        player.loop = mode.value
        await interaction.response.send_message(f"🔁 Loop mode: **{mode.name}**.")

    @music.command(name="volume", description="Sets the volume.")
    @app_commands.describe(level="Volume from 1 to 100 (default 50)")
    async def volume(self, interaction: discord.Interaction, level: app_commands.Range[int, 1, 100]):
        active = await self._require_active(interaction)
        if active is None:
            return
        vc, player = active
        player.volume = level / 100
        if isinstance(vc.source, discord.PCMVolumeTransformer):
            vc.source.volume = player.volume
        await interaction.response.send_message(f"🔊 Volume set to **{level}%**.")

    # ------------------------------------------------------------ /playlist (saved, per server)

    playlist = app_commands.Group(name="playlist", description="Save and play server playlists.", guild_only=True)

    async def _playlist_autocomplete(self, interaction: discord.Interaction, current: str):
        playlists = load_playlists().get(str(interaction.guild.id), {})
        names = [p["name"] for p in playlists.values() if current.lower() in p["name"].lower()]
        return [app_commands.Choice(name=n, value=n) for n in names[:25]]

    @staticmethod
    def _playlist_key(name: str) -> str:
        return name.strip().lower()

    @playlist.command(name="save", description="Saves the current song and the queue as a playlist.")
    @app_commands.describe(name="Playlist name")
    async def playlist_save(self, interaction: discord.Interaction, name: app_commands.Range[str, 1, 32]):
        player = self.players.get(interaction.guild.id)
        tracks = ([player.current] if player and player.current else []) + (list(player.queue) if player else [])
        if not tracks:
            await interaction.response.send_message("❌ There is nothing to save. Play something first.", ephemeral=True)
            return

        data = load_playlists()
        guild_playlists = data.setdefault(str(interaction.guild.id), {})
        key = self._playlist_key(name)
        existing = guild_playlists.get(key)
        if existing is None and len(guild_playlists) >= MAX_SAVED_PLAYLISTS:
            await interaction.response.send_message(f"❌ This server already has {MAX_SAVED_PLAYLISTS} playlists. Delete one first.", ephemeral=True)
            return
        if existing and existing["owner"] != interaction.user.id and not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ A playlist with that name already exists and belongs to someone else.", ephemeral=True)
            return

        guild_playlists[key] = {
            "name": name.strip(),
            "owner": interaction.user.id,
            "tracks": [track_to_dict(t) for t in tracks[:MAX_SAVED_TRACKS]],
        }
        save_playlists(data)
        await interaction.response.send_message(
            f"💾 Saved **{len(guild_playlists[key]['tracks'])}** song(s) as playlist **{discord.utils.escape_markdown(name.strip())}**.",
            allowed_mentions=discord.AllowedMentions.none())

    @playlist.command(name="add", description="Adds a song (or a YouTube playlist link) to a saved playlist.")
    @app_commands.describe(name="Playlist name (created if it doesn't exist)", query="Song name or YouTube / SoundCloud link")
    @app_commands.autocomplete(name=_playlist_autocomplete)
    async def playlist_add(self, interaction: discord.Interaction, name: app_commands.Range[str, 1, 32], query: str):
        await interaction.response.defer(ephemeral=True)
        try:
            _, tracks = await asyncio.to_thread(extract_tracks, query, interaction.user.id)
        except MusicError as e:
            await interaction.followup.send(f"❌ {e}")
            return
        except Exception as e:
            print(f"[music] Playlist add failed for {query!r}: {e!r}")
            await interaction.followup.send("❌ I couldn't load that.")
            return

        # Load after the slow part so changes made in the meantime aren't overwritten.
        data = load_playlists()
        guild_playlists = data.setdefault(str(interaction.guild.id), {})
        key = self._playlist_key(name)
        playlist = guild_playlists.get(key)
        if playlist is None:
            if len(guild_playlists) >= MAX_SAVED_PLAYLISTS:
                await interaction.followup.send(f"❌ This server already has {MAX_SAVED_PLAYLISTS} playlists. Delete one first.")
                return
            playlist = guild_playlists[key] = {"name": name.strip(), "owner": interaction.user.id, "tracks": []}
        elif playlist["owner"] != interaction.user.id and not interaction.user.guild_permissions.manage_guild:
            await interaction.followup.send("❌ That playlist belongs to someone else.")
            return

        room = MAX_SAVED_TRACKS - len(playlist["tracks"])
        if room <= 0:
            await interaction.followup.send(f"❌ That playlist is full ({MAX_SAVED_TRACKS} songs).")
            return
        added = tracks[:room]
        playlist["tracks"].extend(track_to_dict(t) for t in added)
        save_playlists(data)
        await interaction.followup.send(
            f"✅ Added **{len(added)}** song(s) to **{discord.utils.escape_markdown(playlist['name'])}** "
            f"({len(playlist['tracks'])} total).",
            allowed_mentions=discord.AllowedMentions.none())

    @playlist.command(name="play", description="Queues a saved playlist.")
    @app_commands.describe(name="Playlist name", shuffle="Shuffle the songs before queueing")
    @app_commands.autocomplete(name=_playlist_autocomplete)
    async def playlist_play(self, interaction: discord.Interaction, name: str, shuffle: bool = False):
        await interaction.response.defer()
        playlist = load_playlists().get(str(interaction.guild.id), {}).get(self._playlist_key(name))
        if playlist is None or not playlist["tracks"]:
            await interaction.followup.send("❌ I couldn't find a playlist with that name.", ephemeral=True)
            return

        vc = await self._ensure_voice(interaction)
        if vc is None:
            return

        tracks = [Track(t["title"], t["url"], t.get("duration"), interaction.user.id) for t in playlist["tracks"]]
        await self._enqueue(interaction, tracks, playlist["name"], shuffle=shuffle)

    @playlist.command(name="list", description="Lists the saved playlists of this server.")
    async def playlist_list(self, interaction: discord.Interaction):
        playlists = load_playlists().get(str(interaction.guild.id), {})
        if not playlists:
            await interaction.response.send_message("❌ No playlists saved yet. Use `/playlist save` or `/playlist add`.", ephemeral=True)
            return
        embed = discord.Embed(title="📚 Saved playlists", colour=discord.Colour.blurple())
        for p in playlists.values():
            total = sum(t.get("duration") or 0 for t in p["tracks"])
            embed.add_field(
                name=p["name"],
                value=f"{len(p['tracks'])} song(s) • {fmt_duration(total)} • by <@{p['owner']}>",
                inline=False,
            )
        await interaction.response.send_message(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @playlist.command(name="delete", description="Deletes a saved playlist.")
    @app_commands.describe(name="Playlist name")
    @app_commands.autocomplete(name=_playlist_autocomplete)
    async def playlist_delete(self, interaction: discord.Interaction, name: str):
        data = load_playlists()
        guild_playlists = data.get(str(interaction.guild.id), {})
        key = self._playlist_key(name)
        playlist = guild_playlists.get(key)
        if playlist is None:
            await interaction.response.send_message("❌ I couldn't find a playlist with that name.", ephemeral=True)
            return
        if playlist["owner"] != interaction.user.id and not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Only the creator or someone with **Manage Server** can delete this playlist.", ephemeral=True)
            return
        del guild_playlists[key]
        save_playlists(data)
        await interaction.response.send_message(
            f"🗑️ Deleted playlist **{discord.utils.escape_markdown(playlist['name'])}**.",
            allowed_mentions=discord.AllowedMentions.none())

    # ------------------------------------------------------------ errors

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        print(f"[music] Command error: {error!r}")
        message = f"❌ Error: {error}"
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Music(bot))
