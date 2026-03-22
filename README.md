# WGBot (v1.0.0)
An open source Discord moderation bot with slash commands, supporting ban, timeout, warn, rank system, voice management, and more. Configured entirely through Discord without touching any config files.

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

✅ Administrator

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
