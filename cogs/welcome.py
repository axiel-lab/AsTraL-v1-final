import discord
from discord import app_commands
from discord.ext import commands
import db
from ui import success_embed, error_embed, main_embed
from config import EMOJI_INFO

class Welcome(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="welcome", description="Setup welcome message and auto-role")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str, role: discord.Role = None):
        role_id = role.id if role else None
        await db.set_welcome(interaction.guild.id, channel.id, message, role_id)
        await interaction.response.send_message(embed=success_embed("Welcome system configured."), ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        config = await db.get_welcome(member.guild.id)
        if not config: return
        chan_id, msg, role_id = config
        if role_id:
            role = member.guild.get_role(int(role_id))
            if role:
                try: await member.add_roles(role)
                except: pass
        channel = member.guild.get_channel(int(chan_id))
        if channel:
            formatted = msg.replace("{user}", member.mention).replace("{server}", member.guild.name)
            await channel.send(embed=main_embed(f"{EMOJI_INFO} Welcome!", formatted))

async def setup(bot): await bot.add_cog(Welcome(bot))
