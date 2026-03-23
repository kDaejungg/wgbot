# WGBot (v1.1.0)
An open source Discord moderation bot with slash commands, supporting ban, timeout, warn, rank system, voice management, and more. Configured entirely through Discord without touching any config files.

## ⚠️ If you only want to add the bot to your server, use this link and ignore the steps below: [![Discord Invite](https://img.shields.io/badge/Discord-Add_to_Server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/oauth2/authorize?client_id=1485221526084128910&permissions=8&integration_type=0&scope=bot)
---

## ✨ Features

### 🔨 Moderation
- **Ban, kick & unban** members with automatic hierarchy checks
- **Timeout** members for a specified duration
- **Warn system** with automatic DM notifications and persistent warn records
- **Bulk message deletion** with auto-deleting confirmation
- **Lock & unlock** channels instantly
- **Slowmode** per channel

### 🔊 Voice
- **Server mute & unmute** members in voice channels
- **Move** members between voice channels

### 🏷️ Roles
- **Add or remove roles** from members with hierarchy validation

### 📁 Channels
- **Create** text or voice channels via slash command

### ℹ️ Info
- **Member info** — joined date, roles, account age and more
- **Avatar** — display any member's profile picture
- **Server info** — member count, boost level, creation date and more
- **Role list** — all roles in the server at a glance

### ⭐ Rank & XP
- Members earn **15–25 XP** per message (60-second cooldown to prevent spam)
- **Level-up announcements** in channel
- **Role rewards** — assign roles automatically when members reach specific levels
- `/rank` and `/leaderboard` commands

### 💬 Auto Reply
- Set up **automatic replies** triggered by specific messages
- **Multiple responses per trigger** (bot picks one at random)
- Add multiple responses at once by separating them with commas

### 🎥 YouTube Notifications
- Subscribe to **multiple YouTube channels** per server
- Notifications sent to a designated channel with an embed and optional role ping
- Identified by **custom tags** for easy management
- Checks for new videos every **5 minutes** via RSS (no API key required)

### 🎲 Fun
- **Dice roller** with customisable number of sides

### ⚙️ Setup
- **Welcome messages** with customisable text and member mention
- **Auto role** assignment on member join
- All settings configured **entirely through Discord**

---

# Installation

Follow the steps according to your OS.

## Configuration
After completing step one of the installation section, follow these steps:

The bot needs a **Discord Bot Token** to run. If you don't know how to get one, go to the [Discord Developer Portal](https://discord.com/developers/applications), create an application, and copy your token from the **Bot** tab.

### Step-by-Step Token Setup:

1. **Show Hidden Files:**
   - **Windows:** In the folder, click the "View" tab and check "Hidden Items".
   - **Linux / macOS:** Press `Ctrl + H` inside the folder to reveal the `.env` file.

2. **Paste Your Token:**
   - Open the `.env` file with Notepad or any text editor.
   - Replace `DISCORD_TOKEN=` with your token: `DISCORD_TOKEN=your_token_here`
   - Save and close the file.

> All other settings (welcome channel, auto role) are configured directly in Discord via the `/set-welcome-channel`, `/set-welcome-message`, and `/set-auto-role` commands. No need to edit any files.

### Enable Privileged Intents
Go to the [Discord Developer Portal](https://discord.com/developers/applications), select your application, click the **Bot** tab, and enable the following:

- ✅ Server Members Intent
- ✅ Message Content Intent

---

## Linux

Python is usually pre-installed on Linux. Open your terminal and follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kDaejungg/wgbot.git
   ```

   ⚠️ FOLLOW THE CONFIGURATION STEPS MENTIONED ABOVE BEFORE CONTINUING

   ```bash
   cd wgbot
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

4. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the bot:**
   ```bash
   python3 bot.py
   ```

---

## Windows

You can use PowerShell or Command Prompt (CMD). Make sure Python is added to your system PATH.

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/kDaejungg/wgbot.git
   ```

   ⚠️ FOLLOW THE CONFIGURATION STEPS MENTIONED ABOVE BEFORE CONTINUING

   ```powershell
   cd wgbot
   ```

2. **Create a virtual environment:**
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   ```powershell
   .\venv\Scripts\activate
   ```

4. **Install requirements:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Run the bot:**
   ```powershell
   python bot.py
   ```

---

## macOS

Mac users can follow these steps using the Terminal app:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kDaejungg/wgbot.git
   ```

   ⚠️ FOLLOW THE CONFIGURATION STEPS MENTIONED ABOVE BEFORE CONTINUING

   ```bash
   cd wgbot
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

4. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the bot:**
   ```bash
   python3 bot.py
   ```

---

## Adding the Bot to Your Server

After running the bot, follow these steps to invite it to your server:

### 1. Generate an OAuth2 Link
1. Go to the **[Discord Developer Portal](https://discord.com/developers/applications)** and select your application.
2. In the left menu, click **OAuth2** → **URL Generator**.
3. Under **Scopes**, check the following:
   - [x] `bot`
   - [x] `applications.commands` (required for slash commands)

### 2. Select Required Permissions
Under **Bot Permissions**, check exactly the following:

**General Permissions**

✅ Manage Roles

✅ Manage Channels

✅ Kick Members

✅ Ban Members

✅ Moderate Members

**Text Permissions**

✅ Send Messages

✅ Manage Messages

✅ Embed Links

✅ Read Message History

✅ Use Slash Commands

**Voice Permissions**

✅ Mute Members

✅ Move Members

### 3. Invite
4. Copy the **Generated URL** at the bottom of the page.
5. Paste it into your browser and invite the bot to your server.

> **⚠️ Note:** If slash commands don't appear after adding the bot, restart your Discord client or make sure the bot has the "Use Application Commands" permission.

---

## 📂 File Structure

```
WGBot/
├── bot.py              # Main bot engine, loads all cogs automatically
├── config.py           # Token loader and settings manager
├── settings.json       # Saved bot configuration
├── about.json          # Bot identity info (version, developer)
├── requirements.txt    # Required Python libraries
├── .env                # Your bot token (never share this)
├── .gitignore          # Prevents token and unnecessary files from being pushed to GitHub
├── data/
│   ├── warns.json      # Warning records (auto-generated)
│   └── ranks.json      # XP and rank data (auto-generated)
└── cogs/
    ├── moderation.py   # ban, unban, timeout, delete, lock, unlock, slowmode
    ├── warns.py        # warn, warnings, clearwarnings
    ├── voice.py        # mute-voice, unmute-voice, move
    ├── roles.py        # role add/remove
    ├── channels.py     # create-channel
    ├── info.py         # userinfo, avatar, serverinfo, roles
    ├── rank.py         # rank, leaderboard, XP system
    ├── fun.py          # roll
    ├── welcome.py      # welcome messages and auto role on member join
    ├── setup.py        # set-welcome-channel, set-welcome-message, set-auto-role, settings
    ├── about.py        # about
    └── help.py         # help
```

## ⚠️ Important Security Note
Never share your `.env` file or commit it to a public repository. The `.gitignore` file already excludes it, but always double-check before pushing.

---
*Made by Enes Ramazan Whitelineage*

#### Contact & feedback: [Discord](https://discord.gg/vV8gEpHDXH)
