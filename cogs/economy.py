import discord
from discord import app_commands
from discord.ext import commands
import db
import time
import random
from config import THEME_COLOR, EMOJI_COIN
from ui import success_embed, error_embed

class Economy(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        bal = await db.get_balance(interaction.guild.id, member.id)
        await interaction.response.send_message(embed=discord.Embed(description=f"{EMOJI_COIN} {member.mention} has **{bal:,}** coins.", color=THEME_COLOR))

    @app_commands.command(name="daily", description="Claim your daily coins")
    async def daily(self, interaction: discord.Interaction):
        now = int(time.time())
        last_daily = await db.get_daily(interaction.guild.id, interaction.user.id)
        
        if now - last_daily < 86400:
            remaining = 86400 - (now - last_daily)
            return await interaction.response.send_message(embed=error_embed(f"Already claimed. Try in **{remaining // 3600}h {(remaining % 3600) // 60}m**."), ephemeral=True)

        amount = 4000 
        await db.update_balance(interaction.guild.id, interaction.user.id, amount)
        await db.set_daily(interaction.guild.id, interaction.user.id, now)
        await interaction.response.send_message(embed=success_embed(f"You claimed your daily **{amount:,}** {EMOJI_COIN} coins!"))

    @commands.command(name="cf", description="Flip a coin to double your money")
    async def coinflip(self, ctx, amount: int):
        if amount < 100:
            return await ctx.send(embed=error_embed("Minimum bet is 100 coins."))
            
        bal = await db.get_balance(ctx.guild.id, ctx.author.id)
        if bal < amount:
            return await ctx.send(embed=error_embed("You don't have enough coins."))

        result = random.choice(["Heads", "Tails"])
        user_choice = "Heads"
        
    await db.update_balance(ctx.guild.id, ctx.author.id, -amount)

        if result == "Heads":
            await db.update_balance(ctx.guild.id, ctx.author.id, amount * 2)
            await ctx.send(embed=success_embed(f"🪙 The coin landed on **{result}**! You won `{amount:,}` coins!"))
        else:
            await ctx.send(embed=error_embed(f"🪙 The coin landed on **{result}**. You lost `{amount:,}` coins."))

async def setup(bot): await bot.add_cog(Economy(bot))
