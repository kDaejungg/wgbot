import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import random

AUTOREPLIES_FILE = "data/autoreplies.json"

def load_autoreplies():
    if not os.path.exists(AUTOREPLIES_FILE):
        return {}
    with open(AUTOREPLIES_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_autoreplies(data):
    with open(AUTOREPLIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

class AutoReply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        guild_id = str(message.guild.id)
        autoreplies = load_autoreplies()
        guild_replies = autoreplies.get(guild_id, {})

        content = message.content.lower().strip()
        if content in guild_replies:
            responses = guild_replies[content]
            await message.channel.send(random.choice(responses))

    autoreply_group = app_commands.Group(name="autoreply", description="Manage automatic replies.")

    @autoreply_group.command(name="add", description="Adds an automatic reply. Separate multiple responses with commas.")
    @app_commands.describe(trigger="The message that triggers the reply", response="Response(s) separated by commas")
    @app_commands.checks.has_permissions(administrator=True)
    async def add(self, interaction: discord.Interaction, trigger: str, response: str):
        guild_id = str(interaction.guild.id)
        autoreplies = load_autoreplies()
        trigger = trigger.lower().strip()

        if guild_id not in autoreplies:
            autoreplies[guild_id] = {}

        if trigger not in autoreplies[guild_id]:
            autoreplies[guild_id][trigger] = []

        new_responses = [r.strip() for r in response.split(",") if r.strip()]
        autoreplies[guild_id][trigger].extend(new_responses)
        save_autoreplies(autoreplies)

        count = len(autoreplies[guild_id][trigger])
        added_list = "\n".join(f"• `{r}`" for r in new_responses)
        await interaction.response.send_message(
            f"✅ {len(new_responses)} response(s) added to trigger `{trigger}`.\n{added_list}\n**Total responses for this trigger:** {count}",
            ephemeral=True
        )

    @autoreply_group.command(name="remove", description="Removes an entire trigger and all its responses.")
    @app_commands.describe(trigger="The trigger to remove")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove(self, interaction: discord.Interaction, trigger: str):
        guild_id = str(interaction.guild.id)
        autoreplies = load_autoreplies()
        trigger = trigger.lower().strip()

        if guild_id not in autoreplies or trigger not in autoreplies[guild_id]:
            await interaction.response.send_message("❌ No auto reply found for that trigger.", ephemeral=True)
            return

        del autoreplies[guild_id][trigger]
        save_autoreplies(autoreplies)

        await interaction.response.send_message(f"✅ Auto reply for `{trigger}` removed.", ephemeral=True)

    @autoreply_group.command(name="list", description="Lists all automatic replies.")
    @app_commands.checks.has_permissions(administrator=True)
    async def list(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        autoreplies = load_autoreplies()
        guild_replies = autoreplies.get(guild_id, {})

        if not guild_replies:
            await interaction.response.send_message("❌ No auto replies set up yet.", ephemeral=True)
            return

        embed = discord.Embed(title="💬 Auto Replies", colour=discord.Colour.blurple())
        for trigger, responses in guild_replies.items():
            response_list = "\n".join(f"• `{r}`" for r in responses)
            embed.add_field(
                name=f"Trigger: `{trigger}` ({len(responses)} response(s))",
                value=response_list,
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AutoReply(bot))
