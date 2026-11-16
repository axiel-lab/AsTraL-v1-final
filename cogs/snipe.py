import discord
from discord import app_commands
from discord.ext import commands
from ui import error_embed
from config import THEME_COLOR, EMOJI_ERROR

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.snipes = {}

    @commands.Cog.listener()
    async def on_message_delete(self, msg):
        if msg.author.bot or not msg.guild: return
        self.snipes[msg.channel.id] = (msg.content, msg.author.name, msg.author.display_avatar.url)

    @app_commands.command(name="snipe", description="Get the last deleted message")
    async def snipe(self, interaction: discord.Interaction):
        data = self.snipes.get(interaction.channel.id)
        if not data: return await interaction.response.send_message(embed=error_embed("Nothing to snipe."), ephemeral=True)
        content, author, avatar = data
        embed = discord.Embed(description=content, color=THEME_COLOR)
        embed.set_author(name=author, icon_url=avatar)
        await interaction.response.send_message(embed=embed)

async def setup(bot): await bot.add_cog(Snipe(bot))
