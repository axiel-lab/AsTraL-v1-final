import discord
from discord import app_commands
from discord.ext import commands
import db
from ui import success_embed, error_embed

class Prefix(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="set_prefix", description="Change the bot's prefix for this server")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_prefix(self, interaction: discord.Interaction, new_prefix: str):
        if len(new_prefix) > 5:
            return await interaction.response.send_message(embed=error_embed("Prefix cannot be longer than 5 characters."), ephemeral=True)
        
        await db.set_prefix(interaction.guild.id, new_prefix)
        await interaction.response.send_message(embed=success_embed(f"Prefix changed to `{new_prefix}`."), ephemeral=True)

async def setup(bot): await bot.add_cog(Prefix(bot))
