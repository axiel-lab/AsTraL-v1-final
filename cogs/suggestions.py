import discord
from discord import app_commands
from discord.ext import commands
import db
from ui import success_embed, error_embed, main_embed
from config import THEME_COLOR, EMOJI_SUCCESS, EMOJI_ERROR, EMOJI_INFO

class Suggestions(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="setup_suggestions", description="Setup suggestions channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_suggestions(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await db.set_stat(interaction.guild.id, channel.id, "suggestions")
        await interaction.response.send_message(embed=success_embed(f"Suggestions will be sent to {channel.mention}."), ephemeral=True)

    @app_commands.command(name="suggest", description="Submit a suggestion")
    async def suggest(self, interaction: discord.Interaction, text: str):
        stats = await db.get_stats()
        sug_chan = next((c[1] for c in stats if c[0] == str(interaction.guild.id) and c[2] == "suggestions"), None)
        
        if not sug_chan:
            return await interaction.response.send_message(embed=error_embed("Suggestions not setup."), ephemeral=True)
        
        channel = interaction.guild.get_channel(int(sug_chan))
        if not channel:
            return await interaction.response.send_message(embed=error_embed("Suggestions channel not found."), ephemeral=True)

        embed = main_embed(f"{EMOJI_INFO} New Suggestion", text)
        embed.set_footer(text=f"Suggested by {interaction.user.name}")
        
        await interaction.response.send_message(embed=success_embed("Suggestion sent!"), ephemeral=True)
        msg = await channel.send(embed=embed)
        
        # Custom Emoji Reactions
        await msg.add_reaction(discord.PartialEmoji.from_str(EMOJI_SUCCESS))
        await msg.add_reaction(discord.PartialEmoji.from_str(EMOJI_ERROR))
        
        await db.add_suggestion(msg.id, channel.id, interaction.user.id, text)

async def setup(bot): await bot.add_cog(Suggestions(bot))
