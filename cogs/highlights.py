import discord
from discord import app_commands
from discord.ext import commands
import db
from ui import success_embed, error_embed, main_embed

class Highlights(commands.Cog):
    def __init__(self, bot): self.bot = bot
    hl_group = app_commands.Group(name="highlight", description="Manage highlights")

    @hl_group.command(name="add", description="Add a word to get notified for")
    async def hl_add(self, interaction: discord.Interaction, word: str):
        await db.add_highlight(interaction.guild.id, interaction.user.id, word)
        await interaction.response.send_message(embed=success_embed(f"You will be DM'd for `{word}`."), ephemeral=True)

    @hl_group.command(name="remove", description="Remove a highlight word")
    async def hl_remove(self, interaction: discord.Interaction, word: str):
        await db.remove_highlight(interaction.guild.id, interaction.user.id, word)
        await interaction.response.send_message(embed=error_embed(f"Removed `{word}`."), ephemeral=True)

    @hl_group.command(name="list", description="List your highlight words")
    async def hl_list(self, interaction: discord.Interaction):
        words = await db.get_user_highlights(interaction.guild.id, interaction.user.id)
        if not words: return await interaction.response.send_message(embed=info_embed("No highlights set."), ephemeral=True)
        await interaction.response.send_message(embed=main_embed("Highlights", ", ".join(f"`{w[0]}`" for w in words)), ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild: return
        highlights = await db.get_all_highlights(msg.guild.id)
        pinged = set()
        for uid, word in highlights:
            if word in msg.content.lower() and str(msg.author.id) != uid and uid not in pinged:
                pinged.add(uid)
                user = self.bot.get_user(int(uid))
                if user:
                    try:
                        embed = main_embed(f"Highlight: {word}", f"**Server:** {msg.guild.name}\n**Channel:** {msg.channel.mention}\n**Message:** {msg.content[:1000]}\n[Click to jump]({msg.jump_url})")
                        await user.send(embed=embed)
                    except: pass

async def setup(bot): await bot.add_cog(Highlights(bot))
