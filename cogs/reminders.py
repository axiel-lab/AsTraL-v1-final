import discord
from discord import app_commands
from discord.ext import commands, tasks
import db
import re
import time

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()

    def cog_unload(self): self.check_reminders.cancel()

    @app_commands.command(name="remind", description="Set a reminder (e.g., 10m, 2h, 1d)")
    async def remind(self, interaction: discord.Interaction, time_str: str, text: str):
        match = re.match(r"(\d+)([smhd])", time_str.lower())
        if not match:
            return await interaction.response.send_message("❌ Use format `10m`, `2h`, `1d`.", ephemeral=True)
        
        num, unit = int(match.group(1)), match.group(2)
        seconds = num * {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[unit]
        
        await db.add_reminder(interaction.user.id, interaction.channel_id, int(time.time()) + seconds, text)
        await interaction.response.send_message(f"⏰ I'll remind you in {time_str}.", ephemeral=True)

    @tasks.loop(seconds=10)
    async def check_reminders(self):
        reminders = await db.get_reminders()
        for rid, uid, cid, text in reminders:
            channel = self.bot.get_channel(int(cid))
            if channel:
                await channel.send(f"<@{uid}> ⏰ **Reminder:** {text}")
            await db.remove_reminder(rid)

    @check_reminders.before_loop
    async def before(self): await self.bot.wait_until_ready()

async def setup(bot): await bot.add_cog(Reminders(bot))