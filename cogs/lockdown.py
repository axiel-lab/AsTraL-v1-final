import discord
from discord import app_commands
from discord.ext import commands
from config import EMOJI_LOCK, EMOJI_UNLOCK
from ui import success_embed

class Lockdown(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="lock", description="Lock the current channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message(embed=success_embed(f"{EMOJI_LOCK} Channel locked."))

    @app_commands.command(name="unlock", description="Unlock the current channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
        await interaction.response.send_message(embed=success_embed(f"{EMOJI_UNLOCK} Channel unlocked."))

async def setup(bot): await bot.add_cog(Lockdown(bot))
