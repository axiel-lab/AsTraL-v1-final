import discord
from discord import app_commands
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="purge", description="Delete messages")
    @app_commands.describe(amount="Number of messages (1-100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int):
        if amount < 1 or amount > 100:
            return await interaction.response.send_message("1-100 only.", ephemeral=True)
            
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Deleted {len(deleted)}.", ephemeral=True)

    @app_commands.command(name="kick", description="Kick member")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.checks.bot_has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "None"):
        if interaction.user.top_role <= member.top_role:
            return await interaction.response.send_message("Role too high.", ephemeral=True)
            
        await member.kick(reason=reason)
        await interaction.response.send_message(f"Kicked {member.mention}. ({reason})")

    @app_commands.command(name="ban", description="Ban member")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "None"):
        if interaction.user.top_role <= member.top_role:
            return await interaction.response.send_message("Role too high.", ephemeral=True)
            
        await member.ban(reason=reason)
        await interaction.response.send_message(f"Banned {member.mention}. ({reason})")

async def setup(bot):
    await bot.add_cog(Moderation(bot))