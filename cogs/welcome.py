import discord
from discord.ext import commands
import config

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        settings = config.load_settings()

        role_id = settings.get("auto_role")
        if role_id:
            role = member.guild.get_role(int(role_id))
            if role:
                await member.add_roles(role)

        channel_id = settings.get("welcome_channel")
        message = settings.get("welcome_message", "Welcome to the server, {user}!")
        if channel_id:
            channel = member.guild.get_channel(int(channel_id))
            if channel:
                await channel.send(message.replace("{user}", member.mention))

async def setup(bot):
    await bot.add_cog(Welcome(bot))
