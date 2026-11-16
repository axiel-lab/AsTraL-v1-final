import discord
from discord.ext import commands, tasks
import db

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_stats.start()
    def cog_unload(self): self.update_stats.cancel()

    @tasks.loop(minutes=10)
    async def update_stats(self):
        for gid, cid, stype in await db.get_stats():
            channel = self.bot.get_channel(int(cid))
            if channel and stype == "members":
                try: await channel.edit(name=f"👥 Members: {channel.guild.member_count}")
                except: pass

    @update_stats.before_loop
    async def before(self): await self.bot.wait_until_ready()

async def setup(bot): await bot.add_cog(Stats(bot))
