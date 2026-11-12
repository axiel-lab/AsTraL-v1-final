import discord
from discord import app_commands
from discord.ext import commands
import db

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup_counting", description="Setup the counting game")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_counting(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await db.set_counting_channel(interaction.guild.id, channel.id)
        await interaction.response.send_message(f"✅ Counting game setup in {channel.mention}. Start with **1**.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild:
            return

        config = await db.get_counting(msg.guild.id)
        if not config or str(msg.channel.id) != str(config[0]):
            return

        try:
            num = int(msg.content)
        except ValueError:
            return

        current, last_user = config[1], config[2]

        if str(msg.author.id) == str(last_user):
            await msg.add_reaction("❌")
            await msg.reply("You can't count twice in a row!")
            await db.update_counting(msg.guild.id, 0, None)
            return

        if num == current + 1:
            await msg.add_reaction("✅")
            await db.update_counting(msg.guild.id, num, msg.author.id)
        else:
            await msg.add_reaction("❌")
            await msg.reply(f"Wrong number. It was **{current + 1}**. Resetting to 0.")
            await db.update_counting(msg.guild.id, 0, None)

async def setup(bot):
    await bot.add_cog(Counting(bot))