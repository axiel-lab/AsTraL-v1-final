import discord
from discord.ext import commands, tasks
import os
import db
import random
import discord_ios
from config import DISCORD_TOKEN, DEV_GUILD_ID

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

statuses = [
    discord.Activity(type=discord.ActivityType.watching, name="over the server"),
    discord.Activity(type=discord.ActivityType.listening, name="listening to your commands "),
    discord.Activity(type=discord.ActivityType.playing, name="Made by Ax!eL")
]

@tasks.loop(seconds=30)
async def change_status():
    await bot.change_presence(activity=random.choice(statuses))

@bot.event
async def setup_hook():
    await db.init()
    
    extensions = [
        "cogs.core", "cogs.custom_commands", "cogs.moderation", "cogs.tickets", 
        "cogs.nicknames", "cogs.utility", "cogs.fun", "cogs.welcome", "cogs.giveaway", 
        "cogs.leveling", "cogs.button_roles", "cogs.automod", "cogs.mention_responder", 
        "cogs.logging", "cogs.afk", "cogs.temp_voice", "cogs.starboard", "cogs.reminders", 
        "cogs.verification", "cogs.quotes", "cogs.stats", "cogs.bump", "cogs.reaction_roles", 
        "cogs.polls", "cogs.snipe", "cogs.counting", "cogs.embeds", "cogs.warnings", 
        "cogs.lockdown", "cogs.tictactoe", "cogs.temproles", "cogs.translate", 
        "cogs.suggestions", "cogs.weather", "cogs.roleplay", "cogs.highlights", "cogs.notes"
    ]
    for ext in extensions:
        try:
            await bot.load_extension(ext)
        except Exception as e:
            print(f"Failed to load {ext}: {e}")
    
    await bot.tree.sync()
    print("Commands synced globally.")

@bot.event
async def on_ready():
    change_status.start()
    print(f"Online: {bot.user}")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CommandOnCooldown):
        msg = f"⏳ Slow down! Try again in `{error.retry_after:.2f}s`."
    elif isinstance(error, discord.app_commands.MissingPermissions):
        msg = "❌ You don't have permission to use this command."
    else:
        msg = f"❌ Error: `{str(error)}`"
        print(f"Command Error: {error}")

    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(msg, ephemeral=True)
        else:
            await interaction.followup.send(msg, ephemeral=True)
    except:
        pass

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
