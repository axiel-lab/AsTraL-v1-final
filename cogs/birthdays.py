import discord
from discord import app_commands
from discord.ext import commands, tasks
import db
from datetime import datetime

class Birthdays(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bday_loop.start()

    def cog_unload(self): self.bday_loop.cancel()

    @app_commands.command(name="setup_birthdays", description="Setup birthday announcements")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_bday(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await db.set_birthday_channel(interaction.guild.id, channel.id)
        await interaction.response.send_message(f"✅ Birthdays will be announced in {channel.mention}.", ephemeral=True)

    @app_commands.command(name="set_birthday", description="Set your birthday (YYYY-MM-DD)")
    async def set_bday(self, interaction: discord.Interaction, date: str):
        try:
            d = datetime.strptime(date, "%Y-%m-%d")
            await db.set_birthday(interaction.guild.id, interaction.user.id, d.month, d.day)
            await interaction.response.send_message(f"🎂 Birthday set to {d.strftime('%B %d')}!", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Invalid format. Use YYYY-MM-DD.", ephemeral=True)

    @tasks.loop(hours=24)
    async def bday_loop(self):
        now = datetime.utcnow()
        for guild in self.bot.guilds:
            chan_id = await db.get_birthday_channel(guild.id)
            if not chan_id: continue
            channel = guild.get_channel(int(chan_id))
            if not channel: continue
            
            users = await db.get_todays_birthdays(guild.id, now.month, now.day)
            for uid in users:
                member = guild.get_member(int(uid))
                if member:
                    embed = discord.Embed(title="🎉 Happy Birthday!", description=f"Everyone wish {member.mention} a happy birthday!", color=discord.Color.gold())
                    embed.set_thumbnail(url=member.display_avatar.url)
                    await channel.send(embed=embed)

    @bday_loop.before_loop
    async def before_bday(self): await self.bot.wait_until_ready()

async def setup(bot): await bot.add_cog(Birthdays(bot))
