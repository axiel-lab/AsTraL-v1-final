import discord
from discord.ext import commands
import db

class StickyRoles(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        roles = [r.id for r in member.roles if r.name != "@everyone" and not r.managed]
        if roles:
            await db.save_sticky_roles(member.guild.id, member.id, roles)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        roles = await db.get_sticky_roles(member.guild.id, member.id)
        if roles:
            role_objs = [member.guild.get_role(r) for r in roles]
            role_objs = [r for r in role_objs if r is not None]
            try:
                await member.add_roles(*role_objs)
            except: pass

async def setup(bot): await bot.add_cog(StickyRoles(bot))
