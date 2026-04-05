import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import io
import json
import os

TICKETS_FILE = "data/tickets.json"

def load_tickets_config():
    if not os.path.exists(TICKETS_FILE):
        return {}
    with open(TICKETS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_tickets_config(data):
    with open(TICKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_guild_config(guild_id: str) -> dict:
    return load_tickets_config().get(guild_id, {})

def is_configured(guild_id: str) -> bool:
    cfg = get_guild_config(guild_id)
    return bool(cfg.get("ticket_channel_id") and cfg.get("staff_role_id"))

def has_staff_role(interaction: discord.Interaction) -> bool:
    cfg = get_guild_config(str(interaction.guild.id))
    staff_role_id = cfg.get("staff_role_id")
    if not staff_role_id:
        return interaction.user.guild_permissions.administrator
    return any(role.id == int(staff_role_id) for role in interaction.user.roles)

TICKET_TYPES = {
    "ticket": {
        "emoji": "🎫",
        "color": discord.Color.dark_grey(),
        "label": "Ticket",
        "questions": [
            "Describe your issue or request:",
        ],
    },
    "bug": {
        "emoji": "🐛",
        "color": discord.Color.red(),
        "label": "Bug Report",
        "questions": [
            "Briefly describe the bug:",
            "How did you trigger it? (step by step):",
            "What was the expected behaviour?:",
        ],
    },
    "feedback": {
        "emoji": "💡",
        "color": discord.Color.blue(),
        "label": "Feedback",
        "questions": [
            "Share your feedback:",
            "What improvement would you suggest?:",
        ],
    },
    "support": {
        "emoji": "🛠️",
        "color": discord.Color.green(),
        "label": "Support Request",
        "questions": [
            "Describe your issue:",
            "Have you tried solving this before?:",
        ],
    },
}

class TicketSetupModal(discord.ui.Modal):
    def __init__(self, ticket_type: str, guild_id: str):
        self.ticket_type = ticket_type
        self.guild_id = guild_id
        data = TICKET_TYPES[ticket_type]
        super().__init__(title=f"{data['emoji']} {data['label']} — Setup")

        self.embed_title = discord.ui.TextInput(
            label="Embed Title",
            default=f"{data['emoji']} {data['label']}",
            max_length=100,
        )
        self.embed_desc = discord.ui.TextInput(
            label="Embed Description",
            style=discord.TextStyle.paragraph,
            default=f"Click the button below to start a {data['label'].lower()}.",
            max_length=1000,
        )
        self.button_label = discord.ui.TextInput(
            label="Button Label",
            default="Open Ticket",
            max_length=80,
        )
        self.add_item(self.embed_title)
        self.add_item(self.embed_desc)
        self.add_item(self.button_label)

    async def on_submit(self, interaction: discord.Interaction):
        data = TICKET_TYPES[self.ticket_type]
        cfg = get_guild_config(self.guild_id)

        embed = discord.Embed(
            title=self.embed_title.value,
            description=self.embed_desc.value,
            color=data["color"],
        )
        embed.set_footer(text="WGBot Tickets")

        view = OpenTicketView(self.ticket_type, self.button_label.value)
        channel = interaction.guild.get_channel(int(cfg["ticket_channel_id"]))

        if not channel:
            await interaction.response.send_message("❌ Ticket channel not found. Run `/ticket-setup` first.", ephemeral=True)
            return

        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"✅ Setup complete in {channel.mention}", ephemeral=True)

class OpenTicketView(discord.ui.View):
    def __init__(self, ticket_type: str, button_label: str):
        super().__init__(timeout=None)
        styles = {
            "bug": discord.ButtonStyle.danger,
            "feedback": discord.ButtonStyle.primary,
            "support": discord.ButtonStyle.success,
        }
        button = discord.ui.Button(
            label=button_label,
            style=styles.get(ticket_type, discord.ButtonStyle.secondary),
            custom_id=f"wgbot_open_{ticket_type}",
        )
        button.callback = self.callback
        self.add_item(button)

    async def callback(self, interaction: discord.Interaction):
        ticket_type = interaction.data["custom_id"].replace("wgbot_open_", "")
        await handle_ticket(interaction, ticket_type)

class CloseTicketView(discord.ui.View):
    def __init__(self, owner_id: int):
        super().__init__(timeout=None)
        self.owner_id = owner_id

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.secondary, custom_id="wgbot_close_btn")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not (interaction.user.id == self.owner_id or has_staff_role(interaction)):
            await interaction.response.send_message("❌ No permission.", ephemeral=True)
            return

        await interaction.response.send_message("🔒 Closing and generating transcript...")

        log_str = f"Ticket Transcript: {interaction.channel.name}\n" + "=" * 30 + "\n"
        async for m in interaction.channel.history(limit=None, oldest_first=True):
            log_str += f"[{m.created_at.strftime('%Y-%m-%d %H:%M')}] {m.author}: {m.content}\n"

        file = discord.File(
            io.BytesIO(log_str.encode()),
            filename=f"transcript-{interaction.channel.name}.txt",
        )

        cfg = get_guild_config(str(interaction.guild.id))
        log_channel_id = cfg.get("log_channel_id")
        if log_channel_id:
            log_chan = interaction.guild.get_channel(int(log_channel_id))
            if log_chan:
                await log_chan.send(file=file)

        await asyncio.sleep(3)
        await interaction.channel.delete()

