import discord
from discord import app_commands
from discord.ext import commands

# Up to 9 options — each gets a number emoji
NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="poll", description="Creates a poll with up to 9 options. Separate options with a semicolon ( ; ).")
    @app_commands.describe(
        question="The poll question",
        options="Options separated by semicolons. Example: Yes ; No ; Maybe"
    )
    async def poll(self, interaction: discord.Interaction, question: str, options: str):
        option_list = [o.strip() for o in options.split(";") if o.strip()]

        if len(option_list) < 2:
            await interaction.response.send_message("❌ You need at least 2 options. Separate them with `;`.\nExample: `Yes ; No ; Maybe`", ephemeral=True)
            return

        if len(option_list) > 9:
            await interaction.response.send_message("❌ Maximum 9 options allowed.", ephemeral=True)
            return

        description = "\n".join(
            f"{NUMBER_EMOJIS[i]}  {option}" for i, option in enumerate(option_list)
        )

        embed = discord.Embed(
            title=f"📊 {question}",
            description=description,
            colour=discord.Colour.blurple()
        )
        embed.set_footer(text=f"Poll by {interaction.user.display_name} • React to vote!")

        await interaction.response.send_message("✅ Poll created!", ephemeral=True)
        poll_msg = await interaction.channel.send(embed=embed)

        for i in range(len(option_list)):
            await poll_msg.add_reaction(NUMBER_EMOJIS[i])

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Poll(bot))
