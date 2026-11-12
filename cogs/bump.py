import discord
from discord.ext import commands
import db
import time

class Bump(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.id == 302050872383242240: # Disboard Bot ID
            if "Bump done!" in msg.content or "Bump Done!" in msg.content:
                await db.set_bump(msg.guild.id, int(time.time()) + 7200) # 2 hours
                await msg.channel.send("✅ Bump recorded. I will remind you in 2 hours.", delete_after=5)
        
        if msg.content == "!bumptime":
            end = await db.get_bump(msg.guild.id)
            if end > int(time.time()):
                rem = end - int(time.time())
                await msg.reply(f"⏳ Bump available in {rem//60}m {rem%60}s.")
            else:
                await msg.reply("🚀 It's time to bump! `/bump`")

async def setup(bot): await bot.add_cog(Bump(bot))