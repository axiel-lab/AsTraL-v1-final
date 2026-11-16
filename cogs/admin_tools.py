import discord
from discord import app_commands
from discord.ext import commands
from ui import success_embed, error_embed
from config import THEME_COLOR, EMOJI_GEAR, EMOJI_TRASH

class AdminTools(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="admin_rename", description="Force change a user's nickname")
    @app_commands.checks.has_permissions(administrator=True)
    async def admin_rename(self, interaction: discord.Interaction, member: discord.Member, new_name: str):
        try:
            await member.edit(nick=new_name)
            await interaction.response.send_message(embed=success_embed(f"Changed {member.mention}'s nickname to **{new_name}**."), ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(embed=error_embed("I cannot rename this user (role is too high)."), ephemeral=True)

    @app_commands.command(name="admin_create_channel", description="Create a new channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def admin_create_channel(self, interaction: discord.Interaction, name: str, channel_type: str = "text", category: discord.CategoryChannel = None):
        try:
            if channel_type.lower() == "voice": channel = await interaction.guild.create_voice_channel(name=name, category=category)
            else: channel = await interaction.guild.create_text_channel(name=name, category=category)
            await interaction.response.send_message(embed=success_embed(f"{EMOJI_GEAR} Created channel: {channel.mention}"), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=error_embed(f"Error: {e}"), ephemeral=True)

    @app_commands.command(name="admin_delete_channel", description="Delete a channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def admin_delete_channel(self, interaction: discord.Interaction, channel: discord.abc.GuildChannel):
        if channel == interaction.channel: return await interaction.response.send_message(embed=error_embed("Cannot delete the channel you are in."), ephemeral=True)
        try:
            await channel.delete()
            await interaction.response.send_message(embed=success_embed(f"{EMOJI_TRASH} Deleted channel **{channel.name}**."), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(embed=error_embed(f"Error: {e}"), ephemeral=True)

async def setup(bot): await bot.add_cog(AdminTools(bot))
