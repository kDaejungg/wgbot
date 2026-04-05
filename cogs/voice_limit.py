import discord
from discord import app_commands
from discord.ext import commands

class VoiceLimit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="voice-limit", description="Sets the user limit for a voice channel. Use 0 to remove the limit.")
    @app_commands.describe(
        channel="The voice channel to set the limit for",
        limit="Maximum number of users (0 = unlimited, max 99)"
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def voice_limit(self, interaction: discord.Interaction, channel: discord.VoiceChannel, limit: int):
        if limit < 0 or limit > 99:
            await interaction.response.send_message("❌ Limit must be between 0 and 99. Use 0 to remove the limit.", ephemeral=True)
            return

        await channel.edit(user_limit=limit)

        if limit == 0:
            await interaction.response.send_message(f"🔓 User limit removed from **{channel.name}**.", ephemeral=True)
        else:
            await interaction.response.send_message(f"👥 User limit for **{channel.name}** set to **{limit}**.", ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(VoiceLimit(bot))
