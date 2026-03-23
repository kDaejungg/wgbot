import discord
from discord import app_commands
from discord.ext import commands
import json
import os

WARNS_FILE = "data/warns.json"

def load_warns():
    if not os.path.exists(WARNS_FILE):
        return {}
    with open(WARNS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_warns(data):
    with open(WARNS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class Warns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Warns a member and sends them a DM.")
    @app_commands.describe(user="The member to warn", reason="Reason for the warning")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided."):
        warns = load_warns()
        user_id = str(user.id)

        if user_id not in warns:
            warns[user_id] = []

        warns[user_id].append({
            "reason": reason,
            "moderator": str(interaction.user),
            "guild": str(interaction.guild.id)
        })
        save_warns(warns)

        warn_count = len(warns[user_id])

        try:
            dm_embed = discord.Embed(
                title="⚠️ You have received a warning",
                colour=discord.Colour.orange()
            )
            dm_embed.add_field(name="Server", value=interaction.guild.name, inline=True)
            dm_embed.add_field(name="Moderator", value=str(interaction.user), inline=True)
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.set_footer(text=f"You now have {warn_count} warning(s).")
            await user.send(embed=dm_embed)
            dm_status = "DM sent."
        except discord.Forbidden:
            dm_status = "Could not send DM (user has DMs disabled)."

        await interaction.response.send_message(
            f"⚠️ {user.mention} has been warned. Reason: {reason}\n"
            f"Total warnings: **{warn_count}** | {dm_status}",
            ephemeral=True
        )

    @app_commands.command(name="warnings", description="Displays the warnings of a member.")
    @app_commands.describe(user="The member to check")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warnings(self, interaction: discord.Interaction, user: discord.Member):
        warns = load_warns()
        user_id = str(user.id)
        user_warns = warns.get(user_id, [])

        if not user_warns:
            await interaction.response.send_message(f"✅ {user.mention} has no warnings.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"⚠️ Warnings for {user.display_name}",
            colour=discord.Colour.orange()
        )
        for i, w in enumerate(user_warns, 1):
            embed.add_field(
                name=f"Warning #{i}",
                value=f"**Reason:** {w['reason']}\n**Moderator:** {w['moderator']}",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="clearwarnings", description="Clears all warnings for a member.")
    @app_commands.describe(user="The member whose warnings to clear")
    @app_commands.checks.has_permissions(administrator=True)
    async def clearwarnings(self, interaction: discord.Interaction, user: discord.Member):
        warns = load_warns()
        user_id = str(user.id)
        warns[user_id] = []
        save_warns(warns)
        await interaction.response.send_message(f"✅ All warnings for {user.mention} have been cleared.", ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Warns(bot))
