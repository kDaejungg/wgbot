import discord
from discord.ext import commands
import os
import config

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class WGBot(commands.Bot):
    async def setup_hook(self):
        # Every cog stores its data in ./data; a fresh clone does not have it yet.
        os.makedirs("data", exist_ok=True)

        # setup_hook runs exactly once, unlike on_ready which fires again on every
        # reconnect (and would try to load the cogs a second time).
        for filename in sorted(os.listdir("./cogs")):
            if filename.endswith(".py") and filename != "__init__.py":
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    print(f"✅ {filename} loaded.")
                except Exception as e:
                    # e.g. a missing dependency; the rest of the bot should still start.
                    print(f"❌ {filename} failed to load: {e!r}")

        await self.tree.sync()
        print("Slash commands synchronised.")

bot = WGBot(command_prefix=commands.when_mentioned, intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is online.")

bot.run(config.TOKEN)
