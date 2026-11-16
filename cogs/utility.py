import discord
from discord import app_commands
from discord.ext import commands
from config import THEME_COLOR, EMOJI_INFO, EMOJI_GEAR

class Utility(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.hybrid_command(name="ping", description="Check bot latency")
    async def ping(self, ctx: commands.Context):
        latency = round(self.bot.latency * 1000)
        await ctx.send(embed=discord.Embed(description=f"{EMOJI_GEAR} Pong! `{latency}ms`", color=THEME_COLOR))

    @commands.hybrid_command(name="serverinfo", description="Get server information")
    async def serverinfo(self, ctx: commands.Context):
        guild = ctx.guild
        embed = discord.Embed(title=f"{EMOJI_INFO} {guild.name}", color=THEME_COLOR)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Members", value=f"`{guild.member_count}`", inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(guild.created_at, style="D"), inline=True)
        if guild.icon: embed.set_thumbnail(url=guild.icon.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="userinfo", description="Get user information")
    async def userinfo(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"{EMOJI_INFO} {member.name}", color=THEME_COLOR)
        embed.add_field(name="ID", value=f"`{member.id}`", inline=True)
        embed.add_field(name="Joined", value=discord.utils.format_dt(member.joined_at, style="D"), inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(member.created_at, style="D"), inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="avatar", description="Get user avatar")
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"{EMOJI_INFO} {member.name}'s Avatar", color=THEME_COLOR)
        embed.set_image(url=member.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
