import discord
from discord import app_commands
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Displays all available commands and their usage.")
    async def help(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="WGBot Command List",
            description="Here are all available commands and their usage.",
            colour=discord.Colour.blurple()
        )

        embed.add_field(
            name="🔨 Moderation",
            value=(
                "`/ban <user> [reason]` — Bans a member.\n"
                "`/unban <user_id>` — Unbans a user by ID.\n"
                "`/timeout <user> [minutes] [reason]` — Times out a member.\n"
                "`/warn <user> [reason]` — Warns a member via DM.\n"
                "`/warnings <user>` — Shows warnings of a member.\n"
                "`/clearwarnings <user>` — Clears all warnings of a member.\n"
                "`/delete <amount>` — Deletes messages in bulk.\n"
                "`/lock` — Locks the channel.\n"
                "`/unlock` — Unlocks the channel.\n"
                "`/slowmode <seconds>` — Sets slowmode (0 to disable)."
            ),
            inline=False
        )

        embed.add_field(
            name="🔊 Voice",
            value=(
                "`/mute-voice <user>` — Server mutes a member in voice.\n"
                "`/unmute-voice <user>` — Removes server mute from a member.\n"
                "`/move <user> <channel>` — Moves a member to another voice channel."
            ),
            inline=False
        )

        embed.add_field(
            name="🏷️ Roles",
            value=(
                "`/role <user> <role>` — Adds or removes a role from a member."
            ),
            inline=False
        )

        embed.add_field(
            name="📁 Channels",
            value=(
                "`/create-channel <name> [type]` — Creates a text or voice channel.\n"
                "Type: `text` (default) or `voice`."
            ),
            inline=False
        )

        embed.add_field(
            name="ℹ️ Info",
            value=(
                "`/userinfo [user]` — Shows member information.\n"
                "`/avatar [user]` — Shows a member's profile picture.\n"
                "`/serverinfo` — Shows server information.\n"
                "`/roles` — Lists all roles in the server."
            ),
            inline=False
        )

        embed.add_field(
            name="⭐ Rank",
            value=(
                "`/rank [user]` — Shows your rank and XP.\n"
                "`/leaderboard` — Shows the top 10 members by XP."
            ),
            inline=False
        )

        embed.add_field(
            name="🎲 Fun",
            value=(
                "`/roll [sides]` — Rolls a dice. Default is 1d6."
            ),
            inline=False
        )

        embed.add_field(
            name="⚙️ Setup (Admin only)",
            value=(
                "`/set-welcome-channel <channel>` — Sets the welcome channel.\n"
                "`/set-welcome-message <message>` — Sets the welcome message. Use `{user}` for mention.\n"
                "`/set-auto-role <role>` — Sets the auto role for new members.\n"
                "`/disable-welcome` — Disables welcome messages.\n"
                "`/disable-auto-role` — Disables auto role.\n"
                "`/settings` — Shows current bot settings."
            ),
            inline=False
        )

        embed.add_field(
            name="🤖 General",
            value=(
                "`/about` — Displays information about WGBot.\n"
                "`/help` — Shows this message."
            ),
            inline=False
        )

        embed.set_footer(text="<required> • [optional]")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
