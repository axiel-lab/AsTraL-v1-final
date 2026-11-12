import discord
from discord import app_commands
from discord.ext import commands
import db

class Quotes(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="quote_add", description="Save a quote")
    async def quote_add(self, interaction: discord.Interaction, user: discord.Member, text: str):
        await db.add_quote(interaction.guild.id, user.name, text)
        await interaction.response.send_message("✅ Quote saved.")

    @app_commands.command(name="quote", description="Get a random quote")
    async def quote(self, interaction: discord.Interaction):
        q = await db.get_quote(interaction.guild.id)
        if not q: return await interaction.response.send_message("No quotes found.", ephemeral=True)
        embed = discord.Embed(description=f"*\"{q[1]}\"*", color=discord.Color.purple())
        embed.set_footer(text=f"— {q[0]}")
        await interaction.response.send_message(embed=embed)

async def setup(bot): await bot.add_cog(Quotes(bot))