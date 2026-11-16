import discord
from discord.ext import commands
import time

class AntiNuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.actions = {}

    def check_limit(self, uid):
        now = time.time()
        if uid not in self.actions:
            self.actions[uid] = []
        self.actions[uid] = [t for t in self.actions[uid] if now - t < 10]
        self.actions[uid].append(now)
        return len(self.actions[uid]) >= 3

    async def punish(self, guild, user, action):
        if user.bot or user.id == guild.owner_id: return
        try:
            await user.edit(roles=[])
            await guild.owner.send(f"🚨 **ANTI-NUKE TRIGGERED** in **{guild.name}**\n**User:** {user.mention}\n**Action:** Mass {action}")
        except: pass

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            if self.check_limit(entry.user.id):
                await self.punish(channel.guild, entry.user, "channel deletion")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            if self.check_limit(entry.user.id):
                await self.punish(role.guild, entry.user, "role deletion")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if self.check_limit(entry.user.id):
                await self.punish(guild, entry.user, "mass banning")

async def setup(bot):
    await bot.add_cog(AntiNuke(bot))
