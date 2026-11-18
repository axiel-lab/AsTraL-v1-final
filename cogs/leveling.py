import discord
from discord import app_commands
from discord.ext import commands
import db
import time
import random
import math
from config import THEME_COLOR, EMOJI_STAR, EMOJI_GEAR
from ui import success_embed, error_embed, main_embed

class Leveling(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.hybrid_command(name="set_level_channel", description="Set a specific channel for level-up messages")
    @commands.has_permissions(administrator=True)
    async def set_level_channel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        if not channel:
            await db.set_level_channel(ctx.guild.id, None)
            return await ctx.send(embed=success_embed("Level-up notifications have been disabled."))
            
        await db.set_level_channel(ctx.guild.id, channel.id)
        await ctx.send(embed=success_embed(f"Level-up notifications will now be sent to {channel.mention}."))

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild or msg.content.startswith("!"): return

        gid, uid = str(msg.guild.id), str(msg.author.id)
        now = int(time.time())
        xp, level, last_msg = await db.get_level_data(gid, uid)
        
        # 60 second cooldown for XP
        if now - last_msg < 60: return

        gained_xp = random.randint(15, 25)
        new_xp = xp + gained_xp
        new_level = int(math.isqrt(new_xp // 100))
        
        await db.update_level_data(gid, uid, new_xp, new_level, now)

        if new_level > level:
            embed = main_embed(f"{EMOJI_STAR} Level Up!", f"{msg.author.mention} has reached **Level {new_level}**!")
            
            # Check if a specific channel is set
            level_chan_id = await db.get_level_channel(gid)
            if level_chan_id:
                channel = msg.guild.get_channel(int(level_chan_id))
                if channel:
                    await channel.send(embed=embed)
            else:
                # If no channel is set, send it in the current chat
                await msg.channel.send(embed=embed)

    @commands.hybrid_command(name="rank", description="Check your level and XP")
    async def rank(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        xp, level, _ = await db.get_level_data(ctx.guild.id, member.id)
        next_level_xp = ((level + 1) ** 2) * 100
        
        embed = main_embed(f"{EMOJI_STAR} {member.name}'s Rank", f"**Level:** `{level}`\n**XP:** `{xp} / {next_level_xp}`")
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="leaderboard", description="Top 10 most active users")
    async def leaderboard(self, ctx: commands.Context):
        rows = await db.get_top_levels(ctx.guild.id)
        if not rows: 
            return await ctx.send(embed=error_embed("No data yet."), ephemeral=True)

        desc = "".join(f"**{i}.** <@{uid}> - Level `{level}` ({xp} XP)\n" for i, (uid, xp, level) in enumerate(rows, 1))
        embed = main_embed(f"{EMOJI_STAR} Leaderboard", desc)
        await ctx.send(embed=embed)

async def setup(bot): await bot.add_cog(Leveling(bot))
