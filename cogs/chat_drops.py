import discord
from discord.ext import commands
import db
import random

class DropView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.claimed = False

    @discord.ui.button(label="Claim Treasure", style=discord.ButtonStyle.success, emoji="💰")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.claimed:
            return await interaction.response.send_message("Too late!", ephemeral=True)
        
        self.claimed = True
        amount = random.randint(100, 500)
        await db.add_coins(interaction.guild.id, interaction.user.id, amount)
        
        button.disabled = True
        button.label = "Claimed!"
        await interaction.response.edit_message(content=f"🎉 {interaction.user.mention} claimed the drop and won **{amount} coins**!", view=self)

class ChatDrops(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild: return
        
        if random.randint(1, 50) == 1:
            embed = discord.Embed(title="💎 TREASURE DROP!", description="A chest just fell from the sky! Click below to claim it.", color=discord.Color.gold())
            await msg.channel.send(embed=embed, view=DropView())

async def setup(bot): await bot.add_cog(ChatDrops(bot))
