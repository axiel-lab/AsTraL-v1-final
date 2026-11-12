import discord
from discord import app_commands
from discord.ext import commands
import db

class Highlights(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    hl_group = app_commands.Group(name="highlight", description="Manage your highlight words")

    @hl_group.command(name="add", description="Add a word to get notified for")
    async def hl_add(self, interaction: discord.Interaction, word: str):
        await db.add_highlight(interaction.guild.id, interaction.user.id, word)
        await interaction.response.send_message(f"✅ You will now be DM'd when someone says `{word}`.", ephemeral=True)

    @hl_group.command(name="remove", description="Remove a highlight word")
    async def hl_remove(self, interaction: discord.Interaction, word: str):
        await db.remove_highlight(interaction.guild.id, interaction.user.id, word)
        await interaction.response.send_message(f"❌ Removed `{word}` from your highlights.", ephemeral=True)

    @hl_group.command(name="list", description="List your highlight words")
    async def hl_list(self, interaction: discord.Interaction):
        words = await db.get_user_highlights(interaction.guild.id, interaction.user.id)
        if not words:
            return await interaction.response.send_message("You have no highlights set.", ephemeral=True)
        
        word_list = ", ".join(f"`{w[0]}`" for w in words)
        await interaction.response.send_message(f"**Your Highlights:**\n{word_list}", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild:
            return

        highlights = await db.get_all_highlights(msg.guild.id)
        if not highlights:
            return

        content = msg.content.lower()
        pinged_users = set()

        for uid, word in highlights:
            if word in content and str(msg.author.id) != uid and uid not in pinged_users:
                pinged_users.add(uid)
                user = self.bot.get_user(int(uid))
                if user:
                    try:
                        embed = discord.Embed(
                            title="Highlight Triggered",
                            description=f"**Word:** `{word}`\n**Server:** {msg.guild.name}\n**Channel:** {msg.channel.mention}\n**Message:** {msg.content[:1000]}",
                            color=discord.Color.gold()
                        )
                        embed.add_field(name="Link", value=f"[Jump to message]({msg.jump_url})")
                        await user.send(embed=embed)
                    except discord.Forbidden:
                        pass # DMs are closed

async def setup(bot):
    await bot.add_cog(Highlights(bot))