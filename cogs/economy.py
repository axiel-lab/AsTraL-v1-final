import discord
from discord.ext import commands
import db
import time
from config import THEME_COLOR, EMOJI_COIN, EMOJI_WALLET, EMOJI_STAR, EMOJI_HEART, EMOJI_TROPHY
from ui import success_embed, error_embed, main_embed

# This check ensures the command is only used with "$" or as a slash command
def is_economy_prefix():
    async def predicate(ctx):
        if ctx.interaction: return True
        return ctx.prefix == "$"
    return commands.check(predicate)

class Economy(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.hybrid_command(name="profile", description="View your profile")
    @is_economy_prefix()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def profile(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        bal = await db.get_balance(ctx.guild.id, member.id)
        xp, level, _ = await db.get_level_data(ctx.guild.id, member.id)
        partner_id = await db.get_marriage(ctx.guild.id, member.id)
        partner = f"<@{partner_id}>" if partner_id else "None"
        
        embed = discord.Embed(title=f"{member.name}'s Profile", color=THEME_COLOR)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name=f"{EMOJI_WALLET} Cash", value=f"`{bal:,}`", inline=True)
        embed.add_field(name=f"{EMOJI_TROPHY} Level", value=f"`{level}` ({xp} XP)", inline=True)
        embed.add_field(name=f"{EMOJI_HEART} Partner", value=partner, inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="cash", aliases=["balance", "bal"], description="Check your cash balance")
    @is_economy_prefix()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def cash(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        bal = await db.get_balance(ctx.guild.id, member.id)
        await ctx.send(embed=main_embed(f"{EMOJI_WALLET} Cash Balance", f"{member.mention} has **{bal:,}** coins."))

    @commands.hybrid_command(name="daily", description="Claim your daily coins")
    @is_economy_prefix()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def daily(self, ctx: commands.Context):
        now = int(time.time())
        last_daily = await db.get_daily(ctx.guild.id, ctx.author.id)
        
        if now - last_daily < 86400:
            remaining = 86400 - (now - last_daily)
            return await ctx.send(embed=error_embed(f"Already claimed. Try in **{remaining // 3600}h {(remaining % 3600) // 60}m**."), ephemeral=True)

        amount = 4000
        await db.add_coins(ctx.guild.id, ctx.author.id, amount)
        await db.set_daily(ctx.guild.id, ctx.author.id, now)
        await ctx.send(embed=success_embed(f"You claimed your daily **{amount:,}** {EMOJI_COIN} coins!"))

    @commands.hybrid_command(name="pay", description="Transfer coins to another user")
    @is_economy_prefix()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def pay(self, ctx: commands.Context, member: discord.Member, amount: int):
        if member.bot or member == ctx.author or amount < 100:
            return await ctx.send(embed=error_embed("Invalid user or amount (Min 100)."), ephemeral=True)
            
        if await db.get_balance(ctx.guild.id, ctx.author.id) < amount:
            return await ctx.send(embed=error_embed("You don't have enough coins."), ephemeral=True)

        await db.add_coins(ctx.guild.id, ctx.author.id, -amount)
        await db.add_coins(ctx.guild.id, member.id, amount)
        await ctx.send(embed=success_embed(f"Transferred **{amount:,}** coins to {member.mention}."))

async def setup(bot): 
    await bot.add_cog(Economy(bot))
