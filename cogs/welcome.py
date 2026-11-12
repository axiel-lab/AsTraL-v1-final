import discord
from discord import app_commands
from discord.ext import commands
import db

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="welcome", description="Setup welcome message and auto-role")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str, role: discord.Role = None):
        role_id = role.id if role else None
        await db.set_welcome(interaction.guild.id, channel.id, message, role_id)
        await interaction.response.send_message("✅ Welcome system configured.", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        config = await db.get_welcome(member.guild.id)
        if not config:
            return

        chan_id, msg, role_id = config
        
        # Auto-Role
        if role_id:
            role = member.guild.get_role(int(role_id))
            if role:
                try:
                    await member.add_roles(role)
                except discord.Forbidden:
                    pass

        # Welcome Message
        channel = member.guild.get_channel(int(chan_id))
        if channel:
            # Supports {user} and {server} variables
            formatted = msg.replace("{user}", member.mention).replace("{server}", member.guild.name)
            await channel.send(formatted)

async def setup(bot):
    await bot.add_cog(Welcome(bot))