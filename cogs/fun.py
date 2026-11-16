import discord
from discord import app_commands
from discord.ext import commands
import random
import re
from config import THEME_COLOR, EMOJI_STAR

class Fun(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="8ball", description="Ask the magic 8-ball")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        responses = ["Yes.", "No.", "Maybe.", "Definitely.", "Absolutely not.", "Ask again later.", "I don't know.", "Without a doubt.", "Very doubtful."]
        embed = discord.Embed(title="🎱 Magic 8-Ball", description=f"**Q:** {question}\n**A:** {random.choice(responses)}", color=THEME_COLOR)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        embed = discord.Embed(description=f"🪙 **{random.choice(['Heads', 'Tails'])}**", color=THEME_COLOR)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roll", description="Roll dice (e.g., 2d20)")
    async def roll(self, interaction: discord.Interaction, dice: str = "1d20"):
        match = re.match(r"(\d+)d(\d+)", dice.lower())
        if not match:
            return await interaction.response.send_message(embed=discord.Embed(description="❌ Use format XdY (e.g., 2d20).", color=THEME_COLOR), ephemeral=True)
        
        num, sides = int(match.group(1)), int(match.group(2))
        if num < 1 or num > 100 or sides < 2 or sides > 1000:
            return await interaction.response.send_message(embed=discord.Embed(description="❌ Max 100 dice, max 1000 sides.", color=THEME_COLOR), ephemeral=True)
            
        rolls = [random.randint(1, sides) for _ in range(num)]
        embed = discord.Embed(title=f"{EMOJI_STAR} Dice Roll", description=f"**{dice}:** {', '.join(map(str, rolls))}\n**Total:** {sum(rolls)}", color=THEME_COLOR)
        await interaction.response.send_message(embed=embed)

async def setup(bot): await bot.add_cog(Fun(bot))
