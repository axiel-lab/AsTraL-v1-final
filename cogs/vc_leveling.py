import discord
from discord.ext import commands, tasks
import db
import math

class VCLeveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vc_loop.start()

    def cog_unload(self):
        self.vc_loop.cancel()

    @tasks.loop(minutes=1)
    async def vc_loop(self):
        for guild in self.bot.guilds:
            for vc in guild.voice_channels:
                if len(vc.members) > 1:
                    for member in vc.members:
                        if member.bot or member.voice.self_deaf or member.voice.deaf:
                            continue
                        gid, uid = str(guild.id), str(member.id)
                        xp, level, last = await db.get_level_data(gid, uid)
                        new_xp = xp + 10
                        new_level = int(math.isqrt(new_xp // 100))
                        
                        await db.update_level_data(gid, uid, new_xp, new_level, 0)
                        
                        if new_level > level:
                            await member.send(f"🎉 You leveled up to **Level {new_level}** by hanging out in voice chat!")

    @vc_loop.before_loop
    async def before_vc(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(VCLeveling(bot))
