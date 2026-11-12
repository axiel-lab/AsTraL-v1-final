import discord
from discord import app_commands
from discord.ext import commands
import random
import re

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="8ball", description="Ask the magic 8-ball")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        responses = [
            "Yes.", "No.", "Maybe.", "Definitely.", "Absolutely not.", 
            "Ask again later.", "I don't know.", "Without a doubt.", "Very doubtful."
        ]
        await interaction.response.send_message(f"🎱 **Q:** {question}\n**A:** {random.choice(responses)}")

    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["Heads", "Tails"])
        await interaction.response.send_message(f"🪙 **{result}**")

    @app_commands.command(name="roll", description="Roll dice (e.g., 2d20)")
    async def roll(self, interaction: discord.Interaction, dice: str = "1d20"):
        match = re.match(r"(\d+)d(\d+)", dice.lower())
        if not match:
            return await interaction.response.send_message("❌ Use format XdY (e.g., 2d20).", ephemeral=True)
        
        num, sides = int(match.group(1)), int(match.group(2))
        if num < 1 or num > 100 or sides < 2 or sides > 1000:
            return await interaction.response.send_message("❌ Max 100 dice, max 1000 sides.", ephemeral=True)
            
        rolls = [random.randint(1, sides) for _ in range(num)]
        await interaction.response.send_message(f"🎲 **{dice}:** {', '.join(map(str, rolls))}\n**Total:** {sum(rolls)}")

    @app_commands.command(name="say", description="Make the bot say something")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def say(self, interaction: discord.Interaction, text: str):
        await interaction.response.send_message("Sent!", ephemeral=True)
        await interaction.channel.send(text)

async def setup(bot):
    await bot.add_cog(Fun(bot))