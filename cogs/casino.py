import discord
from discord import app_commands
from discord.ext import commands
import db
import random
from config import THEME_COLOR, EMOJI_COIN
from ui import success_embed, error_embed, main_embed

class Casino(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="slots", description="Play the slot machine")
    async def slots(self, interaction: discord.Interaction, amount: int):
        if amount < 100:
            return await interaction.response.send_message(embed=error_embed("Minimum bet is 100 coins."), ephemeral=True)
            
        bal = await db.get_balance(interaction.guild.id, interaction.user.id)
        if bal < amount:
            return await interaction.response.send_message(embed=error_embed("You don't have enough coins."), ephemeral=True)

        emojis = ["🍒", "🍋", "💎", "7️⃣"]
        s1, s2, s3 = random.choice(emojis), random.choice(emojis), random.choice(emojis)
        
        await db.update_balance(interaction.guild.id, interaction.user.id, -amount)
        
        if s1 == s2 == s3:
            win = amount * 5
            await db.update_balance(interaction.guild.id, interaction.user.id, win)
            embed = main_embed("🎰 Slot Machine", f"**[ {s1} | {s2} | {s3} ]**\n\nJACKPOT! You won `{win:,}` {EMOJI_COIN}!")
        elif s1 == s2 or s2 == s3 or s1 == s3:
            win = int(amount * 1.5)
            await db.update_balance(interaction.guild.id, interaction.user.id, win)
            embed = main_embed("🎰 Slot Machine", f"**[ {s1} | {s2} | {s3} ]**\n\nYou matched two! You won `{win:,}` {EMOJI_COIN}!")
        else:
            embed = main_embed("🎰 Slot Machine", f"**[ {s1} | {s2} | {s3} ]**\n\nYou lost `{amount:,}` {EMOJI_COIN}.")

        await interaction.response.send_message(embed=embed)

async def setup(bot): await bot.add_cog(Casino(bot))
