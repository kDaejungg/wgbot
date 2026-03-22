import discord
from discord import app_commands
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="userinfo", description="Displays information about a member.")
    @app_commands.describe(user="The member to look up (defaults to yourself)")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        roles = [r.mention for r in user.roles if r != interaction.guild.default_role]

        embed = discord.Embed(
            title=f"👤 {user.display_name}",
            colour=user.colour
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Username", value=str(user), inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Bot", value="Yes" if user.bot else "No", inline=True)
        embed.add_field(name="Account Created", value=discord.utils.format_dt(user.created_at, style="D"), inline=True)
        embed.add_field(name="Joined Server", value=discord.utils.format_dt(user.joined_at, style="D"), inline=True)
        embed.add_field(name=f"Roles ({len(roles)})", value=" ".join(roles) if roles else "None", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Displays a member's profile picture.")
    @app_commands.describe(user="The member whose avatar to display (defaults to yourself)")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        embed = discord.Embed(title=f"🖼️ {user.display_name}'s Avatar", colour=discord.Colour.blurple())
        embed.set_image(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Displays information about the server.")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(
            title=f"🏠 {guild.name}",
            colour=discord.Colour.blurple()
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Boosts", value=guild.premium_subscription_count, inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(guild.created_at, style="D"), inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roles", description="Lists all roles in the server.")
    async def roles(self, interaction: discord.Interaction):
        role_list = [r.mention for r in reversed(interaction.guild.roles) if r != interaction.guild.default_role]
        chunks = [role_list[i:i+20] for i in range(0, len(role_list), 20)]

        embed = discord.Embed(
            title=f"🏷️ Roles ({len(role_list)})",
            description=" ".join(role_list[:20]),
            colour=discord.Colour.blurple()
        )
        if len(chunks) > 1:
            embed.set_footer(text=f"Showing 20 of {len(role_list)} roles.")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))
