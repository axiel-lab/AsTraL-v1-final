import discord
from discord import app_commands
from discord.ext import commands, tasks
import db

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_stats.start()

    def cog_unload(self): self.update_stats.cancel()

    @app_commands.command(name="setup_stats", description="Setup member count channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_stats(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        await db.set_stat(interaction.guild.id, channel.id, "members")
        await interaction.response.send_message("✅ Stats channel setup. (Lock the channel so users can't join).", ephemeral=True)

    @tasks.loop(minutes=10)
    async def update_stats(self):
        for gid, cid, stype in await db.get_stats():
            channel = self.bot.get_channel(int(cid))
            if channel:
                guild = channel.guild
                try:
                    if stype == "members":
                        await channel.edit(name=f"👥 Members: {guild.member_count}")
                except: pass

    @update_stats.before_loop
    async def before(self): await self.bot.wait_until_ready()

async def setup(bot): await bot.add_cog(Stats(bot))