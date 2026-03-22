import discord
from discord import app_commands
from discord.ext import commands
import config

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set-welcome-channel", description="Sets the welcome channel for new members.")
    @app_commands.describe(channel="The channel to send welcome messages in")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        settings = config.load_settings()
        settings["welcome_channel"] = str(channel.id)
        config.save_settings(settings)
        await interaction.response.send_message(f"✅ Welcome channel set to {channel.mention}.", ephemeral=True)

    @app_commands.command(name="set-welcome-message", description="Sets the welcome message. Use {user} as a placeholder for the member mention.")
    @app_commands.describe(message="Welcome message text. Use {user} for the member mention.")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_welcome_message(self, interaction: discord.Interaction, message: str):
        settings = config.load_settings()
        settings["welcome_message"] = message
        config.save_settings(settings)
        await interaction.response.send_message(f"✅ Welcome message set to: `{message}`", ephemeral=True)

    @app_commands.command(name="set-auto-role", description="Sets the role to be assigned automatically when a member joins.")
    @app_commands.describe(role="The role to assign to new members")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_auto_role(self, interaction: discord.Interaction, role: discord.Role):
        settings = config.load_settings()
        settings["auto_role"] = str(role.id)
        config.save_settings(settings)
        await interaction.response.send_message(f"✅ Auto role set to {role.mention}.", ephemeral=True)

    @app_commands.command(name="disable-welcome", description="Disables welcome messages.")
    @app_commands.checks.has_permissions(administrator=True)
    async def disable_welcome(self, interaction: discord.Interaction):
        settings = config.load_settings()
        settings["welcome_channel"] = None
        config.save_settings(settings)
        await interaction.response.send_message("✅ Welcome messages disabled.", ephemeral=True)

    @app_commands.command(name="disable-auto-role", description="Disables auto role assignment.")
    @app_commands.checks.has_permissions(administrator=True)
    async def disable_auto_role(self, interaction: discord.Interaction):
        settings = config.load_settings()
        settings["auto_role"] = None
        config.save_settings(settings)
        await interaction.response.send_message("✅ Auto role disabled.", ephemeral=True)

    @app_commands.command(name="settings", description="Displays the current bot settings.")
    @app_commands.checks.has_permissions(administrator=True)
    async def settings(self, interaction: discord.Interaction):
        data = config.load_settings()

        welcome_channel = f"<#{data['welcome_channel']}>" if data.get("welcome_channel") else "Not set"
        welcome_message = data.get("welcome_message") or "Not set"
        auto_role = f"<@&{data['auto_role']}>" if data.get("auto_role") else "Not set"

        embed = discord.Embed(title="⚙️ WGBot Settings", colour=discord.Colour.blurple())
        embed.add_field(name="Welcome Channel", value=welcome_channel, inline=True)
        embed.add_field(name="Auto Role", value=auto_role, inline=True)
        embed.add_field(name="Welcome Message", value=f"`{welcome_message}`", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Setup(bot))
