import discord
from discord import app_commands
from discord.ext import commands
from config import THEME_COLOR, EMOJI_INFO, EMOJI_GEAR, EMOJI_VOICE

class Utility(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(embed=discord.Embed(description=f"{EMOJI_GEAR} Pong! `{latency}ms`", color=THEME_COLOR))

    @app_commands.command(name="serverinfo", description="Get server information")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=f"{EMOJI_INFO} {guild.name}", color=THEME_COLOR)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Members", value=f"`{guild.member_count}`", inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(guild.created_at, style="D"), inline=True)
        if guild.icon: embed.set_thumbnail(url=guild.icon.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Get user information")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"{EMOJI_INFO} {member.name}", color=THEME_COLOR)
        embed.add_field(name="ID", value=f"`{member.id}`", inline=True)
        embed.add_field(name="Joined", value=discord.utils.format_dt(member.joined_at, style="D"), inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(member.created_at, style="D"), inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Get user avatar")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"{EMOJI_INFO} {member.name}'s Avatar", color=THEME_COLOR)
        embed.set_image(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
