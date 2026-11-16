import discord
from discord import app_commands
from discord.ext import commands
from ui import success_embed, error_embed
from config import THEME_COLOR, EMOJI_KICK, EMOJI_BAN, EMOJI_TRASH

class Moderation(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.hybrid_command(name="purge", description="Delete messages")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, amount: int):
        if amount < 1 or amount > 100:
            return await ctx.send(embed=error_embed("Amount must be between 1 and 100."), ephemeral=True)
            
        await ctx.defer(ephemeral=True)
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(embed=success_embed(f"{EMOJI_TRASH} Deleted {len(deleted)} messages."), ephemeral=True)

    @commands.hybrid_command(name="kick", description="Kick member")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, reason: str = "None"):
        if ctx.author.top_role <= member.top_role:
            return await ctx.send(embed=error_embed("Role too high."), ephemeral=True)
            
        await member.kick(reason=reason)
        await ctx.send(embed=success_embed(f"{EMOJI_KICK} Kicked {member.mention}. ({reason})"))

    @commands.hybrid_command(name="ban", description="Ban member")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, reason: str = "None"):
        if ctx.author.top_role <= member.top_role:
            return await ctx.send(embed=error_embed("Role too high."), ephemeral=True)
            
        await member.ban(reason=reason)
        await ctx.send(embed=success_embed(f"{EMOJI_BAN} Banned {member.mention}. ({reason})"))

async def setup(bot):
    await bot.add_cog(Moderation(bot))
