import discord
from discord import app_commands
from discord.ext import commands
import db
import re

class AutoResponder(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="autoresponder_add", description="Add a regex auto-responder")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_ar(self, interaction: discord.Interaction, trigger: str, response: str):
        try:
            re.compile(trigger)
        except re.error:
            return await interaction.response.send_message("❌ Invalid Regex pattern.", ephemeral=True)
        
        await db.add_autoresponder(interaction.guild.id, trigger, response)
        await interaction.response.send_message(f"✅ Auto-responder added.", ephemeral=True)

    @app_commands.command(name="autoresponder_remove", description="Remove an auto-responder")
    @app_commands.checks.has_permissions(administrator=True)
    async def rm_ar(self, interaction: discord.Interaction, trigger: str):
        await db.remove_autoresponder(interaction.guild.id, trigger)
        await interaction.response.send_message(f"✅ Removed.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild: return
        
        responders = await db.get_autoresponders(msg.guild.id)
        for trigger, response in responders:
            if re.search(trigger, msg.content, re.IGNORECASE):
                await msg.reply(response, mention_author=False)
                break

async def setup(bot): await bot.add_cog(AutoResponder(bot))
