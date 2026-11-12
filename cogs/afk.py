import discord
from discord import app_commands
from discord.ext import commands
import db

class AFK(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="afk", description="Set your AFK status")
    async def afk(self, interaction: discord.Interaction, reason: str = "AFK"):
        await db.set_afk(interaction.guild.id, interaction.user.id, reason)
        await interaction.response.send_message(f"💤 Set AFK: {reason}")

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild: return
        afk = await db.get_afk(msg.guild.id, msg.author.id)
        if afk:
            await db.remove_afk(msg.guild.id, msg.author.id)
            await msg.channel.send(f"👋 Welcome back {msg.author.mention}, I removed your AFK.", delete_after=5)
        
        for user in msg.mentions:
            target_afk = await db.get_afk(msg.guild.id, user.id)
            if target_afk:
                await msg.reply(f"💤 **{user.name}** is AFK: {target_afk}", mention_author=False)

async def setup(bot): await bot.add_cog(AFK(bot))