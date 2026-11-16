import discord
from discord import app_commands
from discord.ext import commands
from deep_translator import GoogleTranslator
import asyncio
from ui import error_embed, main_embed
from config import EMOJI_INFO

class Translate(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="translate", description="Translate text")
    async def translate(self, interaction: discord.Interaction, language_code: str, text: str):
        await interaction.response.defer()
        try:
            translated = await asyncio.to_thread(GoogleTranslator(source='auto', target=language_code).translate, text)
            await interaction.followup.send(embed=main_embed(f"{EMOJI_INFO} Translated ({language_code})", translated))
        except Exception as e:
            await interaction.followup.send(embed=error_embed(f"Error: {e}"), ephemeral=True)

async def setup(bot): await bot.add_cog(Translate(bot))
