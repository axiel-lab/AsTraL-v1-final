import discord
from discord import app_commands
from discord.ext import commands
import db
import time
import random
import math

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild or msg.content.startswith("!"): 
            return

        gid, uid = str(msg.guild.id), str(msg.author.id)
        now = int(time.time())
        
        xp, level, last_msg = await db.get_level_data(gid, uid)
        
        # 60 second cooldown for XP
        if now - last_msg < 60:
            return

        gained_xp = random.randint(15, 25)
        new_xp = xp + gained_xp
        
        # Math for leveling: Level 1 at 100 XP, Level 2 at 400 XP, etc. (x^2 * 100)
        new_level = int(math.isqrt(new_xp // 100))
        
        await db.update_level_data(gid, uid, new_xp, new_level, now)

        if new_level > level:
            await msg.channel.send(f"🎉 {msg.author.mention} leveled up to **Level {new_level}**!")

    @app_commands.command(name="rank", description="Check your level and XP")
    async def rank(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        xp, level, _ = await db.get_level_data(interaction.guild.id, member.id)
        
        next_level_xp = ((level + 1) ** 2) * 100
        
        embed = discord.Embed(title=f"{member.name}'s Rank", color=discord.Color.green())
        embed.add_field(name="Level", value=level, inline=True)
        embed.add_field(name="XP", value=f"{xp} / {next_level_xp}", inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="Top 10 most active users")
    async def leaderboard(self, interaction: discord.Interaction):
        rows = await db.get_top_levels(interaction.guild.id)
        
        if not rows:
            return await interaction.response.send_message("No data yet.", ephemeral=True)

        desc = ""
        for i, (uid, xp, level) in enumerate(rows, 1):
            desc += f"**{i}.** <@{uid}> - Level {level} ({xp} XP)\n"

        embed = discord.Embed(title="🏆 Leaderboard", description=desc, color=discord.Color.gold())
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))