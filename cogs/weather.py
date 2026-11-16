import discord
from discord import app_commands
from discord.ext import commands
import db
from ui import success_embed, main_embed

class Logging(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="logging", description="Setup server logs")
    @app_commands.checks.has_permissions(administrator=True)
    async def logging(self, interaction: discord.Interaction, message_logs: discord.TextChannel, member_logs: discord.TextChannel):
        await db.set_logging(interaction.guild.id, message_logs.id, member_logs.id)
        await interaction.response.send_message(embed=success_embed("Logging configured."), ephemeral=True)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild: return
        config = await db.get_logging(message.guild.id)
        if config and config[0]:
            channel = message.guild.get_channel(int(config[0]))
            if channel: await channel.send(embed=main_embed("Message Deleted", f"**Author:** {message.author.mention}\n**Channel:** {message.channel.mention}\n**Content:** {message.content or 'None'}"))

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or not before.guild or before.content == after.content: return
        config = await db.get_logging(before.guild.id)
        if config and config[0]:
            channel = before.guild.get_channel(int(config[0]))
            if channel: await channel.send(embed=main_embed("Message Edited", f"**Author:** {before.author.mention}\n**Channel:** {before.channel.mention}\n**Before:** {before.content[:500]}\n**After:** {after.content[:500]}"))

async def setup(bot): await bot.add_cog(Logging(bot))
