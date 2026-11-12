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
    discord.Activity(type=discord.ActivityType.watching, name="judging your messages"),
    discord.Activity(type=discord.ActivityType.listening, name="listening to your commands "),
    discord.Activity(type=discord.ActivityType.playing, name="made by Ax!eL")
]

@tasks.loop(seconds=30)
async def change_status():
    await bot.change_presence(activity=random.choice(statuses))

@bot.event
async def setup_hook():
    if not os.path.exists("data"):
        os.makedirs("data")
        
    await db.init()
    
    await bot.load_extension("cogs.core")
    await bot.load_extension("cogs.custom_commands")
    await bot.load_extension("cogs.moderation")
    await bot.load_extension("cogs.tickets")
    await bot.load_extension("cogs.nicknames")
    await bot.load_extension("cogs.utility")
    await bot.load_extension("cogs.fun")
    await bot.load_extension("cogs.welcome")
    await bot.load_extension("cogs.giveaway")
    await bot.load_extension("cogs.leveling")
    await bot.load_extension("cogs.button_roles")
    await bot.load_extension("cogs.automod")
    await bot.load_extension("cogs.mention_responder")
    await bot.load_extension("cogs.logging")
    await bot.load_extension("cogs.afk")
    await bot.load_extension("cogs.temp_voice")
    await bot.load_extension("cogs.starboard")
    await bot.load_extension("cogs.reminders")
    await bot.load_extension("cogs.verification")
    await bot.load_extension("cogs.quotes")
    await bot.load_extension("cogs.stats")
    await bot.load_extension("cogs.bump")
    await bot.load_extension("cogs.reaction_roles")
    await bot.load_extension("cogs.polls")
    await bot.load_extension("cogs.snipe")
    await bot.load_extension("cogs.counting")
    await bot.load_extension("cogs.embeds")
    await bot.load_extension("cogs.warnings")
    await bot.load_extension("cogs.lockdown")
    await bot.load_extension("cogs.tictactoe")
    await bot.load_extension("cogs.temproles")
    await bot.load_extension("cogs.translate")
    await bot.load_extension("cogs.suggestions")
    await bot.load_extension("cogs.weather")
    await bot.load_extension("cogs.roleplay")
    await bot.load_extension("cogs.highlights")
    await bot.load_extension("cogs.notes")
    
    if DEV_GUILD_ID:
        guild = discord.Object(id=int(DEV_GUILD_ID))
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        print("Commands synced to dev guild.")
    else:
        await bot.tree.sync()
        print("Commands synced globally.")

@bot.event
async def on_ready():
    change_status.start()
    print(f"Online: {bot.user}")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)