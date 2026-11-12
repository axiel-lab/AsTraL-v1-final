import discord
from discord import app_commands
from discord.ext import commands
import uuid

class PollView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def handle_vote(self, interaction: discord.Interaction, choice: str):
        embed = interaction.message.embeds[0]
        current = dict(embed.fields)
        name = interaction.user.name
        
        # Very basic in-memory tracking
        if 'votes' not in self.__dict__: self.votes = {}
        if choice not in self.votes: self.votes[choice] = set()
        
        # Remove from previous
        for c in self.votes:
            self.votes[c].discard(name)
            
        self.votes[choice].add(name)
        
        embed.clear_fields()
        for c in ["A", "B", "C", "D"]:
            if c in self.votes:
                embed.add_field(name=f"Option {c}", value=f"{len(self.votes[c])} votes\n" + ", ".join(self.votes[c])[:100])

        await interaction.message.edit(embed=embed)
        await interaction.response.send_message(f"Voted {choice}", ephemeral=True)

    @discord.ui.button(label="A", style=discord.ButtonStyle.primary)
    async def btn_a(self, i, b): await self.handle_vote(i, "A")

    @discord.ui.button(label="B", style=discord.ButtonStyle.primary)
    async def btn_b(self, i, b): await self.handle_vote(i, "B")

class Polls(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="poll", description="Create a button poll")
    async def poll(self, interaction: discord.Interaction, question: str):
        embed = discord.Embed(title=f"📊 {question}", color=discord.Color.blue())
        embed.add_field(name="Option A", value="0 votes")
        embed.add_field(name="Option B", value="0 votes")
        
        await interaction.response.send_message(embed=embed, view=PollView())

async def setup(bot): await bot.add_cog(Polls(bot))