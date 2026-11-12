import discord
from discord import app_commands
from discord.ext import commands
import db

class Warnings(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        await db.add_warning(interaction.guild.id, member.id, interaction.user.id, reason)
        await interaction.response.send_message(f"⚠️ Warned {member.mention} for: {reason}")
        try:
            await member.send(f"You were warned in **{interaction.guild.name}** for: {reason}")
        except: pass

    @app_commands.command(name="warnings", description="View warnings for a member")
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        rows = await db.get_warnings(interaction.guild.id, member.id)
        if not rows:
            return await interaction.response.send_message(f"{member.mention} has no warnings.", ephemeral=True)
        
        desc = "".join(f"**ID: {r[0]}** | By <@{r[1]}> | {r[2]}\n" for r in rows)
        embed = discord.Embed(title=f"Warnings for {member.name}", description=desc, color=discord.Color.orange())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clearwarnings", description="Clear all warnings for a member")
    @app_commands.checks.has_permissions(administrator=True)
    async def clearwarnings(self, interaction: discord.Interaction, member: discord.Member):
        await db.clear_warnings(interaction.guild.id, member.id)
        await interaction.response.send_message(f"✅ Cleared all warnings for {member.mention}.")

async def setup(bot): await bot.add_cog(Warnings(bot))