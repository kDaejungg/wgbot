import discord
from discord import app_commands
from discord.ext import commands

class DeleteConfirmView(discord.ui.View):
    def __init__(self, author: discord.User, channel: discord.abc.GuildChannel, reason: str):
        super().__init__(timeout=30)
        self.author = author
        self.channel = channel
        self.reason = reason
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Only the person who ran the command can use these buttons.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        name = self.channel.name
        try:
            await self.channel.delete(reason=f"{interaction.user} (ID: {interaction.user.id}): {self.reason}")
        except discord.Forbidden:
            await interaction.response.edit_message(content="❌ I don't have permission to delete that channel.", view=None)
            return
        except discord.HTTPException as e:
            # e.g. the rules / community updates channel of a Community server
            await interaction.response.edit_message(content=f"❌ Discord refused to delete that channel: {e.text or e}", view=None)
            return

        # The channel may have been the one this message lives in, so this can fail.
        try:
            await interaction.response.edit_message(content=f"✅ Channel `{name}` has been deleted.", view=None)
        except discord.HTTPException:
            pass

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        await interaction.response.edit_message(content="❎ Cancelled, the channel was not deleted.", view=None)

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.edit(content="⌛ Timed out, the channel was not deleted.", view=None)
            except discord.HTTPException:
                pass

class Channels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="create-channel", description="Creates a new text or voice channel.")
    @app_commands.describe(name="Channel name", channel_type="Channel type: text or voice")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def create_channel(self, interaction: discord.Interaction, name: str, channel_type: str = "text"):
        guild = interaction.guild
        if channel_type == "voice":
            channel = await guild.create_voice_channel(name)
        else:
            channel = await guild.create_text_channel(name)
        await interaction.response.send_message(f"✅ Channel `{channel.name}` has been created.", ephemeral=True)

    @app_commands.command(name="delete-channel", description="Deletes a channel (asks for confirmation first).")
    @app_commands.describe(channel="The channel to delete", reason="Why the channel is being deleted (shown in the audit log)")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    async def delete_channel(self, interaction: discord.Interaction, channel: discord.abc.GuildChannel, reason: str = "No reason provided"):
        # The option may arrive as a partial channel object; get the real one.
        target = interaction.guild.get_channel(channel.id)
        if target is None:
            try:
                target = await interaction.guild.fetch_channel(channel.id)
            except discord.HTTPException:
                await interaction.response.send_message("❌ I couldn't find that channel.", ephemeral=True)
                return

        # has_permissions only checks the server-wide permission; channel overrides can take it away.
        if not target.permissions_for(interaction.user).manage_channels:
            await interaction.response.send_message("❌ You don't have permission to manage that channel.", ephemeral=True)
            return
        if not target.permissions_for(interaction.guild.me).manage_channels:
            await interaction.response.send_message("❌ I don't have permission to manage that channel.", ephemeral=True)
            return

        note = ""
        if isinstance(target, discord.CategoryChannel) and target.channels:
            note = f"\nThis category contains **{len(target.channels)}** channel(s). They will **not** be deleted, they just lose their category."

        view = DeleteConfirmView(interaction.user, target, reason)
        await interaction.response.send_message(
            f"⚠️ Are you sure you want to delete **{target.name}** ({target.mention})? This cannot be undone.{note}",
            view=view,
            ephemeral=True
        )
        view.message = await interaction.original_response()

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            message = "❌ You don't have permission to use this command."
        elif isinstance(error, app_commands.BotMissingPermissions):
            message = "❌ I need the **Manage Channels** permission to do that."
        else:
            message = f"❌ Error: {error}"

        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Channels(bot))
