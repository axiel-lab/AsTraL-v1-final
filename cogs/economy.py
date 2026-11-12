import discord
from discord import app_commands
from discord.ext import commands
import db
import time
import random

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        bal = await db.get_balance(interaction.guild.id, member.id)
        await interaction.response.send_message(f"💰 {member.mention} has **{bal}** coins.")

    @app_commands.command(name="daily", description="Claim your daily coins")
    async def daily(self, interaction: discord.Interaction):
        now = int(time.time())
        last_daily = await db.get_daily(interaction.guild.id, interaction.user.id)
        
        # 24 hours in seconds
        if now - last_daily < 86400:
            remaining = 86400 - (now - last_daily)
            hours = remaining // 3600
            mins = (remaining % 3600) // 60
            return await interaction.response.send_message(f"❌ You already claimed today. Try again in **{hours}h {mins}m**.", ephemeral=True)

        amount = random.randint(50, 150)
        await db.update_balance(interaction.guild.id, interaction.user.id, amount)
        await db.set_daily(interaction.guild.id, interaction.user.id, now)
        
        await interaction.response.send_message(f"💸 You claimed your daily reward of **{amount}** coins!")

    @app_commands.command(name="work", description="Work for some coins")
    @app_commands.checks.cooldown(1, 3600) # 1 use per hour
    async def work(self, interaction: discord.Interaction):
        jobs = ["programmer", "streamer", "moderator", "artist", "chef"]
        job = random.choice(jobs)
        amount = random.randint(10, 50)
        
        await db.update_balance(interaction.guild.id, interaction.user.id, amount)
        await interaction.response.send_message(f"💼 You worked as a **{job}** and earned **{amount}** coins!")

async def setup(bot):
    await bot.add_cog(Economy(bot))