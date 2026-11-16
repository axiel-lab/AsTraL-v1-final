import discord
from discord import app_commands
from discord.ext import commands
import db
import time
import random
import math
from config import THEME_COLOR, EMOJI_STAR, EMOJI_WARNING

class Leveling(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild or msg.content.startswith("!"): return

        gid, uid = str(msg.guild.id), str(msg.author.id)
        now = int(time.time())
        xp, level, last_msg = await db.get_level_data(gid, uid)
        
        if now - last_msg < 60: return

        gained_xp = random.randint(15, 25)
        new_xp = xp + gained_xp
        new_level = int(math.isqrt(new_xp // 100))
        
        await db.update_level_data(gid, uid, new_xp, new_level, now)

        if new_level > level:
            await msg.channel.send(embed=discord.Embed(description=f"{EMOJI_STAR} {msg.author.mention} leveled up to **Level {new_level}**!", color=THEME_COLOR))

    @app_commands.command(name="rank", description="Check your level and XP")
    async def rank(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        xp, level, _ = await db.get_level_data(interaction.guild.id, member.id)
        next_level_xp = ((level + 1) ** 2) * 100
        
        embed = discord.Embed(title=f"{EMOJI_STAR} {member.name}'s Rank", color=THEME_COLOR)
        embed.add_field(name="Level", value=f"`{level}`", inline=True)
        embed.add_field(name="XP", value=f"`{xp} / {next_level_xp}`", inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="Top 10 most active users")
    async def leaderboard(self, interaction: discord.Interaction):
        rows = await db.get_top_levels(interaction.guild.id)
        if not rows: return await interaction.response.send_message(embed=discord.Embed(description="No data yet.", color=THEME_COLOR), ephemeral=True)

        desc = "".join(f"**{i}.** <@{uid}> - Level `{level}` ({xp} XP)\n" for i, (uid, xp, level) in enumerate(rows, 1))
        embed = discord.Embed(title=f"{EMOJI_STAR} Leaderboard", description=desc, color=THEME_COLOR)
        await interaction.response.send_message(embed=embed)

async def setup(bot): await bot.add_cog(Leveling(bot))