active_sessions = set()

async def handle_ticket(interaction: discord.Interaction, ticket_type: str):
    user = interaction.user
    guild = interaction.guild
    guild_id = str(guild.id)

    if not is_configured(guild_id):
        await interaction.response.send_message("⚠️ Bot is not configured yet. Ask an admin to run `/ticket-setup`.", ephemeral=True)
        return

    if user.id in active_sessions:
        await interaction.response.send_message("⚠️ You already have an active session.", ephemeral=True)
        return

    data = TICKET_TYPES[ticket_type]
    await interaction.response.send_message(f"{data['emoji']} Questions sent to your DMs!", ephemeral=True)

    active_sessions.add(user.id)
    try:
        answers = await ask_questions_dm(interaction.client, user, data)
    finally:
        active_sessions.discard(user.id)

    if not answers:
        return

    cfg = get_guild_config(guild_id)
    ticket_channel = guild.get_channel(int(cfg["ticket_channel_id"]))
    if not ticket_channel:
        await interaction.followup.send("❌ Ticket channel not found. Ask an admin to run `/ticket-setup`.", ephemeral=True)
        return

    staff_role = guild.get_role(int(cfg["staff_role_id"])) if cfg.get("staff_role_id") else None
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
    }
    if staff_role:
        overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

    category = ticket_channel.category
    channel = await guild.create_text_channel(
        name=f"{ticket_type}-{user.name}",
        category=category,
        overwrites=overwrites,
    )

    embed = discord.Embed(title=f"{data['label']} — {user.name}", color=data["color"])
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text=f"User ID: {user.id}")
    for q, a in zip(data["questions"], answers):
        embed.add_field(name=f"❓ {q}", value=a or "*(empty)*", inline=False)

    ping_role_id = cfg.get("ping_role_id")
    ping = f"<@&{ping_role_id}>" if ping_role_id else ""
    await channel.send(content=f"{ping} {user.mention}", embed=embed)
    await channel.send(view=CloseTicketView(user.id))

