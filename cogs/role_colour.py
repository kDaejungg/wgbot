import discord
from discord import app_commands
from discord.ext import commands

class RoleColour(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="role-colour", description="Changes the colour of a role using a HEX code.")
    @app_commands.describe(
        role="The role to recolour",
        hex_code="HEX colour code (e.g. #FF5733 or FF5733)"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def role_colour(self, interaction: discord.Interaction, role: discord.Role, hex_code: str):
        hex_code = hex_code.lstrip("#").strip()

        if len(hex_code) != 6:
            await interaction.response.send_message("❌ Invalid HEX code. Example: `#FF5733` or `FF5733`.", ephemeral=True)
            return

        try:
            colour_int = int(hex_code, 16)
        except ValueError:
            await interaction.response.send_message("❌ Invalid HEX code. Use only hex characters (0-9, A-F).", ephemeral=True)
            return

        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ I can't edit a role that is higher than or equal to my top role.", ephemeral=True)
            return

        if role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            await interaction.response.send_message("❌ You can't edit a role that is higher than or equal to your top role.", ephemeral=True)
            return

        colour = discord.Colour(colour_int)
        await role.edit(colour=colour)

        embed = discord.Embed(
            description=f"🎨 **{role.mention}** colour changed to `#{hex_code.upper()}`.",
            colour=colour
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleColour(bot))
