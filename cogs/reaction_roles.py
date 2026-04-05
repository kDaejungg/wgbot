import discord
from discord import app_commands
from discord.ext import commands
import json
import os

FILE = "data/reactionroles.json"

def load():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    rr_group = app_commands.Group(name="reactionrole", description="Manage reaction roles.")

    @rr_group.command(name="add", description="Adds a reaction role to a message.")
    @app_commands.describe(
        message_id="The ID of the message to add the reaction role to",
        emoji="The emoji users will react with",
        role="The role to assign when reacted"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rr_add(self, interaction: discord.Interaction, message_id: str, emoji: str, role: discord.Role):
        try:
            msg = await interaction.channel.fetch_message(int(message_id))
        except (discord.NotFound, ValueError):
            await interaction.response.send_message("❌ Message not found in this channel. Make sure you're in the right channel.", ephemeral=True)
            return

        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ I can't assign a role that is higher than or equal to my top role.", ephemeral=True)
            return

        if role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            await interaction.response.send_message("❌ You can't assign a role that is higher than or equal to your top role.", ephemeral=True)
            return

        data = load()
        guild_id = str(interaction.guild.id)
        msg_id = str(msg.id)

        data.setdefault(guild_id, {})
        data[guild_id].setdefault(msg_id, {})

        if len(data[guild_id][msg_id]) >= 20:
            await interaction.response.send_message("❌ Maximum 20 reaction roles per message.", ephemeral=True)
            return

        data[guild_id][msg_id][emoji] = str(role.id)
        save(data)

        try:
            await msg.add_reaction(emoji)
        except discord.HTTPException:
            await interaction.response.send_message("❌ Invalid emoji. Make sure it's a standard emoji or one from this server.", ephemeral=True)
            # Rollback
            del data[guild_id][msg_id][emoji]
            if not data[guild_id][msg_id]:
                del data[guild_id][msg_id]
            save(data)
            return

        await interaction.response.send_message(
            f"✅ Reaction role added: {emoji} → {role.mention} on message `{msg_id}`.",
            ephemeral=True
        )

    @rr_group.command(name="remove", description="Removes a reaction role from a message.")
    @app_commands.describe(
        message_id="The ID of the message",
        emoji="The emoji to remove"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rr_remove(self, interaction: discord.Interaction, message_id: str, emoji: str):
        data = load()
        guild_id = str(interaction.guild.id)
        msg_id = message_id.strip()

        if guild_id not in data or msg_id not in data[guild_id] or emoji not in data[guild_id][msg_id]:
            await interaction.response.send_message("❌ No reaction role found for that emoji on that message.", ephemeral=True)
            return

        del data[guild_id][msg_id][emoji]
        if not data[guild_id][msg_id]:
            del data[guild_id][msg_id]
        save(data)

        try:
            msg = await interaction.channel.fetch_message(int(msg_id))
            await msg.clear_reaction(emoji)
        except Exception:
            pass

        await interaction.response.send_message(f"✅ Reaction role removed: {emoji} from message `{msg_id}`.", ephemeral=True)

    @rr_group.command(name="list", description="Lists all reaction roles in this server.")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rr_list(self, interaction: discord.Interaction):
        data = load()
        guild_id = str(interaction.guild.id)

        if guild_id not in data or not data[guild_id]:
            await interaction.response.send_message("📋 No reaction roles configured.", ephemeral=True)
            return

        embed = discord.Embed(title="🎭 Reaction Roles", colour=discord.Colour.blurple())

        for msg_id, emojis in data[guild_id].items():
            lines = []
            for emoji, role_id in emojis.items():
                role = interaction.guild.get_role(int(role_id))
                role_name = role.mention if role else f"*(deleted role `{role_id}`)*"
                lines.append(f"{emoji} → {role_name}")
            embed.add_field(
                name=f"Message `{msg_id}`",
                value="\n".join(lines),
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        data = load()
        guild_id = str(payload.guild_id)
        msg_id = str(payload.message_id)
        emoji = str(payload.emoji)

        if guild_id not in data or msg_id not in data[guild_id]:
            return

        role_id = data[guild_id][msg_id].get(emoji)
        if not role_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        role = guild.get_role(int(role_id))

        if member and role:
            try:
                await member.add_roles(role, reason="Reaction role")
            except discord.Forbidden:
                pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        data = load()
        guild_id = str(payload.guild_id)
        msg_id = str(payload.message_id)
        emoji = str(payload.emoji)

        if guild_id not in data or msg_id not in data[guild_id]:
            return

        role_id = data[guild_id][msg_id].get(emoji)
        if not role_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        role = guild.get_role(int(role_id))

        if member and role:
            try:
                await member.remove_roles(role, reason="Reaction role removed")
            except discord.Forbidden:
                pass

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
