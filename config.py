import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DEV_GUILD_ID = os.getenv("DEV_GUILD_ID")
DB_PATH = "data/bot.db"
RESERVED = {"help", "cc", "ping", "ticket", "automod", "buttonrole"}

THEME_COLOR = 0x2b2d31
BOT_NAME = "AsTraL v1"