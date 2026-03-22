import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def hierarchy_check(self, interaction: discord.Interaction, user: discord.Member) -> str | None:
        """Returns an error message if hierarchy is violated, None if OK."""
        if user == interaction.guild.owner:
            return "❌ You cannot perform this action on the server owner."
        if user.top_role >= interaction.guild.me.top_role:
            return "⚠️ I cannot perform this action as this member has a higher or equal role to mine."
        if user.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            return "⚠️ You cannot perform this action on a member with a higher or equal role to yours."
        return None

    @app_commands.command(name="ban", description="Bans a member from the server.")
    @app_commands.describe(user="The member to ban", reason="Reason for the ban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided."):
        error = self.hierarchy_check(interaction, user)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        await user.ban(reason=reason)
        await interaction.response.send_message(f"🔨 {user.mention} has been banned. Reason: {reason}", ephemeral=True)

    @app_commands.command(name="unban", description="Unbans a user from the server.")
    @app_commands.describe(user_id="The ID of the user to unban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        try:
            user = await interaction.client.fetch_user(int(user_id))
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"✅ {user} has been unbanned.", ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message("❌ No ban found for this user ID.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Invalid user ID.", ephemeral=True)

    @app_commands.command(name="timeout", description="Times out a member.")
    @app_commands.describe(user="The member to time out", minutes="Duration in minutes", reason="Reason for the timeout")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, minutes: int = 10, reason: str = "No reason provided."):
        error = self.hierarchy_check(interaction, user)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        duration = timedelta(minutes=minutes)
        await user.timeout(duration, reason=reason)
        await interaction.response.send_message(f"⏱️ {user.mention} has been timed out for {minutes} minute(s). Reason: {reason}", ephemeral=True)

    @app_commands.command(name="delete", description="Deletes a number of messages from the channel.")
    @app_commands.describe(amount="Number of messages to delete")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def delete(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🗑️ {len(deleted)} message(s) deleted.", ephemeral=True)

    @app_commands.command(name="lock", description="Locks the channel for everyone.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = False
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message("🔒 Channel locked.", ephemeral=True)

    @app_commands.command(name="unlock", description="Unlocks the channel.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = True
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message("🔓 Channel unlocked.", ephemeral=True)

    @app_commands.command(name="slowmode", description="Sets the slowmode for the current channel.")
    @app_commands.describe(seconds="Slowmode delay in seconds (0 to disable)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, seconds: int):
        if seconds < 0 or seconds > 21600:
            await interaction.response.send_message("❌ Slowmode must be between 0 and 21600 seconds.", ephemeral=True)
            return
        await interaction.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await interaction.response.send_message("✅ Slowmode disabled.", ephemeral=True)
        else:
            await interaction.response.send_message(f"🐢 Slowmode set to **{seconds}** second(s).", ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
