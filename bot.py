import discord
from discord.ext import commands
import os
import config

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"✅ {filename} loaded.")

@bot.event
async def on_ready():
    await load_cogs()
    await bot.tree.sync()
    print(f"{bot.user} is online. Slash commands synchronised.")

bot.run(config.TOKEN)
