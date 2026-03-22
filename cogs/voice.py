import discord
from discord import app_commands
from discord.ext import commands

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mute-voice", description="Server mutes a member in voice channel.")
    @app_commands.describe(user="The member to mute")
    @app_commands.checks.has_permissions(mute_members=True)
    async def mute_voice(self, interaction: discord.Interaction, user: discord.Member):
        if not user.voice:
            await interaction.response.send_message("❌ This member is not in a voice channel.", ephemeral=True)
            return
        await user.edit(mute=True)
        await interaction.response.send_message(f"🔇 {user.mention} has been muted in voice.", ephemeral=True)

    @app_commands.command(name="unmute-voice", description="Removes server mute from a member in voice channel.")
    @app_commands.describe(user="The member to unmute")
    @app_commands.checks.has_permissions(mute_members=True)
    async def unmute_voice(self, interaction: discord.Interaction, user: discord.Member):
        if not user.voice:
            await interaction.response.send_message("❌ This member is not in a voice channel.", ephemeral=True)
            return
        await user.edit(mute=False)
        await interaction.response.send_message(f"🔊 {user.mention} has been unmuted in voice.", ephemeral=True)

    @app_commands.command(name="move", description="Moves a member to another voice channel.")
    @app_commands.describe(user="The member to move", channel="The target voice channel")
    @app_commands.checks.has_permissions(move_members=True)
    async def move(self, interaction: discord.Interaction, user: discord.Member, channel: discord.VoiceChannel):
        if not user.voice:
            await interaction.response.send_message("❌ This member is not in a voice channel.", ephemeral=True)
            return
        await user.move_to(channel)
        await interaction.response.send_message(f"➡️ {user.mention} has been moved to **{channel.name}**.", ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Voice(bot))
