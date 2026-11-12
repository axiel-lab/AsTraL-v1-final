import discord
from discord import app_commands
from discord.ext import commands
import db

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="logging", description="Setup server logs")
    @app_commands.checks.has_permissions(administrator=True)
    async def logging(self, interaction: discord.Interaction, message_logs: discord.TextChannel, member_logs: discord.TextChannel):
        await db.set_logging(interaction.guild.id, message_logs.id, member_logs.id)
        await interaction.response.send_message("✅ Logging configured.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild:
            return

        config = await db.get_logging(message.guild.id)
        if not config or not config[0]:
            return

        log_channel = message.guild.get_channel(int(config[0]))
        if log_channel:
            embed = discord.Embed(title="Message Deleted", description=f"**Author:** {message.author.mention}\n**Channel:** {message.channel.mention}\n**Content:** {message.content or 'None (Embed/Image)'}", color=discord.Color.red())
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or not before.guild or before.content == after.content:
            return

        config = await db.get_logging(before.guild.id)
        if not config or not config[0]:
            return

        log_channel = before.guild.get_channel(int(config[0]))
        if log_channel:
            embed = discord.Embed(title="Message Edited", color=discord.Color.orange())
            embed.add_field(name="Author", value=before.author.mention, inline=False)
            embed.add_field(name="Channel", value=before.channel.mention, inline=False)
            embed.add_field(name="Before", value=before.content[:1024], inline=False)
            embed.add_field(name="After", value=after.content[:1024], inline=False)
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        config = await db.get_logging(member.guild.id)
        if not config or not config[1]:
            return

        log_channel = member.guild.get_channel(int(config[1]))
        if log_channel:
            embed = discord.Embed(title="Member Joined", description=f"{member.mention} ({member.name})", color=discord.Color.green())
            embed.set_thumbnail(url=member.display_avatar.url)
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        config = await db.get_logging(member.guild.id)
        if not config or not config[1]:
            return

        log_channel = member.guild.get_channel(int(config[1]))
        if log_channel:
            embed = discord.Embed(title="Member Left", description=f"{member.mention} ({member.name})", color=discord.Color.red())
            embed.set_thumbnail(url=member.display_avatar.url)
            await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Logging(bot))