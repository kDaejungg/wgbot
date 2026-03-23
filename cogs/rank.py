import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import random
import time

RANK_FILE = "data/ranks.json"
LEVELROLES_FILE = "data/levelroles.json"

def load_ranks():
    if not os.path.exists(RANK_FILE):
        return {}
    with open(RANK_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_ranks(data):
    with open(RANK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_levelroles():
    if not os.path.exists(LEVELROLES_FILE):
        return {}
    with open(LEVELROLES_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_levelroles(data):
    with open(LEVELROLES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def xp_for_level(level):
    return 100 * (level ** 2)

class Rank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._cooldowns = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        user_id = str(message.author.id)
        guild_id = str(message.guild.id)
        key = f"{guild_id}-{user_id}"

        now = time.time()
        if key in self._cooldowns and now - self._cooldowns[key] < 60:
            return
        self._cooldowns[key] = now

        ranks = load_ranks()
        if guild_id not in ranks:
            ranks[guild_id] = {}
        if user_id not in ranks[guild_id]:
            ranks[guild_id][user_id] = {"xp": 0, "level": 1}

        gained_xp = random.randint(15, 25)
        ranks[guild_id][user_id]["xp"] += gained_xp
        current_xp = ranks[guild_id][user_id]["xp"]
        current_level = ranks[guild_id][user_id]["level"]

        if current_xp >= xp_for_level(current_level):
            ranks[guild_id][user_id]["level"] += 1
            new_level = ranks[guild_id][user_id]["level"]
            save_ranks(ranks)

            await message.channel.send(
                f"🎉 {message.author.mention} levelled up to **Level {new_level}**!"
            )

            levelroles = load_levelroles()
            guild_roles = levelroles.get(guild_id, {})
            role_id = guild_roles.get(str(new_level))
            if role_id:
                role = message.guild.get_role(int(role_id))
                if role:
                    try:
                        await message.author.add_roles(role)
                        await message.channel.send(
                            f"🏷️ {message.author.mention} has been given the **{role.name}** role for reaching Level {new_level}!"
                        )
                    except discord.Forbidden:
                        pass
        else:
            save_ranks(ranks)

    @app_commands.command(name="rank", description="Displays your rank and XP.")
    @app_commands.describe(user="The member to check (defaults to yourself)")
    async def rank(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        guild_id = str(interaction.guild.id)
        user_id = str(user.id)

        ranks = load_ranks()
        data = ranks.get(guild_id, {}).get(user_id, {"xp": 0, "level": 1})

        current_xp = data["xp"]
        current_level = data["level"]
        next_level_xp = xp_for_level(current_level)

        embed = discord.Embed(
            title=f"⭐ {user.display_name}'s Rank",
            colour=discord.Colour.gold()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Level", value=current_level, inline=True)
        embed.add_field(name="XP", value=f"{current_xp} / {next_level_xp}", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="Displays the top 10 members by XP.")
    async def leaderboard(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        ranks = load_ranks()
        guild_data = ranks.get(guild_id, {})

        if not guild_data:
            await interaction.response.send_message("❌ No rank data found for this server.", ephemeral=False)
            return

        sorted_users = sorted(guild_data.items(), key=lambda x: x[1]["xp"], reverse=True)[:10]

        embed = discord.Embed(title="🏆 Leaderboard", colour=discord.Colour.gold())
        description = ""
        for i, (user_id, data) in enumerate(sorted_users, 1):
            member = interaction.guild.get_member(int(user_id))
            name = member.display_name if member else f"Unknown ({user_id})"
            description += f"**#{i}** {name} — Level {data['level']} ({data['xp']} XP)\n"

        embed.description = description
        await interaction.response.send_message(embed=embed)

    levelrole_group = app_commands.Group(name="levelrole", description="Manage level-based role rewards.")

    @levelrole_group.command(name="add", description="Assigns a role to be given when a member reaches a specific level.")
    @app_commands.describe(level="The level at which the role is given", role="The role to assign")
    @app_commands.checks.has_permissions(administrator=True)
    async def levelrole_add(self, interaction: discord.Interaction, level: int, role: discord.Role):
        if level < 1:
            await interaction.response.send_message("❌ Level must be at least 1.", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        levelroles = load_levelroles()

        if guild_id not in levelroles:
            levelroles[guild_id] = {}

        levelroles[guild_id][str(level)] = str(role.id)
        save_levelroles(levelroles)

        await interaction.response.send_message(
            f"✅ {role.mention} will be given to members who reach **Level {level}**.", ephemeral=False
        )

    @levelrole_group.command(name="remove", description="Removes the role reward for a specific level.")
    @app_commands.describe(level="The level to remove the role reward from")
    @app_commands.checks.has_permissions(administrator=True)
    async def levelrole_remove(self, interaction: discord.Interaction, level: int):
        guild_id = str(interaction.guild.id)
        levelroles = load_levelroles()

        if guild_id not in levelroles or str(level) not in levelroles[guild_id]:
            await interaction.response.send_message(f"❌ No role reward set for Level {level}.", ephemeral=True)
            return

        del levelroles[guild_id][str(level)]
        save_levelroles(levelroles)

        await interaction.response.send_message(f"✅ Role reward for **Level {level}** removed.", ephemeral=False)

    @levelrole_group.command(name="list", description="Lists all level role rewards.")
    async def levelrole_list(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        levelroles = load_levelroles()
        guild_roles = levelroles.get(guild_id, {})

        if not guild_roles:
            await interaction.response.send_message("❌ No level role rewards set up yet.", ephemeral=False)
            return

        embed = discord.Embed(title="🏷️ Level Role Rewards", colour=discord.Colour.gold())
        sorted_levels = sorted(guild_roles.items(), key=lambda x: int(x[0]))
        description = "\n".join(f"**Level {lvl}** → <@&{role_id}>" for lvl, role_id in sorted_levels)
        embed.description = description

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Rank(bot))
