import discord
from discord import app_commands
from discord.ext import commands
import urllib.parse
from ui import error_embed, main_embed
from config import THEME_COLOR

class AIImage(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="imagine", description="Generate an AI image")
    async def imagine(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer()
        
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
        
        embed = main_embed("🎨 AI Generated", f"**Prompt:** {prompt}")
        embed.set_image(url=url)
        
        await interaction.followup.send(embed=embed)

async def setup(bot): await bot.add_cog(AIImage(bot))
