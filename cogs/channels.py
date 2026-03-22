import discord
from discord import app_commands
from discord.ext import commands

class Channels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="create-channel", description="Creates a new text or voice channel.")
    @app_commands.describe(name="Channel name", channel_type="Channel type: text or voice")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def create_channel(self, interaction: discord.Interaction, name: str, channel_type: str = "text"):
        guild = interaction.guild
        if channel_type == "voice":
            channel = await guild.create_voice_channel(name)
        else:
            channel = await guild.create_text_channel(name)
        await interaction.response.send_message(f"✅ Channel `{channel.name}` has been created.", ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Channels(bot))
