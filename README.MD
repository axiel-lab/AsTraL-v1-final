# Ultimate Discord Bot

A comprehensive, all-in-one Discord bot built for power, speed, and moderation.

**Author:** AXIEL
**Note:** Every line of code in this project was hand-typed and written maturely by me
---

## Features

### 🛠️ Core & Admin
- **Custom Commands:** Create, edit, and delete server-specific commands (`/cc`).
- **Moderation:** Purge messages, kick, and ban members with hierarchy checks.
- **Logging:** Track message edits, deletions, joins, and leaves in specific channels.
- **Auto-Mod:** Automatically delete Discord invites and spam mentions.
- **Welcome System:** Custom join messages with auto-role assignment.

### 🎫 Support & Community
- **Ticket System:** Full button-based ticket panel with claiming, closing, and log channels.
- **Nickname System:** Auto-clean user messages into nicknames, filtering out restricted characters, with a sticky rules embed.
- **Verification:** Button-based verification to grant access roles.
- **Reaction Roles:** Self-assign roles using reactions or buttons.
- **Polls:** Create interactive, button-based polls.

### 📈 Engagement & Economy
- **Economy:** `/daily`, `/work`, and `/balance` system to earn coins.
- **Leveling:** XP system with `/rank` and `/leaderboard`.
- **Giveaways:** Button-entry giveaways with automated timers and winner selection.
- **Starboard:** Pin the best messages to a dedicated starboard channel.
- **Quotes:** Save and randomly pull quotes from server members.

### ⚙️ Utilities & Fun
- **Standard Utils:** `/ping`, `/serverinfo`, `/userinfo`, `/avatar`.
- **Fun:** `/8ball`, `/coinflip`, `/roll`.
- **Reminders:** Set timed reminders (`/remind 10m take out trash`).
- **AFK System:** Set an AFK status and get pinged when someone mentions you.
- **Temp Voice:** Join-to-create voice channels that delete when empty.
- **Stats:** Automated voice channel counters for member counts.
- **Bump Reminders:** Tracks Disboard bumps and reminds you when it's time.

---

## Setup Instructions

1. ask axiel for bot src
2. Install dependencies:

bash
pip install -r requirements.txt
Environment Variables:
3. Create a .env file in the root directory and add your bot token and dev guild ID:
env
DISCORD_TOKEN=your_bot_token_here
DEV_GUILD_ID=your_server_id_here

4. Run the bot:
bash
py main.py