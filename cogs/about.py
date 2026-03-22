import discord
from discord import app_commands
from discord.ext import commands
import config

class About(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="about", description="Displays information about WGBot.")
    async def about(self, interaction: discord.Interaction):
        data = config.load_about()

        embed = discord.Embed(
            title=f"✨ {data['bot_name']}",
            description=data["description"],
            colour=discord.Colour.blurple()
        )
        embed.add_field(name="Version", value=data["version"], inline=True)
        embed.add_field(name="Developer", value=data["developer"], inline=True)
        embed.add_field(name="Features", value="\n".join(f"• {f}" for f in data["features"]), inline=False)
        embed.add_field(name="Note", value=data["credits"], inline=False)
        embed.add_field(name="⚖️ License", value=data["license"], inline=True)
        embed.add_field(name="GitHub", value=f"🔗 [Source Code]({data['github_repo']})", inline=True)
        embed.set_footer(text="Made by Enes Ramazan Whitelineage")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(About(bot))
