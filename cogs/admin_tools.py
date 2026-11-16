import discord
from discord import app_commands
from discord.ext import commands

class AdminTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="admin_rename", description="Force change a user's nickname")
    @app_commands.checks.has_permissions(administrator=True)
    async def admin_rename(self, interaction: discord.Interaction, member: discord.Member, new_name: str):
        if not interaction.guild.me.guild_permissions.manage_nicknames:
            return await interaction.response.send_message("❌ I lack the Manage Nicknames permission.", ephemeral=True)
        
        try:
            await member.edit(nick=new_name)
            await interaction.response.send_message(f"✅ Changed {member.mention}'s nickname to **{new_name}**.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I cannot rename this user (their role is higher than mine).", ephemeral=True)

    @app_commands.command(name="admin_create_channel", description="Create a new channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def admin_create_channel(self, interaction: discord.Interaction, name: str, channel_type: str = "text", category: discord.CategoryChannel = None):
        if not interaction.guild.me.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ I lack the Manage Channels permission.", ephemeral=True)

        try:
            if channel_type.lower() == "voice":
                channel = await interaction.guild.create_voice_channel(name=name, category=category)
            else:
                channel = await interaction.guild.create_text_channel(name=name, category=category)
            
            await interaction.response.send_message(f"✅ Created channel: {channel.mention}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error creating channel: {e}", ephemeral=True)

    @app_commands.command(name="admin_delete_channel", description="Delete a channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def admin_delete_channel(self, interaction: discord.Interaction, channel: discord.abc.GuildChannel):
        if not interaction.guild.me.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ I lack the Manage Channels permission.", ephemeral=True)

        if channel == interaction.channel:
            return await interaction.response.send_message("❌ You cannot delete the channel you are currently in (Discord limitation).", ephemeral=True)

        try:
            await channel.delete()
            await interaction.response.send_message(f"🗑️ Deleted channel **{channel.name}**.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error deleting channel: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminTools(bot))
