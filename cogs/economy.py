import discord
from discord import app_commands
from discord.ext import commands
import db
import time
import random
from config import THEME_COLOR, EMOJI_COIN, EMOJI_ERROR, EMOJI_WARNING
from ui import success_embed, error_embed

class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        bal = await db.get_balance(interaction.guild.id, member.id)
        await interaction.response.send_message(embed=discord.Embed(description=f"{EMOJI_COIN} {member.mention} has **{bal}** coins.", color=THEME_COLOR))

    @app_commands.command(name="daily", description="Claim your daily coins")
    async def daily(self, interaction: discord.Interaction):
        now = int(time.time())
        last_daily = await db.get_daily(interaction.guild.id, interaction.user.id)
        
        if now - last_daily < 86400:
            remaining = 86400 - (now - last_daily)
            return await interaction.response.send_message(embed=error_embed(f"Already claimed today. Try in **{remaining // 3600}h {(remaining % 3600) // 60}m**."), ephemeral=True)

        amount = random.randint(50, 150)
        await db.update_balance(interaction.guild.id, interaction.user.id, amount)
        await db.set_daily(interaction.guild.id, interaction.user.id, now)
        await interaction.response.send_message(embed=success_embed(f"You claimed your daily reward of **{amount}** {EMOJI_COIN} coins!"))

    @app_commands.command(name="work", description="Work for some coins")
    @app_commands.checks.cooldown(1, 3600)
    async def work(self, interaction: discord.Interaction):
        jobs = ["programmer", "streamer", "moderator", "artist", "chef"]
        amount = random.randint(10, 50)
        await db.update_balance(interaction.guild.id, interaction.user.id, amount)
        await interaction.response.send_message(embed=success_embed(f"You worked as a **{random.choice(jobs)}** and earned **{amount}** {EMOJI_COIN}!"))

async def setup(bot): await bot.add_cog(Economy(bot))
