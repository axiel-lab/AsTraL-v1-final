import discord
from discord import app_commands
from discord.ext import commands
import db

class MentionResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mention_add", description="Auto-reply when a specific user is mentioned")
    @app_commands.checks.has_permissions(administrator=True)
    async def mention_add(self, interaction: discord.Interaction, user: discord.User, response: str):
        await db.set_mention_responder(interaction.guild.id, user.id, response)
        await interaction.response.send_message(f"✅ Will reply `{response}` when {user.mention} is mentioned.", ephemeral=True)

    @app_commands.command(name="mention_remove", description="Remove an auto-reply for a user")
    @app_commands.checks.has_permissions(administrator=True)
    async def mention_remove(self, interaction: discord.Interaction, user: discord.User):
        await db.remove_mention_responder(interaction.guild.id, user.id)
        await interaction.response.send_message(f"✅ Removed auto-reply for {user.mention}.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild or not msg.mentions:
            return

        responders = await db.get_mention_responders(msg.guild.id)
        for target_id, response in responders:
            if any(str(u.id) == target_id for u in msg.mentions):
                await msg.reply(response, mention_author=False)
                await msg.add_reaction("👀")
                break

async def setup(bot):
    await bot.add_cog(MentionResponder(bot))