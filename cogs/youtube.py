import discord
from discord import app_commands
from discord.ext import commands, tasks
import feedparser
import json
import os

YOUTUBE_FILE = "data/youtube.json"
CHECK_INTERVAL = 5  # minutes

def load_data():
    if not os.path.exists(YOUTUBE_FILE):
        return {}
    with open(YOUTUBE_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_data(data):
    with open(YOUTUBE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_feed_url(channel_id: str) -> str:
    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

class YouTube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_videos.start()

    def cog_unload(self):
        self.check_videos.cancel()

    @tasks.loop(minutes=CHECK_INTERVAL)
    async def check_videos(self):
        data = load_data()
        for guild_id, subscriptions in data.items():
            for tag, sub in subscriptions.items():
                yt_channel_id = sub.get("yt_channel_id")
                notify_channel_id = sub.get("notify_channel")
                ping_role_id = sub.get("ping_role")

                if not yt_channel_id or not notify_channel_id:
                    continue

                channel = self.bot.get_channel(int(notify_channel_id))
                if not channel:
                    continue

                feed = feedparser.parse(get_feed_url(yt_channel_id))
                if not feed.entries:
                    continue

                latest = feed.entries[0]
                latest_id = latest.get("yt_videoid", "")
                last_known = sub.get("last_video_id", "")

                if latest_id and latest_id != last_known:
                    data[guild_id][tag]["last_video_id"] = latest_id
                    save_data(data)

                    if not last_known:
                        continue

                    video_url = f"https://www.youtube.com/watch?v={latest_id}"
                    thumbnail = f"https://img.youtube.com/vi/{latest_id}/maxresdefault.jpg"
                    yt_channel_name = sub.get("name", "Unknown Channel")

                    embed = discord.Embed(
                        title=latest.get("title", "New Video"),
                        url=video_url,
                        description=f"**{yt_channel_name}** just uploaded a new video!",
                        colour=discord.Colour.red()
                    )
                    embed.set_image(url=thumbnail)
                    embed.set_footer(text=f"YouTube Notification • Tag: {tag}")

                    ping = f"<@&{ping_role_id}> " if ping_role_id else ""
                    await channel.send(f"{ping}🎥 New video from **{yt_channel_name}**!", embed=embed)

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

        feed = feedparser.parse(get_feed_url(channel_id))
        if not feed.entries:
            await interaction.followup.send(
                "❌ Could not find a YouTube channel with that ID.\n"
                "**How to find the channel ID:** Go to the YouTube channel → **About** → **Share** → **Copy channel ID**.",
                ephemeral=True
            )
            return

        yt_channel_name = feed.feed.get("title", "Unknown Channel")
        latest_video_id = feed.entries[0].get("yt_videoid", "") if feed.entries else ""

        data[guild_id][tag] = {
            "name": yt_channel_name,
            "yt_channel_id": channel_id,
            "notify_channel": str(notify_channel.id),
            "ping_role": str(ping_role.id) if ping_role else None,
            "last_video_id": latest_video_id
        }
        save_data(data)

        ping_info = f" | Ping: {ping_role.mention}" if ping_role else ""
        await interaction.followup.send(
            f"✅ Subscribed to **{yt_channel_name}**.\n"
            f"**Tag:** `{tag}` | **Channel:** {notify_channel.mention}{ping_info}\n"
            "You'll be notified when a new video is uploaded.",
            ephemeral=True
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

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(YouTube(bot))