async def ask_questions_dm(bot, user: discord.User, data: dict):
    try:
        dm = await user.create_dm()
        intro = discord.Embed(
            title=f"{data['emoji']} {data['label']}",
            description="Answer each question. Type `cancel` to stop. (3 min per question)",
            color=data["color"],
        )
        await dm.send(embed=intro)

        answers = []
        for i, q in enumerate(data["questions"], 1):
            await dm.send(f"**{i}/{len(data['questions'])}.** {q}")
            msg = await bot.wait_for(
                "message",
                timeout=180,
                check=lambda m: m.author == user and m.guild is None,
            )
            if msg.content.lower() == "cancel":
                await dm.send("❌ Cancelled.")
                return None
            answers.append(msg.content)

        await dm.send("✅ Processing your ticket...")
        return answers
    except (discord.Forbidden, asyncio.TimeoutError):
        return None

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for t in TICKET_TYPES:
            self.bot.add_view(OpenTicketView(t, "Open Ticket"))
        self.bot.add_view(CloseTicketView(0))

    @app_commands.command(name="ticket-setup", description="Configure the ticket system. (Admin only)")
    @app_commands.describe(
        ticket_channel="Channel where ticket embeds will be posted",
        staff_role="Role that can manage tickets",
        log_channel="Channel where ticket transcripts will be sent",
        ping_role="Role to ping when a new ticket is opened (optional)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_setup(self, interaction: discord.Interaction,
                           ticket_channel: discord.TextChannel,
                           staff_role: discord.Role,
                           log_channel: discord.TextChannel,
                           ping_role: discord.Role = None):
        guild_id = str(interaction.guild.id)
        data = load_tickets_config()

        data[guild_id] = {
            "ticket_channel_id": str(ticket_channel.id),
            "staff_role_id": str(staff_role.id),
            "log_channel_id": str(log_channel.id),
            "ping_role_id": str(ping_role.id) if ping_role else None,
        }
        save_tickets_config(data)

        embed = discord.Embed(title="✅ Ticket System Configured", color=discord.Color.green())
        embed.add_field(name="Ticket Channel", value=ticket_channel.mention, inline=False)
        embed.add_field(name="Log Channel", value=log_channel.mention, inline=False)
        embed.add_field(name="Staff Role", value=staff_role.mention, inline=False)
        embed.add_field(name="Ping Role", value=ping_role.mention if ping_role else "Not set", inline=False)
        embed.set_footer(text="You can now use /ticket /bugticket /feedbackticket /supportticket")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ticket", description="Create a ticket embed in the ticket channel. (Staff only)")
    async def ticket(self, interaction: discord.Interaction):
        if not has_staff_role(interaction):
            await interaction.response.send_message("❌ You need the staff role to use this command.", ephemeral=True)
            return
        await interaction.response.send_modal(TicketSetupModal("ticket", str(interaction.guild.id)))

    @app_commands.command(name="bugticket", description="Create a bug report embed in the ticket channel. (Staff only)")
    async def bugticket(self, interaction: discord.Interaction):
        if not has_staff_role(interaction):
            await interaction.response.send_message("❌ You need the staff role to use this command.", ephemeral=True)
            return
        await interaction.response.send_modal(TicketSetupModal("bug", str(interaction.guild.id)))

    @app_commands.command(name="feedbackticket", description="Create a feedback embed in the ticket channel. (Staff only)")
    async def feedbackticket(self, interaction: discord.Interaction):
        if not has_staff_role(interaction):
            await interaction.response.send_message("❌ You need the staff role to use this command.", ephemeral=True)
            return
        await interaction.response.send_modal(TicketSetupModal("feedback", str(interaction.guild.id)))

    @app_commands.command(name="supportticket", description="Create a support request embed in the ticket channel. (Staff only)")
    async def supportticket(self, interaction: discord.Interaction):
        if not has_staff_role(interaction):
            await interaction.response.send_message("❌ You need the staff role to use this command.", ephemeral=True)
            return
        await interaction.response.send_modal(TicketSetupModal("support", str(interaction.guild.id)))

    @app_commands.command(name="ticket-config", description="Show current ticket system configuration. (Staff only)")
    async def ticket_config(self, interaction: discord.Interaction):
        if not has_staff_role(interaction) and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Access denied.", ephemeral=True)
            return

        cfg = get_guild_config(str(interaction.guild.id))
        embed = discord.Embed(title="🎫 Ticket System Configuration", color=discord.Color.blurple())
        embed.add_field(name="Ticket Channel", value=f"<#{cfg['ticket_channel_id']}>" if cfg.get("ticket_channel_id") else "Not set", inline=False)
        embed.add_field(name="Log Channel", value=f"<#{cfg['log_channel_id']}>" if cfg.get("log_channel_id") else "Not set", inline=False)
        embed.add_field(name="Staff Role", value=f"<@&{cfg['staff_role_id']}>" if cfg.get("staff_role_id") else "Not set", inline=False)
        embed.add_field(name="Ping Role", value=f"<@&{cfg['ping_role_id']}>" if cfg.get("ping_role_id") else "Not set", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
