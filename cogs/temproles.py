import discord
from discord import app_commands
from discord.ext import commands, tasks
import db
import re
import time
from ui import success_embed, error_embed

class TempRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_roles.start()
    def cog_unload(self): self.check_roles.cancel()

    @app_commands.command(name="temprole", description="Give a temporary role (e.g., 1h, 2d)")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def temprole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role, duration: str):
        match = re.match(r"(\d+)([smhd])", duration.lower())
        if not match: return await interaction.response.send_message(embed=error_embed("Format: `10m`, `2h`, `1d`."), ephemeral=True)
        num, unit = int(match.group(1)), match.group(2)
        secs = num * {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[unit]
        await member.add_roles(role)
        await db.add_temp_role(interaction.guild.id, member.id, role.id, int(time.time()) + secs)
        await interaction.response.send_message(embed=success_embed(f"Gave {role.mention} to {member.mention} for {duration}."))

    @tasks.loop(seconds=30)
    async def check_roles(self):
        for gid, uid, rid in await db.get_expired_roles():
            guild = self.bot.get_guild(int(gid))
            if guild:
                member, role = guild.get_member(int(uid)), guild.get_role(int(rid))
                if member and role:
                    try: await member.remove_roles(role)
                    except: pass
            await db.remove_temp_role(gid, uid, rid)

    @check_roles.before_loop
    async def before(self): await self.bot.wait_until_ready()

async def setup(bot): await bot.add_cog(TempRoles(bot))
