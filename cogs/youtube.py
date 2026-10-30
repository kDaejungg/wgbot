import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
import feedparser
import json
import os
import re

YOUTUBE_FILE = "data/youtube.json"
CHECK_INTERVAL = 5  # minutes
MAX_NOTIFICATIONS_PER_CHECK = 5  # per subscription, so a burst of uploads can't flood a channel
SEEN_LIMIT = 50  # how many video IDs we remember per subscription

CHANNEL_ID_RE = re.compile(r"UC[\w-]{22}")


def load_data():
    if not os.path.exists(YOUTUBE_FILE):
        return {}
    with open(YOUTUBE_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_data(data):
    os.makedirs(os.path.dirname(YOUTUBE_FILE), exist_ok=True)
    with open(YOUTUBE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_feed_url(channel_id: str) -> str:
    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


async def fetch_feed(channel_id: str):
    # feedparser does blocking network I/O; run it in a thread so the bot
    # (heartbeat, commands, music) doesn't freeze while a feed downloads.
    return await asyncio.to_thread(feedparser.parse, get_feed_url(channel_id))


def extract_channel_id(text: str):
    """Accepts a raw channel ID or a youtube.com/channel/UC... URL."""
    match = CHANNEL_ID_RE.search(text or "")
    return match.group(0) if match else None


def update_subscription(guild_id: str, tag: str, **fields) -> bool:
    """Re-reads the file, updates one subscription and saves.

    There is no `await` between the load and the save, so this can't interleave
    with /youtube add or /youtube remove and overwrite their changes with stale data.
    """
    data = load_data()
    sub = data.get(guild_id, {}).get(tag)
    if sub is None:
        return False  # removed while we were busy
    sub.update(fields)
    save_data(data)
    return True


def build_ping(channel, ping_role_id):
    """Returns (mention_text, allowed_mentions) for the configured ping role.

    The mention has to be in the message *content* and the role has to be listed in
    allowed_mentions; otherwise Discord renders it but does not notify anyone.
    """
    if not ping_role_id:
        return "", discord.AllowedMentions.none()

    role = channel.guild.get_role(int(ping_role_id))
    if role is None:
        print(f"[youtube] Ping role {ping_role_id} no longer exists in guild {channel.guild.id}.")
        return "", discord.AllowedMentions.none()

    if role.is_default():
        return "@everyone", discord.AllowedMentions(everyone=True, users=False, roles=False)

    me = channel.guild.me
    if not role.mentionable and not channel.permissions_for(me).mention_everyone:
        print(
            f"[youtube] Role '{role.name}' is not mentionable and the bot lacks the "
            f"'Mention Everyone' permission in #{channel.name}: the ping will not notify anyone."
        )

    return role.mention, discord.AllowedMentions(everyone=False, users=False, roles=[role])


def ping_warning(channel, role) -> str:
    """Human readable warning shown when a ping cannot work, or an empty string."""
    if role is None or role.is_default():
        return ""
    if role.mentionable or channel.permissions_for(channel.guild.me).mention_everyone:
        return ""
    return (
        f"\n⚠️ {role.mention} is **not mentionable** and I don't have the **Mention Everyone** "
        "permission, so the ping will not notify anyone. Either enable "
        "*Allow anyone to @mention this role* in the role settings, or give me the "
        "**Mention Everyone** permission."
    )


def build_embed(title, video_id, channel_name, tag):
    embed = discord.Embed(
        title=title or "New Video",
        url=f"https://www.youtube.com/watch?v={video_id}",
        description=f"**{channel_name}** just uploaded a new video!",
        colour=discord.Colour.red()
    )
    embed.set_image(url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg")
    embed.set_footer(text=f"YouTube Notification • Tag: {tag}")
    return embed


class YouTube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_videos.start()

    def cog_unload(self):
        self.check_videos.cancel()

    async def process_subscription(self, guild_id: str, tag: str, sub: dict):
        yt_channel_id = sub.get("yt_channel_id")
        notify_channel_id = sub.get("notify_channel")
        if not yt_channel_id or not notify_channel_id:
            return

        channel = self.bot.get_channel(int(notify_channel_id))
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(int(notify_channel_id))
            except discord.HTTPException:
                return

        feed = await fetch_feed(yt_channel_id)
        entries = [(e.get("yt_videoid", ""), e) for e in feed.entries if e.get("yt_videoid")]
        if not entries:
            return

        ids = [video_id for video_id, _ in entries]  # newest first
        seen = sub.get("seen_ids")
        if seen is None:
            # Subscription created before seen_ids existed: everything at or below the
            # last known video counts as seen. If that video is gone from the feed, just
            # seed with the current feed instead of announcing old videos again.
            last_known = sub.get("last_video_id", "")
            seen = ids[ids.index(last_known):] if last_known in ids else list(ids)
        seen = list(seen)

        new_entries = [(video_id, entry) for video_id, entry in entries if video_id not in seen]
        new_entries.reverse()  # oldest first, so notifications arrive in upload order
        new_entries = new_entries[:MAX_NOTIFICATIONS_PER_CHECK]

        if not new_entries:
            update_subscription(guild_id, tag, seen_ids=seen[:SEEN_LIMIT], last_video_id=ids[0])
            return

        channel_name = sub.get("name", "Unknown Channel")
        ping_text, allowed_mentions = build_ping(channel, sub.get("ping_role"))

        for video_id, entry in new_entries:
            embed = build_embed(entry.get("title"), video_id, channel_name, tag)
            content = f"{ping_text} 🎥 New video from **{channel_name}**!".strip()
            try:
                await channel.send(content, embed=embed, allowed_mentions=allowed_mentions)
            except discord.HTTPException as e:
                # Not marked as seen, so it is retried on the next check.
                print(f"[youtube] Could not send notification for '{tag}' in guild {guild_id}: {e}")
                break

            # Mark as seen only after the message really went out.
            seen.insert(0, video_id)
            update_subscription(guild_id, tag, seen_ids=seen[:SEEN_LIMIT], last_video_id=video_id)

    @tasks.loop(minutes=CHECK_INTERVAL)
    async def check_videos(self):
        data = load_data()
        for guild_id, subscriptions in data.items():
            for tag, sub in list(subscriptions.items()):
                try:
                    await self.process_subscription(guild_id, tag, sub)
                except Exception as e:
                    # One broken subscription (network error, bad data...) must not
                    # stop the whole loop; discord.py doesn't restart it after an unhandled error.
                    print(f"[youtube] Error while checking '{tag}' in guild {guild_id}: {e!r}")

    @check_videos.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    youtube_group = app_commands.Group(name="youtube", description="Manage YouTube notifications.")

    @youtube_group.command(name="add", description="Adds a YouTube channel notification.")
    @app_commands.describe(
        tag="A short name to identify this subscription (e.g. 'iu', 'pewdiepie')",
        channel_id="YouTube channel ID. To find it: go to the channel → About → Share → Copy channel ID.",
        notify_channel="The Discord channel to send notifications in",
        ping_role="The role to ping when a new video is uploaded (optional)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def add(self, interaction: discord.Interaction, tag: str, channel_id: str, notify_channel: discord.TextChannel, ping_role: discord.Role = None):
        await interaction.response.defer(ephemeral=True)

        guild_id = str(interaction.guild.id)
        tag = tag.lower().strip()
        data = load_data()

        if guild_id not in data:
            data[guild_id] = {}

        if tag in data[guild_id]:
            await interaction.followup.send(f"❌ A subscription with the tag `{tag}` already exists. Use `/youtube remove {tag}` first.", ephemeral=True)
            return

        yt_id = extract_channel_id(channel_id)
        if not yt_id:
            await interaction.followup.send(
                "❌ That doesn't look like a YouTube channel ID (it starts with `UC` and is 24 characters long). "
                "@handles are not supported.\n"
                "**How to find the channel ID:** Go to the YouTube channel → **About** → **Share** → **Copy channel ID**.",
                ephemeral=True
            )
            return

        perms = notify_channel.permissions_for(interaction.guild.me)
        if not (perms.view_channel and perms.send_messages and perms.embed_links):
            await interaction.followup.send(
                f"❌ I need **View Channel**, **Send Messages** and **Embed Links** in {notify_channel.mention} "
                "to post notifications there.",
                ephemeral=True
            )
            return

        feed = await fetch_feed(yt_id)
        if not feed.entries:
            await interaction.followup.send(
                "❌ Could not find a YouTube channel with that ID.\n"
                "**How to find the channel ID:** Go to the YouTube channel → **About** → **Share** → **Copy channel ID**.",
                ephemeral=True
            )
            return

        yt_channel_name = feed.feed.get("title", "Unknown Channel")
        ids = [e.get("yt_videoid", "") for e in feed.entries if e.get("yt_videoid")]

        # Re-read right before saving: the file may have changed while we were fetching the feed.
        data = load_data()
        data.setdefault(guild_id, {})
        data[guild_id][tag] = {
            "name": yt_channel_name,
            "yt_channel_id": yt_id,
            "notify_channel": str(notify_channel.id),
            "ping_role": str(ping_role.id) if ping_role else None,
            "last_video_id": ids[0] if ids else "",
            "seen_ids": ids[:SEEN_LIMIT]
        }
        save_data(data)

        ping_info = f" | Ping: {ping_role.mention}" if ping_role else ""
        await interaction.followup.send(
            f"✅ Subscribed to **{yt_channel_name}**.\n"
            f"**Tag:** `{tag}` | **Channel:** {notify_channel.mention}{ping_info}\n"
            "You'll be notified when a new video is uploaded."
            f"{ping_warning(notify_channel, ping_role)}",
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions.none()
        )

    @youtube_group.command(name="remove", description="Removes a YouTube notification subscription by tag.")
    @app_commands.describe(tag="The tag of the subscription to remove")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove(self, interaction: discord.Interaction, tag: str):
        guild_id = str(interaction.guild.id)
        tag = tag.lower().strip()
        data = load_data()

        if guild_id not in data or tag not in data[guild_id]:
            await interaction.response.send_message(f"❌ No subscription found with tag `{tag}`.", ephemeral=True)
            return

        name = data[guild_id][tag].get("name", tag)
        del data[guild_id][tag]
        save_data(data)

        await interaction.response.send_message(f"✅ Unsubscribed from **{name}** (tag: `{tag}`).", ephemeral=True)

    @youtube_group.command(name="list", description="Lists all YouTube notification subscriptions.")
    @app_commands.checks.has_permissions(administrator=True)
    async def list(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        data = load_data()
        subs = data.get(guild_id, {})

        if not subs:
            await interaction.response.send_message("❌ No YouTube subscriptions set up yet.", ephemeral=True)
            return

        embed = discord.Embed(title="🎥 YouTube Subscriptions", colour=discord.Colour.red())
        for tag, sub in subs.items():
            notify_channel = f"<#{sub['notify_channel']}>" if sub.get("notify_channel") else "Not set"
            ping_role = f"<@&{sub['ping_role']}>" if sub.get("ping_role") else "None"
            embed.add_field(
                name=f"Tag: `{tag}` — {sub.get('name', 'Unknown')}",
                value=f"**Channel:** {notify_channel} | **Ping:** {ping_role}",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @youtube_group.command(name="test", description="Sends a test notification to check the channel and role ping.")
    @app_commands.describe(tag="The tag of the subscription to test")
    @app_commands.checks.has_permissions(administrator=True)
    async def test(self, interaction: discord.Interaction, tag: str):
        guild_id = str(interaction.guild.id)
        tag = tag.lower().strip()
        sub = load_data().get(guild_id, {}).get(tag)

        if sub is None:
            await interaction.response.send_message(f"❌ No subscription found with tag `{tag}`.", ephemeral=True)
            return

        channel = interaction.guild.get_channel(int(sub["notify_channel"])) if sub.get("notify_channel") else None
        if channel is None:
            await interaction.response.send_message("❌ The notification channel no longer exists.", ephemeral=True)
            return

        role = interaction.guild.get_role(int(sub["ping_role"])) if sub.get("ping_role") else None
        ping_text, allowed_mentions = build_ping(channel, sub.get("ping_role"))
        name = sub.get("name", "Unknown Channel")

        embed = discord.Embed(
            title="Test notification",
            description=f"**{name}** — this is only a test, no new video was uploaded.",
            colour=discord.Colour.red()
        )
        embed.set_footer(text=f"YouTube Notification • Tag: {tag}")

        try:
            await channel.send(f"{ping_text} 🧪 Test notification for **{name}**".strip(), embed=embed, allowed_mentions=allowed_mentions)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"❌ I couldn't send a message in {channel.mention}: {e}", ephemeral=True)
            return

        await interaction.response.send_message(
            f"✅ Test notification sent to {channel.mention}.{ping_warning(channel, role)}",
            ephemeral=True
        )

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            message = "❌ You need administrator permissions to use this command."
        else:
            message = f"❌ Error: {error}"

        # /youtube add defers first, so the interaction may already be answered.
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

async def setup(bot):
    await bot.add_cog(YouTube(bot))
