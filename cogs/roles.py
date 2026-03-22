import discord
from discord import app_commands
from discord.ext import commands

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="role", description="Adds or removes a role from a member.")
    @app_commands.describe(user="The member", role="The role to add or remove")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def role(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                "⚠️ I cannot manage this role as it is higher than or equal to my highest role.",
                ephemeral=True
            )
            return
        if role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            await interaction.response.send_message(
                "⚠️ You cannot manage a role that is higher than or equal to your own highest role.",
                ephemeral=True
            )
            return

        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"✅ Removed {role.mention} from {user.mention}.", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"✅ Added {role.mention} to {user.mention}.", ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Roles(bot))
