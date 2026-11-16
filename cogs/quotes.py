import discord
from discord import app_commands
from discord.ext import commands
import db
from ui import success_embed, error_embed, main_embed
from config import EMOJI_INFO

class Quotes(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="quote_add", description="Save a quote")
    async def quote_add(self, interaction: discord.Interaction, user: discord.Member, text: str):
        await db.add_quote(interaction.guild.id, user.name, text)
        await interaction.response.send_message(embed=success_embed("Quote saved."))

    @app_commands.command(name="quote", description="Get a random quote")
    async def quote(self, interaction: discord.Interaction):
        q = await db.get_quote(interaction.guild.id)
        if not q: return await interaction.response.send_message(embed=error_embed("No quotes found."), ephemeral=True)
        await interaction.response.send_message(embed=main_embed(f"{EMOJI_INFO} Random Quote", f"*\"{q[1]}\"*\n\n— {q[0]}"))

async def setup(bot): await bot.add_cog(Quotes(bot))
